"""Original-dictionary reference; no projected rows enter this comparator."""
from copy import deepcopy
from datetime import date
from fractions import Fraction
import query as q
p=q.p

def pointer(parts):return '/'+ '/'.join(x.replace('~','~0').replace('/','~1') for x in parts)

def spec_for(state,kind):
    parent=state['memory_definition']['root']['fields']['claims']['values']
    child=parent['fields'][kind]['values']
    fields={'owner':dict(kind='parent_key',type=p.guards.TEXT),
            'identity':dict(kind='child_key',type=p.guards.TEXT),
            'parent_issued':dict(kind='parent_field',pointer='/issued',type=p.guards.DATE)}
    for name,node in child['fields'].items():
        fields[name]=dict(kind='child_field',pointer='/'+name,type=deepcopy(node['type']))
    return dict(profile=p.PROFILE,context=deepcopy(state['book']['context']),parent_pointer='/claims',
        child_pointer='/'+kind,fields=fields,residuals=['Supplied structural query fixture; financial validity is separate'])

def configure(state):
    derived=p.types.derive(state['memory_definition'],state['book']['memory'],state['book'])
    assert derived['status']=='typed',derived
    state['book'].update(memory_types=derived['memory_types'],memory_schema=derived['schema_sha256'])
    state['schemas'][derived['schema_sha256']]=derived['schema']
    return state

def declaration(state,kind,owner,mode,field=None,value=None,bound=None,inclusive=True,allow_empty=True):
    path='/memory'+pointer(['claims',owner])
    result=dict(profile=q.PROFILE,context=deepcopy(state['book']['context']),mode=mode,
        group=dict(parent_key=owner,parent_path=path,child_map_path=path+'/'+kind))
    if mode=='count':return result
    typ=spec_for(state,kind)['fields'][field]['type']
    result.update(field=field,allow_empty=allow_empty)
    if mode=='match':result['value']=dict(type=deepcopy(typ),binding=dict(status='known',value=value))
    else:result['upper_bound']=None if bound is None else dict(type=deepcopy(typ),binding=dict(status='known',value=bound),inclusive=inclusive)
    return result

def reference(state,kind,decl):
    rows=[];lineage=[];groups=[]
    for owner,parent in state['book']['memory']['claims'].items():
        start=len(rows);parent_path='/memory'+pointer(['claims',owner])
        for child_key,child in parent[kind].items():
            child_path=parent_path+'/'+kind+pointer([child_key])
            raw={'owner':owner,'identity':child_key,'parent_issued':parent['issued'],**child}
            fields={}
            for field in raw:
                if field=='owner':path=parent_path;typ=p.guards.TEXT;binding='parent_key'
                elif field=='identity':path=child_path;typ=p.guards.TEXT;binding='child_key'
                elif field=='parent_issued':path=parent_path+'/issued';typ=p.guards.DATE;binding='parent_field'
                else:path=child_path+'/'+field;typ=state['book']['memory_types'][path[len('/memory'):]];binding='child_field'
                fields[field]=dict(path=path,kind=binding,type=deepcopy(typ))
            rows.append({k:dict(status='known',value=v) for k,v in raw.items()})
            lineage.append(dict(parent_key=owner,child_key=child_key,parent_path=parent_path,child_path=child_path,fields=fields))
        groups.append(dict(parent_key=owner,parent_path=parent_path,child_map_path=parent_path+'/'+kind,
            row_start=start,row_count=len(rows)-start))
    matched=[g for g in groups if g['parent_key']==decl['group']['parent_key']]
    if not matched:return dict(status='invalid',reason='query_group_missing')
    group=matched[0];indices=list(range(group['row_start'],group['row_start']+group['row_count']))
    common=dict(group=group,selected_indices=[],selected=None,selected_lineage=None,failed_stage=None)
    if decl['mode']=='count':
        return dict(common,status='counted',count=len(indices),candidate_indices=indices,candidate_count=len(indices))
    field=decl['field']
    typ=spec_for(state,kind)['fields'][field]['type']['kind']
    def convert(v):return Fraction(v) if typ=='rational' else date.fromisoformat(v) if typ=='date' else v
    raw=decl.get('value') if decl['mode']=='match' else decl['upper_bound']
    if raw is not None and raw['binding']['status']=='unknown':
        return dict(status='unresolved',reason='query_input_unknown',group=group,failed_stage='input')
    operand=None if raw is None else convert(raw['binding']['value'])
    candidates=[];winners=[];best=None
    for index in indices:
        v=convert(rows[index][field]['value'])
        if decl['mode']=='match':eligible=v==operand
        elif raw is None:eligible=True
        else:eligible=v<=operand if raw['inclusive'] else v<operand
        if not eligible:continue
        candidates.append(index)
        if decl['mode']=='match':winners.append(index)
        elif best is None or v>best:best=v;winners=[index]
        elif v==best:winners.append(index)
    common.update(candidate_indices=candidates,candidate_count=len(candidates),selected_indices=winners)
    if not winners:
        common.update(status='none' if decl['allow_empty'] else 'invalid',failed_stage='selection',
            reason='no_matching_row' if decl['allow_empty'] else 'required_row_missing')
    elif len(winners)>1:common.update(status='ambiguous',reason='multiple_selected_rows',failed_stage='selection')
    else:common.update(status='selected',selected=rows[winners[0]],selected_lineage=lineage[winners[0]])
    return common

def run(state,kind,decl,spec=None,coverage=None,projection_call=None,call=None):
    spec=spec_for(state,kind) if spec is None else spec
    coverage=p.population(spec,state['book'],'complete','Original supplied fixture dictionaries') if coverage is None else coverage
    args=(spec,state['book'],state['memory_definition'],state['schemas'],coverage)
    projection_call=p.make_call(*args) if projection_call is None else projection_call
    args=(decl,*args,projection_call)
    return q.evaluate(*args,q.make_call(*args) if call is None else call)
