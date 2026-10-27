from copy import deepcopy
from pathlib import Path
from fractions import Fraction as Q
import importlib.util
import os
import unittest

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'annual_inventory_examples', ROOT/'data/accounting-master/annual-inventory-composition-20261025/examples.py')
x = importlib.util.module_from_spec(spec); spec.loader.exec_module(x); m = x.m


class AnnualInventoryProgramTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = x.cases()
        cls.results = {row['case']: m.run(row['request']) for row in cls.rows}

    def test_all_scenario_statuses_and_successful_prefixes(self):
        for row in self.rows:
            with self.subTest(case=row['case']):
                result = self.results[row['case']]
                self.assertEqual(result['status'], row['expected_status'])
                self.assertEqual(result['stop']['status'] if result.get('stop') else None, row['expected_stop'])
                self.assertEqual(result['remaining_operations'], row['request']['operations'][len(result['trace']):])

    def test_checked_unsold_opening_and_partial_control(self):
        opening = self.results['empty']['period_book']; result = self.results['partial']; book = result['period_book']
        self.assertEqual(opening['after']['lots']['recovered']['units'], '2/1')
        self.assertEqual(opening['after']['balances']['income_tax_payable'], '-41/4')
        self.assertEqual(book['after']['balances']['income_tax_payable'], '-41/4')
        self.assertEqual(book['after']['balances']['cash'], '467/1')
        self.assertEqual(book['after']['balances']['inventory'], '70/1')
        self.assertEqual(book['after']['lots']['recovered']['units'], '1/1')
        self.assertEqual(result['recorded_statements']['recorded_profit'], '5/1')
        self.assertEqual(result['recorded_statements']['cash_flows']['activities']['operating']['net'], '15/1')
        self.assertEqual(len(book['after']['balances']), 26)

    def test_full_sale_matches_original_annual_financial_state(self):
        old = m.annual.run(x.native_full_sale()); new = self.results['full']
        self.assertEqual(old['status'], 'complete_provisional')
        for key in ['period_book', 'recorded_statements', 'stop', 'remaining_operations']:
            self.assertEqual(new[key], old[key])
        for key in ['journal', 'flows', 'after']:
            self.assertEqual(new['trace'][0]['result'][key], old['trace'][0]['result'][key])

    def test_existing_programs_delegate_all_financial_fields_unchanged(self):
        old_requests = [x.previous.scenario(), x.previous.repeated_scenario()]
        for request in old_requests:
            old = m.annual.run(request)
            new = m.run(m.request(request['root_request'], request['operations']))
            for key, value in old.items():
                if key not in ['profile', 'request_sha256', 'source_bundle_sha256', 'implementation_sha256']:
                    self.assertEqual(new[key], value, key)

    def test_liabilities_assessments_and_archives_do_not_change_during_sale(self):
        result = self.results['after_assessment']; before = result['trace'][1]['result']['after']; after = result['period_book']
        for key in ['period_vintages', 'opening_vintages', 'historical_vintages', 'current_assessments',
                    'deferred_assessments', 'loss_state', 'opening_loss', 'known_loss_ids', 'period_archive',
                    'recognition_archive', 'opening', 'findings', 'prior_findings']:
            self.assertEqual(after[key], before[key], key)
        for key in ['income_tax_payable', 'current_tax', 'deferred_tax', 'dta', 'dtl']:
            self.assertEqual(after['after']['balances'][key], before['after']['balances'][key])
        self.assertEqual(after['current_period_tax'], 'activity_after_assessment')
        self.assertEqual(after['current_period_deferred_tax'], 'stale')
        self.assertEqual(after['unassessed_native_events'][-1], 'inventory-partial')

    def test_assessment_timing_and_stale_measurement_vetoes(self):
        expected = {'inside_assessment': 'event_inside_assessed_interval',
                    'stale_carry': 'assessments_incomplete',
                    'measurement_without_reassessment': 'current_assessment_required',
                    'stale_measurement': 'measurement_state_digest'}
        for name, reason in expected.items():
            self.assertEqual(self.results[name]['stop']['reason'], reason)

    def test_residual_stock_survives_boundary_then_is_sold(self):
        result = self.results['residual_carry_and_sale']; state = result['period_book']
        self.assertEqual(result['status'], 'complete_provisional')
        archived = state['period_archive'][0]
        self.assertEqual(archived['after']['lots']['recovered']['units'], '1/1')
        self.assertEqual(archived['after']['lots']['recovered']['carrying'], '10/1')
        self.assertEqual(state['opening']['lots'], archived['after']['lots'])
        self.assertEqual(state['after']['lots']['recovered']['units'], '0/1')
        self.assertTrue(state['after']['lots']['recovered']['disposed'])
        self.assertEqual(state['after']['balances']['cash'], '482/1')
        self.assertEqual(state['after']['balances']['income_tax_payable'], '-49/4')
        self.assertEqual(archived['report']['recorded_profit'], '3/1')
        self.assertEqual(result['recorded_statements']['recorded_profit'], '5/1')
        self.assertEqual(result['recorded_statements']['cash_flows']['activities']['operating']['net'], '15/1')

    def test_fresh_reassessment_and_measurement_allow_carry(self):
        result = self.results['refreshed_carry']; state = result['period_book']; archived = state['period_archive'][0]
        self.assertEqual(result['status'], 'complete_provisional')
        self.assertEqual(state['current_period_tax'], 'unassessed')
        self.assertEqual(state['current_period_deferred_tax'], 'unassessed')
        self.assertEqual(archived['current_period_tax'], 'conditionally_assessed')
        self.assertEqual(archived['current_period_deferred_tax'], 'conditionally_assessed')
        self.assertEqual(len(archived['current_assessments']), 2)
        self.assertEqual(len(archived['deferred_assessments']), 2)
        self.assertEqual(state['after']['balances']['income_tax_payable'], '-53/4')
        self.assertEqual(state['after']['lots']['recovered']['units'], '1/1')

    def test_every_populated_statement_and_journal_reconciles(self):
        for result in self.results.values():
            self.assertEqual(set(result['recorded_statements']['reconciliations'].values()), {'0/1'})
            m.annual.invariant(result['period_book'])
            for row in result['trace']:
                self.assertEqual(sum(Q(v) for v in row['result']['journal'].values()), 0)
                self.assertEqual(Q(row['result']['journal']['cash']), sum(Q(f['amount']) for f in row['result']['flows']))

    def test_oversale_retains_prior_sale_and_remaining_operations(self):
        result = self.results['retained_prefix']
        self.assertEqual(len(result['trace']), 1)
        self.assertEqual(len(result['remaining_operations']), 2)
        self.assertEqual(result['period_book']['after']['balances']['cash'], '467/1')
        self.assertEqual(result['period_book']['after']['lots']['recovered']['units'], '1/1')

    def test_complete_apply_rejects_tax_archive_and_quantity_tampering(self):
        row = next(r for r in self.rows if r['case'] == 'residual_carry_and_sale')
        result = self.results[row['case']]
        self.assertEqual(m.apply(row['request'], result)['status'], 'applied_provisional')
        changes = [lambda z: z['period_book']['after']['balances'].update(income_tax_payable='0/1'),
                   lambda z: z['period_book']['period_archive'][0]['after']['lots']['recovered'].update(units='999/1'),
                   lambda z: z['period_book']['period_vintages'][0].update(closing_payable='0/1'),
                   lambda z: z['trace'][0]['result']['details'].update(released_carrying='0/1')]
        for change in changes:
            bad = deepcopy(result); change(bad)
            self.assertEqual(m.apply(row['request'], bad)['status'], 'invalid')

    def test_missing_root_and_nonportable_inputs_refused(self):
        q = m.request(x.root(), [x.sale()]); q['root_sha256'] = '0'*64
        self.assertEqual(m.run(q)['status'], 'invalid')
        q = m.request(x.root(), [x.sale()]); q['operations'][0]['event']['sold_units'] = 1.0
        self.assertEqual(m.run(q)['status'], 'invalid')

    def test_unknown_and_false_findings_remain_distinct(self):
        self.assertEqual(self.results['unknown_findings']['stop']['status'], 'unresolved')
        self.assertEqual(self.results['false_findings']['stop']['status'], 'unsupported')
        self.assertEqual(self.results['unknown_findings']['period_book'], self.results['empty']['period_book'])

    def test_old_authoring_refuses_new_operation_and_inputs_stay_exact(self):
        import annual_program_authoring_v1 as author
        row = next(r for r in self.rows if r['case'] == 'partial'); body = deepcopy(row['request'])
        before = m.annual.caller.canonical(body); result = m.run(body)
        self.assertEqual(before, m.annual.caller.canonical(body))
        with self.assertRaises(author.Invalid):
            author.from_request(m.annual.request(body['root_request'], body['operations']))
        for key in ['source_admission', 'accounting_admission', 'annual_ready', 'general_annual_execution', 'committed']:
            self.assertIs(result[key], False)


if __name__ == '__main__':
    unittest.main()
