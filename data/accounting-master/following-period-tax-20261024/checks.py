from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import json
from examples import cases,m
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def canonical(x):return m.carry.continuation.caller.canonical(x)
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
        check(name+':no_admission',all(r[k] is False for k in m.FLAGS if k not in ['conditional_current_assessed','provisional']))
        check(name+':provisional',r['provisional'] is True)
        if 'carry_result' in r:check(name+':exact_predecessor',canonical(r['carry_result'])==canonical(m.carry.run(q['carry_request'])))
        if r['status']=='proposed':
            old=r['carry_result']['after'];new=r['after'];opening=r['opening'];v=r['tax_vintages'];lr=r['loss_result'];calc=r['calculation']
            p0=-Q(opening['balances']['income_tax_payable']);paid=sum(Q(s['amount']) for s in v[0]['settlements']);tax=Q(lr['conditional_gross_current_tax'])
            check(name+':actual_opening',opening==r['carry_result']['opening'])
            check(name+':carried_vintage',v[0]['kind']=='carried' and Q(v[0]['opening_payable'])==p0 and Q(v[0]['closing_payable'])==p0-paid>=0)
            check(name+':new_vintage',v[1]['kind']=='current' and v[1]['interval']==q['interval'] and v[1]['settlements']==[] and Q(v[1]['closing_payable'])==tax)
            check(name+':vintage_sum',sum(Q(t['closing_payable']) for t in v)==-Q(new['balances']['income_tax_payable'])==p0-paid+tax)
            check(name+':no_prior_payment_credit',Q(r['journal']['current_tax'])==Q(new['balances']['current_tax'])==tax and Q(r['journal']['income_tax_payable'])==-tax)
            check(name+':journal_balanced',sum(Q(x) for x in r['journal'].values())==0)
            check(name+':book_balanced',sum(Q(x) for x in new['balances'].values())==0)
            check(name+':journal_matches_state',all(Q(new['balances'][k])-Q(x)==Q(r['journal'][k]) for k,x in old['balances'].items()))
            check(name+':other_balances',all(x==new['balances'][k] for k,x in old['balances'].items() if k not in ['current_tax','income_tax_payable']))
            check(name+':other_state',all(x==new[k] for k,x in old.items() if k not in ['balances','date','seen']))
            check(name+':id_and_day',new['seen']==old['seen']+[q['id']] and new['date']==q['interval']['activity_through'])
            check(name+':loss_history',r['loss_state']['history'][:-1]==r['carry_result']['loss_state']['history'] and r['loss_state']['cursor']==r['assessed_until']==q['interval']['end_exclusive'])
            t=lr['totals'];check(name+':loss_conservation',Q(t['opening'])+Q(t['generated'])==Q(t['used'])+Q(t['expired'])+Q(t['closing']))
            check(name+':tax_arithmetic',tax==max(Q(0),Q(calc['taxable_profit'])-Q(t['used']))*Q(calc['rate']))
            check(name+':four_ties',set(r['recorded_statements']['reconciliations'].values())=={'0/1'})
            check(name+':cash_exact',r['recorded_statements']['cash_flows']==r['carry_result']['recorded_statements']['cash_flows'])
            check(name+':unknowns_and_deferred',r['findings']==r['carry_result']['findings'] and r['current_period_deferred_tax']=='unassessed' and r['unresolved']==m.UNRESOLVED)
            applied=m.apply(q,r);check(name+':complete_apply',canonical(applied)==canonical({**r,'status':'applied'}))
        else:check(name+':no_changed_state','after' not in r)
        observations.append({**row,'result':r})
    by={row['case']:row['result'] for row in observations}
    for name,total in [('prior_paid','-5/1'),('prior_partial','-35/4'),('prior_unpaid','-39/4')]:
        r=by[name];check(name+':independent_tax',r['after']['balances']['current_tax']=='5/1' and r['after']['balances']['income_tax_payable']==total and r['recorded_statements']['recorded_profit']=='-15/1')
    check('independent_paid_statement',by['prior_paid']['recorded_statements']['balance_sheet']=={'total_assets':'2735/4','total_liabilities':'115/1','equity_including_profit':'2275/4'})
    check('carried_loss_used_once',by['loss_use']['journal']['current_tax']=='1/4' and by['loss_use']['loss_state']['lots'][0]['used']=='19/1')
    check('carried_loss_expired',by['loss_expiry']['loss_result']['totals']['expired']=='19/1')
    check('native_return_control',by['native_return']['calculation']['pretax_income']=='6/1' and by['native_return']['calculation']['taxable_profit']=='-18/1' and by['native_return']['loss_result']['totals']['generated']=='18/1')
    return checks,observations,tests,lock
