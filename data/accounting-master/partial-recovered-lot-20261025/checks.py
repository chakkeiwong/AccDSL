from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json

from examples import m, settled, sale, native_sale, negatives, statement_control, previous, reports

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def conformance():
    checks = []; cases = []
    def check(name, value):
        checks.append({'name': name, 'passed': bool(value)})
    lock = json.loads((HERE/'source-lock.json').read_text())
    for name, value in lock.items():
        check('protected:' + name, sha256((ROOT/name).read_bytes()).hexdigest() == value)
    tests = json.loads((HERE/'test-observation.json').read_text())
    check('test_suites_pass', tests['exit_code'] == 0)
    for name, value in tests['files'].items():
        check('tested_bytes:' + name, sha256((ROOT/name).read_bytes()).hexdigest() == value)
    state = deepcopy(settled())
    for label, units, proceeds in [('half', '1/1', '15/1'), ('third_unit', '1/3', '7/2'),
                                  ('full', '2/1', '30/1'), ('full_zero', '2/1', '0/1'),
                                  ('full_fractional_proceeds', '2/1', '1/3')]:
        event = sale(units, proceeds, 'sale'); before = m.book.caller.canonical([state, event])
        result = m.propose(state, event); check(label+':proposed', result['status'] == 'proposed')
        p = result['proposal']; after = p['after']; lot = after['lots']['recovered']
        cost = Q(10) * Q(units)
        check(label+':cash_control', Q(after['balances']['cash']) == Q(452) + Q(proceeds))
        check(label+':inventory_control', Q(after['balances']['inventory']) == Q(80) - cost)
        check(label+':remaining_units', Q(lot['units']) == Q(2) - Q(units))
        check(label+':remaining_cost', Q(lot['carrying']) == Q(lot['tax_base']) == Q(20) - cost)
        check(label+':quantity_disposition', lot['disposed'] == (Q(units) == 2))
        check(label+':cost_conservation', Q(lot['carrying']) + Q(p['allocation']['released_carrying']) == 20)
        check(label+':balanced_journal', sum(Q(v) for v in p['journal'].values()) == 0)
        check(label+':cash_flow', Q(p['journal']['cash']) == sum(Q(f['amount']) for f in p['flows']))
        check(label+':apply', m.apply(state, event, p)['after'] == after)
        check(label+':inputs_preserved', before == m.book.caller.canonical([state, event]))
        control = statement_control(previous.opening(), after)
        check(label+':profit_control', Q(control['profit']) == Q(16) + Q(proceeds) - cost)
        check(label+':operating_cash_control', Q(control['operating_cash']) == Q(-48) + Q(proceeds))
        check(label+':statement_ties', set(control['reconciliations'].values()) == {'0/1'})
        if Q(units) == 2:
            old = m.book.propose(state, native_sale(proceeds=proceeds))
            for key in ['after', 'journal', 'flows']:
                check(label+':native_' + key, p[key] == old['proposal'][key])
        cases.append({'case': label, 'event': event, 'result': result, 'statement_control': control})
    sales = [sale(identity='first'), sale(identity='last')]; result = m.run_prefix(state, sales)
    full = m.propose(state, sale('2/1', '30/1'))['proposal']
    check('split_complete', result['status'] == 'complete')
    check('split_remaining_fractions', [r['proposal']['allocation']['fraction_of_remaining'] for r in result['trace']] == ['1/2', '1/1'])
    check('split_same_financials', result['after']['balances'] == full['after']['balances'])
    check('split_same_lot', result['after']['lots'] == full['after']['lots'])
    check('split_distinct_ids', result['after']['seen'] != full['after']['seen'])
    check('split_distinct_flows', result['after']['flows'] != full['after']['flows'])
    cases.append({'case': 'split', 'result': result})
    state0 = deepcopy(state); state0['lots']['recovered'].update(carrying='0/1', tax_base='0/1')
    state0['balances']['inventory'] = '60/1'; state0['balances']['cogs'] = m.fmt(Q(state0['balances']['cogs']) + 20)
    result0 = m.run_prefix(state0, sales)
    check('zero_cost_partial_stays_live', result0['trace'][0]['proposal']['after']['lots']['recovered']['disposed'] is False)
    check('zero_cost_final_disposed', result0['after']['lots']['recovered']['disposed'] is True)
    cases.append({'case': 'zero_cost', 'result': result0})
    multi = deepcopy(state); multi['lots']['other'] = deepcopy(multi['lots']['recovered'])
    multi['lots']['other']['id'] = 'other'; multi['other_inventory'] = '40/1'
    other = m.propose(multi, sale())
    check('other_lot_exact', other['proposal']['after']['lots']['other'] == multi['lots']['other'])
    cases.append({'case': 'other_lot', 'result': other})
    for row in negatives():
        before = m.book.caller.canonical([row['before'], row['event']])
        r = m.propose(row['before'], row['event'])
        check(row['case']+':status', r['status'] == row['expected'])
        check(row['case']+':no_proposal', r['proposal'] is None)
        check(row['case']+':no_mutation', before == m.book.caller.canonical([row['before'], row['event']]))
        cases.append({'case': row['case'], 'expected': row['expected'], 'result': r})
    bad_sales = [sale(identity='valid'), sale('2/1', '30/1', 'over'), sale(identity='later')]
    stopped = m.run_prefix(state, bad_sales)
    check('refusal_retains_prefix', stopped['status'] == 'stopped' and len(stopped['trace']) == 1)
    check('refusal_retains_remaining', stopped['remaining_sales'] == bad_sales[1:])
    check('refusal_retains_cash', stopped['after']['balances']['cash'] == '467/1')
    cases.append({'case': 'refused_prefix', 'result': stopped})
    p = m.propose(state, sale())['proposal']; p['allocation']['released_carrying'] = '0/1'
    check('tampered_allocation_refused', m.apply(state, sale(), p)['status'] == 'invalid')
    cases.append({'case': 'tampered_allocation', 'result': m.apply(state, sale(), p)})
    direct = reports.calculate(reports.request(previous.opening(), previous.events()[:3]))
    control = statement_control(previous.opening(), full['after'])
    check('full_native_statement_profit', control['profit'] == direct['income_recorded']['recorded_profit'])
    check('full_native_statement_cash', control['operating_cash'] == direct['cash_flows_recorded']['activities']['operating']['net'])
    check('full_native_statement_ties', control['reconciliations'] == direct['reconciliations'])
    for key in ['source_admission', 'accounting_admission', 'method_eligible', 'annual_ready', 'committed']:
        check('no_promotion:' + key, full[key] is False)
    return checks, cases, tests, lock
