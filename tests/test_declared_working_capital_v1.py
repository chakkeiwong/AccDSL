from copy import deepcopy
from pathlib import Path
import importlib.util
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1];sys.path.insert(0, str(ROOT / 'scripts'))
import declared_working_capital_v1 as schedules
spec = importlib.util.spec_from_file_location('working_capital_examples', ROOT / 'data/accounting-master/declared-working-capital-20261025/examples.py')
ex = importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)


def refreshed(body):
    body['result'] = ex.program.run(body['program'])
    body['program_sha256'] = ex.program.digest(body['program']);body['result_sha256'] = ex.program.digest(body['result'])
    return body


class WorkingCapitalTests(unittest.TestCase):
    def test_two_charts_stopped_carry_and_second_period_controls(self):
        result = ex.compare();self.assertEqual(len(result['cases']), 5)
        self.assertEqual([c['name'] for c in result['checks'] if not c['passed']], [])

    def test_every_movement_resolves_exact_trace_and_provenance(self):
        body = ex.fixture();result = schedules.report(body);self.assertEqual(result['status'], 'reported')
        for schedule in result['schedules'].values():
            for movement in schedule['movements']:
                row = body['result']['trace'][movement['trace_index']]
                self.assertEqual(movement['request_sha256'], ex.program.digest(row['request']))
                self.assertEqual(movement['result_sha256'], ex.program.digest(row['result']))
                self.assertEqual(movement['event_id'], row['command']['event']['id'])
                self.assertEqual(movement['inputs'], row['command']['event']['inputs'])
                if 'units' in movement:
                    self.assertEqual(movement['unit_cost']['value'], '5/1')
                    self.assertEqual(movement['unit_cost']['opening_sha256'], result['opening_sha256'])

    def test_aliasing_registry_keys_does_not_change_method_classification(self):
        body = ex.fixture();p = body['program'];p['registry']['entries']['alias'] = p['registry']['entries'].pop('purchase')
        p['commands'][0]['method_key'] = 'alias';refreshed(body)
        result = schedules.report(body);self.assertEqual(result['status'], 'reported')
        self.assertEqual(result['schedules']['inventory']['categories'], {'purchases': '30/1', 'cost_released': '-25/1'})

    def test_changed_definition_with_same_key_cannot_be_misclassified(self):
        body = ex.fixture();entry = body['program']['registry']['entries']['purchase']
        entry['method']['residual_prerequisites'].append('Changed method meaning')
        entry['method_sha256'] = ex.program.digest(entry['method']);refreshed(body)
        self.assertEqual(body['result']['status'], 'complete_provisional')
        result = schedules.report(body);self.assertEqual(result['status'], 'unsupported')
        self.assertIn('unclassified_scoped_movement', result['reason'])

    def test_balanced_unsupported_net_zero_movement_is_not_hidden(self):
        body = ex.fixture();p = body['program']
        for key in ['purchase', 'deliver']:
            entry = p['registry']['entries'][key];entry['method']['residual_prerequisites'].append('Unclassified alternative')
            entry['method_sha256'] = ex.program.digest(entry['method'])
        p['commands'][1]['event']['inputs']['units']['value']['value'] = '6/1';refreshed(body)
        self.assertEqual(body['result']['current']['balances']['inventory'], '20/1')
        self.assertEqual(schedules.report(body)['status'], 'unsupported')

    def test_tampered_result_even_with_recomputed_digest_refuses(self):
        for target in ['current', 'trace', 'opening']:
            body = ex.fixture()
            if target == 'current':body['result']['current']['balances']['cash'] = '108/1'
            elif target == 'trace':body['result']['trace'][0]['result']['transition']['journal']['inventory'] = '31/1'
            else:body['result']['trace'][-1]['request']['opening']['balances']['cash'] = '101/1'
            body['result_sha256'] = ex.program.digest(body['result'])
            self.assertEqual(schedules.report(body)['reason'], 'unverified_program_result')

    def test_failed_or_missing_report_cannot_be_selected(self):
        body = ex.fixture(variant='stopped');body['report_id'] = 'late.unknown'
        self.assertEqual(schedules.report(body)['reason'], 'successful_report_required')
        body = ex.fixture();body['report_id'] = 'absent';self.assertEqual(schedules.report(body)['status'], 'invalid')
        body = ex.fixture();p = body['program'];p['commands'][-1]['cutoff'] = '2027-01-01';refreshed(body)
        self.assertEqual(schedules.report(body)['reason'], 'successful_report_required')

    def test_second_period_excludes_prior_movements_and_closing_journal(self):
        body = ex.fixture(variant='second_period');result = schedules.report(body)
        self.assertEqual(result['period']['start'], '2028-01-01')
        events = {m['event_id'] for row in result['schedules'].values() for m in row['movements']}
        self.assertEqual(events, {'collect.2028', 'pay.2028'})
        self.assertEqual(result['schedules']['inventory']['movements'], [])
        self.assertEqual(result['schedules']['payroll_payable']['closing'], '2/1')

    def test_wrong_roles_price_pointer_and_stale_inputs_refuse(self):
        body = ex.fixture();body['roles']['receivables'] = 'cash';self.assertEqual(schedules.report(body)['status'], 'invalid')
        body = ex.fixture();body['unit_cost_pointer'] = '/missing';self.assertEqual(schedules.report(body)['status'], 'invalid')
        body = ex.fixture();body['program_sha256'] = '0' * 64;self.assertEqual(schedules.report(body)['reason'], 'stale_input')

    def test_schedule_tampering_and_false_as_zero_fail_replay(self):
        body = ex.fixture();result = schedules.report(body)
        for kind in ['flag', 'movement', 'disclosure']:
            changed = deepcopy(result)
            if kind == 'flag':changed['notes_complete'] = 0
            elif kind == 'movement':changed['schedules']['inventory']['movements'].pop()
            else:changed['unresolved'] = []
            self.assertFalse(schedules.verify(body, changed))

    def test_dependency_pin_refuses(self):
        with patch.dict(schedules.PINS, {'declared_operating_methods_v1.py': '0' * 64}):
            self.assertEqual(schedules.report(ex.fixture())['status'], 'invalid')

    def test_zero_activity_remains_traceable(self):
        body = ex.fixture();p = body['program'];p['commands'] = [p['commands'][0], p['commands'][-1]]
        p['commands'][0]['event']['inputs']['units']['value']['value'] = '0/1';refreshed(body)
        result = schedules.report(body);self.assertEqual(result['status'], 'reported')
        self.assertEqual(result['schedules']['inventory']['movements'][0]['change'], '0/1')
        self.assertEqual(result['schedules']['inventory']['closing'], '20/1')

    def test_unrelated_noncash_method_retains_explanatory_bridge_residual(self):
        body = ex.fixture();p = body['program']
        entry = deepcopy(p['registry']['entries']['payroll_accrue'])
        entry['method']['account_map'].update(payroll='depreciation', payroll_payable='accum_depreciation')
        entry['account_classes']['payroll_payable'] = 'asset'
        entry['method_sha256'] = ex.program.digest(entry['method'])
        p['registry']['entries']['noncash'] = entry
        event = deepcopy(p['commands'][4]);event['method_key'] = 'noncash'
        event['event'].update(id='noncash.1', date='2027-01-08');event['event']['inputs']['amount']['value']['value'] = '3/1'
        p['commands'].insert(-1, event);refreshed(body)
        self.assertEqual(body['result']['status'], 'complete_provisional')
        result = schedules.report(body);self.assertEqual(result['status'], 'reported')
        self.assertEqual(result['cash_diagnostic']['unexplained_by_four_account_bridge'], '3/1')
        self.assertEqual(result['cash_diagnostic']['direct_operating_cash'], '7/1')
        self.assertEqual(result['cash_diagnostic']['profit'], '12/1')
        self.assertEqual(result['out_of_scope_events'][0]['event_id'], 'noncash.1')
        self.assertFalse(result['notes_complete'])

    def test_unclassified_unit_price_change_refuses_even_without_scoped_postings(self):
        body = ex.fixture();p = body['program']
        entry = deepcopy(p['registry']['entries']['payroll_accrue'])
        entry['method']['memory']['definition']['operations'] = [{'id': 'price_change', 'op': 'replace',
            'path': ['stock', 'unit_cost'], 'value': {'kind': 'literal', 'value': '6/1'}}]
        entry['method_sha256'] = ex.program.digest(entry['method']);p['registry']['entries']['price_change'] = entry
        event = deepcopy(p['commands'][4]);event['method_key'] = 'price_change'
        event['event'].update(id='price.1', date='2027-01-08');event['event']['inputs']['amount']['value']['value'] = '0/1'
        p['commands'].insert(-1, event);refreshed(body)
        self.assertEqual(body['result']['status'], 'complete_provisional')
        result = schedules.report(body);self.assertEqual(result['status'], 'unsupported')
        self.assertEqual(result['reason'], 'unit_cost_changed:price.1')

    def test_unclassified_offsetting_postings_cannot_hide_within_one_event(self):
        body = ex.fixture();p = body['program'];entry = deepcopy(p['registry']['entries']['collect'])
        typ = ex.program.engine.money_type(p['opening'])
        for identity, value in [('unclassified_debit', '1/1'), ('unclassified_credit', '-1/1')]:
            entry['method']['monetary']['definition']['postings'].append({'id': identity, 'account': 'receivables',
                'expression': {'op': 'const', 'type': deepcopy(typ), 'value': value}, 'requires': []})
        entry['method_sha256'] = ex.program.digest(entry['method']);p['registry']['entries']['offset'] = entry
        event = deepcopy(p['commands'][2]);event['method_key'] = 'offset'
        event['event'].update(id='offset.1', date='2027-01-08');event['event']['inputs']['amount']['value']['value'] = '0/1'
        p['commands'] = [event, p['commands'][-1]]
        p['registry']['entries'] = {'offset': entry}
        refreshed(body)
        self.assertEqual(body['result']['status'], 'complete_provisional')
        self.assertEqual(body['result']['trace'][-2]['result']['transition']['journal']['receivables'], '0/1')
        result = schedules.report(body);self.assertEqual(result['status'], 'unsupported')
        self.assertEqual(result['reason'], 'unclassified_scoped_movement:offset.1')


if __name__ == '__main__':unittest.main()
