"""Opening-population conflicts, full-network unknowns and exact preservation."""
from copy import deepcopy
from pathlib import Path
import importlib.util,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('network_history_examples_tests',ROOT/'data/accounting-master/retained-network-history-20261025/examples.py')
examples=importlib.util.module_from_spec(spec);spec.loader.exec_module(examples)
adapter=examples.adapter;BUDGET=examples.BUDGET

class RetainedNetworkHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body=examples.fixture();cls.result=adapter.assess(cls.body,BUDGET)
        assert cls.result['status']=='conditional_candidates_with_unresolved_facts',cls.result.get('reason')

    def test_closing_comparator_preserves_all_contexts_observations_and_equations(self):
        r=self.result
        self.assertEqual((r['selected_observations'],r['selected_relations'],r['context_count']),(60,20,2))
        self.assertTrue(adapter.verify_result(self.body,BUDGET,r))
        retained=r['source_result']['definition'];all_ids=[];all_relations=[]
        for key,a in r['attachments'].items():
            d=a['definition'];self.assertEqual(adapter.context_key(d['history']['value_type']['context']),key)
            all_ids+=list(d['measurements']['observations']);all_relations+=d['measurements']['relations']
            for name,item in d['measurements']['observations'].items():self.assertEqual(item,retained['observations'][name])
            self.assertEqual(len(d['bindings']),30);self.assertEqual(a['target_existence'],'unknown')
        self.assertEqual(set(all_ids),set(retained['observations']));self.assertEqual(len(all_ids),len(set(all_ids)))
        self.assertEqual({x['id']:x for x in all_relations},{x['id']:x for x in retained['relations']})

    def test_reported_opening_rejects_previously_closing_compatible_history(self):
        b=examples.fixture('opening',True);r=adapter.assess(b,BUDGET)
        self.assertEqual(r['source_result']['status'],'conditionally_feasible')
        self.assertEqual(r['status'],'supplied_history_incompatible')
        self.assertTrue(all(a['status']=='conditionally_infeasible' for a in r['attachments'].values()))
        self.assertTrue(adapter.verify_result(b,BUDGET,r))

    def test_opening_cash_population_difference_is_preserved(self):
        b=examples.fixture('opening',True);r=adapter.assess(b,BUDGET);report=r['source_result']['preserved_report']
        def value(alias):return report['observations'][alias]['observation']['record']['body']['value']['amount']['n']
        self.assertEqual(value('annual.opening.cash'),'29965');self.assertEqual(value('annual.cash_flow.opening'),'30737')
        maps=r['source_result']['source_mapping'];ids={a:k for k,m in maps.items() for a in m['aliases']}
        self.assertNotEqual(ids['annual.opening.cash'],ids['annual.cash_flow.opening'])
        a=r['source_result']['definition']['observations'][ids['annual.opening.cash']]
        z=r['source_result']['definition']['observations'][ids['annual.cash_flow.opening']]
        self.assertNotEqual(a['type']['quantity'],z['type']['quantity'])

    def test_unmapped_opening_equations_survive_without_becoming_history_facts(self):
        b=examples.fixture('opening');r=adapter.assess(b,BUDGET)
        self.assertEqual(r['status'],'conditional_candidates_with_unresolved_facts')
        self.assertEqual(r['selected_relations'],38)
        self.assertEqual(sum(len(a['unmapped_observations']) for a in r['attachments'].values()),54)
        self.assertTrue(adapter.verify_result(b,BUDGET,r))

    def test_equity_bridges_reject_constructed_openings(self):
        b=examples.fixture('equity',True);r=adapter.assess(b,BUDGET)
        self.assertEqual(r['status'],'supplied_history_incompatible')
        self.assertEqual(r['source_result']['status'],'conditionally_feasible')
        self.assertTrue(adapter.verify_result(b,BUDGET,r))

    def test_full_source_dash_remains_unresolved(self):
        b=examples.fixture('full');r=adapter.assess(b,BUDGET)
        self.assertEqual(r['status'],'unresolved')
        self.assertEqual((r['selected_observations'],r['selected_relations']),(236,101))
        findings=r['source_result']['unresolved_measurements']
        self.assertEqual(findings[0]['alias'],'annual.cash_flow.debt_issuance')
        self.assertEqual(findings[0]['literal'],'—')
        self.assertTrue(adapter.verify_result(b,BUDGET,r))

    def test_explicit_narrower_numeric_selection_does_not_claim_full_source(self):
        b=examples.fixture('numeric');r=adapter.assess(b,BUDGET)
        self.assertEqual(r['status'],'conditional_candidates_with_unresolved_facts')
        self.assertEqual((r['selected_observations'],r['selected_relations']),(229,100))
        self.assertEqual(r['source_result']['selection_coverage']['excluded_supported_relations'],['annual.financing_cash'])
        self.assertEqual(r['whole_source_compatibility'],'unresolved')
        self.assertTrue(adapter.verify_result(b,BUDGET,r))

    def test_missing_context_history_and_unknown_binding_refuse(self):
        for kind in ['missing','wrong_context','unknown_binding']:
            b=deepcopy(self.body);key=next(iter(b['histories']))
            if kind=='missing':b['histories'].pop(key)
            elif kind=='wrong_context':b['histories'][key]['history']['value_type']['context']['basis']='other'
            else:b['histories'][key]['bindings']['unseen']={}
            r=adapter.assess(b,BUDGET);self.assertEqual(r['status'],'invalid')
            self.assertTrue(adapter.verify_result(b,BUDGET,r))

    def test_missing_population_premise_and_no_budget_remain_distinct(self):
        b=deepcopy(self.body);selected=b['source_request']['selected_relations'][0]
        b['source_request']['mapping_hypotheses'][selected]=None
        r=adapter.assess(b,BUDGET);self.assertEqual(r['status'],'unresolved')
        self.assertTrue(adapter.verify_result(b,BUDGET,r))
        budget={**BUDGET,'max_cells':0};r=adapter.assess(self.body,budget)
        self.assertEqual(r['status'],'unknown');self.assertTrue(adapter.verify_result(self.body,budget,r))

    def test_forged_sources_constraints_admission_and_selection_refuse(self):
        changes=[lambda r:r.update(source_admission=True),lambda r:r.update(context_count=1),
            lambda r:r['source_result']['relation_dispositions'].pop(),
            lambda r:next(iter(r['attachments'].values()))['definition']['measurements']['relations'].pop(),
            lambda r:next(iter(r['attachments'].values()))['replay']['mapping_values'].clear()]
        for mutate in changes:
            r=deepcopy(self.result);mutate(r);self.assertFalse(adapter.verify_result(self.body,BUDGET,r))

if __name__=='__main__':unittest.main()
