"""Explicit typed bindings from recomputed queries into preserved v3 rules."""
from copy import deepcopy
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'grouped-row-query-20261026'))
import query as q
import method_requirements_v3 as guarded
p=q.p;core=q.core
PROFILE='QueryGuardedInvariant/1';CALL='QueryGuardedInvariantCall/1';MAX_QUERIES=32
COUNT_TYPE={'kind':'rational','context':{},'dimensions':{},'scale':'1/1'}

def validate(spec,definition):
    p.base.memory.bounded(spec)
    core.closed(spec,['profile','context','manifest','queries','bindings','residuals'],'query_invariant')
    core.need(spec['profile']==PROFILE,'query_invariant_profile')
    core.need(type(spec['context']) is dict,'invariant_context_record')
    guarded.compile_manifest(spec['manifest'])
    queries=spec['queries'];bindings=spec['bindings'];inputs=spec['manifest']['inputs']
    core.need(type(queries) is dict and 0<len(queries)<=MAX_QUERIES,'invariant_query_limit')
    for name,item in queries.items():
        core.text(name,'query_name')
        core.closed(item,['projection','query','on_ambiguous'],'invariant_query')
        core.need(item['on_ambiguous'] in ('invalid','unresolved'),'ambiguity_policy')
        core.need(item['query']['context']==spec['context'],'invariant_query_context')
        q.compile_query(item['query'],item['projection'],definition)
    core.need(type(bindings) is dict and set(bindings)==set(inputs),'inexact_invariant_bindings')
    used=set()
    for name,binding in bindings.items():
        core.need(type(binding) is dict,'invariant_binding_record')
        kind=binding.get('kind');core.need(kind in ('count','has_row','selected_field'),'invariant_binding_kind')
        core.closed(binding,['kind','query']+(['field'] if kind=='selected_field' else []),'invariant_binding')
        core.text(binding['query'],'binding_query')
        core.need(binding['query'] in queries,'undeclared_query')
        used.add(binding['query']);item=queries[binding['query']];mode=item['query']['mode']
        if kind=='count':
            core.need(mode=='count','count_query_required');typ=COUNT_TYPE
        else:
            core.need(mode in ('match','greatest'),'selection_query_required');typ=core.BOOL
            if kind=='selected_field':
                core.text(binding['field'],'selected_field')
                core.need(binding['field'] in item['projection']['fields'],'undeclared_selected_field')
                typ=item['projection']['fields'][binding['field']]['type']
        core.need(inputs[name]['role']=='state','invariant_input_role')
        core.need(inputs[name]['type']==typ,'invariant_binding_type')
    core.need(used==set(queries),'unused_invariant_query')
    core.identifiers(spec['residuals'],'invariant_residuals',True)

def make_call(spec,book,definition,schemas,coverages,reviewed_selection):
    result=dict(profile=CALL,book_order_sha256=p.order_digest(book),
                spec_order_sha256=p.order_digest(spec),reviewed_selection=reviewed_selection)
    for name,value in [('spec',spec),('book',book),('definition',definition),('schemas',schemas),('coverages',coverages)]:
        result[name+'_sha256']=core.digest(value)
    return result

def assess(spec,book,definition,schemas,coverages,reviewed_selection,call):
    result=dict(profile=PROFILE,**p.FLAGS,method_eligible=False);stage='call'
    try:
        core.need(call==make_call(spec,book,definition,schemas,coverages,reviewed_selection),'stale_invariant_call')
        result.update({k:v for k,v in call.items() if k!='profile'})
        core.need(reviewed_selection==core.digest(spec),'reviewed_invariant_selection')
        stage='declaration';validate(spec,definition)
        core.need(spec['context']==book['context'],'invariant_context')
        core.need(type(coverages) is dict and set(coverages)==set(spec['queries']),'inexact_query_coverages')
        outcomes={};vetoes=[];stage='queries'
        for name,item in spec['queries'].items():
            args=(item['projection'],book,definition,schemas,coverages[name])
            pc=p.make_call(*args);queryargs=(item['query'],*args,pc)
            outcome=q.evaluate(*queryargs,q.make_call(*queryargs));outcomes[name]=outcome
            status=outcome['status']
            if status=='invalid':vetoes.append(dict(query=name,status='invalid',reason=outcome['reason']))
            elif status=='unresolved':vetoes.append(dict(query=name,status='unresolved',reason=outcome['reason']))
            elif status=='ambiguous':vetoes.append(dict(query=name,status=item['on_ambiguous'],reason='ambiguous_query'))
        result.update(query_results=outcomes,query_vetoes=vetoes)
        if any(v['status']=='invalid' for v in vetoes):
            return dict(result,status='invalid',reason='query_failure',failed_stage=stage)
        stage='bindings';values={};lineage={}
        for name,binding in spec['bindings'].items():
            outcome=outcomes[binding['query']];status=outcome['status'];kind=binding['kind']
            if status in ('unresolved','ambiguous'):value=dict(status='unknown',reason='query_'+status)
            elif kind=='count':value=dict(status='known',value=str(outcome['count'])+'/1')
            elif kind=='has_row':value=dict(status='known',value=status=='selected')
            elif status=='none':value=dict(status='unknown',reason='query_no_row')
            else:value=deepcopy(outcome['selected'][binding['field']])
            values[name]=value
            lineage[name]=dict(binding=deepcopy(binding),query_status=status,type=deepcopy(spec['manifest']['inputs'][name]['type']))
            if kind=='selected_field' and status=='selected':
                lineage[name]['source']=deepcopy(outcome['selected_lineage']['fields'][binding['field']])
                lineage[name]['parent_key']=outcome['selected_lineage']['parent_key']
                lineage[name]['child_key']=outcome['selected_lineage']['child_key']
        stage='assessment';manifest=spec['manifest'];h=core.digest(manifest)
        evaluation=guarded.assess({h:manifest},h,values,[])
        core.need('findings' in evaluation,'guarded_assessment_failed:'+evaluation.get('reason',''))
        statuses=[v['status'] for v in vetoes]+[evaluation['status']]
        status=next((s for s in ('invalid','unsupported','unresolved') if s in statuses),evaluation['status'])
        return dict(result,status=status,failed_stage=None,bound_values=values,lineage=lineage,assessment=evaluation,
                    residuals=deepcopy(spec['residuals']))
    except (ValueError,TypeError,KeyError,IndexError,RecursionError,OverflowError) as exc:
        return dict(result,status='invalid',reason=str(exc)[:300],failed_stage=stage)
