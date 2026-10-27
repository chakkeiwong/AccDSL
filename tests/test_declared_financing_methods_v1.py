from copy import deepcopy
from pathlib import Path
import importlib.util
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import declared_company_program_v1 as prior_program
import company_method_clock_v1 as prior_methods
spec = importlib.util.spec_from_file_location('financing_examples',
    ROOT / 'data/accounting-master/declared-financing-clock-20261025/examples.py')
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)


def subset(body, indices):
    body = deepcopy(body)
    body['commands'] = [body['commands'][i] for i in indices]
    keys = {c['method_key'] for c in body['commands'] if c['kind'] == 'event'}
    body['registry']['entries'] = {k: v for k, v in body['registry']['entries'].items() if k in keys}
    return body


class DeclaredFinancingMethodsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body, cls.native_spec, cls.native_events, cls.mapping = ex.fixture()

    def stop(self, body, index, status='invalid'):
        before = deepcopy(body)
        result = ex.program.run(body)
        self.assertEqual(result['status'], 'stopped_provisional', str(result)[:500])
        self.assertEqual(result['stop']['index'], index)
        self.assertEqual(result['stop']['status'], status)
        self.assertEqual(len(result['trace']), index)
        expected = result['trace'][-1]['after_sha256'] if index else ex.program.digest(body['opening'])
        self.assertEqual(ex.program.digest(result['current']), expected)
        self.assertEqual(body, before)
        return result

    def build(self, body, policy=None, windows=None, roles=None):
        return ex.financing.build(body['opening'], body['schemas'],
            roles or {k: self.mapping[k] for k in ex.financing.CLASSES},
            '/finance/cursor', '/finance/debt', policy or deepcopy(ex.POLICY),
            deepcopy(ex.INTERVALS) if windows is None else windows)

    def test_native_is_comparator_only_and_actual_interest_is_not_supplied(self):
        body = subset(self.body, [0, 7])
        self.assertEqual(set(body['commands'][1]['event']['inputs']), {'approved'})
        with patch.object(ex.native.Engine, 'apply', side_effect=AssertionError('not a callback')):
            result = ex.program.run(body)
        self.assertEqual(result['status'], 'complete_provisional')
        self.assertEqual(result['current']['balances']['interest'], '9/5')
        self.assertEqual(result['current']['memory']['finance'], {'cursor': '2027-04-01', 'debt': '-100/1'})

    def test_duplicate_or_skipped_interval_preserves_the_successful_prefix(self):
        body = subset(self.body, [0, 7, 7])
        body['commands'][2]['event']['id'] = 'repeat-interest'
        self.stop(body, 2)
        self.stop(subset(self.body, [0, 13]), 1)

    def test_principal_change_before_accrual_boundary_is_refused(self):
        body = subset(self.body, [0, 8])
        body['commands'][1]['event']['date'] = '2027-02-01'
        result = self.stop(body, 1)
        findings = result['stop']['result']['transition']['preconditions']['findings']
        self.assertTrue(any(x['id'] == 'accrual_boundary' and x['body_truth'] == 'false' for x in findings))

    def test_exact_interval_date_and_backdating_are_refused(self):
        for day in ['2027-03-30', '2027-04-01']:
            body = subset(self.body, [0, 7])
            body['commands'][1]['event']['date'] = day
            self.stop(body, 1)
        body = subset(self.body, [0, 7, 8])
        body['commands'][2]['event']['date'] = '2027-03-30'
        self.stop(body, 2)

    def test_same_boundary_changes_use_the_new_principal_prospectively(self):
        body = subset(self.body, [0, 7, 8, 9, 13])
        result = ex.program.run(body)
        self.assertEqual(result['status'], 'complete_provisional')
        self.assertEqual(result['current']['balances']['debt'], '-80/1')
        self.assertEqual(result['current']['balances']['interest'], '407/125')
        self.assertEqual(result['trace'][1]['result']['transition']['journal']['interest'], '9/5')
        self.assertEqual(result['trace'][-1]['result']['transition']['journal']['interest'], '182/125')

    def test_foreign_principal_change_cannot_silently_reprice_interest(self):
        body = subset(self.body, [7])
        body['opening']['balances'].update(debt='-10/1', cash='110/1')
        result = self.stop(body, 0)
        self.assertEqual(result['current']['memory']['finance']['debt'], '0/1')

    def test_unknown_and_false_findings_remain_distinct(self):
        for index in [0, 7, 10, 11]:
            body = subset(self.body, [index])
            # These methods are structurally valid from zero debt at the opening.
            for value, status in [({'status': 'unknown', 'reason': 'Missing contractual finding'}, 'unresolved'),
                                  ({'status': 'known', 'value': False}, 'unsupported')]:
                trial = deepcopy(body)
                trial['commands'][0]['event']['inputs']['approved']['value'] = value
                self.stop(trial, 0, status)

    def test_payment_overrun_and_missing_funding_remain_distinct(self):
        body = subset(self.body, [0, 7, 15])
        body['commands'][2]['event']['inputs']['amount']['value']['value'] = '2/1'
        self.stop(body, 2)
        body = subset(self.body, [11, 12])
        body['opening']['balances'].update(cash='1/1', capital='-21/1')
        result = self.stop(body, 1)
        diagnostic = ex.op.operations.refusal_diagnostic(result['stop']['result'])
        self.assertEqual(diagnostic['category'], 'economic_funding_failure')
        body['commands'][1]['event']['inputs']['amount']['value']['value'] = '13/1'
        result = self.stop(body, 1)
        self.assertEqual(ex.op.operations.refusal_diagnostic(result['stop']['result'])['category'], 'invalid')

    def test_negative_and_wrong_dimension_inputs_are_refused(self):
        body = subset(self.body, [10])
        body['commands'][0]['event']['inputs']['shares']['value']['value'] = '-1/1'
        self.stop(body, 0)
        body = subset(self.body, [10])
        body['commands'][0]['event']['inputs']['shares']['type'] = ex.program.engine.money_type(body['opening'])
        self.assertEqual(ex.program.run(body)['status'], 'invalid')

    def test_interest_cash_classification_is_an_explicit_policy(self):
        body, _, _, _ = ex.fixture(activity='financing')
        body = subset(body, [0, 7, 15])
        body['commands'][2]['event']['inputs']['amount']['value']['value'] = '1/1'
        result = ex.program.run(body)
        self.assertEqual(result['status'], 'complete_provisional')
        flow = result['trace'][-1]['result']['transition']['flows'][0]
        self.assertEqual((flow['activity'], flow['amount']), ('financing', '-1/1'))
        policy = deepcopy(ex.POLICY)
        policy['interest_cash_activity'] = 'investing'
        with self.assertRaisesRegex(ValueError, 'explicit_interest_cash_policy'):
            self.build(self.body, policy=policy)

    def test_calendar_requires_contiguity_and_handles_leap_days(self):
        for windows in [[], [{'start': '2027-01-02', 'end_exclusive': '2027-04-01'}],
                        [ex.INTERVALS[0], {'start': '2027-03-31', 'end_exclusive': '2027-07-01'}]]:
            with self.assertRaises(ValueError):
                self.build(self.body, windows=windows)
        body = deepcopy(self.body)
        book = body['opening']
        book['period'] = {'start': '2028-01-01', 'end_exclusive': '2029-01-01'}
        book['date'] = book['memory']['finance']['cursor'] = '2028-01-01'
        registry = self.build(body, windows=[{'start': '2028-01-01', 'end_exclusive': '2029-01-01'}])
        body['registry'] = registry
        body['commands'] = [ex.event(body, 'debt_issue', 'leap-issue', '2028-01-01', {'amount': '100/1'}),
                            ex.event(body, 'interest_accrue.1', 'leap-interest', '2028-12-31', {})]
        result = ex.program.run(body)
        self.assertEqual(result['status'], 'complete_provisional', str(result)[:500])
        self.assertEqual(result['current']['balances']['interest'], '183/25')

    def test_zero_principal_advances_clock_without_inventing_interest(self):
        body = subset(self.body, [7])
        result = ex.program.run(body)
        self.assertEqual(result['status'], 'complete_provisional')
        self.assertEqual(result['current']['balances'], body['opening']['balances'])
        self.assertEqual(result['current']['memory']['finance']['cursor'], '2027-04-01')

    def test_complete_equity_explanations_are_required(self):
        body = subset(self.body, [10, 11, 16])
        result = ex.program.run(body)
        self.assertEqual(result['status'], 'complete_provisional')
        self.assertEqual(result['trace'][-1]['result']['equity']['direct_movements'], '18/1')
        body['commands'][-1]['equity_movements'] = []
        self.stop(body, 2)

    def test_stopped_text_and_full_result_replay_agree(self):
        body = subset(self.body, [0, 8])
        body['commands'][1]['event']['date'] = '2027-02-01'
        result = self.stop(body, 1)
        author, imports = ex.text.from_program(body)
        source = ex.text.render(author)
        self.assertEqual(ex.text.execute_text(source, imports), result)
        self.assertTrue(ex.program.verify(body, result))
        changed = deepcopy(result)
        changed['current']['balances']['cash'] = '201/1'
        self.assertFalse(ex.program.verify(body, changed))

    def test_v1_small_program_financial_and_transition_payloads_are_unchanged(self):
        old, _, _, _ = ex.op.fixture()
        new = deepcopy(old)
        new['profile'] = ex.program.PROFILE
        new['registry']['profile'] = ex.program.methods.REGISTRY
        a, b = prior_program.run(old), ex.program.run(new)
        self.assertEqual(a['status'], b['status'])
        self.assertEqual(a['current'], b['current'])
        for x, y in zip(a['trace'], b['trace']):
            if x['command']['kind'] == 'event':
                self.assertEqual(x['result']['materialized_request'], y['result']['materialized_request'])
                self.assertEqual(x['result']['transition'], y['result']['transition'])
            else:
                self.assertEqual(x['result'], y['result'])

    def test_unused_bad_entry_still_refuses_and_v1_remains_bounded(self):
        body = subset(self.body, [0])
        body['registry']['entries']['unused'] = deepcopy(self.body['registry']['entries']['dividend_pay'])
        body['registry']['entries']['unused']['method']['version'] = 'bad'
        self.assertEqual(ex.program.run(body)['status'], 'invalid')
        old = deepcopy(self.body)
        old['profile'] = prior_program.PROFILE
        old['registry']['profile'] = prior_methods.REGISTRY
        self.assertEqual(prior_program.run(old)['reason'], 'record_structure_limit')
        too_large = deepcopy(self.body)
        too_large['name'] = 'x' * ex.program.core.MAX_BYTES
        self.assertEqual(ex.program.run(too_large)['reason'], 'program_size_limit')

    def test_per_entry_bounds_and_registry_identities_are_not_bypassed(self):
        body = subset(self.body, [0])
        entry = body['registry']['entries']['debt_issue']
        entry['method']['residual_prerequisites'] = ['x' + str(i) for i in range(4200)]
        entry['method_sha256'] = ex.program.digest(entry['method'])
        self.assertEqual(ex.program.run(body)['reason'], 'record_structure_limit')
        body = subset(self.body, [0])
        call = ex.program.call(body['opening'], body['registry'], body['commands'][0])
        call['expected_registry_sha256'] = '0' * 64
        self.assertEqual(ex.program.methods.propose(body['opening'], call)['reason'], 'registry_digest')

    def test_carry_preserves_principal_clock_unpaid_interest_and_complement(self):
        body = subset(self.body, [0, 7])
        body['commands'].append({'kind': 'carry', 'id': 'carry', 'cutoff': '2027-12-31',
            'equity_movements': [], 'notes': [], 'retained_account': 'retained',
            'next_end_exclusive': '2029-01-01',
            'memory_policies': {p: {'kind': 'preserve', 'provenance': 'Explicit provisional preservation'}
                                for p in body['opening']['memory_types']}})
        result = ex.program.run(body)
        self.assertEqual(result['status'], 'complete_provisional')
        self.assertEqual(result['current']['memory']['finance'], {'cursor': '2027-04-01', 'debt': '-100/1'})
        self.assertEqual(result['current']['balances']['interest_payable'], '-9/5')
        self.assertFalse(result['fiscal_complete'])
        self.assertEqual(result['current']['memory']['complement'], body['opening']['memory']['complement'])
        # Carry/report remain explicitly provisional, not an interest completeness test.

    def test_builder_inputs_role_maps_and_dependency_pins_are_checked(self):
        before = deepcopy(self.body)
        self.assertEqual(self.build(self.body), self.build(self.body))
        self.assertEqual(before, self.body)
        roles = {k: self.mapping[k] for k in ex.financing.CLASSES}
        roles['interest_payable'] = roles['debt']
        with self.assertRaises(ValueError):
            self.build(self.body, roles=roles)
        with patch.object(ex.financing, 'HELPER_SHA256', '0' * 64):
            with self.assertRaisesRegex(ValueError, 'helper_dependency_hash'):
                self.build(self.body)


if __name__ == '__main__':
    unittest.main()
