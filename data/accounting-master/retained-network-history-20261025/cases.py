"""Preserve full-source unknowns and explicit candidate conflicts."""
from copy import deepcopy
import examples
adapter=examples.adapter;BUDGET=examples.BUDGET
def cases():
    rows=[]
    def add(name,body,status,budget=BUDGET):
        result=adapter.assess(body,budget);assert result['status']==status,(name,result['status'],result.get('reason'))
        assert adapter.verify_result(body,budget,result),name
        rows.append({'case':name,'request':body,'budget':budget,'expected':status,'result':result})
    for mode,mapped,status in [
        ('closing',False,'conditional_candidates_with_unresolved_facts'),
        ('opening',False,'conditional_candidates_with_unresolved_facts'),
        ('opening',True,'supplied_history_incompatible'),
        ('equity',True,'supplied_history_incompatible'),
        ('full',False,'unresolved'),
        ('numeric',False,'conditional_candidates_with_unresolved_facts')]:
        add(mode+('-mapped' if mapped else '-unmapped'),examples.fixture(mode,mapped),status)
    base=deepcopy(rows[0]['request'])
    add('no_cells',deepcopy(base),'unknown',{**BUDGET,'max_cells':0})
    b=deepcopy(base);selected=b['source_request']['selected_relations'][0]
    b['source_request']['mapping_hypotheses'][selected]=None;add('missing_premise',b,'unresolved')
    b=deepcopy(base);b['histories'].pop(next(iter(b['histories'])));add('missing_context',b,'invalid')
    b=deepcopy(base);next(iter(b['histories'].values()))['history']['value_type']['context']['basis']='other';add('changed_context',b,'invalid')
    b=deepcopy(base);b['source_request']['statement_request']['source']['request_sha256']='0'*64;add('changed_source',b,'invalid')
    return rows
