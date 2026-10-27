"""Selected cross-statement constraints reject cash-only overinterpretation."""
from copy import deepcopy
from pathlib import Path
from fractions import Fraction as Q
import importlib.util,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('retained_statement_examples_tests',ROOT/'data/accounting-master/retained-statement-history-20261025/examples.py')
examples=importlib.util.module_from_spec(spec);spec.loader.exec_module(examples)
adapter=examples.adapter;attachment=adapter.attachment;BUDGET=examples.BUDGET

class RetainedStatementHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bodies={g:examples.fixture(g) for g in ['annual','interim']}
        cls.results={g:adapter.assess(b,BUDGET) for g,b in cls.bodies.items()}
        for r in cls.results.values():assert r['status']=='conditional_candidates_with_unresolved_facts',r.get('reason')

    def test_full_selected_balance_and_cash_parents_retained(self):
        for group,r in self.results.items():
            key=group+'.cash_closing';a=r['attachments'][key]
            self.assertEqual(len(a['definition']['measurements']['observations']),30)
            self.assertEqual(len(a['definition']['measurements']['relations']),10)
            self.assertEqual(len(a['definition']['bindings']),30)
            self.assertEqual(len(r['balance_parent']['preserved_report']['observations']),256)
            self.assertEqual(len(r['balance_parent']['relation_dispositions']),143)
            self.assertEqual(r['balance_parent']['preserved_report'],r['cash_parent']['source_result']['preserved_report'])
            self.assertTrue(adapter.verify_result(self.bodies[group],BUDGET,r))
            self.assertFalse(r['source_admission']);self.assertEqual(a['target_existence'],'unknown')

    def test_cash_only_candidate_fails_reported_equity(self):
        b=examples.fixture(conflicting=True);r=adapter.assess(b,BUDGET)
        self.assertEqual(r['cash_parent']['status'],'conditional_candidates_with_unresolved_facts')
        self.assertEqual(r['balance_parent']['status'],'conditionally_feasible')
        self.assertEqual(r['status'],'supplied_history_incompatible')
        self.assertEqual(r['attachments']['annual.cash_closing']['status'],'conditionally_infeasible')
        self.assertTrue(adapter.verify_result(b,BUDGET,r))

    def test_independent_source_caption_targets_and_alternate_gross_events(self):
        for group,r in self.results.items():
            key=group+'.cash_closing';row=r['attachments'][key];d=row['definition'];replays=[]
            report=r['balance_parent']['preserved_report']
            for extra in [0,100]:
                w=examples.witness(d,extra);replay=attachment.replay_witness(d,BUDGET,w);replays.append(replay)
                for obs,mapping in r['balance_parent']['source_mapping'].items():
                    expected=examples.values(report,mapping['aliases'][0])
                    self.assertEqual(Q(replay['mapping_values'][obs]),expected)
                for event in replay['history']['events']:
                    self.assertEqual(sum(map(Q,event['postings'].values())),0)
                    self.assertEqual(sum(map(Q,event['after']['accounts'].values())),0)
            self.assertEqual(replays[0]['mapping_values'],replays[1]['mapping_values'])
            self.assertNotEqual(replays[0]['history']['events'],replays[1]['history']['events'])
            alternate=deepcopy(r);a=alternate['attachments'][key]
            a['witness']=examples.witness(d,100);a['replay']=replays[1]
            self.assertTrue(adapter.verify_result(self.bodies[group],BUDGET,alternate))

    def test_all_source_equations_survive_time_conversion(self):
        for group,r in self.results.items():
            d=r['attachments'][group+'.cash_closing']['definition'];source=r['balance_parent']
            converted={x['id']:x for x in d['measurements']['relations']}
            for old in source['definition']['equations']:
                new=converted[old['id']]
                for field in ['terms','rhs','identity_premise']:self.assertEqual(new[field],old[field])
            for obs,mapping in source['source_mapping'].items():
                typ=d['measurements']['observations'][obs]['type'];original=mapping['original_context']
                self.assertEqual(typ['time'],mapping['measurement_time'])
                self.assertEqual(typ['value_type']['context'],{k:v for k,v in original.items() if k not in ['unit','period','measurement_kind']})
                self.assertEqual(typ['value_type']['scale'],'1000000/1')

    def test_unmapped_operands_preserve_equations_and_obligations(self):
        b=deepcopy(self.bodies['annual']);b['balance_bindings']['annual.cash_closing']={}
        r=adapter.assess(b,BUDGET);a=r['attachments']['annual.cash_closing']
        self.assertEqual(r['status'],'conditional_candidates_with_unresolved_facts')
        self.assertEqual(len(a['unmapped_observations']),27)
        self.assertEqual(len(a['definition']['measurements']['relations']),10)
        self.assertEqual(sum(o['origin']=='unmapped_measurement' for o in a['target_obligations']),27)
        self.assertTrue(adapter.verify_result(b,BUDGET,r))

    def test_unmapped_balance_operands_still_constrain_mapped_total(self):
        b=examples.fixture(conflicting=True)
        self.assertEqual(len(b['balance_bindings']['annual.cash_closing']),1)
        r=adapter.assess(b,BUDGET);a=r['attachments']['annual.cash_closing']
        self.assertEqual(len(a['unmapped_observations']),3)
        self.assertEqual(a['status'],'conditionally_infeasible')

    def test_missing_balance_premises_remain_unresolved(self):
        for mode in ['rounding','identity','mapping']:
            b=deepcopy(self.bodies['annual'])
            if mode=='rounding':b['balance_request']['rounding_hypothesis']=None
            elif mode=='identity':b['balance_request']['identity_hypotheses']['annual.balance:equity']=None
            else:next(iter(b['balance_bindings']['annual.cash_closing'].values()))['premise']=None
            r=adapter.assess(b,BUDGET);self.assertEqual(r['status'],'unresolved')
            self.assertTrue(adapter.verify_result(b,BUDGET,r))

    def test_no_budget_is_not_infeasibility(self):
        budget={**BUDGET,'max_cells':0};r=adapter.assess(self.bodies['annual'],budget)
        self.assertEqual(r['status'],'unknown');self.assertTrue(adapter.verify_result(self.bodies['annual'],budget,r))

    def test_context_scale_sign_and_quantity_do_not_change_implicitly(self):
        for field in ['context','scale','sign','quantity']:
            b=deepcopy(self.bodies['annual']);bindings=b['balance_bindings']['annual.cash_closing']
            row=next(x for x in bindings.values() if x['quantity'].endswith('.equity'))
            if field=='context':row['terms'][0]['coefficient']['type']['context']['basis']='another basis'
            elif field=='scale':row['terms'][0]['coefficient']['type']['scale']='1000/1'
            elif field=='quantity':row['quantity']='legal_equity'
            else:row['terms'][0]['coefficient']['value']='1/1'
            r=adapter.assess(b,BUDGET)
            self.assertEqual(r['status'],'supplied_history_incompatible' if field=='sign' else 'invalid_history_attachment')

    def test_different_reports_and_source_bytes_refuse(self):
        b=deepcopy(self.bodies['annual']);b['balance_request']['statement_request']['source']['request_sha256']='0'*64
        self.assertEqual(adapter.assess(b,BUDGET)['status'],'invalid')
        b['cash_request']['source_request']['statement_request']['source']['request_sha256']='0'*64
        self.assertEqual(adapter.assess(b,BUDGET)['status'],'invalid')

    def test_unsupported_group_and_unknown_binding_refuse(self):
        for mutate in [lambda b:b['balance_request']['selected_relations'].append('interim.balance:equity'),
                       lambda b:b['balance_bindings']['annual.cash_closing'].update(unknown={}),
                       lambda b:b.update(auto_merge_contexts=True)]:
            b=deepcopy(self.bodies['annual']);mutate(b);r=adapter.assess(b,BUDGET)
            self.assertEqual(r['status'],'invalid');self.assertTrue(adapter.verify_result(b,BUDGET,r))

    def test_forged_parent_constraint_replay_and_admission_refuse(self):
        changes=[lambda r:r.update(source_admission=True),
            lambda r:r['balance_parent']['definition']['equations'].pop(),
            lambda r:r['attachments']['annual.cash_closing']['definition']['measurements']['relations'].pop(),
            lambda r:r['cash_parent']['source_result']['preserved_report']['observations'].pop('annual.balance.cash'),
            lambda r:r['attachments']['annual.cash_closing']['replay']['mapping_values'].clear()]
        for mutate in changes:
            r=deepcopy(self.results['annual']);mutate(r)
            self.assertFalse(adapter.verify_result(self.bodies['annual'],BUDGET,r))

    def test_combined_request_keeps_two_distinct_source_contexts(self):
        b=examples.combined_fixture();r=adapter.assess(b,BUDGET)
        self.assertEqual(r['status'],'conditional_candidates_with_unresolved_facts')
        self.assertEqual(len(r['attachments']),2);self.assertFalse(r['joint_cross_context_history'])
        self.assertEqual(len(r['balance_parent']['definition']['observations']),54)
        self.assertEqual(len(r['balance_parent']['definition']['equations']),18)
        a,z=[r['attachments'][g+'.cash_closing']['definition'] for g in ['annual','interim']]
        self.assertNotEqual(a['history']['value_type']['context'],z['history']['value_type']['context'])
        self.assertTrue(adapter.verify_result(b,BUDGET,r))

if __name__=='__main__':unittest.main()
