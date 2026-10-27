"""Exact authoring/exchange identity and adversarial parser checks."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import method_requirements_v1 as core
import method_requirement_text_v1 as front
spec = importlib.util.spec_from_file_location('requirement_author_examples',
    ROOT/'data/accounting-master/method-requirement-authoring-20261024/examples.py')
fixtures = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixtures)


class RequirementTextTests(unittest.TestCase):
    def setUp(self):
        self.examples = fixtures.examples()
        self.example = self.examples['legal_cash']
        self.text = front.render(self.example)

    def rejected(self, source):
        with self.assertRaises((ValueError,TypeError,RecursionError)):
            front.lower(source)

    def test_independent_expected_status_and_roundtrip(self):
        expected = {'operations.baseline':'requirements_satisfied',
                    'returns.baseline':'requirements_satisfied','legal_cash':'requirements_satisfied',
                    'reported_cash':'unresolved','insurance_cohort':'unresolved'}
        for name, example in self.examples.items():
            with self.subTest(name=name):
                before = deepcopy(example)
                text = front.render(example)
                lowered = front.lower(text)
                self.assertEqual(lowered,example)
                self.assertEqual(front.render(lowered),text)
                self.assertEqual(front.decode_exchange(core.canonical(example).decode()),example)
                self.assertEqual(front.assess_exchange(lowered),front.assess_exchange(example))
                result = front.assess_exchange(lowered)
                self.assertEqual(result['status'],expected[name])
                self.assertFalse(result['accounting_admission'])
                self.assertFalse(result['method_eligible'])
                self.assertEqual(before,example)

    def test_handwritten_text_matches_independent_definition(self):
        e = self.example
        text = '\n'.join([
            'requirements "MethodRequirements/1" "example.legal_cash" "1";',
            'input "amount" rational state {"entity":"SampleCo","book_role":"legal","unit":"USD","at":"2025-01-01"} "constructed-language-case:amount";',
            'input "review" boolean caller_finding {} "constructed-language-case:caller-finding";',
            'require "nonnegative" invalid unresolved ["amount"] [] (le (const rational {"entity":"SampleCo","book_role":"legal","unit":"USD","at":"2025-01-01"} "0/1") (ref "amount"));',
            'require "caller_scope" unsupported unresolved ["review"] ["separate-review-required"] (ref "review");',
            'capability "example.legal_cash";',
            'residual "Constructed grammar case only; no implemented accounting method.";',
            'residual "Legal state, authority, source admission and full method checks remain.";',
            'select "'+e['selected_digest']+'";',
            'bind "amount" known "100/1";',
            'bind "review" known true;',
            'available "example.legal_cash";',
            'end_requirements;'])
        self.assertEqual(front.lower(text),e)

    def test_quoted_delimiters_unicode_and_no_normalization(self):
        for name in ['a; (b) "quoted" \\ slash', 'Café', 'Café', 'x\u2028y']:
            e = deepcopy(self.example)
            e['definition']['method_id'] = name
            e['selected_digest'] = core.digest(e['definition'])
            self.assertEqual(front.lower(front.render(e)),e)
        a,b = deepcopy(self.example),deepcopy(self.example)
        a['definition']['method_id']='Café'
        b['definition']['method_id']='Café'
        self.assertNotEqual(core.digest(a['definition']),core.digest(b['definition']))
        self.rejected(self.text.replace('"example.legal_cash"','"line\\nname"',1))

    def test_declaration_integrity(self):
        lines = self.text.splitlines()
        for prefix in ['requirements ','input ','require ','select ','bind ','available ']:
            line = next(x for x in lines if x.startswith(prefix))
            self.rejected(self.text.replace(line,line+'\n'+line,1))
        for source in [self.text.replace('end_requirements;',''),
                       self.text+'available "extra";',
                       self.text.replace('select ', 'include ',1),
                       self.text.replace('requirements ', 'import ',1),
                       self.text.replace(';','',1),
                       self.text.replace('(ref "review")','(ref "review" "extra")'),
                       self.text.replace('(ref "review")','(eval "review")'),
                       self.text.replace('(ref "review")','(all)'),
                       self.text.replace('bind "review" known true;','bind "review" known 1;'),
                       self.text.replace('bind "review" known true;','bind "review" known "true";'),
                       self.text.replace('"100/1"','"200/2"'),
                       self.text.replace('"100/1"','NaN')]:
            self.rejected(source)

    def test_duplicate_json_keys_and_stale_identity(self):
        self.rejected(self.text.replace('"unit":"USD"','"unit":"USD","unit":"EUR"',1))
        self.rejected(self.text.replace(self.example['selected_digest'],'0'*64))
        raw = core.canonical(self.example).decode()
        for text in [raw.replace('"values":','"values":{},"values":',1),
                     raw.replace('"unit":"USD"','"unit":"USD","unit":"EUR"',1),
                     raw.replace('"100/1"','NaN'),raw+' {}']:
            with self.assertRaises(ValueError):
                front.decode_exchange(text)
        e = deepcopy(self.example)
        e['definition']['inputs']['amount']['role'] = 'reported_measurement'
        with self.assertRaises(ValueError):
            front.validate_exchange(e)

    def test_book_context_mismatch_remains_invalid(self):
        e = deepcopy(self.example)
        d = e['definition']
        d['inputs']['reported'] = deepcopy(d['inputs']['amount'])
        d['inputs']['reported']['type']['context']['book_role'] = 'consolidated'
        d['inputs']['reported']['role'] = 'reported_measurement'
        d['requirements'][0].update(predicate={'op':'eq','left':{'op':'ref','id':'amount'},
                                             'right':{'op':'ref','id':'reported'}},
                                    requires=['amount','reported'])
        e['values']['reported']={'status':'known','value':'100/1'}
        e['selected_digest']=core.digest(d)
        with self.assertRaises(ValueError):
            front.validate_exchange(e)

    def test_known_unknown_text_and_missing_binding(self):
        e = deepcopy(self.example)
        d = e['definition']
        d['inputs']['amount']['type']={'kind':'text','context':{}}
        d['requirements'][0]['predicate']={'op':'eq','left':{'op':'ref','id':'amount'},
            'right':{'op':'const','type':{'kind':'text','context':{}},'value':'unknown'}}
        e['values']['amount']={'status':'known','value':'unknown'}
        e['selected_digest']=core.digest(d)
        text=front.render(e)
        self.assertIn('bind "amount" known "unknown";',text)
        self.assertEqual(front.assess_exchange(front.lower(text))['status'],'requirements_satisfied')
        e['values'].pop('amount')
        result=front.assess_exchange(front.lower(front.render(e)))
        self.assertEqual(result['status'],'unresolved')
        self.assertEqual(result['findings'][0]['unresolved_inputs'],{'amount':'missing_input'})

    def test_all_operators_and_limits(self):
        expressions = [
            {'op':'all','args':[{'op':'ref','id':'review'},{'op':'not','arg':{'op':'ref','id':'review'}}]},
            {'op':'any','args':[{'op':'ref','id':'review'},{'op':'not','arg':{'op':'ref','id':'review'}}]}]
        for node in expressions:
            e=deepcopy(self.example)
            e['definition']['requirements'][1]['predicate']=node
            e['selected_digest']=core.digest(e['definition'])
            self.assertEqual(front.lower(front.render(e)),e)
        r={'op':'ref','id':'amount'}
        for op in ['eq','le','lt']:
            for arithmetic in ['add','sub']:
                e=deepcopy(self.example)
                e['definition']['requirements'][0]['predicate']={'op':op,'left':r,
                    'right':{'op':arithmetic,'left':r,'right':r}}
                e['selected_digest']=core.digest(e['definition'])
                self.assertEqual(front.lower(front.render(e)),e)
        deep='(not '*(core.MAX_DEPTH+1)+'(ref "review")'+')'*(core.MAX_DEPTH+1)
        self.rejected(self.text.replace('(ref "review")',deep))
        self.rejected(' '*(core.MAX_BYTES+1))


if __name__ == '__main__':
    unittest.main()
