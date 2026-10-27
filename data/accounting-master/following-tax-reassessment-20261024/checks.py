from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import json
from examples import cases,m
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def canonical(x):return m.continuation.caller.canonical(x)
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
        if 'continuation_result' in r:
            check(name+':exact_predecessor',canonical(r['continuation_result'])==canonical(m.continuation.run(q['continuation_request'])))
        if r['status']=='proposed':
            p=r['continuation_result'];old=p['after'];new=r['after'];v=r['tax_vintages'];j=r['journal']
            original=p['assessment_result']['carry_result']['loss_state'];lr=r['replacement_loss_result'];fc=r['financial_calculation']
            paid=sum(Q(s['amount']) for s in p['tax_vintages'][1]['settlements'])
            c0=Q(old['balances']['current_tax']);c1=Q(lr['conditional_gross_current_tax']);o=Q(p['tax_vintages'][0]['closing_payable'])
            check(name+':actual_opening',r['opening']==p['opening'])
            check(name+':old_vintage_exact',v[0]==p['tax_vintages'][0])
            check(name+':current_identity',v[1]['id']==p['tax_vintages'][1]['id'] and v[1]['assessment_id']==q['id'])
            check(name+':settlements_exact',v[1]['settlements']==p['tax_vintages'][1]['settlements'])
            check(name+':supersession_exact',v[1]['supersession_history'][0]['previous_vintage']==p['tax_vintages'][1])
            check(name+':current_conservation',Q(v[1]['new_assessment'])==c1 and Q(v[1]['closing_payable'])==c1-paid>=0)
            check(name+':aggregate_conservation',sum(Q(a['closing_payable']) for a in v)==-Q(new['balances']['income_tax_payable'])==o+c1-paid)
            check(name+':increment_only',Q(j['current_tax'])==c1-c0 and Q(j['income_tax_payable'])==c0-c1)
            check(name+':cash_and_flows_exact',new['balances']['cash']==old['balances']['cash'] and new['flows']==old['flows'])
            check(name+':journal_balanced',sum(Q(a) for a in j.values())==0)
            check(name+':book_balanced',sum(Q(a) for a in new['balances'].values())==0)
            check(name+':exact_account_set',set(new['balances'])==set(old['balances'])==set(m.carry.continuation.ACCOUNTS))
            check(name+':journal_effect',all(Q(new['balances'][k])-Q(a)==Q(j[k]) for k,a in old['balances'].items()))
            check(name+':other_balances',all(a==new['balances'][k] for k,a in old['balances'].items() if k not in ['current_tax','income_tax_payable']))
            check(name+':other_state',all(a==new[k] for k,a in old.items() if k not in ['balances','seen','date']))
            check(name+':assessment_identity',new['seen']==old['seen']+[q['id']] and new['date']==q['interval']['activity_through'])
            check(name+':original_loss_binding',r['original_loss_opening_sha256']==m.book.digest(original))
            check(name+':prior_loss_history',r['loss_state']['history'][:-1]==original['history'])
            check(name+':loss_cursor',r['loss_state']['cursor']==r['assessed_until']==q['interval']['end_exclusive'])
            t=lr['totals'];check(name+':loss_conservation',Q(t['opening'])+Q(t['generated'])==Q(t['used'])+Q(t['expired'])+Q(t['closing']))
            check(name+':tax_arithmetic',c1==max(Q(0),Q(r['calculation']['taxable_profit'])-Q(t['used']))*Q(r['calculation']['rate']))
            check(name+':four_ties',set(r['recorded_statements']['reconciliations'].values())=={'0/1'})
            check(name+':same_cash_report',r['recorded_statements']['cash_flows']==p['recorded_statements']['cash_flows'])
            check(name+':findings_deferred',r['findings']==p['findings'] and r['current_period_deferred_tax']=='unassessed')
            check(name+':complete_apply',canonical(m.apply(q,r))==canonical({**r,'status':'applied'}))
        else:check(name+':no_changed_state','after' not in r and 'tax_vintages' not in r)
        observations.append({**row,'result':r})
    by={row['case']:row['result'] for row in observations}
    check('independent_increase',by['increase']['financial_calculation']['replacement_total_payable']=='35/4' and by['increase']['journal']['current_tax']=='2/1' and by['increase']['recorded_statements']['recorded_profit']=='-19/1')
    check('independent_decrease',by['decrease']['financial_calculation']['replacement_total_payable']=='19/4' and by['decrease']['journal']['current_tax']=='-2/1')
    check('old_payable_cannot_hide_credit',by['overpaid_current']['financial_calculation']['replacement_current_payable']=='-1/1' and by['overpaid_current']['financial_calculation']['replacement_total_payable']=='11/4' and by['overpaid_current']['status']=='unsupported')
    check('loss_not_double_consumed',by['loss_reuse_from_opening']['loss_state']['lots'][0]['used']=='19/1' and by['loss_reuse_from_opening']['financial_calculation']['replacement_expense']=='1/4')
    check('loss_expiry_control',by['loss_expiry']['replacement_loss_result']['totals']['expired']=='19/1')
    check('return_control',by['native_return']['calculation']['taxable_profit']=='-18/1' and by['native_return']['recorded_statements']['recorded_profit']=='6/1')
    return checks,observations,tests,lock
