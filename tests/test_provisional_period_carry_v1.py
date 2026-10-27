from pathlib import Path
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('provisional_carry_examples',ROOT/'data/accounting-master/provisional-period-carry-20261024/examples.py')
x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x);m=x.m


class CarryTests(unittest.TestCase):
    def test_return_activity_after_carry_uses_carried_component(self):
        r=m.run(x.unsettled_return());self.assertEqual(r['status'],'complete_provisional')
        self.assertFalse(r['opening']['component']['settled']);self.assertTrue(r['after']['component']['settled'])
        self.assertEqual(r['after']['balances']['cash'],'482/1')
        # Settlement contributes 4 - 8 = -4; resale contributes 30 - 20 = 10.
        self.assertEqual(r['recorded_statements']['recorded_profit'],'6/1')
        self.assertEqual(r['recorded_statements']['indirect_operating']['net'],'-18/1')
        self.assertEqual(sum(Q(a['amount']) for a in r['after']['tax_adjustments']),-24)
        self.assertEqual(set(r['recorded_statements']['reconciliations'].values()),{'0/1'})

    def test_used_loss_inventory_remains_exact(self):
        q=x.request();origin=x.previous.origin_with_opening_loss(use='1/1')
        q['prior_request']=x.previous.scenario('21/1',False,origin=origin,
            uses=[{'lot_id':'original-loss','amount':'19/1'}],cap='19/1')
        q['prior_sha256']=m.book.digest(q['prior_request'])
        r=m.run(q);self.assertEqual(r['status'],'complete_provisional')
        self.assertEqual(r['loss_state'],r['prior_result']['loss_state'])
        self.assertEqual(r['loss_state']['lots'][0]['used'],'19/1')
        self.assertEqual(r['loss_state']['lots'][0]['remaining'],'0/1')

    def test_recorded_loss_transfer_and_exact_opening(self):
        r=m.run(x.request());self.assertEqual(r['status'],'complete_provisional')
        b=r['opening']['balances'];prior=r['prior_result']['after']
        self.assertEqual(r['carried_recorded_profit'],'-1/4');self.assertEqual(b['retained'],'-47/4')
        self.assertEqual(b['cash'],'721/2');self.assertEqual(b['income_tax_payable'],'-19/4')
        income=r['prior_result']['continuation_result']['native_report']['account_classes']['income']
        self.assertTrue(all(b[k]=='0/1' for k in income))
        self.assertEqual(sum(Q(v) for v in r['carry_journal'].values()),0)
        for k,v in prior['balances'].items():
            if k not in income+['retained']:self.assertEqual(b[k],v,k)
        self.assertEqual(r['recorded_statements']['opening_equity'],'2367/4')
        self.assertEqual(r['recorded_statements']['recorded_profit'],'0/1')

    def test_positive_and_zero_profit_transfer(self):
        positive=m.run(x.request('0/1',False));self.assertEqual(positive['status'],'complete_provisional')
        self.assertEqual(positive['carried_recorded_profit'],'5/1')
        self.assertEqual(positive['opening']['balances']['retained'],'-17/1')
        zero=m.run(x.request('20/1',False));self.assertEqual(zero['status'],'complete_provisional')
        self.assertEqual(zero['carried_recorded_profit'],'0/1');self.assertEqual(zero['opening']['balances']['retained'],'-12/1')

    def test_pay_carried_liability_without_repeating_expense(self):
        r=m.run(x.request(operations=[x.payment()]));self.assertEqual(r['status'],'complete_provisional')
        self.assertEqual(r['after']['balances']['cash'],'1423/4')
        self.assertEqual(r['after']['balances']['income_tax_payable'],'0/1')
        self.assertEqual(r['after']['balances']['current_tax'],'0/1')
        self.assertEqual(r['recorded_statements']['recorded_profit'],'0/1')
        self.assertEqual(r['recorded_statements']['indirect_operating']['net'],'-19/4')
        self.assertEqual(len(r['after']['flows']),1)
        self.assertEqual(r['recorded_statements']['cash_flows']['opening_cash'],'721/2')

    def test_payment_and_depreciation_use_new_opening(self):
        r=m.run(x.request(operations=[x.payment(),x.depreciation()]))
        self.assertEqual(r['status'],'complete_provisional')
        self.assertEqual(r['recorded_statements']['recorded_profit'],'-10/1')
        self.assertEqual(r['recorded_statements']['balance_sheet'],{
            'total_assets':'2743/4','total_liabilities':'104/1','equity_including_profit':'2327/4'})
        self.assertEqual(r['recorded_statements']['indirect_operating']['net'],'-19/4')
        self.assertEqual(set(r['recorded_statements']['reconciliations'].values()),{'0/1'})

    def test_archive_and_component_identity(self):
        r=m.run(x.request());old=r['prior_result']['after'];new=r['opening']
        self.assertEqual(new['flows'],[]);self.assertEqual(new['tax_adjustments'],[])
        self.assertEqual(r['archive']['prior_flows'],old['flows'])
        self.assertEqual(r['archive']['prior_tax_adjustments'],old['tax_adjustments'])
        self.assertEqual(r['archive']['prior_tax_adjustments'][-1]['amount'],'-24/1')
        for k in ['lots','component','leases','opening_interest_remaining','other_inventory']:
            self.assertEqual(new[k],old[k],k)
        self.assertEqual(new['seen'],old['seen']+['carry-2026'])
        self.assertEqual(new['prior_years'][-1]['closing_sha256'],m.book.digest(old))
        self.assertEqual(new['tax_premises']['opening_dta'],old['balances']['dta'])
        self.assertEqual(new['tax_premises']['opening_dtl'],'4/1')

    def test_loss_history_preserved(self):
        r=m.run(x.request('-19/1',False));self.assertEqual(r['status'],'complete_provisional')
        self.assertEqual(r['loss_state'],r['prior_result']['loss_state'])
        self.assertEqual(r['loss_state']['lots'][0]['remaining'],'19/1')
        self.assertEqual(r['loss_state']['cursor'],'2026-01-01')
        self.assertEqual(r['opening']['balances']['dta'],'10/1')

    def test_unknown_false_true_findings_never_promote(self):
        for value,label in [(None,'unresolved'),(False,'asserted_false'),(True,'asserted_true')]:
            finding={k:({'status':'unknown','reason':'Missing'} if value is None else x.known(value)) for k in m.FINDINGS}
            r=m.run(x.request(findings=finding));self.assertEqual(r['status'],'complete_provisional')
            self.assertEqual(set(r['finding_status'].values()),{label});self.assertEqual(r['findings'],finding)
            self.assertTrue(r['provisional']);self.assertFalse(r['annual_close_ready'])
            self.assertFalse(r['complete_financial_statements']);self.assertEqual(r['unresolved'],m.OBLIGATIONS)
            self.assertEqual(r['current_period_tax'],'unassessed')

    def test_strict_annual_model_and_invalid_findings(self):
        q=x.request();q['model']['profile']='strict_annual_close_v1'
        r=m.run(q);self.assertEqual(r['status'],'unsupported');self.assertFalse(r['recorded_balance_carry'])
        q=x.request();q['findings']['event_coverage']=x.known(1);self.assertEqual(m.run(q)['status'],'invalid')
        q=x.request();q['findings'].pop('deferred_tax_assessment');self.assertEqual(m.run(q)['status'],'invalid')

    def test_period_gap_overlap_and_incomplete_assessment(self):
        q=x.request()
        for start in ['2025-12-31','2026-01-02']:
            body=deepcopy(q);body['next_period']['start']=start;self.assertEqual(m.run(body)['status'],'invalid')
        body=deepcopy(q);body['next_period']['end_exclusive']='2026-01-01';self.assertEqual(m.run(body)['status'],'invalid')
        body=deepcopy(q);body['prior_request']['interval'].update(end_exclusive='2025-07-01',activity_through='2025-06-30')
        body['prior_sha256']=m.book.digest(body['prior_request'])
        r=m.run(body);self.assertEqual(r['status'],'unresolved');self.assertEqual(r['reason'],'current_tax_or_loss_interval_incomplete')

    def test_duplicate_event_ids_and_period_dates(self):
        for op in [x.payment(identity='tax-payment'),x.payment(identity='carry-2026'),
                   x.payment(day='2025-12-31'),x.payment(day='2027-01-01')]:
            r=m.run(x.request(operations=[op]));self.assertEqual(r['status'],'stopped_provisional')
            self.assertEqual(r['stop']['status'],'invalid');self.assertEqual(r['after'],r['opening'])
        q=x.request();q['id']='tax-payment';self.assertEqual(m.run(q)['status'],'invalid')

    def test_shared_funding_and_stopped_prefix(self):
        r=m.run(x.request('2000/1',True,operations=[x.payment('999/2')]))
        self.assertEqual(r['status'],'stopped_provisional');self.assertEqual(r['stop']['status'],'funding_failure')
        self.assertEqual(r['after'],r['opening'])
        r=m.run(x.request(operations=[x.payment('1/1'),x.payment('5/1',identity='overpay')]))
        self.assertEqual(r['status'],'stopped_provisional');self.assertEqual(len(r['trace']),1)
        self.assertEqual(r['after']['balances']['cash'],'719/2')
        self.assertEqual(r['after']['balances']['income_tax_payable'],'-15/4')
        self.assertEqual(len(r['remaining_operations']),1)

    def test_full_apply_retains_uncertainty_and_archive(self):
        q=x.request(operations=[x.payment(),x.depreciation()]);before=deepcopy(q);r=m.run(q)
        self.assertEqual(q,before);applied=m.apply(q,r);self.assertEqual(applied['status'],'applied_provisional')
        for key in ['after','opening','loss_state','findings','unresolved','archive','prior_result']:
            self.assertEqual(applied[key],r[key],key)
        for key,value in [('annual_close_ready',True),('unresolved',[]),('archive',{}),('committed',0)]:
            altered=deepcopy(r);altered[key]=value;self.assertEqual(m.apply(q,altered)['status'],'invalid')
        q['prior_sha256']='0'*64;self.assertEqual(m.run(q)['status'],'invalid')


if __name__=='__main__':unittest.main()
