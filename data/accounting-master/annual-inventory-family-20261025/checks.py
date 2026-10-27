from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json

from examples import m, fixture, variant, inventory, legacy_pair, legacy, financial_result

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def conformance():
    checks = []
    cases = []
    def check(name, value):
        checks.append({'name': name, 'passed': bool(value)})
    lock = json.loads((HERE / 'source-lock.json').read_text())
    for name, h in lock.items():
        check('protected:' + name, sha256((ROOT / name).read_bytes()).hexdigest() == h)
    tests = json.loads((HERE / 'test-observation.json').read_text())
    check('focused_and_regression_tests', tests['exit_code'] == 0)
    for name, h in tests['files'].items():
        check('tested_bytes:' + name, sha256((ROOT / name).read_bytes()).hexdigest() == h)
    body = deepcopy(fixture()); before = m.canonical(body)
    with patch.object(m.runtime, 'run', side_effect=AssertionError('hidden financial evaluation')):
        check('validation_without_execution', m.validate(body) == body)
    result = m.run(body)
    check('full_family_status', result['status'] == 'evaluated_with_incomplete_members')
    check('declared_search_complete', result['declared_search'] == 'complete')
    check('ordered_member_identities', [r['id'] for r in result['members']] == [r['id'] for r in body['members']])
    failures = {'unknown_units': (0,'unresolved'), 'false_divisibility': (0,'unsupported'),
                'oversale': (0,'invalid'), 'unsupported_method': (0,'unsupported'), 'later_oversale': (4,'invalid')}
    for member, row in zip(body['members'], result['members']):
        name = member['id']; direct = m.runtime.run(m.runtime.request(body['root_request'], member['operations']))
        check(name + ':full_direct_equality', row['result'] == direct)
        check(name + ':full_result_digest', row['result_sha256'] == m.digest(direct))
        check(name + ':assumptions_retained', row['assumptions'] == member['assumptions'])
        check(name + ':member_digest', row['member_sha256'] == m.digest(member))
        check(name + ':remaining_prefix', direct['remaining_operations'] == member['operations'][len(direct['trace']):])
        if name in failures:
            index, status = failures[name]
            check(name + ':refusal', (direct['stop']['index'], direct['stop']['status']) == (index, status))
        cases.append({'case': name, 'request_sha256': row['request_sha256'], 'result': direct})
    check('equal_paths_distinct_members', result['members'][0]['result'] == result['members'][-1]['result']
          and result['members'][0]['member_sha256'] != result['members'][-1]['member_sha256'])
    for p in body['periods']:
        query = m.joint_report(body, result, p['start'])
        check(p['start'] + ':joint_ids', [r['id'] for r in query['members']] == [r['id'] for r in body['members']])
        for row, member in zip(query['members'], result['members']):
            state = member['result']['period_book']; archived = [a for a in state['period_archive'] if a['after']['period'] == p]
            expected = archived[0]['report'] if archived else member['result']['recorded_statements'] if state['after']['period'] == p else None
            status = 'archived_provisional' if archived else 'current_prefix_provisional' if expected else 'unavailable'
            prefix = p['start'] + ':' + row['id']
            check(prefix + ':complete_vector', row['report'] == expected)
            check(prefix + ':availability', row['status'] == status)
            check(prefix + ':result_binding', row['result_sha256'] == member['result_sha256'])
            check(prefix + ':report_binding', row['report_sha256'] == (m.digest(expected) if expected else None))
            if expected:
                check(prefix + ':reconciliations', set(expected['reconciliations'].values()) == {'0/1'})
            else:
                check(prefix + ':unavailable_reason', row['reason'] == 'period_not_reached')
        cases.append({'case': 'joint_' + p['start'], 'query': query})
    for budget in [0, 2]:
        q = variant(budget=budget); r = m.run(q)
        check('budget' + str(budget) + ':count', r['checked_members'] == budget)
        check('budget' + str(budget) + ':preserved_prefix', r['members'][:budget] == result['members'][:budget])
        check('budget' + str(budget) + ':unvisited', r['unvisited_member_ids'] == [x['id'] for x in q['members'][budget:]])
        check('budget' + str(budget) + ':null_results', all(x['result'] is None for x in r['members'][budget:]))
        cases.append({'case': 'budget_' + str(budget), 'result': r})
    empty = m.run(variant(budget=0, empty=True))
    check('empty_is_authored_selection', empty['status'] == 'empty_authored_selection')
    cases.append({'case': 'empty', 'result': empty})
    # Three consecutive periods exercise archived residual stock and later tax carry.
    member = deepcopy(body['members'][0]); state = result['members'][0]['result']['period_book']
    assessment = inventory.previous.assessment(state, '8/1', 'family-second-current', end='2029-01-01')
    state = m.runtime.transition(state, assessment)['after']
    measure = inventory.previous.deferred(state, 'family-second-deferred')
    state = m.runtime.transition(state, measure)['after']
    carry = inventory.previous.carry(state, 'family-second-carry', '2030-01-01')
    member['operations'].extend([assessment, measure, carry])
    q = m.request(body['root_request'], body['periods'] + [carry['event']['next_period']], [member], 1)
    r = m.run(q); direct = m.runtime.run(m.runtime.request(q['root_request'], member['operations']))
    check('three_periods_full_direct_match', r['members'][0]['result'] == direct)
    check('three_periods_complete', r['status'] == 'evaluated_all_members')
    check('three_periods_two_archives', len(direct['period_book']['period_archive']) == 2)
    check('three_periods_payable_control', direct['period_book']['after']['balances']['income_tax_payable'] == '-57/4')
    check('three_periods_cash_control', direct['period_book']['after']['balances']['cash'] == '482/1')
    for p, profit, activity, status in zip(q['periods'], ['3/1', '3/1', '0/1'], ['15/1', '15/1', '0/1'],
                                         ['archived_provisional', 'archived_provisional', 'current_prefix_provisional']):
        report = m.joint_report(q, r, p['start']); row = report['members'][0]
        check(p['start'] + ':third_path_status', row['status'] == status)
        check(p['start'] + ':profit_control', row['report']['recorded_profit'] == profit)
        check(p['start'] + ':cash_flow_control', row['report']['cash_flows']['activities']['operating']['net'] == activity)
        cases.append({'case': 'third_path_' + p['start'], 'query': report})
    cases.append({'case': 'three_periods', 'request': q, 'result': r})
    old,new=legacy_pair();a=legacy.m.run(old);b=m.run(new)
    check('legacy_family_status',a['status']==b['status'])
    check('legacy_family_root',financial_result(a['root_check'])==financial_result(b['root_check']))
    for prior,current in zip(a['members'],b['members']):
        check('legacy_member:'+prior['id'],prior['id']==current['id'] and prior['assumptions']==current['assumptions'] and financial_result(prior['result'])==financial_result(current['result']))
    cases.append({'case':'legacy_financial_equality','legacy_result':a,'inventory_result':b})
    for key in ['probability_admitted', 'historical_family_admitted', 'annual_ready', 'source_admission',
                'accounting_admission', 'exhaustive_scenario_coverage']:
        check('no_promotion:' + key, result[key] is False and r[key] is False)
    check('input_unchanged', before == m.canonical(body))
    cases.append({'case': 'full_family', 'request': body, 'result': result})
    return checks, cases, tests, lock
