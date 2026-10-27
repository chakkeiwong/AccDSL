from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import json
from examples import cases,m
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def canonical(x):return m.caller.canonical(x)
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
        check(name+':no_admission',all(r[k] is False for k in m.FLAGS if k not in ['conditional_current_assessed','provisional']))
        check(name+':provisional',r['provisional'] is True)
        if 'assessment_result' in r:
            check(name+':exact_predecessor',canonical(r['assessment_result'])==canonical(m.assessment.propose(q['assessment_request'])))
        if r['status'] in ['complete_provisional','stopped_provisional']:
            p=r['assessment_result'];state=p['after'];vintages=p['tax_vintages']
            check(name+':actual_opening',r['opening']==p['opening'])
            check(name+':tax_scope',r['assessed_until']==p['assessed_until'] and r['current_period_deferred_tax']=='unassessed')
            check(name+':loss_findings',r['loss_state']==p['loss_state'] and r['findings']==p['findings'])
            check(name+':remaining_exact',r['remaining_operations']==q['operations'][len(r['trace']):])
            check(name+':stop_status',(r['stop']['status'] if r['stop'] else None)==row['expected_stop'])
            check(name+':stop_index',r['stop'] is None or r['stop']['index']==len(r['trace']))
            for i,t in enumerate(r['trace']):
                tag=name+':step'+str(i);op=t['operation'];s=t['result'];after=s['after'];new=s['tax_vintages'];j=s['journal']
                check(tag+':ordered_operation',op==q['operations'][i])
                check(tag+':bound_inputs',s['before_sha256']==m.book.digest(state) and s['before_vintages_sha256']==m.book.digest(vintages) and s['operation_sha256']==m.book.digest(op))
                check(tag+':account_set',set(after['balances'])==set(state['balances'])==set(m.continuation.ACCOUNTS))
                check(tag+':balanced',sum(Q(a) for a in j.values())==sum(Q(a) for a in after['balances'].values())==0)
                check(tag+':journal_effect',all(Q(after['balances'][k])-Q(a)==Q(j[k]) for k,a in state['balances'].items()))
                check(tag+':cash_flow',Q(j['cash'])==sum(Q(f['amount']) for f in s['flows']))
                check(tag+':history_append',after['flows']==state['flows']+s['flows'] and after['seen'][:-1]==state['seen'])
                check(tag+':no_tax_expense_change',all(j[k]=='0/1' for k in ['current_tax','deferred_tax','dta','dtl']))
                check(tag+':vintage_sum',sum(Q(v['closing_payable']) for v in new)==-Q(after['balances']['income_tax_payable']))
                check(tag+':conservation',all(Q(v['opening_payable'])+Q(v['new_assessment'])-sum(Q(a['amount']) for a in v['settlements'])==Q(v['closing_payable'])>=0 for v in new))
                if op['kind']=='allocated_tax_payment':
                    e=op['event'];allocation={a['vintage_id']:Q(a['amount']) for a in e['allocations']}
                    check(tag+':explicit_sum',sum(allocation.values())==Q(e['amount'])==Q(j['income_tax_payable'])==-Q(j['cash']))
                    check(tag+':vintage_deltas',all(Q(a['closing_payable'])-Q(b['closing_payable'])==allocation.get(a['id'],0) for a,b in zip(vintages,new)))
                    check(tag+':prior_settlements',all(b['settlements'][:len(a['settlements'])]==a['settlements'] for a,b in zip(vintages,new)))
                    check(tag+':other_balances',all(j[k]=='0/1' for k in j if k not in ['cash','income_tax_payable']))
                else:check(tag+':native_vintages_unchanged',new==vintages and j['income_tax_payable']=='0/1')
                state=after;vintages=new
            check(name+':exact_prefix',r['after']==state and r['tax_vintages']==vintages)
            check(name+':four_ties',set(r['recorded_statements']['reconciliations'].values())=={'0/1'})
            check(name+':complete_apply',canonical(m.apply(q,r))==canonical({**r,'status':'applied_provisional'}))
        else:check(name+':no_changed_state','after' not in r)
        observations.append({**row,'result':r})
    by={row['case']:row['result'] for row in observations};r=by['split_payment_then_native']
    check('independent_split_balances',r['after']['balances']['cash']=='715/2' and r['after']['balances']['income_tax_payable']=='-27/4' and r['after']['balances']['current_tax']=='5/1')
    check('independent_split_statements',r['recorded_statements']['recorded_profit']=='-17/1' and r['recorded_statements']['balance_sheet']=={'total_assets':'1367/2','total_liabilities':'467/4','equity_including_profit':'2267/4'})
    check('equal_totals_distinct_vintages',by['old_only']['after']['balances']==by['current_only']['after']['balances'] and by['old_only']['tax_vintages']!=by['current_only']['tax_vintages'])
    check('independent_return',by['native_return']['after']['balances']['cash']=='482/1' and by['native_return']['recorded_statements']['recorded_profit']=='1/1')
    return checks,observations,tests,lock
