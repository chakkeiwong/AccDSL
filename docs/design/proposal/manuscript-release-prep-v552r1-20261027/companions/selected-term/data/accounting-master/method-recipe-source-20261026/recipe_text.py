"""Explicit recipe source; protected constructors own contextual semantics."""
from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'ordered-eligibility-source-20261026'))
import eligibility_text as syntax
sys.path.insert(0,str(HERE.parent/'ordered-assessment-expansion-20261026'))
import expander
c=expander.c;core=c.core;rules=syntax.rules;j=syntax.j
Invalid=syntax.Invalid;need=syntax.need
PROFILE='MethodRecipeText/1'

@dataclass(frozen=True)
class Parameter:
    name:str

def encode(value):
    if isinstance(value,Parameter):return {'node':'parameter','name':value.name}
    if type(value) is dict:return {'node':'object','fields':{k:encode(v) for k,v in value.items()}}
    if type(value) is list:return {'node':'array','items':[encode(v) for v in value]}
    need(value is None or type(value) in (str,int,bool),'literal_scalar')
    return {'node':'literal','value':value}

def decode(node):
    kind=node['node']
    if kind=='parameter':return Parameter(node['name'])
    if kind=='literal':return deepcopy(node['value'])
    if kind=='object':return {k:decode(v) for k,v in node['fields'].items()}
    need(kind=='array','template_node');return [decode(v) for v in node['items']]

def has_parameter(value):
    if isinstance(value,Parameter):return True
    if type(value) is dict:return any(has_parameter(v) for v in value.values())
    if type(value) is list:return any(has_parameter(v) for v in value)
    return False

def datum(value):
    if isinstance(value,Parameter):return '(parameter '+j(value.name)+')'
    if not has_parameter(value):return j(value)
    if type(value) is list:return '(array '+' '.join(datum(v) for v in value)+')'
    return '(record '+' '.join('(field '+j(k)+' '+datum(v)+')' for k,v in value.items())+')'


class Reader(syntax.Reader):
    def data(self,depth=0):
        self.nodes+=1;need(depth<=core.MAX_DEPTH and self.nodes<=core.MAX_NODES,'data_limit',self.location())
        if self.pos<len(self.items) and self.items[self.pos][0]=='value':return self.take('value')
        self.take('(');index=self.pos;kind=self.take('word')
        if kind=='parameter':result=Parameter(self.string())
        elif kind=='array':
            result=[]
            while self.pos<len(self.items) and self.items[self.pos][0]!=')':result.append(self.data(depth+1))
        elif kind=='record':
            result={}
            while self.pos<len(self.items) and self.items[self.pos][0]=='(':
                self.take('(');self.take('word','field');key=self.string()
                need(key not in result,'duplicate_data_field',self.location());result[key]=self.data(depth+1);self.take(')')
        else:raise Invalid('data_operator:'+kind,self.location(index))
        self.take(')');return result

    def scalar(self):
        index=self.pos;value=self.data()
        need(isinstance(value,Parameter) or type(value) is str and bool(value),'string_or_parameter',self.location(index))
        return value

    def expr(self,depth=0,monetary=False):
        self.nodes+=1;need(depth<=core.MAX_DEPTH and self.nodes<=core.MAX_NODES,'expression_limit',self.location())
        self.take('(');index=self.pos;op=self.take('word')
        if op=='ref':value={'op':op,'id':self.scalar()}
        elif op=='const':value={'op':op,'type':self.data(),'value':self.data()}
        elif op in (('add','sub','mul','min') if monetary else ('eq','le','lt','add','sub','mul')):
            value={'op':op,'left':self.expr(depth+1,monetary),'right':self.expr(depth+1,monetary)}
        elif not monetary and op=='not':value={'op':op,'arg':self.expr(depth+1)}
        elif not monetary and op in ('all','any'):
            args=[]
            while self.pos<len(self.items) and self.items[self.pos][0]=='(':args.append(self.expr(depth+1))
            need(bool(args),'empty_boolean_expression',self.location());value={'op':op,'args':args}
        else:raise Invalid('expression_operator:'+op,self.location(index))
        self.take(')');return value

    def parameter_source(self):
        self.take('(');index=self.pos;kind=self.take('word');result={'kind':kind}
        if kind=='event_input':result['name']=self.string()
        elif kind in ('event_metadata','book_metadata'):result['field']=self.string()
        elif kind=='pointer':
            result['segments']=[]
            while self.pos<len(self.items) and self.items[self.pos][0]=='(':
                self.take('(');tag=self.take('word');need(tag in ('literal','parameter'),'pointer_segment',self.location())
                result['segments'].append({tag:self.string()});self.take(')')
        else:need(kind=='input_schema','parameter_source:'+kind,self.location(index))
        self.take(')');return result


def parse_method(rows,source):
    method=None;section=None;manifest=None;seen=set();spans=[]
    def unique(obj,key,value,loc):
        need(key not in obj,'duplicate_declaration:'+str(key),loc);obj[key]=value
    for line,loc in rows:
        if not line.strip():continue
        r=Reader(source,line,loc);word=r.take('word');spans.append(loc)
        if method is None:
            need(word=='company_method','method_header',loc)
            method=dict(profile=r.scalar(),id=r.scalar(),version=r.scalar(),account_map={},
                        preconditions={'bindings':{}},postconditions={'bindings':{}},monetary={'bindings':{}},
                        memory={},residual_prerequisites=[])
        elif section=='rules':
            if word=='input':
                key=r.string();unique(manifest['inputs'],key,dict(type=r.data(),role=r.take('word'),source_ref=r.scalar()),loc)
            elif word=='guarded':
                manifest['requirements'].append(dict(id=r.scalar(),on_false=r.take('word'),on_unknown=r.take('word'),
                    guard_requires=r.data(),requires=r.data(),admission_refs=r.data(),guard=r.expr(),predicate=r.expr()))
            elif word=='required_known':
                need(not known_seen,'duplicate_required_known',loc);manifest['required_known']=r.data();known_seen=True
            elif word in ('capability','residual'):
                manifest['capabilities' if word=='capability' else 'residual_prerequisites'].append(r.scalar())
            else:
                need(word=='end_rules' and known_seen,'incomplete_rules',loc)
                method[parent]['manifest']=manifest;manifest=None;section=parent
        elif section in ('preconditions','postconditions'):
            if word=='begin_rules':
                need('manifest' not in method[section],'duplicate_rules',loc)
                manifest=dict(profile=r.string(),method_id=r.scalar(),version=r.scalar(),inputs={},requirements=[],required_known=[],capabilities=[],residual_prerequisites=[])
                need(manifest['profile']=='MethodRequirements/3','guard_profile',loc)
                known_seen=False;parent=section;section='rules'
            else:
                need(word=='end_'+section and 'manifest' in method[section],'condition_section',loc);section=None
        elif section=='monetary':
            d=method['monetary']['definition']
            if word=='money_input':
                key=r.string();unique(d['inputs'],key,dict(type=r.data(),role=r.take('word'),source_ref=r.scalar()),loc)
            elif word=='money_account':unique(d['accounts'],r.string(),r.data(),loc)
            elif word=='cash_account':unique(d,'cash_account',r.scalar(),loc)
            elif word in ('calculation','posting','flow'):
                item={'id':r.scalar()}
                if word=='calculation':item['type']=r.data()
                elif word=='posting':item['account']=r.scalar()
                else:item.update(activity=r.scalar(),origin=r.scalar())
                item.update(requires=r.data(),expression=r.expr(monetary=True))
                d[{'calculation':'calculations','posting':'postings','flow':'flows'}[word]].append(item)
            else:need(word=='end_monetary' and 'cash_account' in d,'monetary_section',loc);section=None
        elif section=='memory':
            part=method['memory']
            if word=='memory_input':unique(part['input_bindings'],r.string(),r.data(),loc)
            elif word=='write':part['definition']['operations'].append(dict(id=r.scalar(),op=r.scalar(),path=r.data(),value=r.data()))
            else:need(word=='end_memory','memory_section',loc);section=None
        elif word=='context':unique(method,'context',r.data(),loc)
        elif word=='account_map':unique(method['account_map'],r.string(),r.scalar(),loc)
        elif word=='input_binding':
            target=r.string();need(target in ('preconditions','postconditions','monetary'),'binding_section',loc)
            unique(method[target]['bindings'],r.string(),r.data(),loc)
        elif word in ('begin_preconditions','begin_postconditions','begin_monetary','begin_memory'):
            section=word.removeprefix('begin_');need(section not in seen,'duplicate_section',loc);seen.add(section)
            if section=='monetary':method[section]['definition']=dict(profile=r.scalar(),method_id=r.scalar(),version=r.scalar(),inputs={},accounts={},calculations=[],postings=[],flows=[])
            elif section=='memory':method[section]=dict(definition=dict(profile=r.scalar(),state_schema=r.scalar(),input_schema=r.scalar(),operations=[]),input_bindings={})
        elif word=='residual':method['residual_prerequisites'].append(r.scalar())
        else:raise Invalid('method_declaration:'+word,r.location(0))
        r.finish()
    need(method is not None and section is None and seen=={'preconditions','postconditions','monetary','memory'} and 'context' in method,'incomplete_method',spans[-1] if spans else None)
    return encode(method)


def lower(source):
    location=None
    try:
        rows=syntax.source_rows(source);template=None;state='header';spans=[];method_rows=[];names=set();method_span=None
        for line,location in rows:
            if not line.strip():continue
            spans.append(location);need(state!='done','declaration_after_end',location)
            if state=='method':
                if line.strip()=='end_method;':
                    template['method_template']=parse_method(method_rows,source);state='body'
                    method_span=syntax.span(source,method_start['byte_start'],location['byte_end'],method_start['line'],'method')
                else:method_rows.append((line,location))
                continue
            r=Reader(source,line,location);word=r.take('word')
            if state=='header':
                need(word=='parameterized_recipe' and r.string()==PROFILE,'recipe_source_profile',location)
                template=dict(profile=r.string(),transition_profile=r.string(),parameters=[],residuals=[])
                need(template['profile']==c.PROFILE,'template_profile',location)
                need(template['transition_profile']==c.frontend.v2.PROFILE,'transition_profile',location);state='body'
            elif word in ('context','input_schema'):
                key='context' if word=='context' else 'input_schema_definition'
                need(key not in template,'duplicate_declaration:'+word,location);template[key]=r.take('value')
            elif word=='parameter':
                name=r.string();need(name not in names,'duplicate_parameter',location);names.add(name)
                template['parameters'].append(dict(name=name,type=r.take('value'),source=r.parameter_source()))
            elif word=='residual':template['residuals'].append(r.string())
            elif word=='begin_method':
                need('method_template' not in template,'duplicate_method',location);state='method';method_start=location
            else:
                need(word=='end_recipe','recipe_declaration:'+word,r.location(0))
                need(all(k in template for k in ('context','input_schema_definition','method_template')),'incomplete_recipe',location);state='done'
            r.finish()
        need(state=='done','incomplete_source:'+state,location)
        c.base.memory.bounded(template);c.exact(template)
        return dict(profile=PROFILE,status='lowered_syntax_only',template=template,template_sha256=core.digest(template),
                    source_sha256=sha256(source.encode()).hexdigest(),source_spans=spans,method_span=method_span,
                    executed=False,contextually_compiled=False,source_admission=False,accounting_admission=False)
    except Exception as exc:
        if isinstance(exc,Invalid):raise
        raise Invalid(getattr(exc,'reason',str(exc)),location) from exc


def construct_source(source,book,event,schemas,definition,call):
    lowered=lower(source)
    try:return c.construct(lowered['template'],book,event,schemas,definition,call)
    except Exception as exc:
        raise Invalid(getattr(exc,'reason',str(exc)),syntax.span(source,0,len(source.encode()),1,'document')) from exc


def expression(node):
    op=node['op']
    if op=='ref':args=[datum(node['id'])]
    elif op=='const':args=[datum(node['type']),datum(node['value'])]
    elif op=='not':args=[expression(node['arg'])]
    elif op in ('all','any'):args=[expression(x) for x in node['args']]
    else:args=[expression(node['left']),expression(node['right'])]
    return '('+' '.join([op]+args)+')'


def render_method(node):
    m=decode(node);rows=[]
    def add(word,*values):rows.append(word+(' '+' '.join(datum(x) for x in values) if values else '')+';')
    add('company_method',m['profile'],m['id'],m['version']);add('context',m['context'])
    for key,value in m['account_map'].items():add('account_map',key,value)
    def bindings(section):
        for key,value in m[section]['bindings'].items():add('input_binding',section,key,value)
    def conditions(section):
        add('begin_'+section);d=m[section]['manifest'];add('begin_rules',d['profile'],d['method_id'],d['version'])
        for key,v in d['inputs'].items():rows.append('input '+' '.join([j(key),datum(v['type']),v['role'],datum(v['source_ref'])])+';')
        for q in d['requirements']:
            rows.append('guarded '+' '.join([datum(q['id']),q['on_false'],q['on_unknown'],datum(q['guard_requires']),datum(q['requires']),datum(q['admission_refs']),expression(q['guard']),expression(q['predicate'])])+';')
        add('required_known',d['required_known'])
        for word,key in [('capability','capabilities'),('residual','residual_prerequisites')]:
            for value in d[key]:add(word,value)
        add('end_rules');add('end_'+section);bindings(section)
    conditions('preconditions');d=m['monetary']['definition'];add('begin_monetary',d['profile'],d['method_id'],d['version'])
    for key,v in d['inputs'].items():rows.append('money_input '+' '.join([j(key),datum(v['type']),v['role'],datum(v['source_ref'])])+';')
    for key,value in d['accounts'].items():add('money_account',key,value)
    add('cash_account',d['cash_account'])
    for word,key in [('calculation','calculations'),('posting','postings'),('flow','flows')]:
        for q in d[key]:
            args=[q['id']]
            if word=='calculation':args.append(q['type'])
            elif word=='posting':args.append(q['account'])
            else:args.extend([q['activity'],q['origin']])
            args.append(q['requires']);rows.append(word+' '+' '.join(datum(x) for x in args)+' '+expression(q['expression'])+';')
    add('end_monetary');bindings('monetary');d=m['memory']['definition'];add('begin_memory',d['profile'],d['state_schema'],d['input_schema'])
    for key,value in m['memory']['input_bindings'].items():add('memory_input',key,value)
    for q in d['operations']:add('write',*[q[k] for k in ('id','op','path','value')])
    add('end_memory');conditions('postconditions')
    for value in m['residual_prerequisites']:add('residual',value)
    return rows


def render(template):
    rows=[]
    def add(word,*values):rows.append(word+(' '+' '.join(j(x) for x in values) if values else '')+';')
    add('parameterized_recipe',PROFILE,template['profile'],template['transition_profile'])
    add('context',template['context']);add('input_schema',template['input_schema_definition'])
    for p in template['parameters']:
        source=p['source'];kind=source['kind'];args=[]
        if kind=='event_input':args=[j(source['name'])]
        elif kind in ('event_metadata','book_metadata'):args=[j(source['field'])]
        elif kind=='pointer':args=['('+key+' '+j(value)+')' for segment in source['segments'] for key,value in segment.items()]
        else:need(kind=='input_schema','parameter_source')
        rows.append('parameter '+j(p['name'])+' '+j(p['type'])+' ('+' '.join([kind]+args)+');')
    for value in template['residuals']:add('residual',value)
    add('begin_method');rows.extend(render_method(template['method_template']));add('end_method');add('end_recipe')
    source='\n'.join(rows)+'\n';need(core.canonical(lower(source)['template'])==core.canonical(template),'render_roundtrip');return source
