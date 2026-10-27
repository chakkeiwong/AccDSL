from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import importlib.util,os,sys,unittest
os.environ['CUDA_VISIBLE_DEVICES']='-1'
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('inventory_family_examples',ROOT/'data/accounting-master/annual-inventory-family-20261025/examples.py')
x=importlib.util.module_from_spec(s);s.loader.exec_module(x);m=x.m

class AnnualInventoryFamilyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body=deepcopy(x.fixture());cls.result=m.run(cls.body)
        cls.reports={p['start']:m.joint_report(cls.body,cls.result,p['start']) for p in cls.body['periods']}

    def test_full_requests_and_results_match_direct_execution(self):
        self.assertEqual(self.result['status'],'evaluated_with_incomplete_members')
        for member,row in zip(self.body['members'],self.result['members']):
            request=m.runtime.request(self.body['root_request'],member['operations'])
            self.assertEqual(m.member_request(self.body,member),request)
            self.assertEqual(row['result'],m.runtime.run(request));self.assertEqual(row['result_sha256'],m.digest(row['result']))
            self.assertEqual(row['assumptions'],member['assumptions'])

    def test_simple_partial_and_full_sale(self):
        body=x.simple();r=m.run(body);self.assertEqual(r['status'],'evaluated_all_members')
        self.assertEqual(r['members'][0]['result']['period_book']['after']['lots']['recovered']['units'],'1/1')
        self.assertTrue(r['members'][1]['result']['period_book']['after']['lots']['recovered']['disposed'])

    def test_failure_prefixes_and_pending_operations_preserved(self):
        expected={'unknown_units':(0,'unresolved'),'false_divisibility':(0,'unsupported'),'oversale':(0,'invalid'),'unsupported_method':(0,'unsupported'),'later_oversale':(4,'invalid')}
        for member,row in zip(self.body['members'],self.result['members']):
            if member['id'] in expected:
                result=row['result'];self.assertEqual((result['stop']['index'],result['stop']['status']),expected[member['id']])
                self.assertEqual(result['remaining_operations'],member['operations'][len(result['trace']):])

    def test_joint_reports_preserve_complete_vectors(self):
        for period,report in self.reports.items():
            self.assertEqual(report['status'],'joint_authored_reports')
            for row,member in zip(report['members'],self.result['members']):
                state=member['result']['period_book'];archive=[a for a in state['period_archive'] if a['after']['period']['start']==period]
                expected=archive[0]['report'] if archive else member['result']['recorded_statements'] if state['after']['period']['start']==period else None
                self.assertEqual(row['report'],expected)
                self.assertEqual(row['report_sha256'],m.digest(expected) if expected else None)
                if expected is None:self.assertEqual(row['status'],'unavailable')

    def test_financial_controls_and_tax_vintages(self):
        first=self.reports['2027-01-01']['members'][0]['report'];later=self.reports['2028-01-01']['members'][0]['report']
        self.assertEqual(first['recorded_profit'],'3/1');self.assertEqual(first['cash_flows']['closing_cash'],'467/1')
        self.assertEqual(later['recorded_profit'],'5/1');self.assertEqual(later['cash_flows']['closing_cash'],'482/1')
        for report in [first,later]:self.assertEqual(report['cash_flows']['activities']['operating']['net'],'15/1')
        state=self.result['members'][0]['result']['period_book'];self.assertEqual(state['after']['balances']['income_tax_payable'],'-49/4')
        self.assertEqual(state['period_archive'][0]['after']['lots']['recovered']['units'],'1/1')
        self.assertEqual(self.result['members'][1]['result']['period_book']['after']['balances']['income_tax_payable'],'-53/4')

    def test_unreached_periods_are_unavailable_not_zero(self):
        rows={r['id']:r for r in self.reports['2028-01-01']['members']}
        for key in ['unknown_units','false_divisibility','oversale','unsupported_method']:
            self.assertIsNone(rows[key]['report']);self.assertEqual(rows[key]['reason'],'period_not_reached')
        self.assertEqual(rows['later_oversale']['status'],'current_prefix_provisional')

    def test_budgets_and_empty_selection_preserve_meaning(self):
        for budget in [0,2]:
            body=x.variant(budget=budget);result=m.run(body)
            self.assertEqual(result['status'],'partial_evaluation');self.assertEqual(result['checked_members'],budget)
            self.assertEqual(result['members'][:budget],self.result['members'][:budget])
            self.assertEqual(result['unvisited_member_ids'],[z['id'] for z in body['members'][budget:]])
            for row in result['members'][budget:]:self.assertIsNone(row['result'])
            report=m.joint_report(body,result,'2027-01-01')
            for row in report['members'][budget:]:self.assertIsNone(row['report']);self.assertEqual(row['reason'],'member_budget')
        empty=m.run(x.variant(budget=0,empty=True));self.assertEqual(empty['status'],'empty_authored_selection');self.assertEqual(empty['declared_search'],'complete')

    def test_equal_outputs_preserve_distinct_names(self):
        first,last=self.result['members'][0],self.result['members'][-1]
        self.assertEqual(last['id'],'同額別案');self.assertEqual(first['result'],last['result']);self.assertNotEqual(first['member_sha256'],last['member_sha256'])

    def test_validation_is_pure(self):
        with patch.object(m.runtime,'run',side_effect=AssertionError('hidden runtime')),patch.object(m.annual.root,'run',side_effect=AssertionError('hidden root')):
            self.assertEqual(m.validate(self.body),self.body)

    def test_invalid_structures_weights_and_limits_reject(self):
        changes=[lambda q:q['members'][1].update(id=q['members'][0]['id']),lambda q:q['members'][0]['assumptions'].append(deepcopy(q['members'][0]['assumptions'][0])),lambda q:q['members'][0].update(weight='1/8'),lambda q:q.update(weighting='equal_probability'),lambda q:q.update(coverage='all_feasible_histories'),lambda q:q['budget'].update(max_members=True),lambda q:q['budget'].update(max_members=-1),lambda q:q['budget'].update(max_members=65),lambda q:q.update(members=[deepcopy(q['members'][0]) for _ in range(65)]),lambda q:q.update(name='\ud800')]
        for change in changes:
            body=deepcopy(self.body);change(body);self.assertEqual(m.run(body)['status'],'invalid')

    def test_root_horizon_and_calendar_reject(self):
        body=deepcopy(self.body);body['root_sha256']='0'*64;self.assertEqual(m.run(body)['reason'],'root_digest')
        body=deepcopy(self.body);body['periods'][0]['start']='2026-12-31';self.assertEqual(m.run(body)['reason'],'root_period')
        body=deepcopy(self.body);body['periods'][0]['start']='2027-02-30';self.assertEqual(m.run(body)['status'],'invalid')
        body=deepcopy(self.body);body['members'][0]['operations'][3]['event']['next_period']['end_exclusive']='2030-01-01';self.assertEqual(m.run(body)['reason'],'member_horizon')

    def test_zero_budget_still_checks_unavailable_root(self):
        body=x.variant(budget=0);body['root_request']['operations'].append({'kind':'unknown','event':{}});body['root_sha256']=m.digest(body['root_request'])
        result=m.run(body);self.assertEqual(result['status'],'root_unavailable');self.assertEqual(result['checked_members'],0)
        self.assertEqual(len(result['members']),len(body['members']))
        report=m.joint_report(body,result,'2027-01-01');self.assertTrue(all(r['reason']=='root_unavailable' and r['report'] is None for r in report['members']))

    def test_rehashed_financial_and_assumption_tampering_reject(self):
        for change in [lambda z:z['members'][0]['result']['period_book']['after']['balances'].update(cash='999/1'),lambda z:z['members'][0].update(assumptions=[])]:
            result=deepcopy(self.result);change(result);result['members'][0]['result_sha256']=m.digest(result['members'][0]['result'])
            self.assertFalse(m.verify_result(self.body,result));self.assertEqual(m.joint_report(self.body,result,'2027-01-01')['reason'],'family_replay')
        body=x.variant(budget=0);result=m.run(body);result['members'].pop();self.assertFalse(m.verify_result(body,result))

    def test_legacy_family_financial_semantics_unchanged(self):
        old,new=x.legacy_pair();a=x.legacy.m.run(old);b=m.run(new)
        self.assertEqual(a['status'],b['status']);self.assertEqual(a['declared_search'],b['declared_search'])
        self.assertEqual(x.financial_result(a['root_check']),x.financial_result(b['root_check']))
        for prior,current in zip(a['members'],b['members']):
            self.assertEqual(prior['id'],current['id']);self.assertEqual(prior['assumptions'],current['assumptions'])
            self.assertEqual(x.financial_result(prior['result']),x.financial_result(current['result']))

    def test_no_admission_or_input_mutation(self):
        before=m.canonical(self.body);result=m.run(self.body);self.assertEqual(before,m.canonical(self.body))
        for key in ['probability_admitted','historical_family_admitted','annual_ready','source_admission','accounting_admission','exhaustive_scenario_coverage']:self.assertIs(result[key],False)

    def test_legacy_family_rejects_optional_sale(self):
        body=x.simple();body['profile']=x.legacy.m.PROFILE
        self.assertEqual(x.legacy.m.run(body)['status'],'invalid')

    def test_outside_period_query_invalid(self):
        self.assertEqual(m.joint_report(self.body,self.result,'2030-01-01')['reason'],'outside_authored_horizon')

if __name__=='__main__':unittest.main()
