from copy import deepcopy
from pathlib import Path
import importlib.util
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import declared_company_program_v1 as program
spec = importlib.util.spec_from_file_location('declared_program_examples', ROOT / 'data/accounting-master/declared-company-program-20261025/examples.py')
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)


class DeclaredCompanyProgramTests(unittest.TestCase):
    def run_body(self, body, status='complete_provisional'):
        original = deepcopy(body); result = program.run(body)
        self.assertEqual(result['status'], status, result.get('stop', result))
        self.assertEqual(body, original)
        for key in program.FLAGS:self.assertIs(result[key], False)
        return result

    def stopped(self, body, index):
        result = self.run_body(body, 'stopped_provisional')
        self.assertEqual(len(result['trace']), index)
        self.assertEqual(result['stop']['index'], index)
        self.assertEqual(result['stop']['command'], body['commands'][index])
        self.assertEqual(result['remaining_commands'], body['commands'][index:])
        expected = result['trace'][-1]['after_sha256'] if index else program.digest(body['opening'])
        self.assertEqual(program.digest(result['current']), expected)
        self.assertTrue(program.verify(body, result))
        return result

    def test_manual_composition_and_independent_two_chart_arithmetic(self):
        result = ex.compare()
        self.assertEqual(len(result['cases']), 2)
        self.assertEqual([x['name'] for x in result['checks'] if not x['passed']], [])

    def test_interim_cutoff_only_advances_observation_date(self):
        result = self.run_body(ex.fixture()); previous = result['trace'][0]['result']['transition']['after']
        observed = result['trace'][1]['request']['closing']
        expected = deepcopy(previous); expected['date'] = '2027-06-30'
        self.assertEqual(observed, expected)
        self.assertEqual(result['trace'][1]['observation']['before_sha256'], program.digest(previous))
        self.assertFalse(result['trace'][1]['result']['fiscal_complete'])

    def test_requests_use_actual_current_state_and_new_period_opening(self):
        result = self.run_body(ex.fixture())
        for row in result['trace']:
            if row['command']['kind'] == 'event':self.assertEqual(row['request']['expected_state_sha256'], row['before_sha256'])
        after_carry = result['trace'][4]['result']['next_opening']
        self.assertEqual(result['trace'][7]['request']['opening'], after_carry)
        self.assertEqual(result['trace'][7]['result']['equity']['opening'], '125/1')
        self.assertEqual(result['trace'][9]['result']['income']['profit'], '0/1')

    def test_archive_and_report_indexes_resolve_exact_trace_results(self):
        result = self.run_body(ex.fixture())
        for item in result['reports']:
            row = result['trace'][item['index']]
            actual = row['result'] if row['command']['kind'] == 'report' else row['result']['report']
            self.assertEqual(item['report_sha256'], program.digest(actual))
        for item in result['archives']:self.assertEqual(item['archive'], result['trace'][item['index']]['result']['archive'])

    def test_unknown_finding_preserves_successful_prefix(self):
        body = ex.fixture();body['commands'][2]['event']['inputs']['approved']['value'] = {'status': 'unknown', 'reason': 'No finding supplied'}
        result = self.stopped(body, 2)
        self.assertEqual(result['stop']['status'], 'unresolved')
        self.assertEqual(result['current']['date'], '2027-06-30')

    def test_false_finding_preserves_unsupported_reason(self):
        body = ex.fixture();body['commands'][2]['event']['inputs']['approved']['value']['value'] = False
        result = self.stopped(body, 2)
        self.assertEqual(result['stop']['status'], 'unsupported')
        self.assertEqual(result['stop']['result']['transition']['reason'], 'preconditions')

    def test_state_prerequisite_runs_at_turn_not_against_initial_book(self):
        body = ex.fixture();body['commands'][6]['event']['inputs']['amount']['value']['value'] = '30/1'
        result = self.stopped(body, 6)
        self.assertEqual(result['stop']['status'], 'invalid')
        self.assertEqual(result['current']['balances']['note.alpha'], '-53/2')

    def test_failed_report_does_not_commit_observation(self):
        body = ex.fixture();body['commands'][1]['equity_movements'] = [{'id': 'false', 'event_id': 'sale.2027', 'date': '2027-02-01',
            'account': 'capital.alpha', 'amount': '1/1', 'description': 'Unsubstantiated equity change'}]
        result = self.stopped(body, 1)
        self.assertEqual(result['current']['date'], '2027-02-01')
        self.assertEqual(result['stop']['observation']['cutoff'], '2027-06-30')

    def test_failed_carry_preserves_prior_period_and_full_report_prefix(self):
        body = ex.fixture();body['commands'][4]['memory_policies'].pop('/loan/paid')
        result = self.stopped(body, 4)
        self.assertEqual(result['current']['period'], body['opening']['period'])
        self.assertEqual(result['current']['balances']['sales.alpha'], '-40/1')
        self.assertEqual(result['archives'], [])

    def test_midperiod_carry_is_refused(self):
        body = ex.fixture();body['commands'] = body['commands'][:2] + [{**body['commands'][4], 'cutoff': '2027-06-30'}]
        result = self.stopped(body, 2)
        self.assertEqual(result['stop']['result']['reason'], 'last_period_day_required')

    def test_event_and_report_date_bounds_and_authored_order(self):
        for index, field, day in [(2, 'event', '2027-06-29'), (2, 'event', '2028-01-01'), (1, 'cutoff', '2027-01-01'), (1, 'cutoff', '2028-01-01')]:
            body = ex.fixture()
            if field == 'event':body['commands'][index][field]['date'] = day
            else:body['commands'][index][field] = day
            self.stopped(body, index)

    def test_duplicate_event_close_and_report_ids_do_not_erase_prefix(self):
        for index, value in [(2, 'sale.2027'), (4, 'annual.2027'), (8, 'close.2027'), (7, 'interim.2027')]:
            body = ex.fixture()
            if body['commands'][index]['kind'] == 'event':body['commands'][index]['event']['id'] = value
            else:body['commands'][index]['id'] = value
            self.assertEqual(self.stopped(body, index)['stop']['reason'], 'duplicate_command_identity')

    def test_structurally_invalid_later_command_prevents_execution(self):
        body = ex.fixture();body['commands'][-1]['expected_state_sha256'] = '0' * 64
        result = self.run_body(body, 'invalid');self.assertNotIn('trace', result)
        body = ex.fixture();body['commands'][-1]['notes'][0]['status'] = 'complete'
        self.run_body(body, 'invalid')

    def test_unused_broken_registry_entry_and_mismatched_schema_rejected(self):
        body = ex.fixture();body['registry']['entries']['unused'] = deepcopy(body['registry']['entries']['pay'])
        body['registry']['entries']['unused']['method_sha256'] = '0' * 64
        self.run_body(body, 'invalid')
        body = ex.fixture();key = body['registry']['entries']['sell']['method']['memory']['definition']['input_schema'];del body['schemas'][key]
        self.run_body(body, 'invalid')

    def test_unsupported_method_and_clock_are_not_reported_as_success(self):
        body = ex.fixture();body['commands'][2]['method_key'] = 'unknown'
        self.run_body(body, 'unsupported')
        body = ex.fixture();body['registry']['entries']['sell']['clock']['kind'] = 'assessment_interval'
        self.run_body(body, 'unsupported')

    def test_changed_program_or_result_fails_canonical_replay(self):
        body = ex.fixture();result = self.run_body(body)
        for kind in ['boolean', 'opening', 'trace', 'archive', 'report']:
            bad = deepcopy(result)
            if kind == 'boolean':bad['committed'] = 0
            elif kind == 'opening':bad['opening']['memory']['untouched']['tag'] = 'lost'
            elif kind == 'trace':bad['trace'].pop()
            elif kind == 'archive':bad['archives'][0]['archive']['report_sha256'] = '0' * 64
            else:bad['reports'][0]['report_sha256'] = '0' * 64
            self.assertFalse(program.verify(body, bad))
        changed = deepcopy(body);changed['name'] = 'different'
        self.assertFalse(program.verify(changed, result))

    def test_input_and_trace_budgets_preserve_bounded_failure(self):
        body = ex.fixture();body['commands'] = body['commands'] * 7
        self.run_body(body, 'invalid')
        body = ex.fixture();complete = self.run_body(body)
        first_size = len(program.core.canonical(complete['trace'][0])) + 2
        with patch.object(program, 'MAX_TRACE_BYTES', first_size):
            result = self.stopped(body, 1)
            self.assertEqual(result['stop']['reason'], 'trace_size_limit')
            self.assertIn('result_sha256', result['stop'])

    def test_dependency_change_and_empty_program_are_rejected(self):
        with patch.dict(program.PINS, {'company_book_carry_v1.py': '0' * 64}):self.run_body(ex.fixture(), 'invalid')
        body = ex.fixture();body['commands'] = [];self.run_body(body, 'invalid')

    def test_zero_profit_can_require_nonzero_temporary_closing_entries(self):
        body = ex.fixture();body['commands'] = [body['commands'][0], body['commands'][4]]
        body['commands'][0]['event']['inputs']['proceeds']['value']['value'] = '15/1'
        result = self.run_body(body);close = result['trace'][1]['result']
        self.assertEqual(close['report']['income']['profit'], '0/1')
        self.assertEqual(close['journal']['capital.alpha'], '0/1')
        self.assertEqual(close['journal']['sales.alpha'], '15/1')
        self.assertEqual(close['journal']['cost.alpha'], '-15/1')


if __name__ == '__main__':unittest.main()
