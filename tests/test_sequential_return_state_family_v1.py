"""Do not select an intermediate witness or lose shared carrying cost."""
from copy import deepcopy
from pathlib import Path
from fractions import Fraction as Q
import sys,json,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import sequential_return_state_family_v1 as sequence
from test_conditional_return_state_family_v2 import fixture as first_fixture
from test_typed_return_transition_v1 import fixtures
from test_conditional_history_family_v1 import domain
from test_joint_measurement_constraints_v1 import premise
from test_piecewise_method_family_v1 import BUDGET


def fixture(variable_sale=False):
    first=first_fixture();_,_,sale=next(x for x in fixtures.selected_cases() if x[2]['kind']=='sell')
    sale=deepcopy(sale);sale['date']=first['event']['date'];sale['lot_id']=first['event']['lot_id']
    proceeds=None
    if variable_sale:
        sale['proceeds']='unknown';proceeds=domain('0/1','100/1')
        proceeds['source_ref']=sequence.parent.source_ref(sequence.core.digest(sale),'/proceeds')
    return {'profile':sequence.PROFILE,'first_family':first,'sale_event':sale,'proceeds_domain':proceeds,
            'premise':premise('same_created_lot_sale'),'observations':[],'obligations':[]}


def observation(d,prefix,account,value,upper=None):
    first=d['first_family'];date=first['event']['date'] if prefix==1 else d['sale_event']['date']
    typ={'kind':'rational','context':{'entity':first['state']['context']['entity'],'book_role':'legal','at':date},
         'dimensions':{'currency:USD':1},'scale':'1/1'}
    return {'id':'observed_'+str(prefix)+'_'+account,'prefix':prefix,'account':account,'type':typ,'domain':domain(value,upper)}


class SequentialReturnStateFamilyTests(unittest.TestCase):
    def test_both_intermediate_states_survive_and_terminal_states_converge(self):
        d=fixture();before=deepcopy(d);r=sequence.assess(d,BUDGET)
        self.assertEqual(r['status'],'conditional_sequence_family_witness',r)
        self.assertEqual(r['coverage']['feasible'],2);self.assertEqual(d,before)
        replays=[b['replay'] for b in r['branches']]
        self.assertNotEqual(replays[0]['sale_cost'],replays[1]['sale_cost'])
        self.assertEqual(replays[0]['after'],replays[1]['after'])
        for p in replays:
            self.assertEqual(p['sale_cost'],p['first']['after']['lots'][d['sale_event']['lot_id']]['carrying'])
            self.assertTrue(p['both_event_transitions_checked']);self.assertFalse(p['committed'])
        self.assertTrue(sequence.verify_result(d,BUDGET,r))

    def test_intermediate_observation_excludes_first_witness_only(self):
        d=fixture();d['observations']=[observation(d,1,'inventory','65/1')]
        r=sequence.assess(d,BUDGET);self.assertEqual(r['status'],'conditional_sequence_family_witness',r)
        self.assertEqual([b['status'] for b in r['branches']],['infeasible','feasible'])
        b=r['branches'][1];self.assertEqual(b['replay']['sale_cost'],'5/1')
        self.assertEqual(b['replay']['observation_values']['observed_1_inventory'],'65/1')

    def test_terminal_only_observation_retains_both_paths(self):
        d=fixture();d['observations']=[observation(d,2,'inventory','60/1')]
        r=sequence.assess(d,BUDGET);self.assertEqual(r['coverage']['feasible'],2)

    def test_unknown_sale_proceeds_constrained_by_terminal_cash(self):
        d=fixture(True);base=fixture();known=sequence.assess(base,BUDGET)
        cash=known['branches'][0]['replay']['after']['balances']['cash']
        d['observations']=[observation(d,2,'cash',cash)]
        r=sequence.assess(d,BUDGET);self.assertEqual(r['status'],'conditional_sequence_family_witness',r)
        for b in r['branches']:self.assertEqual(b['witness'][sequence.SALE_KEY],base['sale_event']['proceeds'])
        self.assertEqual(d['sale_event']['proceeds'],'unknown')

    def test_sale_cannot_rescue_unfunded_intermediate_settlement(self):
        d=fixture();s=d['first_family']['state'];cash=Q(s['balances']['cash'])
        s['balances']['cash']='1/1';s['balances']['original_equity']=sequence.native.monetary.fmt(Q(s['balances']['original_equity'])+cash-1)
        d['sale_event']['proceeds']='1000/1'
        r=sequence.assess(d,BUDGET);self.assertEqual(r['status'],'conditionally_infeasible',r)
        self.assertTrue(sequence.verify_result(d,BUDGET,r))

    def test_wrong_lot_duplicate_identity_and_chronology_reject(self):
        for mutate in [lambda d:d['sale_event'].update(lot_id='wrong'),
                       lambda d:d['sale_event'].update(id=d['first_family']['event']['id']),
                       lambda d:d['sale_event'].update(date='2025-01-31'),
                       lambda d:d['sale_event'].update(date='2026-01-01'),
                       lambda d:d['sale_event'].update(method='returns.settle')]:
            d=fixture();mutate(d);self.assertEqual(sequence.assess(d,BUDGET)['status'],'invalid')

    def test_unknown_and_false_sale_facts_keep_status(self):
        for field,value,status in [('performance_complete','unknown','unresolved'),
                                   ('performance_complete',False,'unsupported'),
                                   ('fraction','unknown','unresolved'),('fraction','1/2','unsupported')]:
            d=fixture();d['sale_event'][field]=value;self.assertEqual(sequence.assess(d,BUDGET)['status'],status)

    def test_missing_and_conflicting_sequence_premises(self):
        d=fixture();d['premise']=None;r=sequence.assess(d,BUDGET)
        self.assertEqual(r['status'],'unresolved');self.assertFalse(r['formulation_complete'])
        self.assertIn('sequence_premise',r['missing_premises'])
        d=fixture();d['observations']=[observation(d,1,'inventory','65/1')];d['observations'][0]['domain']['premise']=None
        self.assertEqual(sequence.assess(d,BUDGET)['status'],'unresolved')
        d=fixture();d['premise']=deepcopy(d['first_family']['premise']);d['premise']['meaning']='changed'
        self.assertEqual(sequence.assess(d,BUDGET)['status'],'invalid')

    def test_wrong_observation_types_prefixes_and_known_domain_reject(self):
        for mutate in [lambda r:r.update(prefix=0),lambda r:r['type']['context'].update(at='2024-01-01'),
                       lambda r:r['type'].update(scale='1000/1'),lambda r:r.update(account='missing')]:
            d=fixture();o=observation(d,1,'inventory','65/1');mutate(o);d['observations']=[o]
            self.assertEqual(sequence.assess(d,BUDGET)['status'],'invalid')
        d=fixture();d['proceeds_domain']=domain('0/1','100/1')
        self.assertEqual(sequence.assess(d,BUDGET)['status'],'invalid')

    def test_budgets_and_first_constraints_survive(self):
        d=fixture();d['observations']=[observation(d,1,'inventory','65/1')]
        r=sequence.assess(d,{**BUDGET,'max_cells':1});self.assertEqual(r['status'],'unknown',r)
        self.assertEqual(r['branches'][1]['status'],'unvisited')
        for field in ['max_cells','elapsed_ms','solver_timeout_ms','solver_rlimit']:
            self.assertEqual(sequence.assess(fixture(),{**BUDGET,field:0})['status'],'unknown')
        d=fixture();d['first_family']['branch_limit']=1
        self.assertEqual(sequence.assess(d,BUDGET)['status'],'unknown')

    def test_obligations_preserve_actual_target_unknown(self):
        d=fixture();d['first_family']['obligations']=[{'id':'source','meaning':'No source admission','affects':['history']}]
        d['obligations']=[{'id':'sequence','meaning':'No actual lot continuity','affects':['execution']}]
        r=sequence.assess(d,BUDGET);self.assertEqual(r['status'],'candidate_sequence_with_unresolved_obligations')
        self.assertEqual(len(r['target_obligations']),2);self.assertEqual(r['target_existence'],'unknown')

    def test_json_roundtrip_and_alternate_witness(self):
        d=fixture();r=sequence.assess(d,BUDGET);self.assertTrue(sequence.verify_result(d,BUDGET,json.loads(json.dumps(r))))
        b=r['branches'][0];b['witness']['nrv']='25/1';b['replay']=sequence.replay_witness(d,BUDGET,0,b['witness'])
        self.assertTrue(sequence.verify_result(d,BUDGET,json.loads(json.dumps(r))))

    def test_forged_intermediate_final_and_cost_reject(self):
        d=fixture();r=sequence.assess(d,BUDGET)
        for mutate in [lambda x:x.update(committed=True),lambda x:x['branches'][0]['replay'].update(sale_cost='999/1'),
                       lambda x:x['branches'][0]['replay']['after']['balances'].update(cash='999/1'),
                       lambda x:x['sequence_compilation']['cost_lineage'].update(lot_id='wrong')]:
            bad=deepcopy(r);mutate(bad);self.assertFalse(sequence.verify_result(d,BUDGET,bad))

    def test_later_sale_date_and_explicit_context_continuity(self):
        d=fixture();d['sale_event']['date']='2025-03-01'
        d['observations']=[observation(d,2,'inventory','60/1')]
        r=sequence.assess(d,BUDGET);self.assertEqual(r['status'],'conditional_sequence_family_witness',r)
        lineage=r['sequence_compilation']['cost_lineage']
        self.assertEqual((lineage['from_date'],lineage['to_date']),('2025-02-01','2025-03-01'))
        self.assertEqual(r['branches'][0]['replay']['after']['date'],'2025-03-01')

    def test_negative_proceeds_and_strict_observation_empty(self):
        d=fixture();d['sale_event']['proceeds']='-1/1'
        self.assertEqual(sequence.assess(d,BUDGET)['status'],'conditionally_infeasible')
        d=fixture();o=observation(d,2,'inventory','60/1','61/1');o['domain']['interval']['lower_inclusive']=False
        d['observations']=[o];self.assertEqual(sequence.assess(d,BUDGET)['status'],'conditionally_infeasible')

    def test_all_new_premises_retained_and_maps_not_shared_between_arms(self):
        d=fixture();d['observations']=[observation(d,1,'inventory','65/1','80/1')]
        r=sequence.assess(d,BUDGET)
        self.assertIn(d['premise']['id'],r['premises'])
        self.assertIn(d['observations'][0]['domain']['premise']['id'],r['premises'])
        branches,_,_,_,_,_=sequence.compile_selection(d,BUDGET)
        self.assertIsNot(branches[0]['problem'].variables,branches[1]['problem'].variables)
        self.assertEqual(set(branches[0]['problem'].variables),set(branches[1]['problem'].variables))


if __name__=='__main__':unittest.main()
