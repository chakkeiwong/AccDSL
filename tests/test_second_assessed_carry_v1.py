from pathlib import Path
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
s=importlib.util.spec_from_file_location('second_carry_examples',ROOT/'data/accounting-master/second-assessed-carry-20261024/examples.py')
x=importlib.util.module_from_spec(s);s.loader.exec_module(x);m=x.m

class SecondCarryTests(unittest.TestCase):
    def test_negative_profit_actual_retained_transfer(self):
        r=m.run(x.request());self.assertEqual(r['status'],'complete_provisional')
        self.assertEqual(r['carried_recorded_profit'],'-17/1');b=r['after']['balances']
        self.assertEqual(b['retained'],'53/4');self.assertEqual(r['carry_journal']['retained'],'17/1')
        self.assertEqual(sum(Q(v) for v in r['carry_journal'].values()),0)
        self.assertEqual(b['cash'],'715/2');self.assertEqual(b['dta'],'5/1');self.assertEqual(b['dtl'],'-5/1')
        self.assertEqual(b['income_tax_payable'],'-35/4')
        self.assertEqual(r['recorded_statements']['balance_sheet'],{'total_assets':'1361/2','total_liabilities':'455/4','equity_including_profit':'2267/4'})
        self.assertEqual(r['recorded_statements']['recorded_profit'],'0/1')
        self.assertEqual(set(r['recorded_statements']['reconciliations'].values()),{'0/1'})

    def test_positive_and_zero_profit_signs(self):
        for body,profit,retained,journal in [(x.positive_profit(),'6/1','-107/4','-6/1'),
                                           (x.zero_profit(),'0/1','-15/4','0/1')]:
            r=m.run(body);self.assertEqual(r['status'],'complete_provisional')
            self.assertEqual(r['carried_recorded_profit'],profit);self.assertEqual(r['after']['balances']['retained'],retained)
            self.assertEqual(r['carry_journal']['retained'],journal)
            self.assertEqual(r['recorded_statements']['balance_sheet'],r['prior_result']['recorded_statements']['balance_sheet'])

    def test_historical_settlements_and_period_openings_are_distinct(self):
        r=m.run(x.request());p=r['prior_result']
        self.assertEqual(r['tax_vintages'],p['tax_vintages'])
        self.assertEqual([v['opening_payable'] for v in r['period_vintages']],['15/4','5/1'])
        self.assertEqual([len(v['settlements']) for v in r['tax_vintages']],[1,1])
        self.assertTrue(all(v['settlements']==[] for v in r['period_vintages']))
        self.assertEqual(r['after']['flows'],[]);self.assertEqual(r['archive']['prior_flows'],p['after']['flows'])
        self.assertEqual(r['recorded_statements']['cash_flows']['net_movement'],'0/1')
        for old,new in zip(r['tax_vintages'],r['period_vintages']):
            self.assertEqual(old['id'],new['id']);self.assertEqual(new['prior_vintage_sha256'],m.book.digest(old))
        self.assertEqual(r['tax_vintages'][1]['supersession_history'],p['tax_vintages'][1]['supersession_history'])

    def test_fully_paid_vintages_are_not_discarded(self):
        r=m.run(x.paid_vintages());self.assertEqual(r['status'],'complete_provisional')
        self.assertEqual(len(r['tax_vintages']),2);self.assertEqual(len(r['period_vintages']),2)
        self.assertEqual([v['opening_payable'] for v in r['period_vintages']],['0/1','0/1'])
        self.assertEqual([len(v['settlements']) for v in r['tax_vintages']],[1,1])
        self.assertEqual(r['after']['balances']['income_tax_payable'],'0/1')

    def test_all_permanent_accounts_and_components_survive(self):
        r=m.run(x.request());p=r['prior_result'];old=p['after'];new=r['after'];classes=m.classes(p)
        self.assertEqual(len(new['balances']),26)
        for key,value in old['balances'].items():
            if key not in classes['income']+['retained']:self.assertEqual(new['balances'][key],value,key)
        self.assertTrue(all(new['balances'][k]=='0/1' for k in classes['income']))
        for key in ['component','lots','leases','other_inventory','context']:self.assertEqual(new[key],old[key],key)
        self.assertEqual(new['seen'],old['seen']+['second-carry-2027'])
        self.assertEqual(new['prior_years'][:-1],old['prior_years'])
        self.assertEqual(new['date'],'2027-01-01');self.assertEqual(new['tax_closed_until'],'2027-01-01')

    def test_loss_and_recognition_archive_are_not_renewed(self):
        r=m.run(x.request(x.previous.loss_scenario()));p=r['prior_result']
        self.assertEqual(r['loss_state'],p['loss_state']);self.assertEqual(r['loss_state']['cursor'],'2027-01-01')
        self.assertEqual(r['loss_state']['lots'][0]['remaining'],'9/1')
        self.assertEqual(r['archive']['recognition_capacity'],p['recovery_capacity'])
        self.assertEqual(r['archive']['recognition_measurement'],p['measurement'])
        self.assertEqual(r['archive']['earlier_recognition'],p['historical_recognition'])
        self.assertEqual(r['current_period_tax'],'unassessed');self.assertEqual(r['current_period_deferred_tax'],'unassessed')
        self.assertEqual(r['after']['tax_premises']['opening_dta'],'29/4')
        self.assertFalse(r['conditional_current_assessed']);self.assertFalse(r['conditional_deferred_assessed'])

    def test_findings_do_not_promote_annual_readiness(self):
        for value,status in [(None,'unresolved'),(True,'asserted_true'),(False,'asserted_false')]:
            findings={k:({'status':'unknown','reason':'Missing'} if value is None else x.known(value)) for k in m.FINDINGS}
            r=m.run(x.request(findings=findings));self.assertEqual(r['status'],'complete_provisional')
            self.assertEqual(set(r['finding_status'].values()),{status});self.assertEqual(r['findings'],findings)
            self.assertFalse(r['annual_close_ready']);self.assertFalse(r['complete_financial_statements']);self.assertFalse(r['committed'])

    def test_incomplete_year_and_noncontiguous_period_refuse(self):
        partial=x.previous.previous.scenario(end='2026-10-01',through='2026-09-30')
        r=m.run(x.request(x.previous.scenario(partial)));self.assertEqual(r['status'],'unresolved')
        self.assertEqual(r['reason'],'assessment_or_loss_incomplete');self.assertNotIn('opening',r)
        q=x.request()
        for change in [{'start':'2027-01-02'},{'start':'2026-12-31'},{'end_exclusive':'2027-01-01'}]:
            bad=deepcopy(q);bad['next_period'].update(change);self.assertEqual(m.run(bad)['status'],'invalid')

    def test_no_implicit_new_period_operations(self):
        q=x.request();q['operations']=[];r=m.run(q)
        self.assertEqual(r['status'],'invalid');self.assertNotIn('after',r)
        q=x.request();q['model']['profile']='certified_annual_close_v1'
        self.assertEqual(m.run(q)['status'],'unsupported')

    def test_period_opening_tamper_is_rejected(self):
        r=m.run(x.request())
        for mutate in [lambda v:v[0].update(opening_payable='1/1'),
                       lambda v:v[0].update(prior_vintage_sha256='0'*64),
                       lambda v:v[0]['settlements'].append({'amount':'1/1'}),
                       lambda v:v[0]['period'].update(start='2028-01-01')]:
            bad=deepcopy(r['period_vintages']);mutate(bad)
            with self.assertRaises(ValueError):m.period_opening_invariant(r['after'],r['tax_vintages'],bad)

    def test_complete_apply_and_request_immutability(self):
        q=x.request();before=deepcopy(q);r=m.run(q)
        self.assertEqual(q,before);self.assertEqual(m.apply(q,r),{**r,'status':'applied_provisional'})
        for key,value in [('archive',{}),('tax_vintages',[]),('period_vintages',[]),('prior_result',{}),
                          ('loss_state',{}),('annual_close_ready',True),('committed',0)]:
            bad=deepcopy(r);bad[key]=value;self.assertEqual(m.apply(q,bad)['status'],'invalid')

if __name__=='__main__':unittest.main()
