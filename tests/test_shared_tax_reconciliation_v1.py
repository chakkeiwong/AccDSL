from copy import deepcopy
from fractions import Fraction as Q
import importlib.util
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import shared_tax_reconciliation_v1 as m
spec=importlib.util.spec_from_file_location('tax_reconciliation_examples',ROOT/'data/accounting-master/shared-tax-reconciliation-20261024/examples.py')
examples=importlib.util.module_from_spec(spec);spec.loader.exec_module(examples)

class ReconciliationTests(unittest.TestCase):
    def test_classifications_and_preservation(self):
        for row in examples.cases():
            with self.subTest(case=row['case']):
                before=m.book.digest(row['request']);r=m.calculate(row['request'])
                self.assertEqual(r['status'],row['expected_status'],r.get('reason'))
                self.assertTrue(all(r[k] is False for k in m.FLAGS))
                self.assertEqual(before,m.book.digest(row['request']))

    def test_independent_exact_arithmetic(self):
        for extra,expected in [('40/1','21/4'),('19/1','0/1'),('39/2','1/8')]:
            body=examples.control(extra);r=m.calculate(body);c=r['calculation']
            self.assertEqual(c['pretax_income'],'5/1')
            self.assertEqual(Q(c['signed_adjustments']),Q(-24)+Q(extra))
            self.assertEqual(Q(c['taxable_profit']),Q(5)-24+Q(extra))
            self.assertEqual(c['gross_current_tax'],expected)
            self.assertEqual(c['native_adjustment_ids'],['return_settlement'])
            self.assertEqual(sum(Q(v) for v in c['adjustment_totals'].values()),Q(c['signed_adjustments']))

    def test_loss_has_no_refund_or_tax_amount(self):
        body=examples.control();r=m.calculate(body)
        self.assertEqual(r['status'],'loss_route_required')
        self.assertEqual(r['calculation']['taxable_profit'],'-19/1')
        self.assertNotIn('gross_current_tax',r['calculation'])
        self.assertEqual(r['tax_cash_settlement'],'unresolved')
        self.assertFalse(r['cash_settled'])
        body['information_request']['information']['loss_route']['value']='refund automatically'
        self.assertEqual(m.calculate(examples.rehash(body))['status'],'loss_route_required')

    def test_every_native_item_required_once(self):
        body=examples.control('40/1')
        for mutate in ['missing','duplicate','amount','identity']:
            x=deepcopy(body)
            if mutate=='missing':x['allocations'].pop(0)
            elif mutate=='duplicate':
                item=deepcopy(x['allocations'][0]);item['id']='repeat';x['allocations'].append(item)
            elif mutate=='amount':x['allocations'][0]['amount']='0/1'
            else:x['allocations'][0]['origin']['event_id']='different'
            self.assertEqual(m.calculate(x)['status'],'invalid')

    def test_all_four_basis_identities(self):
        for when in ['opening','closing']:
            for side,account in [('asset','rou'),('liability','lease_liability')]:
                body=examples.control('40/1')
                body['information_request']['information']['basis/'+account+'/'+when]['value']='1/3'
                r=m.calculate(examples.rehash(body))
                self.assertEqual(r['status'],'invalid')
                self.assertEqual(r['reason'],'lease_basis_mismatch:'+when+':'+side)
                self.assertEqual(r['information_result']['native_report']['income_recorded']['recorded_profit'],'5/1')
                self.assertEqual(r['request'],body)

    def test_no_native_posting_or_reclassification(self):
        body=examples.control('40/1');r=m.calculate(body)
        native=r['information_result']['native_report']
        expected=m.information.reports.calculate(body['information_request']['report_request'])
        self.assertEqual(m.book.caller.canonical(native),m.book.caller.canonical(expected))
        self.assertEqual(native['cash_flows_recorded']['closing_cash'],'361/1')
        self.assertEqual(native['income_recorded']['recorded_profit'],'5/1')
        self.assertEqual(native['coverage']['tax_assessment'],'unresolved')
        self.assertNotIn('journal',r)

    def test_tampering_is_detected(self):
        body=examples.control('40/1');r=m.calculate(body)
        self.assertTrue(m.verify_result(body,r))
        for field in ['tax','flags','allocation','basis']:
            changed=deepcopy(r)
            if field=='tax':changed['calculation']['gross_current_tax']='6/1'
            elif field=='flags':changed['posted']=True
            elif field=='allocation':changed['request']['allocations'][0]['amount']='-23/1'
            else:changed['calculation']['basis_reconciliations']['closing_asset']['rights_total']='1/1'
            self.assertFalse(m.verify_result(body,changed))

    def test_closed_records_and_numeric_types(self):
        for kind in ['extra','float','boolean','unreduced','empty_origin','no_provenance']:
            body=examples.control('40/1')
            if kind=='extra':body['journal']={}
            elif kind=='float':body['allocations'][1]['amount']=40.0
            elif kind=='boolean':body['allocations'][1]['amount']=True
            elif kind=='unreduced':body['allocations'][1]['amount']='80/2'
            elif kind=='empty_origin':body['allocations'][1]['origin']['reference']=''
            else:del body['model']['selected']['provenance']
            self.assertEqual(m.calculate(body)['status'],'invalid')

if __name__=='__main__':unittest.main()
