from copy import deepcopy
from pathlib import Path
import importlib.util
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import declared_company_text_v1 as text
spec = importlib.util.spec_from_file_location('text_program_examples', ROOT / 'data/accounting-master/declared-company-program-20261025/examples.py')
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)


class DeclaredCompanyTextTests(unittest.TestCase):
    def fixture(self, owner='alpha'):
        body = ex.fixture(owner); author, imports = text.from_program(body)
        return body, author, imports, text.render(author)

    def test_two_company_roundtrips_and_complete_execution(self):
        for owner in ['alpha', 'beta']:
            body, author, imports, source = self.fixture(owner)
            compiled = text.compile_text(source, imports)
            self.assertEqual(compiled['program'], body)
            self.assertEqual(text.lower(source), author)
            self.assertEqual(text.render(text.lower(source)), source)
            self.assertEqual(text.execute_text(source, imports), ex.program.run(body))
            self.assertEqual(text.execute_program(author, imports), ex.program.run(body))
            self.assertEqual([r['role'] for r in compiled['dependencies']], list(text.IMPORTS))
            self.assertFalse(compiled['executed'])
            for key in text.runner.FLAGS:self.assertIs(compiled[key], False)

    def test_unknown_reason_and_stopped_prefix_survive(self):
        body = ex.fixture(); body['commands'][2]['event']['inputs']['approved']['value'] = {'status': 'unknown', 'reason': 'Approval evidence 未知'}
        author, imports = text.from_program(body); source = text.render(author)
        result = text.execute_text(source, imports)
        self.assertEqual(result, ex.program.run(body))
        self.assertEqual(len(result['trace']), 2)
        self.assertEqual(result['stop']['status'], 'unresolved')
        self.assertIn('Approval evidence 未知', source)

    def test_source_spans_and_hash_cover_actual_text(self):
        body, author, imports, source = self.fixture()
        source = '\n\n' + source.replace('\n', '\r\n')
        compiled = text.compile_text(source.encode(), imports); spans = compiled['source_spans']
        self.assertEqual(compiled['program'], body)
        self.assertEqual(spans['program']['line'], 3)
        self.assertEqual(compiled['source_text_sha256'], text.sha256(source.encode()).hexdigest())
        for span in spans['commands']:
            self.assertTrue(source[span['offset']:].startswith(span['kind'] + ' '))
            self.assertGreater(span['end_line'], span['line'])
            for field in span['fields']:self.assertTrue(source[field['offset']:].startswith(field['declaration'] + ' '))

    def test_missing_altered_extra_and_swapped_imports(self):
        body, author, imports, source = self.fixture()
        for kind in text.IMPORTS:
            key = author['imports'][kind]; missing = deepcopy(imports); del missing[key]
            with self.assertRaises(text.Invalid):text.compile_text(source, missing)
            bad = deepcopy(imports); bad[key]['unexpected'] = True
            with self.assertRaises(text.Invalid) as caught:text.compile_text(source, bad)
            self.assertEqual(caught.exception.stage, 'import:' + kind)
            self.assertIsNotNone(caught.exception.line)
        extra = deepcopy(imports); extra['0' * 64] = {}
        with self.assertRaises(text.Invalid):text.compile_text(source, extra)
        bad = deepcopy(author); bad['imports']['opening'], bad['imports']['mapping'] = bad['imports']['mapping'], bad['imports']['opening']
        with self.assertRaises(text.Invalid):text.compile_program(bad, imports)

    def test_duplicate_and_missing_import_declarations(self):
        body, author, imports, source = self.fixture(); line = source.splitlines()[1]
        for bad in [source.replace(line, line + '\n' + line), source.replace(line + '\n', ''), source.replace('import_schemas', 'import_opening')]:
            with self.assertRaises(text.Invalid):text.lower(bad)

    def test_duplicate_input_policy_singleton_and_unknown_fields(self):
        body, author, imports, source = self.fixture()
        for prefix in ['input ', 'memory ', 'retained_account ', 'next_end_exclusive ']:
            line = next(s for s in source.splitlines() if s.startswith(prefix))
            with self.assertRaises(text.Invalid):text.lower(source.replace(line, line + '\n' + line, 1))
        for bad in [source.replace('end_report;', 'unexpected "x";\nend_report;', 1), source + 'report "late" at "2029-01-01";\n']:
            with self.assertRaises(text.Invalid):text.lower(bad)

    def test_json_objects_arrays_numbers_null_and_injection_are_not_scalars(self):
        body, author, imports, source = self.fixture()
        for replacement in ['{}', '[]', '15', '15.0', 'null', 'NaN', '__import__("os")']:
            bad = source.replace('known "40/1"', 'known ' + replacement, 1)
            with self.assertRaises(text.Invalid):text.lower(bad)

    def test_malformed_rational_date_and_boolean_are_not_coerced(self):
        body, author, imports, source = self.fixture()
        for bad in [source.replace('"2027-02-01"', '"2027-02-30"', 1), source.replace('known "40/1"', 'known "40/0"', 1), source.replace('known true', 'known "true"', 1)]:
            with self.assertRaises(text.Invalid):text.compile_text(bad, imports)

    def test_missing_policies_preserve_runtime_carry_refusal(self):
        body = ex.fixture(); del body['commands'][4]['memory_policies']['/loan/paid']
        author, imports = text.from_program(body); result = text.execute_text(text.render(author), imports)
        self.assertEqual(result, ex.program.run(body))
        self.assertEqual(len(result['trace']), 4)
        self.assertEqual(result['stop']['result']['reason'], 'complete_memory_policies')

    def test_reset_types_are_resolved_exactly_and_wrong_types_cannot_be_erased(self):
        body = ex.fixture(); leaf = '/loan/paid'; typ = body['opening']['memory_types'][leaf]
        body['commands'][4]['memory_policies'][leaf] = {'kind': 'reset', 'type': deepcopy(typ), 'value': '0/1', 'provenance': 'Explicit period counter'}
        body['commands'][4]['memory_policies']['/loan/last_date'] = {'kind': 'next_period_start', 'provenance': 'Explicit cursor policy'}
        author, imports = text.from_program(body); source = text.render(author)
        self.assertEqual(text.compile_text(source, imports)['program'], body)
        self.assertEqual(text.execute_text(source, imports), ex.program.run(body))
        bad = deepcopy(body); bad['commands'][4]['memory_policies'][leaf]['type']['dimensions'] = {'goods:unit': 1}
        with self.assertRaisesRegex(text.Invalid, 'reset_type_correspondence'):text.from_program(bad)
        with self.assertRaises(text.Invalid):text.compile_text(source.replace('reset "0/1"', 'reset "tomorrow"', 1), imports)

    def test_direct_equity_and_note_fields_roundtrip_without_omission(self):
        body = ex.fixture(); body['commands'][1]['equity_movements'] = [{'id': 'supplied', 'event_id': 'sale.2027', 'date': '2027-02-01',
            'account': 'capital.alpha', 'amount': '1/1', 'description': 'Supplied explanation remains subject to reconciliation'}]
        body['commands'][1]['notes'].extend([{'id': 'unsupported', 'label': 'Unimplemented schedule', 'status': 'unsupported', 'reason': 'Method absent'},
            {'id': 'uncertain', 'label': 'Uncertain facts', 'status': 'unresolved', 'reason': 'Two alternatives'}])
        author, imports = text.from_program(body); source = text.render(author)
        self.assertEqual(text.compile_text(source, imports)['program'], body)
        self.assertEqual(text.execute_text(source, imports), ex.program.run(body))

    def test_reordered_and_duplicate_commands_keep_engine_refusals(self):
        for duplicate in [False, True]:
            body = ex.fixture()
            if duplicate:body['commands'][2]['event']['id'] = 'sale.2027'
            else:body['commands'][0], body['commands'][2] = body['commands'][2], body['commands'][0]
            author, imports = text.from_program(body)
            self.assertEqual(text.execute_text(text.render(author), imports), ex.program.run(body))
            self.assertEqual(ex.program.run(body)['status'], 'stopped_provisional')

    def test_program_record_extras_are_rejected_instead_of_dropped(self):
        body, author, imports, source = self.fixture()
        for field in ['command', 'input', 'policy', 'note']:
            bad = deepcopy(author)
            if field == 'command':bad['commands'][0]['expected_state_sha256'] = '0' * 64
            elif field == 'input':bad['commands'][0]['event']['inputs']['proceeds']['surprise'] = True
            elif field == 'policy':bad['commands'][4]['memory_policies']['/loan/paid']['surprise'] = True
            else:bad['commands'][1]['notes'][0]['surprise'] = True
            with self.assertRaises(text.Invalid):text.compile_program(bad, imports)

    def test_parse_errors_retain_line_and_character_offset(self):
        body, author, imports, source = self.fixture()
        bad = source.replace('known "40/1"', 'known @', 1)
        at = bad.index('@')
        with self.assertRaises(text.Invalid) as caught:text.lower(bad)
        self.assertEqual(caught.exception.offset, at)
        self.assertEqual(caught.exception.line, bad[:at].count('\n') + 1)
        with self.assertRaises(text.Invalid):text.lower(source.replace('end_event;', 'end_report;', 1))
        with self.assertRaises(text.Invalid):text.lower(source.removesuffix('end_program;\n'))

    def test_missing_end_required_carry_field_and_semicolon(self):
        body, author, imports, source = self.fixture()
        line = next(s for s in source.splitlines() if s.startswith('retained_account'))
        for bad in [source.replace(line + '\n', '', 1), source.replace('end_carry;', '', 1), source.replace(';', '', 1)]:
            with self.assertRaises(text.Invalid):text.lower(bad)

    def test_unknown_method_input_and_reset_leaf_are_localized(self):
        body, author, imports, source = self.fixture()
        for bad in [source.replace('method "sell"', 'method "absent"', 1), source.replace('input "proceeds"', 'input "extra"', 1),
                    source.replace('memory "/loan/paid" preserve', 'memory "/missing" reset "0/1"', 1)]:
            with self.assertRaises(text.Invalid) as caught:text.compile_text(bad, imports)
            self.assertTrue(caught.exception.stage.startswith('command:'))
            self.assertIsNotNone(caught.exception.offset)

    def test_utf8_and_string_boundaries(self):
        body, author, imports, source = self.fixture()
        for bad in [b'\xff', '\ufeff' + source, source.replace('\n', '\r'), source.replace('two-period-alpha', 'bad\u2028name'),
                    source.replace('"40/1"', '"\\ud800"', 1)]:
            with self.assertRaises((text.Invalid, ValueError)):text.lower(bad)

    def test_command_bound_and_dependency_pin(self):
        body, author, imports, source = self.fixture()
        report = author['commands'][1]; author['commands'] = [{**deepcopy(report), 'id': str(i)} for i in range(64)]
        self.assertEqual(len(text.lower(text.render(author))['commands']), 64)
        author['commands'].append(deepcopy(report))
        with self.assertRaises(text.Invalid):text.render(author)
        with patch.dict(text.PINS, {'declared_company_program_v1.py': '0' * 64}):
            with self.assertRaises(text.Invalid):text.compile_text(source, imports)

    def test_independently_authored_source_matches_typed_program(self):
        spec = importlib.util.spec_from_file_location('independent_text_examples', ROOT / 'data/accounting-master/declared-company-text-20261025/examples.py')
        examples = importlib.util.module_from_spec(spec); spec.loader.exec_module(examples)
        body, imports, source = examples.independent_source()
        self.assertEqual(text.compile_text(source, imports)['program'], body)
        self.assertEqual(text.execute_text(source, imports), ex.program.run(body))


if __name__ == '__main__':unittest.main()
