from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / 'scripts'))
import sector_reference_binding_v1 as binding


def fixture(sector='bank'):
    packet, _ = binding.load_native(sector)
    case_id = binding.CATALOG[sector]['case']
    selected = binding.native_selection(packet, sector, case_id)
    context = packet['record_registry'][selected['context']['digest']]['body']
    book = {'entity': context['bank_id'] if sector == 'bank' else context['entity_id'],
            'book': context['book_id'], 'currency': context['currency'], 'sector': sector,
            'state_ref': selected['state']['digest'], 'source_ref': selected['source']['digest'],
            'view_ref': selected['view']['digest']}
    component = {key: book[key] for key in ['sector','state_ref','source_ref','view_ref']}
    component.update(owner='selected', profile=binding.world.SECTORS[sector],
                     status='unresolved', obligation_ids=['actual-facts'])
    world = {'profile': binding.world.PROFILE,
             'context': {'world_id': 'retained-reference', 'currency': 'USD', 'calendar': 'gregorian',
                         'case_id': 'separate-retained-case', 'mode': 'conditional'},
             'books': {'selected': book}, 'control_edges': [], 'components': {'selected': component},
             'obligations': [{'id': 'actual-facts', 'meaning': 'Actual entity and current-law admission unresolved',
                              'affects': ['accounting', 'execution']}]}
    return {'profile': binding.PROFILE, 'world': world, 'component_id': 'selected', 'case_id': case_id}


class SectorReferenceTests(unittest.TestCase):
    def checked(self, request, reason=None):
        before = deepcopy(request); result = binding.bind(request)
        self.assertEqual(request, before)
        self.assertEqual(result['status'], 'invalid' if reason else 'assessment_reference_resolved', result)
        for flag in binding.FLAGS:
            self.assertIs(result[flag], flag == 'selected_references_resolved' and reason is None)
        if reason:
            self.assertEqual(result['reason'], reason); self.assertNotIn('world', result)
        return result

    def test_retained_bank_preserves_capital_context_state_sources_and_obligations(self):
        request = fixture(); result = self.checked(request)
        self.assertEqual(result['native_context']['unit'], 'million')
        self.assertEqual(result['native_context']['perimeter_id'], 'Solo')
        self.assertEqual(result['native_context']['accounting_basis'], 'US_GAAP_CECL_supplied')
        self.assertEqual(result['native_state_kind'], 'AccountingState')
        self.assertTrue(result['native_state_contains_balances'])
        source = result['records'][result['selection']['source']['digest']]['body']
        self.assertEqual(len(source['source_refs']), 10)
        self.assertEqual(source['law_mode'], 'scenario_frozen_not_actual_applicability')
        self.assertEqual(result['component_status'], 'unresolved')
        self.assertEqual(result['unresolved_obligations'], request['world']['obligations'])
        self.assertTrue(binding.verify(request, result))

    def test_insurer_head_is_not_a_materialized_legal_book(self):
        result = self.checked(fixture('insurance'))
        self.assertEqual(result['native_context']['unit'], 'illustrative_million')
        self.assertEqual(result['native_context']['authority'], 'historical_EU2023_IFRS17')
        self.assertEqual(result['native_state_kind'], 'AccountingHead')
        self.assertFalse(result['native_state_contains_balances'])
        state = result['records'][result['selection']['state']['digest']]['body']
        self.assertIn('balances_sha256', state); self.assertNotIn('balances', state)
        self.assertEqual(result['native_accounting_effect'], 'none')

    def test_full_world_is_unchanged_and_unselected_books_stay_opaque(self):
        request = fixture('insurance')
        other = deepcopy(request['world']['books']['selected']); other['entity'] = 'Unrelated'
        other['state_ref'] = '0' * 64
        request['world']['books']['other'] = other
        result = self.checked(request)
        self.assertEqual(result['world'], request['world'])
        self.assertFalse(result['references_resolved'])
        result['world']['books']['other']['entity'] = 'changed'
        self.assertEqual(request['world']['books']['other']['entity'], 'Unrelated')

    def test_native_handle_mismatches_refuse_after_envelope_agreement(self):
        for field in ['state_ref','source_ref','view_ref']:
            with self.subTest(field=field):
                request = fixture()
                request['world']['books']['selected'][field] = '0' * 64
                request['world']['components']['selected'][field] = '0' * 64
                self.checked(request, 'native_' + field + '_binding')

    def test_owner_currency_and_case_mismatches_have_exact_refusals(self):
        request = fixture(); request['world']['books']['selected']['entity'] = 'Another'
        self.checked(request, 'native_owner_binding')
        request = fixture(); request['world']['books']['selected']['book'] = 'Consolidated'
        self.checked(request, 'native_owner_binding')
        request = fixture(); request['world']['books']['selected']['currency'] = 'EUR'
        request['world']['context']['currency'] = 'EUR'
        self.checked(request, 'native_currency_binding')
        request = fixture(); request['case_id'] = 'route.full'
        self.checked(request, 'unsupported_native_case')

    def test_group_packet_cannot_be_used_as_a_legal_book_projection(self):
        request = fixture()
        request['world']['books']['selected']['sector'] = 'corporate'
        request['world']['components']['selected'].update(sector='corporate', profile='CompanyComposition/1')
        self.checked(request, 'unsupported_sector_projection')

    def test_missing_record_and_reference_type_are_checked(self):
        packet, schemas = binding.load_native('insurance')
        roots = list(binding.native_selection(packet, 'insurance', 'route.full').values())
        del packet['record_registry'][roots[2]['digest']]
        with self.assertRaisesRegex(binding.core.Invalid, '^missing_native_record$'):
            binding.resolve_closure(packet, schemas, roots)
        packet, schemas = binding.load_native('insurance')
        roots[0]['kind'] = 'Context'
        with self.assertRaisesRegex(binding.core.Invalid, '^native_reference_type$'):
            binding.resolve_closure(packet, schemas, roots)

    def test_changed_native_record_is_not_hidden_by_a_valid_reference(self):
        packet, schemas = binding.load_native('insurance')
        selection = binding.native_selection(packet, 'insurance', 'route.full')
        packet['record_registry'][selection['context']['digest']]['body']['entity_id'] = 'Changed'
        with self.assertRaisesRegex(binding.core.Invalid, '^native_record_digest$'):
            binding.resolve_closure(packet, schemas, list(selection.values()))

    def test_blob_bytes_and_length_are_checked(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'data') as tmp:
            path = Path(tmp) / 'small.txt'; path.write_bytes(b'abc')
            digest = sha256(b'abc').hexdigest()
            ref = {'kind':'blob','algorithm':'sha256','digest':digest,'byte_length':3}
            index = {digest:{'path':str(path.relative_to(ROOT)),'byte_length':3}}
            self.assertEqual(binding.checked_blob(ref,index)['sha256'],digest)
            path.write_bytes(b'abd')
            with self.assertRaisesRegex(binding.core.Invalid, '^blob_digest$'): binding.checked_blob(ref,index)
            path.write_bytes(b'a')
            with self.assertRaisesRegex(binding.core.Invalid, '^blob_length$'): binding.checked_blob(ref,index)
            with self.assertRaisesRegex(binding.core.Invalid, '^missing_blob$'): binding.checked_blob(ref,{})

    def test_native_pins_and_result_tampering_refuse(self):
        request = fixture('insurance')
        with patch.dict(binding.CATALOG['insurance'], packet_sha256='0'*64):
            self.checked(request, 'native_packet_sha256')
        with patch.object(binding, 'WORLD_SHA256', '0'*64):
            self.checked(request, 'world_dependency_hash')
        result = self.checked(request); result['posting_authorized'] = True
        self.assertFalse(binding.verify(request,result))


if __name__ == '__main__': unittest.main()
