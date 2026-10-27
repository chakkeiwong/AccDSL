from pathlib import Path
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
s=importlib.util.spec_from_file_location('following_tax_examples',ROOT/'data/accounting-master/following-period-tax-20261024/examples.py')
x=importlib.util.module_from_spec(s);s.loader.exec_module(x);m=x.m
class FollowingTaxTests(unittest.TestCase):
    def test_native_return_adjustment_exactly_once(self):
        q=x.return_scenario();r=m.propose(q);self.assertEqual(r['status'],'proposed')
        self.assertEqual(r['calculation']['pretax_income'],'6/1')
        self.assertEqual(r['calculation']['signed_adjustments'],'-24/1')
        self.assertEqual(r['calculation']['taxable_profit'],'-18/1')
        self.assertEqual(r['loss_result']['totals']['generated'],'18/1')
        self.assertEqual(r['after']['balances']['cash'],'482/1')
        q['allocations']=[a for a in q['allocations'] if a['origin']['kind']!='native_return']
        self.assertEqual(m.propose(q)['status'],'invalid')

    def test_carried_loss_expiry_and_usage_day(self):
        r=m.propose(x.expiring_loss());self.assertEqual(r['status'],'proposed')
        self.assertEqual(r['loss_result']['totals']['expired'],'19/1')
        self.assertEqual(r['loss_state']['lots'][0]['remaining'],'0/1')
        q=x.expiring_loss('1/1');self.assertEqual(m.propose(q)['status'],'invalid')
        q['interval'].update(end_exclusive='2026-04-01',activity_through='2026-03-31')
        r=m.propose(q);self.assertEqual(r['status'],'proposed')
        self.assertEqual(r['loss_state']['lots'][0]['remaining'],'18/1')

    def test_paid_prior_tax_does_not_credit_new_tax(self):
        r=m.propose(x.scenario());self.assertEqual(r['status'],'proposed')
        self.assertEqual(r['after']['balances']['current_tax'],'5/1');self.assertEqual(r['after']['balances']['income_tax_payable'],'-5/1')
        self.assertEqual(r['after']['balances']['cash'],'1423/4')
        self.assertEqual([v['closing_payable'] for v in r['tax_vintages']],['0/1','5/1'])
        self.assertEqual(r['tax_vintages'][0]['settlements'][0]['amount'],'19/4')
        report=r['recorded_statements'];self.assertEqual(report['recorded_profit'],'-15/1')
        self.assertEqual(report['balance_sheet'],{'total_assets':'2735/4','total_liabilities':'115/1','equity_including_profit':'2275/4'})
        self.assertEqual(report['indirect_operating']['net'],'-19/4');self.assertEqual(set(report['reconciliations'].values()),{'0/1'})

    def test_unpaid_partial_and_full_payment_have_same_new_expense(self):
        for paid,old,total in [('0/1','19/4','-39/4'),('1/1','15/4','-35/4'),('19/4','0/1','-5/1')]:
            r=m.propose(x.scenario(payment=paid));self.assertEqual(r['status'],'proposed')
            self.assertEqual(r['tax_vintages'][0]['closing_payable'],old)
            self.assertEqual(r['after']['balances']['income_tax_payable'],total)
            self.assertEqual(r['journal']['current_tax'],'5/1');self.assertEqual(r['recorded_statements']['recorded_profit'],'-15/1')

    def test_zero_and_negative_taxable_preserve_old_liability(self):
        for taxable in ['0/1','-7/1']:
            r=m.propose(x.scenario(taxable,payment='0/1'));self.assertEqual(r['status'],'proposed')
            self.assertEqual(r['after']['balances']['current_tax'],'0/1');self.assertEqual(r['after']['balances']['income_tax_payable'],'-19/4')
        self.assertEqual(r['loss_state']['lots'][0]['remaining'],'7/1')
        self.assertEqual(r['loss_state']['lots'][0]['available_from'],'2027-01-01')

    def test_loss_use_continues_real_inventory_and_history(self):
        r=m.propose(x.loss_scenario());self.assertEqual(r['status'],'proposed')
        self.assertEqual(r['journal']['current_tax'],'1/4');lot=r['loss_state']['lots'][0]
        self.assertEqual((lot['used'],lot['remaining']),('19/1','0/1'))
        old=r['carry_result']['loss_state'];self.assertEqual(r['loss_state']['history'][:-1],old['history'])
        self.assertEqual(r['loss_state']['cursor'],'2027-01-01')
        self.assertEqual(r['loss_result']['totals'],{'opening':'19/1','generated':'0/1','used':'19/1','expired':'0/1','closing':'0/1'})

    def test_loss_overuse_and_generation_identity(self):
        q=x.loss_scenario(use='20/1');r=m.propose(q);self.assertEqual(r['status'],'invalid')
        q=x.loss_scenario(use='0/1',taxable='-7/1');q['loss_policy']['generation']['id']='replacement-loss'
        self.assertEqual(m.propose(q)['status'],'invalid')

    def test_deferred_and_other_state_unchanged(self):
        r=m.propose(x.scenario());old=r['carry_result']['after'];new=r['after']
        for k,v in old.items():
            if k not in ['balances','date','seen']:self.assertEqual(new[k],v,k)
        for k,v in old['balances'].items():
            if k not in ['current_tax','income_tax_payable']:self.assertEqual(new['balances'][k],v,k)
        self.assertEqual(r['findings'],r['carry_result']['findings']);self.assertFalse(r['annual_close_ready'])
        self.assertEqual(r['current_period_deferred_tax'],'unassessed')
        self.assertEqual(r['recorded_statements']['cash_flows'],r['carry_result']['recorded_statements']['cash_flows'])

    def test_scope_and_unknown_information(self):
        q=x.scenario()
        for key,value,status in [('rate',{'status':'unknown','reason':'Missing'},'unresolved'),
            ('interval_coverage',x.known(False),'unsupported'),('jurisdiction',x.known('other'),'invalid'),
            ('rate',x.known('-1/4'),'invalid')]:
            a=deepcopy(q);a['information'][key]=value;r=m.propose(a)
            self.assertEqual(r['status'],status);self.assertNotIn('after',r)
        a=deepcopy(q);a['information'].pop('basis/income_tax_payable/opening');self.assertEqual(m.propose(a)['status'],'unresolved')

    def test_intervals_identity_and_partial_assessment(self):
        q=x.scenario()
        for key,value in [('start','2026-01-02'),('end_exclusive','2028-01-01'),('activity_through','2026-12-30')]:
            a=deepcopy(q);a['interval'][key]=value;self.assertEqual(m.propose(a)['status'],'invalid')
        a=deepcopy(q);a['id']='assessed-carry-2026';self.assertEqual(m.propose(a)['status'],'invalid')
        a=deepcopy(q);a['interval'].update(end_exclusive='2026-07-01',activity_through='2026-06-30')
        r=m.propose(a);self.assertEqual(r['status'],'proposed');self.assertEqual(r['assessed_until'],'2026-07-01')

    def test_stopped_carry_is_not_silently_assessed(self):
        q=x.scenario();q['carry_request']['operations'].append(x.previous.payment('1/1',identity='excess'))
        q['carry_sha256']=m.book.digest(q['carry_request']);r=m.propose(q)
        self.assertEqual(r['status'],'unresolved');self.assertEqual(r['carry_result']['status'],'stopped_provisional')
        self.assertNotIn('after',r)

    def test_allocations_and_bases_must_reconcile(self):
        q=x.scenario()
        a=deepcopy(q);a['allocations'][0]['amount']='29/1';self.assertEqual(m.propose(a)['status'],'invalid')
        a=deepcopy(q);a['allocations'].append(deepcopy(a['allocations'][0]));self.assertEqual(m.propose(a)['status'],'invalid')
        a=deepcopy(q);a['information']['basis/rou/closing']=x.known('1/1');self.assertEqual(m.propose(a)['status'],'invalid')

    def test_full_apply_and_vintage_tamper(self):
        q=x.scenario();before=deepcopy(q);r=m.propose(q);applied=m.apply(q,r)
        self.assertEqual(q,before);self.assertEqual(applied,{**r,'status':'applied'})
        for key,value in [('tax_vintages',[]),('carry_result',{}),('loss_state',{}),('annual_close_ready',True),('committed',0)]:
            bad=deepcopy(r);bad[key]=value;self.assertEqual(m.apply(q,bad)['status'],'invalid')
        q['carry_sha256']='0'*64;self.assertEqual(m.propose(q)['status'],'invalid')

if __name__=='__main__':unittest.main()
