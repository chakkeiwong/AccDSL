from pathlib import Path
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
s=importlib.util.spec_from_file_location('following_reassessment_examples',ROOT/'data/accounting-master/following-tax-reassessment-20261024/examples.py')
x=importlib.util.module_from_spec(s);s.loader.exec_module(x);m=x.m

class FollowingReassessmentTests(unittest.TestCase):
    def test_independent_increase_and_statement_totals(self):
        r=m.propose(x.scenario());self.assertEqual(r['status'],'proposed')
        self.assertEqual(r['financial_calculation'],{'previous_expense':'5/1','replacement_expense':'7/1',
            'current_vintage_paid':'2/1','carried_remaining':'15/4','incremental_expense':'2/1',
            'replacement_current_payable':'5/1','replacement_total_payable':'35/4'})
        self.assertEqual(r['journal']['current_tax'],'2/1');self.assertEqual(r['journal']['income_tax_payable'],'-2/1')
        self.assertEqual(r['after']['balances']['cash'],'715/2');self.assertEqual(r['after']['balances']['current_tax'],'7/1')
        self.assertEqual(r['after']['balances']['income_tax_payable'],'-35/4')
        report=r['recorded_statements'];self.assertEqual(report['recorded_profit'],'-19/1')
        self.assertEqual(report['balance_sheet'],{'total_assets':'1367/2','total_liabilities':'475/4','equity_including_profit':'2259/4'})
        self.assertEqual(report['indirect_operating']['net'],'-3/1');self.assertEqual(set(report['reconciliations'].values()),{'0/1'})

    def test_decrease_equal_and_exactly_paid_current(self):
        for taxable,delta,total,profit in [('12/1','-2/1','-19/4','-15/1'),
                ('20/1','0/1','-27/4','-17/1'),('8/1','-3/1','-15/4','-14/1')]:
            r=m.propose(x.scenario(taxable));self.assertEqual(r['status'],'proposed')
            self.assertEqual(r['journal']['current_tax'],delta);self.assertEqual(r['after']['balances']['income_tax_payable'],total)
            self.assertEqual(r['recorded_statements']['recorded_profit'],profit)
            self.assertEqual(r['after']['balances']['cash'],'715/2')

    def test_old_liability_cannot_hide_current_credit(self):
        q=x.scenario('4/1');r=m.propose(q);self.assertEqual(r['status'],'unsupported')
        self.assertEqual(r['reason'],'current_tax_receivable_or_refund_route_required')
        self.assertEqual(r['financial_calculation']['replacement_current_payable'],'-1/1')
        self.assertEqual(r['financial_calculation']['replacement_total_payable'],'11/4')
        self.assertNotIn('after',r);self.assertNotIn('tax_vintages',r)
        self.assertEqual(r['continuation_result']['after']['balances']['current_tax'],'5/1')
        self.assertEqual(m.apply(q,r)['status'],'invalid')

    def test_carried_payments_do_not_reduce_new_expense(self):
        for old,new,total in [('0/1','0/1','47/4'),('1/1','0/1','43/4'),
                              ('0/1','2/1','39/4'),('19/4','2/1','5/1')]:
            q=x.previous.assessment();ops=([x.previous.payment(q,old,new)] if Q(old)+Q(new)>0 else [])+[x.previous.depreciation()]
            r=m.propose(x.scenario(prior=x.previous.scenario(ops,q)))
            self.assertEqual(r['status'],'proposed');self.assertEqual(r['after']['balances']['current_tax'],'7/1')
            self.assertEqual(r['financial_calculation']['replacement_total_payable'],total)
            self.assertEqual(r['journal']['current_tax'],'2/1')

    def test_stable_vintage_identity_and_full_supersession(self):
        r=m.propose(x.scenario());p=r['continuation_result'];a,b=r['tax_vintages']
        self.assertEqual(a,p['tax_vintages'][0]);self.assertEqual(b['id'],p['tax_vintages'][1]['id'])
        self.assertEqual(b['settlements'],p['tax_vintages'][1]['settlements'])
        self.assertEqual(b['assessment_id'],'following-reassessment')
        self.assertEqual(b['supersession_history'][0]['previous_vintage'],p['tax_vintages'][1])
        self.assertEqual(b['supersession_history'][0]['previous_loss_state_sha256'],m.book.digest(p['loss_state']))
        self.assertEqual(b['assessment_request_sha256'],r['request_sha256'])
        m.continuation.vintage_invariant(r['after'],r['tax_vintages'])

    def test_original_loss_opening_replaces_not_reuses_remaining(self):
        r=m.propose(x.losses());self.assertEqual(r['status'],'proposed')
        p=r['continuation_result'];self.assertEqual(p['loss_state']['lots'][0]['remaining'],'0/1')
        self.assertEqual(r['replacement_loss_result']['totals']['opening'],'19/1')
        self.assertEqual(r['replacement_loss_result']['totals']['used'],'19/1')
        self.assertEqual(r['loss_state']['lots'][0]['used'],'19/1')
        self.assertEqual(r['financial_calculation']['replacement_expense'],'1/4')
        original=p['assessment_result']['carry_result']['loss_state']
        self.assertEqual(r['loss_state']['history'][:-1],original['history'])
        self.assertNotIn('following-assessment',r['loss_state']['seen'])
        r=m.propose(x.losses('10/1'));self.assertEqual(r['loss_state']['lots'][0]['remaining'],'9/1')
        self.assertEqual(r['financial_calculation']['replacement_expense'],'5/2')

    def test_loss_expiry_reassesses_at_new_close(self):
        r=m.propose(x.expiry());self.assertEqual(r['status'],'proposed')
        self.assertEqual(r['replacement_loss_result']['totals']['expired'],'19/1')
        self.assertEqual(r['loss_state']['lots'][0]['used'],'0/1')
        self.assertEqual(m.propose(x.expiry('1/1'))['status'],'invalid')
        self.assertEqual(m.propose(x.losses('20/1'))['status'],'invalid')

    def test_provisional_generated_lot_is_superseded(self):
        q=x.previous.assessment(taxable='-5/1');continued=x.previous.scenario([],q)
        r=m.propose(x.scenario('-7/1',continued));self.assertEqual(r['status'],'proposed')
        self.assertEqual([a['id'] for a in r['loss_state']['lots']],['reassessed-loss'])
        self.assertEqual(r['loss_state']['lots'][0]['remaining'],'7/1')
        self.assertEqual(r['continuation_result']['loss_state']['lots'][0]['id'],'following-loss')
        bad=x.scenario('-7/1',continued);bad['loss_policy']['generation']['id']='following-loss'
        self.assertEqual(m.propose(bad)['status'],'invalid')
        bad=x.scenario('20/1',continued,[{'lot_id':'following-loss','amount':'1/1'}],'1/1')
        self.assertEqual(m.propose(bad)['status'],'invalid')

    def test_native_return_adjustment_exactly_once(self):
        q=x.scenario('-18/1',x.previous.return_scenario());r=m.propose(q)
        self.assertEqual(r['status'],'proposed');self.assertEqual(r['calculation']['pretax_income'],'6/1')
        self.assertEqual(r['calculation']['signed_adjustments'],'-24/1');self.assertEqual(r['calculation']['taxable_profit'],'-18/1')
        self.assertEqual(r['replacement_loss_result']['totals']['generated'],'18/1')
        self.assertEqual(r['journal']['current_tax'],'-5/1');self.assertEqual(r['recorded_statements']['recorded_profit'],'6/1')
        self.assertEqual(r['after']['balances']['cash'],'482/1')
        q['allocations']=[a for a in q['allocations'] if a['origin']['kind']!='native_return']
        self.assertEqual(m.propose(q)['status'],'invalid')

    def test_timing_and_same_endpoint_correction(self):
        q=x.previous.assessment();r=m.propose(x.scenario(prior=x.previous.scenario([],q),end='2026-07-01',through='2026-06-30'))
        self.assertEqual(r['status'],'proposed')
        base=x.scenario()
        for interval in [{'start':'2026-01-02'}, {'end_exclusive':'2026-07-01','activity_through':'2026-06-30'},
                {'end_exclusive':'2026-06-01','activity_through':'2026-05-31'},
                {'end_exclusive':'2028-01-01','activity_through':'2027-12-31'}, {'activity_through':'2026-12-30'}]:
            bad=deepcopy(base);bad['interval'].update(interval);self.assertEqual(m.propose(bad)['status'],'invalid')

    def test_unchanged_cash_components_deferred_and_findings(self):
        r=m.propose(x.scenario());p=r['continuation_result'];before=p['after'];after=r['after']
        for key,value in before.items():
            if key not in ['balances','date','seen']:self.assertEqual(after[key],value,key)
        for key,value in before['balances'].items():
            if key not in ['current_tax','income_tax_payable']:self.assertEqual(after['balances'][key],value,key)
        self.assertEqual(r['findings'],p['findings']);self.assertEqual(r['recorded_statements']['cash_flows'],p['recorded_statements']['cash_flows'])
        self.assertEqual(r['unassessed_native_events'],[]);self.assertEqual(r['current_period_deferred_tax'],'unassessed')
        self.assertFalse(r['annual_close_ready']);self.assertFalse(r['committed'])

    def test_stopped_predecessor_requires_resolution(self):
        q=x.scenario();p=q['continuation_request'];p['operations'].append(x.previous.payment(p['assessment_request'],'4/1',identity='excess',day='2026-07-02'))
        q['continuation_sha256']=m.book.digest(p);r=m.propose(q)
        self.assertEqual(r['status'],'unresolved');self.assertEqual(r['continuation_result']['status'],'stopped_provisional')
        self.assertNotIn('after',r)

    def test_complete_apply_tamper_and_immutability(self):
        q=x.scenario();before=deepcopy(q);r=m.propose(q)
        self.assertEqual(q,before);self.assertEqual(m.apply(q,r),{**r,'status':'applied'})
        for key,value in [('tax_vintages',[]),('superseded',{}),('continuation_result',{}),
                          ('loss_state',{}),('annual_close_ready',True),('committed',0)]:
            bad=deepcopy(r);bad[key]=value;self.assertEqual(m.apply(q,bad)['status'],'invalid')

if __name__=='__main__':unittest.main()
