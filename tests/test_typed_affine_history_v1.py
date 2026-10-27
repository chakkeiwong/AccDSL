"""Dimensional and event-prefix counterexamples with exact independent replay."""
from copy import deepcopy
from pathlib import Path
import sys, unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'tests')]
import typed_affine_history_v1 as typed
import conditional_history_family_v1 as prior
from test_conditional_history_family_v1 import fixture as old_fixture, domain, witness, BUDGET
from test_joint_measurement_constraints_v1 import premise


def typ(dimensions, scale='1/1'):
    return {'kind':'rational','context':{'entity':'Synthetic','book':'example','basis':'authored'},
            'dimensions':dimensions, 'scale':scale}


def coefficient(value, dimensions=None, scale='1/1'):
    return {'value':value,'type':typ({} if dimensions is None else dimensions, scale)}


def monetary_embedding():
    d = old_fixture()
    d['profile'] = typed.PROFILE
    d['state_constraints'] = []
    d['memory'] = {k:{'type':deepcopy(d['value_type']),'domain':v} for k,v in d['memory'].items()}
    for template in d['templates'].values():
        template['event_type'] = deepcopy(d['value_type'])
        for group in ['postings','memory']:
            template[group] = {k:coefficient(v) for k,v in template[group].items()}
    for row in d['measurements']:
        row['value_type'] = deepcopy(d['value_type'])
        for term in row['terms']: term['coefficient'] = coefficient(term['coefficient'])
    return d


def stock_fixture(sale_first=False, constrained=True):
    money, units = typ({'currency:USD':1}), typ({'units:widget':1})
    price = {'currency:USD':1,'units:widget':-1}
    qty_term = {'kind':'memory','field':'units','coefficient':coefficient('1/1')}
    events = [
        {'id':'restock','date':'2024-06-30','template':'restock','amount':domain('4/1')},
        {'id':'sale','date':'2024-06-30','template':'sale','amount':domain('3/1')}]
    if sale_first: events.reverse()
    return {'profile':typed.PROFILE,
        'scope':{'name':'authored_fixed_unit_cost_stock','exclusions':[
            'real issuer facts','accounting treatment admission','integer lots','unknown prices']},
        'value_type':money,'opening_date':'2023-12-31','dates':['2024-06-30','2024-12-31'],
        'accounts':{'Cash':domain('20/1'),'Inventory':domain('0/1'),'Equity':domain('-20/1')},
        'memory':{'units':{'type':units,'domain':domain('0/1')}},
        'balance_premise':premise('opening_balance'),
        'templates':{
            'restock':{'event_type':units,'postings':{'Cash':coefficient('-2/1',price),
                'Inventory':coefficient('2/1',price)}, 'memory':{'units':coefficient('1/1')},
                'premise':premise('authored_fixed_cost'),'provenance':'constructed:cost2'},
            'sale':{'event_type':units,'postings':{'Cash':coefficient('3/1',price),
                'Inventory':coefficient('-2/1',price),'Equity':coefficient('-1/1',price)},
                'memory':{'units':coefficient('-1/1')},
                'premise':premise('authored_fixed_sale'),'provenance':'constructed:price3_cost2'}},
        'events':events,
        'measurements':[
            {'id':'closing_cash','date':'2024-12-31','value_type':money,
             'terms':[{'kind':'account','field':'Cash','coefficient':coefficient('1/1')}],
             'domain':domain('21/1')},
            {'id':'closing_units','date':'2024-12-31','value_type':units,
             'terms':[deepcopy(qty_term)],'domain':domain('1/1')}],
        'obligations':[],
        'state_constraints':([{'id':'stock_bounds','value_type':units,
            'terms':[qty_term], 'domain':domain('0/1','100/1')}] if constrained else [])}


class TypedAffineHistoryTests(unittest.TestCase):
    def test_monetary_embedding_matches_original_for_two_histories(self):
        d = monetary_embedding()
        r = typed.assess(d, BUDGET)
        self.assertEqual(r['status'], 'conditional_family_witness', r)
        for w in [witness(10,2,3), witness(8,3,4)]:
            old, new = prior.replay_witness(old_fixture(),BUDGET,w), typed.replay_witness(d,BUDGET,w)
            self.assertEqual(new['opening'],old['opening'])
            self.assertEqual(new['snapshots'],old['snapshots'])
            self.assertEqual({k:v['value'] for k,v in new['measurements'].items()},old['measurements'])
        self.assertFalse(r['replay']['declared_state_constraints_checked'])

    def test_units_and_money_replay_exactly(self):
        d = stock_fixture(); before = deepcopy(d); r = typed.assess(d,BUDGET)
        self.assertEqual(r['status'],'conditional_family_witness',r)
        self.assertEqual(d,before); self.assertEqual(r['definition'],d)
        replay = r['replay']
        self.assertEqual(replay['events'][0]['after']['memory']['units'],'4/1')
        self.assertEqual(replay['events'][1]['after']['memory']['units'],'1/1')
        self.assertEqual(replay['snapshots']['2024-12-31']['accounts'],
                         {'Cash':'21/1','Inventory':'2/1','Equity':'-23/1'})
        self.assertEqual([c['value'] for c in replay['state_constraints']],['0/1','4/1','1/1'])
        self.assertEqual(replay['field_types']['memory']['units']['dimensions'],{'units:widget':1})
        self.assertTrue(replay['declared_state_constraints_checked'])
        self.assertFalse(replay['operational_preconditions_checked'])

    def test_closing_match_does_not_hide_intermediate_shortage(self):
        good, bad = typed.assess(stock_fixture(),BUDGET), typed.assess(stock_fixture(True),BUDGET)
        self.assertEqual(good['status'],'conditional_family_witness')
        self.assertEqual(bad['status'],'conditionally_infeasible',bad)
        self.assertEqual(bad['target_existence'],'conditionally_empty')
        self.assertTrue(all(c['rechecked']=='unsat' for c in bad['conflicts']))
        relaxed = typed.assess(stock_fixture(True,False),BUDGET)
        self.assertEqual(relaxed['status'],'conditional_family_witness')
        self.assertEqual(relaxed['replay']['events'][0]['after']['memory']['units'],'-3/1')
        self.assertEqual(relaxed['replay']['measurements'],good['replay']['measurements'])
        self.assertFalse(relaxed['replay']['declared_state_constraints_checked'])

    def test_constraint_applies_to_opening_not_only_events(self):
        d = stock_fixture(); d['memory']['units']['domain'] = domain('-1/1')
        d['measurements'][1]['domain'] = domain('0/1')
        self.assertEqual(typed.assess(d,BUDGET)['status'],'conditionally_infeasible')
        d['state_constraints'] = []
        self.assertEqual(typed.assess(d,BUDGET)['status'],'conditional_family_witness')

    def test_typed_measurement_can_value_units_explicitly(self):
        d=stock_fixture(); row=d['measurements'][1]
        row['value_type']=d['value_type']; row['terms'][0]['coefficient']=coefficient(
            '2/1',{'currency:USD':1,'units:widget':-1});row['domain']=domain('2/1')
        r=typed.assess(d,BUDGET)
        self.assertEqual(r['status'],'conditional_family_witness',r)
        self.assertEqual(r['replay']['measurements']['closing_units']['value'],'2/1')

    def test_mixed_dimensions_context_and_scale_reject_before_solver(self):
        for mutate in [
            lambda d:d['templates']['sale']['postings']['Cash']['type'].update(dimensions={}),
            lambda d:d['templates']['sale']['event_type']['context'].update(book='different'),
            lambda d:d['templates']['sale']['postings']['Cash']['type'].update(scale='1000/1'),
            lambda d:d['measurements'][1].update(value_type=d['value_type']),
            lambda d:d['memory']['units']['type'].update(dimensions={'units:other':1}),
            lambda d:d['templates']['sale']['postings']['Cash'].update(value={'op':'unknown_product'})]:
            d=stock_fixture();mutate(d);r=typed.assess(d,BUDGET)
            self.assertEqual(r['status'],'invalid',r);self.assertNotIn('solver_status',r)

    def test_missing_state_premise_prevents_solving(self):
        d=stock_fixture();d['state_constraints'][0]['domain']['premise']=None
        r=typed.assess(d,BUDGET)
        self.assertEqual(r['status'],'unresolved');self.assertNotIn('witness',r)
        self.assertIn('state_constraint:stock_bounds',r['missing_premises'])

    def test_conflicting_premise_identity_rejects(self):
        d=stock_fixture();p=d['state_constraints'][0]['domain']['premise']
        p['meaning']='different meaning for shared id'
        self.assertEqual(typed.assess(d,BUDGET)['status'],'invalid')

    def test_obligations_do_not_promote_candidate_or_empty_target(self):
        for sale_first in [False,True]:
            d=stock_fixture(sale_first);d['obligations']=[{
                'id':'rights','meaning':'Contract rights unavailable','affects':['membership']}]
            r=typed.assess(d,BUDGET)
            self.assertEqual(r['target_existence'],'unknown');self.assertFalse(r['formulation_complete'])
            if not sale_first:self.assertEqual(r['status'],'candidate_witness_with_unresolved_obligations')

    def test_resource_stop_never_means_empty(self):
        for field in ['max_slots','max_cells','max_formula_nodes','elapsed_ms','solver_timeout_ms','solver_rlimit']:
            r=typed.assess(stock_fixture(),{**BUDGET,field:0})
            self.assertEqual(r['status'],'unknown',(field,r));self.assertNotIn('witness',r)

    def test_forged_or_incomplete_witness_rejects(self):
        d=stock_fixture();r=typed.assess(d,BUDGET)
        for w in [{}, {**r['witness'],typed.identifier('event_amount','sale'):'4/1'}]:
            with self.assertRaises(ValueError):typed.replay_witness(d,BUDGET,w)
        with self.assertRaises(ValueError):typed.replay_witness(stock_fixture(True),BUDGET,r['witness'])

    def test_semantic_verifier_allows_alternate_valid_witness(self):
        d=monetary_embedding();r=typed.assess(d,BUDGET)
        r['witness']=witness(8,3,4);r['replay']=typed.replay_witness(d,BUDGET,r['witness'])
        self.assertTrue(typed.verify_result(d,BUDGET,r))
        r['replay']['field_types']['memory']['cumulative_sales']['scale']='1000/1'
        self.assertFalse(typed.verify_result(d,BUDGET,r))

    def test_result_and_conflict_tampering_reject(self):
        for d in [stock_fixture(),stock_fixture(True)]:
            r=typed.assess(d,BUDGET);self.assertTrue(typed.verify_result(d,BUDGET,r))
            forged=deepcopy(r);forged['accounting_admission']=True
            self.assertFalse(typed.verify_result(d,BUDGET,forged))
            if 'conflicts' in r:
                r['conflicts'][0]['labels']=['not-a-constraint']
                self.assertFalse(typed.verify_result(d,BUDGET,r))

    def test_chronology_closed_fields_duplicate_constraints_and_bounds(self):
        for mutate in [lambda d:d['dates'].reverse(),
            lambda d:d['events'][0].update(date='2024-02-30'),
            lambda d:d['state_constraints'].append(deepcopy(d['state_constraints'][0])),
            lambda d:d['memory']['units'].update(extra='silent'),
            lambda d:d['state_constraints'][0]['domain']['interval'].update(lower='2/2'),
            lambda d:d['templates']['sale']['postings']['Equity'].update(value='-2/1')]:
            d=stock_fixture();mutate(d);self.assertEqual(typed.assess(d,BUDGET)['status'],'invalid')

    def test_open_endpoint_constraint_is_not_rounded(self):
        d=stock_fixture();d['state_constraints'][0]['domain']=domain('0/1','100/1',False,True)
        self.assertEqual(typed.assess(d,BUDGET)['status'],'conditionally_infeasible')

    def test_unmeasured_nonmonetary_memory_is_retained(self):
        d=stock_fixture();d['memory']['hours']={'type':typ({'hours':1}), 'domain':domain('2/1','3/1')}
        r=typed.assess(d,BUDGET);self.assertEqual(r['status'],'conditional_family_witness',r)
        self.assertIn(typed.identifier('opening_memory','hours'),r['witness'])
        self.assertIn('hours',r['replay']['field_types']['memory'])

    def test_explicit_compensating_scales_are_checked(self):
        d=stock_fixture()
        # Explicit reciprocal scales multiply to one; the checker does not
        # silently rescale a coefficient or an event magnitude.
        for template in d['templates'].values():
            template['event_type']=deepcopy(template['event_type'])
            template['event_type']['scale']='2/1'
            for group in ['postings','memory']:
                for item in template[group].values():item['type']['scale']='1/2'
        r=typed.assess(d,BUDGET)
        self.assertEqual(r['status'],'conditional_family_witness',r)
        self.assertEqual(r['replay']['measurements']['closing_units']['value'],'1/1')

    def test_expanded_constraint_limit_and_unnamed_currency_reject(self):
        d=stock_fixture()
        d['state_constraints'][0]['terms']=[deepcopy(d['state_constraints'][0]['terms'][0]) for _ in range(1366)]
        r=typed.assess(d,BUDGET)
        self.assertEqual(r['status'],'invalid');self.assertEqual(r['reason'],'state_constraint_expansion_limit')
        d=stock_fixture();d['value_type']['dimensions']={'currency:':1}
        self.assertEqual(typed.assess(d,BUDGET)['status'],'invalid')


if __name__ == '__main__': unittest.main()
