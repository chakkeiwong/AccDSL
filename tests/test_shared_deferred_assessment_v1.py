from pathlib import Path
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
s=importlib.util.spec_from_file_location('deferred_examples',ROOT/'data/accounting-master/shared-deferred-assessment-20261024/examples.py')
x=importlib.util.module_from_spec(s);s.loader.exec_module(x);m=x.m

class DeferredTests(unittest.TestCase):
    def test_incremental_gross_balances_and_statements(self):
        r=m.propose(x.scenario());self.assertEqual(r['status'],'proposed')
        self.assertEqual(r['after']['balances']['dta'],'8/1');self.assertEqual(r['after']['balances']['dtl'],'-10/1')
        self.assertEqual(r['journal']['dta'],'-2/1');self.assertEqual(r['journal']['dtl'],'-6/1')
        self.assertEqual(r['journal']['deferred_tax'],'8/1');self.assertEqual(sum(Q(v) for v in r['journal'].values()),0)
        report=r['recorded_statements'];self.assertEqual(report['recorded_profit'],'-33/4')
        self.assertEqual(report['balance_sheet'],{'total_assets':'1397/2','total_liabilities':'459/4','equity_including_profit':'2335/4'})
        self.assertEqual(report['indirect_operating']['net'],'-59/2')
        self.assertEqual(set(report['reconciliations'].values()),{'0/1'})

    def test_preserves_cash_current_tax_loss_and_component_history(self):
        r=m.propose(x.scenario());old=r['prior_result']['after'];new=r['after']
        for k,v in old.items():
            if k not in ['balances','seen']:self.assertEqual(new[k],v,k)
        for k,v in old['balances'].items():
            if k not in ['dta','dtl','deferred_tax']:self.assertEqual(new['balances'][k],v,k)
        self.assertEqual(r['loss_state'],r['prior_result']['loss_state'])
        self.assertEqual(new['seen'],old['seen']+['deferred-assessment'])
        self.assertFalse(r['accounting_admission']);self.assertFalse(r['annual_close_ready'])
        self.assertTrue(r['conditional_deferred_assessed']);self.assertTrue(r['deferred_asset_recognized'])

    def test_zero_rate_reverses_recorded_balances_without_cash(self):
        r=m.propose(x.scenario(rate='0/1'));self.assertEqual(r['status'],'proposed')
        self.assertEqual(r['after']['balances']['dta'],'0/1');self.assertEqual(r['after']['balances']['dtl'],'0/1')
        self.assertEqual(r['journal']['deferred_tax'],'6/1');self.assertFalse(r['deferred_asset_recognized'])

    def test_matching_bases_and_unchanged_desired_balances(self):
        q=x.scenario(ppe_base='84/1',recognized='40/1',capacity='40/1')
        r=m.propose(q);self.assertEqual(r['status'],'proposed');self.assertTrue(all(v=='0/1' for v in r['journal'].values()))
        r=m.propose(x.scenario(ppe_base='100/1',debt_base='100/1',recognized='0/1',capacity='0/1'))
        self.assertEqual(r['status'],'proposed');self.assertEqual(r['journal']['deferred_tax'],'6/1')

    def test_asset_deduction_and_liability_taxable_signs(self):
        q=x.scenario(ppe_base='140/1',debt_base='120/1',recognized='0/1',capacity='20/1')
        x.item(q,'account/ppe')['recognized_deduction']=x.known('20/1')
        r=m.propose(q);self.assertEqual(r['status'],'proposed')
        self.assertEqual(r['calculation']['desired_dta'],'5/1');self.assertEqual(r['calculation']['desired_dtl'],'5/1')
        self.assertEqual(r['journal']['deferred_tax'],'6/1')

    def test_partial_and_unrecognized_deductions(self):
        r=m.propose(x.scenario(recognized='0/1',capacity='0/1'));self.assertEqual(r['status'],'proposed')
        debt=next(a for a in r['calculation']['items'] if a['id']=='account/debt')
        self.assertEqual(debt['unrecognized_deduction'],'40/1');self.assertEqual(debt['desired_dta'],'0/1')
        self.assertEqual(r['journal']['deferred_tax'],'16/1')

    def test_capacity_shared_with_losses_and_never_generated_from_dtl(self):
        q=x.scenario(taxable='-19/1',paid=False);loss=next(i for i in q['items'] if i['id'].startswith('loss/'))
        loss['recognized_deduction']=x.known('10/1')
        r=m.propose(q);self.assertEqual(r['status'],'invalid');self.assertEqual(r['reason'],'recovery_capacity_reused')
        q['recovery_capacity']=x.known('42/1');r=m.propose(q);self.assertEqual(r['status'],'proposed')
        self.assertEqual(r['calculation']['desired_dta'],'21/2')
        self.assertEqual(r['loss_state'],r['prior_result']['loss_state'])
        self.assertEqual(r['loss_state']['lots'][0]['remaining'],'19/1')

    def test_unknown_false_and_unsupported_allocation(self):
        q=x.scenario()
        for value,status in [({'status':'unknown','reason':'Not established'},'unresolved'),(x.known(False),'unsupported')]:
            a=deepcopy(q);a['findings']['single_recovery_pool_supported']=value
            r=m.propose(a);self.assertEqual(r['status'],status);self.assertNotIn('after',r)
        for route in ['other_comprehensive_income','equity','business_combination','offset']:
            a=deepcopy(q);x.item(a,'account/ppe')['route']=x.known(route)
            self.assertEqual(m.propose(a)['status'],'unsupported')
        a=deepcopy(q);x.item(a,'account/ppe')['rate']={'status':'unknown','reason':'Missing rate'}
        self.assertEqual(m.propose(a)['status'],'unresolved')

    def test_duplicate_missing_and_extra_item_rejected(self):
        q=x.scenario()
        for mode in ['duplicate','missing','extra']:
            a=deepcopy(q)
            if mode=='duplicate':a['items'].append(deepcopy(a['items'][0]))
            elif mode=='missing':a['items'].pop()
            else:a['items'][0]['id']='invented'
            r=m.propose(a);self.assertEqual(r['status'],'invalid');self.assertNotIn('after',r)

    def test_basis_binding_and_recorded_allocation(self):
        q=x.scenario()
        for identity,field,value in [('account/ppe','tax_base','61/1'),('account/debt','recorded_dta','9/1'),
            ('account/ppe','recorded_dta','1/1'),('lease/lease1/A/asset','tax_base','0/1'),
            ('inventory/lot/recovered','tax_base','1/1')]:
            a=deepcopy(q);x.item(a,identity)[field]=x.known(value)
            self.assertEqual(m.propose(a)['status'],'invalid')

    def test_negative_mistyped_excess_and_fractional_inputs(self):
        q=x.scenario()
        for identity,field,value in [('account/ppe','rate','-1/4'),('account/debt','recognized_deduction','41/1'),
            ('account/ppe','recognized_deduction','1/1'),('account/ppe','tax_base',60),
            ('account/debt','recorded_dta',True)]:
            a=deepcopy(q);x.item(a,identity)[field]=x.known(value);self.assertEqual(m.propose(a)['status'],'invalid')
        r=m.propose(x.scenario(rate='1/3'));self.assertEqual(r['status'],'proposed')
        self.assertEqual(r['calculation']['desired_dta'],'32/3');self.assertEqual(r['calculation']['desired_dtl'],'40/3')

    def test_identity_and_full_apply(self):
        q=x.scenario();before=deepcopy(q);r=m.propose(q);a=m.apply(q,r)
        self.assertEqual(q,before);self.assertEqual(a['status'],'applied')
        for k in ['after','prior_result','loss_state','calculation','findings']:self.assertEqual(a[k],r[k])
        for key,value in [('annual_close_ready',True),('calculation',{}),('prior_result',{}),('committed',0)]:
            bad=deepcopy(r);bad[key]=value;self.assertEqual(m.apply(q,bad)['status'],'invalid')
        q['id']='replacement-assessment';self.assertEqual(m.propose(q)['status'],'invalid')
        q['prior_sha256']='0'*64;self.assertEqual(m.propose(q)['status'],'invalid')

if __name__=='__main__':unittest.main()
