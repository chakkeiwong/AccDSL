from copy import deepcopy
from pathlib import Path
import importlib.util
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import group_period_report_v1 as group
spec=importlib.util.spec_from_file_location('group_period_examples',ROOT/'data/accounting-master/group-period-report-20261025/examples.py')
ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)

class GroupPeriodReportTests(unittest.TestCase):
    def checked(self,body,reason=None):
        before=deepcopy(body);r=group.report(body);self.assertEqual(body,before)
        self.assertEqual(r['status'],'invalid' if reason else 'period_reported',r)
        if reason:self.assertEqual(r['reason'],reason)
        for key in group.FLAGS:self.assertIs(r[key],False)
        return r

    def test_four_cases_and_gross_legal_flows_preserved(self):
        cases=ex.cases();self.assertEqual(len(cases),4)
        for row in cases.values():
            self.assertEqual(len(row['result']['raw_cash_flows']['origins']),3)
            self.assertEqual(row['result']['closing_worksheet']['books'],row['request']['closing']['books'])

    def test_missing_pair_is_not_inferred_from_balanced_net_cash(self):
        body=ex.fixture();body['internal_cash_pairs']=[];r=self.checked(body)
        self.assertEqual(len(r['cash_flows']['origins']),3)
        self.assertEqual(r['cash_flows']['activities']['investing']['payments'],'30/1')
        self.assertIn('Truth and completeness of supplied internal-transfer pairs',r['unresolved'])

    def test_stale_duplicate_and_unknown_cash_references(self):
        body=ex.fixture();body['internal_cash_pairs'][0]['payer']['expected_flow_sha256']='0'*64;self.checked(body,'stale_cash_flow')
        body=ex.fixture();body['internal_cash_pairs'][0]['payer']['flow_id']='missing';self.checked(body,'missing_cash_flow')
        body=ex.fixture();body['internal_cash_pairs'].append(deepcopy(body['internal_cash_pairs'][0]));self.checked(body,'duplicate_cash_pair')
        body=ex.fixture();row=deepcopy(body['internal_cash_pairs'][0]);row['id']='again';body['internal_cash_pairs'].append(row);self.checked(body,'reused_cash_flow')

    def test_customer_receipt_cannot_cancel_different_amount(self):
        body=ex.fixture();flow=body['closing']['books']['S']['flows'][1]
        body['internal_cash_pairs'][0]['payee'].update(flow_id=flow['id'],expected_flow_sha256=group.core.digest(flow))
        self.checked(body,'opposite_full_cash_pair')

    def test_different_dates_refuse_after_legal_reports_pass(self):
        body=ex.fixture();flow=body['closing']['books']['S']['flows'][0];flow['date']='2025-07-01'
        body['internal_cash_pairs'][0]['payee']['expected_flow_sha256']=group.core.digest(flow);ex.refresh(body)
        self.checked(body,'cash_pair_date')

    def test_legal_book_and_flow_population_must_match(self):
        body=ex.fixture();body['legal_reports']['P']['closing']['memory']['origin']='S-state';self.checked(body,'legal_closing_binding')
        body=ex.fixture();body['closing']['books']['S']['flows'].pop();ex.refresh(body)
        self.checked(body,'legal_report:statement_reconciliation')
        body=ex.fixture();body['closing']['books']['S']['seen'].pop();ex.refresh(body)
        self.checked(body,'closing_worksheet:flow_event')

    def test_period_perimeter_and_policy_changes_refuse(self):
        body=ex.fixture();body['closing']['compatibility']['accounting_policies']='Changed policy';self.checked(body,'period_compatibility:compatibility')
        body=ex.fixture();body['closing']['world']['control_edges'][0]['start']='2025-02-01';self.checked(body,'period_world:control_edges')
        body=ex.fixture();body['closing']['world']['context']['world_id']='changed';self.checked(body,'period_world:context')

    def test_missing_closing_reciprocal_elimination_is_visible(self):
        body=ex.fixture();body['closing']['eliminations']=body['closing']['eliminations'][1:];r=self.checked(body)
        self.assertEqual(r['closing_worksheet']['adjusted_totals']['assets'],'250/1')
        self.assertEqual(r['closing_worksheet']['adjusted_totals']['liabilities'],'30/1')
        self.assertFalse(r['consolidation_complete'])

    def test_missing_investment_elimination_breaks_group_equity(self):
        body=ex.fixture();body['closing']['eliminations']=body['closing']['eliminations'][:1]
        self.checked(body,'group_period_reconciliation')

    def test_false_balance_adjustment_never_mutates_inputs(self):
        body=ex.fixture();body['closing']['eliminations'][0]['positive']['expected_balance']='29/1'
        self.checked(body,'closing_worksheet:stale_elimination_balance')

    def test_replay_checks_full_legal_and_group_results(self):
        body=ex.fixture();r=self.checked(body);self.assertTrue(group.verify(body,r))
        for key,value in [('cash_flows',{}),('legal_reports',{}),('fiscal_complete',True),('executed',0)]:
            changed=deepcopy(r);changed[key]=value;self.assertFalse(group.verify(body,changed))

    def test_structure_limit_and_dependency_pin(self):
        from unittest.mock import patch
        with patch.dict(group.PINS,{'company_book_reports_v1.py':'0'*64}):self.checked(ex.fixture(),'dependency_hash:company_book_reports_v1.py')
        body=ex.fixture();body['internal_cash_pairs'].append(body)
        self.assertEqual(group.report(body)['reason'],'record_structure_limit')

    def test_reversed_signs_and_same_book_pairs_refuse(self):
        body=ex.fixture();pair=body['internal_cash_pairs'][0];pair['payer'],pair['payee']=pair['payee'],pair['payer']
        self.checked(body,'opposite_full_cash_pair')
        body=ex.fixture();book=body['closing']['books']['P'];original=book['flows'][0]
        for name,amount in [('extra-in','30/1'),('extra-out','-30/1')]:
            f={**deepcopy(original),'id':name,'event_id':name+'-event','amount':amount}
            book['flows'].append(f);book['seen'].append(f['event_id'])
        flow=book['flows'][1];body['internal_cash_pairs'][0]['payee']={'owner':'P','flow_id':flow['id'],'expected_flow_sha256':group.core.digest(flow)}
        ex.refresh(body);self.checked(body,'cross_book_cash_pair')

    def test_opening_and_report_population_requirements(self):
        body=ex.fixture();del body['legal_reports']['S'];self.checked(body,'exact_legal_reports')
        body=ex.fixture()
        for book in body['opening']['books'].values():book['date']='2025-01-02'
        ex.refresh(body);self.checked(body,'legal_report:opening_at_period_start')
        body=ex.fixture();body['closing']['books']['S']['flows'][0]['event_id']=body['opening']['books']['S']['seen'][0]
        ex.refresh(body);self.checked(body,'legal_report:current_period_flow_event')

if __name__=='__main__':unittest.main()
