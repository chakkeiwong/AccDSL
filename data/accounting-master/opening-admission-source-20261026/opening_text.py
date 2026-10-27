"""Direct source declarations for the selected opening-admission contract."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'ordered-eligibility-source-20261026'))
import eligibility_text as syntax
sys.path.insert(0,str(HERE.parent/'declared-opening-admission-20261026'))
import admission
core=admission.core; rules=syntax.rules; j=syntax.j
Invalid=syntax.Invalid; need=syntax.need
PROFILE='OpeningAdmissionText/1'
ARGUMENTS={
    'record_fields':('path','fields'), 'record_values':('path',),
    'text':('path','label'), 'equals':('path','value'), 'typed_book':(),
    'map_values':('path','values'), 'role_population':('roles',),
    'role_injective':(), 'role_classes':(), 'cash_role':('role',),
    'memory_leaf':(), 'memory_type':('type',), 'opening_report':(),
    'commands':('maximum',)}


class Reader(syntax.Reader):
    def opening_binding(self):
        self.take('('); index=self.pos; kind=self.take('word'); source={'kind':kind}
        if kind=='path':
            source['path']=self.take('value')
        elif kind=='role_balance':
            source['role']=self.string()
        else:
            need(kind=='memory_pointer','unsupported_binding_source:'+kind,self.location(index))
        source['type']=self.take('value'); self.take(')')
        return source


def lower(source):
    location=None
    try:
        rows=syntax.source_rows(source); state='header'; template=None; stage=None
        spans=[]; stage_spans=[]; fields={}; ids=set()
        def unique(obj,key,value):
            need(key not in obj,'duplicate_declaration:'+key,location);obj[key]=value
        for line,location in rows:
            if not line.strip():continue
            spans.append(location);need(state!='done','declaration_after_end',location)
            r=Reader(source,line,location);word=r.take('word')
            if state=='header':
                need(word=='opening_admission' and r.string()==PROFILE,'source_profile',location)
                template=dict(profile=r.string(),dependency_pins=[],stages=[],residuals=[])
                need(template['profile']==admission.PROFILE,'opening_profile',location);state='body'
            elif state=='body':
                if word=='context':
                    unique(template,'context',r.take('value'));fields['context']=location
                elif word=='dependency':
                    template['dependency_pins'].append(dict(file=r.string(),sha256=r.string(),reason=r.string()))
                elif word=='residual':
                    template['residuals'].append(r.string())
                elif word=='stage':
                    name=r.string();op=r.take('word');reason=r.string()
                    need(name not in ids,'duplicate_stage',location);ids.add(name)
                    need(len(ids)<=64,'stage_population',location)
                    need(op in ARGUMENTS or op=='predicate','unsupported_stage:'+op,r.location(2))
                    stage=dict(id=name,op=op,reason=reason);template['stages'].append(stage)
                    if op=='predicate':stage['bindings']={}
                    elif op=='record_values':stage['values']={}
                    elif op=='role_classes':stage['classes']=[]
                    stage_start=location;check_seen=False;state='stage'
                else:
                    need(word=='end_opening','unknown_declaration:'+word,r.location(0))
                    need('context' in template and template['dependency_pins'] and template['stages'],'incomplete_template',location)
                    state='done'
            elif state=='stage':
                op=stage['op']
                if word=='check':
                    need(op!='predicate','predicate_uses_rules',location)
                    need(not check_seen,'duplicate_check',location);check_seen=True
                    for name in ARGUMENTS[op]:stage[name]=r.take('value')
                elif word=='record_value':
                    need(op=='record_values','record_value_stage',location)
                    unique(stage['values'],r.string(),r.take('value'))
                elif word=='role_class':
                    need(op=='role_classes','role_class_stage',location)
                    stage['classes'].append(dict(role=r.string(),classification=r.string()))
                elif word=='bind':
                    need(op=='predicate','binding_predicate_stage',location)
                    unique(stage['bindings'],r.string(),r.opening_binding())
                elif word=='begin_rules':
                    need(op=='predicate','rules_predicate_stage',location)
                    need('manifest' not in stage,'duplicate_rules',location)
                    manifest=dict(profile=r.string(),method_id=r.string(),version=r.string(),inputs={},
                                  requirements=[],required_known=[],capabilities=[],residual_prerequisites=[])
                    need(manifest['profile']=='MethodRequirements/3','explicit_guard_profile',location)
                    known_seen=False;state='rules'
                else:
                    need(word=='end_stage','stage_declaration:'+word,r.location(0))
                    need('manifest' in stage if op=='predicate' else check_seen,'stage_body_required',location)
                    stage_spans.append(syntax.span(source,stage_start['byte_start'],location['byte_end'],stage_start['line'],'stage'))
                    stage=None;state='body'
            elif state=='rules':
                if word=='input':
                    key=r.string();unique(manifest['inputs'],key,dict(type=r.take('value'),role=r.take('word'),source_ref=r.string()))
                elif word=='guarded':
                    manifest['requirements'].append(dict(id=r.string(),on_false=r.take('word'),on_unknown=r.take('word'),
                        guard_requires=r.take('value'),requires=r.take('value'),admission_refs=r.take('value'),
                        guard=r.expression(),predicate=r.expression()))
                elif word=='required_known':
                    need(not known_seen,'duplicate_required_known',location)
                    manifest['required_known']=r.take('value');known_seen=True
                elif word in ('capability','residual'):
                    manifest['capabilities' if word=='capability' else 'residual_prerequisites'].append(r.string())
                else:
                    need(word=='end_rules','rules_declaration:'+word,r.location(0))
                    need(known_seen,'explicit_required_known_declaration',location)
                    stage['manifest']=manifest;manifest=None;state='stage'
            r.finish()
        eof=syntax.span(source,len(source.encode()),len(source.encode()),source.count('\n')+1,'token')
        need(state=='done','incomplete_source:'+state,eof)
        return dict(profile=PROFILE,status='lowered_structural',template=template,template_sha256=core.digest(template),
                    source_sha256=sha256(source.encode()).hexdigest(),source_spans=spans,stage_spans=stage_spans,field_spans=fields,
                    executed=False,opening_admitted=False,source_admission=False,accounting_admission=False)
    except Exception as exc:
        if isinstance(exc,Invalid):raise
        raise Invalid(getattr(exc,'reason',str(exc)),location) from exc


def compile_text(source):
    lowered=lower(source);template=lowered['template']
    header=deepcopy(template);header['stages']=[]
    try:
        admission.compile_template(header)
    except Exception as exc:
        reason=getattr(exc,'reason',str(exc))
        if reason!='stage_population':
            raise Invalid(reason,syntax.span(source,0,len(source.encode()),1,'document')) from exc
    for index in range(len(template['stages'])):
        prefix=deepcopy(template);prefix['stages']=prefix['stages'][:index+1]
        try:
            admission.compile_template(prefix)
        except Exception as exc:
            raise Invalid(getattr(exc,'reason',str(exc)),lowered['stage_spans'][index]) from exc
    admission.compile_template(template)
    return dict(lowered,status='compiled_structural')


def assess_source(source,body,call):
    compiled=compile_text(source)
    return admission.assess(compiled['template'],body,call)


def render(template):
    rows=[]
    def add(word,*values):rows.append(word+(' '+' '.join(j(x) for x in values) if values else '')+';')
    add('opening_admission',PROFILE,template['profile']);add('context',template['context'])
    for pin in template['dependency_pins']:add('dependency',pin['file'],pin['sha256'],pin['reason'])
    for residual in template['residuals']:add('residual',residual)
    for stage in template['stages']:
        op=stage['op'];rows.append('stage '+j(stage['id'])+' '+op+' '+j(stage['reason'])+';')
        if op=='predicate':
            for name,binding in stage['bindings'].items():
                kind=binding['kind'];args=[]
                if kind=='path':args.append(j(binding['path']))
                elif kind=='role_balance':args.append(j(binding['role']))
                else:need(kind=='memory_pointer','unsupported_binding_source')
                args.append(j(binding['type']))
                rows.append('bind '+j(name)+' ('+' '.join([kind]+args)+');')
            d=stage['manifest'];add('begin_rules',d['profile'],d['method_id'],d['version'])
            exchange=dict(profile=rules.EXCHANGE,definition=d,selected_digest=core.digest(d),values={},available_capabilities=[])
            rows.extend(rules.render(exchange).rstrip('\n').split('\n')[1:-2]);add('end_rules')
        else:
            add('check',*[stage[name] for name in ARGUMENTS[op]])
            if op=='record_values':
                for key,value in stage['values'].items():add('record_value',key,value)
            elif op=='role_classes':
                for row in stage['classes']:add('role_class',row['role'],row['classification'])
        add('end_stage')
    add('end_opening');source='\n'.join(rows)+'\n'
    need(core.canonical(lower(source)['template'])==core.canonical(template),'render_roundtrip')
    return source
