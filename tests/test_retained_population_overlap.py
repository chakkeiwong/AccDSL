from copy import deepcopy
from pathlib import Path
import importlib.util
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'data/accounting-master/retained-population-overlap-20261025'
sys.path.insert(0,str(FOLDER));sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('retained_overlap_examples',FOLDER/'examples.py')
ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)
api=ex.compose

class RetainedPopulationOverlapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request,cls.groups=ex.fixture()
        cls.result=api.assess(cls.request,cls.groups,ex.BUDGET)
        assert cls.result['status']=='conditionally_feasible',cls.result.get('reason')

    def test_source_observations_relations_and_report_survive(self):
        r=self.result;p=r['source_result'];d=r['definition'];old=p['definition']
        self.assertEqual((len(old['observations']),len(old['relations'])),(114,38))
        self.assertEqual((len(d['observations']),len(d['relations'])),(120,42))
        self.assertEqual(len(p['preserved_report']['observations']),256)
        self.assertEqual(len(p['preserved_report']['relations']),143)
        self.assertEqual(d['relations'][:38],old['relations'])
        self.assertTrue(all(d['observations'][k]==v for k,v in old['observations'].items()))
        self.assertTrue(api.verify(self.request,self.groups,ex.BUDGET,r))

    def test_all_declared_statuses_replay(self):
        for name,(s,g,b,status) in ex.cases().items():
            with self.subTest(name=name):
                result=api.assess(s,g,b)
                self.assertEqual(result['status'],status,result.get('reason'))
                self.assertTrue(api.verify(s,g,b,result),name)

    def test_distinct_regions_preserve_all_source_equations(self):
        for extra in [0,100]:
            witness=ex.alternative_witness(self.result,extra)
            self.assertTrue(api.temporal.check_witness(self.result['definition'],ex.BUDGET,witness))
            changed=deepcopy(self.result);changed['assessment']['joint_assessment']['witness']=witness
            self.assertTrue(api.verify(self.request,self.groups,ex.BUDGET,changed))

    def test_unknown_source_or_cross_context_refuses(self):
        for other in ['not_an_observation',next(k for k,v in self.result['source_result']['source_mapping'].items()
                       if 'interim.cash_flow.opening' in v['aliases'])]:
            groups=deepcopy(self.groups);groups['opening']['observations']['F']=other
            self.assertEqual(api.assess(self.request,groups,ex.BUDGET)['status'],'invalid')

    def test_dropping_original_equations_or_changing_source_refuses(self):
        for mutate in [lambda r:r['definition']['relations'].pop(0),
                       lambda r:r['source_result']['preserved_report']['relations'].pop(),
                       lambda r:r['groups']['opening']['retained_source_mappings']['B'].update(literal='0'),
                       lambda r:r.update(accounting_admission=True),
                       lambda r:r.update(executable_opening={})]:
            bad=deepcopy(self.result);mutate(bad)
            self.assertFalse(api.verify(self.request,self.groups,ex.BUDGET,bad))

    def test_source_intervals_and_proposed_regions_are_distinct(self):
        r=self.result;group=r['groups']['opening']
        for n,oid in group['source_ids'].items():
            self.assertEqual(r['definition']['observations'][oid],r['source_result']['definition']['observations'][oid])
        for key in ['region:01','region:10','region:11']:
            row=r['definition']['observations'][group['rename'][key]]
            self.assertTrue(row['source_ref'].startswith('constructed_boolean_region:'))
            self.assertEqual(row['type']['time'],{'kind':'instant','at':'2023-09-30'})
        self.assertFalse(r['source_admission']);self.assertIsNone(r['executable_opening'])

if __name__=='__main__':unittest.main()
