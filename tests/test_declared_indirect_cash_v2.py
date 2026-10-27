from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import importlib.util
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import declared_indirect_cash_v2 as bridge
spec = importlib.util.spec_from_file_location('profit_component_examples', ROOT /
    'data/accounting-master/declared-indirect-profit-components-20261025/examples.py')
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)


class IndirectProfitComponentsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base, cls.expected = ex.fixture('alpha', 'disposal_gain')

    def test_gain_loss_and_alternate_chart(self):
        for chart in ['alpha', 'beta']:
            for variant, adjustment in [('disposal_gain', '-2/1'), ('disposal_loss', '2/1')]:
                row = ex.checked_case(chart, variant)
                self.assertEqual(row['result']['items']['nonoperating_profit_adjustment'], adjustment)
                self.assertEqual(row['result']['items']['indirect_operating_cash'], '0/1')

    def test_report_preservation_and_no_input_mutation(self):
        body = deepcopy(self.base)
        before = deepcopy(body)
        result = bridge.report(body)
        self.assertEqual(body, before)
        self.assertEqual(result['financial_report'], body['result']['trace'][-1]['result'])
        self.assertTrue(all(result[key] is False for key in bridge.FLAGS))

    def test_misclassified_gain_refuses_without_reclassifying_cash(self):
        body = deepcopy(self.base)
        entry = next(iter(body['policy']['methods'].values()))
        entry['profit_accounts']['revenue'] = 'operating'
        result = bridge.report(body)
        self.assertEqual(result['status'], 'unsupported')
        self.assertEqual(result['reason'], 'nonoperating_reconciliation:disposal_gain.1')
        self.assertEqual(body['result']['trace'][-1]['result']['cash_flows']['activities']['investing']['net'], '12/1')

    def test_missing_extra_wrong_and_invalid_profit_classification(self):
        for mode in ['missing', 'extra', 'category', 'type']:
            body = deepcopy(self.base)
            entry = next(iter(body['policy']['methods'].values()))
            if mode == 'missing':
                entry['profit_accounts'] = {}
            elif mode == 'extra':
                entry['profit_accounts']['cash'] = 'operating'
            elif mode == 'category':
                entry['profit_accounts']['revenue'] = 'residual'
            else:
                entry['profit_accounts'] = []
            self.assertEqual(bridge.report(body)['status'], 'invalid', mode)

    def test_missing_and_extra_method_and_balance_sheet_bindings(self):
        for mode in ['missing_method', 'extra_method', 'missing_account', 'extra_account']:
            body = deepcopy(self.base)
            methods = body['policy']['methods']
            key = next(iter(methods))
            if mode == 'missing_method':
                methods.pop(key)
            elif mode == 'extra_method':
                methods['0' * 64] = deepcopy(methods[key])
            elif mode == 'missing_account':
                methods[key]['accounts'].pop('plant_cost')
            else:
                methods[key]['accounts']['cash'] = 'nonoperating'
            self.assertIn(bridge.report(body)['status'], ['invalid', 'unsupported'])

    def test_zero_net_gross_profit_still_requires_classification(self):
        body, _ = ex.fixture('alpha', 'zero_net')
        source = body['program']
        entry = source['registry']['entries']['zero_net']
        m = entry['method'];money = bridge.program.engine.money_type(source['opening'])
        m['account_map']['revenue'] = 'revenue'
        m['monetary']['definition']['accounts']['revenue'] = money
        entry['account_classes']['revenue'] = 'income'
        for i, amount in enumerate(['5/1', '-5/1']):
            m['monetary']['definition']['postings'].append({'id': 'profit.' + str(i), 'account': 'revenue',
                'expression': ex.prior.fin.financing.constant(money, amount), 'requires': []})
        old_key = next(iter(body['policy']['methods']))
        new_key = bridge.core.digest(m);entry['method_sha256'] = new_key
        body['policy']['methods'][new_key] = body['policy']['methods'].pop(old_key)
        result = bridge.program.run(source)
        self.assertEqual(result['status'], 'complete_provisional')
        body['program_sha256'] = bridge.core.digest(source)
        body['result'] = result;body['result_sha256'] = bridge.core.digest(result)
        self.assertEqual(bridge.report(body)['reason'], 'exact_profit_posting_classification')
        body['policy']['methods'][new_key]['profit_accounts'] = {'revenue': 'nonoperating'}
        out = bridge.report(body)
        self.assertEqual(out['status'], 'explained_provisional')
        self.assertEqual(len(out['events'][0]['gross_postings']), 4)
        self.assertEqual(out['items']['nonoperating_profit_adjustment'], '0/1')

    def test_rehashed_altered_result_is_replayed_and_refused(self):
        body = deepcopy(self.base)
        body['result']['trace'][-1]['result']['income']['profit'] = '0/1'
        body['result_sha256'] = bridge.core.digest(body['result'])
        self.assertEqual(bridge.report(body)['reason'], 'unverified_program_result')

    def test_wrong_policy_profile_context_or_premise_refuses(self):
        for mode in ['profile', 'context', 'premise']:
            body = deepcopy(self.base)
            if mode == 'profile':
                body['policy']['profile'] = 'DeclaredIndirectCashPolicy/1'
            elif mode == 'context':
                body['policy']['context']['entity'] = 'another'
            else:
                next(iter(body['policy']['methods'].values()))['premise'] = ''
            self.assertEqual(bridge.report(body)['status'], 'invalid')

    def test_policy_bounds_precede_program_replay(self):
        body = deepcopy(self.base)
        body['policy']['cycle'] = body['policy']
        with patch.object(bridge.program, 'verify', side_effect=AssertionError('replay must not start')) as verify:
            result = bridge.report(body)
        self.assertEqual(result['status'], 'invalid')
        verify.assert_not_called()

    def test_dependency_and_result_replay_protect_all_fields(self):
        with patch.object(bridge, 'PIN', '0' * 64):
            self.assertEqual(bridge.report(self.base)['reason'], 'indirect_program_dependency')
        result = bridge.report(self.base)
        self.assertTrue(bridge.verify(self.base, result))
        for key, value in [('events', []), ('classification_admission', True), ('policy', {})]:
            altered = deepcopy(result);altered[key] = value
            self.assertFalse(bridge.verify(self.base, altered))

    def test_algebra_does_not_admit_an_arbitrary_adjustment_name(self):
        body, _ = ex.fixture('alpha', 'depreciation')
        for row in body['policy']['methods'].values():
            for account in row['accounts']:
                row['accounts'][account] = 'working_capital'
        result = bridge.report(body)
        self.assertEqual(result['status'], 'explained_provisional')
        self.assertFalse(result['classification_admission'])
        self.assertEqual(result['items']['working_capital'], '5/1')
        self.assertEqual(result['items']['indirect_operating_cash'], '0/1')


if __name__ == '__main__':
    unittest.main()
