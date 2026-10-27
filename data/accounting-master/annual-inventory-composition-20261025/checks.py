from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json

from examples import m, cases, root, previous, native_full_sale

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def conformance():
    checks = []; stored = []
    def check(name, value):
        checks.append({'name': name, 'passed': bool(value)})
    locks = json.loads((HERE/'source-lock.json').read_text())
    for name, value in locks.items():
        check('protected:' + name, sha256((ROOT/name).read_bytes()).hexdigest() == value)
    tests = json.loads((HERE/'test-observation.json').read_text())
    check('tests_pass', tests['exit_code'] == 0)
    for name, value in tests['files'].items():
        check('tested_bytes:' + name, sha256((ROOT/name).read_bytes()).hexdigest() == value)
    results = {}
    for row in cases():
        name, request = row['case'], row['request']; before = m.annual.caller.canonical(request)
        r = m.run(request); results[name] = r
        check(name+':status', r['status'] == row['expected_status'])
        check(name+':stop', (r['stop']['status'] if r.get('stop') else None) == row['expected_stop'])
        check(name+':input_exact', before == m.annual.caller.canonical(request))
        check(name+':remaining', r['remaining_operations'] == request['operations'][len(r['trace']):])
        check(name+':full_apply', m.apply(request, r)['status'] == 'applied_provisional')
        check(name+':statement_ties', set(r['recorded_statements']['reconciliations'].values()) == {'0/1'})
        check(name+':full_account_registry', len(r['period_book']['after']['balances']) == 26)
        for index, trace in enumerate(r['trace']):
            p = trace['result']; prefix = name+':op'+str(index)
            check(prefix+':balanced', sum(Q(v) for v in p['journal'].values()) == 0)
            check(prefix+':cash_identity', Q(p['journal']['cash']) == sum(Q(f['amount']) for f in p['flows']))
            if trace['operation']['kind'] == 'partial_inventory_sale':
                state = r['trace'][index-1]['result']['after'] if index else results['empty']['period_book']
                for key in ['period_vintages','historical_vintages','current_assessments','deferred_assessments',
                            'loss_state','opening_loss','period_archive','recognition_archive','opening','findings']:
                    check(prefix+':preserve_'+key, p['after'][key] == state[key])
                check(prefix+':tax_postings_zero', all(p['journal'][key] == '0/1' for key in
                      ['income_tax_payable','current_tax','deferred_tax','dta','dtl']))
        stored.append({'case': name, 'request': request, 'result': r})
    partial = results['partial']; state = partial['period_book']
    for field, value in [('cash','467/1'),('inventory','70/1'),('income_tax_payable','-41/4')]:
        check('partial_control:'+field, state['after']['balances'][field] == value)
    check('partial_profit', partial['recorded_statements']['recorded_profit'] == '5/1')
    check('partial_operating_cash', partial['recorded_statements']['cash_flows']['activities']['operating']['net'] == '15/1')
    check('partial_units', state['after']['lots']['recovered']['units'] == '1/1')
    old = m.annual.run(native_full_sale()); full = results['full']
    for key in ['period_book','recorded_statements','stop','remaining_operations']:
        check('full_sale_native:'+key, full[key] == old[key])
    for key in ['after','journal','flows']:
        check('full_sale_transition:'+key, full['trace'][0]['result'][key] == old['trace'][0]['result'][key])
    for name, q in [('old_current', previous.scenario()), ('old_repeated', previous.repeated_scenario())]:
        old = m.annual.run(q); newer = m.run(m.request(q['root_request'],q['operations']))
        for key, value in old.items():
            if key not in ['profile','request_sha256','source_bundle_sha256','implementation_sha256']:
                check(name+':'+key, newer[key] == value)
        stored.append({'case': name, 'old_result': old, 'new_result': newer})
    r = results['after_assessment']; state = r['period_book']
    check('activity_marks_current', state['current_period_tax'] == 'activity_after_assessment')
    check('activity_marks_deferred', state['current_period_deferred_tax'] == 'stale')
    for name, reason in [('inside_assessment','event_inside_assessed_interval'),('stale_carry','assessments_incomplete'),
                         ('measurement_without_reassessment','current_assessment_required'),('stale_measurement','measurement_state_digest')]:
        check(name+':specific_refusal', results[name]['stop']['reason'] == reason)
    r = results['residual_carry_and_sale']; state = r['period_book']; archived = state['period_archive'][0]
    check('carried_lot_exact', state['opening']['lots'] == archived['after']['lots'])
    check('carried_unit', state['opening']['lots']['recovered']['units'] == '1/1')
    check('next_period_sale_exhausts', state['after']['lots']['recovered']['disposed'] is True)
    check('next_period_cash', state['after']['balances']['cash'] == '482/1')
    check('next_period_payable', state['after']['balances']['income_tax_payable'] == '-49/4')
    check('archived_profit_control', archived['report']['recorded_profit'] == '3/1')
    check('new_period_profit_control', r['recorded_statements']['recorded_profit'] == '5/1')
    check('new_period_cash_control', r['recorded_statements']['cash_flows']['activities']['operating']['net'] == '15/1')
    refreshed = results['refreshed_carry']['period_book']; archive = refreshed['period_archive'][0]
    check('fresh_carry_resets', refreshed['current_period_tax'] == refreshed['current_period_deferred_tax'] == 'unassessed')
    check('fresh_history_kept', len(archive['current_assessments']) == len(archive['deferred_assessments']) == 2)
    check('fresh_payable_control', refreshed['after']['balances']['income_tax_payable'] == '-53/4')
    for key in ['source_admission','accounting_admission','annual_ready','general_annual_execution','committed']:
        check('no_promotion:'+key, full[key] is False)
    return checks, stored, tests, locks
