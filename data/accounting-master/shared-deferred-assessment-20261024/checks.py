from pathlib import Path
from hashlib import sha256
from fractions import Fraction as Q
import json
from examples import cases,m
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def canonical(x):return m.prior.continuation.caller.canonical(x)

def conformance():
    checks=[];observations=[]
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    lock=json.loads((HERE/'source-lock.json').read_text())
    for p,h in lock.items():check('protected:'+p,sha(ROOT/p)==h)
    tests=json.loads((HERE/'test-observation.json').read_text());check('tests_pass',tests['exit_code']==0)
    for p,h in tests['files'].items():check('tested_bytes:'+p,sha(ROOT/p)==h)
    for row in cases():
        q=row['request'];before=canonical(q);r=m.propose(q);name=row['case']
        check(name+':status',r['status']==row['expected_status'])
        check(name+':inputs_preserved',canonical(q)==before)
        check(name+':no_admission',all(r[k] is False for k in m.FLAGS if k not in ['conditional_deferred_assessed','deferred_asset_recognized']))
        if 'prior_result' in r:check(name+':exact_prior',canonical(r['prior_result'])==canonical(m.prior.propose(q['prior_request'])))
        if r['status']=='proposed':
            old=r['prior_result']['after'];new=r['after'];c=r['calculation'];items=c['items']
            check(name+':population',len(items)==len({i['id'] for i in items})==len(q['items']) and {i['id'] for i in items}=={i['id'] for i in m.population(r['prior_result'])})
            check(name+':item_arithmetic',all(Q(i['desired_dta'])==Q(i['rate'])*Q(i['recognized_deduction']) and Q(i['desired_dtl'])==Q(i['rate'])*Q(i['taxable_difference']) and Q(i['recognized_deduction'])+Q(i['unrecognized_deduction'])==Q(i['deductible_difference']) for i in items))
            def signed(i):
                if i['kind']=='loss':return -Q(i['carrying'])
                return (Q(i['carrying'])-Q(i['tax_base']))*(1 if i['kind']=='asset' else -1)
            check(name+':difference_signs',all(signed(i)==Q(i['taxable_difference'])-Q(i['deductible_difference']) and min(Q(i['taxable_difference']),Q(i['deductible_difference']))==0 for i in items))
            check(name+':gross_totals',sum(Q(i['desired_dta']) for i in items)==Q(c['desired_dta']) and sum(Q(i['desired_dtl']) for i in items)==Q(c['desired_dtl']))
            check(name+':recorded_allocation',sum(Q(i['recorded_dta']) for i in items)==Q(old['balances']['dta']) and sum(Q(i['recorded_dtl']) for i in items)==-Q(old['balances']['dtl']))
            check(name+':shared_capacity',sum(Q(i['recognized_deduction']) for i in items)==Q(c['recognized_deductions'])<=Q(c['recovery_capacity']) and Q(c['unused_capacity'])+Q(c['recognized_deductions'])==Q(c['recovery_capacity']))
            check(name+':gross_targets',new['balances']['dta']==c['desired_dta'] and -Q(new['balances']['dtl'])==Q(c['desired_dtl']))
            check(name+':incremental_journal',all(Q(new['balances'][k])-Q(v)==Q(r['journal'][k]) for k,v in old['balances'].items()))
            check(name+':journal_balanced',sum(Q(v) for v in r['journal'].values())==0)
            check(name+':book_balanced',sum(Q(v) for v in new['balances'].values())==0)
            check(name+':other_balances',all(v==new['balances'][k] for k,v in old['balances'].items() if k not in ['dta','dtl','deferred_tax']))
            check(name+':other_state',all(v==new[k] for k,v in old.items() if k not in ['balances','seen']))
            check(name+':lifetime_ids',new['seen']==old['seen']+[q['id']])
            check(name+':loss_history',r['loss_state']==r['prior_result']['loss_state'])
            check(name+':four_ties',set(r['recorded_statements']['reconciliations'].values())=={'0/1'})
            check(name+':cash_exact',r['recorded_statements']['cash_flows']==r['prior_result']['recorded_statements']['cash_flows'])
            check(name+':conditional_flag',r['conditional_deferred_assessed'] is True and r['deferred_asset_recognized']==(Q(c['desired_dta'])>0))
            a=m.apply(q,r);check(name+':complete_apply',a['status']=='applied' and all(a[k]==r[k] for k in ['after','prior_result','loss_state','calculation','findings','request_sha256']))
        else:check(name+':no_changed_state','after' not in r)
        observations.append({**row,'result':r})
    by={r['case']:r['result'] for r in observations}
    base=by['mixed_partial_recognition'];j=base['journal']
    check('independent_mixed_journal',(j['dta'],j['dtl'],j['deferred_tax'])==('-2/1','-6/1','8/1'))
    check('independent_mixed_report',base['recorded_statements']['recorded_profit']=='-33/4' and base['recorded_statements']['balance_sheet']=={'total_assets':'1397/2','total_liabilities':'459/4','equity_including_profit':'2335/4'})
    check('unchanged_balances_zero_journal',all(v=='0/1' for v in by['unchanged_balances']['journal'].values()))
    check('zero_rate_reversal',by['zero_rate']['journal']['deferred_tax']=='6/1')
    check('opposite_signs_control',by['opposite_signs']['calculation']['desired_dta']=='5/1' and by['opposite_signs']['calculation']['desired_dtl']=='5/1')
    check('losses_share_capacity',by['loss_recognition']['calculation']['desired_dta']=='21/2' and by['loss_recognition']['calculation']['recognized_deductions']=='42/1')
    check('fractional_measurement',by['fractional_rate']['calculation']['desired_dta']=='32/3' and by['fractional_rate']['calculation']['desired_dtl']=='40/3')
    return checks,observations,tests,lock
