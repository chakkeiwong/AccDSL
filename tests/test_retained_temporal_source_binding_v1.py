"""Exact fiscal source lineage without implicit same-date population merging."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import retained_temporal_source_binding_v1 as adapter
from test_joint_measurement_constraints_v1 import BUDGET


class RetainedTemporalSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request=adapter.fixture(assume=True)
        cls.result=adapter.assess(cls.request,BUDGET)
        assert cls.result['status']=='conditionally_feasible',cls.result.get('reason')

    def test_complete_report_and_exact_sources_preserved(self):
        r=self.result
        self.assertEqual(r['preserved_report'],adapter.source.statement.evaluate(self.request['statement_request']))
        self.assertEqual(len(r['preserved_report']['observations']),256)
        self.assertEqual(len(r['preserved_report']['relations']),143)
        self.assertEqual(len(r['definition']['observations']),6)
        self.assertEqual(len(r['definition']['relations']),2)
        self.assertEqual(sum(d['selected'] for d in r['relation_dispositions']),2)
        self.assertTrue(adapter.verify_result(self.request,BUDGET,r))

    def test_witness_against_original_signed_source_coefficients(self):
        r=self.result;w={k:Q(v) for k,v in r['temporal_assessment']['joint_assessment']['witness'].items()}
        report=r['preserved_report']['observations']
        for row in self.request['statement_request']['relations']:
            if row['id'] not in adapter.SUPPORTED:continue
            residual=Q(0)
            for side,sign in [('lhs',1),('rhs',-1)]:
                for term in row[side]:
                    item=report[term['alias']];key=item['declaration']['observation_ref']['digest']
                    residual+=sign*Q(term['coefficient'])*w[key]
                    amount=item['observation']['record']['body']['value']['amount']
                    d=Q(int(amount['n']),int(amount['d']));lo,hi=d-Q(1,2),d+Q(1,2)
                    self.assertTrue(w[key]>=lo if d>0 else w[key]>lo)
                    self.assertTrue(w[key]<=hi if d<0 else w[key]<hi)
            self.assertEqual(residual,0)

    def test_source_dates_kinds_and_original_context_retained(self):
        r=self.result;expected={
            'annual.cash_flow.opening':{'kind':'instant','at':'2023-09-30'},
            'annual.cash_flow.change':{'kind':'period','start':'2023-10-01','end_exclusive':'2024-09-29'},
            'annual.cash_flow.closing':{'kind':'instant','at':'2024-09-28'},
            'interim.cash_flow.opening':{'kind':'instant','at':'2024-09-28'},
            'interim.cash_flow.change':{'kind':'period','start':'2024-09-29','end_exclusive':'2024-12-29'},
            'interim.cash_flow.closing':{'kind':'instant','at':'2024-12-28'}}
        for key,mapping in r['source_mapping'].items():
            typ=r['definition']['observations'][key]['type'];alias=mapping['alias']
            self.assertEqual(typ['time'],expected[alias]);self.assertEqual(mapping['measurement_time'],expected[alias])
            self.assertEqual(mapping['original_context'],r['preserved_report']['observations'][alias]['observation']['context'])
            self.assertEqual(typ['value_type']['context'],{k:v for k,v in mapping['original_context'].items()
                if k not in ['unit','period','measurement_kind']})

    def test_equal_date_endpoints_do_not_merge_source_identity(self):
        r=self.result;aliases={v['alias']:k for k,v in r['source_mapping'].items()}
        a=aliases['annual.cash_flow.closing'];b=aliases['interim.cash_flow.opening']
        self.assertNotEqual(a,b)
        self.assertEqual(r['definition']['observations'][a]['type']['time'],r['definition']['observations'][b]['type']['time'])
        self.assertNotEqual(r['definition']['observations'][a]['type']['value_type']['context']['basis'],
                            r['definition']['observations'][b]['type']['value_type']['context']['basis'])
        self.assertEqual(len(r['temporal_assessment']['joint_assessment']['witness']),6)

    def test_no_assumption_is_silently_enabled(self):
        r=adapter.assess(adapter.fixture(),BUDGET);self.assertEqual(r['status'],'unresolved')
        self.assertNotIn('witness',r['temporal_assessment']['joint_assessment'])
        for field in ['rounding_hypothesis','identity_hypotheses','mapping_hypotheses']:
            body=deepcopy(self.request)
            if field=='rounding_hypothesis':body[field]=None
            else:body[field][adapter.SUPPORTED[0]]=None
            r=adapter.assess(body,BUDGET);self.assertEqual(r['status'],'unresolved')
            self.assertTrue(r['missing_hypotheses'])

    def test_mapping_and_identity_semantics_are_pinned(self):
        for collection in ['identity_hypotheses','mapping_hypotheses']:
            for field in ['id','meaning','status']:
                body=deepcopy(self.request);body[collection][adapter.SUPPORTED[0]][field]='changed'
                self.assertEqual(adapter.assess(body,BUDGET)['status'],'invalid')
        body=deepcopy(self.request);body['rounding_hypothesis']['mode']='half_even'
        self.assertEqual(adapter.assess(body,BUDGET)['status'],'invalid')

    def test_request_source_date_and_coefficient_tampering_rejected(self):
        def date_edit(body):
            o=next(x for x in body['statement_request']['observations'] if x['alias']=='annual.cash_flow.opening')
            o['measurement_time']['at']='2023-10-01'
        def coefficient_edit(body):
            r=next(x for x in body['statement_request']['relations'] if x['id']=='annual.cash_closing')
            r['lhs'][1]['coefficient']='-1/1'
        def source_edit(body):body['statement_request']['source']['request_sha256']='0'*64
        for mutate in [date_edit,coefficient_edit,source_edit]:
            body=deepcopy(self.request);mutate(body)
            self.assertEqual(adapter.assess(body,BUDGET)['status'],'invalid')

    def test_non_bridge_selections_and_missing_budgets_rejected(self):
        body=deepcopy(self.request);body['selected_relations']=['annual.closing_cash_population_match']
        self.assertEqual(adapter.assess(body,BUDGET)['status'],'invalid')
        self.assertEqual(adapter.assess(adapter.fixture([],True),BUDGET)['status'],'invalid')
        self.assertEqual(adapter.assess(self.request,{})['status'],'invalid')

    def test_replay_rejects_time_lowering_context_and_admission_tampering(self):
        def date_edit(r):next(iter(r['definition']['observations'].values()))['type']['time']['at']='2024-01-01'
        def lowering(r):r['temporal_assessment']['numeric_definition']['equations'][0]['terms'][0]['coefficient']='2/1'
        def context(r):next(iter(r['source_mapping'].values()))['original_context']['perimeter']='legal cash'
        def admission(r):r['source_admission']=True
        def omit(r):r['preserved_report']['observations'].pop('annual.balance.cash')
        for mutate in [date_edit,lowering,context,admission,omit]:
            r=deepcopy(self.result);mutate(r)
            self.assertFalse(adapter.verify_result(self.request,BUDGET,r))

    def test_valid_displayed_witness_and_unknown_budget(self):
        r=deepcopy(self.result);values={}
        for key,mapping in r['source_mapping'].items():
            amount=r['preserved_report']['observations'][mapping['alias']]['observation']['record']['body']['value']['amount']
            value=Q(int(amount['n']),int(amount['d']));values[key]=f'{value.numerator}/{value.denominator}'
        self.assertEqual(sorted(values.values()),sorted(['30737/1','-794/1','29943/1','29943/1','356/1','30299/1']))
        r['temporal_assessment']['joint_assessment']['witness']=values
        self.assertTrue(adapter.verify_result(self.request,BUDGET,r))
        unknown=adapter.assess(self.request,{**BUDGET,'max_cells':0})
        self.assertEqual(unknown['status'],'unknown');self.assertIsNone(unknown['executable_opening'])


if __name__=='__main__':unittest.main()
