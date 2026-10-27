from copy import deepcopy
from pathlib import Path
import importlib.util
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / 'scripts'))
import declared_receivable_text_v1 as text
spec = importlib.util.spec_from_file_location('receivable_text_examples', ROOT /
    'data/accounting-master/declared-collection-state-growth-20261025/examples.py')
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)


class ReceivableTextTests(unittest.TestCase):
    def test_two_charts_roundtrip_and_exact_execution(self):
        for owner in ['alpha', 'beta']:
            body, _, _ = ex.lifecycle_fixture(owner); source, imports = text.from_program(body)
            compiled = text.compile_text(source, imports)
            self.assertEqual(compiled['status'], 'compiled', compiled)
            self.assertEqual(compiled['program'], body)
            self.assertEqual(text.execute_text(source, imports), text.lifecycle.run(body))

    def test_customer_with_quotes_slashes_and_profile_name_is_preserved(self):
        body, _, _ = ex.lifecycle_fixture(); body['commands'] = body['commands'][:1]
        value = 'Client "DeclaredCompanyText/2" / ~'
        body['commands'][0]['event']['inputs']['customer']['value']['value'] = value
        source, imports = text.from_program(body); compiled = text.compile_text(source, imports)
        self.assertEqual(compiled['program'], body)

    def test_tampered_missing_extra_and_wrong_config_imports_refuse(self):
        body, _, _ = ex.lifecycle_fixture(); source, imports = text.from_program(body)
        for mutation in ['tamper', 'missing', 'extra']:
            changed = deepcopy(imports)
            if mutation == 'tamper': next(v for v in changed.values() if v.get('profile') == text.CONFIG)['policy']['carry'] = 'reset'
            elif mutation == 'missing': changed.pop(next(iter(changed)))
            else: changed['0' * 64] = {}
            self.assertEqual(text.compile_text(source, changed)['status'], 'invalid')

    def test_wrong_header_duplicate_input_and_carry_override_refuse(self):
        body, _, _ = ex.lifecycle_fixture(); source, imports = text.from_program(body)
        variants = [source.replace(text.PROFILE, 'Unknown/1', 1),
            source.replace('end_event;', 'input "approved" known true because "duplicate";\nend_event;', 1),
            source.replace('end_carry;', 'memory "/collection_clock/cursor" preserve because "override";\nend_carry;', 1)]
        for changed in variants: self.assertEqual(text.compile_text(changed, imports)['status'], 'invalid')

    def test_unknown_preserves_matching_prefix(self):
        body, _, _ = ex.lifecycle_fixture()
        body['commands'][4]['event']['inputs']['approved']['value'] = {'status': 'unknown', 'reason': 'missing choice'}
        source, imports = text.from_program(body); result = text.execute_text(source, imports)
        self.assertEqual(result, text.lifecycle.run(body)); self.assertEqual(result['successful_commands'], 4)


if __name__ == '__main__': unittest.main()
