from copy import deepcopy
from pathlib import Path
import importlib.util
import sys
import unittest
from hashlib import sha256

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import declared_financing_schedules_v1 as schedules

spec = importlib.util.spec_from_file_location(
    'financing_schedule_examples',
    ROOT / 'data/accounting-master/declared-financing-clock-20261025/examples.py')
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)


def request(body, result, report_id='annual'):
    roles = {}
    for entry in body['registry']['entries'].values():
        for role, account in entry['method']['account_map'].items():
            if role in schedules.financing.CLASSES:
                roles[role] = account
    if set(roles) != set(schedules.financing.CLASSES):
        raise AssertionError('fixture did not expose every financing role')
    return schedules.request(body, result, report_id, roles, '/finance/cursor',
                             '/finance/debt', ex.POLICY, ex.INTERVALS)


class DeclaredFinancingSchedulesTests(unittest.TestCase):
    def make(self, owner='alpha', commands=None):
        body, _, _, mapping = ex.fixture(owner)
        if commands is not None:
            body['commands'] = deepcopy(commands)
        result = ex.program.run(body)
        self.assertIn(result['status'], ['complete_provisional', 'stopped_provisional'])
        return body, result, mapping

    def test_complete_financing_schedules_and_coverage(self):
        body, result, _ = self.make()
        out = schedules.report(request(body, result))
        self.assertEqual(out['status'], 'reported', out)
        self.assertEqual(out['interest_expense'], '31/5')
        self.assertTrue(out['interest_coverage']['complete_for_selected_period'])
        self.assertEqual(out['interest_coverage']['needs'], [])
        self.assertEqual(out['schedules']['debt']['opening'], '0/1')
        self.assertEqual(out['schedules']['debt']['closing'], '80/1')
        self.assertEqual(out['schedules']['interest_payable']['closing'], '11/5')
        self.assertEqual(out['financing_cash']['by_activity']['financing'], '105/1')
        self.assertEqual(out['financing_cash']['by_activity']['operating'], '-4/1')
        self.assertTrue(schedules.verify(request(body, result), out))

    def test_two_charts_have_identical_schedule_amounts(self):
        first, first_result, _ = self.make('alpha')
        second, second_result, _ = self.make('beta')
        a = schedules.report(request(first, first_result))
        b = schedules.report(request(second, second_result))
        self.assertEqual(a['status'], b['status'])
        for key in schedules.SCOPED:
            self.assertEqual(a['schedules'][key]['opening'], b['schedules'][key]['opening'])
            self.assertEqual(a['schedules'][key]['closing'], b['schedules'][key]['closing'])
            self.assertEqual(a['schedules'][key]['categories'], b['schedules'][key]['categories'])
        for x, y in zip(a['interest_coverage']['intervals'], b['interest_coverage']['intervals']):
            self.assertEqual((x['start'], x['end_exclusive'], x['days'], x['principal'], x['interest']),
                             (y['start'], y['end_exclusive'], y['days'], y['principal'], y['interest']))

    def test_selected_report_before_final_interest_is_a_coverage_gap(self):
        body, _, _, mapping = ex.fixture()
        commands = deepcopy(body['commands'])
        commands = commands[:8] + [{
            'kind': 'report', 'id': 'early', 'cutoff': '2027-03-31',
            'equity_movements': [], 'notes': []}]
        body['commands'] = commands
        result = ex.program.run(body)
        self.assertEqual(result['status'], 'complete_provisional')
        out = schedules.report(request(body, result, 'early'))
        self.assertEqual(out['status'], 'reported', out)
        coverage = out['interest_coverage']
        self.assertTrue(coverage['complete_for_selected_period'])
        self.assertEqual(coverage['closing_cursor'], '2027-04-01')
        self.assertEqual(coverage['expected_end_exclusive'], '2027-04-01')

    def test_stopped_program_can_select_prior_successful_report(self):
        body, _, _, _ = ex.fixture()
        commands = deepcopy(body['commands'])
        commands = commands[:8] + [{
            'kind': 'report', 'id': 'early', 'cutoff': '2027-03-31',
            'equity_movements': [], 'notes': []},
            deepcopy(body['commands'][-1])]
        commands[-1]['id'] = 'bad-report'
        commands[-1]['cutoff'] = '2027-01-01'
        body['commands'] = commands
        result = ex.program.run(body)
        self.assertEqual(result['status'], 'stopped_provisional')
        out = schedules.report(request(body, result, 'early'))
        self.assertEqual(out['status'], 'reported', out)
        self.assertEqual(out['report_id'], 'early')

    def test_tampered_program_result_is_refused(self):
        body, result, _ = self.make()
        bad = deepcopy(result)
        bad['current']['balances']['debt'] = '-81/1'
        out = schedules.report(request(body, bad))
        self.assertEqual(out['status'], 'invalid')
        self.assertIn(out['reason'], ['stale_input', 'unverified_program_result'])

    def test_tampered_policy_or_interval_identity_is_refused(self):
        body, result, _ = self.make()
        q = request(body, result)
        q['policy']['annual_rate'] = '1/10'
        self.assertIn(schedules.report(q)['status'], ['invalid', 'unsupported'])
        q = request(body, result)
        q['intervals'][0]['end_exclusive'] = '2027-03-30'
        self.assertIn(schedules.report(q)['status'], ['invalid', 'unsupported'])

    def test_unknown_scoped_method_cannot_be_silently_classified(self):
        body, _, _, mapping = ex.fixture()
        entry = deepcopy(body['registry']['entries']['debt_issue'])
        identity = 'synthetic.financing.unknown_issue'
        entry['method']['id'] = identity
        entry['method']['preconditions']['manifest']['method_id'] = identity
        entry['method']['postconditions']['manifest']['method_id'] = identity
        entry['method']['monetary']['definition']['method_id'] = identity
        entry['method_sha256'] = ex.program.digest(entry['method'])
        body['registry']['entries']['unknown_issue'] = entry
        body['commands'] = [ex.event(body, 'unknown_issue', 'unknown.1', '2027-01-01',
                                     {'amount': '10/1'}),
                            {'kind': 'report', 'id': 'annual', 'cutoff': '2027-01-01',
                             'equity_movements': [], 'notes': []}]
        result = ex.program.run(body)
        self.assertEqual(result['status'], 'complete_provisional')
        out = schedules.report(request(body, result))
        self.assertEqual(out['status'], 'unsupported')
        self.assertIn('unclassified_gross_financing_movement', out['reason'])

    def test_cursor_or_debt_memory_change_is_not_a_gap(self):
        body, result, _ = self.make()
        trace = result['trace']
        trace[0]['result']['transition']['after']['memory']['finance']['debt'] = '-999/1'
        out = schedules.report(request(body, result))
        self.assertEqual(out['status'], 'invalid')
        self.assertIn(out['reason'], ['stale_input', 'unverified_program_result'])

    def test_next_period_opening_preserves_unpaid_interest(self):
        body, _, _, mapping = ex.fixture()
        commands = deepcopy(body['commands'])
        commands = commands[:8] + [{
            'kind': 'report', 'id': 'early', 'cutoff': '2027-03-31',
            'equity_movements': [], 'notes': []},
            {'kind': 'carry', 'id': 'carry', 'cutoff': '2027-12-31',
             'equity_movements': [], 'notes': [], 'retained_account': mapping['retained'],
             'next_end_exclusive': '2029-01-01',
             'memory_policies': {key: {'kind': 'preserve', 'provenance': 'Explicit'}
                                 for key in body['opening']['memory_types']}}]
        body['commands'] = commands
        result = ex.program.run(body)
        self.assertEqual(result['status'], 'complete_provisional', str(result)[:500])
        out = schedules.report(request(body, result, 'early'))
        self.assertEqual(out['status'], 'reported')
        self.assertEqual(out['interest_coverage']['complete_for_selected_period'], True)
        self.assertEqual(out['schedules']['interest_payable']['closing'], '9/5')

    def test_builder_dependency_and_role_pins_are_checked(self):
        body, _, _, mapping = ex.fixture()
        schedules.PINS['declared_company_program_v2.py'] = '0' * 64
        try:
            out = schedules.report(request(body, ex.program.run(body)))
        finally:
            schedules.PINS['declared_company_program_v2.py'] = sha256(
                (ROOT / 'scripts/declared_company_program_v2.py').read_bytes()).hexdigest()
        self.assertEqual(out['status'], 'invalid')
        self.assertIn('dependency_hash', out['reason'])


if __name__ == '__main__':
    unittest.main()
