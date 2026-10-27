"""Ordered explicit event-rule source; reuse preserved data/expression parsers."""
from pathlib import Path
from hashlib import sha256
import importlib.util,json,sys
HERE=Path(__file__).resolve().parent
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
ct=load('term_event_contract_syntax',HERE.parent/'nested-contract-source-20261026/contract_text.py')
sys.path.insert(0,str(HERE.parent/'method-recipe-source-20261026'))
import recipe_text as recipe
sys.path.insert(0,str(HERE.parent/'term-full-event-binding-20261026'))
import full_composition as full
B=ct.block;M=ct.mapping;L=ct.sequence;S=ct.STRING;V=ct.VALUE;W=ct.WORD
D='data';P='parameter_expression';R='row_expression'
PROFILE='SelectedTermEventText/1';Invalid=ct.Invalid;need=ct.need;core=ct.core;j=ct.j
ct.SCHEMAS.update({
 'carry_policy':(None,dict(mode=W,cursor=S,preserve_provenance=S,cursor_provenance=S)),
 'event_rule':(None,dict(eligibility=B('eligibility'),construction=('construction',))),
 'eligibility':('OrderedNestedEventEligibility/1',dict(context=V,operation=W,input_types=M('input',V),stages=L('stage',B('eligibility_stage')),residuals=ct.STRINGS)),
 'eligibility_stage':(None,dict(id=S,reason=S,bindings=M('binding',B('event_binding_source')),manifest=B('rules'))),
 'event_binding_source':(None,dict(kind=W,name=S,field=S,pointer=S,key_input=S,after_stage=S,
   parent_after_stage=S,child_pointer=S,child_key_input=S,value=B('event_binding_source'),left=B('event_binding_source'),right=B('event_binding_source'))),
 'recipe':('ParameterizedCompanyMethod/1',dict(transition_profile=S,context=V,parameters=L('parameter',B('parameter')),
   method_template=('encoded_method',),input_schema_definition=V,residuals=ct.STRINGS)),
 'parameter':(None,dict(name=S,type=V,source=B('parameter_source'))),
 'parameter_source':(None,dict(kind=W,name=S,field=S,segments=L('segment',B('segment')))),
 'segment':(None,dict(literal=S,parameter=S)),
 'expansion':('OrderedNestedMethodExpansion/1',dict(base_template=B('recipe'),map_pointer=S,row_definition=V,
   row_operations=L('write',R),suffix_operations=L('write',R),residuals=ct.STRINGS)),
 'method':('CompanyBookMethod/1',dict(id=D,version=D,context=D,account_map=M('account',D),preconditions=B('condition'),postconditions=B('condition'),
   monetary=B('monetary'),memory=B('memory'),residual_prerequisites=L('item',D))),
 'condition':(None,dict(manifest=B('method_rules'),bindings=M('binding',B('method_binding')))),
 'method_binding':(None,dict(kind=D,name=D,pointer=D,field=D,account=D,role=D)),
 'method_rules':('MethodRequirements/3',dict(method_id=D,version=D,inputs=M('input',B('method_input')),requirements=L('requirement',B('method_requirement')),
   required_known=D,capabilities=L('item',D),residual_prerequisites=L('item',D))),
 'method_input':(None,dict(type=D,role=W,source_ref=D)),
 'method_requirement':(None,dict(id=D,guard=P,guard_requires=D,predicate=P,requires=D,admission_refs=D,on_false=W,on_unknown=W)),
 'monetary':(None,dict(definition=B('money_definition'),bindings=M('binding',B('method_binding')))),
 'money_definition':('MethodMonetaryEffects/1',dict(method_id=D,version=D,inputs=M('input',B('method_input')),
   calculations=L('calculation',B('calculation')),accounts=M('account',D),cash_account=D,
   postings=L('posting',B('posting')),flows=L('flow',B('flow')))),
 'calculation':(None,dict(id=D,type=D,requires=D,expression=P)),
 'posting':(None,dict(id=D,account=D,requires=D,expression=P)),
 'flow':(None,dict(id=D,activity=D,origin=D,requires=D,expression=P)),
 'memory':(None,dict(definition=B('memory_definition'),input_bindings=M('binding',B('method_binding')))),
 'memory_definition':('MethodMemoryEffects/1',dict(state_schema=D,input_schema=D,operations=L('write',B('memory_write')))),
 'memory_write':(None,dict(id=D,op=D,path=D,value=B('write_value'))),
 'write_value':(None,dict(kind=D,value=D,fields=M('field',B('write_value')),source=D,pointer=D)),
})

class Reader(recipe.Reader):
    def row_expression(self,depth=0):
        self.nodes+=1;need(depth<=core.MAX_DEPTH and self.nodes<=core.MAX_NODES,'row_expression_limit',self.location())
        self.take('(');index=self.pos;kind=self.take('word')
        if kind=='const':v=dict(expr='literal',type=self.take('value'),value=self.take('value'))
        elif kind=='row':v=dict(expr=kind,field=self.string())
        elif kind=='key':v=dict(expr=kind)
        elif kind=='event_metadata':v=dict(expr=kind,field=self.string())
        elif kind=='event_input':v=dict(expr=kind,name=self.string(),type=self.take('value'))
        elif kind in ('date_lt','date_le'):v=dict(expr=kind,left=self.row_expression(depth+1),right=self.row_expression(depth+1))
        elif kind=='if':v={'expr':kind,'condition':self.row_expression(depth+1),'then':self.row_expression(depth+1),'else':self.row_expression(depth+1)}
        elif kind=='operation_id':v=dict(expr=kind,prefix=self.string())
        elif kind=='array':
            v=dict(expr='array',items=[])
            while self.items[self.pos][0]=='(':v['items'].append(self.row_expression(depth+1))
        elif kind=='object':
            v=dict(expr='object',fields={})
            while self.items[self.pos][0]=='(':
                self.take('(');self.take('word','field');key=self.string()
                need(key not in v['fields'],'duplicate_row_field',self.location());v['fields'][key]=self.row_expression(depth+1);self.take(')')
        else:raise Invalid('row_operator:'+kind,self.location(index))
        self.take(')');return v

class Parser(ct.Parser):
    def next(self):
        r,loc=super().next();line,_=self.rows[self.pos-1]
        return Reader(self.source,line,loc),loc
    def item(self,desc,r,loc,path,depth):
        if desc in (D,P,R):
            try:
                value=r.data() if desc==D else r.expr(monetary=True) if desc==P and '/monetary/' in path else r.expr() if desc==P else r.row_expression()
                r.finish();self.locations[path]=loc;return value
            except Exception as exc:
                if isinstance(exc,Invalid):raise
                raise Invalid(str(exc),r.location()) from exc
        if desc==('construction',):
            profile=r.items[r.pos][1] if r.pos<len(r.items) else None
            need(profile in ('ParameterizedCompanyMethod/1','OrderedNestedMethodExpansion/1'),'construction_profile',r.location())
            return self.item(B('recipe' if profile=='ParameterizedCompanyMethod/1' else 'expansion'),r,loc,path,depth)
        if desc==('encoded_method',):
            value=self.item(B('method'),r,loc,path,depth);return recipe.encode(value)
        return super().item(desc,r,loc,path,depth)
    def parse(self,carry=False):
        r,loc=self.next();need(r.take('word')==('term_carry_policy' if carry else 'term_event_rule'),'source_header',loc);need(r.string()==PROFILE,'source_profile',loc)
        result=self.item(B('carry_policy' if carry else 'event_rule'),r,loc,'',0)
        need(self.pos==len(self.rows),'declaration_after_end',self.rows[self.pos][1] if self.pos<len(self.rows) else loc)
        return result

def datum(value):
    if isinstance(value,recipe.Parameter):return '(parameter '+j(value.name)+')'
    if not recipe.has_parameter(value):return j(value)
    if type(value) is list:return '(array '+' '.join(datum(x) for x in value)+')'
    return '(record '+' '.join('(field '+j(k)+' '+datum(v)+')' for k,v in value.items())+')'
def expression(value):
    op=value['op']
    if op=='ref':args=[datum(value['id'])]
    elif op=='const':args=[datum(value['type']),datum(value['value'])]
    elif op=='not':args=[expression(value['arg'])]
    elif op in ('all','any'):args=[expression(x) for x in value['args']]
    else:args=[expression(value['left']),expression(value['right'])]
    return '('+' '.join([op]+args)+')'
def row_expression(v):
    kind=v['expr']
    if kind=='literal':kind='const';args=[j(v['type']),j(v['value'])]
    elif kind in ('row','event_metadata'):args=[j(v['field'])]
    elif kind=='event_input':args=[j(v['name']),j(v['type'])]
    elif kind=='key':args=[]
    elif kind=='operation_id':args=[j(v['prefix'])]
    elif kind in ('date_lt','date_le'):args=[row_expression(v['left']),row_expression(v['right'])]
    elif kind=='if':args=[row_expression(v[x]) for x in ('condition','then','else')]
    elif kind=='array':args=[row_expression(x) for x in v['items']]
    elif kind=='object':args=['(field '+j(k)+' '+row_expression(x)+')' for k,x in v['fields'].items()]
    else:raise Invalid('row_operator:'+kind)
    return '('+' '.join([kind]+args)+')'

def render(rule,carry=False):
    rows=[]
    def emit(word,value,desc,depth):
        indent='  '*depth
        if type(desc) is str:
            text=datum(value) if desc==D else expression(value) if desc==P else row_expression(value) if desc==R else ct.value_text(value,desc)
            rows.append(indent+word+' '+text+';');return
        if desc==('construction',):
            return emit(word,value,B('recipe' if value['profile']=='ParameterizedCompanyMethod/1' else 'expansion'),depth)
        if desc==('encoded_method',):return emit(word,recipe.decode(value),B('method'),depth)
        if desc[0]=='block':
            profile,fields=ct.SCHEMAS[desc[1]]
            need(type(value) is dict,'block_required')
            if profile:need(value.get('profile')==profile and next(iter(value))=='profile','profile_order')
            rows.append(indent+word+(' '+j(profile) if profile else '')+';')
            for key,item in value.items():
                if key=='profile' and profile:continue
                need(key in fields,'unknown_field:'+key);emit(key,item,fields[key],depth+1)
        else:
            kind,entry,child=desc;rows.append(indent+word+';')
            if kind=='map':
                for key,item in value.items():emit(entry+' '+j(key),item,child,depth+1)
            else:
                for item in value:emit(entry,item,child,depth+1)
        rows.append(indent+'end;')
    emit(('term_carry_policy' if carry else 'term_event_rule')+' '+j(PROFILE),rule,B('carry_policy' if carry else 'event_rule'),0)
    source='\n'.join(rows)+'\n'
    need(ct.s.p.order_digest(Parser(source).parse(carry))==ct.s.p.order_digest(rule),'render_order_roundtrip')
    return source

def lower(source,carry=False):
    parser=Parser(source);rule=parser.parse(carry)
    return dict(profile=PROFILE,status='lowered_syntax_only',rule=rule,rule_sha256=core.digest(rule),
      rule_order_sha256=ct.s.p.order_digest(rule),source_sha256=sha256(source.encode()).hexdigest(),locations=parser.locations,
      executed=False,contextually_compiled=False,source_admission=False,accounting_admission=False)

def compile_rule(source,book,definition):
    lowered=lower(source)
    try:full.gate.compile_template(lowered['rule']['eligibility'],book,definition)
    except Exception as exc:raise Invalid(getattr(exc,'reason',str(exc)),lowered['locations']['/eligibility']) from exc
    return dict(lowered,status='eligibility_compiled',construction_contextually_compiled=False)

def execute_sources(contract_source,rule_sources,definition,state,request,coverage,selection,call):
    contract=ct.compile_text(contract_source,definition)['contract'];rules={};locations={}
    need(type(rule_sources) is dict and set(rule_sources)=={'assessment','amendment','collection','carry'},'source_rule_population')
    for name,source in rule_sources.items():
        item=lower(source,carry=name=='carry') if name=='carry' else compile_rule(source,state['book'],definition)
        rules[name]=item['rule'];locations[name]=item['locations']
    result=full.execute(contract,rules,state,request,coverage,selection,call)
    diagnostics=[]
    if result.get('failed_stage') in ('construction','eligibility'):
        name={'assess':'assessment','amend':'amendment','collect':'collection'}.get(request.get('operation'))
        if name:
            part='/construction' if result['failed_stage']=='construction' else '/eligibility'
            diagnostics.append(dict(source=name,reason=result.get('reason'),location=locations[name][part]))
    return dict(execution=result,source_diagnostics=diagnostics,
      source_sha256={name:sha256(source.encode()).hexdigest() for name,source in rule_sources.items()},
      contract_source_sha256=sha256(contract_source.encode()).hexdigest())
