"""Global bounds, exact endpoints and complete native replay."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import json,sys,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import sequential_outcome_range_v1 as ranges
from test_sequential_outcome_query_v1 import fixture as predicate,profit as profit_predicate,observation,BUDGET
from test_conditional_history_family_v1 import domain

def fixture(prefix=2):
    d=predicate(prefix);d['profile']=ranges.PROFILE
    for key in ['operator','threshold']:d.pop(key)
    return d

def profit(prefix=2):
    d=fixture(prefix);d['terms']=profit_predicate(prefix)['terms'];return d

def empty():
    d=fixture();s=d['family']['first_family']['state'];cash=Q(s['balances']['cash']);s['balances']['cash']='1/1'
    s['balances']['original_equity']=ranges.native.monetary.fmt(Q(s['balances']['original_equity'])+cash-1);return d

def variable_proceeds():
    d=profit();d['family']['sale_event']['proceeds']='unknown'
    d['family']['proceeds_domain']=domain('0/1','100/1')
    d['family']['proceeds_domain']['source_ref']=ranges.family.parent.source_ref(ranges.core.digest(d['family']['sale_event']),'/proceeds')
    return d

class SequentialOutcomeRangeTests(unittest.TestCase):
    def answer(self,d,b=BUDGET):
        r=ranges.assess(d,b);self.assertIn(r['status'],['conditional_outcome_range','candidate_outcome_range'],r);return r

    def bounds(self,d,lo,hi,lc=True,hc=True):
        r=self.answer(d);self.assertEqual(r['range']['status'],'finite_envelope');self.assertTrue(r['range']['globally_certified'])
        for side,v,attained in [('lower',lo,lc),('upper',hi,hc)]:
            self.assertEqual(r['range']['bounds'][side]['value'],v)
            self.assertEqual(r['range']['bounds'][side]['attained'],attained)
        return r

    def test_intermediate_inventory_global_bounds(self):
        d=fixture(1);before=deepcopy(d);r=self.bounds(d,'65/1','80/1');self.assertEqual(d,before)
        self.assertEqual(r['range']['bounds']['lower']['supporting_branches'],[1])
        self.assertEqual(r['range']['bounds']['upper']['supporting_branches'],[0,1])
        self.assertEqual(r['range']['bounds']['upper']['attaining_branches'],[0])
        self.assertTrue(ranges.verify_result(d,BUDGET,json.loads(json.dumps(r))))

    def test_terminal_inventory_and_profit_singletons(self):
        self.bounds(fixture(),'60/1','60/1');self.bounds(profit(),'16/1','16/1')

    def test_intermediate_profit_range(self):self.bounds(profit(1),'-19/1','-4/1')

    def test_open_endpoints_have_no_witness(self):
        d=fixture(1);d['family']['first_family']['event_domains']['inventory_nrv']['interval'].update(upper='20/1',lower_inclusive=False,upper_inclusive=False)
        r=self.bounds(d,'65/1','80/1',False,False)
        for e in r['branches'][1]['bounds'].values():self.assertIsNone(e['witness']);self.assertIsNone(e['replay'])
        self.assertTrue(ranges.verify_result(d,BUDGET,r))

    def test_one_open_endpoint_and_closed_tie(self):
        d=fixture(1);d['family']['first_family']['event_domains']['inventory_nrv']['interval']['lower_inclusive']=False
        self.bounds(d,'65/1','80/1',False,True)

    def test_observation_selects_nonfirst_branch(self):
        d=fixture(1);d['family']['observations']=[observation(d['family'],1,'inventory','65/1')]
        r=self.bounds(d,'65/1','65/1');self.assertEqual(r['branches'][0]['status'],'infeasible')

    def test_variable_sale_proceeds_keep_full_profit_range(self):self.bounds(variable_proceeds(),'-24/1','76/1')

    def test_empty_family_has_no_bounds(self):
        d=empty();r=self.answer(d);self.assertEqual(r['range']['status'],'empty_family')
        self.assertIsNone(r['range']['bounds']);self.assertFalse(r['range']['nonempty']);self.assertTrue(ranges.verify_result(d,BUDGET,r))

    def test_first_branch_bounds_never_global(self):
        r=self.answer(fixture(1),{**BUDGET,'max_cells':1})
        self.assertTrue(r['range']['nonempty']);self.assertFalse(r['range']['globally_certified'])
        self.assertIsNone(r['range']['bounds']);self.assertEqual(r['branches'][0]['bounds']['lower']['value'],'80/1')
        self.assertEqual(r['branches'][1]['status'],'unvisited')

    def test_zero_resources_remain_unknown(self):
        for key in ['max_cells','elapsed_ms','max_integer_assignments','solver_timeout_ms','solver_rlimit','max_formula_nodes']:
            r=self.answer(fixture(),{**BUDGET,key:0});self.assertEqual(r['range']['status'],'unknown',key)
            self.assertFalse(r['range']['globally_certified'])

    def test_branch_limit_and_missing_premise_preserve_status(self):
        d=fixture();d['family']['first_family']['branch_limit']=1
        self.assertEqual(ranges.assess(d,BUDGET)['status'],'unknown')
        d=fixture();d['family']['premise']=None;r=ranges.assess(d,BUDGET)
        self.assertEqual(r['status'],'unresolved');self.assertFalse(r['formulation_complete'])

    def test_candidate_obligation_cannot_admit_actual_outcome(self):
        d=fixture();d['family']['obligations']=[{'id':'source','meaning':'actual source unknown','affects':['history']}]
        r=self.bounds(d,'60/1','60/1');self.assertEqual(r['status'],'candidate_outcome_range')
        self.assertEqual(r['actual_outcome'],'unknown');self.assertFalse(r['formulation_complete'])

    def test_original_native_findings_remain_distinct(self):
        for value,status in [(False,'unsupported'),('unknown','unresolved')]:
            d=fixture();d['family']['sale_event']['performance_complete']=value
            self.assertEqual(ranges.assess(d,BUDGET)['status'],status)

    def test_type_terms_and_extra_query_fields_reject(self):
        edits=[lambda d:d.update(prefix=True),lambda d:d.update(operator='eq'),lambda d:d.update(terms=[]),
          lambda d:d['terms'].append(deepcopy(d['terms'][0])),lambda d:d['type'].update(scale='1000/1'),
          lambda d:d['type']['context'].update(at='2025-03-01'),lambda d:d['terms'][0].update(coefficient='2/2')]
        for edit in edits:
            d=fixture();edit(d);self.assertEqual(ranges.assess(d,BUDGET)['status'],'invalid')

    def test_alternative_valid_endpoint_witness_is_accepted(self):
        d=fixture();r=self.answer(d);e=r['branches'][0]['bounds']['lower'];e['witness']['nrv']='25/1'
        e['replay']=ranges.replay_value(d,BUDGET,0,e['witness'])
        self.assertTrue(ranges.verify_result(d,BUDGET,json.loads(json.dumps(r))))

    def test_forged_bound_attainment_state_and_coverage_reject(self):
        d=fixture(1);r=self.answer(d)
        for field in ['bound','attainment','state','coverage','proof']:
            bad=deepcopy(r);e=bad['branches'][0]['bounds']['lower']
            if field=='bound':e['value']='79/1'
            elif field=='attainment':e['attained']=False
            elif field=='state':e['replay']['original_complete_replay']['after']['balances']['cash']='0/1'
            elif field=='coverage':bad['coverage']['complete']=False
            else:e['proof']['no_better']='sat'
            self.assertFalse(ranges.verify_result(d,BUDGET,bad),field)

    def test_false_infeasibility_core_rejects(self):
        d=empty();r=self.answer(d);r['branches'][0]['conflict']['labels']=['sale:proceeds_nonnegative']
        self.assertFalse(ranges.verify_result(d,BUDGET,r))

    def test_unknown_proof_prevents_certification(self):
        with patch.object(ranges,'proof_checks',return_value={'closure_endpoint':'sat','no_better':'unknown','attainment':'sat'}):
            r=self.answer(fixture());self.assertTrue(r['range']['nonempty']);self.assertFalse(r['range']['globally_certified'])

    def test_impossible_infinity_is_vetoed(self):
        original=ranges.solver.solve
        def wrong(*args,**kwargs):
            r=original(*args,**kwargs)
            for cell in r['cells']:
                if cell['feasibility']=='sat':cell['bounds']['upper']['status']='Unbounded'
            return r
        with patch.object(ranges.solver,'solve',side_effect=wrong):
            r=ranges.assess(fixture(),BUDGET)
            self.assertEqual(r['status'],'invalid');self.assertEqual(r['reason'],'unbounded_in_finite_fragment')

if __name__=='__main__':unittest.main()
