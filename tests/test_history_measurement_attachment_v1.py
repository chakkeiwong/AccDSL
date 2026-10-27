"""Attachment must preserve complete parent formulas and all shared alternatives."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import history_measurement_attachment_v1 as attachment
from test_conditional_history_family_v1 import fixture as history_fixture,domain,witness,BUDGET
from test_joint_measurement_constraints_v1 import premise


def fixture():
    h=history_fixture();period={'kind':'period','start':'2024-01-01','end_exclusive':'2025-01-01'}
    def obs(low,high,when,quantity):
        return {'type':{'value_type':deepcopy(h['value_type']),'time':when,'quantity':quantity},
                'interval':domain(low,high)['interval'],'interval_premise':premise('authored_measurements'),
                'source_ref':'constructed:measurements'}
    m={'profile':attachment.temporal.PROFILE,'observations':{
        'opening':obs('8/1','12/1',{'kind':'instant','at':'2023-12-31'},'cash'),
        'flow':obs('3/1','7/1',period,'cash_change'),
        'closing':obs('15/1','15/1',{'kind':'instant','at':'2024-12-31'},'cash')},
       'relations':[{'id':'bridge','kind':'stock_flow','period':period,'opening':'opening',
         'movements':[{'observation':'flow','coefficient':'1/1'}],'closing':'closing',
         'identity_premise':premise('cash_measurement_bridge')}]}
    bindings={name:{'kind':'movement' if name=='flow' else 'snapshot',
        'quantity':item['type']['quantity'],'terms':[{'kind':'account','field':'Cash','coefficient':'1/1'}],
        'premise':premise('explicit_mapping:'+name)} for name,item in m['observations'].items()}
    return {'profile':attachment.PROFILE,'history':h,'measurements':m,'bindings':bindings,'obligations':[]}


def joined_witness(opening,early,late):
    result={attachment.key('history',k):v for k,v in witness(opening,early,late).items()}
    result.update({attachment.key('measurement',k):f'{v}/1' for k,v in
                   [('opening',opening),('flow',early+late),('closing',opening+early+late)]})
    return result


class HistoryAttachmentTests(unittest.TestCase):
    def test_complete_parent_formulas_join_without_selected_parent_witness(self):
        d=fixture();before=deepcopy(d);r=attachment.assess(d,BUDGET)
        self.assertEqual(r['status'],'conditional_attachment_witness',r)
        self.assertEqual(d,before);self.assertEqual(r['definition'],before)
        self.assertTrue(r['replay']['both_parent_constraints_checked'])
        self.assertTrue(r['replay']['all_supplied_mappings_checked'])
        self.assertEqual(r['replay']['mapping_values']['closing'],'15/1')
        self.assertEqual(r['unmapped_observations'],[])
        self.assertTrue(attachment.verify_result(d,BUDGET,r))

    def test_multiple_joint_histories_preserve_different_openings_and_memory(self):
        d=fixture();a=attachment.replay_witness(d,BUDGET,joined_witness(10,2,3))
        b=attachment.replay_witness(d,BUDGET,joined_witness(8,3,4))
        self.assertEqual(a['measurement_witness']['closing'],b['measurement_witness']['closing'])
        self.assertNotEqual(a['measurement_witness']['opening'],b['measurement_witness']['opening'])
        self.assertNotEqual(a['history']['snapshots']['2024-12-31']['memory'],b['history']['snapshots']['2024-12-31']['memory'])

    def test_selecting_one_parent_witness_would_wrongly_discard_valid_history(self):
        d=fixture();h=d['history'];h['accounts']={'Cash':domain('10/1'),'Equity':domain('-10/1')}
        # (8,7,15) is valid for the measurement family alone but incompatible with this history opening.
        self.assertTrue(attachment.temporal.check_witness(d['measurements'],attachment.measurement_budget(BUDGET),
                        {'opening':'8/1','flow':'7/1','closing':'15/1'}))
        r=attachment.assess(d,BUDGET);self.assertEqual(r['status'],'conditional_attachment_witness')
        self.assertEqual(r['replay']['measurement_witness']['opening'],'10/1')
        self.assertEqual(r['replay']['measurement_witness']['flow'],'5/1')

    def test_separately_feasible_parents_can_have_infeasible_attachment(self):
        d=fixture();d['history']['accounts']={'Cash':domain('10/1'),'Equity':domain('-10/1')}
        d['measurements']['observations']['opening']['interval']=domain('8/1')['interval']
        self.assertEqual(attachment.history.assess(d['history'],BUDGET)['status'],'conditional_family_witness')
        self.assertEqual(attachment.temporal.assess(d['measurements'],attachment.measurement_budget(BUDGET))['status'],'conditionally_feasible')
        r=attachment.assess(d,BUDGET);self.assertEqual(r['status'],'conditionally_infeasible')
        self.assertTrue(attachment.verify_result(d,BUDGET,r))

    def test_flow_uses_only_period_events_not_opening_balance(self):
        r=attachment.replay_witness(fixture(),BUDGET,joined_witness(10,2,3))
        self.assertEqual(r['mapping_values']['flow'],'5/1')
        self.assertEqual(r['mapping_values']['opening'],'10/1')
        self.assertEqual(r['mapping_values']['closing'],'15/1')
        d=fixture();d['bindings']['flow']['kind']='snapshot'
        self.assertEqual(attachment.assess(d,BUDGET)['status'],'invalid')

    def test_wrong_dates_contexts_quantities_and_unknown_fields_reject(self):
        for mutate in [lambda d:d['bindings']['opening'].update(quantity='legal_available_cash'),
                       lambda d:d['bindings']['opening']['terms'][0].update(field='missing'),
                       lambda d:d['measurements']['observations']['opening']['type']['value_type']['context'].update(entity='Apple'),
                       lambda d:d['history']['dates'].__setitem__(1,'2025-01-01'),
                       lambda d:d.update(parent_witness={'opening':'8/1'})]:
            d=fixture();mutate(d);self.assertEqual(attachment.assess(d,BUDGET)['status'],'invalid')

    def test_missing_mapping_premise_prevents_solver(self):
        d=fixture();d['bindings']['flow']['premise']=None;r=attachment.assess(d,BUDGET)
        self.assertEqual(r['status'],'unresolved');self.assertIn('mapping:flow',r['missing_premises'])
        self.assertNotIn('witness',r)

    def test_unmapped_observations_remain_in_parent_and_target_obligations(self):
        d=fixture();d['bindings'].pop('opening');r=attachment.assess(d,BUDGET)
        self.assertEqual(r['status'],'candidate_attachment_with_unresolved_obligations')
        self.assertEqual(r['unmapped_observations'],['opening'])
        self.assertIn(attachment.key('measurement','opening'),r['witness'])
        self.assertEqual(r['target_existence'],'unknown');self.assertFalse(r['formulation_complete'])

    def test_parent_and_attachment_obligations_survive(self):
        d=fixture();d['history']['obligations']=[{'id':'source','meaning':'No admitted opening','affects':['history']}]
        d['obligations']=[{'id':'authority','meaning':'Mapping has no accounting admission','affects':['execution']}]
        r=attachment.assess(d,BUDGET);self.assertEqual(r['status'],'candidate_attachment_with_unresolved_obligations')
        self.assertEqual({x['origin'] for x in r['target_obligations']},{'history','attachment'})
        self.assertEqual(r['target_existence'],'unknown')

    def test_distinct_namespaces_do_not_alias_identical_text_ids(self):
        d=fixture();old='opening';new=attachment.history.identifier('opening_account','Cash')
        d['measurements']['observations'][new]=d['measurements']['observations'].pop(old)
        d['measurements']['relations'][0]['opening']=new
        d['bindings'][new]=d['bindings'].pop(old)
        r=attachment.assess(d,BUDGET);self.assertEqual(r['status'],'conditional_attachment_witness')
        self.assertIn(attachment.key('measurement',new),r['witness']);self.assertIn(attachment.key('history',new),r['witness'])

    def test_zero_budgets_unknown_and_strict_bound_conflict(self):
        for field in ['max_slots','max_cells','max_formula_nodes','elapsed_ms','solver_timeout_ms','solver_rlimit']:
            r=attachment.assess(fixture(),{**BUDGET,field:0})
            self.assertEqual(r['status'],'unknown',(field,r))
        d=fixture();d['history']['accounts']={'Cash':domain('10/1'),'Equity':domain('-10/1')}
        d['measurements']['observations']['opening']['interval']=domain('10/1','11/1',False,True)['interval']
        self.assertEqual(attachment.assess(d,BUDGET)['status'],'conditionally_infeasible')

    def test_semantic_replay_rejects_changed_parent_formula_scope_and_trace(self):
        d=fixture();r=attachment.assess(d,BUDGET)
        for mutate in [lambda x:x['definition']['history']['scope']['exclusions'].clear(),
                       lambda x:x['numeric_measurement_definition']['equations'][0].update(rhs='1/1'),
                       lambda x:x['replay']['mapping_values'].update(flow='99/1'),
                       lambda x:x.update(source_admission=True),
                       lambda x:x.update(executable_opening={})]:
            changed=deepcopy(r);mutate(changed);self.assertFalse(attachment.verify_result(d,BUDGET,changed))
        r['witness']=joined_witness(8,3,4);r['replay']=attachment.replay_witness(d,BUDGET,r['witness'])
        self.assertTrue(attachment.verify_result(d,BUDGET,r))

    def test_retained_source_context_cannot_silently_become_synthetic_book(self):
        import retained_temporal_source_binding_v1 as retained
        from test_joint_measurement_constraints_v1 import BUDGET as MB
        real=retained.assess(retained.fixture(assume=True),MB)
        d=fixture();d['measurements']=real['definition'];d['bindings']={}
        observation=next(iter(d['measurements']['observations']))
        d['bindings'][observation]={'kind':'snapshot','quantity':d['measurements']['observations'][observation]['type']['quantity'],
            'terms':[{'kind':'account','field':'Cash','coefficient':'1/1'}],'premise':premise('unsupported_real_mapping')}
        r=attachment.assess(d,BUDGET);self.assertEqual(r['status'],'invalid')
        self.assertIn('mapping_value_type_mismatch',r['reason'])
        self.assertIsNone(real['executable_opening'])


if __name__=='__main__':unittest.main()
