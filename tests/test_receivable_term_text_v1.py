from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import importlib.util
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import receivable_term_text_v1 as text

spec = importlib.util.spec_from_file_location('term_text_examples', ROOT /
    'data/accounting-master/receivable-term-authoring-20261025/examples.py')
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)


class ReceivableTermTextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retained = ex.retained()
        cls.body = ex.program(cls.retained['alpha'], 'alpha')
        cls.source, cls.imports = text.from_program(cls.body)

    def execute(self, body):
        source, imports = text.from_program(body)
        return text.execute_text(source, imports)

    def test_full_two_chart_correspondence_to_retained_requests_and_results(self):
        for chart, case in self.retained.items():
            result = ex.check(case, chart)
            self.assertEqual(result['result']['current'], case['final'])

    def test_exact_roundtrip_and_no_input_mutation(self):
        before = deepcopy(self.body)
        source, imports = text.from_program(self.body)
        old_imports = deepcopy(imports)
        compiled = text.compile_text(source, imports)
        self.assertEqual(compiled['program'], self.body)
        self.assertEqual(self.body, before)
        self.assertEqual(imports, old_imports)

    def test_quoted_unicode_and_profile_text_are_preserved(self):
        body = deepcopy(self.body)
        value = 'Premise "ReceivableTermText/1" / ~ 客戶'
        body['commands'][0]['event']['inputs']['premise']['value']['value'] = value
        source, imports = text.from_program(body)
        self.assertEqual(text.compile_text(source, imports)['program'], body)

    def test_control_characters_remain_refused_by_typed_contract(self):
        body = deepcopy(self.body)
        body['commands'][0]['event']['inputs']['premise']['value']['value'] = 'first\nsecond'
        with self.assertRaisesRegex(Exception, 'control:text'):
            text.from_program(body)

    def test_rehashed_import_cannot_relabel_historical_assessment(self):
        imports = deepcopy(self.imports)
        key = next(k for k, v in imports.items() if 'memory' in v and 'claims' in v['memory'])
        book = imports.pop(key)
        book['memory']['claims']['invoice/a~1']['assessments']['imported']['term_id'] = 'absent'
        new = text.core.digest(book)
        imports[new] = book
        result = text.compile_text(self.source.replace(key, new), imports)
        self.assertEqual(result['status'], 'invalid')

    def test_tampered_missing_extra_and_wrong_profile_imports_refuse(self):
        for mode in ['tamper', 'missing', 'extra', 'profile']:
            imports = deepcopy(self.imports)
            source = self.source
            key = next(k for k, v in imports.items() if v.get('profile') == text.CONFIG)
            if mode == 'tamper':
                imports[key]['migration']['premise'] = 'changed'
            elif mode == 'missing':
                del imports[key]
            elif mode == 'extra':
                imports['0' * 64] = {}
            else:
                config = imports.pop(key)
                config['profile'] = 'Unknown/1'
                new = text.core.digest(config)
                imports[new] = config
                source = source.replace(key, new)
            self.assertEqual(text.compile_text(source, imports)['status'], 'invalid', mode)

    def test_header_duplicate_inputs_trailing_text_and_carry_override_refuse(self):
        variants = [self.source.replace(text.PROFILE, 'Unknown/1', 1),
                    self.source.replace('end_event;', 'input "approved" known true because "duplicate";\nend_event;', 1),
                    self.source + 'extra;',
                    self.source.replace('end_carry;', 'memory "/collection_clock/cursor" preserve because "override";\nend_carry;', 1)]
        for source in variants:
            self.assertEqual(text.compile_text(source, self.imports)['status'], 'invalid')

    def test_wrong_typed_input_is_not_erased_by_rendering(self):
        body = deepcopy(self.body)
        body['commands'][0]['event']['inputs']['due']['type'] = text.core.BOOL
        with self.assertRaisesRegex(Exception, 'event_type:due'):
            text.from_program(body)

    def test_unknown_keeps_exact_successful_prefix(self):
        body = deepcopy(self.body)
        body['commands'][1]['event']['inputs']['approved']['value'] = {'status': 'unknown', 'reason': 'No selection'}
        result = self.execute(body)
        self.assertEqual(result['status'], 'stopped_provisional')
        self.assertEqual(result['successful_commands'], 1)
        self.assertEqual(result['current'], self.retained['alpha']['steps'][0]['result']['after'])
        self.assertEqual(result['stop']['status'], 'unresolved')

    def test_false_approval_preserves_initial_state(self):
        body = deepcopy(self.body)
        body['commands'][0]['event']['inputs']['approved']['value']['value'] = False
        result = self.execute(body)
        self.assertEqual(result['successful_commands'], 0)
        self.assertEqual(result['current'], body['state'])
        self.assertEqual(result['stop']['status'], 'unsupported')

    def test_stale_term_and_customer_refuse_without_mutation(self):
        for name, value in [('prior_term', 'absent'), ('customer', 'Other')]:
            body = deepcopy(self.body)
            body['commands'][0]['event']['inputs'][name]['value']['value'] = value
            result = self.execute(body)
            self.assertEqual(result['successful_commands'], 0)
            self.assertEqual(result['current'], body['state'])
            self.assertEqual(result['stop']['status'], 'invalid')

    def test_duplicate_identity_stops_after_first_success(self):
        body = deepcopy(self.body)
        body['commands'][1]['event']['id'] = body['commands'][0]['event']['id']
        result = self.execute(body)
        self.assertEqual(result['successful_commands'], 1)
        self.assertEqual(result['stop']['reason'], 'duplicate_command')

    def test_carry_cannot_invent_a_later_closing_date(self):
        body = deepcopy(self.body)
        body['commands'][7]['cutoff'] = '2027-12-30'
        result = self.execute(body)
        self.assertEqual(result['successful_commands'], 7)
        self.assertEqual(result['stop']['reason'], 'carry_cutoff_must_match_state')
        self.assertEqual(result['current'], self.retained['alpha']['carry_before'])

    def test_unsupported_operation_and_report_are_explicitly_refused(self):
        source = self.source.replace('method "amend"', 'method "sale"', 1)
        self.assertEqual(text.compile_text(source, self.imports)['status'], 'invalid')
        lines = self.source.splitlines()
        report = '\n'.join(lines[:5] + ['report "r" at "2027-02-28";', 'end_report;', 'end_program;']) + '\n'
        result = text.compile_text(report, self.imports)
        self.assertEqual(result['reason'], 'unsupported_term_command')

    def test_missing_extra_inputs_and_bad_scalar_refuse(self):
        variants = [self.source.replace('input "approved" known true', 'input "unregistered" known true', 1),
                    self.source.replace('known "2027-04-30"', 'known "not-a-date"', 1)]
        for source in variants:
            self.assertEqual(text.compile_text(source, self.imports)['status'], 'invalid')

    def test_dependency_and_recursive_import_bounds(self):
        with patch.dict(text.PINS, {'receivable_term_history_v1.py': '0' * 64}):
            self.assertEqual(text.compile_text(self.source, self.imports)['status'], 'invalid')
        imports = deepcopy(self.imports)
        value = next(iter(imports.values()))
        value['cycle'] = value
        self.assertEqual(text.compile_text(self.source, imports)['status'], 'invalid')

    def test_replay_rejects_altered_history_or_flags(self):
        body = deepcopy(self.body)
        body['commands'] = body['commands'][:1]
        result = self.execute(body)
        self.assertTrue(text.verify(body, result))
        for key, value in [('current', {}), ('term_history_complete', True)]:
            altered = deepcopy(result)
            altered[key] = value
            self.assertFalse(text.verify(body, altered))


if __name__ == '__main__':
    unittest.main()
