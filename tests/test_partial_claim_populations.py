from copy import deepcopy
from pathlib import Path
import importlib.util
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('partial_claim_populations',ROOT/'data/accounting-master/partial-claim-populations-20261025/populations.py')
pop=importlib.util.module_from_spec(spec);spec.loader.exec_module(pop)
CONTEXT={'entity':'Constructed example','scope':'declared legal book','currency':'USD','scale':'1/1'}

def row(identity,amount='20/1',due='2027-01-31'):
    return {'id':pop.known(identity),'remaining':pop.known(amount),'due':pop.known(due)}

class PartialClaimPopulationTests(unittest.TestCase):
    def test_retained_partial_state_is_preserved_for_each_view(self):
        for view,expected in [('annual',2),('interim',2),('combined',4)]:
            body=pop.partial_state.fixture(view=view);before=deepcopy(body);result=pop.evaluate(body)
            self.assertEqual(body,before);self.assertEqual(result['partial_state'],pop.partial_state.evaluate(body))
            self.assertEqual(len(result['populations']),expected)
            if view=='combined':self.assertEqual(len(result['partial_state']['constraints']),54)
            for r in result['populations']:
                v=r['population_view'];self.assertEqual(v['population']['status'],'partial')
                self.assertEqual(v['population']['rows'],[]);self.assertEqual(v['known_row_count'],0)
                for field in ['claim_count','gross_remaining','contractual_due_terms','future_receipts']:self.assertEqual(v[field]['status'],'unknown')
                self.assertEqual(v['native_assessment']['status'],'unresolved')
                self.assertEqual(r['measurement_relation']['status'],'unresolved')
            for key in ['executed','source_admission','accounting_admission','posting_authorized']:self.assertIs(result[key],False)
            self.assertIsNone(result['executable_opening'])

    def test_unknown_empty_and_complete_are_distinct(self):
        partial=pop.inspect(CONTEXT,{'status':'partial','rows':[],'reason':'No schedule'})
        empty=pop.inspect(CONTEXT,{'status':'complete','rows':[]})
        complete=pop.inspect(CONTEXT,{'status':'complete','rows':[row('a'),row('b','40/1','2027-02-28')]})
        self.assertEqual(partial['claim_count']['status'],'unknown')
        self.assertEqual(empty['claim_count'],pop.known(0));self.assertEqual(empty['gross_remaining'],pop.known('0/1'))
        self.assertEqual(empty['native_assessment']['status'],'collection_requirements_satisfied')
        self.assertEqual(complete['claim_count'],pop.known(2));self.assertEqual(complete['gross_remaining'],pop.known('60/1'))
        self.assertEqual(len(complete['contractual_due_terms']['value']),2)
        for result in [empty,complete]:self.assertEqual(result['future_receipts']['status'],'unknown')

    def test_partial_known_rows_never_become_complete_total(self):
        result=pop.inspect(CONTEXT,{'status':'partial','rows':[row('a')],'reason':'More members may exist'})
        self.assertEqual(result['known_row_count'],1)
        for key in ['claim_count','gross_remaining','contractual_due_terms']:self.assertEqual(result[key]['status'],'unknown')

    def test_duplicate_identity_and_negative_amount_refuse(self):
        for population in [{'status':'complete','rows':[row('a'),row('a')]},
                           {'status':'partial','rows':[row('a'),row('a')],'reason':'Unknown rest'},
                           {'status':'complete','rows':[row('a','-1/1')]}]:
            self.assertEqual(pop.inspect(CONTEXT,population)['status'],'invalid')

    def test_missing_values_do_not_erase_known_count(self):
        missing=row('a');missing['remaining']=pop.unknown('Unreadable amount');missing['due']=pop.unknown('No terms')
        result=pop.inspect(CONTEXT,{'status':'complete','rows':[missing]})
        self.assertEqual(result['claim_count'],pop.known(1))
        self.assertEqual(result['gross_remaining']['status'],'unknown')
        self.assertEqual(result['contractual_due_terms']['status'],'unknown')
        missing['id']=pop.unknown('Unreadable ID')
        self.assertEqual(pop.inspect(CONTEXT,{'status':'complete','rows':[missing]})['claim_count']['status'],'unknown')

    def test_rounding_remains_conditional_and_does_not_resolve_population(self):
        body=pop.partial_state.fixture(view='annual')
        binding=next(b for b in body['bindings'] if b['id']=='annual.balance.receivables')
        binding['interpretation']={'mode':'assumed_rounding','assumption_id':'rounding-hypothesis'}
        body['assumptions']=[{'id':'rounding-hypothesis','rule':'nearest_ties_away_from_zero','quantum':'1/1',
            'provenance':'Explicit diagnostic hypothesis, not issuer policy','disposition':'proposed_not_admitted'}]
        result=pop.evaluate(body);r=next(p for p in result['populations'] if p['constraint_id']==binding['id'])
        self.assertEqual(r['source_constraint']['underlying_measurement'],
            {'status':'conditional_on_proposed_rounding','interval':{'lower':'66819/2','upper':'66821/2','lower_inclusive':True,'upper_inclusive':False}})
        self.assertEqual(r['population_view']['gross_remaining']['status'],'unknown')
        self.assertEqual(r['measurement_relation']['status'],'unresolved')

    def test_forged_completeness_lost_obligations_and_exactness_fail_replay(self):
        body=pop.partial_state.fixture();result=pop.evaluate(body);self.assertTrue(pop.verify(body,result))
        for change in [lambda r:r['populations'][0]['population_view']['population'].update(status='complete'),
                       lambda r:r['partial_state']['dependencies'].clear(),
                       lambda r:r['populations'][0]['measurement_relation'].update(status='exact'),
                       lambda r:r.update(posting_authorized=True)]:
            altered=deepcopy(result);change(altered);self.assertFalse(pop.verify(body,altered))

    def test_source_substitution_and_membership_override_refuse(self):
        body=pop.partial_state.fixture();body['bindings'][0]['context']['perimeter']='Different'
        with self.assertRaises(Exception):pop.evaluate(body)
        body=pop.partial_state.fixture();body['claims']={'status':'complete','rows':[]}
        with self.assertRaises(Exception):pop.evaluate(body)

if __name__=='__main__':unittest.main()
