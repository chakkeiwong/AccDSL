"""Hand-checkable conditional histories and independent old-constructor comparison."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import conditional_history_family_v1 as history
import reconstruction_v1 as old
from test_joint_measurement_constraints_v1 import premise

BUDGET={'max_slots':4,'max_formula_nodes':10000,'max_integer_assignments':1,
        'max_cells':1,'elapsed_ms':5000,'solver_timeout_ms':1000,'solver_rlimit':1000000}


def domain(low,high=None,lower=True,upper=True):
    return {'interval':{'lower':low,'upper':low if high is None else high,
            'lower_inclusive':lower,'upper_inclusive':upper},
            'premise':premise('authored_domains'),'source_ref':'constructed:history_test'}


def fixture():
    return {'profile':history.PROFILE,'scope':{'name':'authored_linear_sale_history',
            'exclusions':['legal authority','operational liquidity','general contracts']},
        'value_type':{'kind':'rational','context':{'entity':'Synthetic','book':'example','basis':'authored'},
                      'dimensions':{'currency:USD':1},'scale':'1/1'},
        'opening_date':'2023-12-31','dates':['2024-06-30','2024-12-31'],
        'accounts':{'Cash':domain('8/1','12/1'),'Equity':domain('-12/1','-8/1')},
        'memory':{'cumulative_sales':domain('0/1')},'balance_premise':premise('opening_balance'),
        'templates':{'sale':{'postings':{'Cash':'1/1','Equity':'-1/1'},
            'memory':{'cumulative_sales':'1/1'},'premise':premise('authored_sale'),
            'provenance':'constructed:linear_sale_incidence'}},
        'events':[{'id':'early','date':'2024-06-30','template':'sale','amount':domain('0/1','5/1')},
                  {'id':'late','date':'2024-12-31','template':'sale','amount':domain('0/1','5/1')}],
        'measurements':[{'id':'closing_cash','date':'2024-12-31',
            'terms':[{'kind':'account','field':'Cash','coefficient':'1/1'}],'domain':domain('15/1')}],
        'obligations':[]}


def witness(opening,early,late):
    return {history.identifier('opening_account','Cash'):f'{opening}/1',
            history.identifier('opening_account','Equity'):f'{-opening}/1',
            history.identifier('opening_memory','cumulative_sales'):'0/1',
            history.identifier('event_amount','early'):f'{early}/1',
            history.identifier('event_amount','late'):f'{late}/1'}


class ConditionalHistoryTests(unittest.TestCase):
    def test_symbolic_opening_has_exact_replayed_history(self):
        d=fixture();before=deepcopy(d);r=history.assess(d,BUDGET)
        self.assertEqual(r['status'],'conditional_family_witness',r)
        self.assertEqual(d,before);self.assertEqual(r['definition'],before)
        self.assertEqual(r['replay']['measurements']['closing_cash'],'15/1')
        self.assertTrue(r['replay']['checked_exactly']);self.assertFalse(r['replay']['operational_preconditions_checked'])
        self.assertEqual(r['target_existence'],'conditional_witness')
        for event in r['replay']['events']:
            self.assertEqual(sum(map(Q,event['postings'].values())),0)
            self.assertEqual(sum(map(Q,event['after']['accounts'].values())),0)

    def test_two_histories_share_closing_but_preserve_different_memory(self):
        d=fixture();a=history.replay_witness(d,BUDGET,witness(10,2,3));b=history.replay_witness(d,BUDGET,witness(8,3,4))
        self.assertEqual(a['measurements'],b['measurements'])
        self.assertNotEqual(a['opening'],b['opening'])
        self.assertEqual(a['snapshots']['2024-12-31']['memory']['cumulative_sales'],'5/1')
        self.assertEqual(b['snapshots']['2024-12-31']['memory']['cumulative_sales'],'7/1')
        self.assertNotEqual(a['snapshots']['2024-06-30'],b['snapshots']['2024-06-30'])

    def test_one_opening_is_shared_across_all_snapshot_equations(self):
        d=fixture()
        for event in d['events']:event['amount']=domain('0/1')
        d['measurements'][0]['domain']=domain('10/1')
        d['measurements'].append({'id':'opening_cash','date':d['opening_date'],
            'terms':[{'kind':'account','field':'Cash','coefficient':'1/1'}],'domain':domain('9/1')})
        r=history.assess(d,BUDGET);self.assertEqual(r['status'],'conditionally_infeasible')
        self.assertEqual(r['target_existence'],'conditionally_empty')
        self.assertTrue(all(c['rechecked']=='unsat' for c in r['conflicts']))

    def test_missing_premises_prevent_solving(self):
        for mutate in [lambda d:d.update(balance_premise=None),
                       lambda d:d['accounts']['Cash'].update(premise=None),
                       lambda d:d['templates']['sale'].update(premise=None),
                       lambda d:d['events'][0]['amount'].update(premise=None),
                       lambda d:d['measurements'][0]['domain'].update(premise=None)]:
            d=fixture();mutate(d);r=history.assess(d,BUDGET)
            self.assertEqual(r['status'],'unresolved');self.assertTrue(r['missing_premises'])
            self.assertNotIn('witness',r);self.assertEqual(r['declared_search'],'not_started')

    def test_unresolved_target_obligations_allow_only_candidates(self):
        d=fixture();d['obligations']=[{'id':'source_opening','meaning':'No source-admitted opening',
                                    'affects':['target_history_membership','execution']}]
        r=history.assess(d,BUDGET)
        self.assertEqual(r['status'],'candidate_witness_with_unresolved_obligations')
        self.assertEqual(r['candidate_feasibility'],'conditionally_feasible')
        self.assertEqual(r['target_existence'],'unknown');self.assertFalse(r['formulation_complete'])
        self.assertEqual(r['economic_scope'],'unresolved');self.assertEqual(r['declared_search'],'complete')

    def test_chronology_and_calendar_validation(self):
        for mutate in [lambda d:d['dates'].reverse(),lambda d:d['dates'].append(d['dates'][-1]),
                       lambda d:d.update(opening_date='2024-06-30'),lambda d:d['events'].reverse(),
                       lambda d:d['events'][0].update(date='2023-12-31'),
                       lambda d:d['events'][1].update(date='2025-01-01'),
                       lambda d:d['dates'].__setitem__(0,'2024-02-30')]:
            d=fixture();mutate(d);self.assertEqual(history.assess(d,BUDGET)['status'],'invalid')

    def test_same_day_supplied_event_order_is_preserved(self):
        d=fixture();d['events'][0]['date']=d['events'][1]['date']
        a=history.replay_witness(d,BUDGET,witness(10,2,3));d['events'].reverse()
        b=history.replay_witness(d,BUDGET,witness(10,2,3))
        self.assertEqual(a['measurements'],b['measurements'])
        self.assertEqual([e['event_id'] for e in a['events']],['early','late'])
        self.assertEqual([e['event_id'] for e in b['events']],['late','early'])
        self.assertNotEqual(a['events'][0]['after'],b['events'][0]['after'])

    def test_fixed_opening_matches_existing_constructor(self):
        d=fixture();d['accounts']={'Cash':domain('10/1'),'Equity':domain('-10/1')}
        d['events'][0]['amount']=domain('2/1');d['events'][1]['amount']=domain('3/1')
        r=history.assess(d,BUDGET);self.assertEqual(r['status'],'conditional_family_witness')
        spec=json.loads((ROOT/'docs/design/fixtures/p04-reconstruction-cases-v1.json').read_text())['input_fixture']
        spec['opening']={'Cash':'10','Equity':'-10'};spec['economic_opening']={'cumulative_sales':'0'}
        spec['dates']=d['dates'];spec['templates']={'sale':{'postings':{'Cash':'1','Equity':'-1'},
            'state':{'cumulative_sales':'1'},'provenance':['constructed:linear_sale_incidence']}}
        spec['slots']=[{'id':e['id'],'date':e['date'],'template':'sale','kind':'Real','active':True} for e in d['events']]
        spec['constraints']=[{'id':key,'expression':['==',key,str(value)]} for key,value in [('early',2),('late',3)]]
        spec['mappings']={'cash':'balance:2024-12-31:Cash','memory':'state:2024-12-31:cumulative_sales'}
        spec['views']={};p=old.construct(spec);prior=old.solve(p,old.Budget(**BUDGET))
        self.assertEqual(prior['feasibility'],'Feasible')
        values=prior['cells'][0]['witness'];self.assertEqual(Q(values['early']),2);self.assertEqual(Q(values['late']),3)
        for label,wanted in [('cash','15/1'),('memory','5/1')]:
            value=old.z3.simplify(old.z3.substitute(p.outputs[label],
                (p.variables['early'],old.q(values['early'])),(p.variables['late'],old.q(values['late']))))
            self.assertEqual(history.joint.solver.fraction(value),Q(wanted))

    def test_strict_domains_and_opening_balance(self):
        d=fixture();d['accounts']['Cash']=domain('10/1','11/1',False,True)
        d['accounts']['Equity']=domain('-10/1');self.assertEqual(history.assess(d,BUDGET)['status'],'conditionally_infeasible')
        d=fixture();d['accounts']['Cash']=domain('10/1');d['accounts']['Equity']=domain('-9/1')
        self.assertEqual(history.assess(d,BUDGET)['status'],'conditionally_infeasible')

    def test_unbalanced_incidence_bad_domains_and_unbound_fields_reject(self):
        for mutate in [lambda d:d['templates']['sale']['postings'].update(Cash='2/1'),
                       lambda d:d['events'][0].update(amount=domain('-1/1','1/1')),
                       lambda d:d['templates']['sale']['memory'].update(unknown='1/1'),
                       lambda d:d['templates']['sale']['postings'].update(Cash='2/2'),
                       lambda d:d['events'][0].update(template='absent')]:
            d=fixture();mutate(d);self.assertEqual(history.assess(d,BUDGET)['status'],'invalid')

    def test_forged_history_witness_and_missing_assignment_reject(self):
        d=fixture()
        for w in [witness(10,2,4),witness(10,6,-1),{},
                  {**witness(10,2,3),history.identifier('opening_account','Equity'):'-9/1'}]:
            with self.assertRaises(ValueError):history.replay_witness(d,BUDGET,w)

    def test_resource_limits_remain_unknown(self):
        for field in ['max_slots','max_cells','max_formula_nodes','elapsed_ms','solver_timeout_ms','solver_rlimit']:
            r=history.assess(fixture(),{**BUDGET,field:0})
            self.assertEqual(r['status'],'unknown',(field,r))
            self.assertNotIn('witness',r);self.assertEqual(r['target_existence'],'unknown')

    def test_monetary_scope_cannot_hide_units_or_dates(self):
        for mutate in [lambda d:d['value_type'].update(dimensions={'units':1}),
                       lambda d:d['value_type']['context'].update(instant='2024-12-31'),
                       lambda d:d['accounts']['Cash'].update(extra='ignored'),
                       lambda d:d['obligations'].append({'id':'x','meaning':'missing','affects':[]})]:
            d=fixture();mutate(d);self.assertEqual(history.assess(d,BUDGET)['status'],'invalid')

    def test_unmeasured_monetary_memory_stays_in_family(self):
        d=fixture();d['memory']['unobserved_liability']=domain('0/1','10/1')
        r=history.assess(d,BUDGET);self.assertEqual(r['status'],'conditional_family_witness')
        self.assertIn(history.identifier('opening_memory','unobserved_liability'),r['witness'])
        self.assertIn('unobserved_liability',r['replay']['opening']['memory'])

    def test_boundaries_no_operational_or_source_admission(self):
        r=history.assess(fixture(),BUDGET)
        for flag in ['executed','source_admission','accounting_admission']:self.assertFalse(r[flag])
        self.assertIsNone(r['executable_opening']);self.assertEqual(r['actual_history'],'unknown')
        self.assertIn('not enumeration',r['family_representation'])

    def test_semantic_replay_allows_another_valid_history(self):
        d=fixture();r=history.assess(d,BUDGET)
        r['witness']=witness(8,3,4);r['replay']=history.replay_witness(d,BUDGET,r['witness'])
        self.assertTrue(history.verify_result(d,BUDGET,r))
        r['replay']['events'][0]['after']['accounts']['Cash']='999/1'
        self.assertFalse(history.verify_result(d,BUDGET,r))

    def test_semantic_replay_rejects_promoted_scope_or_changed_family(self):
        d=fixture();r=history.assess(d,BUDGET)
        for mutate in [lambda x:x.update(source_admission=True),
                       lambda x:x.update(executable_opening=x['replay']['opening']),
                       lambda x:x['definition']['scope']['exclusions'].clear(),
                       lambda x:x['coverage'].update(complete=False)]:
            altered=deepcopy(r);mutate(altered)
            self.assertFalse(history.verify_result(d,BUDGET,altered))

    def test_conflict_and_unknown_semantic_replay(self):
        d=fixture();d['accounts']['Cash']=domain('10/1');d['accounts']['Equity']=domain('-9/1')
        r=history.assess(d,BUDGET);self.assertTrue(history.verify_result(d,BUDGET,r))
        r['conflicts'][0]['labels']=['domain:'+history.identifier('opening_account','Cash')]
        self.assertFalse(history.verify_result(d,BUDGET,r))
        b={**BUDGET,'max_slots':0};unknown=history.assess(fixture(),b)
        self.assertTrue(history.verify_result(fixture(),b,unknown))


if __name__=='__main__':unittest.main()
