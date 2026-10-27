"""Explicit finite term/assessment query examples and independent bindings."""
from copy import deepcopy
import importlib.util
import compose as c
spec=importlib.util.spec_from_file_location('grouped_query_reference',c.HERE.parent/'grouped-row-query-20261026/fixtures.py')
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
p=c.p;core=c.core
def ref(k):return {'op':'ref','id':k}
def const(t,v):return {'op':'const','type':deepcopy(t),'value':v}
def binary(op,a,b):return {'op':op,'left':a,'right':b}
def rule(name,predicate,deps,guard=None,guard_deps=None):
    return dict(id=name,guard=const(core.BOOL,True) if guard is None else guard,guard_requires=guard_deps or [],
        predicate=predicate,requires=deps,admission_refs=[],on_false='invalid',on_unknown='unresolved')
def query_item(state,kind,owner,mode,field=None,**kw):
    return dict(projection=f.spec_for(state,kind),query=f.declaration(state,kind,owner,mode,field,**kw),on_ambiguous='invalid')
def assemble(state,queries,bindings,rules,required=None):
    inputs={}
    for key,b in bindings.items():
        typ=c.COUNT_TYPE if b['kind']=='count' else core.BOOL if b['kind']=='has_row' else queries[b['query']]['projection']['fields'][b['field']]['type']
        inputs[key]=dict(type=deepcopy(typ),role='state',source_ref='explicit query binding:'+key)
    manifest=dict(profile=c.guarded.PROFILE,method_id='finite.query.invariant',version='1',inputs=inputs,
        requirements=rules,required_known=required or [],capabilities=[],residual_prerequisites=['Supplied internal finite query relations only'])
    return dict(profile=c.PROFILE,context=deepcopy(state['book']['context']),manifest=manifest,queries=queries,bindings=bindings,
        residuals=['No dynamic parent/child enumeration or financial admission'])
def history_spec(state,owner,assessment):
    a=state['book']['memory']['claims'][owner]['assessments'][assessment]
    queries={'term':query_item(state,'terms',owner,'greatest','effective',bound=a['as_of'],allow_empty=False),
             'assessment':query_item(state,'assessments',owner,'match','identity',value=assessment,allow_empty=False),
             'term_count':query_item(state,'terms',owner,'count')}
    bindings={'count':dict(kind='count',query='term_count'),'has_term':dict(kind='has_row',query='term')}
    for name,query,field in [('due','term','due'),('selected_id','term','identity'),('referenced_id','assessment','term_id'),
                           ('as_of','assessment','as_of'),('remaining','assessment','remaining'),('overdue','assessment','overdue')]:
        bindings[name]=dict(kind='selected_field',query=query,field=field)
    money=p.base.money_type(state['book']);zero=const(money,'0/1')
    rules=[rule('terms_nonempty',binary('lt',const(c.COUNT_TYPE,'0/1'),ref('count')),['count']),
      rule('unique_term_exists',ref('has_term'),['has_term']),
      rule('historical_term_reference',binary('eq',ref('selected_id'),ref('referenced_id')),['selected_id','referenced_id']),
      rule('overdue_after_due',binary('eq',ref('overdue'),ref('remaining')),['overdue','remaining'],
           binary('lt',ref('due'),ref('as_of')),['due','as_of']),
      rule('zero_by_due',binary('eq',ref('overdue'),zero),['overdue'],
           binary('le',ref('as_of'),ref('due')),['as_of','due'])]
    return assemble(state,queries,bindings,rules)
def presence_spec(state,owner,value='initial',required=False):
    queries={'row':query_item(state,'terms',owner,'match','identity',value=value)}
    bindings={'present':dict(kind='has_row',query='row'),'due':dict(kind='selected_field',query='row',field='due')}
    return assemble(state,queries,bindings,[rule('selected_due_known',binary('eq',ref('due'),ref('due')),['due'],ref('present'),['present'])],['due'] if required else [])
def run(state,spec,coverage=None,selection=None,call=None):
    coverage={name:p.population(item['projection'],state['book'],'complete','Original supplied query-guard fixture') for name,item in spec['queries'].items()} if coverage is None else coverage
    selection=core.digest(spec) if selection is None else selection
    args=(spec,state['book'],state['memory_definition'],state['schemas'],coverage,selection)
    return c.assess(*args,c.make_call(*args) if call is None else call)
def reference(state,spec):
    outcomes={name:f.reference(state,item['projection']['child_pointer'][1:],item['query']) for name,item in spec['queries'].items()}
    vetoes=[]
    for name,outcome in outcomes.items():
        status=outcome['status']
        if status=='invalid':vetoes.append(dict(query=name,status='invalid',reason=outcome['reason']))
        elif status=='unresolved':vetoes.append(dict(query=name,status='unresolved',reason=outcome['reason']))
        elif status=='ambiguous':vetoes.append(dict(query=name,status=spec['queries'][name]['on_ambiguous'],reason='ambiguous_query'))
    if any(v['status']=='invalid' for v in vetoes):return dict(status='invalid',reason='query_failure',query_vetoes=vetoes)
    values={};lineage={}
    for name,b in spec['bindings'].items():
        outcome=outcomes[b['query']];status=outcome['status'];kind=b['kind']
        if status in ('unresolved','ambiguous'):value=dict(status='unknown',reason='query_'+status)
        elif kind=='count':value=dict(status='known',value=str(outcome['count'])+'/1')
        elif kind=='has_row':value=dict(status='known',value=status=='selected')
        elif status=='none':value=dict(status='unknown',reason='query_no_row')
        else:value=deepcopy(outcome['selected'][b['field']])
        values[name]=value;lineage[name]=dict(binding=deepcopy(b),query_status=status,type=deepcopy(spec['manifest']['inputs'][name]['type']))
        if kind=='selected_field' and status=='selected':
            lineage[name].update(source=deepcopy(outcome['selected_lineage']['fields'][b['field']]),
                parent_key=outcome['selected_lineage']['parent_key'],child_key=outcome['selected_lineage']['child_key'])
    manifest=spec['manifest'];h=core.digest(manifest);assessment=c.guarded.assess({h:manifest},h,values,[])
    statuses=[v['status'] for v in vetoes]+[assessment['status']]
    status=next((s for s in ('invalid','unsupported','unresolved') if s in statuses),assessment['status'])
    return dict(status=status,bound_values=values,lineage=lineage,assessment=assessment,query_vetoes=vetoes)
