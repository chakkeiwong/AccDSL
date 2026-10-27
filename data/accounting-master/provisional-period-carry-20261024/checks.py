from pathlib import Path
from hashlib import sha256
from fractions import Fraction as Q
import json
from examples import cases,m
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def canonical(x):return m.continuation.caller.canonical(x)

def conformance():
    checks=[];observations=[]
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    lock=json.loads((HERE/'source-lock.json').read_text())
    for path,h in lock.items():check('protected:'+path,sha(ROOT/path)==h)
    tests=json.loads((HERE/'test-observation.json').read_text())
    check('tests_pass',tests['exit_code']==0)
    for path,h in tests['files'].items():check('tested_bytes:'+path,sha(ROOT/path)==h)
    for row in cases():
        body=row['request'];before=canonical(body);r=m.run(body);name=row['case']
        check(name+':status',r['status']==row['expected_status'])
        check(name+':inputs_preserved',canonical(body)==before)
        check(name+':no_promotion',all(r[k] is False for k in m.FLAGS if k not in ['provisional','recorded_balance_carry']))
        check(name+':always_provisional',r['provisional'] is True)
        if 'prior_result' in r:
            expected=m.assessment.propose(body['prior_request'])
            check(name+':complete_upstream',canonical(r['prior_result'])==canonical(expected))
        if r['status'] in ['complete_provisional','stopped_provisional']:
            old=r['prior_result']['after'];o=r['opening'];a=r['after']
            income=r['prior_result']['continuation_result']['native_report']['account_classes']['income']
            profit=-sum(Q(old['balances'][k]) for k in income)
            check(name+':recorded_transfer',Q(o['balances']['retained'])==Q(old['balances']['retained'])-profit and Q(r['carried_recorded_profit'])==profit)
            check(name+':income_zero',all(Q(o['balances'][k])==0 for k in income))
            check(name+':other_balances_exact',all(v==o['balances'][k] for k,v in old['balances'].items() if k not in income+['retained']))
            check(name+':complete_journal',all(Q(o['balances'][k])-Q(v)==Q(r['carry_journal'][k]) for k,v in old['balances'].items()))
            check(name+':balanced_transfer',sum(Q(v) for v in r['carry_journal'].values())==0)
            check(name+':balanced_open_and_close',sum(Q(v) for v in o['balances'].values())==sum(Q(v) for v in a['balances'].values())==0)
            changed={'balances','period','date','tax_closed_until','flows','tax_adjustments','opening_interest_paid','tax_premises','seen','prior_years'}
            check(name+':all_other_state_exact',all(o[k]==v for k,v in old.items() if k not in changed))
            check(name+':archive_exact',r['archive']['prior_flows']==old['flows'] and r['archive']['prior_tax_adjustments']==old['tax_adjustments'] and o['flows']==o['tax_adjustments']==[])
            check(name+':archive_binding',r['archive']['prior_result_sha256']==m.book.digest(r['prior_result']) and r['archive']['closing_sha256']==m.book.digest(old) and r['archive']['report_sha256']==m.book.digest(r['prior_result']['recorded_statements']))
            check(name+':loss_state_exact',r['loss_state']==r['prior_result']['loss_state'])
            check(name+':period_contiguous',o['period']==body['next_period'] and o['period']['start']==old['period']['end_exclusive']==r['loss_state']['cursor'])
            check(name+':empty_tax_interval',o['tax_closed_until']==o['period']['start'] and r['current_period_tax']=='unassessed')
            check(name+':lifetime_ids',o['seen']==old['seen']+[body['id']])
            check(name+':prior_years_append',o['prior_years']==old['prior_years']+[{'period':old['period'],'closing_sha256':m.book.digest(old),'report_sha256':m.book.digest(r['prior_result']['recorded_statements'])}])
            check(name+':opening_allocations',o['tax_premises']=={**old['tax_premises'],'opening_dta':old['balances']['dta'],'opening_dtl':m.book.fmt(-Q(old['balances']['dtl']))} and o['opening_interest_paid']=='0/1')
            check(name+':findings_preserved',r['findings']==body['findings'] and r['unresolved']==m.OBLIGATIONS)
            check(name+':four_statement_ties',set(r['recorded_statements']['reconciliations'].values())=={'0/1'})
            check(name+':prefix_partition',[t['operation'] for t in r['trace']]+r['remaining_operations']==body['operations'])
            check(name+':prefix_state',a==(r['trace'][-1]['result']['after'] if r['trace'] else o))
            check(name+':stop_status',(r['stop']['status'] if r['stop'] else None)==row['expected_stop'])
            check(name+':new_cash_only',Q(r['recorded_statements']['cash_flows']['net_movement'])==Q(a['balances']['cash'])-Q(o['balances']['cash']))
            applied=m.apply(body,r)
            check(name+':complete_apply',applied['status']=='applied_provisional' and all(applied[k]==r[k] for k in ['opening','after','loss_state','findings','unresolved','archive','prior_result','request_sha256']))
        observations.append({**row,'result':r})
    by={r['case']:r['result'] for r in observations}
    check('negative_transfer',by['negative_profit']['opening']['balances']['retained']=='-47/4')
    check('positive_transfer',by['positive_profit']['opening']['balances']['retained']=='-17/1')
    check('zero_transfer',by['zero_profit']['opening']['balances']['retained']=='-12/1')
    paid=by['pay_carried_tax']
    check('payment_independent_control',paid['after']['balances']['cash']=='1423/4' and paid['recorded_statements']['recorded_profit']=='0/1' and paid['recorded_statements']['indirect_operating']['net']=='-19/4')
    dep=by['payment_and_depreciation']['recorded_statements']
    check('depreciation_independent_control',dep['recorded_profit']=='-10/1' and dep['balance_sheet']=={'total_assets':'2743/4','total_liabilities':'104/1','equity_including_profit':'2327/4'})
    returned=by['return_activity_after_carry']
    check('return_independent_control',returned['after']['balances']['cash']=='482/1' and returned['recorded_statements']['recorded_profit']=='6/1' and returned['recorded_statements']['indirect_operating']['net']=='-18/1')
    check('generated_loss_exact',sum(Q(l['remaining']) for l in by['generated_loss']['loss_state']['lots'])==19)
    check('used_loss_not_reused',by['used_loss_history']['loss_state']['lots'][0]['used']=='19/1')
    check('partial_payment_prefix',by['completed_prefix']['after']['balances']['cash']=='719/2' and by['completed_prefix']['after']['balances']['income_tax_payable']=='-15/4')
    return checks,observations,tests,lock
