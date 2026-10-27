from copy import deepcopy
from pathlib import Path
import importlib.util
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / 'scripts'))
import declared_collection_clock_v1 as clock
spec = importlib.util.spec_from_file_location('collection_clock_examples', ROOT /
    'data/accounting-master/declared-dynamic-collection-clock-20261025/examples.py')
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)


class CollectionClockTests(unittest.TestCase):
    def test_two_charts_native_and_text(self):
        result = ex.compare()
        self.assertEqual(len(result['cases']), 4)
        self.assertEqual([r['name'] for r in result['checks'] if not r['passed']], [])

    def test_due_day_and_missing_assessment(self):
        q, _, _ = ex.fixture(); q['program']['commands'] = q['program']['commands'][:3]
        out = clock.run(q); self.assertEqual(out['observation']['status'], 'current')
        self.assertEqual(out['observation']['claims'][0]['assessed_overdue'], '0/1')
        q['program']['commands'] = [q['program']['commands'][0], {'kind': 'report', 'id': 'late',
            'cutoff': '2027-12-31', 'equity_movements': [], 'notes': []}]
        out = clock.run(q); self.assertEqual(out['status'], 'complete_provisional')
        self.assertEqual(out['observation']['status'], 'unassessed')
        self.assertIsNone(out['observation']['claims'][0]['assessed_overdue'])

    def test_stale_assessment_does_not_update_on_receipt_or_report(self):
        q, _, _ = ex.fixture(); q['program']['commands'] = q['program']['commands'][:4]
        out = clock.run(q); self.assertEqual(out['observation']['status'], 'historical')
        self.assertEqual(out['observation']['claims'][1]['remaining'], '30/1')
        self.assertEqual(out['observation']['claims'][1]['assessed_remaining'], '40/1')
        self.assertEqual(out['observation']['next_window_start'], '2027-02-01')

    def test_duplicate_backdated_and_post_period_events_preserve_prefix(self):
        for key, value in [('id', 'receipt.a'), ('date', '2027-01-14'), ('date', '2028-01-01')]:
            q, _, _ = ex.fixture(); p = q['program']; p['commands'] = p['commands'][:1] + [deepcopy(p['commands'][0])]
            p['commands'][1]['event'].update(id='second', **{key: value}) if key != 'id' else p['commands'][1]['event'].update(id=value)
            out = clock.run(q)
            self.assertEqual(out['status'], 'stopped_provisional', out.get('reason'))
            self.assertEqual(out['successful_commands'], 1)

    def test_amount_unknown_false_approval_and_overpayment(self):
        for field, value, status in [('amount', {'status': 'unknown', 'reason': 'missing'}, 'unresolved'),
                ('approved', {'status': 'known', 'value': False}, 'unsupported'),
                ('amount', {'status': 'known', 'value': '61/1'}, 'invalid')]:
            q, _, _ = ex.fixture(); q['program']['commands'][0]['event']['inputs'][field]['value'] = value
            out = clock.run(q); self.assertEqual(out['stop']['status'], status)
            self.assertEqual(out['successful_commands'], 0); self.assertEqual(out['current'], q['program']['opening'])

    def test_windows_duplicate_overlap_gap_and_reverse_refuse(self):
        for value in ['2027-01-01', '2027-01-31', '2027-02-02', '2028-01-01']:
            q, _, _ = ex.fixture(); q['windows'][1]['start'] = value
            self.assertEqual(clock.run(q)['status'], 'invalid')

    def test_wrong_assessment_day_and_skipped_window_refuse(self):
        q, _, _ = ex.fixture(); p = q['program']; p['commands'][1]['event']['date'] = '2027-01-30'
        out = clock.run(q); self.assertEqual(out['successful_commands'], 1); self.assertEqual(out['stop']['status'], 'invalid')
        q, _, _ = ex.fixture(); p = q['program']; p['commands'] = [p['commands'][0], p['commands'][4]]
        out = clock.run(q); self.assertEqual(out['successful_commands'], 1); self.assertEqual(out['stop']['status'], 'invalid')

    def test_same_day_collection_after_assessment_is_refused(self):
        q, _, _ = ex.fixture(); p = q['program']; p['commands'] = p['commands'][:2] + [ex.event(p, 'collect.1', 'late', '2027-01-31', '1/1')]
        out = clock.run(q); self.assertEqual(out['successful_commands'], 2)
        self.assertEqual(out['stop']['status'], 'invalid')

    def test_report_seals_cutoff_against_earlier_events(self):
        q, _, _ = ex.fixture(); p = q['program']; p['commands'] = p['commands'][:3] + [ex.event(p, 'collect.1', 'late', '2027-01-30', '1/1')]
        out = clock.run(q); self.assertEqual(out['successful_commands'], 3); self.assertEqual(len(out['reports']), 1)

    def test_carry_resets_cannot_erase_unpaid_claims_or_assessments(self):
        for pointer in ['/collection/cursor', '/collection/a/remaining', '/collection/assessed']:
            q, _, _ = ex.fixture(carry=True); p = q['program']; policy = p['commands'][7]['memory_policies'][pointer]
            value = clock.leaf(p['opening'], pointer)
            policy.update(kind='reset', type=deepcopy(p['opening']['memory_types'][pointer]), value=value)
            out = clock.run(q); self.assertEqual(out['successful_commands'], 7, out.get('reason'))
            self.assertEqual(out['stop']['reason'], 'collection_carry_must_preserve')

    def test_unclassified_gross_offset_and_equal_value_memory_write_refuse(self):
        for variant in ['gross', 'memory']:
            q, _, _ = ex.fixture(); p = q['program']
            entry = deepcopy(p['registry']['entries']['collect.1' if variant == 'gross' else 'assess.1'])
            if variant == 'gross':
                for name, value in [('offset.a', '1/1'), ('offset.b', '-1/1')]:
                    entry['method']['monetary']['definition']['postings'].append({'id': name, 'account': 'receivables',
                        'expression': clock.constant(clock.engine.money_type(p['opening']), value), 'requires': []})
            else:
                entry['method']['memory']['definition']['operations'].append({'id': 'hidden', 'op': 'replace',
                    'path': ['collection', 'a', 'due'], 'value': {'kind': 'literal', 'value': '2027-01-31'}})
            entry['method_sha256'] = clock.core.digest(entry['method']); p['registry']['entries']['foreign'] = entry
            p['commands'] = [ex.event(p, 'foreign', 'foreign', '2027-01-01' if variant == 'gross' else '2027-01-31',
                                     '0/1' if variant == 'gross' else None)]
            out = clock.run(q); self.assertEqual(out['successful_commands'], 0, out.get('reason'))
            self.assertEqual(out['stop']['reason'], 'unclassified_receivable_posting' if variant == 'gross'
                             else 'unclassified_collection_memory_write')

    def test_aliases_and_tamper_replay(self):
        q, _, _ = ex.fixture(); p = q['program']; p['registry']['entries']['alias'] = p['registry']['entries'].pop('collect.1')
        p['commands'][0]['method_key'] = 'alias'; out = clock.run(q)
        self.assertEqual(out['status'], 'complete_provisional')
        for key, value in [('source_admission', 0), ('observation', {}), ('current', p['opening'])]:
            changed = deepcopy(out); changed[key] = value; self.assertFalse(clock.verify(q, changed))

    def test_claim_sum_pointers_due_dates_and_pins(self):
        q, _, _ = ex.fixture(); q['claims'][1]['balance_pointer'] = q['claims'][0]['balance_pointer']
        self.assertEqual(clock.run(q)['status'], 'invalid')
        q, _, _ = ex.fixture(); q['claims'][0]['due_date'] = '2027-02-01'
        self.assertEqual(clock.run(q)['reason'], 'declared_due_date_mismatch')
        with patch.dict(clock.PINS, {'declared_company_program_v2.py': '0' * 64}):
            self.assertEqual(clock.run(q)['status'], 'invalid')

    def test_leap_day_assessment_after_due_date(self):
        q, _, _ = ex.fixture(); p = q['program']; book = p['opening']
        book['period'] = {'start': '2028-01-01', 'end_exclusive': '2029-01-01'}; book['date'] = '2028-01-01'
        book['memory']['collection']['cursor'] = '2028-01-01'
        for claim in q['claims']:
            claim['due_date'] = '2028-02-28'
            key = claim['id'].rsplit('.', 1)[1]; book['memory']['collection'][key]['due'] = claim['due_date']
        q['windows'] = [{'start': '2028-01-01', 'end_exclusive': '2028-03-01'}]
        p['registry'] = clock.build(book, p['schemas'], q['roles'], q['claims'], q['windows'], q['policy'])
        for e in p['registry']['entries'].values(): p['schemas'].update(e['schemas'])
        p['commands'] = [ex.event(p, 'assess.1', 'leap', '2028-02-29')]
        out = clock.run(q); self.assertEqual(out['status'], 'complete_provisional', out.get('reason'))
        self.assertEqual([c['assessed_overdue'] for c in out['observation']['claims']], ['60/1', '40/1'])

    def test_duplicate_window_with_new_event_identity_refuses(self):
        q, _, _ = ex.fixture(); p = q['program']
        p['commands'] = [p['commands'][1], ex.event(p, 'assess.1', 'repeat', '2027-01-31')]
        out = clock.run(q); self.assertEqual(out['successful_commands'], 1)
        self.assertEqual(out['stop']['status'], 'invalid')

    def test_unknown_assessment_after_successful_report_retains_report(self):
        q, _, _ = ex.fixture(); p = q['program']; p['commands'][4]['event']['inputs']['approved']['value'] = {
            'status': 'unknown', 'reason': 'No assessment selection'}
        out = clock.run(q); self.assertEqual(out['successful_commands'], 4)
        self.assertEqual(out['stop']['status'], 'unresolved'); self.assertEqual(len(out['reports']), 1)
        self.assertEqual(out['observation']['assessment_as_of'], '2027-01-31')
        self.assertTrue(clock.verify(q, out))

    def test_missing_window_does_not_block_provisional_carry_or_create_assessment(self):
        q, _, _ = ex.fixture(carry=True); p = q['program']
        p['commands'] = [p['commands'][0], p['commands'][7], p['commands'][8], p['commands'][9]]
        out = clock.run(q); self.assertEqual(out['successful_commands'], 3)
        self.assertEqual(out['stop']['status'], 'invalid')
        self.assertEqual(out['observation']['status'], 'unassessed')
        self.assertEqual(out['observation']['next_window_start'], '2027-01-01')

    def test_foreign_write_after_report_returns_only_the_safe_prefix(self):
        q, _, _ = ex.fixture(); p = q['program']; entry = deepcopy(p['registry']['entries']['assess.2'])
        entry['method']['memory']['definition']['operations'].append({'id': 'due_mutation', 'op': 'replace',
            'path': ['collection', 'a', 'due'], 'value': {'kind': 'literal', 'value': '2027-01-31'}})
        entry['method_sha256'] = clock.core.digest(entry['method']); p['registry']['entries']['foreign'] = entry
        p['commands'] = p['commands'][:3] + [ex.event(p, 'foreign', 'foreign', '2027-02-28')]
        out = clock.run(q); self.assertEqual(out['successful_commands'], 3)
        self.assertEqual(out['stop']['reason'], 'unclassified_collection_memory_write')
        prefix = deepcopy(p); prefix['commands'] = prefix['commands'][:3]
        self.assertEqual(out['program_result'], clock.program.run(prefix))
        self.assertEqual(len(out['assessments']), 1); self.assertEqual(len(out['reports']), 1)

    def test_wrong_claim_allocation_with_same_aggregate_refuses(self):
        q, _, _ = ex.fixture(); p = q['program']; p['opening']['memory']['collection']['a']['remaining'] = '50/1'
        p['opening']['memory']['collection']['b']['remaining'] = '50/1'
        p['commands'] = [ex.event(p, 'collect.1', 'too_much', '2027-01-02', '60/1')]
        out = clock.run(q); self.assertEqual(out['successful_commands'], 0)
        self.assertEqual(out['stop']['status'], 'invalid')

    def test_declared_work_bounds_and_wrong_policy_refuse(self):
        for variant in ['claims', 'windows', 'policy']:
            q, _, _ = ex.fixture()
            if variant == 'claims': q['claims'] *= 5
            elif variant == 'windows': q['windows'] *= 5
            else: q['policy']['past_due'] = 'on_due_date'
            self.assertEqual(clock.run(q)['status'], 'invalid')

    def test_metadata_date_cannot_be_replaced_by_caller_input(self):
        q, _, _ = ex.fixture(); p = q['program']; entry = p['registry']['entries']['assess.1']
        entry['metadata_bindings'] = {}
        entry['event_inputs']['event_date'] = deepcopy(clock.DATE)
        command = deepcopy(p['commands'][1]); command['event']['date'] = '2027-01-02'
        command['event']['inputs']['event_date'] = {'type': deepcopy(clock.DATE),
            'value': {'status': 'known', 'value': '2027-01-31'}, 'provenance': 'Spoofed future observation'}
        p['commands'] = [command]
        out = clock.run(q)
        self.assertEqual(out['status'], 'invalid')
        self.assertIn('collection_call_binding', out['reason'])


if __name__ == '__main__': unittest.main()
