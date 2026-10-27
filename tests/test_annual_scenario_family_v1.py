from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import importlib.util
import os
import sys
import unittest

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'annual_family_examples', ROOT / 'data/accounting-master/annual-scenario-family-20261025/examples.py')
x = importlib.util.module_from_spec(spec)
spec.loader.exec_module(x)
m = x.m


class AnnualScenarioFamilyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body = deepcopy(x.fixture())
        cls.result = m.run(cls.body)
        cls.reports = {p['start']: m.joint_report(cls.body, cls.result, p['start'])
                       for p in cls.body['periods']}

    def test_full_results_match_independent_execution(self):
        self.assertEqual(self.result['status'], 'evaluated_with_incomplete_members')
        for member, actual in zip(self.body['members'], self.result['members']):
            expected = m.annual.run(m.annual.request(self.body['root_request'], member['operations']))
            self.assertEqual(actual['result'], expected)
            self.assertEqual(actual['result_sha256'], m.digest(expected))
            self.assertEqual(actual['assumptions'], member['assumptions'])

    def test_expected_failures_preserve_exact_prefixes_and_remaining_operations(self):
        expected = {'unknown_rate': (0, 'unresolved'), 'false_authority': (1, 'unsupported'),
                    'unknown_capacity': (4, 'unresolved'), 'stale_measurement': (4, 'invalid'),
                    'cash_shortage': (1, 'funding_failure')}
        for member, row in zip(self.body['members'], self.result['members']):
            if member['id'] in expected:
                index, status = expected[member['id']]
                result = row['result']
                self.assertEqual((result['stop']['index'], result['stop']['status']), (index, status))
                self.assertEqual(len(result['trace']), index)
                self.assertEqual(result['remaining_operations'], member['operations'][index:])

    def test_joint_reports_preserve_whole_archived_and_current_vectors(self):
        for period, report in self.reports.items():
            self.assertEqual(report['status'], 'joint_authored_reports')
            for row, member in zip(report['members'], self.result['members']):
                book = member['result']['period_book']
                archived = [a for a in book['period_archive'] if a['after']['period']['start'] == period]
                if archived:
                    self.assertEqual(row['status'], 'archived_provisional')
                    self.assertEqual(row['report'], archived[0]['report'])
                    self.assertEqual(row['through_date'], archived[0]['after']['date'])
                elif book['after']['period']['start'] == period:
                    self.assertEqual(row['status'], 'current_prefix_provisional')
                    self.assertEqual(row['report'], member['result']['recorded_statements'])
                    self.assertEqual(row['through_date'], book['after']['date'])
                else:
                    self.assertEqual(row['status'], 'unavailable')
                    self.assertIsNone(row['report'])
                self.assertEqual(row['result_sha256'], member['result_sha256'])

    def test_independent_financial_controls(self):
        first = self.reports['2027-01-01']['members'][0]['report']
        later = self.reports['2028-01-01']['members'][0]['report']
        self.assertEqual(first['recorded_profit'], '-5/1')
        self.assertEqual(first['cash_flows']['closing_cash'], '701/2')
        self.assertEqual(first['cash_flows']['activities']['operating']['net'], '-7/1')
        self.assertEqual(later['recorded_profit'], '-2/1')
        self.assertEqual(later['cash_flows']['closing_cash'], '701/2')
        self.assertEqual(later['cash_flows']['net_movement'], '0/1')
        book = self.result['members'][0]['result']['period_book']
        self.assertEqual(book['after']['balances']['income_tax_payable'], '-27/4')
        self.assertEqual(book['after']['balances']['retained'], '73/4')

    def test_later_period_unavailable_for_failed_member(self):
        rows = {row['id']: row for row in self.reports['2028-01-01']['members']}
        for key in ['unknown_rate', 'false_authority', 'cash_shortage', 'unknown_capacity', 'stale_measurement']:
            self.assertEqual(rows[key]['reason'], 'period_not_reached')
            self.assertIsNone(rows[key]['report'])
        self.assertEqual(rows['repeated_periods']['status'], 'current_prefix_provisional')

    def test_zero_and_partial_budgets_retain_unvisited_members(self):
        for budget in [0, 2]:
            body = x.variant(budget=budget); result = m.run(body)
            self.assertEqual(result['status'], 'partial_evaluation')
            self.assertEqual(result['checked_members'], budget)
            self.assertEqual(len(result['members']), len(body['members']))
            self.assertEqual(result['members'][:budget], self.result['members'][:budget])
            self.assertEqual(result['unvisited_member_ids'], [v['id'] for v in body['members'][budget:]])
            query = m.joint_report(body, result, '2027-01-01')
            for row in query['members'][budget:]:
                self.assertEqual(row['reason'], 'member_budget')
                self.assertIsNone(row['report'])
            for row in result['members'][budget:]:
                self.assertIsNone(row['result'])

    def test_empty_selection_does_not_claim_infeasibility(self):
        body = x.variant(budget=0, empty=True); result = m.run(body)
        self.assertEqual(result['status'], 'empty_authored_selection')
        self.assertEqual(result['declared_search'], 'complete')
        self.assertFalse(result['historical_family_admitted'])
        self.assertFalse(result['exhaustive_scenario_coverage'])
        self.assertEqual(m.joint_report(body, result, '2027-01-01')['members'], [])

    def test_equal_results_keep_distinct_unicode_names(self):
        first, last = self.result['members'][0], self.result['members'][-1]
        self.assertEqual(last['id'], '同額別案')
        self.assertEqual(first['result'], last['result'])
        self.assertEqual(first['request_sha256'], last['request_sha256'])
        self.assertNotEqual(first['member_sha256'], last['member_sha256'])

    def test_structural_validation_never_executes_finance(self):
        with patch.object(m.annual, 'run', side_effect=AssertionError('hidden evaluation')):
            self.assertEqual(m.validate(self.body), self.body)

    def test_invalid_identity_assumptions_weights_and_limits(self):
        variants = []
        def add(change):
            body = deepcopy(self.body); change(body); variants.append(body)
        add(lambda q: q['members'][1].update(id=q['members'][0]['id']))
        add(lambda q: q['members'][0]['assumptions'].append(deepcopy(q['members'][0]['assumptions'][0])))
        add(lambda q: q['members'][0].update(weight='1/8'))
        add(lambda q: q.update(weighting='equal_probability'))
        add(lambda q: q.update(coverage='all_feasible_histories'))
        add(lambda q: q['budget'].update(max_members=True))
        add(lambda q: q['budget'].update(max_members=-1))
        add(lambda q: q['budget'].update(max_members=65))
        add(lambda q: q.update(members=[deepcopy(q['members'][0]) for _ in range(65)]))
        add(lambda q: q.update(name='\ud800'))
        for body in variants:
            with self.subTest(body_name=body['name']):
                self.assertEqual(m.run(body)['status'], 'invalid')

    def test_root_horizon_and_calendar_mismatches_reject(self):
        body = deepcopy(self.body); body['root_sha256'] = '0' * 64
        self.assertEqual(m.run(body)['reason'], 'root_digest')
        body = deepcopy(self.body); body['periods'][0]['start'] = '2026-12-31'
        self.assertEqual(m.run(body)['reason'], 'root_period')
        body = deepcopy(self.body); body['periods'][0]['start'] = '2027-02-30'
        self.assertEqual(m.run(body)['status'], 'invalid')
        body = deepcopy(self.body); body['members'][0]['operations'][5]['event']['next_period']['end_exclusive'] = '2030-01-01'
        self.assertEqual(m.run(body)['reason'], 'member_horizon')

    def test_unavailable_common_root_retains_every_named_member(self):
        body = deepcopy(self.body)
        body['root_request']['operations'].append({'kind': 'unknown', 'event': {}})
        body['root_sha256'] = m.digest(body['root_request'])
        result = m.run(body)
        self.assertEqual(result['status'], 'root_unavailable')
        self.assertEqual(result['checked_members'], 0)
        self.assertEqual(len(result['members']), len(body['members']))
        query = m.joint_report(body, result, '2027-01-01')
        self.assertTrue(all(r['reason'] == 'root_unavailable' and r['report'] is None for r in query['members']))

    def test_rehashed_financial_tampering_is_rejected(self):
        changed = deepcopy(self.result)
        changed['members'][0]['result']['period_book']['after']['balances']['cash'] = '999/1'
        changed['members'][0]['result_sha256'] = m.digest(changed['members'][0]['result'])
        self.assertFalse(m.verify_result(self.body, changed))
        self.assertEqual(m.joint_report(self.body, changed, '2027-01-01')['reason'], 'family_replay')

    def test_assumption_and_unvisited_tampering_is_rejected(self):
        changed = deepcopy(self.result); changed['members'][0]['assumptions'] = []
        self.assertFalse(m.verify_result(self.body, changed))
        body = x.variant(budget=0); result = m.run(body)
        result['members'].pop()
        self.assertFalse(m.verify_result(body, result))

    def test_no_admission_and_no_inputs_mutated(self):
        before = m.canonical(self.body); result = m.run(self.body)
        self.assertEqual(before, m.canonical(self.body))
        for key in ['probability_admitted', 'historical_family_admitted', 'annual_ready',
                    'source_admission', 'accounting_admission', 'exhaustive_scenario_coverage']:
            self.assertIs(result[key], False)

    def test_outside_period_query_is_invalid(self):
        self.assertEqual(m.joint_report(self.body, self.result, '2030-01-01')['reason'], 'outside_authored_horizon')


if __name__ == '__main__':
    unittest.main()
