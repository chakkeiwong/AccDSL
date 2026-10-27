from pathlib import Path
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
s=importlib.util.spec_from_file_location('assessed_carry_examples',ROOT/'data/accounting-master/assessed-period-carry-20261024/examples.py')
x=importlib.util.module_from_spec(s);s.loader.exec_module(x);m=x.m
class AssessedCarryTests(unittest.TestCase):
    def test_strict_mode_and_prior_unknown_refused(self):
        q=x.request();q['model']['profile']='strict_annual_close_v1'
        self.assertEqual(m.run(q)['status'],'unsupported')
        q=x.request();q['prior_request']['recovery_capacity']={'status':'unknown','reason':'Missing capacity'}
        q['prior_sha256']=m.book.digest(q['prior_request']);r=m.run(q)
        self.assertEqual(r['status'],'unresolved');self.assertNotIn('opening',r)

    def test_positive_profit_and_shared_funding(self):
        q=x.deferred.scenario(ppe_base='100/1',debt_base='0/1',recognized='100/1',capacity='100/1')
        r=m.run(x.request(q));self.assertEqual(r['status'],'complete_provisional')
        self.assertEqual(r['carried_recorded_profit'],'75/4');self.assertEqual(r['opening']['balances']['retained'],'-123/4')
        r=m.run(x.request(x.deferred.scenario(taxable='2000/1'),[x.payment('999/2')]))
        self.assertEqual(r['status'],'stopped_provisional');self.assertEqual(r['stop']['status'],'funding_failure')
        self.assertEqual(r['after'],r['opening'])

    def test_actual_deferred_closing_not_old_reassessment(self):
        r=m.run(x.request());self.assertEqual(r['status'],'complete_provisional')
        self.assertEqual(r['carried_recorded_profit'],'-33/4');b=r['opening']['balances']
        self.assertEqual((b['retained'],b['dta'],b['dtl'],b['cash'],b['income_tax_payable']),('-15/4','8/1','-10/1','721/2','-19/4'))
        self.assertEqual(b['deferred_tax'],'0/1');self.assertEqual(r['recorded_statements']['recorded_profit'],'0/1')
        self.assertEqual(sum(Q(v) for v in r['carry_journal'].values()),0)

    def test_full_deferred_history_and_allocations_survive(self):
        r=m.run(x.request());p=r['prior_result'];o=r['opening']
        self.assertEqual(r['archive']['prior_deferred_calculation'],p['calculation'])
        self.assertEqual(r['archive']['prior_deferred_findings'],p['findings'])
        self.assertEqual(r['archive']['prior_recovery_capacity'],p['recovery_capacity'])
        self.assertEqual(o['tax_premises']['opening_dta'],'8/1');self.assertEqual(o['tax_premises']['opening_dtl'],'10/1')
        self.assertEqual(r['current_period_deferred_tax'],'unassessed');self.assertFalse(r['conditional_deferred_assessed'])
        self.assertEqual(r['loss_state'],p['loss_state'])

    def test_payment_and_depreciation_do_not_repeat_tax(self):
        r=m.run(x.request(operations=[x.payment(),x.depreciation()]));self.assertEqual(r['status'],'complete_provisional')
        self.assertEqual(r['after']['balances']['cash'],'1423/4');self.assertEqual(r['after']['balances']['current_tax'],'0/1')
        self.assertEqual(r['after']['balances']['deferred_tax'],'0/1')
        report=r['recorded_statements'];self.assertEqual(report['recorded_profit'],'-10/1')
        self.assertEqual(report['balance_sheet'],{'total_assets':'2735/4','total_liabilities':'110/1','equity_including_profit':'2295/4'})
        self.assertEqual(report['indirect_operating']['net'],'-19/4');self.assertEqual(set(report['reconciliations'].values()),{'0/1'})

    def test_zero_and_unchanged_deferred_scenarios(self):
        for previous,dta,dtl in [(x.deferred.scenario(rate='0/1'),'0/1','0/1'),
            (x.deferred.scenario(ppe_base='84/1',recognized='40/1',capacity='40/1'),'10/1','-4/1')]:
            r=m.run(x.request(previous));self.assertEqual(r['status'],'complete_provisional')
            self.assertEqual((r['opening']['balances']['dta'],r['opening']['balances']['dtl']),(dta,dtl))

    def test_loss_recognition_is_not_loss_consumption(self):
        q=x.deferred.scenario(taxable='-19/1',paid=False,capacity='42/1')
        next(i for i in q['items'] if i['id'].startswith('loss/'))['recognized_deduction']=x.known('10/1')
        r=m.run(x.request(q));self.assertEqual(r['status'],'complete_provisional')
        self.assertEqual(r['opening']['balances']['dta'],'21/2');self.assertEqual(r['loss_state']['lots'][0]['remaining'],'19/1')
        self.assertEqual(r['current_period_tax'],'unassessed')

    def test_false_unknown_and_true_never_promote(self):
        for value in [None,False,True]:
            fs={k:({'status':'unknown','reason':'Missing'} if value is None else x.known(value)) for k in m.FINDINGS}
            r=m.run(x.request(findings=fs));self.assertEqual(r['status'],'complete_provisional')
            self.assertEqual(r['findings'],fs);self.assertFalse(r['annual_close_ready']);self.assertFalse(r['complete_financial_statements'])

    def test_dates_ids_and_prefix(self):
        q=x.request()
        for change in [('id','deferred-assessment'),('prior_sha256','0'*64)]:
            a=deepcopy(q);a[change[0]]=change[1];self.assertEqual(m.run(a)['status'],'invalid')
        a=deepcopy(q);a['next_period']['start']='2026-01-02';self.assertEqual(m.run(a)['status'],'invalid')
        r=m.run(x.request(operations=[x.payment('1/1'),x.payment('5/1',identity='excess')]))
        self.assertEqual(r['status'],'stopped_provisional');self.assertEqual(len(r['trace']),1)
        self.assertEqual(r['after']['balances']['cash'],'719/2')

    def test_complete_apply_and_tamper(self):
        q=x.request();r=m.run(q);a=m.apply(q,r);self.assertEqual(a['status'],'applied_provisional')
        for k in ['opening','after','loss_state','findings','archive','prior_result']:self.assertEqual(a[k],r[k])
        for key,value in [('archive',{}),('prior_result',{}),('annual_close_ready',True),('conditional_deferred_assessed',True)]:
            bad=deepcopy(r);bad[key]=value;self.assertEqual(m.apply(q,bad)['status'],'invalid')
        self.assertEqual(a['current_period_deferred_tax'],'unassessed')

if __name__=='__main__':unittest.main()
