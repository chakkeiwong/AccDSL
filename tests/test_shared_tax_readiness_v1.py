from copy import deepcopy
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import shared_tax_readiness_v1 as m
path = ROOT / 'data/accounting-master/shared-tax-readiness-20261024/examples.py'
spec = importlib.util.spec_from_file_location('tax_information_examples', path)
examples = importlib.util.module_from_spec(spec); spec.loader.exec_module(examples)


class TaxInformationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = examples.cases()
        cls.complete = examples.supplied()

    def same(self, a, b):
        self.assertEqual(m.book.caller.canonical(a), m.book.caller.canonical(b))

    def test_classifications_and_all_flags(self):
        for row in self.rows:
            with self.subTest(case=row['case']):
                before = m.book.digest(row['request'])
                result = m.assess(row['request'])
                self.assertEqual(result['status'], row['expected_status'], result.get('reason'))
                self.assertTrue(all(result[k] is False for k in m.FLAGS))
                self.assertEqual(before, m.book.digest(row['request']))

    def test_population_is_independent_of_closing_zeros(self):
        result = m.assess(examples.missing())
        self.assertEqual(result['population']['pretax_accounts'], [
            'revenue', 'cogs', 'selling_expense', 'wages', 'depreciation', 'finance_expense', 'other_gains'])
        self.assertEqual(set(result['population']['basis_accounts']), {
            'cash', 'inventory', 'ppe', 'recovery_asset', 'investment', 'receivable', 'rou',
            'refund_liability', 'debt', 'payable', 'lease_liability'})
        self.assertEqual(result['population']['lease_rights'], [
            {'lease_id': 'lease1', 'right_id': 'A'}, {'lease_id': 'lease1', 'right_id': 'B'}])
        self.assertEqual(len(result['required_information']), 61)
        self.assertEqual(set(result['unresolved_information']), set(result['required_information']))
        self.assertIn('income/other_gains/treatment', result['required_information'])
        self.assertIn('basis/recovery_asset/closing', result['required_information'])
        closing = result['native_report']['execution']['after']
        self.assertEqual(closing['balances']['recovery_asset'], '0/1')
        right_b = next(r for l in closing['leases'] for r in l['component']['rights'] if r['right_id'] == 'B')
        self.assertEqual(right_b['rou'], '0/1')
        self.assertEqual(right_b['liability'], '0/1')

    def test_every_missing_declaration_blocks_success(self):
        for field in self.complete['information']:
            with self.subTest(field=field):
                body = deepcopy(self.complete); del body['information'][field]
                result = m.assess(body)
                self.assertEqual(result['status'], 'unresolved')
                self.assertEqual(result['unresolved_information'], [field])

    def test_every_false_finding_is_preserved(self):
        for field in m.GLOBAL_FINDINGS:
            body = deepcopy(self.complete); body['information'][field]['value'] = False
            result = m.assess(body)
            self.assertEqual(result['status'], 'unsupported')
            self.assertIs(result['request']['information'][field]['value'], False)
            finding = next(f for f in result['requirements_result']['findings'] if f['id'] == field)
            self.assertEqual(finding['body_truth'], 'false')

    def test_native_report_and_provenance_are_preserved(self):
        result = m.assess(self.complete)
        self.same(result['native_report'], examples.originals()['mixed_lifecycle']['result'])
        self.same(result['request'], self.complete)
        self.assertEqual(result['native_report']['income_recorded']['recorded_profit'], '5/1')
        self.assertEqual(result['native_report']['coverage']['tax_assessment'], 'unresolved')
        self.assertFalse(result['calculation_ready'])
        self.assertEqual(result['status'], 'information_supplied')

    def test_stopped_prefix_is_not_coverage(self):
        result = m.assess(examples.supplied(examples.missing('shared_cash_competition')))
        self.assertEqual(result['status'], 'unresolved')
        self.assertEqual(result['unresolved_information'], ['execution_complete'])
        self.assertEqual(result['native_report']['coverage']['completed_events'], 2)
        self.assertEqual(result['native_report']['cash_flows_recorded']['closing_cash'], '82/1')

    def test_replay_detects_changed_result(self):
        result = m.assess(self.complete)
        self.assertTrue(m.verify_result(self.complete, result))
        for mutate in ['flag', 'native', 'population', 'provenance']:
            changed = deepcopy(result)
            if mutate == 'flag': changed['annual_close_ready'] = True
            elif mutate == 'native': changed['native_report']['income_recorded']['recorded_profit'] = '6/1'
            elif mutate == 'population': changed['population']['lease_rights'].pop()
            else: changed['request']['information']['regime']['provenance']['kind'] = 'source_reference'
            self.assertFalse(m.verify_result(self.complete, changed))

    def test_interval_date_boundary_is_separate_from_state_time(self):
        result = m.assess(self.complete)
        self.assertEqual(result['native_report']['execution']['after']['date'], '2025-01-01')
        self.assertEqual(result['request']['interval']['activity_through'], '2025-12-31')
        self.assertEqual(result['request']['interval']['end_exclusive'], '2026-01-01')
        self.assertEqual(result['native_report']['coverage']['annual_completion'], 'unresolved')
        for values in [dict(start='2024-02-30'), dict(end_exclusive='2024-01-01'),
                       dict(activity_through='2025-12-30')]:
            body = deepcopy(self.complete); body['interval'].update(values)
            self.assertEqual(m.assess(body)['status'], 'invalid')

    def test_closed_shapes_and_untrusted_types(self):
        bodies = []
        x = deepcopy(self.complete); x['closing'] = {}; bodies.append(x)
        x = deepcopy(self.complete); x['interval']['annual_ready'] = True; bodies.append(x)
        x = deepcopy(self.complete); x['information']['rate']['provenance']['kind'] = 'admitted'; bodies.append(x)
        x = deepcopy(self.complete); x['information']['rate']['provenance']['reference'] = ''; bodies.append(x)
        x = deepcopy(self.complete); x['information']['rate']['value'] = '2/4'; bodies.append(x)
        x = deepcopy(self.complete); x['information']['rate']['value'] = None; bodies.append(x)
        x = deepcopy(self.complete); x['information']['regime']['value'] = '\ud800'; bodies.append(x)
        for body in bodies: self.assertEqual(m.assess(body)['status'], 'invalid')

    def test_exact_numeric_dimensions(self):
        result = m.assess(self.complete)
        fields = result['required_information']
        self.assertEqual(fields['rate']['dimensions'], {})
        money = fields['income/other_gains/current_adjustment']
        self.assertEqual(money['dimensions'], {'currency:USD': 1})
        self.assertEqual(money['scale'], '1/1')
        self.assertNotIn('currency', money['context'])


if __name__ == '__main__': unittest.main()
