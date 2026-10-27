"""Source-preserving measurement constraints do not reconstruct an actual book."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
from unittest.mock import patch
import json
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import henkel_lease_measurements_v1 as h


class HenkelMeasurementsTests(unittest.TestCase):
    def test_default_retains_all_source_observations_and_state_unknowns(self):
        body=h.fixture();original=deepcopy(body);r=h.assess(body,h.BUDGET)
        self.assertEqual(r['status'],'unresolved');self.assertEqual(body,original)
        self.assertEqual(r['preserved_inventory'],json.loads((h.SOURCE/'observations.json').read_text()))
        self.assertEqual(len(r['preserved_inventory']['observations']),104)
        self.assertEqual(len(r['preserved_state_dependencies']['dependencies']),14)
        self.assertTrue(all(o['interval'] is None for o in r['definition']['observations'].values()))
        self.assertFalse(r['native_state_admission']);self.assertFalse(r['source_admission'])
        self.assertFalse(r['accounting_admission']);self.assertIsNone(r['executable_opening'])

    def test_joint_hypothesis_has_exact_independently_checked_witness(self):
        r=h.assess(h.fixture(assume=True),h.BUDGET)
        self.assertEqual(r['status'],'conditionally_feasible',r.get('reason'))
        values={k:Q(v) for k,v in r['temporal_assessment']['joint_assessment']['witness'].items()}
        for year in [2024,2025]:
            def v(key):return values[f'{year}.{key}']
            self.assertEqual(v('liability.total'),v('liability.current')+v('liability.noncurrent'))
            self.assertEqual(v('rou_gross.total')-v('rou_accumulated.total'),v('rou_net.total'))
            self.assertEqual(v('reconciliation.cash'),v('reconciliation.interest_paid')+v('reconciliation.redemption'))
            self.assertEqual(v('reconciliation.closing'),v('reconciliation.opening')+sum(v('reconciliation.'+k) for k in ['cash','expense','additions','acquisitions','fx','fair_value','sundry']))
            self.assertEqual(v('reconciliation.closing'),-v('liability.total'))
        self.assertEqual(values['2025.reconciliation.opening'],values['2024.reconciliation.closing'])
        self.assertEqual(len(values),54)
        self.assertTrue(h.verify_result(h.fixture(assume=True),h.BUDGET,r))

    def test_separate_year_and_partial_assumptions(self):
        for year in [2024,2025]:
            keys=[k for k in h.SUPPORTED if k.startswith(str(year)) and not k.endswith('continuity')]
            self.assertEqual(h.assess(h.fixture(keys,True),h.BUDGET)['status'],'conditionally_feasible')
        for missing in ['rounding','identity']:
            b=h.fixture(assume=True)
            if missing=='rounding':b['rounding_hypothesis']=None
            else:b['identity_hypotheses'][h.SUPPORTED[0]]=None
            self.assertEqual(h.assess(b,h.BUDGET)['status'],'unresolved')

    def test_zero_and_unsupported_resources_remain_distinct(self):
        b=h.fixture(assume=True)
        r=h.assess(b,{**h.BUDGET,'max_cells':0});self.assertEqual(r['status'],'unknown')
        self.assertNotIn('witness',r['temporal_assessment']['joint_assessment'])
        for change in [{'max_cells':2},{'max_slots':1},{'elapsed_ms':60001},{'solver_timeout_ms':10001}]:
            self.assertEqual(h.assess(b,{**h.BUDGET,**change})['status'],'invalid')

    def test_rounding_endpoints_signed_zero_and_no_dash_coercion(self):
        self.assertEqual(h.interval('1'),{'lower':'1/2','upper':'3/2','lower_inclusive':True,'upper_inclusive':False})
        self.assertEqual(h.interval('-1'),{'lower':'-3/2','upper':'-1/2','lower_inclusive':False,'upper_inclusive':True})
        self.assertEqual(h.interval('0'),{'lower':'-1/2','upper':'1/2','lower_inclusive':False,'upper_inclusive':False})
        r=h.assess(h.fixture(assume=True),h.BUDGET)
        self.assertEqual(r['source_mapping']['2025.reconciliation.fair_value']['literal'],'-0')
        self.assertEqual(r['definition']['observations']['2025.reconciliation.fair_value']['interval'],h.interval('0'))
        self.assertFalse(any('construction' in k for k in r['definition']['observations']))
        self.assertEqual(sum(o['literal']=='–' for o in r['preserved_inventory']['observations']),8)

    def test_treating_displayed_totals_as_exact_is_rejected_by_math(self):
        r=h.build(h.fixture(['2024.rou_gross_net'],True),h.BUDGET);d=r['definition']
        for key,o in d['observations'].items():
            amount=h.rational(r['source_mapping'][key]['displayed_rational'])
            o['interval']={'lower':amount,'upper':amount,'lower_inclusive':True,'upper_inclusive':True}
            o['interval_premise']={'id':'counterfactual_exact_displays','status':'proposed','meaning':'Deliberately treat rounded displays as exact to test contradiction.'}
        result=h.temporal.assess(d,h.BUDGET)
        self.assertEqual(result['status'],'conditionally_infeasible')
        self.assertTrue(all(c['rechecked']=='unsat' for c in result['joint_assessment']['conflicts']))

    def test_context_and_time_cannot_be_lost_in_lowering(self):
        r=h.build(h.fixture(['2025.signed_liability_bridge'],True),h.BUDGET)
        for action in ['date','period','currency','scale','owner','quantity']:
            d=deepcopy(r['definition']);o=d['observations']['2025.reconciliation.opening']['type']
            if action=='date':o['time']['at']='2025-01-01'
            elif action=='period':d['observations']['2025.reconciliation.cash']['type']['time']['end_exclusive']='2025-12-31'
            elif action=='currency':o['value_type']['dimensions']={'currency:USD':1}
            elif action=='scale':o['value_type']['scale']='1/1'
            elif action=='owner':o['value_type']['context']['perimeter']='single legal company'
            else:o['quantity']='ROU'
            self.assertEqual(h.temporal.assess(d,h.BUDGET)['status'],'invalid',action)

    def test_closed_request_and_unsupported_relations(self):
        for change in [{'inventory_sha256':'0'*64},{'currency':'USD'},{'selected_relations':['unknown'],'identity_hypotheses':{'unknown':None}}, {'selected_relations':[h.SUPPORTED[0],h.SUPPORTED[0]],'identity_hypotheses':{h.SUPPORTED[0]:None}}]:
            b=h.fixture();b.update(change);self.assertEqual(h.assess(b,h.BUDGET)['status'],'invalid')
        b=h.fixture(assume=True);b['rounding_hypothesis']['unit']='USD million'
        self.assertEqual(h.assess(b,h.BUDGET)['status'],'invalid')
        b=h.fixture(assume=True);b['identity_hypotheses'][h.SUPPORTED[0]]['status']='admitted'
        self.assertEqual(h.assess(b,h.BUDGET)['status'],'invalid')
        with patch.object(h,'LOCK_SHA256','0'*64):
            self.assertEqual(h.assess(h.fixture(),h.BUDGET)['status'],'invalid')

    def test_empty_selection_preserves_source_without_assertions(self):
        b=h.fixture([]);r=h.assess(b,h.BUDGET)
        self.assertEqual(r['status'],'no_asserted_system')
        self.assertEqual(len(r['preserved_inventory']['observations']),104)
        self.assertTrue(h.verify_result(b,h.BUDGET,r))

    def test_forged_results_cannot_gain_admission_or_drop_unknowns(self):
        b=h.fixture(assume=True);r=h.assess(b,h.BUDGET)
        for action in ['admission','dependency','literal','witness','time','extra','missing_witness']:
            bad=deepcopy(r)
            if action=='admission':bad['native_state_admission']=True
            elif action=='dependency':bad['preserved_state_dependencies']['dependencies'].pop()
            elif action=='literal':bad['preserved_inventory']['observations'][0]['literal']='0'
            elif action=='witness':bad['temporal_assessment']['joint_assessment']['witness']['2024.rou_net.total']='0/1'
            elif action=='time':bad['temporal_assessment']['joint_assessment']['solver_wall_seconds']=-1
            elif action=='extra':bad['new_field']=True
            else:bad['temporal_assessment']['joint_assessment'].pop('witness')
            self.assertFalse(h.verify_result(b,h.BUDGET,bad),action)


if __name__=='__main__':unittest.main()
