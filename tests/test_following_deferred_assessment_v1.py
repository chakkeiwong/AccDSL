from pathlib import Path
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
s=importlib.util.spec_from_file_location('following_deferred_examples',ROOT/'data/accounting-master/following-deferred-assessment-20261024/examples.py')
x=importlib.util.module_from_spec(s);s.loader.exec_module(x);m=x.m

class FollowingDeferredTests(unittest.TestCase):
    def test_independent_desired_minus_carried_balances(self):
        r=m.propose(x.scenario());self.assertEqual(r['status'],'proposed');b=r['after']['balances']
        self.assertEqual(b['dta'],'5/1');self.assertEqual(b['dtl'],'-5/1');self.assertEqual(b['deferred_tax'],'-2/1')
        self.assertEqual(r['journal']['dta'],'-3/1');self.assertEqual(r['journal']['dtl'],'5/1')
        self.assertEqual(r['journal']['deferred_tax'],'-2/1');self.assertEqual(b['cash'],'715/2')
        self.assertEqual(b['current_tax'],'7/1');self.assertEqual(b['income_tax_payable'],'-35/4')
        report=r['recorded_statements'];self.assertEqual(report['recorded_profit'],'-17/1')
        self.assertEqual(report['balance_sheet'],{'total_assets':'1361/2','total_liabilities':'455/4','equity_including_profit':'2267/4'})
        self.assertEqual(report['indirect_operating']['net'],'-3/1');self.assertEqual(set(report['reconciliations'].values()),{'0/1'})

    def test_no_change_reverse_and_fractional_measurement(self):
        r=m.propose(x.scenario(ppe_base='60/1',recognized='32/1',capacity='32/1'))
        self.assertEqual(r['status'],'proposed');self.assertEqual(set(r['journal'].values()),{'0/1'})
        for q in [x.scenario(rate='0/1'),x.scenario(ppe_base='100/1',debt_base='100/1',recognized='0/1',capacity='0/1')]:
            r=m.propose(q);self.assertEqual(r['status'],'proposed')
            self.assertEqual(r['after']['balances']['dta'],'0/1');self.assertEqual(r['after']['balances']['dtl'],'0/1')
            self.assertEqual(r['journal']['deferred_tax'],'-2/1')
        r=m.propose(x.scenario(rate='1/3'));self.assertEqual(r['calculation']['desired_dta'],'20/3')
        self.assertEqual(r['calculation']['desired_dtl'],'20/3')

    def test_capacity_is_shared_across_debt_and_remaining_losses(self):
        r=m.propose(x.loss_scenario());self.assertEqual(r['status'],'proposed')
        self.assertEqual(r['calculation']['desired_dta'],'29/4')
        self.assertEqual(r['calculation']['recognized_deductions'],'29/1')
        self.assertEqual(r['loss_state']['lots'][0]['remaining'],'9/1')
        r=m.propose(x.loss_scenario('20/1'));self.assertEqual(r['status'],'invalid')
        self.assertEqual(r['reason'],'recovery_capacity_reused');self.assertNotIn('after',r)

    def test_old_capacity_is_historical_not_renewed(self):
        q=x.scenario();r=m.propose(q);self.assertEqual(r['status'],'proposed')
        self.assertEqual(r['historical_recognition']['capacity']['value'],'32/1')
        self.assertEqual(r['recovery_capacity']['value'],'20/1')
        q['recovery_capacity']={'status':'unknown','reason':'No fresh recovery evidence'}
        self.assertEqual(m.propose(q)['status'],'unresolved')
        q=x.scenario(recognized='0/1',capacity='0/1');r=m.propose(q)
        self.assertEqual(r['calculation']['desired_dta'],'0/1');self.assertEqual(r['calculation']['desired_dtl'],'5/1')
        self.assertEqual(r['journal']['deferred_tax'],'3/1')

    def test_measurement_binds_post_current_tax_state(self):
        q=x.scenario();r=m.propose(q)
        self.assertEqual(q['measurement']['account_bases']['income_tax_payable']['value'],'35/4')
        self.assertEqual(q['prior_request']['information']['basis/income_tax_payable/closing']['value'],'27/4')
        self.assertEqual(q['measurement']['state_sha256'],m.book.digest(r['prior_result']['after']))
        for change in [lambda b:b['measurement'].update(state_sha256='0'*64),
                       lambda b:b['measurement'].update(at='2026-06-30'),
                       lambda b:b['measurement']['account_bases'].update(income_tax_payable=x.known('27/4'))]:
            bad=deepcopy(q);change(bad);self.assertEqual(m.propose(bad)['status'],'invalid')

    def test_measurement_population_scope_and_unknowns(self):
        q=x.scenario()
        for change,status in [(lambda b:b['measurement']['account_bases'].pop('income_tax_payable'),'invalid'),
            (lambda b:b['measurement']['lease_bases'].pop('lease/lease1/A/asset'),'invalid'),
            (lambda b:b['measurement'].update(jurisdiction=x.known('other')),'invalid'),
            (lambda b:b['measurement']['account_bases'].update(cash={'status':'unknown','reason':'Missing'}),'unresolved')]:
            bad=deepcopy(q);change(bad);self.assertEqual(m.propose(bad)['status'],status)

    def test_recorded_allocations_and_item_bases_reconcile(self):
        q=x.scenario()
        for identity,field,value in [('account/debt','recorded_dta','7/1'),('account/ppe','recorded_dtl','9/1'),
                ('account/ppe','tax_base','81/1'),('lease/lease1/A/asset','tax_base','1/1'),
                ('inventory/lot/recovered','tax_base','1/1'),('account/debt','recognized_deduction','41/1')]:
            bad=deepcopy(q);x.item(bad,identity)[field]=x.known(value);self.assertEqual(m.propose(bad)['status'],'invalid')
        bad=deepcopy(q);bad['items'].pop();self.assertEqual(m.propose(bad)['status'],'invalid')
        bad=deepcopy(q);bad['items'].append(deepcopy(bad['items'][0]));self.assertEqual(m.propose(bad)['status'],'invalid')

    def test_current_tax_payments_losses_and_components_unchanged(self):
        r=m.propose(x.scenario());p=r['prior_result'];after=r['after'];before=p['after']
        self.assertEqual(len(after['balances']),26)
        for k,v in before.items():
            if k not in ['balances','seen']:self.assertEqual(after[k],v,k)
        for k,v in before['balances'].items():
            if k not in ['dta','dtl','deferred_tax']:self.assertEqual(after['balances'][k],v,k)
        self.assertEqual(r['tax_vintages'],p['tax_vintages']);self.assertEqual(r['loss_state'],p['loss_state'])
        self.assertEqual(r['prior_findings'],p['findings']);self.assertEqual(r['opening'],p['opening'])
        self.assertEqual(r['recorded_statements']['cash_flows'],p['recorded_statements']['cash_flows'])
        self.assertFalse(r['annual_close_ready']);self.assertFalse(r['committed'])

    def test_return_generated_loss_not_automatically_recognized(self):
        q=x.scenario(x.previous.scenario('-18/1',x.previous.previous.return_scenario()));r=m.propose(q)
        self.assertEqual(r['status'],'proposed');self.assertEqual(r['after']['balances']['cash'],'482/1')
        loss=next(i for i in r['calculation']['items'] if i['kind']=='loss')
        self.assertEqual(loss['carrying'],'18/1');self.assertEqual(loss['desired_dta'],'0/1')
        self.assertEqual(loss['unrecognized_deduction'],'18/1')

    def test_unsupported_routes_and_predecessor_are_retained(self):
        for route in ['equity','other_comprehensive_income','offset']:
            q=x.scenario();x.item(q,'account/ppe')['route']=x.known(route)
            r=m.propose(q);self.assertEqual(r['status'],'unsupported');self.assertNotIn('after',r)
        q=x.scenario();q['prior_request']=x.previous.scenario('4/1');q['prior_sha256']=m.book.digest(q['prior_request'])
        r=m.propose(q);self.assertEqual(r['status'],'unsupported');self.assertNotIn('after',r)
        self.assertEqual(r['prior_result']['reason'],'current_tax_receivable_or_refund_route_required')

    def test_complete_apply_tamper_and_no_input_mutation(self):
        q=x.scenario();before=deepcopy(q);r=m.propose(q)
        self.assertEqual(q,before);self.assertEqual(m.apply(q,r),{**r,'status':'applied'})
        for key,value in [('measurement',{}),('historical_recognition',{}),('prior_findings',{}),
                          ('tax_vintages',[]),('prior_result',{}),('annual_close_ready',True),('committed',0)]:
            bad=deepcopy(r);bad[key]=value;self.assertEqual(m.apply(q,bad)['status'],'invalid')

if __name__=='__main__':unittest.main()
