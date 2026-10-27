from copy import deepcopy
from pathlib import Path
import importlib.util
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('overlap_examples',ROOT/'data/accounting-master/population-overlap-20261025/examples.py')
ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)
api=ex.overlap

class PopulationOverlapTests(unittest.TestCase):
    def test_declared_cases_and_semantic_replay(self):
        for name,(body,budget,status) in ex.cases().items():
            with self.subTest(name=name):
                old=deepcopy(body);r=api.assess(body,budget)
                self.assertEqual(r['status'],status,r.get('reason'))
                self.assertTrue(api.verify_result(body,budget,r),name)
                self.assertEqual(body,old)

    def test_distinct_exact_witnesses_do_not_identify_membership(self):
        cases=ex.cases()
        for name,witnesses in ex.explicit_witnesses().items():
            body,budget,_=cases[name];result=api.assess(body,budget)
            for w in witnesses:
                api.joint.check_witness(result['definition'],w)
                r=deepcopy(result);r['joint_result']['witness']=w
                self.assertTrue(api.verify_result(body,budget,r))
                self.assertEqual(r['membership_identity'],'unresolved')
            self.assertNotEqual(witnesses[0],witnesses[1])

    def test_restricted_dimension_survives_formal_projection(self):
        body=ex.fixture('2024',True,True);r=api.assess(body,ex.BUDGET)
        self.assertEqual(r['source_dimensions']['R'],{
            'us-gaap:LossContingenciesByNatureOfContingencyAxis':
            'aapl:UnfavorableInvestigationOutcomeEUStateAidRulesMember'})
        self.assertEqual(r['definition']['observations']['population:R']['interval'],ex.interval(2550,2650,True,False))
        for key in ['001','011']:
            self.assertEqual(r['joint_result']['witness']['region:'+key],'0/1')

    def test_rounding_endpoints_and_nonnegative_region_values(self):
        b=ex.fixture(rounded=True);d,_=api.lower(b)
        w=deepcopy(ex.explicit_witnesses()['2023_unknown_overlap'][0])
        w.update({'population:B':'59929/2','region:11':'59929/2','region:01':'1545/2'})
        self.assertTrue(api.joint.check_witness(d,w))
        w.update({'population:B':'59931/2','region:11':'59931/2','region:01':'1543/2'})
        with self.assertRaises(ValueError):api.joint.check_witness(d,w)
        b['regions']['10']['interval']['lower']='-1/1'
        self.assertEqual(api.assess(b,ex.BUDGET)['reason'],'negative_region_value')

    def test_missing_premises_do_not_hide_invalid_numeric_input(self):
        b=ex.fixture();b['valuation_premise']=None
        self.assertEqual(api.assess(b,ex.BUDGET)['status'],'unresolved')
        b['regions']['10']['interval']['upper']='1.5'
        self.assertEqual(api.assess(b,ex.BUDGET)['status'],'invalid')

    def test_complete_regions_limits_and_closed_schema(self):
        for mutate in [lambda b:b['regions'].pop('11'),
                       lambda b:b['regions'].update({'00':deepcopy(b['regions']['10'])}),
                       lambda b:b.update(source_admission=True),
                       lambda b:b['populations']['B'].update(legal_account='cash'),
                       lambda b:b['populations']['B']['measurement']['type'].update(scale='1/1')]:
            b=ex.fixture();mutate(b)
            self.assertEqual(api.assess(b,ex.BUDGET)['status'],'invalid')
        with self.assertRaises(ValueError):api.region_keys(5)

    def test_duplicate_premise_identity_cannot_change_meaning(self):
        b=ex.fixture();b['populations']['F']['projection_premise']['id']='projection.B'
        b['populations']['F']['projection_premise']['meaning']='A conflicting assumption.'
        self.assertEqual(api.assess(b,ex.BUDGET)['reason'],'conflicting_premise_identity')

    def test_forged_sources_equations_regions_and_admission_refuse(self):
        b=ex.fixture();r=api.assess(b,ex.BUDGET)
        for mutate in [lambda x:x.update(source_admission=True),
                       lambda x:x.update(membership_identity='equal'),
                       lambda x:x['definition']['equations'].pop(),
                       lambda x:x['source_dimensions'].update(B={'fake':'member'}),
                       lambda x:x['joint_result']['witness'].update({'region:11':'40001/1'}),
                       lambda x:x['joint_result'].update(solver_wall_seconds=float('nan'))]:
            bad=deepcopy(r);mutate(bad);self.assertFalse(api.verify_result(b,ex.BUDGET,bad))

    def test_no_actual_opening_or_posting_authority(self):
        r=api.assess(ex.fixture(),ex.BUDGET)
        for k in ['executed','source_admission','accounting_admission','posting_authorized']:
            self.assertIs(r[k],False)
        self.assertIsNone(r['executable_opening'])
        self.assertEqual(r['actual_history'],'unknown')

    def test_infeasible_conflict_is_rechecked_not_trusted(self):
        b,u,_=ex.cases()['2023_assumed_equal_populations'];r=api.assess(b,u)
        for mutate in [lambda x:x['joint_result']['conflicts'][0].update(labels=['domain:population:B']),
                       lambda x:x['joint_result']['conflicts'][0].update(labels=['made_up']),
                       lambda x:x['joint_result']['conflicts'][0].update(minimal=True)]:
            bad=deepcopy(r);mutate(bad);self.assertFalse(api.verify_result(b,u,bad))

    def test_four_populations_have_complete_bounded_boolean_expansion(self):
        b=ex.fixture('2024')
        for name in ['C','D']:
            b['populations'][name]=deepcopy(b['populations']['B'])
        b['regions']={k:{'interval':ex.interval(0,40000),
            'bound_premise':ex.premise('bound.'+k,'Authored upper bound; no member identity.')}
            for k in api.region_keys(4)}
        d,meta=api.lower(b)
        self.assertEqual(len(meta['region_order']),15)
        self.assertEqual(len(d['observations']),19)
        self.assertTrue(all(len(eq['terms'])==9 for eq in d['equations']))
        r=api.assess(b,ex.BUDGET)
        self.assertEqual(r['status'],'conditionally_feasible')
        self.assertTrue(api.verify_result(b,ex.BUDGET,r))

if __name__=='__main__':unittest.main()
