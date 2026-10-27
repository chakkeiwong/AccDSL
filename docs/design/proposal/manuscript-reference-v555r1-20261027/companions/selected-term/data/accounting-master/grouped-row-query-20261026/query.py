"""Typed finite queries over freshly recomputed supplied nested populations."""
from copy import deepcopy
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'nested-map-projection-20261026'))
import projection as p
core=p.core
PROFILE='GroupedRowQuery/1';CALL='GroupedRowQueryCall/1'

def typed_input(item,expected):
    core.closed(item,['type','binding'],'typed_query_input')
    p.base.dimensions.typed(item['type'])
    core.need(item['type']==expected,'query_input_type')
    binding=item['binding'];core.need(type(binding) is dict,'query_binding')
    if binding.get('status')=='known':
        core.closed(binding,['status','value'],'known_query_input')
        return True,core.scalar(binding['value'],expected['kind'])
    core.closed(binding,['status','reason'],'unknown_query_input')
    core.need(binding['status']=='unknown','query_input_status')
    core.text(binding['reason'],'query_unknown_reason')
    return False,None

def compile_query(query,spec,definition):
    p.base.memory.bounded(query);p.compile_spec(spec,definition)
    core.need(type(query) is dict,'query_record')
    mode=query.get('mode');core.need(mode in ('count','match','greatest'),'query_mode')
    extra=[] if mode=='count' else ['field','allow_empty','value' if mode=='match' else 'upper_bound']
    core.closed(query,['profile','context','group','mode']+extra,'query_fields')
    core.need(query['profile']==PROFILE,'query_profile')
    core.need(query['context']==spec['context'],'query_context')
    group=query['group'];core.closed(group,['parent_key','parent_path','child_map_path'],'query_group')
    core.text(group['parent_key'],'query_parent_key')
    expected='/memory'+p.types.pointer(p.exact_pointer(spec['parent_pointer'])+[group['parent_key']])
    core.need(group['parent_path']==expected,'query_parent_path')
    core.need(group['child_map_path']==expected+spec['child_pointer'],'query_child_map_path')
    if mode=='count':return True,None
    core.need(type(query['allow_empty']) is bool,'query_allow_empty')
    core.text(query['field'],'query_field')
    core.need(query['field'] in spec['fields'],'query_field_missing')
    typ=spec['fields'][query['field']]['type']
    if mode=='match':return typed_input(query['value'],typ)
    core.need(typ['kind'] in ('date','rational'),'query_nonorderable_field')
    bound=query['upper_bound']
    if bound is None:return True,None
    core.closed(bound,['type','binding','inclusive'],'query_upper_bound')
    core.need(type(bound['inclusive']) is bool,'query_bound_inclusive')
    return typed_input({k:bound[k] for k in ('type','binding')},typ)

def make_call(query,spec,book,definition,schemas,coverage,projection_call):
    return dict(profile=CALL,query_sha256=core.digest(query),query_order_sha256=p.order_digest(query),
        projection_call_sha256=core.digest(projection_call),
        expected_projection_call_sha256=core.digest(p.make_call(spec,book,definition,schemas,coverage)))

def evaluate(query,spec,book,definition,schemas,coverage,projection_call,call):
    result=dict(profile=PROFILE,**p.FLAGS);stage='call'
    try:
        core.need(call==make_call(query,spec,book,definition,schemas,coverage,projection_call),'stale_query_call')
        result.update({k:v for k,v in call.items() if k!='profile'})
        stage='declaration';known,operand=compile_query(query,spec,definition)
        stage='projection';projection=p.project(spec,book,definition,schemas,coverage,projection_call)
        result['projection']=projection
        if projection['status']!='projected':
            return dict(result,status=projection['status'],reason=projection['reason'],failed_stage=stage)
        stage='group'
        groups=[g for g in projection['groups'] if all(g[k]==v for k,v in query['group'].items())]
        core.need(len(groups)==1,'query_group_missing')
        group=groups[0];result['group']=deepcopy(group)
        if not known:return dict(result,status='unresolved',reason='query_input_unknown',failed_stage='input')
        stage='selection';mode=query['mode']
        indices=list(range(group['row_start'],group['row_start']+group['row_count']))
        if mode=='count':
            return dict(result,status='counted',count=len(indices),candidate_indices=indices,candidate_count=len(indices),
                selected_indices=[],selected=None,selected_lineage=None,failed_stage=None)
        field=query['field'];kind=spec['fields'][field]['type']['kind']
        values={i:core.scalar(projection['rows'][i][field]['value'],kind) for i in indices}
        if mode=='match':candidates=[i for i in indices if values[i]==operand]
        elif query['upper_bound'] is None:candidates=indices
        elif query['upper_bound']['inclusive']:candidates=[i for i in indices if values[i]<=operand]
        else:candidates=[i for i in indices if values[i]<operand]
        selected=candidates
        if mode=='greatest' and candidates:
            greatest=max(values[i] for i in candidates)
            selected=[i for i in candidates if values[i]==greatest]
        details=dict(candidate_indices=candidates,candidate_count=len(candidates),selected_indices=selected,
            selected=None,selected_lineage=None)
        if not selected:
            return dict(result,**details,status='none' if query['allow_empty'] else 'invalid',
                reason='no_matching_row' if query['allow_empty'] else 'required_row_missing',failed_stage=stage)
        if len(selected)>1:return dict(result,**details,status='ambiguous',reason='multiple_selected_rows',failed_stage=stage)
        details.update(selected=deepcopy(projection['rows'][selected[0]]),
            selected_lineage=deepcopy(projection['lineage'][selected[0]]))
        return dict(result,**details,status='selected',failed_stage=None)
    except (ValueError,TypeError,KeyError,IndexError,RecursionError,OverflowError) as exc:
        return dict(result,status='invalid',reason=str(exc)[:300],failed_stage=stage)
