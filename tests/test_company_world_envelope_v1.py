from copy import deepcopy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / 'scripts'))
import company_world_envelope_v1 as world


def digest(seed): return ('%064x' % seed)


def fixture(mode='conditional'):
    books = {
        'parent': {'entity':'P','book':'legal-P','currency':'USD','sector':'corporate',
                   'state_ref':digest(1),'source_ref':digest(2),'view_ref':digest(3)},
        'bank': {'entity':'B','book':'legal-B','currency':'USD','sector':'bank',
                 'state_ref':digest(4),'source_ref':digest(5),'view_ref':digest(6)},
        'insurer': {'entity':'I','book':'legal-I','currency':'USD','sector':'insurance',
                    'state_ref':digest(7),'source_ref':digest(8),'view_ref':digest(9)}}
    return {'profile':world.PROFILE,
        'context': {'world_id':'world.1','currency':'USD','calendar':'gregorian','case_id':'synthetic.world','mode':mode},
        'books': books,
        'control_edges': [{'id':'control.1','parent':'P','child':'B','ownership_fraction':'4/5',
                           'start':'2025-01-01','end_exclusive':'2026-01-01','control_premise':'Explicit synthetic control premise'}],
        'components': {
            'corporate.P': {'owner':'parent','sector':'corporate','profile':'CompanyComposition/1','state_ref':digest(1),
                            'source_ref':digest(2),'view_ref':digest(3),'status':'conditional','obligation_ids':['p5.scope']},
            'bank.B': {'owner':'bank','sector':'bank','profile':'BankAssessment/1','state_ref':digest(4),
                       'source_ref':digest(5),'view_ref':digest(6),'status':'unresolved','obligation_ids':['bank.law']},
            'insurance.I': {'owner':'insurer','sector':'insurance','profile':'InsuranceAssessment/1','state_ref':digest(7),
                            'source_ref':digest(8),'view_ref':digest(9),'status':'conditional','obligation_ids':[]}},
        'obligations': [
            {'id':'p5.scope','meaning':'Finite synthetic group scope only','affects':['consolidation','execution']},
            {'id':'bank.law','meaning':'Jurisdictional capital and allowance rules unresolved','affects':['accounting','execution']} ]}


class CompanyWorldTests(unittest.TestCase):
    def checked(self, body, reason=None):
        before = deepcopy(body)
        result = world.propose(body)
        self.assertEqual(result['status'], 'invalid' if reason else 'proposed', result)
        self.assertEqual(body, before)
        for flag in world.FLAGS: self.assertIs(result[flag], False)
        if reason:
            self.assertEqual(result['reason'], reason)
            self.assertNotIn('world', result)
        return result

    def test_mixed_world_retains_opaque_handles_and_all_obligations(self):
        body = fixture()
        result = self.checked(body)
        self.assertEqual(result['book_ids'], ['bank', 'insurer', 'parent'])
        self.assertEqual(result['component_ids'], ['bank.B', 'corporate.P', 'insurance.I'])
        self.assertEqual(result['world'], body)
        self.assertEqual(result['unresolved_obligations'], body['obligations'])
        self.assertTrue(world.verify(body, result))
        result['world']['books']['bank']['state_ref'] = digest(90)
        self.assertEqual(body, fixture())
        self.assertFalse(world.verify(body, result))

    def test_empty_components_do_not_imply_completeness(self):
        body = fixture(); body['components'] = {}; body['obligations'] = []
        result = self.checked(body)
        self.assertEqual(result['component_ids'], [])
        self.assertFalse(result['world_complete'])

    def test_state_source_and_view_bind_to_the_named_book(self):
        for field in ['state_ref', 'source_ref', 'view_ref']:
            with self.subTest(field=field):
                body = fixture(); body['components']['corporate.P'][field] = digest(60)
                self.checked(body, 'component_' + field + '_binding')
        body = fixture(); body['components']['corporate.P']['owner'] = 'absent'
        self.checked(body, 'component_unknown_owner')

    def test_component_sector_must_match_profile_and_owner_sector(self):
        body = fixture(); body['components']['bank.B']['profile'] = 'CompanyComposition/1'
        self.checked(body, 'component_profile_sector')
        body = fixture(); body['components']['corporate.P']['owner'] = 'bank'
        self.checked(body, 'component_owner_sector')
        body = fixture(); component = body['components']['bank.B']
        component['sector'] = 'insurance'; component['profile'] = 'InsuranceAssessment/1'
        self.checked(body, 'component_owner_sector')

    def test_one_root_sector_component_per_book(self):
        body = fixture(); body['components']['duplicate'] = deepcopy(body['components']['bank.B'])
        self.checked(body, 'duplicate_sector_owner')

    def test_multiple_books_per_entity_have_distinct_identities(self):
        body = fixture(); other = deepcopy(body['books']['parent']); other['book'] = 'second-P'
        body['books']['parent.second'] = other
        self.checked(body)
        other['book'] = 'legal-P'
        self.checked(body, 'duplicate_legal_book')

    def test_currency_and_calendar_are_explicit_supported_context(self):
        body = fixture(); body['books']['bank']['currency'] = 'EUR'
        self.checked(body, 'book_currency_context')
        body = fixture(); body['context']['calendar'] = '360-day'
        self.checked(body, 'world_calendar')
        body = fixture(); body['context']['mode'] = 'admitted'
        self.checked(body, 'world_mode')

    def test_control_entity_date_and_id_refusals_are_distinct(self):
        body = fixture(); body['control_edges'][0]['child'] = 'X'
        self.checked(body, 'control_unknown_entity')
        body = fixture(); body['control_edges'][0]['child'] = 'P'
        self.checked(body, 'self_control')
        body = fixture(); body['control_edges'].append(deepcopy(body['control_edges'][0]))
        self.checked(body, 'duplicate_control_id')
        body['control_edges'][1]['id'] = 'different'
        self.checked(body, 'duplicate_control_pair')
        body = fixture(); body['control_edges'][0]['end_exclusive'] = '2024-01-01'
        self.checked(body, 'control_date_order')

    def test_exact_reduced_ownership_fraction_is_not_a_control_test(self):
        for value in ['0/1', '1/100', '4/5', '1/1']:
            body = fixture(); body['control_edges'][0]['ownership_fraction'] = value
            result = self.checked(body)
            self.assertFalse(result['control_assessed'])
        for value, reason in [('8/10', 'noncanonical_rational'), ('5/4', 'ownership_fraction_range'),
                              ('-1/5', 'ownership_fraction_range'), ('0.8', 'rational_syntax'),
                              ('1/0', 'rational_syntax'), ('01/2', 'rational_syntax')]:
            with self.subTest(value=value):
                body = fixture(); body['control_edges'][0]['ownership_fraction'] = value
                self.checked(body, reason)
        body = fixture(); body['control_edges'][0]['ownership_fraction'] = True
        self.checked(body, 'world_scalar_type')
        body = fixture(); body['control_edges'][0]['control_premise'] = ' '
        self.checked(body, 'world_scalar')

    def test_unknown_duplicate_and_missing_obligations_refuse(self):
        body = fixture(); body['components']['corporate.P']['obligation_ids'] = ['missing']
        self.checked(body, 'unknown_component_obligation')
        body = fixture(); body['obligations'].append(deepcopy(body['obligations'][0]))
        self.checked(body, 'duplicate_obligation_id')
        body = fixture(); body['components']['bank.B']['obligation_ids'] = []
        self.checked(body, 'unresolved_component_obligation_required')
        body = fixture(); body['components']['corporate.P']['obligation_ids'] = ['p5.scope', 'p5.scope']
        self.checked(body, 'duplicate:component_obligation_ids')

    def test_digest_and_closed_schema_refuse(self):
        body = fixture(); body['books']['parent']['state_ref'] = 'a' * 63
        self.checked(body, 'book_state_ref_sha256')
        body = fixture(); body['books']['parent']['state_ref'] = 'A' * 64
        self.checked(body, 'book_state_ref_sha256')
        body = fixture(); body['unexpected'] = 'value'
        self.checked(body, 'fields:world')

    def test_finite_record_limits_precede_copying(self):
        body = fixture(); body['books'] = {str(i): deepcopy(body['books']['parent']) for i in range(65)}
        self.checked(body, 'book_count')
        body = fixture(); body['obligations'] = [
            {'id': str(i), 'meaning': 'x' * 4000, 'affects': ['execution']} for i in range(300)]
        self.checked(body, 'world_size_limit')
        nested = 'leaf'
        for _ in range(50): nested = [nested]
        self.checked({'too_deep': nested}, 'world_structure_limit')
        self.checked({'too_wide': ['leaf'] * 4097}, 'world_structure_limit')
        cyclic = {}; cyclic['self'] = cyclic
        self.assertEqual(world.propose(cyclic)['reason'], 'world_structure_limit')
        self.assertIs(cyclic['self'], cyclic)

    def test_dependency_and_result_identity_are_checked(self):
        body = fixture(); result = self.checked(body)
        for flag in world.FLAGS:
            altered = deepcopy(result); altered[flag] = True
            self.assertFalse(world.verify(body, altered))
        body['context']['case_id'] = 'changed'
        self.assertFalse(world.verify(body, result))
        with patch.object(world, 'CORE_SHA256', '0' * 64):
            self.checked(fixture(), 'world_core_dependency_hash')


if __name__ == '__main__': unittest.main()
