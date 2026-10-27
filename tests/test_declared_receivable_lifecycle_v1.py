from copy import deepcopy
from pathlib import Path
import importlib.util
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / 'scripts'))
import declared_receivable_lifecycle_v1 as life
spec = importlib.util.spec_from_file_location('receivable_lifecycle_examples', ROOT /
    'data/accounting-master/declared-collection-state-growth-20261025/examples.py')
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)


class ReceivableLifecycleTests(unittest.TestCase):
    def run_checked(self, body):
        before = deepcopy(body); result = life.run(body)
        self.assertEqual(body, before)
        for flag in life.FLAGS: self.assertIs(result[flag], False)
        return result

    def test_two_charts_exact_lifecycle_reports_and_carry(self):
        for owner in ['alpha', 'beta']:
            body, mapping, _ = ex.lifecycle_fixture(owner); result = self.run_checked(body)
            self.assertEqual(result['status'], 'complete_provisional', result.get('stop', result.get('reason')))
            annual = next(r['result'] for r in result['reports'] if r['id'] == 'annual')
            self.assertEqual(annual['balance_sheet']['total_assets'], '140/1')
            self.assertEqual(annual['income']['profit'], '20/1')
            self.assertEqual(annual['cash_flows']['activities']['operating']['net'], '10/1')
            self.assertEqual(result['current']['balances'][mapping['cash']], '130/1')
            self.assertEqual(result['current']['balances'][mapping['receivables']], '0/1')
            self.assertEqual(result['current']['balances'][mapping['retained']], '-20/1')
            self.assertEqual(result['reports'][-1]['result']['cash_flows']['activities']['operating']['net'], '20/1')
            observations = {r['command'].get('event', {}).get('id'): r for r in result['trace']}
            self.assertEqual(observations['assess.jan']['observation']['claims'][0]['overdue'], '0/1')
            self.assertEqual(observations['assess.feb']['observation']['claims'][0]['overdue'], '20/1')
            for identity in ['assess.jan', 'assess.feb', 'assess.year', 'assess.next']:
                out = observations[identity]['result']; self.assertEqual(set(out['journal'].values()), {'0/1'})
                self.assertEqual(out['flows'], [])
            boundary = result['trace'][7]['result']
            self.assertEqual(boundary['next_opening']['memory'], boundary['closed_book']['memory'])
            self.assertEqual(result['trace'][8]['observation']['claims'][0]['overdue'], '20/1')
            self.assertEqual(result['trace'][8]['observation']['claims'][0]['status'], 'historical')
            self.assertTrue(life.verify(body, result))

    def test_new_claim_after_assessment_has_no_invented_snapshot(self):
        body, _, _ = ex.lifecycle_fixture(); second = deepcopy(body['commands'][0])
        second['event'].update(id='sale.2', date='2027-02-02')
        second['event']['inputs']['claim_id']['value']['value'] = 'new'
        second['event']['inputs']['due']['value']['value'] = '2027-03-01'
        body['commands'] = body['commands'][:4] + [second]
        result = self.run_checked(body); self.assertEqual(result['status'], 'complete_provisional', result.get('stop'))
        new = result['observation']['claims'][1]
        self.assertIsNone(new['overdue']); self.assertIsNone(new['assessment_as_of'])
        self.assertEqual(new['status'], 'unassessed'); self.assertEqual(new['remaining'], '30/1')

    def test_duplicate_customer_overpayment_and_currency_refusals(self):
        for variant in ['duplicate', 'customer', 'amount', 'currency']:
            body, _, _ = ex.lifecycle_fixture(); command = body['commands'][1]
            if variant == 'duplicate':
                command = deepcopy(body['commands'][0]); command['event']['id'] = 'sale.2'
                body['commands'][1] = command
            elif variant == 'customer': command['event']['inputs']['customer']['value']['value'] = 'Customer B'
            elif variant == 'amount': command['event']['inputs']['amount']['value']['value'] = '31/1'
            else: command['event']['inputs']['amount']['type']['dimensions'] = {'currency:EUR': 1}
            result = self.run_checked(body); self.assertEqual(result['status'], 'stopped_provisional')
            self.assertEqual(result['successful_commands'], 1)
            self.assertEqual(result['current'], result['trace'][0]['result']['after'])

    def test_unknown_and_unsupported_keep_reports_and_exact_prefix(self):
        for value, status in [({'status': 'unknown', 'reason': 'No selection'}, 'unresolved'),
                              ({'status': 'known', 'value': False}, 'unsupported')]:
            body, _, _ = ex.lifecycle_fixture(); body['commands'][4]['event']['inputs']['approved']['value'] = value
            result = self.run_checked(body); self.assertEqual(result['stop']['status'], status)
            self.assertEqual(result['successful_commands'], 4); self.assertEqual(len(result['reports']), 1)

    def test_sealed_assessment_day_and_noncontiguous_window_refuse(self):
        for variant in ['sale', 'collect', 'window']:
            body, _, _ = ex.lifecycle_fixture()
            if variant == 'window': body['commands'][4]['event']['inputs']['start']['value']['value'] = '2027-02-02'
            else:
                command = deepcopy(body['commands'][0 if variant == 'sale' else 1]); command['event'].update(id='late', date='2027-01-31')
                body['commands'] = body['commands'][:4] + [command]
            result = self.run_checked(body); self.assertEqual(result['successful_commands'], 4)
            self.assertEqual(result['stop']['status'], 'invalid')

    def test_due_date_and_orphan_opening_receivable_refuse(self):
        body, mapping, _ = ex.lifecycle_fixture(); body['commands'][0]['event']['inputs']['due']['value']['value'] = '2027-01-01'
        result = self.run_checked(body); self.assertEqual(result['successful_commands'], 0)
        body, mapping, _ = ex.lifecycle_fixture(); body['opening']['balances'][mapping['cash']] = '90/1'
        body['opening']['balances'][mapping['receivables']] = '10/1'
        result = self.run_checked(body); self.assertEqual(result['status'], 'invalid')
        self.assertEqual(result['reason'], 'claim_receivable_sum')

    def test_no_assessment_stays_unknown_and_replay_tamper_refuses(self):
        body, _, _ = ex.lifecycle_fixture(); body['commands'] = body['commands'][:2] + [body['commands'][6]]
        result = self.run_checked(body); self.assertEqual(result['status'], 'complete_provisional')
        self.assertIsNone(result['observation']['claims'][0]['overdue'])
        changed = deepcopy(result); changed['current']['memory']['claims'].clear()
        self.assertFalse(life.verify(body, changed))

    def test_unknown_identity_extra_inputs_and_backdated_events_keep_prefix(self):
        for variant in ['identity', 'extra', 'date', 'negative']:
            body, _, _ = ex.lifecycle_fixture(); event = body['commands'][1]['event']
            if variant == 'identity': event['inputs']['claim_id']['value']['value'] = 'missing'
            elif variant == 'extra': event['inputs']['ignored'] = deepcopy(event['inputs']['customer'])
            elif variant == 'date': event['date'] = '2027-01-01'
            else: event['inputs']['amount']['value']['value'] = '-1/1'
            result = self.run_checked(body); self.assertEqual(result['successful_commands'], 1)
            self.assertEqual(result['stop']['status'], 'invalid')

    def test_capacity_refuses_second_sale_without_monetary_change(self):
        body, _, _ = ex.lifecycle_fixture()
        body['memory_definition']['root']['fields']['claims']['max_items'] = 1
        second = deepcopy(body['commands'][0]); second['event'].update(id='sale.2', date='2027-01-03')
        second['event']['inputs']['claim_id']['value']['value'] = 'second'
        body['commands'] = [body['commands'][0], second]
        result = self.run_checked(body); self.assertEqual(result['successful_commands'], 1)
        self.assertIn('capacity', result['stop']['reason'])
        self.assertEqual(result['current'], result['trace'][0]['result']['after'])

    def test_empty_assessment_and_same_due_day_have_exact_semantics(self):
        body, _, _ = ex.lifecycle_fixture(); body['commands'] = [body['commands'][2]]
        result = self.run_checked(body); self.assertEqual(result['status'], 'complete_provisional')
        self.assertEqual(result['observation']['claims'], [])
        self.assertEqual(result['current']['memory']['collection_clock']['cursor'], '2027-02-01')

    def test_carry_before_last_day_and_overridden_policies_refuse(self):
        for variant in ['date', 'policies']:
            body, _, _ = ex.lifecycle_fixture(); body['commands'] = body['commands'][:4] + [body['commands'][7]]
            if variant == 'date': body['commands'][4]['cutoff'] = '2027-06-30'
            else: body['commands'][4]['memory_policies'] = {}
            result = self.run_checked(body); self.assertEqual(result['successful_commands'], 4)
            self.assertEqual(result['stop']['status'], 'invalid')

    def test_frozen_dependency_changes_refuse(self):
        body, _, _ = ex.lifecycle_fixture()
        with patch.dict(life.PINS, {'declared_operating_methods_v1.py': '0' * 64}):
            result = self.run_checked(body); self.assertEqual(result['status'], 'invalid')

    def test_multiple_claims_and_receipts_do_not_cross_identities(self):
        body, _, _ = ex.lifecycle_fixture(); second = deepcopy(body['commands'][0])
        second['event'].update(id='sale.2', date='2027-01-03')
        second['event']['inputs']['claim_id']['value']['value'] = 'second'
        second['event']['inputs']['customer']['value']['value'] = 'Customer B'
        body['commands'] = [body['commands'][0], second, body['commands'][1], body['commands'][2]]
        result = self.run_checked(body); self.assertEqual(result['status'], 'complete_provisional', result.get('stop'))
        self.assertEqual([r['remaining'] for r in result['observation']['claims']], ['20/1', '30/1'])
        self.assertEqual([r['overdue'] for r in result['observation']['claims']], ['0/1', '0/1'])


if __name__ == '__main__': unittest.main()
