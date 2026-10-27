from pathlib import Path
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import shared_book_statements_v1 as m
spec=importlib.util.spec_from_file_location('statement_examples',ROOT/'data/accounting-master/shared-book-statements-20261024/examples.py');e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)

class StatementTests(unittest.TestCase):
    def test_all_cases_preserve_requests_and_replay(self):
        for row in e.cases():
            body=row['request'];before=deepcopy(body);result=m.calculate(body)
            self.assertEqual(result['status'],row['expected_status'],row['case'])
            self.assertEqual(before,body);self.assertTrue(m.verify_result(body,result))
            self.assertTrue(all(result[k] is False for k in m.FLAGS))

    def test_mixed_views_have_independent_exact_expected_totals(self):
        r=m.calculate(e.cases()[0]['request']);b=r['balance_sheet_recorded'];cf=r['cash_flows_recorded']
        self.assertEqual(b['total_assets'],'701/1');self.assertEqual(b['total_liabilities'],'104/1')
        self.assertEqual(b['equity_including_recorded_profit'],'597/1')
        self.assertEqual(r['income_recorded']['recorded_profit'],'5/1')
        self.assertEqual(r['equity_recorded'],{'opening':'592/1','recorded_profit':'5/1','owner_movement':'0/1','closing':'597/1'})
        self.assertEqual(cf['closing_cash'],'361/1');self.assertEqual(cf['net_movement'],'-139/1')
        self.assertEqual(cf['activities']['operating'],{'receipts':'30/1','payments':'59/1','net':'-29/1'})
        self.assertEqual(cf['activities']['financing'],{'receipts':'0/1','payments':'110/1','net':'-110/1'})
        bridge=r['indirect_operating_recorded'];self.assertEqual(bridge['net'],'-29/1')
        self.assertEqual(bridge['items']['remove_lease_gain'],'-20/1');self.assertEqual(bridge['items']['depreciation'],'10/1')
        self.assertEqual(bridge['items']['change_recovery_asset'],'16/1');self.assertEqual(bridge['items']['change_refund_liability'],'-40/1')
        self.assertTrue(all(v=='0/1' for v in r['reconciliations'].values()))

    def test_failure_reports_completed_prefix_only(self):
        row=next(x for x in e.cases() if x['case']=='shared_cash_competition');r=m.calculate(row['request'])
        self.assertEqual(r['cash_flows_recorded']['closing_cash'],'82/1')
        self.assertEqual(r['coverage']['execution_status'],'stopped');self.assertEqual(r['coverage']['completed_events'],2)
        self.assertEqual(r['coverage']['unexecuted_events'],1);self.assertEqual(r['coverage']['last_completed_date'],'2024-02-01')
        self.assertEqual(r['coverage']['failed_event']['result']['status'],'funding_failure')
        self.assertEqual(r['income_recorded']['recorded_profit'],'16/1')

    def test_tax_and_period_are_never_promoted_from_balancing(self):
        for row in e.cases():
            r=m.calculate(row['request'])
            if r['status']!='recorded_prefix':continue
            for name in ['tax_assessment','annual_completion','period_completion']:self.assertEqual(r['coverage'][name],'unresolved')
            self.assertFalse(r['annual_close_ready']);self.assertFalse(r['complete_financial_statements'])
            self.assertEqual(r['income_recorded']['expenses']['current_tax'],'0/1')
            self.assertEqual(r['income_recorded']['tax_assessment'],'unresolved')

    def test_forged_result_fields_and_wrong_types_fail(self):
        body=e.cases()[0]['request'];r=m.calculate(body)
        for kind in ['profit','flow','memory','period','boolean','class','coverage']:
            x=deepcopy(r)
            if kind=='profit':x['income_recorded']['recorded_profit']='6/1'
            elif kind=='flow':x['cash_flows_recorded']['gross_origins']=[]
            elif kind=='memory':x['execution']['after']['lots']={}
            elif kind=='period':x['coverage']['annual_completion']='complete'
            elif kind=='boolean':x['committed']=0
            elif kind=='class':x['account_classes']['assets'].remove('rou')
            else:x['coverage']['completed_events']=4
            self.assertFalse(m.verify_result(body,x),kind)

    def test_outputs_do_not_mutate_account_registry(self):
        body=e.cases()[0]['request'];r=m.calculate(body);r['account_classes']['assets'].clear()
        self.assertIn('rou',m.calculate(body)['account_classes']['assets'])

    def test_stopped_first_event_retains_valid_opening_and_failure(self):
        row=next(x for x in e.cases() if x['case']=='unsupported_tax');r=m.calculate(row['request'])
        self.assertEqual(r['coverage']['completed_events'],0);self.assertEqual(r['cash_flows_recorded']['closing_cash'],'500/1')
        self.assertEqual(r['coverage']['failed_event']['result']['status'],'unsupported')

    def test_original_annual_report_still_requires_completed_tax(self):
        path=ROOT/'data/accounting-master/company-return-execution-20261024'
        sys.path.insert(0,str(path))
        spec=importlib.util.spec_from_file_location('original_annual_report_for_statement_test',path/'native_reports.py')
        native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
        row=e.execution.sources()['typed_return'];opening=deepcopy(row['before']);closing=deepcopy(row['native_result']['proposal']['after'])
        with self.assertRaises(Exception) as caught:native.report(opening,closing)
        self.assertEqual(getattr(caught.exception,'status',None),'unresolved')
        self.assertEqual(str(caught.exception),'annual tax incomplete')
        self.assertEqual(opening,row['before']);self.assertEqual(closing,row['native_result']['proposal']['after'])

if __name__=='__main__':unittest.main()
