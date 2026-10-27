"""Temporal roles must be valid before any scalar feasibility question."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import sys, unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import temporal_measurement_constraints_v1 as temporal
from test_joint_measurement_constraints_v1 import BUDGET, premise

VALUE={'kind':'rational','context':{'issuer':'Example','perimeter':'consolidated','basis':'authored'},
       'dimensions':{'currency:USD':1},'scale':'1000000/1'}
PERIOD={'kind':'period','start':'2024-01-01','end_exclusive':'2025-01-01'}


def observation(amount,when,quantity='cash_population'):
    return {'type':{'value_type':deepcopy(VALUE),'time':deepcopy(when),'quantity':quantity},
            'interval':{'lower':amount,'upper':amount,'lower_inclusive':True,'upper_inclusive':True},
            'interval_premise':premise('constructed_exact_values'),'source_ref':'constructed:test'}


def fixture():
    return {'profile':temporal.PROFILE,'observations':{
        'opening':observation('10/1',{'kind':'instant','at':'2023-12-31'}),
        'change':observation('-3/1',PERIOD,'period_cash_change'),
        'closing':observation('7/1',{'kind':'instant','at':'2024-12-31'})},
        'relations':[{'id':'cash_bridge','kind':'stock_flow','period':deepcopy(PERIOD),
            'opening':'opening','movements':[{'observation':'change','coefficient':'1/1'}],
            'closing':'closing','identity_premise':premise('cash_bridge_identity')}]}


class TemporalMeasurementTests(unittest.TestCase):
    def test_exact_bridge_retains_times_and_signed_arithmetic(self):
        definition=fixture();before=deepcopy(definition);result=temporal.assess(definition,BUDGET)
        self.assertEqual(result['status'],'conditionally_feasible',result)
        self.assertEqual(definition,before);self.assertEqual(result['definition'],before)
        values={k:Q(v) for k,v in result['joint_assessment']['witness'].items()}
        self.assertEqual(values['opening']+values['change'],values['closing'])
        self.assertEqual(result['numeric_definition']['equations'][0]['terms'],[
            {'observation':'opening','coefficient':'1/1'},
            {'observation':'change','coefficient':'1/1'},
            {'observation':'closing','coefficient':'-1/1'}])
        self.assertEqual([r['role'] for r in result['lowering'][0]['roles']],['opening','period_movement','closing'])

    def test_wrong_dates_and_roles_reject_even_when_arithmetic_balances(self):
        for key,when in [('opening',{'kind':'instant','at':'2024-01-01'}),
                         ('closing',{'kind':'instant','at':'2025-01-01'}),
                         ('change',{'kind':'period','start':'2024-01-02','end_exclusive':'2025-01-01'}),
                         ('change',{'kind':'instant','at':'2024-12-31'})]:
            d=fixture();d['observations'][key]['type']['time']=when
            self.assertEqual(temporal.assess(d,BUDGET)['status'],'invalid')
        d=fixture();r=d['relations'][0];r['opening'],r['closing']=r['closing'],r['opening']
        self.assertEqual(temporal.assess(d,BUDGET)['status'],'invalid')

    def test_economic_and_population_mismatches_reject(self):
        for field,value in [('issuer','Other'),('perimeter','legal book'),('basis','another basis')]:
            d=fixture();d['observations']['closing']['type']['value_type']['context'][field]=value
            self.assertEqual(temporal.assess(d,BUDGET)['status'],'invalid')
        for field,value in [('scale','1/1'),('dimensions',{'currency:EUR':1})]:
            d=fixture();d['observations']['change']['type']['value_type'][field]=value
            self.assertEqual(temporal.assess(d,BUDGET)['status'],'invalid')
        d=fixture();d['observations']['closing']['type']['quantity']='available_legal_cash'
        self.assertEqual(temporal.assess(d,BUDGET)['status'],'invalid')

    def test_same_time_relations_preserve_shared_variables(self):
        d=fixture();d['observations']['other']=observation('7/1',{'kind':'instant','at':'2024-12-31'},'other_reported_total')
        d['relations'].append({'id':'same_closing','kind':'same_time',
            'terms':[{'observation':'closing','coefficient':'1/1'},{'observation':'other','coefficient':'-1/1'}],
            'rhs':'0/1','identity_premise':premise('same_population')})
        self.assertEqual(temporal.assess(d,BUDGET)['status'],'conditionally_feasible')
        d['observations']['other']['type']['time']['at']='2024-12-30'
        self.assertEqual(temporal.assess(d,BUDGET)['status'],'invalid')

    def test_shared_closing_constraint_detects_joint_conflict(self):
        d=fixture();d['relations'].append({'id':'incompatible_closing','kind':'same_time',
            'terms':[{'observation':'closing','coefficient':'1/1'}], 'rhs':'8/1',
            'identity_premise':premise('counterexample')})
        r=temporal.assess(d,BUDGET);self.assertEqual(r['status'],'conditionally_infeasible')
        self.assertTrue(all(c['rechecked']=='unsat' for c in r['joint_assessment']['conflicts']))

    def test_missing_premises_unresolved_after_structure_checks(self):
        for key in ['identity','interval']:
            d=fixture()
            if key=='identity':d['relations'][0]['identity_premise']=None
            else:d['observations']['opening']['interval_premise']=None
            self.assertEqual(temporal.assess(d,BUDGET)['status'],'unresolved')
            d['observations']['opening']['type']['time']['at']='2024-01-02'
            self.assertEqual(temporal.assess(d,BUDGET)['status'],'invalid')

    def test_temporal_fields_cannot_be_hidden_in_value_context(self):
        for field in ['instant','period','measurement_kind']:
            d=fixture()
            for o in d['observations'].values():o['type']['value_type']['context'][field]='hidden'
            self.assertEqual(temporal.assess(d,BUDGET)['status'],'invalid')

    def test_original_joint_profile_still_rejects_different_contexts(self):
        from test_joint_measurement_constraints_v1 import definition,obs,equation
        a=obs();b=obs();b['type']['context']['at']='2024-12-28'
        d=definition({'a':a,'b':b},[equation('mixed',[('a','1/1'),('b','-1/1')])])
        self.assertEqual(temporal.joint.assess(d,BUDGET)['status'],'invalid')

    def test_empty_reversed_noncanonical_and_boundary_dates(self):
        for start,end in [('2025-01-01','2025-01-01'),('2025-01-01','2024-01-01'),
                          ('20240101','2025-01-01'),('0001-01-01','0002-01-01')]:
            d=fixture();d['relations'][0]['period'].update(start=start,end_exclusive=end)
            self.assertEqual(temporal.assess(d,BUDGET)['status'],'invalid')

    def test_duplicate_unknown_and_swapped_observation_roles(self):
        for field,value in [('opening','missing'),('closing','opening'),('movements',[{'observation':'opening','coefficient':'1/1'}])]:
            d=fixture();d['relations'][0][field]=value
            self.assertEqual(temporal.assess(d,BUDGET)['status'],'invalid')
        d=fixture();d['relations'].append(deepcopy(d['relations'][0]))
        self.assertEqual(temporal.assess(d,BUDGET)['status'],'invalid')

    def test_signed_fractional_movement_and_strict_endpoint(self):
        d=fixture();d['observations']['change']['interval'].update(lower='6/1',upper='6/1')
        d['relations'][0]['movements'][0]['coefficient']='-1/2'
        self.assertEqual(temporal.assess(d,BUDGET)['status'],'conditionally_feasible')
        d['observations']['closing']['interval'].update(lower='7/1',upper='8/1',lower_inclusive=False)
        self.assertEqual(temporal.assess(d,BUDGET)['status'],'conditionally_infeasible')

    def test_resources_and_forged_witness_remain_distinct(self):
        d=fixture();r=temporal.assess(d,{**BUDGET,'max_cells':0})
        self.assertEqual(r['status'],'unknown')
        with self.assertRaises(ValueError):temporal.check_witness(d,BUDGET,{'opening':'10/1','change':'-3/1','closing':'8/1'})
        self.assertFalse(r['executed']);self.assertIsNone(r['executable_opening'])


if __name__=='__main__':unittest.main()
