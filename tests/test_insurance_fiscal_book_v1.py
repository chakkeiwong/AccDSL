from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import importlib.util
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import insurance_fiscal_book_v1 as fiscal
spec=importlib.util.spec_from_file_location('insurance_fiscal_examples',ROOT/'data/accounting-master/insurance-fiscal-book-20261025/examples.py')
ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)


class InsuranceFiscalBookTests(unittest.TestCase):
    def result(self,q,status='proposed_provisional'):
        before=deepcopy(q);r=fiscal.propose(q)
        self.assertEqual(r['status'],status,r);self.assertEqual(q,before)
        self.assertTrue(all(r[k] is False for k in fiscal.FLAGS))
        if status!='proposed_provisional':self.assertNotIn('execution',r)
        return r

    def test_two_charts_two_cases_and_complements(self):
        for chart in ['named','numbered']:
            for case in fiscal.base.CASES:
                for complement in [False,True]:ex.checked_case(chart,case,complement)

    def test_exact_replay_and_tampered_result(self):
        q=ex.fixture();r=self.result(q)
        self.assertTrue(fiscal.verify(q,r))
        r['execution']['current']['memory']['insurance']['loss_component']='1/1'
        self.assertFalse(fiscal.verify(q,r))

    def test_only_balance_conditions_change(self):
        q=ex.fixture();compiled,baseline,changes=fiscal.build(q)
        for i in range(1,7):
            key='insurance.'+str(i);old=baseline['program']['registry']['entries'][key]
            current=compiled['registry']['entries'][key]
            if i<=3:self.assertEqual(current,old);continue
            delta=next(d for d in changes if d['method_key']==key)
            self.assertEqual(len(delta['deltas']),8)
            restored=deepcopy(current)
            for d in delta['deltas']:
                row=next(x for x in restored['method'][d['phase']]['manifest']['requirements'] if x['id']=='balance_'+d['role'])
                row['predicate']['right']['value']=d['before']
            restored['method_sha256']=fiscal.core.digest(restored['method'])
            self.assertEqual(restored,old)

    def test_native_dates_zero_profit_carry_and_fiscal_profit(self):
        q=ex.fixture();r=self.result(q);trace=r['execution']['trace']
        dates=[x['command']['event']['date'] for x in trace if x['command']['kind']=='event']
        self.assertEqual(dates,['2026-01-01']*3+['2027-01-01']*3)
        carries=[x for x in trace if x['command']['kind']=='carry']
        self.assertTrue(all(v=='0/1' for v in carries[0]['result']['journal'].values()))
        self.assertEqual([x['result']['report']['income']['profit'] for x in carries],['0/1','-5/1','10/1'])
        self.assertEqual([x['result']['next_opening']['period']['start'] for x in carries],['2026-01-01','2027-01-01','2028-01-01'])
        self.assertEqual(sum(fiscal.Fraction(x['result']['report']['income']['profit']) for x in carries),5)

    def test_archive_hashes_and_no_cash_on_close(self):
        q=ex.fixture();r=self.result(q)
        for row in r['execution']['trace']:
            if row['command']['kind']!='carry':continue
            c=row['result'];a=c['archive']
            for key,value in [('report_sha256',c['report']),('closed_book_sha256',c['closed_book']),
                              ('next_opening_sha256',c['next_opening']),('memory_policies_sha256',q['memory_policies'])]:
                self.assertEqual(a[key],fiscal.core.digest(value))
            self.assertEqual(c['cash_flows'],[]);self.assertEqual(c['next_opening']['flows'],[])
            self.assertEqual(c['journal'][q['base_request']['roles']['cash']],'0/1')

    def test_unmodified_second_year_method_stops_after_valid_prefix(self):
        q=ex.fixture();compiled,baseline,_=fiscal.build(q)
        compiled['registry']['entries']['insurance.4']=deepcopy(baseline['program']['registry']['entries']['insurance.4'])
        r=fiscal.program.run(compiled)
        self.assertEqual(r['status'],'stopped_provisional');self.assertEqual(len(r['trace']),6)
        self.assertEqual(r['stop']['reason'],'preconditions')
        self.assertEqual(r['current']['memory']['insurance']['next_step'],'3/1')

    def test_missing_carry_and_date_shift_stop(self):
        q=ex.fixture();compiled,_,_=fiscal.build(q)
        missing=deepcopy(compiled);missing['commands'].pop(5)
        r=fiscal.program.run(missing)
        self.assertEqual(r['status'],'stopped_provisional');self.assertEqual(len(r['trace']),5)
        shifted=deepcopy(compiled);shifted['commands'][6]['event']['date']='2026-12-31'
        r=fiscal.program.run(shifted);self.assertEqual(r['status'],'stopped_provisional')
        self.assertEqual(len(r['trace']),6)

    def test_skipped_and_repeated_event_refuse(self):
        q=ex.fixture();compiled,_,_=fiscal.build(q)
        skipped=deepcopy(compiled);skipped['commands'].pop(6)
        r=fiscal.program.run(skipped);self.assertEqual(r['status'],'stopped_provisional');self.assertEqual(len(r['trace']),6)
        repeated=deepcopy(compiled);repeated['commands'].insert(2,deepcopy(repeated['commands'][1]))
        r=fiscal.program.run(repeated);self.assertEqual(r['status'],'stopped_provisional');self.assertEqual(len(r['trace']),2)

    def test_stale_result_hash_and_forged_native_result(self):
        q=ex.fixture();q['base_result_sha256']='0'*64
        self.assertEqual(self.result(q,'invalid')['reason'],'base_result_recomputation')
        q=ex.fixture();b=q['base_request'];b['native_result']['report']['journals'][0]['finance_expense']='9'
        b['native_result_sha256']=fiscal.core.digest(b['native_result'])
        self.assertIn('native_result_recomputation',self.result(q,'invalid')['reason'])

    def test_unknown_and_false_native_findings_preserved(self):
        for value,status in [(None,'unresolved'),(False,'unsupported')]:
            q=ex.fixture();b=q['base_request'];b['native_request']['findings']['source_profile_applicable']=value
            b['native_request_sha256']=fiscal.core.digest(b['native_request'])
            self.assertIn('source_profile_applicable',self.result(q,status)['reason'])

    def test_unbound_fiscal_policy_and_completeness_refuse(self):
        for key,value in [('kind','automatic'),('event_completeness','complete'),('premise','')]:
            q=ex.fixture();q['fiscal_policy'][key]=value;self.result(q,'invalid')

    def test_retained_account_wrong_class_missing_or_role(self):
        for key in ['absent','cash','liability']:
            q=ex.fixture();q['retained_account']=q['base_request']['roles'].get(key,key)
            self.assertEqual(self.result(q,'invalid')['reason'],'retained_equity_account')

    def test_memory_policy_missing_extra_or_reset_refuse(self):
        for kind in ['missing','extra','reset','empty_provenance']:
            q=ex.fixture();p='/insurance/loss_component'
            if kind=='missing':q['memory_policies'].pop(p)
            elif kind=='extra':q['memory_policies']['/absent']={'kind':'preserve','provenance':'x'}
            elif kind=='reset':q['memory_policies'][p]['kind']='reset'
            else:q['memory_policies'][p]['provenance']=''
            self.result(q,'invalid')

    def test_closed_shape_recursive_input_and_dependency_change(self):
        q=ex.fixture();q['extra']=True;self.result(q,'invalid')
        q=ex.fixture();q['memory_policies']['cycle']=q
        with patch.object(fiscal.base,'propose') as base:
            self.assertEqual(fiscal.propose(q)['status'],'invalid');base.assert_not_called()
        q=ex.fixture()
        with patch.dict(fiscal.PINS,{'scripts/company_book_carry_v1.py':'0'*64}):
            with patch.object(fiscal.base,'propose') as base:
                self.assertEqual(self.result(q,'invalid')['reason'],'dependency_hash:scripts/company_book_carry_v1.py')
                base.assert_not_called()


if __name__=='__main__':unittest.main()
