from pathlib import Path
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
s=importlib.util.spec_from_file_location('period_vintage_examples',ROOT/'data/accounting-master/period-vintage-continuation-20261024/examples.py')
x=importlib.util.module_from_spec(s);s.loader.exec_module(x);m=x.m

class PeriodVintageContinuationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body=x.scenario();cls.result=m.run(cls.body)
        assert cls.result['status']=='complete_provisional',cls.result.get('reason')

    def test_independent_split_and_depreciation(self):
        r=self.result;b=r['after']['balances'];p=r['recorded_statements']
        self.assertEqual(len(b),26)
        for k,v in {'cash':'709/2','rou':'76/1','income_tax_payable':'-23/4','retained':'53/4',
                    'current_tax':'0/1','deferred_tax':'0/1','dta':'5/1','dtl':'-5/1'}.items():self.assertEqual(b[k],v,k)
        self.assertEqual([v['closing_payable'] for v in r['period_vintages']],['11/4','3/1'])
        self.assertEqual(p['recorded_profit'],'-2/1')
        self.assertEqual(p['balance_sheet'],{'total_assets':'1351/2','total_liabilities':'443/4','equity_including_profit':'2259/4'})
        self.assertEqual(p['indirect_operating']['net'],'-3/1')
        self.assertEqual(set(p['reconciliations'].values()),{'0/1'})
        self.assertEqual(r['unassessed_native_events'],['period-depreciation'])

    def test_empty_period_does_not_replay_old_payments(self):
        r=m.run(x.scenario([]))
        self.assertEqual(r['after'],r['opening']);self.assertEqual(r['after']['flows'],[])
        self.assertEqual([len(v['settlements']) for v in r['tax_vintages']],[1,1])
        self.assertEqual([v['settlements'] for v in r['period_vintages']],[[],[]])
        self.assertEqual(r['recorded_statements']['indirect_operating']['net'],'0/1')

    def test_exact_historical_records_and_complete_boundary(self):
        r=self.result;p=m.boundary.run(self.body['boundary_request'])
        self.assertEqual(m.caller.canonical(r['boundary_result']),m.caller.canonical(p))
        for k in ['opening','tax_vintages','loss_state','archive','findings','finding_status','prior_findings']:
            self.assertEqual(m.caller.canonical(r[k]),m.caller.canonical(p[k]),k)
        self.assertTrue(r['tax_vintages'][1]['supersession_history'])
        self.assertEqual(r['current_period_tax'],r['current_period_deferred_tax'])
        self.assertEqual(r['current_period_tax'],'unassessed')

    def test_equal_cash_different_liabilities(self):
        a=m.run(x.scenario([x.payment(old='3/1',new='0/1')]))
        b=m.run(x.scenario([x.payment(old='0/1',new='3/1')]))
        self.assertEqual(a['after']['balances'],b['after']['balances'])
        self.assertEqual([v['closing_payable'] for v in a['period_vintages']],['3/4','5/1'])
        self.assertEqual([v['closing_payable'] for v in b['period_vintages']],['15/4','2/1'])
        self.assertEqual(a['tax_vintages'],b['tax_vintages'])

    def test_exact_fractional_payments(self):
        r=m.run(x.scenario([x.payment(old='1/3',new='2/3')]))
        self.assertEqual([v['closing_payable'] for v in r['period_vintages']],['41/12','13/3'])
        self.assertEqual(r['after']['balances']['cash'],'713/2')
        self.assertEqual(r['after']['balances']['income_tax_payable'],'-31/4')

    def test_successive_payments_exhaust_only_current_openings(self):
        r=m.run(x.scenario([x.payment(),x.payment(old='11/4',new='3/1',identity='second',day='2027-01-02')]))
        self.assertEqual(r['status'],'complete_provisional')
        self.assertEqual([v['closing_payable'] for v in r['period_vintages']],['0/1','0/1'])
        self.assertEqual([len(v['settlements']) for v in r['period_vintages']],[2,2])
        self.assertEqual(r['after']['balances']['cash'],'1395/4')
        self.assertEqual(r['recorded_statements']['indirect_operating']['net'],'-35/4')
        self.assertEqual(r['tax_vintages'],r['boundary_result']['tax_vintages'])

    def test_failure_keeps_successful_prefix_and_remaining_operations(self):
        first=x.payment();bad=x.payment(old='3/1',new='0/1',identity='excess')
        q=x.scenario([first,bad,x.depreciation()]);r=m.run(q);good=m.run(x.scenario([first]))
        self.assertEqual(r['status'],'stopped_provisional');self.assertEqual(r['stop']['index'],1)
        self.assertEqual(r['stop']['reason'],'allocation_exceeds_vintage')
        for k in ['after','period_vintages','tax_vintages','archive','recorded_statements']:self.assertEqual(r[k],good[k],k)
        self.assertEqual(r['remaining_operations'],[bad,x.depreciation()])
        self.assertEqual(m.apply(q,r)['status'],'applied_provisional')

    def test_real_cash_shortage_does_not_mutate(self):
        q=x.funding_scenario();r=m.run(q)
        self.assertEqual(r['stop']['status'],'funding_failure');self.assertEqual(r['stop']['reason'],'cash_shortage')
        self.assertGreater(-Q(r['opening']['balances']['income_tax_payable']),Q(r['opening']['balances']['cash']))
        self.assertEqual(r['after'],r['opening']);self.assertEqual(r['trace'],[])
        self.assertEqual(r['remaining_operations'],q['operations'])

    def test_native_sale_of_retained_lot(self):
        r=m.run(x.retained_lot_scenario());self.assertEqual(r['status'],'complete_provisional')
        self.assertEqual(r['after']['balances']['cash'],'482/1')
        self.assertEqual(r['recorded_statements']['recorded_profit'],'10/1')
        self.assertEqual(r['recorded_statements']['indirect_operating']['net'],'30/1')
        self.assertEqual(r['period_vintages'],r['boundary_result']['period_vintages'])
        self.assertEqual(r['tax_vintages'],r['boundary_result']['tax_vintages'])

    def test_loss_and_recognition_are_not_renewed(self):
        r=m.run(x.scenario([],x.previous.request(x.previous.previous.loss_scenario())))
        self.assertEqual(r['after']['balances']['dta'],'29/4')
        self.assertEqual(r['loss_state'],r['boundary_result']['loss_state'])
        self.assertEqual(r['archive'],r['boundary_result']['archive'])
        self.assertFalse(r['conditional_deferred_assessed'])

    def test_all_case_statuses_and_stop_categories(self):
        for row in x.cases():
            with self.subTest(case=row['case']):
                r=m.run(row['request']);self.assertEqual(r['status'],row['expected_status'],r.get('reason'))
                self.assertEqual(r.get('stop',{}).get('status') if r.get('stop') else None,row['expected_stop'])

    def test_complete_apply_rejects_every_top_level_tamper(self):
        r=self.result
        for key in r:
            with self.subTest(field=key):
                altered=deepcopy(r);altered[key]={'tampered':True}
                self.assertEqual(m.apply(self.body,altered)['status'],'invalid')
        self.assertEqual(m.apply(self.body,r)['status'],'applied_provisional')

    def test_invariant_rejects_period_history_and_flow_corruption(self):
        for name,mutate in [
            ('historical_digest',lambda s,h,v:v[0].update(prior_vintage_sha256='0'*64)),
            ('opening',lambda s,h,v:v[0].update(opening_payable='99/1')),
            ('missing_settlement',lambda s,h,v:v[0]['settlements'].clear()),
            ('wrong_period',lambda s,h,v:v[0]['period'].update(start='2026-01-01')),
            ('old_date',lambda s,h,v:v[0]['settlements'][0].update(date='2026-01-01')),
            ('different_total',lambda s,h,v:v[0]['settlements'][0].update(payment_amount='4/1')),
            ('different_provenance',lambda s,h,v:v[0]['settlements'][0].update(financial_result_sha256='0'*64)),
            ('missing_flow',lambda s,h,v:s['flows'].clear()),
            ('duplicate_flow',lambda s,h,v:s['flows'].append(deepcopy(s['flows'][0]))),
            ('changed_history',lambda s,h,v:h[0].update(closing_payable='1/1'))]:
            with self.subTest(case=name):
                state=deepcopy(self.result['after']);history=deepcopy(self.result['tax_vintages']);vs=deepcopy(self.result['period_vintages'])
                mutate(state,history,vs)
                with self.assertRaises((m.continuation.Refused,m.losses.Refused,ValueError)):
                    m.period_invariant(state,history,vs)

    def test_payment_provenance_links_original_and_financial_operation(self):
        r=self.result;t=r['trace'][0];op=t['operation'];p=r['boundary_result']
        kernel={'kind':'tax_payment','event':{k:deepcopy(v) for k,v in op['event'].items() if k!='allocations'}}
        financial=m.continuation.transition(p['after'],kernel,p['after']['period']['start'])
        for v in r['period_vintages']:
            self.assertEqual(v['settlements'][0]['operation_sha256'],m.book.digest(op))
            self.assertEqual(v['settlements'][0]['financial_result_sha256'],m.book.digest(financial))
        self.assertEqual(t['result']['operation_sha256'],m.book.digest(op))

    def test_inputs_unchanged_and_replay_exact(self):
        before=m.caller.canonical(self.body);r=m.run(self.body)
        self.assertEqual(m.caller.canonical(self.body),before)
        self.assertEqual(m.caller.canonical(r),m.caller.canonical(self.result))

if __name__=='__main__':unittest.main()
