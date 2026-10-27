"""Complete accepted, incompatible, unresolved and invalid exchanges."""
from copy import deepcopy
import examples
adapter=examples.adapter;BUDGET=examples.BUDGET
def cases():
    rows=[]
    def add(name,body,status,budget=BUDGET):
        result=adapter.assess(body,budget);assert result['status']==status,(name,result.get('reason'),result['status'])
        assert adapter.verify_result(body,budget,result),name
        rows.append({'case':name,'request':body,'budget':budget,'expected':status,'result':result})
    for group in ['annual','interim']:
        b=examples.fixture(group);add(group,b,'conditional_candidates_with_unresolved_facts')
    base=deepcopy(rows[0]['request'])
    add('both_contexts',examples.combined_fixture(),'conditional_candidates_with_unresolved_facts')
    add('cash_only_conflicts_equity',examples.fixture(conflicting=True),'supplied_history_incompatible')
    b=deepcopy(base);b['balance_bindings']['annual.cash_closing']={}
    add('unmapped_operands',b,'conditional_candidates_with_unresolved_facts')
    b=deepcopy(base);b['balance_request']['rounding_hypothesis']=None
    add('missing_rounding',b,'unresolved')
    b=deepcopy(base);b['balance_request']['identity_hypotheses']['annual.balance:equity']=None
    add('missing_identity',b,'unresolved')
    b=deepcopy(base);next(iter(b['balance_bindings']['annual.cash_closing'].values()))['premise']=None
    add('missing_mapping',b,'unresolved')
    add('no_cells',deepcopy(base),'unknown',{**BUDGET,'max_cells':0})
    b=deepcopy(base);next(iter(b['balance_bindings']['annual.cash_closing'].values()))['terms'][0]['coefficient']['type']['context']['basis']='different'
    add('wrong_context',b,'invalid_history_attachment')
    b=deepcopy(base);b['balance_request']['statement_request']['source']['request_sha256']='0'*64
    add('changed_source',b,'invalid')
    b=deepcopy(base);b['balance_bindings']['annual.cash_closing']['unknown']={}
    add('unknown_mapping',b,'invalid')
    for index in [0,1]:
        row=deepcopy(rows[index]);row['case']+='-alternate-gross'
        for result in row['result']['attachments'].values():
            d=result['definition'];result['witness']=examples.witness(d,100)
            result['replay']=adapter.attachment.replay_witness(d,BUDGET,result['witness'])
        assert adapter.verify_result(row['request'],BUDGET,row['result']);rows.append(row)
    return rows
