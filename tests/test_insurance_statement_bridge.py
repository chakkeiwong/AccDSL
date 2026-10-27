"""Composition evidence for existing fiscal and indirect statement engines."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('insurance_statement_examples',ROOT/'data/accounting-master/insurance-statement-bridge-20261025/examples.py')
ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)
bridge=ex.bridge


class InsuranceStatementBridgeTests(unittest.TestCase):
    def test_both_charts_cases_and_annual_reports(self):
        for chart in ['named','numbered']:
            for case in ['loss-service-finance','zero-loss-boundary']:
                row=ex.fixture(chart,case)
                for year in [2025,2026,2027]:ex.exchange(row,year)

    def test_alternative_splits_preserve_cash_and_financial_report(self):
        row=ex.fixture()
        for year in [2025,2026,2027]:
            a=ex.exchange(row,year);b=ex.exchange(row,year,'all_noncash')
            self.assertEqual(a['result']['financial_report'],b['result']['financial_report'])
            self.assertEqual(a['result']['direct_operating_cash'],b['result']['direct_operating_cash'])
            if year!=2025:
                self.assertNotEqual(a['result']['items']['working_capital'],b['result']['items']['working_capital'])

    def test_missing_zero_reversal_classification_refuses(self):
        row=ex.fixture(case='zero-loss-boundary');q=ex.exchange(row,2026)['request']
        reversal=row['request']['base_request']['roles']['loss_reversal']
        for method in q['policy']['methods'].values():method['profit_accounts'].pop(reversal,None)
        r=bridge.report(q);self.assertEqual(r['status'],'invalid')
        self.assertEqual(r['reason'],'exact_profit_posting_classification')

    def test_missing_liability_classification_has_no_residual(self):
        row=ex.fixture();q=ex.exchange(row,2026)['request']
        for method in q['policy']['methods'].values():method['accounts']={}
        r=bridge.report(q);self.assertEqual(r['status'],'unsupported')
        self.assertIn('exact_gross_posting_classification',r['reason']);self.assertNotIn('items',r)

    def test_stale_pre_fiscal_method_hash_refuses(self):
        row=ex.fixture();q=ex.exchange(row,2027)['request']
        delta=row['result']['transformations'][0]
        q['policy']['methods'][delta['before_sha256']]=q['policy']['methods'].pop(delta['after_sha256'])
        r=bridge.report(q);self.assertEqual(r['status'],'invalid');self.assertEqual(r['reason'],'exact_policy_methods')

    def test_cross_period_policy_refuses(self):
        row=ex.fixture();q=ex.exchange(row,2027)['request'];q['policy']=ex.policy(row,2026)
        r=bridge.report(q);self.assertEqual(r['status'],'invalid');self.assertEqual(r['reason'],'exact_policy_methods')

    def test_rehashed_altered_execution_refuses(self):
        row=ex.fixture();q=ex.exchange(row,2026)['request']
        q['result']['current']['memory']['insurance']['loss_component']='1/1'
        q['result_sha256']=bridge.core.digest(q['result'])
        r=bridge.report(q);self.assertEqual(r['status'],'invalid');self.assertEqual(r['reason'],'unverified_program_result')

    def test_replay_zero_year_and_forged_result(self):
        row=ex.fixture();x=ex.exchange(row,2025)
        self.assertEqual(x['request']['policy']['methods'],{});self.assertEqual(x['result']['events'],[])
        self.assertTrue(bridge.verify(x['request'],x['result']))
        bad=deepcopy(x['result']);bad['items']['noncash_profit']='1/1'
        self.assertFalse(bridge.verify(x['request'],bad))


if __name__=='__main__':unittest.main()
