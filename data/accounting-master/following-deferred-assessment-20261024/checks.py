from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import json
from examples import cases,m
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def canonical(x):return m.prior.continuation.caller.canonical(x)
def conformance():
    checks=[];observations=[]
    def check(n,v):checks.append({'name':n,'passed':bool(v)})
    lock=json.loads((HERE/'source-lock.json').read_text())
    for p,h in lock.items():check('protected:'+p,sha(ROOT/p)==h)
    tests=json.loads((HERE/'test-observation.json').read_text());check('tests_pass',tests['exit_code']==0)
    for p,h in tests['files'].items():check('tested_bytes:'+p,sha(ROOT/p)==h)
    for row in cases():
        q=row['request'];before=canonical(q);r=m.propose(q);name=row['case']
        check(name+':status',r['status']==row['expected_status'])
        check(name+':inputs_preserved',canonical(q)==before)
        allowed=['conditional_current_assessed','conditional_deferred_assessed','deferred_asset_recognized','provisional']
        check(name+':no_admission',all(r[k] is False for k in m.FLAGS if k not in allowed))
        check(name+':provisional',r['provisional'] is True)
        if 'prior_result' in r:check(name+':exact_predecessor',canonical(r['prior_result'])==canonical(m.prior.propose(q['prior_request'])))
        if r['status']=='proposed':
            p=r['prior_result'];old=p['after'];new=r['after'];calc=r['calculation'];j=r['journal'];items=calc['items']
            a0=Q(old['balances']['dta']);l0=-Q(old['balances']['dtl']);a1=Q(calc['desired_dta']);l1=Q(calc['desired_dtl'])
            check(name+':actual_opening',r['opening']==p['opening'])
            check(name+':bound_measurement',r['measurement']==q['measurement'] and r['measurement']['state_sha256']==m.book.digest(old) and r['measurement']['at']==old['date'])
            check(name+':complete_population',[i['id'] for i in items]==[i['id'] for i in m.population(p)])
            check(name+':recognized_amounts',all(0<=Q(i['recognized_deduction'])<=Q(i['deductible_difference']) for i in items))
            check(name+':desired_sums',a1==sum(Q(i['rate'])*Q(i['recognized_deduction']) for i in items) and l1==sum(Q(i['rate'])*Q(i['taxable_difference']) for i in items))
            check(name+':shared_capacity',sum(Q(i['recognized_deduction']) for i in items)==Q(calc['recognized_deductions'])<=Q(calc['recovery_capacity']))
            check(name+':recorded_allocations',sum(Q(i['recorded_dta']) for i in items)==a0 and sum(Q(i['recorded_dtl']) for i in items)==l0)
            check(name+':desired_balances',Q(new['balances']['dta'])==a1 and -Q(new['balances']['dtl'])==l1)
            check(name+':journal_deltas',Q(j['dta'])==a1-a0 and Q(j['dtl'])==l0-l1 and Q(j['deferred_tax'])==l1-l0-a1+a0)
            check(name+':journal_balanced',sum(Q(v) for v in j.values())==0)
            check(name+':book_balanced',sum(Q(v) for v in new['balances'].values())==0)
            check(name+':same_account_set',set(new['balances'])==set(old['balances'])==set(m.prior.carry.continuation.ACCOUNTS))
            check(name+':journal_effect',all(Q(new['balances'][k])-Q(v)==Q(j[k]) for k,v in old['balances'].items()))
            check(name+':other_balances',all(v==new['balances'][k] for k,v in old['balances'].items() if k not in ['dta','dtl','deferred_tax']))
            check(name+':other_state',all(v==new[k] for k,v in old.items() if k not in ['balances','seen']))
            check(name+':new_identity',new['seen']==old['seen']+[q['id']])
            check(name+':vintages_loss_findings',r['tax_vintages']==p['tax_vintages'] and r['loss_state']==p['loss_state'] and r['prior_findings']==p['findings'])
            check(name+':cash_report_exact',r['recorded_statements']['cash_flows']==p['recorded_statements']['cash_flows'])
            check(name+':four_ties',set(r['recorded_statements']['reconciliations'].values())=={'0/1'})
            check(name+':fresh_capacity',r['recovery_capacity']==q['recovery_capacity'])
            archive=p['continuation_result']['assessment_result']['carry_result']['archive']
            check(name+':historical_capacity_retained',r['historical_recognition']['capacity']==archive['prior_recovery_capacity'] and r['historical_recognition']['calculation']==archive['prior_deferred_calculation'])
            check(name+':complete_apply',canonical(m.apply(q,r))==canonical({**r,'status':'applied'}))
        else:check(name+':no_changed_state','after' not in r)
        observations.append({**row,'result':r})
    by={row['case']:row['result'] for row in observations};r=by['remeasure_carried']
    check('independent_balance_movements',r['journal']['dta']=='-3/1' and r['journal']['dtl']=='5/1' and r['journal']['deferred_tax']=='-2/1')
    check('independent_statements',r['recorded_statements']['recorded_profit']=='-17/1' and r['recorded_statements']['balance_sheet']=={'total_assets':'1361/2','total_liabilities':'455/4','equity_including_profit':'2267/4'})
    check('fresh_payable_base',r['measurement']['account_bases']['income_tax_payable']['value']=='35/4' and r['prior_result']['continuation_result']['after']['balances']['income_tax_payable']=='-27/4')
    check('combined_loss_debt_capacity',by['loss_and_debt']['calculation']['desired_dta']=='29/4' and by['capacity_reused']['status']=='invalid')
    check('unchanged_zero_journal',set(by['unchanged']['journal'].values())=={'0/1'})
    return checks,observations,tests,lock
