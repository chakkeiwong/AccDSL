"""Discriminating evidence missing from the original schedule test packet."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('schedule_evidence_examples',
    ROOT / 'data/accounting-master/declared-financing-schedules-validation-20261025/examples.py')
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)


class FinancingScheduleEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base, cls.mapping = ex.fixture()

    def small(self, indices=(0, 7), cutoff='2027-03-31', ident='annual'):
        body = ex.subset(self.base, indices)
        body['commands'].append(ex.report_command(ident, cutoff))
        return body

    def run_schedule(self, body, report_id='annual'):
        result = ex.program.run(body)
        self.assertIn(result['status'], ['complete_provisional', 'stopped_provisional'], str(result)[:300])
        request = ex.request(body, result, self.mapping, report_id)
        output = ex.schedules.report(request)
        return result, request, output

    def test_actual_missing_final_interval_is_exposed_without_changing_balances(self):
        body = self.small(cutoff='2027-12-31')
        result, _, output = self.run_schedule(body)
        self.assertEqual(result['status'], 'complete_provisional')
        self.assertEqual(output['status'], 'reported')
        self.assertEqual(output['schedules']['debt']['closing'], '100/1')
        self.assertEqual(output['schedules']['interest_payable']['closing'], '9/5')
        self.assertFalse(output['interest_coverage']['complete_for_selected_period'])
        self.assertEqual(output['interest_coverage']['needs'], [
            {'kind': 'unaccrued_interval', 'start': '2027-04-01', 'end_exclusive': '2028-01-01'}])
        self.assertFalse(output['fiscal_complete'])

    def test_no_accrual_does_not_mean_zero_interest_is_complete(self):
        _, _, output = self.run_schedule(self.small(indices=(0,), cutoff='2027-12-31'))
        self.assertEqual(output['status'], 'reported')
        self.assertEqual(output['interest_expense'], '0/1')
        self.assertEqual(output['interest_coverage']['intervals'], [])
        self.assertEqual(output['interest_coverage']['needs'][0],
            {'kind': 'unaccrued_interval', 'start': '2027-01-01', 'end_exclusive': '2028-01-01'})

    def test_quarter_report_is_complete_only_through_its_own_cutoff(self):
        _, _, output = self.run_schedule(self.small())
        self.assertEqual(output['status'], 'reported')
        self.assertTrue(output['interest_coverage']['complete_for_selected_period'])
        self.assertEqual(output['interest_coverage']['expected_end_exclusive'], '2027-04-01')
        self.assertEqual([x['days'] for x in output['interest_coverage']['intervals']], [90])
        self.assertFalse(output['notes_complete'])

    def test_selected_carry_report_exposes_omitted_interest_before_closing(self):
        body = ex.subset(self.base, (0, 7))
        body['commands'].append(ex.carry_command(body, self.mapping))
        result, _, output = self.run_schedule(body, 'carry')
        self.assertEqual(result['status'], 'complete_provisional')
        self.assertEqual(output['status'], 'reported')
        self.assertEqual(output['interest_expense'], '9/5')
        self.assertEqual(output['schedules']['retained']['closing'], '0/1')
        self.assertEqual(result['current']['balances']['retained'], '9/5')
        self.assertFalse(output['interest_coverage']['complete_for_selected_period'])

    def test_next_period_schedule_uses_carried_opening_and_retains_old_gap(self):
        body = deepcopy(self.base)
        payment = ex.finance.event(body, 'interest_pay', 'next-pay', '2028-01-01', {'amount': '1/1'})
        body['commands'] = [body['commands'][0], body['commands'][7],
                            ex.carry_command(body, self.mapping), payment,
                            ex.report_command('next-report', '2028-01-01')]
        ex.prune(body)
        result, _, output = self.run_schedule(body, 'next-report')
        self.assertEqual(result['status'], 'complete_provisional')
        self.assertEqual(output['status'], 'reported')
        row = output['schedules']['interest_payable']
        self.assertEqual((row['opening'], row['increases'], row['decreases'], row['closing']),
                         ('9/5', '0/1', '1/1', '4/5'))
        self.assertEqual([x['event_id'] for x in row['movements']], ['next-pay'])
        self.assertEqual(output['interest_expense'], '0/1')
        self.assertEqual(output['opening_sha256'], ex.program.digest(result['trace'][2]['result']['next_opening']))
        self.assertEqual(output['period']['start'], '2028-01-01')
        self.assertEqual(output['interest_coverage']['intervals'], [])
        self.assertEqual({x['kind'] for x in output['interest_coverage']['needs']},
                         {'opening_coverage_mismatch', 'unaccrued_interval'})

    def test_later_valid_events_do_not_contaminate_the_selected_report(self):
        body = self.small()
        body['commands'].append(ex.finance.event(body, 'debt_issue', 'later', '2027-04-01', {'amount': '20/1'}))
        result, _, output = self.run_schedule(body)
        self.assertEqual(result['status'], 'complete_provisional')
        self.assertEqual(result['current']['balances']['debt'], '-120/1')
        self.assertEqual(output['schedules']['debt']['closing'], '100/1')
        self.assertEqual(len(output['schedules']['debt']['movements']), 1)

    def test_stopped_later_event_retains_the_prior_report(self):
        body = self.small()
        body['commands'].append(ex.finance.event(body, 'debt_issue', 'bad-boundary', '2027-04-02', {'amount': '20/1'}))
        result, _, output = self.run_schedule(body)
        self.assertEqual(result['status'], 'stopped_provisional')
        self.assertEqual(result['stop']['index'], 3)
        self.assertEqual(output['status'], 'reported')
        self.assertEqual(output['schedules']['debt']['closing'], '100/1')

    def test_failed_report_cannot_be_selected(self):
        body = self.small()
        body['commands'].append(ex.report_command('backdated', '2027-01-01'))
        result, _, output = self.run_schedule(body, 'backdated')
        self.assertEqual(result['status'], 'stopped_provisional')
        self.assertEqual(output['status'], 'invalid')
        self.assertEqual(output['reason'], 'successful_report_required')

    def test_gross_offsetting_debt_postings_are_rejected_despite_zero_net(self):
        body = ex.unknown_method(deepcopy(self.base), gross=True)
        result, _, output = self.run_schedule(body)
        self.assertEqual(result['status'], 'complete_provisional')
        self.assertEqual(result['trace'][0]['result']['transition']['journal']['debt'], '0/1')
        self.assertEqual(output['status'], 'unsupported')
        self.assertEqual(output['reason'], 'unclassified_gross_financing_movement:foreign')

    def test_valid_foreign_cursor_event_is_rejected_rather_than_labelled_a_gap(self):
        body = ex.unknown_method(deepcopy(self.base), gross=False)
        result, _, output = self.run_schedule(body)
        self.assertEqual(result['status'], 'complete_provisional')
        self.assertEqual(result['current']['memory']['finance']['cursor'], '2027-02-01')
        self.assertEqual(output['status'], 'unsupported')
        self.assertEqual(output['reason'], 'unclassified_financing_memory_change:foreign')

    def test_rehashed_forged_result_is_refused_by_recomputation(self):
        body = self.small()
        result = ex.program.run(body)
        result['trace'][1]['result']['transition']['journal']['interest'] = '2/1'
        request = ex.request(body, result, self.mapping)
        output = ex.schedules.report(request)
        self.assertEqual(output['reason'], 'unverified_program_result')

    def test_unrehashed_input_digest_and_changed_schedule_do_not_verify(self):
        body = self.small()
        _, request, output = self.run_schedule(body)
        bad = deepcopy(request)
        bad['result_sha256'] = '0' * 64
        self.assertEqual(ex.schedules.report(bad)['reason'], 'stale_input')
        output['schedules']['debt']['closing'] = '999/1'
        self.assertFalse(ex.schedules.verify(request, output))

    def test_changed_policy_and_broken_interval_refuse_for_exact_reasons(self):
        _, request, _ = self.run_schedule(self.small())
        policy = deepcopy(request)
        policy['policy']['annual_rate'] = '1/10'
        changed = ex.schedules.report(policy)
        self.assertEqual(changed['status'], 'unsupported')
        self.assertEqual(changed['reason'], 'unclassified_gross_financing_movement:issue.1')
        broken = deepcopy(request)
        broken['intervals'][0]['end_exclusive'] = '2027-03-30'
        self.assertEqual(ex.schedules.report(broken)['reason'], 'contiguous_positive_intervals')

    def test_renamed_registry_key_preserves_schedule_classification(self):
        body = self.small()
        body['registry']['entries']['borrow'] = body['registry']['entries'].pop('debt_issue')
        body['commands'][0]['method_key'] = 'borrow'
        result, _, output = self.run_schedule(body)
        self.assertEqual(result['status'], 'complete_provisional')
        self.assertEqual(output['schedules']['debt']['categories'], {'issued': '100/1'})
        self.assertTrue(output['interest_coverage']['complete_for_selected_period'])

    def test_required_dependency_hash_is_checked_before_replay(self):
        request = ex.request(self.base, {}, self.mapping)
        with patch.dict(ex.schedules.PINS, {'declared_company_program_v2.py': '0' * 64}):
            result = ex.schedules.report(request)
        self.assertEqual(result['status'], 'invalid')
        self.assertEqual(result['reason'], 'dependency_hash:declared_company_program_v2.py')


if __name__ == '__main__':
    unittest.main()
