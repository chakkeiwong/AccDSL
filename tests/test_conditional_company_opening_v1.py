from copy import deepcopy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]; sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'tests')]
import conditional_company_opening_v1 as adapter
from test_typed_history_measurement_attachment_v1 import monetary_fixture, fixture as stock_fixture
from test_history_measurement_attachment_v1 import joined_witness
from test_conditional_history_family_v1 import BUDGET, domain


def request(owner='alpha', selected=(10,2,3)):
    definition = monetary_fixture()
    context = {'entity':'Synthetic','book':'example','currency':'USD','case_id':'selected-' + owner,'mode':'synthetic'}
    names = {'Cash':'cash' if owner=='alpha' else '101', 'Equity':'capital' if owner=='alpha' else '301'}
    mapping = {'source_date':'2024-12-31', 'context':context,
        'period':{'start':'2025-01-01','end_exclusive':'2026-01-01'},
        'accounts':{k:{'id':v,'classification':'asset' if k=='Cash' else 'equity',
                      'provenance':'Explicit synthetic chart classification'} for k,v in names.items()},
        'memory':{'cumulative_sales':{'path':['history','sales/a~1'], 'provenance':'Preserve conditional sales total'}},
        'cash_account':names['Cash'], 'context_premise':'Preserve source basis in provenance; no accounting basis conversion',
        'boundary_premise':'No intervening event between final snapshot and next-day opening'}
    return {'profile':adapter.PROFILE,'attachment':definition,'budget':deepcopy(BUDGET),
            'witness':joined_witness(*selected),'mapping':mapping}


class ConditionalOpeningTests(unittest.TestCase):
    def checked(self, body, status):
        before = deepcopy(body); result = adapter.map_opening(body)
        self.assertEqual(result['status'], status, result)
        self.assertEqual(body, before)
        for flag in adapter.FLAGS: self.assertIs(result[flag], False)
        if status in ['invalid','unresolved']: self.assertNotIn('opening', result)
        return result

    def test_two_charts_two_witnesses_preserve_distinct_memory(self):
        for owner in ['alpha','beta']:
            a = self.checked(request(owner, (10,2,3)), 'conditional_opening')
            b = self.checked(request(owner, (8,3,4)), 'conditional_opening')
            self.assertEqual(a['opening']['balances'], b['opening']['balances'])
            self.assertEqual(set(a['opening']['balances'].values()), {'15/1','-15/1'})
            self.assertEqual(a['opening']['memory']['history']['sales/a~1'], '5/1')
            self.assertEqual(b['opening']['memory']['history']['sales/a~1'], '7/1')
            self.assertNotEqual(a['witness_sha256'], b['witness_sha256'])
            self.assertEqual(a['attachment_sha256'], b['attachment_sha256'])
            self.assertEqual(a['opening']['seen'], ['early','late'])
            self.assertEqual(a['opening']['flows'], [])
            self.assertEqual(a['provenance']['source_snapshot_date'], '2024-12-31')
            self.assertEqual(a['opening']['date'], '2025-01-01')
            self.assertEqual(a['source_context']['basis'], 'authored')
            self.assertEqual(a['opening_report']['balance_sheet']['total_assets'], '15/1')
            self.assertTrue(adapter.verify(request(owner), a))

    def test_stock_units_remain_separate_from_money(self):
        body = request(); body['attachment'] = stock_fixture()
        assessed = adapter.attachment.assess(body['attachment'], body['budget'])
        self.assertEqual(assessed['status'], 'conditional_attachment_witness')
        body['witness'] = assessed['witness']
        body['mapping']['accounts']['Inventory'] = {'id':'stock','classification':'asset','provenance':'Declared inventory'}
        body['mapping']['memory'] = {'units':{'path':['stock','units'],'provenance':'Exact units mapping'}}
        result = self.checked(body, 'conditional_opening')
        self.assertEqual(result['opening']['memory']['stock']['units'], '1/1')
        self.assertEqual(result['opening']['memory_types']['/stock/units']['dimensions'], {'units:widget':1})
        self.assertEqual(result['opening']['balances']['stock'], '2/1')
        self.assertEqual(result['opening']['balances']['cash'], '21/1')

    def test_invalid_witness_refuses_before_constructing_opening(self):
        body = request(); key = next(k for k in body['witness'] if 'measurement' in k and 'closing' in k)
        body['witness'][key] = '16/1'; self.checked(body, 'invalid')

    def test_missing_premise_and_obligations_are_not_promoted(self):
        body = request(); body['attachment']['history']['balance_premise'] = None
        result = self.checked(body, 'unresolved'); self.assertTrue(result['missing_premises'])
        body = request(); obligation = {'id':'invoice_terms','meaning':'Unobserved contract population', 'affects':['execution']}
        body['attachment']['obligations'].append(obligation)
        result = self.checked(body, 'candidate_opening_with_unresolved_obligations')
        self.assertEqual(result['target_obligations'][0]['obligation'], obligation)
        self.assertEqual(result['provenance']['attachment_definition'], body['attachment'])
        self.assertFalse(result['execution_clearance'])

    def test_missing_duplicate_and_extra_account_or_memory_map_refuse(self):
        for variant in ['missing_account','duplicate_account','extra_account','missing_memory','extra_memory']:
            body = request(); mapping = body['mapping']
            if variant == 'missing_account': mapping['accounts'].pop('Equity')
            elif variant == 'duplicate_account': mapping['accounts']['Equity']['id'] = mapping['accounts']['Cash']['id']
            elif variant == 'extra_account': mapping['accounts']['Other'] = deepcopy(mapping['accounts']['Equity'])
            elif variant == 'missing_memory': mapping['memory'].clear()
            else: mapping['memory']['Invented'] = {'path':['invented'],'provenance':'not a fact'}
            self.checked(body, 'invalid')

    def test_context_currency_and_date_mismatches_refuse(self):
        for field, value in [('entity','Other'),('book','consolidated'),('currency','EUR'),('mode','admitted')]:
            body = request(); body['mapping']['context'][field] = value; self.checked(body, 'invalid')
        for variant in ['source','day','end']:
            body = request()
            if variant == 'source': body['mapping']['source_date'] = '2024-06-30'
            else: body['mapping']['period']['start' if variant == 'day' else 'end_exclusive'] = '2024-12-31'
            self.checked(body, 'invalid')

    def test_nonzero_temporary_balance_is_not_silently_closed(self):
        body = request(); body['mapping']['accounts']['Equity']['classification'] = 'income'
        result = self.checked(body, 'invalid'); self.assertIn('opening_temporary_balance', result['reason'])

    def test_blank_bridge_and_bad_paths_refuse(self):
        for variant in ['context','boundary','path']:
            body = request()
            if variant == 'path': body['mapping']['memory']['cumulative_sales']['path'] = []
            else: body['mapping'][variant + '_premise'] = ' '
            self.checked(body, 'invalid')

    def test_provenance_and_flags_tamper_refuse(self):
        body = request(); result = self.checked(body, 'conditional_opening')
        changed = deepcopy(result); changed['source_admission'] = 0; self.assertFalse(adapter.verify(body, changed))
        changed = deepcopy(result); changed['provenance']['target_obligations'] = ['erased']
        self.assertFalse(adapter.verify(body, changed))
        with patch.dict(adapter.PINS, {'typed_affine_history_v1.py':'0' * 64}): self.checked(body, 'invalid')

    def test_overlapping_memory_paths_and_nonunit_money_scale_refuse(self):
        body = request(); history = body['attachment']['history']
        history['memory']['other'] = deepcopy(history['memory']['cumulative_sales'])
        body['witness'][adapter.attachment.key('history', adapter.attachment.history.identifier('opening_memory','other'))] = '0/1'
        body['mapping']['memory']['other'] = {'path':['history'], 'provenance':'Overlapping destination'}
        result = self.checked(body, 'invalid'); self.assertEqual(result['reason'], 'overlapping_memory_paths')
        body = request()
        # A coherent rescaling is not provided: the mismatch must refuse, never coerce.
        body['attachment']['history']['value_type']['scale'] = '1000/1'
        self.checked(body, 'invalid')

    def test_unmapped_observation_survives_as_execution_obligation(self):
        body = request(); body['attachment']['bindings'].pop('opening')
        result = self.checked(body, 'candidate_opening_with_unresolved_obligations')
        self.assertTrue(any(row['origin']=='unmapped_measurement' and row['observation']=='opening'
                            for row in result['target_obligations']))
        self.assertFalse(result['execution_clearance'])


if __name__ == '__main__': unittest.main()
