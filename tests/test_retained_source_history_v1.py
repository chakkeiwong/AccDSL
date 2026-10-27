"""Source lineage, selected-history counterexamples and semantic replay."""
from copy import deepcopy
from pathlib import Path
import importlib.util,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('retained_history_examples',ROOT/'data/accounting-master/retained-source-history-20261025/examples.py')
examples=importlib.util.module_from_spec(spec);spec.loader.exec_module(examples)
adapter=examples.adapter;attachment=adapter.attachment;BUDGET=examples.BUDGET

class RetainedSourceHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body=examples.fixture();cls.result=adapter.assess(cls.body,BUDGET)
        assert cls.result['status']=='conditional_candidates_with_unresolved_facts',cls.result.get('reason',cls.result.get('attachment_statuses'))

    def test_complete_source_and_both_parent_constraints_retained(self):
        r=self.result
        self.assertEqual(r['source_observation_count'],256);self.assertEqual(r['source_relation_count'],143)
        self.assertEqual(len(r['source_result']['relation_dispositions']),143)
        self.assertEqual(len(r['source_result']['definition']['observations']),6)
        self.assertTrue(adapter.verify_result(self.body,BUDGET,r))
        for name,a in r['attachments'].items():
            self.assertEqual(a['definition']['history'],self.body['histories'][name]['history'])
            self.assertTrue(a['replay']['both_parent_constraints_checked'])
            self.assertTrue(a['replay']['all_supplied_mappings_checked'])
            self.assertEqual(a['target_existence'],'unknown')
            self.assertEqual(len(a['target_obligations']),2)

    def test_distinct_contexts_are_preserved_at_equal_dates(self):
        a,b=[self.result['attachments'][k]['definition'] for k in adapter.source.SUPPORTED]
        self.assertNotEqual(a['history']['value_type']['context']['basis'],b['history']['value_type']['context']['basis'])
        self.assertEqual(a['history']['dates'][-1],b['history']['opening_date'])
        self.assertFalse(self.result['joint_cross_context_history'])
        self.assertEqual(a['history']['value_type']['scale'],'1000000/1')

    def test_two_different_gross_histories_fit_the_selected_source_values(self):
        for name,amounts in [('annual.cash_closing',[(0,794),(100,894)]),('interim.cash_closing',[(356,0),(456,100)])]:
            d=self.result['attachments'][name]['definition'];replays=[]
            for borrow,repay in amounts:
                w=examples.witness(d,borrow,repay)
                replays.append(attachment.replay_witness(d,BUDGET,w))
            self.assertEqual(replays[0]['mapping_values'],replays[1]['mapping_values'])
            self.assertNotEqual(replays[0]['history']['events'],replays[1]['history']['events'])
            self.assertEqual(replays[0]['history']['snapshots'][d['history']['dates'][-1]],replays[1]['history']['snapshots'][d['history']['dates'][-1]])

    def test_alternate_valid_witness_is_accepted(self):
        r=deepcopy(self.result)
        for name,amounts in [('annual.cash_closing',(100,894)),('interim.cash_closing',(456,100))]:
            row=r['attachments'][name];w=examples.witness(row['definition'],*amounts)
            row['witness']=w;row['replay']=attachment.replay_witness(row['definition'],BUDGET,w)
        self.assertTrue(adapter.verify_result(self.body,BUDGET,r))

    def test_joint_incompatibility_does_not_reject_other_history(self):
        b=deepcopy(self.body);h=b['histories']['annual.cash_closing']['history']
        for event in h['events']:event['amount']=examples.domain(0)
        self.assertEqual(attachment.history.assess(h,BUDGET)['status'],'conditional_family_witness')
        r=adapter.assess(b,BUDGET)
        self.assertEqual(r['status'],'supplied_history_incompatible')
        self.assertEqual(r['attachments']['annual.cash_closing']['status'],'conditionally_infeasible')
        self.assertEqual(r['attachments']['interim.cash_closing']['candidate_feasibility'],'conditionally_feasible')
        self.assertTrue(adapter.verify_result(b,BUDGET,r))

    def test_missing_source_or_binding_premises_stay_unresolved(self):
        for kind in ['rounding','identity','mapping','history_mapping']:
            b=deepcopy(self.body)
            if kind=='rounding':b['source_request']['rounding_hypothesis']=None
            elif kind=='identity':b['source_request']['identity_hypotheses']['annual.cash_closing']=None
            elif kind=='mapping':b['source_request']['mapping_hypotheses']['annual.cash_closing']=None
            else:next(iter(b['histories']['annual.cash_closing']['bindings'].values()))['premise']=None
            r=adapter.assess(b,BUDGET);self.assertEqual(r['status'],'unresolved',(kind,r.get('reason')))
            self.assertNotIn('witness',r['attachments']['annual.cash_closing'])
            self.assertTrue(adapter.verify_result(b,BUDGET,r))

    def test_missing_or_crossed_mappings_refuse(self):
        b=deepcopy(self.body);b['histories']['annual.cash_closing']['bindings'].pop(next(iter(b['histories']['annual.cash_closing']['bindings'])))
        r=adapter.assess(b,BUDGET);self.assertEqual(r['status'],'invalid')
        self.assertTrue(adapter.verify_result(b,BUDGET,r))
        b=deepcopy(self.body);b['histories']['annual.cash_closing']['bindings']=deepcopy(b['histories']['interim.cash_closing']['bindings'])
        self.assertEqual(adapter.assess(b,BUDGET)['status'],'invalid')

    def test_same_date_is_not_authority_to_relabel_context(self):
        b=deepcopy(self.body);h=b['histories']['interim.cash_closing']['history']
        h['value_type']['context']=deepcopy(b['histories']['annual.cash_closing']['history']['value_type']['context'])
        r=adapter.assess(b,BUDGET);self.assertEqual(r['status'],'invalid_history_attachment')
        self.assertTrue(adapter.verify_result(b,BUDGET,r))

    def test_wrong_units_quantity_or_time_refuse(self):
        for field in ['scale','quantity','time']:
            b=deepcopy(self.body);row=next(iter(b['histories']['annual.cash_closing']['bindings'].values()))
            if field=='scale':row['terms'][0]['coefficient']['type']['scale']='1000/1'
            elif field=='quantity':row['quantity']='legal_cash'
            else:row['kind']='movement'
            r=adapter.assess(b,BUDGET);self.assertEqual(r['status'],'invalid_history_attachment')

    def test_source_request_tampering_refuses(self):
        b=deepcopy(self.body);b['source_request']['statement_request']['source']['request_sha256']='0'*64
        r=adapter.assess(b,BUDGET);self.assertEqual(r['status'],'invalid')
        self.assertTrue(adapter.verify_result(b,BUDGET,r))

    def test_budget_exhaustion_remains_unknown(self):
        budget={**BUDGET,'max_cells':0};r=adapter.assess(self.body,budget)
        self.assertEqual(r['status'],'unknown');self.assertTrue(adapter.verify_result(self.body,budget,r))
        for row in r['attachments'].values():self.assertNotIn('witness',row)

    def test_unselected_source_material_cannot_disappear(self):
        r=deepcopy(self.result);r['source_result']['preserved_report']['observations'].pop('annual.balance.cash')
        self.assertFalse(adapter.verify_result(self.body,BUDGET,r))
        r=deepcopy(self.result);r['source_result']['relation_dispositions'].pop()
        self.assertFalse(adapter.verify_result(self.body,BUDGET,r))

    def test_forged_admission_replay_and_counts_refuse(self):
        mutations=[lambda r:r.update(source_admission=True),lambda r:r.update(joint_cross_context_history=True),
            lambda r:r.update(source_observation_count=6),
            lambda r:r['attachments']['annual.cash_closing'].update(source_admission=True),
            lambda r:r['attachments']['annual.cash_closing']['definition']['obligations'].clear(),
            lambda r:r['attachments']['annual.cash_closing']['replay']['mapping_values'].clear()]
        for mutate in mutations:
            r=deepcopy(self.result);mutate(r);self.assertFalse(adapter.verify_result(self.body,BUDGET,r))

    def test_closed_request_and_complete_history_selection(self):
        for mutate in [lambda b:b.update(parent_witness={}),lambda b:b['histories'].pop('annual.cash_closing'),
                       lambda b:b['histories']['annual.cash_closing'].update(admitted=True)]:
            b=deepcopy(self.body);mutate(b);self.assertEqual(adapter.assess(b,BUDGET)['status'],'invalid')

    def test_single_bridge_selection_retains_full_report(self):
        b=deepcopy(self.body);s=b['source_request'];s['selected_relations']=['annual.cash_closing']
        for field in ['identity_hypotheses','mapping_hypotheses']:s[field].pop('interim.cash_closing')
        b['histories'].pop('interim.cash_closing');r=adapter.assess(b,BUDGET)
        self.assertEqual(r['status'],'conditional_candidates_with_unresolved_facts')
        self.assertEqual(r['source_observation_count'],256);self.assertEqual(len(r['attachments']),1)
        self.assertTrue(adapter.verify_result(b,BUDGET,r))

if __name__=='__main__':unittest.main()
