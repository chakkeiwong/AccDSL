"""Typed scalar substitution over complete supplied nested row/group iterations."""
from copy import deepcopy
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'query-guard-composition-20261026'))
import compose as c
p=c.p;core=c.core
PROFILE='NestedQueryInvariantTemplate/1';CALL='NestedQueryInvariantCall/1'
MAX_INSTANCES=64;MAX_SLOTS=64

def const_targets(spec):
    targets={}
    def visit(node,path):
        if node['op']=='const':targets[p.types.pointer(path+['value'])]=node['type']
        elif node['op']=='not':visit(node['arg'],path+['arg'])
        elif node['op'] in ('all','any'):
            for i,arg in enumerate(node['args']):visit(arg,path+['args',str(i)])
        elif node['op']!='ref':
            visit(node['left'],path+['left']);visit(node['right'],path+['right'])
    for i,r in enumerate(spec['manifest']['requirements']):
        for part in ('guard','predicate'):visit(r[part],['manifest','requirements',str(i),part])
    return targets

def capture_type(binding,mode,parent,child,definition):
    core.need(type(binding) is dict,'capture_record')
    kind=binding.get('kind')
    core.need(kind in ('parent_key','child_key','parent_field','child_field','book_field'),'capture_kind')
    core.closed(binding,['kind','type']+(['pointer'] if kind.endswith('_field') else []),'capture')
    p.base.dimensions.typed(binding['type'])
    core.need(mode=='rows' or not kind.startswith('child_'),'child_capture_requires_rows')
    if kind.endswith('_key'):actual=p.guards.TEXT
    elif kind=='book_field':
        path=binding['pointer'];p.exact_pointer(path)
        if path in ('/date','/period/start','/period/end_exclusive'):actual=p.guards.DATE
        else:
            core.need(path.startswith('/memory/'),'book_capture_path')
            node=p.record_path(definition['root'],path[len('/memory'):])
            core.need(node['node']=='scalar','book_capture_scalar');actual=node['type']
    else:
        node=p.record_path(parent['values'] if kind=='parent_field' else child['values'],binding['pointer'])
        core.need(node['node']=='scalar','capture_scalar');actual=node['type']
    core.need(binding['type']==actual,'capture_type')
    return actual

def validate(spec,definition):
    p.base.memory.bounded(spec)
    core.closed(spec,['profile','context','iteration','mode','captures','template','slots','residuals'],'nested_template')
    core.need(spec['profile']==PROFILE and spec['mode'] in ('groups','rows'),'nested_template_profile_mode')
    core.need(spec['context']==spec['iteration']['context']==spec['template']['context'],'nested_template_context')
    parent,child=p.compile_spec(spec['iteration'],definition);c.validate(spec['template'],definition)
    captures=spec['captures'];core.need(type(captures) is dict,'captures_record')
    for name,binding in captures.items():
        core.text(name,'capture_name');capture_type(binding,spec['mode'],parent,child,definition)
    targets=const_targets(spec['template'])
    for name,item in spec['template']['queries'].items():
        query=item['query'];mode=query['mode'];prefix=['queries',name,'query']
        core.need(item['projection']['parent_pointer']==spec['iteration']['parent_pointer'],'shared_parent_population')
        if mode=='match' and query['value']['binding']['status']=='known':
            targets[p.types.pointer(prefix+['value','binding','value'])]=query['value']['type']
        if mode=='greatest' and query['upper_bound'] is not None and query['upper_bound']['binding']['status']=='known':
            targets[p.types.pointer(prefix+['upper_bound','binding','value'])]=query['upper_bound']['type']
    slots=spec['slots'];core.need(type(slots) is list and 0<len(slots)<=MAX_SLOTS,'template_slot_limit')
    groups=set();scalars=set();used=set()
    for slot in slots:
        core.need(type(slot) is dict,'slot_record');kind=slot.get('kind')
        if kind=='group':
            core.closed(slot,['kind','query'],'group_slot');name=slot['query'];core.text(name,'slot_query')
            core.need(name in spec['template']['queries'],'slot_query_missing')
            core.need(name not in groups,'duplicate_group_slot');groups.add(name)
        else:
            core.need(kind=='scalar','slot_kind');core.closed(slot,['kind','capture','target'],'scalar_slot')
            name=slot['capture'];core.text(name,'slot_capture');core.need(name in captures,'slot_capture_missing')
            target=slot['target'];p.exact_pointer(target)
            core.need(target in targets,'unsafe_scalar_slot');core.need(target not in scalars,'duplicate_scalar_slot')
            core.need(targets[target]==captures[name]['type'],'slot_capture_type')
            scalars.add(target);used.add(name)
    core.need(groups==set(spec['template']['queries']),'inexact_group_slots')
    core.need(used==set(captures),'unused_capture')
    core.identifiers(spec['residuals'],'template_residuals',True)

def make_call(spec,book,definition,schemas,coverage,query_coverages,reviewed_selection):
    result=dict(profile=CALL,book_order_sha256=p.order_digest(book),spec_order_sha256=p.order_digest(spec),reviewed_selection=reviewed_selection)
    for n,v in [('spec',spec),('book',book),('definition',definition),('schemas',schemas),('coverage',coverage),('query_coverages',query_coverages)]:
        result[n+'_sha256']=core.digest(v)
    return result

def captured(binding,group,child_lineage,book):
    kind=binding['kind'];typ=binding['type']
    if kind=='parent_key':value=group['parent_key'];path=group['parent_path']
    elif kind=='child_key':value=child_lineage['child_key'];path=child_lineage['child_path']
    else:
        if kind=='book_field':path=binding['pointer']
        else:path=(group['parent_path'] if kind=='parent_field' else child_lineage['child_path'])+binding['pointer']
        found,value=p.base.binding.located(book,path);core.need(found,'captured_value_missing')
        if path.startswith('/memory/'):
            core.need(book['memory_types'][path[len('/memory'):]]==typ,'captured_leaf_type')
    core.scalar(value,typ['kind'])
    return dict(value=deepcopy(value),type=deepcopy(typ),kind=kind,path=path)

def replace_scalar(root,pointer,value):
    tokens=p.exact_pointer(pointer);node=root
    for token in tokens[:-1]:node=node[int(token)] if type(node) is list else node[token]
    key=tokens[-1]
    if type(node) is list:node[int(key)]=deepcopy(value)
    else:node[key]=deepcopy(value)

def evaluate(spec,book,definition,schemas,coverage,query_coverages,reviewed_selection,call):
    result=dict(profile=PROFILE,**p.FLAGS,method_eligible=False);stage='call'
    try:
        core.need(call==make_call(spec,book,definition,schemas,coverage,query_coverages,reviewed_selection),'stale_template_call')
        result.update({k:v for k,v in call.items() if k!='profile'})
        core.need(reviewed_selection==core.digest(spec),'reviewed_template_selection')
        stage='declaration';validate(spec,definition)
        core.need(spec['context']==book['context'],'template_book_context')
        core.need(type(query_coverages) is dict and set(query_coverages)==set(spec['template']['queries']),'inexact_template_coverages')
        stage='population'
        args=(spec['iteration'],book,definition,schemas,coverage)
        projection=p.project(*args,p.make_call(*args));result['iteration_projection']=projection
        if projection['status']!='projected':return dict(result,status=projection['status'],reason=projection['reason'],failed_stage=stage)
        # Validate each query population even when iteration produces no instance.
        population_results={};population_statuses=[]
        for name,item in spec['template']['queries'].items():
            args=(item['projection'],book,definition,schemas,query_coverages[name])
            projected=p.project(*args,p.make_call(*args));population_results[name]=projected
            if projected['status']!='projected':population_statuses.append(projected['status'])
        result['query_populations']=population_results
        if population_statuses:
            status='invalid' if 'invalid' in population_statuses else 'unresolved'
            return dict(result,status=status,reason='query_population_unavailable',failed_stage=stage)
        stage='instances';work=[]
        for group in projection['groups']:
            if spec['mode']=='groups':work.append((group,None))
            else:
                for i in range(group['row_start'],group['row_start']+group['row_count']):work.append((group,projection['lineage'][i]))
        core.need(len(work)<=MAX_INSTANCES,'template_instance_limit')
        instances=[];statuses=[]
        for index,(group,child) in enumerate(work):
            captures={n:captured(b,group,child,book) for n,b in spec['captures'].items()}
            instantiated=deepcopy(spec['template'])
            for slot in spec['slots']:
                if slot['kind']=='group':
                    item=instantiated['queries'][slot['query']]
                    item['query']['group']=dict(parent_key=group['parent_key'],parent_path=group['parent_path'],
                        child_map_path=group['parent_path']+item['projection']['child_pointer'])
                else:replace_scalar(instantiated,slot['target'],captures[slot['capture']]['value'])
            selection=core.digest(instantiated)
            args=(instantiated,book,definition,schemas,query_coverages,selection)
            assessment=c.assess(*args,c.make_call(*args));statuses.append(assessment['status'])
            instances.append(dict(index=index,parent_key=group['parent_key'],child_key=None if child is None else child['child_key'],
                captures=captures,declaration=instantiated,derived_selection=selection,
                selection_basis='Deterministic substitution from reviewed template; not independent instance review',result=assessment))
        status=next((s for s in ('invalid','unsupported','unresolved') if s in statuses),
                    'requirements_satisfied' if 'requirements_satisfied' in statuses else 'no_active_requirements')
        return dict(result,status=status,failed_stage=None,instance_count=len(instances),instances=instances,
                    residuals=deepcopy(spec['residuals']))
    except (ValueError,TypeError,KeyError,IndexError,RecursionError,OverflowError) as exc:
        return dict(result,status='invalid',reason=str(exc)[:300],failed_stage=stage)
