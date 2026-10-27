"""Exact method-family comparisons, disjoint minimum arms and resource boundaries."""
from copy import deepcopy
from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import piecewise_method_family_v1 as family
from test_method_monetary_effects_v1 import fixture as method_fixture,examples
from test_conditional_history_family_v1 import domain

BUDGET={'max_slots':0,'max_formula_nodes':10000,'max_integer_assignments':1,
        'max_cells':16,'elapsed_ms':5000,'solver_timeout_ms':1000,'solver_rlimit':1000000}

def fixture(variable=True):
    method,values=method_fixture()
    domains={key:domain(item['value']) for key,item in values.items()}
    if variable:domains['nrv']=domain('5/1','25/1')
    return {'profile':family.PROFILE,'method':method,'selected_method_digest':family.core.digest(method),
            'domains':domains,'measurements':[],'obligations':[],'branch_limit':16}

def measure(d,category,target,low,high=None):
    method=d['method']
    typ=(next(r['type'] for r in method['calculations'] if r['id']==target) if category=='calculation'
         else method['accounts'][method['cash_account']])
    d['measurements'].append({'id':'measurement.'+str(len(d['measurements'])),
        'category':category,'target':target,'type':deepcopy(typ),'domain':domain(low,high)})


class PiecewiseMethodFamilyTests(unittest.TestCase):
    def test_fixed_inputs_match_original_method_exactly(self):
        d=fixture(False);before=deepcopy(d);r=family.assess(d,BUDGET)
        self.assertEqual(r['status'],'conditional_family_witness',r)
        self.assertEqual(r['coverage']['total'],1);self.assertTrue(r['coverage']['complete'])
        original=examples.run(d['method'],{k:{'status':'known','value':v['interval']['lower']} for k,v in d['domains'].items()})
        replay=r['branches'][0]['replay']
        self.assertEqual(replay['journal'],original['journal']);self.assertEqual(replay['flows'],original['flows'])
        self.assertEqual(d,before);self.assertTrue(family.verify_result(d,BUDGET,r))

    def test_variable_minimum_retains_both_feasible_arms(self):
        d=fixture();r=family.assess(d,BUDGET)
        self.assertEqual(r['status'],'conditional_family_witness',r)
        self.assertEqual(r['coverage'],{'total':2,'attempted':2,'feasible':2,'infeasible':0,'unresolved':0,'complete':True})
        self.assertEqual([b['decisions'][0]['arm'] for b in r['branch_manifest']],['left','right'])
        for b in r['branches']:
            self.assertEqual(b['replay'],family.replay_witness(d,BUDGET,b['index'],b['witness']))
        self.assertTrue(family.verify_result(d,BUDGET,r))

    def test_tie_has_one_arm_and_exact_value(self):
        d=fixture();measure(d,'calculation','carrying','20/1')
        r=family.assess(d,BUDGET)
        self.assertEqual([b['status'] for b in r['branches']],['feasible','infeasible'])
        w={k:v['interval']['lower'] for k,v in d['domains'].items()};w['nrv']='20/1'
        self.assertEqual(family.replay_witness(d,BUDGET,0,w)['calculations']['carrying'],'20/1')
        with self.assertRaises(ValueError):family.replay_witness(d,BUDGET,1,w)

    def test_unknown_quantity_with_fixed_prices_is_piecewise_affine(self):
        d=fixture();d['domains']['n']=domain('1/1','3/1')
        r=family.assess(d,BUDGET);self.assertEqual(r['status'],'conditional_family_witness',r)
        self.assertEqual(r['coverage']['feasible'],2)
        self.assertTrue(all(b['replay']['checked_exactly'] for b in r['branches']))

    def test_two_unknown_product_operands_stay_unsupported(self):
        d=fixture();d['domains']['n']=domain('1/1','3/1');d['domains']['p']=domain('10/1','20/1')
        r=family.assess(d,BUDGET)
        self.assertEqual(r['status'],'unsupported',r);self.assertIn('unknown_by_unknown_product',r['reason'])
        self.assertEqual(r['definition'],d);self.assertNotIn('branches',r)

    def test_missing_premise_stays_unresolved_before_compile(self):
        d=fixture();d['domains']['nrv']['premise']=None
        r=family.assess(d,BUDGET);self.assertEqual(r['status'],'unresolved')
        self.assertIn('input:nrv',r['missing_premises']);self.assertNotIn('branches',r)

    def test_unresolved_obligations_never_promote_target(self):
        d=fixture();d['obligations']=[{'id':'contract','meaning':'Native contract state missing','affects':['target_membership']}]
        r=family.assess(d,BUDGET);self.assertEqual(r['status'],'candidate_with_unresolved_obligations')
        self.assertEqual(r['target_existence'],'unknown');self.assertFalse(r['formulation_complete'])
        measure(d,'journal','inventory','100/1')
        r=family.assess(d,BUDGET);self.assertEqual(r['status'],'conditionally_infeasible')
        self.assertEqual(r['target_existence'],'unknown')

    def test_infeasible_measurement_checks_all_arms(self):
        d=fixture();measure(d,'journal','inventory','21/1')
        r=family.assess(d,BUDGET)
        self.assertEqual(r['status'],'conditionally_infeasible');self.assertEqual(r['target_existence'],'conditionally_empty')
        self.assertEqual(r['coverage']['infeasible'],2);self.assertTrue(family.verify_result(d,BUDGET,r))

    def test_one_global_cell_limit_leaves_unvisited_arm(self):
        d=fixture();r=family.assess(d,{**BUDGET,'max_cells':1})
        self.assertEqual(r['coverage']['attempted'],1);self.assertEqual(r['branches'][1]['status'],'unvisited')
        self.assertFalse(r['coverage']['complete']);self.assertEqual(r['declared_search'],'partial')
        self.assertEqual(r['status'],'conditional_family_witness')
        measure(d,'journal','inventory','21/1')
        r=family.assess(d,{**BUDGET,'max_cells':1})
        self.assertEqual(r['status'],'unknown');self.assertEqual(r['target_existence'],'unknown')

    def test_zero_and_branch_cap_do_not_mean_empty(self):
        for key in ['max_cells','elapsed_ms','max_integer_assignments','solver_timeout_ms','solver_rlimit','max_formula_nodes']:
            r=family.assess(fixture(),{**BUDGET,key:0});self.assertEqual(r['status'],'unknown',(key,r))
        for limit in [0,1]:
            d=fixture();d['branch_limit']=limit;r=family.assess(d,BUDGET)
            self.assertEqual(r['status'],'unknown');self.assertFalse(r['branch_partition_complete'])
            self.assertEqual(r['definition'],d)

    def test_unbalanced_and_cash_mismatch_are_not_balancing_constraints(self):
        for group in ['postings','flows']:
            d=fixture();d['method'][group].pop()
            # Remove the final handling cash posting or cash-flow row; its input
            # is still used elsewhere, so the original type compiler accepts it.
            d['selected_method_digest']=family.core.digest(d['method'])
            r=family.assess(d,BUDGET)
            self.assertEqual(r['status'],'unsupported',r)
            self.assertIn('identity',r['reason']);self.assertNotIn('branches',r)

    def test_exact_domain_types_and_digest_are_mandatory(self):
        for mutate in [lambda d:d['domains'].pop('p'),
                       lambda d:d['domains']['nrv']['interval'].update(lower='10/2'),
                       lambda d:d.update(selected_method_digest='0'*64),
                       lambda d:d['method']['inputs']['p']['type'].update(dimensions={'currency:EUR':1}),
                       lambda d:d.update(extra=True)]:
            d=fixture();mutate(d);self.assertEqual(family.assess(d,BUDGET)['status'],'invalid')
        d=fixture();measure(d,'journal','inventory','1/1');d['measurements'][0]['type']['scale']='1000/1'
        self.assertEqual(family.assess(d,BUDGET)['status'],'invalid')

    def test_alternate_witness_and_tampered_replay(self):
        d=fixture();r=family.assess(d,BUDGET)
        left=r['branches'][0];left['witness']['nrv']='22/1'
        left['replay']=family.replay_witness(d,BUDGET,0,left['witness'])
        self.assertTrue(family.verify_result(d,BUDGET,r))
        left['replay']['journal']['inventory']='22/1'
        self.assertFalse(family.verify_result(d,BUDGET,r))

    def test_wrong_branch_and_conflict_labels_reject(self):
        d=fixture();r=family.assess(d,BUDGET)
        with self.assertRaises(ValueError):family.replay_witness(d,BUDGET,1,r['branches'][0]['witness'])
        measure(d,'journal','inventory','21/1');r=family.assess(d,BUDGET)
        r['branches'][0]['conflict']['labels']=['fabricated']
        self.assertFalse(family.verify_result(d,BUDGET,r))

    def test_nested_minimum_preserves_all_combinations(self):
        d=fixture();old=d['method']['calculations'][2]['expression']
        d['method']['calculations'][2]['expression']={'op':'min','left':old,
            'right':{'op':'const','value':'18/1','type':deepcopy(d['method']['calculations'][2]['type'])}}
        d['selected_method_digest']=family.core.digest(d['method'])
        r=family.assess(d,BUDGET)
        self.assertEqual(r['coverage']['total'],4,r);self.assertTrue(r['coverage']['complete'])
        self.assertTrue(family.verify_result(d,BUDGET,r))

    def test_affine_sale_preserves_unknown_inputs_and_fractional_measurements(self):
        d=fixture();method=examples.program('sell',{'entity':'test','book_role':'legal','at':'2025-01-01'},
                                           list(d['method']['accounts']))
        d.update(method=method,selected_method_digest=family.core.digest(method),
                 domains={'proceeds':domain('0/1','10/1'),'cost':domain('1/3','2/3')})
        measure(d,'flow','flow.0','7/3');measure(d,'journal','inventory','-2/3')
        r=family.assess(d,BUDGET)
        self.assertEqual(r['status'],'conditional_family_witness',r)
        self.assertEqual(r['coverage']['total'],1)
        w=r['branches'][0]['witness'];self.assertEqual(w,{'cost':'2/3','proceeds':'7/3'})
        self.assertEqual(r['branches'][0]['replay']['journal']['cash'],'7/3')

    def test_open_domain_endpoint_is_preserved_in_exact_search(self):
        d=fixture();d['domains']['nrv']=domain('5/1','20/1',True,False)
        measure(d,'calculation','carrying','20/1')
        r=family.assess(d,BUDGET);self.assertEqual(r['status'],'conditionally_infeasible',r)

    def test_conflicting_premise_and_declared_limit_bounds_reject(self):
        d=fixture();d['domains']['nrv']['premise']['meaning']='conflicts with same id elsewhere'
        self.assertEqual(family.assess(d,BUDGET)['status'],'invalid')
        for limit in [True,-1,65]:
            d=fixture();d['branch_limit']=limit
            self.assertEqual(family.assess(d,BUDGET)['status'],'invalid')

    def test_status_manifest_and_coverage_tampering_reject(self):
        d=fixture();r=family.assess(d,BUDGET)
        for mutate in [lambda x:x.update(accounting_admission=True),
                       lambda x:x['coverage'].update(complete=False),
                       lambda x:x['branch_manifest'][0]['decisions'][0].update(arm='right'),
                       lambda x:x.update(status='conditionally_infeasible')]:
            bad=deepcopy(r);mutate(bad);self.assertFalse(family.verify_result(d,BUDGET,bad))


if __name__=='__main__':unittest.main()
