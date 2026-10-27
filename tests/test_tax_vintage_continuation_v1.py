from pathlib import Path
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
s=importlib.util.spec_from_file_location('vintage_examples',ROOT/'data/accounting-master/tax-vintage-continuation-20261024/examples.py')
x=importlib.util.module_from_spec(s);s.loader.exec_module(x);m=x.m

class VintageContinuationTests(unittest.TestCase):
    def test_independent_split_payment_and_native_arithmetic(self):
        r=m.run(x.scenario());self.assertEqual(r['status'],'complete_provisional')
        b=r['after']['balances'];self.assertEqual(len(b),26)
        self.assertEqual([v['closing_payable'] for v in r['tax_vintages']],['15/4','3/1'])
        self.assertEqual(b['income_tax_payable'],'-27/4');self.assertEqual(b['cash'],'715/2')
        self.assertEqual(b['current_tax'],'5/1');self.assertEqual(b['deferred_tax'],'0/1')
        self.assertEqual(b['depreciation'],'12/1');self.assertEqual(b['rou'],'78/1')
        report=r['recorded_statements'];self.assertEqual(report['recorded_profit'],'-17/1')
        self.assertEqual(report['balance_sheet'],{'total_assets':'1367/2','total_liabilities':'467/4','equity_including_profit':'2267/4'})
        self.assertEqual(report['indirect_operating']['net'],'-3/1')
        self.assertEqual(set(report['reconciliations'].values()),{'0/1'})
        self.assertEqual(r['unassessed_native_events'],['post-assessment-depreciation'])

    def test_equal_total_different_vintages(self):
        q=x.assessment();old=m.run(x.scenario([x.payment(q,'3/1')],q));new=m.run(x.scenario([x.payment(q,new='3/1')],q))
        self.assertEqual(old['after']['balances'],new['after']['balances'])
        self.assertEqual([v['closing_payable'] for v in old['tax_vintages']],['7/4','5/1'])
        self.assertEqual([v['closing_payable'] for v in new['tax_vintages']],['19/4','2/1'])

    def test_successive_and_prior_settlements_are_retained(self):
        q=x.assessment(payment='1/1');r=m.run(x.scenario([x.payment(q,'1/1','2/1'),x.payment(q,'11/4','3/1','second','2026-07-01')],q))
        self.assertEqual(r['status'],'complete_provisional')
        self.assertEqual([v['closing_payable'] for v in r['tax_vintages']],['0/1','0/1'])
        self.assertEqual(r['tax_vintages'][0]['settlements'][:1],r['assessment_result']['tax_vintages'][0]['settlements'])
        self.assertEqual([len(v['settlements']) for v in r['tax_vintages']],[3,2])
        self.assertEqual(r['after']['balances']['cash'],'1403/4')
        self.assertEqual(r['recorded_statements']['recorded_profit'],'-15/1')
        self.assertEqual(r['recorded_statements']['indirect_operating']['net'],'-39/4')

    def test_fractional_allocations_and_zero_balance_history(self):
        q=x.assessment();r=m.run(x.scenario([x.payment(q,'1/3','2/3')],q))
        self.assertEqual([v['closing_payable'] for v in r['tax_vintages']],['53/12','13/3'])
        self.assertEqual(r['after']['balances']['income_tax_payable'],'-35/4')
        q=x.assessment(payment='19/4');r=m.run(x.scenario([x.payment(q,new='2/1')],q))
        self.assertEqual(r['tax_vintages'][0],r['assessment_result']['tax_vintages'][0])
        self.assertEqual(len(r['tax_vintages']),2)

    def test_failure_preserves_completed_prefix(self):
        q=x.assessment();ops=[x.payment(q,'1/1'),x.payment(q,'4/1',identity='excess'),x.depreciation()]
        body=x.scenario(ops,q);r=m.run(body)
        self.assertEqual(r['status'],'stopped_provisional');self.assertEqual(r['stop']['index'],1)
        self.assertEqual(r['stop']['reason'],'allocation_exceeds_vintage')
        prefix=m.run(x.scenario(ops[:1],q))
        for key in ['after','tax_vintages','recorded_statements']:self.assertEqual(r[key],prefix[key])
        self.assertEqual(r['remaining_operations'],ops[1:])
        self.assertEqual(m.apply(body,r),{**r,'status':'applied_provisional'})

    def test_cash_shortage_and_unknown_authorization(self):
        q=x.assessment(taxable='2000/1');r=m.run(x.scenario([x.payment(q,new='400/1')],q))
        self.assertEqual(r['stop']['status'],'funding_failure');self.assertEqual(r['after'],r['assessment_result']['after'])
        op=x.payment(q,new='1/1');op['event']['authorization']={'status':'unknown','reason':'Missing'}
        r=m.run(x.scenario([op],q));self.assertEqual(r['stop']['status'],'unresolved')
        self.assertEqual(r['tax_vintages'],r['assessment_result']['tax_vintages'])

    def test_invalid_allocations_never_write(self):
        q=x.assessment()
        for mutate in [lambda e:e['allocations'][0].update(vintage_id='missing'),
                       lambda e:e['allocations'].append(deepcopy(e['allocations'][0])),
                       lambda e:e.update(amount='4/1'),lambda e:e['allocations'][0].update(amount='0/1'),
                       lambda e:e['allocations'][0].update(amount='-1/1')]:
            op=x.payment(q,'1/1','2/1');mutate(op['event']);r=m.run(x.scenario([op],q))
            self.assertEqual(r['status'],'stopped_provisional');self.assertEqual(r['stop']['status'],'invalid')
            self.assertEqual(r['trace'],[]);self.assertEqual(r['after'],r['assessment_result']['after'])

    def test_no_implicit_allocation(self):
        r=m.run(x.scenario([x.prior.previous.payment()]))
        self.assertEqual(r['stop']['reason'],'explicit_vintage_allocation_required')
        self.assertEqual(r['stop']['status'],'unsupported')

    def test_dates_assessment_boundary_and_financial_endpoint(self):
        q=x.assessment();r=m.run(x.scenario([x.payment(q,'1/1'),x.depreciation()],q))
        self.assertEqual(r['status'],'complete_provisional')
        for op in [x.payment(q,'1/1',day='2026-06-29'),x.depreciation(day='2026-06-30'),
                   x.payment(q,'1/1',day='2027-01-01')]:
            r=m.run(x.scenario([op],q));self.assertEqual(r['stop']['status'],'invalid')
        full=x.assessment(full_year=True)
        r=m.run(x.scenario([x.payment(full,new='1/1',day='2026-12-31')],full));self.assertEqual(r['status'],'complete_provisional')
        r=m.run(x.scenario([x.depreciation(day='2027-01-01')],full));self.assertEqual(r['stop']['status'],'invalid')

    def test_duplicate_event_lifetime(self):
        q=x.assessment()
        for identity in [q['id'],'assessed-carry-2026','following-depreciation']:
            r=m.run(x.scenario([x.payment(q,'1/1',identity=identity)],q));self.assertEqual(r['stop']['reason'],'duplicate_event')
        op=x.payment(q,'1/1');r=m.run(x.scenario([op,op],q))
        self.assertEqual(len(r['trace']),1);self.assertEqual(r['stop']['reason'],'duplicate_event')

    def test_loss_deferred_findings_and_payment_footprint(self):
        q=x.assessment();r=m.run(x.scenario([x.payment(q,'1/1','2/1')],q));p=r['assessment_result']
        self.assertEqual(r['loss_state'],p['loss_state']);self.assertEqual(r['findings'],p['findings'])
        for key,value in p['after'].items():
            if key not in ['balances','seen','flows','date']:self.assertEqual(r['after'][key],value,key)
        for key,value in p['after']['balances'].items():
            if key not in ['cash','income_tax_payable']:self.assertEqual(r['after']['balances'][key],value,key)
        self.assertFalse(r['annual_close_ready']);self.assertFalse(r['committed'])
        self.assertEqual(r['current_period_deferred_tax'],'unassessed')

    def test_return_adjustments_remain_unassessed(self):
        r=m.run(x.return_scenario());self.assertEqual(r['status'],'complete_provisional')
        self.assertEqual(r['after']['balances']['cash'],'482/1');self.assertEqual(r['recorded_statements']['recorded_profit'],'1/1')
        self.assertEqual(r['after']['balances']['current_tax'],'5/1')
        self.assertEqual(sum(Q(a['amount']) for a in r['after']['tax_adjustments']),Q(-24))
        self.assertEqual(len(r['unassessed_native_events']),2)
        self.assertEqual(r['loss_state'],r['assessment_result']['loss_state'])

    def test_flow_and_vintage_tamper_detected_by_invariant(self):
        r=m.run(x.scenario());state=r['after'];v=r['tax_vintages']
        for mutate in [lambda a:a[0].update(closing_payable='4/1'),
                       lambda a:a[0]['settlements'][0].update(amount='2/1'),
                       lambda a:a[1]['settlements'][0].update(date='2026-07-01'),
                       lambda a:a[1]['settlements'][0].update(payment_amount='2/1')]:
            bad=deepcopy(v);mutate(bad)
            with self.assertRaises(ValueError):m.vintage_invariant(state,bad)

    def test_complete_apply_and_request_immutability(self):
        body=x.scenario();before=deepcopy(body);r=m.run(body)
        self.assertEqual(body,before);self.assertEqual(m.apply(body,r),{**r,'status':'applied_provisional'})
        for key,value in [('tax_vintages',[]),('assessment_result',{}),('loss_state',{}),
                          ('trace',[]),('annual_close_ready',True),('committed',0)]:
            bad=deepcopy(r);bad[key]=value;self.assertEqual(m.apply(body,bad)['status'],'invalid')

    def test_predecessor_digest_and_unknown_information(self):
        body=x.scenario([]);body['assessment_sha256']='0'*64
        self.assertEqual(m.run(body)['status'],'invalid')
        q=x.assessment();q['information']['rate']={'status':'unknown','reason':'Missing'}
        r=m.run(x.scenario([],q));self.assertEqual(r['status'],'unresolved');self.assertNotIn('after',r)

if __name__=='__main__':unittest.main()
