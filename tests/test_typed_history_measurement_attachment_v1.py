"""Exact complete-parent typed mappings and intermediate-state counterexamples."""
from copy import deepcopy
from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import typed_history_measurement_attachment_v1 as attachment
import history_measurement_attachment_v1 as old
from test_history_measurement_attachment_v1 import fixture as old_fixture,joined_witness
from test_typed_affine_history_v1 import monetary_embedding,stock_fixture,coefficient,typ
from test_conditional_history_family_v1 import domain,BUDGET
from test_joint_measurement_constraints_v1 import premise


def monetary_fixture():
    d=old_fixture();d['profile']=attachment.PROFILE;d['history']=monetary_embedding()
    for b in d['bindings'].values():
        for term in b['terms']:term['coefficient']=coefficient(term['coefficient'])
    return d


def fixture(sale_first=False,constrained=True):
    h=stock_fixture(sale_first,constrained)
    for row in h['measurements']:row['domain']=domain('-100/1','100/1')
    period={'kind':'period','start':'2024-01-01','end_exclusive':'2025-01-01'}
    observations={};bindings={};relations=[]
    for prefix,kind,field,value_type,vals in [
        ('units','memory','units',typ({'units:widget':1}),['0/1','1/1','1/1']),
        ('cash','account','Cash',typ({'currency:USD':1}),['20/1','1/1','21/1'])]:
        for role,value in zip(['opening','flow','closing'],vals):
            name=prefix+'_'+role
            when=(period if role=='flow' else {'kind':'instant','at':h['opening_date'] if role=='opening' else h['dates'][-1]})
            quantity=prefix+'_change' if role=='flow' else prefix
            observations[name]={'type':{'value_type':deepcopy(value_type),'time':deepcopy(when),'quantity':quantity},
                'interval':domain(value)['interval'],'interval_premise':premise('observation:'+name),
                'source_ref':'constructed:'+name}
            bindings[name]={'kind':'movement' if role=='flow' else 'snapshot','quantity':quantity,
                'terms':[{'kind':kind,'field':field,'coefficient':coefficient('1/1')}],
                'premise':premise('mapping:'+name)}
        relations.append({'id':prefix+'_bridge','kind':'stock_flow','period':deepcopy(period),
            'opening':prefix+'_opening','movements':[{'observation':prefix+'_flow','coefficient':'1/1'}],
            'closing':prefix+'_closing','identity_premise':premise('bridge:'+prefix)})
    return {'profile':attachment.PROFILE,'history':h,
        'measurements':{'profile':attachment.temporal.PROFILE,'observations':observations,'relations':relations},
        'bindings':bindings,'obligations':[]}


class TypedHistoryAttachmentTests(unittest.TestCase):
    def test_money_and_units_share_the_complete_history(self):
        d=fixture();before=deepcopy(d);r=attachment.assess(d,BUDGET)
        self.assertEqual(r['status'],'conditional_attachment_witness',r)
        self.assertEqual(d,before);self.assertTrue(attachment.verify_result(d,BUDGET,r))
        self.assertEqual(r['replay']['mapping_values']['units_closing'],'1/1')
        self.assertEqual(r['replay']['mapping_values']['cash_closing'],'21/1')
        self.assertEqual([x['value'] for x in r['replay']['history']['state_constraints']],['0/1','4/1','1/1'])
        self.assertTrue(r['replay']['both_parent_constraints_checked'])
        self.assertFalse(r['source_admission']);self.assertFalse(r['executed'])

    def test_closing_measurements_do_not_erase_intermediate_stock_shortage(self):
        bad=fixture(True);r=attachment.assess(bad,BUDGET)
        self.assertEqual(r['status'],'conditionally_infeasible',r)
        self.assertTrue(attachment.verify_result(bad,BUDGET,r))
        relaxed=fixture(True,False);s=attachment.assess(relaxed,BUDGET)
        self.assertEqual(s['status'],'conditional_attachment_witness',s)
        self.assertEqual(s['replay']['history']['events'][0]['after']['memory']['units'],'-3/1')
        self.assertFalse(s['replay']['history']['declared_state_constraints_checked'])

    def test_observations_restrict_shared_unknown_event_quantities(self):
        d=fixture()
        for e in d['history']['events']:e['amount']=domain('0/1','10/1')
        r=attachment.assess(d,BUDGET);self.assertEqual(r['status'],'conditional_attachment_witness',r)
        values={e['event_id']:e['amount'] for e in r['replay']['history']['events']}
        self.assertEqual(values,{'restock':'4/1','sale':'3/1'})

    def test_monetary_embedding_matches_original_attachment(self):
        d=monetary_fixture();r=attachment.assess(d,BUDGET)
        self.assertEqual(r['status'],'conditional_attachment_witness',r)
        for w in [joined_witness(10,2,3),joined_witness(8,3,4)]:
            a=old.replay_witness(old_fixture(),BUDGET,w);b=attachment.replay_witness(d,BUDGET,w)
            self.assertEqual(a['mapping_values'],b['mapping_values'])
            self.assertEqual(a['history']['snapshots'],b['history']['snapshots'])
        self.assertEqual(r['definition']['history'],d['history'])

    def test_arbitrary_measurement_witness_does_not_replace_parent_formula(self):
        d=monetary_fixture();d['history']['accounts']={'Cash':domain('10/1'),'Equity':domain('-10/1')}
        self.assertTrue(attachment.temporal.check_witness(d['measurements'],attachment.measurement_budget(BUDGET),
                                                       {'opening':'8/1','flow':'7/1','closing':'15/1'}))
        r=attachment.assess(d,BUDGET);self.assertEqual(r['status'],'conditional_attachment_witness',r)
        self.assertEqual(r['replay']['mapping_values']['opening'],'10/1')

    def test_separately_feasible_parents_can_have_empty_intersection(self):
        d=monetary_fixture();d['history']['accounts']={'Cash':domain('10/1'),'Equity':domain('-10/1')}
        d['measurements']['observations']['opening']['interval']=domain('8/1')['interval']
        self.assertEqual(attachment.history.assess(d['history'],BUDGET)['status'],'conditional_family_witness')
        self.assertEqual(attachment.temporal.assess(d['measurements'],attachment.measurement_budget(BUDGET))['status'],'conditionally_feasible')
        r=attachment.assess(d,BUDGET);self.assertEqual(r['status'],'conditionally_infeasible',r)

    def test_typed_coefficient_can_explicitly_value_units(self):
        d=fixture()
        for name in ['units_opening','units_flow','units_closing']:
            item=d['measurements']['observations'][name];item['type']['value_type']=typ({'currency:USD':1})
            item['interval']=domain('0/1' if name=='units_opening' else '2/1')['interval']
            d['bindings'][name]['terms'][0]['coefficient']=coefficient('2/1',{'currency:USD':1,'units:widget':-1})
        r=attachment.assess(d,BUDGET);self.assertEqual(r['status'],'conditional_attachment_witness',r)
        self.assertEqual(r['replay']['mapping_values']['units_closing'],'2/1')

    def test_wrong_dimensions_scale_context_and_plain_coefficient_reject(self):
        changes=[lambda t:t['coefficient']['type'].update(dimensions={'currency:USD':1}),
                 lambda t:t['coefficient']['type'].update(scale='1000/1'),
                 lambda t:t['coefficient']['type']['context'].update(entity='Other'),
                 lambda t:t.update(coefficient='1/1'),lambda t:t.update(field='missing')]
        for change in changes:
            d=fixture();change(d['bindings']['units_closing']['terms'][0])
            self.assertEqual(attachment.assess(d,BUDGET)['status'],'invalid')

    def test_period_movement_excludes_opening_stock(self):
        d=fixture();d['history']['memory']['units']['domain']=domain('2/1')
        for name,v in [('units_opening','2/1'),('units_closing','3/1')]:
            d['measurements']['observations'][name]['interval']=domain(v)['interval']
        r=attachment.assess(d,BUDGET);self.assertEqual(r['status'],'conditional_attachment_witness',r)
        self.assertEqual(r['replay']['mapping_values']['units_flow'],'1/1')
        self.assertEqual(r['replay']['mapping_values']['units_closing'],'3/1')

    def test_wrong_time_quantity_and_parent_result_reject(self):
        for mutate in [lambda d:d['bindings']['units_closing'].update(quantity='other_goods'),
                       lambda d:d['bindings']['units_flow'].update(kind='snapshot'),
                       lambda d:d['history']['dates'].__setitem__(1,'2025-01-01'),
                       lambda d:d.update(parent_witness={})]:
            d=fixture();mutate(d);self.assertEqual(attachment.assess(d,BUDGET)['status'],'invalid')

    def test_missing_and_conflicting_premises(self):
        for mutate in [lambda d:d['bindings']['units_flow'].update(premise=None),
                       lambda d:d['history']['state_constraints'][0]['domain'].update(premise=None),
                       lambda d:d['measurements']['relations'][0].update(identity_premise=None)]:
            d=fixture();mutate(d);r=attachment.assess(d,BUDGET)
            self.assertEqual(r['status'],'unresolved',r);self.assertNotIn('witness',r)
        d=fixture();p=deepcopy(d['history']['balance_premise']);p['meaning']='conflicting identity'
        d['bindings']['units_flow']['premise']=p
        self.assertEqual(attachment.assess(d,BUDGET)['status'],'invalid')

    def test_unmapped_observations_and_obligations_are_preserved(self):
        d=fixture();d['bindings'].pop('units_closing')
        d['history']['obligations']=[{'id':'facts','meaning':'No actual source facts','affects':['history']}]
        d['obligations']=[{'id':'admission','meaning':'No admitted mappings','affects':['execution']}]
        r=attachment.assess(d,BUDGET);self.assertEqual(r['status'],'candidate_attachment_with_unresolved_obligations')
        self.assertEqual({x['origin'] for x in r['target_obligations']},{'history','attachment','unmapped_measurement'})
        self.assertIn(attachment.key('measurement','units_closing'),r['witness'])
        self.assertEqual(r['target_existence'],'unknown')

    def test_unmeasured_typed_memory_retains_alternative_values(self):
        d=fixture();d['history']['memory']['latent']={'type':typ({'units:widget':1}),'domain':domain('0/1','5/1')}
        r=attachment.assess(d,BUDGET);self.assertEqual(r['status'],'conditional_attachment_witness',r)
        for v in ['1/1','4/1']:
            w=deepcopy(r['witness']);w[attachment.key('history',attachment.history.identifier('opening_memory','latent'))]=v
            replay=attachment.replay_witness(d,BUDGET,w)
            self.assertEqual(replay['history']['snapshots']['2024-12-31']['memory']['latent'],v)

    def test_zero_budgets_and_strict_boundary(self):
        for field in ['max_slots','max_cells','max_formula_nodes','elapsed_ms','solver_timeout_ms','solver_rlimit']:
            r=attachment.assess(fixture(),{**BUDGET,field:0});self.assertEqual(r['status'],'unknown',(field,r))
        d=fixture();d['measurements']['observations']['units_closing']['interval']=domain('1/1','2/1',False,True)['interval']
        self.assertEqual(attachment.assess(d,BUDGET)['status'],'conditionally_infeasible')

    def test_forged_result_and_witness_reject(self):
        d=fixture();r=attachment.assess(d,BUDGET);self.assertTrue(attachment.verify_result(d,BUDGET,r))
        for mutate in [lambda x:x.update(source_admission=True),
                       lambda x:x['typed_fields']['memory']['units'].update(scale='1000/1'),
                       lambda x:x['replay']['mapping_values'].update(units_closing='2/1'),
                       lambda x:x['definition']['history']['state_constraints'].clear()]:
            bad=deepcopy(r);mutate(bad);self.assertFalse(attachment.verify_result(d,BUDGET,bad))
        w=deepcopy(r['witness']);w[attachment.key('measurement','units_closing')]='2/1'
        with self.assertRaises(ValueError):attachment.replay_witness(d,BUDGET,w)

    def test_alternate_valid_witness_and_conflict(self):
        d=monetary_fixture();r=attachment.assess(d,BUDGET)
        r['witness']=joined_witness(8,3,4);r['replay']=attachment.replay_witness(d,BUDGET,r['witness'])
        self.assertTrue(attachment.verify_result(d,BUDGET,r))
        d=fixture(True);r=attachment.assess(d,BUDGET);r['conflicts'][0]['labels']=['invented']
        self.assertFalse(attachment.verify_result(d,BUDGET,r))

    def test_same_day_snapshot_includes_every_ordered_event(self):
        d=fixture();obs=deepcopy(d['measurements']['observations']['units_closing'])
        obs['type']['time']={'kind':'instant','at':'2024-06-30'}
        obs['interval']=domain('4/1')['interval']
        d['measurements']['observations']['same_day']=obs
        d['bindings']['same_day']=deepcopy(d['bindings']['units_closing'])
        d['measurements']['relations'].append({'id':'same_day_identity','kind':'same_time',
            'terms':[{'observation':'same_day','coefficient':'1/1'}],'rhs':'4/1',
            'identity_premise':premise('same_day_identity')})
        self.assertEqual(attachment.assess(d,BUDGET)['status'],'conditionally_infeasible')
        obs['interval']=domain('1/1')['interval'];d['measurements']['relations'][-1]['rhs']='1/1'
        r=attachment.assess(d,BUDGET);self.assertEqual(r['status'],'conditional_attachment_witness',r)
        self.assertEqual(r['replay']['mapping_values']['same_day'],'1/1')

    def test_scale_conversion_requires_explicit_compensating_coefficient(self):
        d=fixture()
        for name in ['units_opening','units_flow','units_closing']:
            obs=d['measurements']['observations'][name]
            obs['type']['value_type']['scale']='1000/1'
            obs['interval']=domain('0/1' if name=='units_opening' else '1/1000')['interval']
            d['bindings'][name]['terms'][0]['coefficient']=coefficient('1/1000',{},'1000/1')
        r=attachment.assess(d,BUDGET);self.assertEqual(r['status'],'conditional_attachment_witness',r)
        self.assertEqual(r['replay']['mapping_values']['units_closing'],'1/1000')

    def test_unmapped_parent_equation_can_still_make_system_empty(self):
        d=fixture();d['bindings'].pop('units_closing')
        d['measurements']['relations'].append({'id':'extra_constraint','kind':'same_time',
            'terms':[{'observation':'units_closing','coefficient':'1/1'}],'rhs':'2/1',
            'identity_premise':premise('extra_constraint')})
        r=attachment.assess(d,BUDGET);self.assertEqual(r['status'],'conditionally_infeasible',r)
        self.assertEqual(r['target_existence'],'unknown')


if __name__=='__main__':unittest.main()
