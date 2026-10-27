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
        q=row['request'];before=canonical(q);r=m.run(q);name=row['case']
        check(name+':status',r['status']==row['expected_status'])
        check(name+':inputs_preserved',canonical(q)==before)
        check(name+':no_admission',all(r[k] is False for k in m.FLAGS if k not in ['recorded_balance_carry','provisional']))
        check(name+':provisional',r['provisional'] is True)
        if 'prior_result' in r:check(name+':exact_predecessor',canonical(r['prior_result'])==canonical(m.assessment.propose(q['prior_request'])))
        if r['status']=='complete_provisional':
            p=r['prior_result'];old=p['after'];new=r['after'];j=r['carry_journal'];classes=m.classes(p)
            profit=-sum(Q(old['balances'][k]) for k in classes['income'])
            check(name+':actual_profit',Q(r['carried_recorded_profit'])==profit==Q(p['recorded_statements']['recorded_profit']))
            check(name+':retained_transfer',Q(new['balances']['retained'])==Q(old['balances']['retained'])-profit)
            check(name+':zero_income',all(new['balances'][k]=='0/1' for k in classes['income']))
            check(name+':permanent_accounts',all(v==new['balances'][k] for k,v in old['balances'].items() if k not in classes['income']+['retained']))
            check(name+':journal_balanced',sum(Q(v) for v in j.values())==0)
            check(name+':book_balanced',sum(Q(v) for v in new['balances'].values())==0)
            check(name+':exact_account_set',set(new['balances'])==set(old['balances'])==set(m.carry.continuation.ACCOUNTS))
            check(name+':journal_effect',all(Q(new['balances'][k])-Q(v)==Q(j[k]) for k,v in old['balances'].items()))
            check(name+':opening_equals_after',r['opening']==new)
            check(name+':components_exact',all(new[k]==old[k] for k in ['component','lots','leases','other_inventory','context']))
            check(name+':next_period',new['period']==q['next_period'] and new['date']==new['tax_closed_until']==q['next_period']['start'])
            check(name+':lifetime_ids',new['seen']==old['seen']+[q['id']])
            check(name+':past_years',new['prior_years'][:-1]==old['prior_years'])
            check(name+':current_movements_reset',new['flows']==new['tax_adjustments']==[] and new['opening_interest_paid']=='0/1')
            check(name+':loss_exact',r['loss_state']==p['loss_state'] and r['loss_state']['cursor']==new['period']['start'])
            check(name+':vintages_exact',r['tax_vintages']==p['tax_vintages'])
            check(name+':period_vintage_ids',[v['id'] for v in r['period_vintages']]==[v['id'] for v in r['tax_vintages']])
            check(name+':period_vintage_openings',all(n['prior_vintage_sha256']==m.book.digest(o) and n['opening_payable']==n['closing_payable']==o['closing_payable'] and n['settlements']==[] for o,n in zip(r['tax_vintages'],r['period_vintages'])))
            check(name+':vintage_sum',sum(Q(v['opening_payable']) for v in r['period_vintages'])==-Q(new['balances']['income_tax_payable']))
            check(name+':archive_movements',r['archive']['prior_flows']==old['flows'] and r['archive']['prior_tax_adjustments']==old['tax_adjustments'])
            check(name+':archive_recognition',r['archive']['recognition_calculation']==p['calculation'] and r['archive']['recognition_capacity']==p['recovery_capacity'] and r['archive']['recognition_measurement']==p['measurement'])
            check(name+':no_renewed_assessment',r['current_period_tax']==r['current_period_deferred_tax']=='unassessed')
            check(name+':findings_exact',r['findings']==q['findings'] and r['prior_findings']=={'carry':p['prior_findings'],'deferred':p['findings']})
            report=r['recorded_statements'];check(name+':four_ties',set(report['reconciliations'].values())=={'0/1'})
            check(name+':same_balance_sheet',report['balance_sheet']==p['recorded_statements']['balance_sheet'])
            check(name+':zero_current_reports',report['recorded_profit']==report['cash_flows']['net_movement']==report['indirect_operating']['net']=='0/1')
            check(name+':complete_apply',canonical(m.apply(q,r))==canonical({**r,'status':'applied_provisional'}))
        else:check(name+':no_new_opening','after' not in r and 'opening' not in r)
        observations.append({**row,'result':r})
    by={row['case']:row['result'] for row in observations}
    for name,profit,retained in [('negative_profit','-17/1','53/4'),('positive_profit','6/1','-107/4'),('zero_profit','0/1','-15/4')]:
        check(name+':independent_sign',by[name]['carried_recorded_profit']==profit and by[name]['after']['balances']['retained']==retained)
    check('paid_history_preserved',len(by['fully_paid_vintages']['tax_vintages'])==2 and all(v['opening_payable']=='0/1' for v in by['fully_paid_vintages']['period_vintages']))
    return checks,observations,tests,lock
