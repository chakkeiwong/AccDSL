from pathlib import Path
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util
import json
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('tax_continuation_examples',
    ROOT/'data/accounting-master/shared-tax-continuation-20261024/examples.py')
x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x)
m=x.m


class ContinuationTests(unittest.TestCase):
    def test_mixed_independent_arithmetic_and_loss_identity(self):
        origin=x.origin();q=m.request(origin,x.mixed());r=m.run(q)
        self.assertEqual(r['status'],'complete');self.assertEqual(len(r['trace']),5)
        self.assertEqual(r['after']['balances']['cash'],'721/2')
        self.assertEqual(r['after']['balances']['income_tax_payable'],'0/1')
        self.assertEqual(r['after']['balances']['current_tax'],'1/2')
        self.assertEqual(r['recorded_statements']['recorded_profit'],'9/2')
        self.assertEqual(r['recorded_statements']['balance_sheet'],{
            'total_assets':'1401/2','total_liabilities':'104/1','equity_including_profit':'1193/2'})
        self.assertEqual(r['recorded_statements']['cash_flows']['activities']['operating']['net'],'-59/2')
        self.assertEqual(r['recorded_statements']['cash_flows']['activities']['financing']['net'],'-110/1')
        self.assertEqual(set(r['recorded_statements']['reconciliations'].values()),{'0/1'})
        self.assertEqual(r['loss_state'],origin['loss_state'])
        self.assertEqual(r['assessed_until'],'2025-01-01')
        self.assertEqual(r['after']['tax_adjustments'][-1]['amount'],'-24/1')
        self.assertEqual(r['after']['tax_closed_until'],'2024-01-01')

    def test_selected_native_journals_and_component_memory_match(self):
        origin=x.origin('0/1');base=m.tax.propose(origin['accrual_request'])['native_report']['execution']['after']
        operations=[x.ordinary(i) for i in [1,2,3,4]]
        native=m.book.run_prefix(base,[op['event'] for op in operations]);r=m.run(m.request(origin,operations))
        self.assertEqual((native['status'],r['status']),('complete','complete'))
        for old,new in zip(native['trace'],r['trace']):
            expected=old['result']['proposal']
            self.assertEqual(new['result']['journal'],{**expected['journal'],'income_tax_payable':'0/1'})
            self.assertEqual(new['result']['flows'],expected['flows'])
        for k in base:
            if k in ['profile','seen','balances']:continue
            self.assertEqual(r['after'][k],native['after'][k],k)
        self.assertEqual(r['after']['balances'],{**native['after']['balances'],'income_tax_payable':'0/1'})

    def test_tax_first_reduces_lease_funding(self):
        origin=x.origin(cash='485/4')
        control=m.run(m.request(origin,[x.ordinary(3)]))
        self.assertEqual(control['status'],'complete');self.assertEqual(control['after']['balances']['cash'],'1/4')
        r=m.run(m.request(origin,[x.payment(),x.ordinary(3),x.ordinary(4)]))
        self.assertEqual(r['status'],'stopped');self.assertEqual(r['stop']['status'],'funding_failure')
        self.assertEqual(len(r['trace']),1);self.assertEqual(len(r['remaining_operations']),2)
        self.assertEqual(r['after']['balances']['cash'],'483/4')
        self.assertEqual(r['after']['balances']['lease_liability'],'-110/1')

    def test_lease_first_reduces_tax_funding(self):
        r=m.run(m.request(x.origin(cash='485/4'),[x.ordinary(3),x.payment()]))
        self.assertEqual(r['status'],'stopped');self.assertEqual(r['stop']['status'],'funding_failure')
        self.assertEqual(r['after']['balances']['cash'],'1/4')
        self.assertEqual(r['after']['balances']['income_tax_payable'],'-1/2')
        self.assertEqual(r['after']['balances']['lease_liability'],'0/1')

    def test_assessment_endpoint_and_period_boundaries(self):
        origin=x.origin()
        for day in ['2024-12-31','2026-01-01']:
            r=m.run(m.request(origin,[x.ordinary(1,day)]))
            self.assertEqual(r['status'],'stopped');self.assertEqual(r['stop']['status'],'invalid')
        yes=m.run(m.request(origin,[x.ordinary(1,'2025-01-01')]))
        self.assertEqual(yes['status'],'complete')
        payment=m.run(m.request(origin,[x.payment(day='2024-12-31')]))
        self.assertEqual(payment['status'],'complete')

    def test_origin_prior_payment_preserved(self):
        origin=x.origin();q=m.tax.settlement_request(origin,'prepayment','2024-12-31','1/4',x.known())
        origin=m.tax.propose(q)['after'];r=m.run(m.request(origin,[x.payment('1/4')]))
        self.assertEqual(r['status'],'complete');self.assertEqual(r['after']['balances']['cash'],'999/2')
        self.assertEqual(r['after']['balances']['income_tax_payable'],'0/1')
        self.assertEqual([f['event_id'] for f in r['after']['flows']],['prepayment','tax-payment'])
        self.assertIn('prepayment',r['after']['seen'])

    def test_unknown_native_and_payment_findings(self):
        origin=x.origin();op=x.ordinary(1);op['event']['event']['inventory_nrv']='unknown'
        r=m.run(m.request(origin,[op]));self.assertEqual(r['stop']['status'],'unresolved')
        for value,status in [({'status':'unknown','reason':'Not instructed'},'unresolved'),(x.known(False),'unsupported')]:
            op=x.payment();op['event']['authorization']=value
            r=m.run(m.request(origin,[op]));self.assertEqual(r['stop']['status'],status)
            self.assertEqual(r['after']['balances']['cash'],'500/1')

    def test_duplicate_ids_overpayment_and_invalid_shape(self):
        origin=x.origin()
        operations=[[x.payment(identity='current-tax-assessment')],
                    [x.payment('1/4'),x.payment('1/4')],[x.payment('3/4')],
                    [{'kind':'tax_payment','event':{}}],[x.ordinary(0)],
                    [{'kind':'invented','event':{}}]]
        for ops in operations:
            with self.subTest(ops=ops):
                r=m.run(m.request(origin,ops));self.assertEqual(r['status'],'stopped')
        origin['balances']['cash']='501/1'
        self.assertEqual(m.run(m.request(origin,[]))['status'],'invalid')

    def test_complete_replay_and_stopped_prefix_apply(self):
        q=m.request(x.origin(),x.mixed());saved=deepcopy(q);r=m.run(q)
        self.assertEqual(q,saved);self.assertEqual(m.apply(q,r)['status'],'applied_prefix')
        for key,value in [('committed',0),('assessed_until','2026-01-01'),('loss_state',{})]:
            tampered=deepcopy(r);tampered[key]=value
            self.assertEqual(m.apply(q,tampered)['status'],'invalid')
        q=m.request(x.origin(),[x.payment(),x.payment()]);r=m.run(q)
        self.assertEqual(r['status'],'stopped');a=m.apply(q,r)
        self.assertEqual(a['status'],'applied_prefix');self.assertEqual(a['completed_operations'],1)
        self.assertEqual(a['after'],r['after'])

    def test_deferred_balances_and_tax_expense_survive_native_events(self):
        origin=x.origin();r=m.run(m.request(origin,[x.ordinary(i) for i in [1,2,3,4]]))
        self.assertEqual(r['status'],'complete')
        for key in ['dta','dtl','deferred_tax','current_tax','income_tax_payable']:
            self.assertEqual(r['after']['balances'][key],origin['balances'][key])
        self.assertEqual(r['after']['balances']['cash'],'361/1')
        self.assertEqual(r['recorded_statements']['indirect_operating']['net'],'-29/1')
        self.assertTrue(all(r[k] is False for k in m.FLAGS))

    def test_end_of_period_origin_has_no_ordinary_continuation(self):
        rows=json.loads((ROOT/'data/accounting-master/shared-tax-state-20261024/cases.json').read_text())
        origin=next(r['result']['after'] for r in rows if r['case']=='accrual_consume_19_from_21')
        for day in ['2026-12-31','2027-01-01']:
            r=m.run(m.request(origin,[x.ordinary(1,day)]))
            self.assertEqual(r['status'],'stopped');self.assertEqual(r['stop']['status'],'invalid')
            self.assertEqual(r['after']['balances'],origin['balances'])

    def test_chronological_prefix_and_generated_loss_preservation(self):
        origin=x.origin('-19/1');r=m.run(m.request(origin,[x.ordinary(1),x.ordinary(2)]))
        self.assertEqual(r['status'],'complete');self.assertEqual(r['loss_state'],origin['loss_state'])
        self.assertEqual(r['loss_state']['lots'][0]['remaining'],'19/1')
        q=m.request(x.origin(),[x.ordinary(1),x.payment(day='2024-12-31')]);r=m.run(q)
        self.assertEqual(r['status'],'stopped');self.assertEqual(len(r['trace']),1)
        self.assertEqual(r['stop']['reason'],'event_chronology')
        self.assertEqual(r['after']['balances']['cash'],'452/1')


if __name__=='__main__':unittest.main()
