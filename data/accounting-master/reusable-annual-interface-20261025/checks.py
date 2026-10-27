from pathlib import Path
from hashlib import sha256
from fractions import Fraction as Q
import json
from cases import cases,m
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
        name=row['case'];q=row['request'];before=canonical(q);r=m.run(q)
        check(name+':status',r['status']==row['expected_status'])
        check(name+':inputs_preserved',canonical(q)==before)
        check(name+':no_annual_promotion',r['annual_ready'] is False and r['general_annual_execution'] is False)
        if 'root_result' in r:check(name+':exact_root',canonical(r['root_result'])==canonical(m.root.run(q['root_request'])))
        if r['status'] in ['complete_provisional','stopped_provisional']:
            state=m.seed(r['root_result'])
            check(name+':remaining_exact',r['remaining_operations']==q['operations'][len(r['trace']):])
            check(name+':stop_status',(r['stop']['status'] if r['stop'] else None)==row['expected_stop'])
            check(name+':stop_index',r['stop'] is None or r['stop']['index']==len(r['trace']))
            for i,t in enumerate(r['trace']):
                tag=name+':step'+str(i);op=t['operation'];s=t['result'];after=s['after'];j=s['journal']
                check(tag+':ordered_operation',op==q['operations'][i])
                check(tag+':bound_inputs',s['before_sha256']==m.book.digest(state) and s['operation_sha256']==m.book.digest(op))
                check(tag+':account_set',set(after['after']['balances'])==set(state['after']['balances'])==set(m.native.ACCOUNTS))
                check(tag+':balanced',sum(Q(v) for v in j.values())==sum(Q(v) for v in after['after']['balances'].values())==0)
                check(tag+':journal_effect',all(Q(after['after']['balances'][k])-Q(v)==Q(j[k]) for k,v in state['after']['balances'].items()))
                check(tag+':cash_effect',Q(j['cash'])==sum(Q(f['amount']) for f in s['flows']))
                check(tag+':historical_unchanged',after['historical_vintages']==state['historical_vintages']==r['root_result']['tax_vintages'])
                check(tag+':recognition_archive',after['recognition_archive']==state['recognition_archive']==r['root_result']['archive'])
                check(tag+':one_new_identity',after['after']['seen'][:-1]==state['after']['seen'])
                check(tag+':vintage_population',len(after['period_vintages'])==len({v['id'] for v in after['period_vintages']}))
                check(tag+':vintage_sum',sum(Q(v['closing_payable']) for v in after['period_vintages'])==-Q(after['after']['balances']['income_tax_payable']))
                check(tag+':period_conservation',all(Q(v['opening_payable'])+Q(v['new_assessment'])-sum(Q(a['amount']) for a in v['settlements'])==Q(v['closing_payable'])>=0 for v in after['period_vintages']))
                if op['kind']=='current_assessment':
                    first=op['event']['mode']=='first'
                    check(tag+':no_tax_cash',j['cash']=='0/1' and s['flows']==[])
                    check(tag+':older_rows_exact',after['period_vintages'][:-1]==(state['period_vintages'] if first else state['period_vintages'][:-1]))
                    check(tag+':history_append',after['current_assessments'][:-1]==state['current_assessments'])
                    check(tag+':original_loss_opening',after['opening_loss']==state['opening_loss'])
                    check(tag+':loss_history_prefix',after['loss_state']['history'][:-1]==state['opening_loss']['history'])
                    check(tag+':loss_conservation',all(Q(a['opening'])+Q(a['generated'])==Q(a['used'])+Q(a['expired'])+Q(a['closing']) for a in after['loss_state']['history']))
                    check(tag+':deferred_invalidated',after['current_period_deferred_tax'] in ['unassessed','stale'])
                elif op['kind']=='provisional_carry':
                    archive=after['period_archive'][-1]
                    check(tag+':prior_archives_exact',after['period_archive'][:-1]==state['period_archive'])
                    check(tag+':closing_archived',archive['after']==state['after'] and archive['period_vintages']==state['period_vintages'])
                    check(tag+':opening_exact',after['opening']==after['after'])
                    check(tag+':income_zero',all(after['after']['balances'][k]=='0/1' for k in state['account_classes']['income']))
                    check(tag+':actual_profit_to_retained',Q(after['after']['balances']['retained'])==Q(state['after']['balances']['retained'])-Q(s['details']['carried_profit']))
                    check(tag+':new_period_movements_empty',after['after']['flows']==[] and after['after']['tax_adjustments']==[] and all(v['settlements']==[] for v in after['period_vintages']))
                    check(tag+':carried_rows_exact',[(v['id'],v['closing_payable']) for v in state['period_vintages']]==[(v['id'],v['opening_payable']) for v in after['period_vintages']])
                    check(tag+':unassessed',after['current_period_tax']==after['current_period_deferred_tax']=='unassessed')
                elif op['kind']=='deferred_assessment':
                    check(tag+':vintages_unchanged',after['period_vintages']==state['period_vintages'])
                    check(tag+':loss_unchanged',after['loss_state']==state['loss_state'])
                    check(tag+':current_unchanged',after['after']['balances']['current_tax']==state['after']['balances']['current_tax'])
                    check(tag+':state_bound',after['deferred_assessments'][-1]['post_state_sha256']==m.book.digest(after['after']))
                    check(tag+':capacity_explicit',after['deferred_assessments'][-1]['recovery_capacity']==op['event']['recovery_capacity'])
                elif op['kind']=='allocated_tax_payment':
                    allocations={a['vintage_id']:Q(a['amount']) for a in op['event']['allocations']}
                    check(tag+':exact_allocations',all(Q(a['closing_payable'])-Q(b['closing_payable'])==allocations.get(a['id'],0) for a,b in zip(state['period_vintages'],after['period_vintages'])))
                    check(tag+':prior_settlements',all(b['settlements'][:len(a['settlements'])]==a['settlements'] for a,b in zip(state['period_vintages'],after['period_vintages'])))
                    check(tag+':expense_unchanged',all(j[k]=='0/1' for k in ['current_tax','deferred_tax','dta','dtl']))
                if op['kind']!='provisional_carry':check(tag+':cash_history_append',after['after']['flows']==state['after']['flows']+s['flows'])
                report=m.root.carry.statements(after['opening'],after['after'],after['account_classes'])
                check(tag+':four_statement_ties',set(report['reconciliations'].values())=={'0/1'})
                state=after
            check(name+':exact_prefix',canonical(state)==canonical(r['period_book']))
            check(name+':four_statement_ties',set(r['recorded_statements']['reconciliations'].values())=={'0/1'})
            check(name+':complete_apply',canonical(m.apply(q,r))==canonical({**r,'status':'applied_provisional'}))
        else:check(name+':no_changed_state','period_book' not in r)
        observations.append({**row,'result':r})
    by={r['case']:r['result'] for r in observations}
    a=by['cumulative_replacement'];b=a['period_book']['after']['balances']
    check('independent_three_vintages',b['cash']=='701/2' and b['income_tax_payable']=='-19/4' and b['current_tax']=='3/1' and a['recorded_statements']['recorded_profit']=='-5/1')
    a=by['four_vintages_new_period'];b=a['period_book']['after']['balances']
    check('independent_four_vintages',b['cash']=='701/2' and b['retained']=='73/4' and b['income_tax_payable']=='-27/4' and a['recorded_statements']['indirect_operating']['net']=='0/1')
    a=by['same_carry_repeated']
    check('independent_second_generic_carry',a['period_book']['after']['balances']['retained']=='81/4' and len(a['period_book']['period_archive'])==2)
    a=by['four_vintage_payment']
    check('independent_four_allocation',a['period_book']['after']['balances']['cash']=='693/2' and a['period_book']['after']['balances']['income_tax_payable']=='-11/4' and a['recorded_statements']['indirect_operating']['net']=='-4/1')
    return checks,observations,tests,lock
