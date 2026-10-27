from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import importlib.util
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import group_indirect_cash_v1 as bridge

spec = importlib.util.spec_from_file_location('group_indirect_examples', ROOT /
    'data/accounting-master/group-indirect-cash-20261025/examples.py')
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)


class GroupIndirectTests(unittest.TestCase):
    def result(self, request, status='group_explained_provisional'):
        before = deepcopy(request)
        result = bridge.report(request)
        self.assertEqual(result['status'], status, result)
        self.assertEqual(before, request)
        self.assertTrue(all(result[k] is False for k in bridge.FLAGS))
        return result

    def test_two_charts_four_classifications_and_independent_arithmetic(self):
        for chart in ['named', 'numbered']:
            for variant in ex.VARIANTS:
                with self.subTest(chart=chart, variant=variant):
                    case = ex.checked_case(chart, variant)
                    r, q = case['result'], case['request']
                    self.assertEqual(r['group_report'], q['group_result'])
                    self.assertEqual(r['legal'], q['legal'])
                    self.assertEqual(r['items']['profit'], '20/1')
                    self.assertEqual(r['items']['noncash_profit'], '0/1')
                    self.assertEqual(r['items']['nonoperating_profit_adjustment'], '0/1')
                    self.assertEqual(r['group_report']['cash_flows']['activities'],
                                     case['baseline_result']['cash_flows']['activities'])
                    self.assertEqual(len(case['adapter']['flow_id_translation']), 3)
                    self.assertEqual(len(case['adapter']['added_schemas']), 1)
                    self.assertTrue(case['adapter']['complete_states_and_reports_equal_after_declared_adaptation'])

    def test_request_and_inputs_unchanged_and_full_result_replays(self):
        q = ex.fixture()['request']
        r = self.result(q)
        self.assertTrue(bridge.verify(q, r))
        r['items']['profit'] = '999/1'
        self.assertFalse(bridge.verify(q, r))

    def test_missing_extra_owner_refused(self):
        for kind in ['missing', 'extra']:
            q = ex.fixture()['request']
            if kind == 'missing':
                q['legal'].pop('S')
            else:
                q['legal']['foreign'] = deepcopy(q['legal']['S'])
            self.assertEqual(self.result(q, 'invalid')['reason'], 'exact_legal_bridge_population')

    def test_valid_but_unrelated_legal_trace_refused(self):
        q = ex.fixture('named')['request']
        q['legal']['P'] = ex.fixture('numbered')['request']['legal']['P']
        self.assertEqual(self.result(q, 'invalid')['reason'], 'legal_book_binding:P')

    def test_swapped_legal_owners_refused(self):
        q = ex.fixture()['request']
        q['legal']['P'], q['legal']['S'] = q['legal']['S'], q['legal']['P']
        self.assertEqual(self.result(q, 'invalid')['reason'], 'legal_book_binding:P')

    def test_rehashed_forged_legal_execution_refused(self):
        q = ex.fixture()['request']
        req = q['legal']['P']['request']
        req['result']['current']['balances'][req['program']['opening']['cash_account']] = '71/1'
        req['result_sha256'] = bridge.core.digest(req['result'])
        q['legal']['P']['result']['request_sha256'] = bridge.core.digest(req)
        self.assertEqual(self.result(q, 'invalid')['reason'], 'unverified_legal_bridge:P')

    def test_forged_legal_explanation_refused(self):
        q = ex.fixture()['request']
        q['legal']['P']['result']['items']['working_capital'] = '999/1'
        self.assertEqual(self.result(q, 'invalid')['reason'], 'unverified_legal_bridge:P')

    def test_rehashed_forged_group_report_refused(self):
        q = ex.fixture()['request']
        q['group_result']['cash_flows']['activities']['operating']['net'] = '19/1'
        q['group_result_sha256'] = bridge.core.digest(q['group_result'])
        self.assertEqual(self.result(q, 'invalid')['reason'], 'unverified_group_report')

    def test_stale_group_inputs_refused(self):
        for field in ['group_request_sha256', 'group_result_sha256']:
            q = ex.fixture()['request']; q[field] = '0' * 64
            self.assertEqual(self.result(q, 'invalid')['reason'], 'stale_group_input')

    def test_stale_or_reused_pair_cannot_hide_behind_rehash(self):
        for kind in ['stale', 'reused']:
            q = ex.fixture()['request']; source = q['group_request']
            if kind == 'stale':
                source['internal_cash_pairs'][0]['payer']['expected_flow_sha256'] = '0' * 64
            else:
                pair = deepcopy(source['internal_cash_pairs'][0]); pair['id'] = 'duplicate'
                source['internal_cash_pairs'].append(pair)
            q['group_request_sha256'] = bridge.core.digest(source)
            q['group_result'] = bridge.group.report(source)
            q['group_result_sha256'] = bridge.core.digest(q['group_result'])
            self.assertEqual(self.result(q, 'invalid')['reason'], 'unverified_group_report')

    def test_zero_net_pair_keeps_both_gross_flows(self):
        q = ex.fixture('named', 'operating')['request']
        r = self.result(q); row = r['internal_cash_adjustments'][0]
        self.assertEqual(row['adjustment'], '0/1')
        self.assertEqual(row['pair']['payer_flow']['amount'], '-30/1')
        self.assertEqual(row['pair']['payee_flow']['amount'], '30/1')
        self.assertEqual(r['group_report']['raw_cash_flows']['activities']['operating'],
                         {'receipts': '50/1', 'payments': '30/1', 'net': '20/1'})
        self.assertEqual(r['group_report']['cash_flows']['activities']['operating'],
                         {'receipts': '20/1', 'payments': '0/1', 'net': '20/1'})

    def test_unpaired_population_remains_conditional_not_invented(self):
        q = ex.fixture('named', 'payer_operating')['request']
        q['group_request']['internal_cash_pairs'] = []
        q['group_result'] = bridge.group.report(q['group_request'])
        q['group_request_sha256'] = bridge.core.digest(q['group_request'])
        q['group_result_sha256'] = bridge.core.digest(q['group_result'])
        r = self.result(q)
        self.assertEqual(r['internal_cash_adjustments'], [])
        self.assertEqual(r['items']['indirect_operating_cash'], '-10/1')
        self.assertFalse(r['consolidation_complete'])

    def test_closed_shape_and_recursive_input_reject_before_replay(self):
        q = ex.fixture()['request']; q['extra'] = True
        self.result(q, 'invalid')
        q = ex.fixture()['request']; q['legal']['cycle'] = q
        with patch.object(bridge.group, 'verify') as verify:
            r = bridge.report(q)
            self.assertEqual(r['status'], 'invalid')
            verify.assert_not_called()

    def test_dependency_change_rejects_before_execution(self):
        q = ex.fixture()['request']
        with patch.dict(bridge.PINS, {'declared_indirect_cash_v2.py': '0' * 64}):
            self.assertEqual(self.result(q, 'invalid')['reason'],
                             'dependency_hash:declared_indirect_cash_v2.py')


if __name__ == '__main__':
    unittest.main()
