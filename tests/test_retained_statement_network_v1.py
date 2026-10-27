"""Joint statement context fidelity, honest scope, and exact original arithmetic."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import retained_statement_network_v1 as network
import retained_temporal_source_binding_v1 as cash
from test_joint_measurement_constraints_v1 import BUDGET


class StatementNetworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.full_request=network.fixture(assume=True)
        cls.full=network.assess(cls.full_request,BUDGET)
        assert cls.full['status']=='unresolved',cls.full.get('reason')
        selected=network.numeric_selection(cls.full_request['statement_request'],cls.full['preserved_report'])
        cls.request=network.fixture(selected,True);cls.result=network.assess(cls.request,BUDGET)
        assert cls.result['status']=='conditionally_feasible',cls.result.get('reason')

    def test_full_request_keeps_dash_and_never_solves_a_hidden_subset(self):
        r=self.full;c=r['selection_coverage']
        self.assertEqual((c['selected_relations'],c['selected_observations']),(101,236))
        self.assertTrue(c['all_supported_selected']);self.assertEqual(c['excluded_supported_relations'],[])
        self.assertEqual(len(r['unresolved_measurements']),1)
        finding=r['unresolved_measurements'][0]
        self.assertEqual(finding['alias'],'annual.cash_flow.debt_issuance')
        self.assertEqual(finding['literal'],'—');self.assertEqual(finding['source_value']['tag'],'reported_dash')
        self.assertNotIn('solver_status',r['temporal_assessment']['joint_assessment'])
        self.assertIsNone(r['definition']['observations'][finding['observation']]['interval'])

    def test_narrower_request_names_exclusion_and_preserves_every_record(self):
        r=self.result;c=r['selection_coverage']
        self.assertEqual((c['selected_relations'],c['selected_observations']),(100,229))
        self.assertFalse(c['all_supported_selected']);self.assertFalse(c['whole_statement_history_complete'])
        self.assertEqual(c['excluded_supported_relations'],['annual.financing_cash'])
        self.assertEqual(r['preserved_report'],self.full['preserved_report'])
        self.assertEqual(len(r['preserved_report']['observations']),256)
        self.assertEqual(len(r['relation_dispositions']),143)
        self.assertEqual(len(r['preserved_report']['relations']),143)
        self.assertTrue(network.verify_result(self.request,BUDGET,r))

    def test_witness_satisfies_every_original_source_equation_and_signed_bound(self):
        r=self.result;w={k:Q(v) for k,v in r['temporal_assessment']['joint_assessment']['witness'].items()}
        observed=r['preserved_report']['observations'];used=set()
        for row in self.request['statement_request']['relations']:
            if row['id'] not in self.request['selected_relations']:continue
            residual=Q(0)
            for side,sign in [('lhs',1),('rhs',-1)]:
                for term in row[side]:
                    item=observed[term['alias']];key=item['declaration']['observation_ref']['digest'];used.add(key)
                    residual+=sign*Q(term['coefficient'])*w[key]
                    amount=item['observation']['record']['body']['value']['amount']
                    d=Q(int(amount['n']),int(amount['d']));low,high=d-Q(1,2),d+Q(1,2)
                    self.assertTrue(w[key]>=low if d>0 else w[key]>low)
                    self.assertTrue(w[key]<=high if d<0 else w[key]<high)
            self.assertEqual(residual,0,row['id'])
        self.assertEqual(used,set(w));self.assertEqual(len(w),229)

    def test_shared_observations_recur_across_relations_without_merging(self):
        r=self.result
        self.assertTrue(any(len(m['relation_ids'])>=4 for m in r['source_mapping'].values()))
        for key,mapping in r['source_mapping'].items():
            typ=r['definition']['observations'][key]['type']
            self.assertEqual(typ['time'],mapping['measurement_time'])
            self.assertEqual(key,mapping['observation_ref']['digest'])
            self.assertEqual(typ['value_type']['context'],{k:v for k,v in mapping['original_context'].items()
                if k not in ['unit','period','measurement_kind']})
        keys={a:key for key,m in r['source_mapping'].items() for a in m['aliases']}
        self.assertNotEqual(keys['annual.cash_flow.closing'],keys['interim.cash_flow.opening'])
        self.assertNotEqual(keys['annual.balance.cash'],keys['annual.cash_flow.closing'])

    def test_omitted_rows_excluded_with_original_dispositions(self):
        rows={x['id']:x for x in self.full['relation_dispositions']}
        for key in ['interim.capital','interim.financing_cash','interim.whole_equity_bridge']:
            self.assertEqual(rows[key]['status'],'omitted_source_rows_require_separate_interpretation')
            self.assertTrue(rows[key]['omitted_source_rows']);self.assertFalse(rows[key]['selected'])
            request=network.fixture([key],True)
            self.assertEqual(network.assess(request,BUDGET)['status'],'invalid')

    def test_unsupported_relation_forms_are_never_asserted(self):
        rows={x['id']:x for x in self.full['relation_dispositions']}
        unsupported=[x for x in rows.values() if x['classification']=='outside_relation_forms']
        self.assertEqual(len(unsupported),39)
        for key in ['annual.closing_cash_population_match','annual.other_equity_movements','annual.balance_changes']:
            self.assertFalse(rows[key]['selected'])
            self.assertEqual(network.assess(network.fixture([key],True),BUDGET)['status'],'invalid')

    def test_rounding_identity_and_population_assumptions_all_optional(self):
        for field in ['rounding_hypothesis','identity_hypotheses','mapping_hypotheses']:
            body=deepcopy(self.request)
            if field=='rounding_hypothesis':body[field]=None
            else:body[field][body['selected_relations'][0]]=None
            result=network.assess(body,BUDGET)
            self.assertEqual(result['status'],'unresolved');self.assertTrue(result['missing_hypotheses'])
        self.assertEqual(network.assess(network.fixture(),BUDGET)['status'],'unresolved')

    def test_source_terms_context_times_and_premises_cannot_be_altered(self):
        def coefficient(b):b['statement_request']['relations'][0]['lhs'][0]['coefficient']='2/1'
        def time(b):b['statement_request']['observations'][0]['measurement_time']={'kind':'instant','at':'2000-01-01'}
        def unit(b):b['statement_request']['observations'][0]['unit']='USD'
        def premise(b):b['mapping_hypotheses'][b['selected_relations'][0]]['meaning']='same legal cash'
        for mutate in [coefficient,time,unit,premise]:
            body=deepcopy(self.request);mutate(body)
            self.assertEqual(network.assess(body,BUDGET)['status'],'invalid')

    def test_forged_scope_definition_source_or_witness_fails_replay(self):
        def scope(r):r['selection_coverage']['all_supported_selected']=True
        def omit(r):r['relation_dispositions'].pop()
        def source(r):r['preserved_report']['observations'].pop('annual.cash_flow.debt_issuance')
        def lowering(r):r['temporal_assessment']['numeric_definition']['equations'][0]['terms'][0]['coefficient']='2/1'
        def witness(r):r['temporal_assessment']['joint_assessment']['witness'][next(iter(r['definition']['observations']))]='0/1'
        for mutate in [scope,omit,source,lowering,witness]:
            r=deepcopy(self.result);mutate(r)
            self.assertFalse(network.verify_result(self.request,BUDGET,r))

    def test_checked_balance_comparator_preserves_terms_and_intervals(self):
        selected=list(network.source.SUPPORTED)
        r=network.assess(network.fixture(selected,True),BUDGET)
        old=network.source.assess(network.source.fixture(selected,True),BUDGET)
        self.assertEqual(r['status'],old['status'])
        new=r['temporal_assessment']['numeric_definition'];prior=old['definition']
        self.assertEqual(set(new['observations']),set(prior['observations']))
        for key in new['observations']:
            for field in ['interval','interval_premise','source_ref']:
                self.assertEqual(new['observations'][key][field],prior['observations'][key][field])
        for a,b in zip(new['equations'],prior['equations']):
            self.assertEqual(a['id'],b['id']);self.assertEqual(a['terms'],b['terms']);self.assertEqual(a['rhs'],b['rhs'])

    def test_checked_cash_bridge_comparator_preserves_lowering(self):
        r=network.assess(network.fixture(list(cash.SUPPORTED),True),BUDGET)
        old=cash.assess(cash.fixture(assume=True),BUDGET)
        self.assertEqual(r['status'],old['status'])
        a=r['temporal_assessment']['numeric_definition'];b=old['temporal_assessment']['numeric_definition']
        self.assertEqual(a['observations'],b['observations'])
        for new,prior in zip(a['equations'],b['equations']):
            self.assertEqual(new['terms'],prior['terms']);self.assertEqual(new['rhs'],prior['rhs'])

    def test_unknown_resource_limits_and_boundaries_remain_explicit(self):
        r=network.assess(self.request,{**BUDGET,'max_cells':0})
        self.assertEqual(r['status'],'unknown');self.assertNotIn('witness',r['temporal_assessment']['joint_assessment'])
        for result in [self.full,self.result,r]:
            self.assertIsNone(result['executable_opening']);self.assertEqual(result['actual_history'],'unknown')
            self.assertFalse(result['executed']);self.assertFalse(result['source_admission']);self.assertFalse(result['accounting_admission'])


if __name__=='__main__':unittest.main()
