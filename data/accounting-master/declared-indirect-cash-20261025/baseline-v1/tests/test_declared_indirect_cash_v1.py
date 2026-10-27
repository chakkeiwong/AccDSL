from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import importlib.util
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import declared_indirect_cash_v1 as bridge
spec = importlib.util.spec_from_file_location('indirect_examples', ROOT /
    'data/accounting-master/declared-indirect-cash-20261025/examples.py')
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)


class DeclaredIndirectCashTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base, cls.expected = ex.fixture()

    def test_both_charts_complete_independent_cases(self):
        cases = ex.cases()
        self.assertEqual(len(cases), 16)
        for row in cases.values():
            self.assertEqual(row['result']['items'], row['expected'])
            self.assertEqual(row['result']['direct_operating_cash'], row['expected']['indirect_operating_cash'])
            self.assertTrue(all(row['result'][key] is False for key in bridge.FLAGS))

    def test_request_and_original_report_remain_unchanged(self):
        body = deepcopy(self.base)
        before = deepcopy(body)
        result = bridge.report(body)
        self.assertEqual(body, before)
        self.assertEqual(result['financial_report'], body['result']['trace'][-1]['result'])
        self.assertTrue(bridge.verify(body, result))

    def test_stale_hash_and_rehashed_forged_result_refuse(self):
        for rehash in [False, True]:
            body = deepcopy(self.base)
            body['result']['current']['balances']['cash'] = '999/1'
            if rehash:
                body['result_sha256'] = bridge.core.digest(body['result'])
            result = bridge.report(body)
            self.assertEqual(result['status'], 'invalid')
            self.assertEqual(result['reason'], 'unverified_program_result' if rehash else 'stale_input')

    def test_missing_extra_method_or_account_classification_refuses(self):
        for mode in ['method_missing', 'method_extra', 'account_missing', 'account_extra']:
            body = deepcopy(self.base)
            methods = body['policy']['methods']
            key = next(k for k, v in methods.items() if v['accounts'])
            if mode == 'method_missing':
                methods.pop(key)
            elif mode == 'method_extra':
                methods['0' * 64] = deepcopy(methods[key])
            elif mode == 'account_missing':
                methods[key]['accounts'].pop(next(iter(methods[key]['accounts'])))
            else:
                methods[key]['accounts']['invented'] = 'working_capital'
            self.assertIn(bridge.report(body)['status'], ['invalid', 'unsupported'], mode)

    def test_wrong_debt_classification_cannot_be_balancing_adjustment(self):
        body = deepcopy(self.base)
        for row in body['policy']['methods'].values():
            if 'debt' in row['accounts']:
                row['accounts']['debt'] = 'working_capital'
        result = bridge.report(body)
        self.assertEqual(result['status'], 'unsupported')
        self.assertIn('nonoperating_reconciliation', result['reason'])

    def test_zero_net_gross_postings_still_require_classification(self):
        body, _ = ex.fixture(variant='zero_net')
        for row in body['policy']['methods'].values():
            row['accounts'] = {}
        result = bridge.report(body)
        self.assertEqual(result['status'], 'unsupported')
        self.assertIn('exact_gross_posting_classification', result['reason'])

    def test_wrong_category_owner_context_and_premise_refuse(self):
        for mode in ['category', 'owner', 'context', 'premise']:
            body = deepcopy(self.base)
            methods = body['policy']['methods']
            row = next(v for v in methods.values() if 'debt' in v['accounts'])
            if mode == 'category':
                row['accounts']['debt'] = 'residual'
            elif mode == 'owner':
                row['accounts']['debt'] = 'owner'
            elif mode == 'context':
                body['policy']['context']['entity'] = 'another'
            else:
                row['premise'] = ''
            self.assertEqual(bridge.report(body)['status'], 'invalid', mode)

    def test_no_successful_report_is_not_an_empty_cash_statement(self):
        body = deepcopy(self.base)
        body['report_id'] = 'missing'
        result = bridge.report(body)
        self.assertEqual(result['reason'], 'successful_report_required')

    def test_disposal_gain_requires_a_richer_decomposition(self):
        body, _ = ex.fixture(variant='disposal_gain')
        result = bridge.report(body)
        self.assertEqual(result['status'], 'unsupported')
        self.assertIn('nonoperating_reconciliation', result['reason'])
        self.assertEqual(body['result']['trace'][-1]['result']['income']['profit'], '2/1')

    def test_algebra_does_not_prove_unique_accounting_classification(self):
        body = deepcopy(self.base)
        for row in body['policy']['methods'].values():
            for account, category in list(row['accounts'].items()):
                if category == 'working_capital':
                    row['accounts'][account] = 'noncash_profit'
        result = bridge.report(body)
        self.assertEqual(result['status'], 'explained_provisional')
        self.assertFalse(result['classification_admission'])
        self.assertEqual(result['items']['indirect_operating_cash'], '3/1')
        self.assertEqual(result['items']['working_capital'], '0/1')
        self.assertEqual(result['items']['noncash_profit'], '-29/5')

    def test_dependencies_and_policy_structure_limits(self):
        with patch.object(bridge, 'PIN', '0' * 64):
            self.assertEqual(bridge.report(self.base)['reason'], 'indirect_program_dependency')
        body = deepcopy(self.base)
        body['policy']['cycle'] = body['policy']
        self.assertEqual(bridge.report(body)['status'], 'invalid')

    def test_replay_rejects_changed_rows_flags_and_report(self):
        result = bridge.report(self.base)
        for key, value in [('events', []), ('classification_admission', True), ('financial_report', {})]:
            altered = deepcopy(result)
            altered[key] = value
            self.assertFalse(bridge.verify(self.base, altered))


if __name__ == '__main__':
    unittest.main()
