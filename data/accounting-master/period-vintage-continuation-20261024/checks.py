from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
from copy import deepcopy
import json
from examples import cases,m
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def canonical(x):return m.caller.canonical(x)

def conformance():
    checks=[];observations=[]
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    lock=json.loads((HERE/'source-lock.json').read_text())
    for p,h in lock.items():check('protected:'+p,sha(ROOT/p)==h)
    tests=json.loads((HERE/'test-observation.json').read_text());check('tests_pass',tests['exit_code']==0)
    for p,h in tests['files'].items():check('tested_bytes:'+p,sha(ROOT/p)==h)
    for row in cases():
        q=row['request'];before=canonical(q);r=m.run(q);name=row['case']
        check(name+':status',r['status']==row['expected_status'])
        check(name+':inputs_preserved',canonical(q)==before)
        check(name+':no_promotion',all(r[k] is False for k,v in m.FLAGS.items() if v is False))
        if 'boundary_result' in r:
            check(name+':exact_predecessor',canonical(r['boundary_result'])==canonical(m.boundary.run(q['boundary_request'])))
        if r['status'] in ['complete_provisional','stopped_provisional']:
            p=r['boundary_result'];state=p['after'];vs=p['period_vintages'];historical=p['tax_vintages']
            for key in ['opening','tax_vintages','loss_state','archive','findings','finding_status','prior_findings']:
                check(name+':preserved_'+key,canonical(r[key])==canonical(p[key]))
            check(name+':unassessed',r['current_period_tax']==r['current_period_deferred_tax']=='unassessed')
            check(name+':remaining_exact',r['remaining_operations']==q['operations'][len(r['trace']):])
            check(name+':stop_status',(r['stop']['status'] if r['stop'] else None)==row['expected_stop'])
            check(name+':stop_index',r['stop'] is None or r['stop']['index']==len(r['trace']))
            for i,t in enumerate(r['trace']):
                tag=name+':step'+str(i);op=t['operation'];s=t['result'];after=s['after'];new=s['period_vintages'];j=s['journal']
                check(tag+':ordered_operation',op==q['operations'][i])
                check(tag+':bound_inputs',s['before_sha256']==m.book.digest(state) and s['before_vintages_sha256']==m.book.digest(vs) and s['operation_sha256']==m.book.digest(op) and s['historical_vintages_sha256']==m.book.digest(historical))
                check(tag+':account_set',set(after['balances'])==set(state['balances'])==set(m.continuation.ACCOUNTS))
                check(tag+':balanced',sum(Q(a) for a in j.values())==sum(Q(a) for a in after['balances'].values())==0)
                check(tag+':journal_effect',all(Q(after['balances'][k])-Q(a)==Q(j[k]) for k,a in state['balances'].items()))
                check(tag+':cash_flow',Q(j['cash'])==sum(Q(f['amount']) for f in s['flows']))
                check(tag+':append_history',after['flows']==state['flows']+s['flows'] and after['seen'][:-1]==state['seen'])
                check(tag+':no_tax_expense_change',all(j[k]=='0/1' for k in ['current_tax','deferred_tax','dta','dtl']))
                check(tag+':vintage_sum',sum(Q(v['closing_payable']) for v in new)==-Q(after['balances']['income_tax_payable']))
                check(tag+':conservation',all(Q(v['opening_payable'])-sum(Q(a['amount']) for a in v['settlements'])==Q(v['closing_payable'])>=0 for v in new))
                check(tag+':historical_bindings',all(v['id']==h['id'] and v['prior_vintage_sha256']==m.book.digest(h) and v['opening_payable']==h['closing_payable'] and v['period']==after['period'] for v,h in zip(new,historical)))
                if op['kind']=='allocated_tax_payment':
                    e=op['event'];allocation={a['vintage_id']:Q(a['amount']) for a in e['allocations']}
                    check(tag+':explicit_sum',sum(allocation.values())==Q(e['amount'])==Q(j['income_tax_payable'])==-Q(j['cash']))
                    check(tag+':vintage_deltas',all(Q(a['closing_payable'])-Q(b['closing_payable'])==allocation.get(a['id'],0) for a,b in zip(vs,new)))
                    check(tag+':prior_settlements',all(b['settlements'][:len(a['settlements'])]==a['settlements'] for a,b in zip(vs,new)))
                    check(tag+':other_balances',all(j[k]=='0/1' for k in j if k not in ['cash','income_tax_payable']))
                    kernel={'kind':'tax_payment','event':{k:deepcopy(v) for k,v in e.items() if k!='allocations'}}
                    financial=m.continuation.transition(state,kernel,state['period']['start'])
                    check(tag+':financial_provenance',s['details']['financial_result_sha256']==m.book.digest(financial))
                    check(tag+':settlement_provenance',all(a['operation_sha256']==m.book.digest(op) and a['financial_result_sha256']==m.book.digest(financial) for v in new for a in v['settlements'] if a['event_id']==e['id']))
                else:check(tag+':native_vintages_unchanged',new==vs and j['income_tax_payable']=='0/1')
                state=after;vs=new
            check(name+':exact_prefix',r['after']==state and r['period_vintages']==vs)
            check(name+':four_ties',set(r['recorded_statements']['reconciliations'].values())=={'0/1'})
            check(name+':actual_cash_opening',r['recorded_statements']['cash_flows']['opening_cash']==p['opening']['balances']['cash'])
            check(name+':complete_apply',canonical(m.apply(q,r))==canonical({**r,'status':'applied_provisional'}))
        else:check(name+':no_changed_state','after' not in r)
        observations.append({**row,'result':r})
    by={row['case']:row['result'] for row in observations};r=by['split_payment_then_native']
    check('independent_balances',all(r['after']['balances'][k]==v for k,v in {'cash':'709/2','rou':'76/1','income_tax_payable':'-23/4','current_tax':'0/1','deferred_tax':'0/1'}.items()))
    check('independent_statements',r['recorded_statements']['recorded_profit']=='-2/1' and r['recorded_statements']['indirect_operating']['net']=='-3/1' and r['recorded_statements']['balance_sheet']=={'total_assets':'1351/2','total_liabilities':'443/4','equity_including_profit':'2259/4'})
    check('equal_totals_distinct_allocations',by['old_only']['after']['balances']==by['recent_only']['after']['balances'] and by['old_only']['period_vintages']!=by['recent_only']['period_vintages'])
    check('empty_period_no_old_flows',by['no_operations']['after']['flows']==[] and [len(v['settlements']) for v in by['no_operations']['tax_vintages']]==[1,1])
    check('independent_exhaustion',by['successive_payments']['after']['balances']['cash']=='1395/4' and by['successive_payments']['after']['balances']['income_tax_payable']=='0/1')
    check('independent_fraction', [v['closing_payable'] for v in by['fractional_split']['period_vintages']]==['41/12','13/3'])
    check('independent_return',by['retained_lot_sale']['after']['balances']['cash']=='482/1' and by['retained_lot_sale']['recorded_statements']['recorded_profit']=='10/1')
    check('funding_is_real',by['cash_shortage']['stop']['reason']=='cash_shortage' and -Q(by['cash_shortage']['opening']['balances']['income_tax_payable'])>Q(by['cash_shortage']['opening']['balances']['cash']))
    return checks,observations,tests,lock
