from copy import deepcopy
from pathlib import Path
import importlib.util
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / 'scripts'))
import company_book_transition_v2 as engine
spec = importlib.util.spec_from_file_location('typed_growth_examples', ROOT /
    'data/accounting-master/declared-collection-state-growth-20261025/examples.py')
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)


class TypedBookTests(unittest.TestCase):
    def checked(self, book, request, status):
        before = deepcopy((book, request)); result = engine.propose(book, request)
        self.assertEqual(result['status'], status, result)
        self.assertEqual((book, request), before)
        for flag in engine.FLAGS: self.assertIs(result[flag], False)
        if status != 'proposed': self.assertNotIn('after', result)
        return result

    def test_fixed_replacements_equal_v1_on_two_charts(self):
        for owner in ['alpha', 'beta']:
            oldbook, oldrequest = ex.old.fixture(owner)
            prior = engine.base.propose(oldbook, oldrequest)
            book, request = ex.fixed_fixture(owner); result = self.checked(book, request, 'proposed')
            for key in ['after', 'journal', 'flows', 'preconditions', 'monetary', 'postconditions']:
                self.assertEqual(result[key], prior[key], key)

    def test_new_sale_atomically_creates_claim_and_all_postings(self):
        for owner in ['alpha', 'beta']:
            book, request, mapping = ex.sale_fixture(owner)
            result = self.checked(book, request, 'proposed'); after = result['after']
            self.assertEqual(after['memory']['claims'], {'invoice/a~1': {
                'due': '2027-01-31', 'remaining': '30/1', 'sale_event': 'sale.1'}})
            expected = {k: '0/1' for k in book['accounts']}
            for role, amount in [('receivables', '30/1'), ('revenue', '-30/1'),
                                 ('cost_of_sales', '10/1'), ('inventory', '-10/1')]:
                expected[mapping[role]] = amount
            self.assertEqual(result['journal'], expected); self.assertEqual(result['flows'], [])
            self.assertEqual(after['balances'][mapping['inventory']], '10/1')
            self.assertEqual(after['memory_types']['/claims/invoice~1a~01/remaining'], engine.base.money_type(book))
            self.assertEqual(engine.apply(book, request, result)['status'], 'applied_provisional')

    def test_duplicate_insert_preserves_input_and_provides_no_after(self):
        book, request, _ = ex.sale_fixture(); after = self.checked(book, request, 'proposed')['after']
        request['event']['id'] = 'sale.2'; ex.rehash(after, request)
        result = self.checked(after, request, 'invalid')
        self.assertEqual(result['memory']['reason'], 'insert_target_exists')

    def test_dynamic_key_is_one_escaped_token(self):
        book, request, _ = ex.sale_fixture()
        request['event']['id'] = 'sale/a~1'
        request['method']['memory']['definition']['operations'][0]['path'][1] = {'input_pointer': '/event_id'}
        ex.rehash(book, request); after = self.checked(book, request, 'proposed')['after']
        self.assertIn('/claims/sale~1a~01/remaining', after['memory_types'])

    def test_capacity_is_checked_after_stage_before_proposal(self):
        book, request, _ = ex.sale_fixture(capacity=1)
        after = self.checked(book, request, 'proposed')['after']
        request['event']['id'] = 'sale.2'
        request['method']['memory']['definition']['operations'][0]['path'][1] = 'second'
        ex.rehash(after, request); result = self.checked(after, request, 'invalid')
        self.assertIn('memory_map_capacity', result['reason'])

    def test_dimension_mismatch_cannot_hide_behind_false_approval(self):
        book, request, _ = ex.sale_fixture()
        typ = request['memory_definition']['root']['fields']['claims']['values']['fields']['remaining']['type']
        typ['dimensions'] = {'goods:unit': 1}
        request['event']['inputs']['approved']['value'] = engine.base.known(False)
        ex.rehash(book, request); result = self.checked(book, request, 'invalid')
        self.assertEqual(result['reason'], 'memory_write_type_mismatch')

    def test_record_replacement_append_and_bad_dynamic_key_refuse(self):
        for variant in ['replace', 'append', 'bad_key', 'missing_field']:
            book, request, _ = ex.sale_fixture()
            operation = request['method']['memory']['definition']['operations'][0]
            if variant in ['replace', 'append']: operation['op'] = variant
            elif variant == 'bad_key': operation['path'][1] = {'input_pointer': '/amount'}
            else: operation['value']['fields'].pop('due')
            ex.rehash(book, request); self.checked(book, request, 'invalid')

    def test_unknown_input_and_false_approval_do_not_create_claim(self):
        for key, value, status in [('consideration', {'status': 'unknown', 'reason': 'absent'}, 'unresolved'),
                                   ('approved', engine.base.known(False), 'unsupported')]:
            book, request, _ = ex.sale_fixture(); request['event']['inputs'][key]['value'] = value
            self.checked(book, request, status)

    def test_old_profile_still_rejects_structural_writes(self):
        book, request, _ = ex.sale_fixture(); request.pop('memory_definition'); request['profile'] = engine.base.PROFILE
        result = engine.base.propose(book, request)
        self.assertEqual(result['status'], 'invalid'); self.assertEqual(result['reason'], 'fixed_scalar_replacements_only')

    def test_postcondition_failure_stale_state_and_tamper(self):
        book, request = ex.fixed_fixture()
        request['method']['memory']['definition']['operations'][0]['value'] = {'kind': 'literal', 'value': '29/1'}
        ex.rehash(book, request); self.checked(book, request, 'invalid')
        book, request, _ = ex.sale_fixture(); request['expected_state_sha256'] = '0' * 64
        self.checked(book, request, 'invalid')
        ex.rehash(book, request); result = self.checked(book, request, 'proposed')
        result['after']['memory']['claims'].clear()
        self.assertEqual(engine.apply(book, request, result)['status'], 'invalid')


if __name__ == '__main__': unittest.main()
