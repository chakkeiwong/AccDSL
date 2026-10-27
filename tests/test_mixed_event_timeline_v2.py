from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
from unittest.mock import patch
import importlib.util
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('assessment_timeline_examples',ROOT/'data/accounting-master/assessment-timeline-20261025/examples.py')
ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex);api=ex.timeline

class AssessmentTimelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.initial=ex.start()

    def run_case(self,root,status='complete_mixed_timeline'):
        before=deepcopy((self.initial,root));r=api.run(self.initial,root)
        self.assertEqual(r['status'],status,r.get('reason',r.get('stop')))
        self.assertEqual((self.initial,root),before)
        for key in api.FLAGS:self.assertIs(r[key],False)
        return r

    def test_declared_cases(self):
        for name,(_,root,status) in ex.cases().items():
            with self.subTest(name=name):self.run_case(root,status)

    def test_entire_manual_decision_then_native_assessment_agrees(self):
        root=ex.root(self.initial);r=self.run_case(root)
        request=ex.manual_decision(self.initial,root)
        decision=api.decision.apply(self.initial,request,api.decision.propose(self.initial,request))
        self.assertEqual(r['trace'][0]['request'],request)
        self.assertEqual(r['trace'][0]['result'],decision)
        operation=root['operations'][0]['operation']
        native=api.runtime.transition(decision['after'],operation)
        self.assertEqual(r['trace'][1]['result']['transition'],native)
        self.assertEqual(r['after'],native['after'])
        report=api.runtime.annual.root.carry.statements(r['after']['opening'],r['after']['after'],r['after']['account_classes'])
        for k,v in report.items():
            if k not in ['scope','unresolved']:self.assertEqual(r['recorded_statements'][k],v)
        self.assertEqual(r['calendar'][1]['clock']['interval'],operation['event']['interval'])
        self.assertFalse(r['fiscal_complete'])

    def test_independent_tax_and_cash_arithmetic(self):
        r=self.run_case(ex.root(self.initial));b=r['after']['after']['balances']
        self.assertEqual((b['cash'],b['inventory'],b['revenue'],b['cogs']),('467/1','70/1','-15/1','10/1'))
        self.assertEqual(b['current_tax'],'5/4')
        self.assertEqual(Q(b['income_tax_payable']),-Q(41,4)-Q(5,4))
        self.assertEqual(r['after']['current_assessments'][-1]['calculation']['taxable_profit'],'5/1')
        self.assertEqual(r['after']['historical_vintages'],self.initial['historical_vintages'])
        self.assertEqual(r['trace'][1]['result']['transition']['flows'],[])

    def test_assessment_first_blocks_same_day_later_sale_and_preserves_prefix(self):
        root=ex.root(self.initial,True);r=self.run_case(root,'stopped_provisional')
        native=api.runtime.transition(self.initial,root['operations'][0]['operation'])
        self.assertEqual(r['after'],native['after']);self.assertEqual(len(r['trace']),1)
        self.assertEqual(r['after']['after']['balances']['current_tax'],'0/1')
        self.assertEqual(r['after']['after']['balances']['cash'],'452/1')
        self.assertEqual(r['stop']['outcome']['reason'],'event_inside_assessed_interval')
        self.assertEqual(r['remaining_actions'],r['calendar'][1:])

    def test_replacement_preserves_cumulative_tax_vintage(self):
        root=ex.replacement_root(self.initial);r=self.run_case(root)
        self.assertEqual(len(r['trace']),4)
        self.assertEqual(r['after']['after']['balances']['cash'],'949/2')
        self.assertEqual(r['after']['after']['balances']['inventory'],'65/1')
        self.assertEqual(r['after']['after']['balances']['current_tax'],'15/8')
        self.assertEqual([a['tax_amount'] for a in r['after']['current_assessments']],['5/4','15/8'])
        self.assertEqual(len(r['after']['period_vintages']),3)
        self.assertEqual(r['after']['period_vintages'][-1]['new_assessment'],'15/8')
        self.assertEqual(r['trace'][-1]['result']['transition']['journal']['current_tax'],'5/8')

    def test_unknown_false_and_missing_information_keep_sale_prefix(self):
        for mode,expected in [('unknown','unresolved'),('false','unsupported'),('missing','unresolved')]:
            root=ex.root(self.initial);event=root['operations'][0]['operation']['event']
            if mode=='unknown':event['information']['rate']={'status':'unknown','reason':'Missing rate'}
            elif mode=='missing':del event['information']['rate']
            else:event['model']['selected']=ex.annual.known(False)
            r=self.run_case(root,'stopped_provisional')
            self.assertEqual(r['stop']['outcome']['status'],expected)
            self.assertEqual(len(r['trace']),1);self.assertEqual(r['after']['after']['balances']['cash'],'467/1')

    def test_bad_later_clock_or_shape_prevents_all_execution(self):
        for mutate in [lambda e:e['interval'].update(activity_through='2027-01-01'),
                       lambda e:e['interval'].update(start='2027-01-03'),
                       lambda e:e.update(date='2027-01-02'),
                       lambda e:e['loss_policy'].update(extra='bad')]:
            root=ex.root(self.initial);mutate(root['operations'][0]['operation']['event'])
            with patch.object(api.runtime,'transition',wraps=api.runtime.transition) as call:
                self.run_case(root,'invalid');self.assertEqual(call.call_count,0)

    def test_duplicate_ids_ties_and_stale_state_refuse(self):
        root=ex.root(self.initial);root['operations'][0]['priority']=10
        self.run_case(root,'unresolved')
        root=ex.root(self.initial);token=api.digest([root['id'],root['schedules'][0]['id'],0])
        root['operations'][0]['operation']['event']['id']='scheduled-event:'+token
        self.run_case(root,'invalid')
        root=ex.root(self.initial);root['expected_state_sha256']='0'*64
        self.run_case(root,'invalid')

    def test_actual_32_current_assessment_boundary(self):
        root=ex.root(self.initial);root['schedules']=[];template=root['operations'][0]
        root['operations']=[deepcopy(template) for _ in range(32)]
        for i,row in enumerate(root['operations']):
            row.update(id='assessment-entry-'+str(i),priority=i)
            row['operation']['event'].update(id='assessment-'+str(i),mode='first' if i==0 else 'replace')
        r=self.run_case(root);self.assertEqual(len(r['trace']),32)
        self.assertEqual(len(r['after']['period_vintages']),3)
        root['operations'].append(deepcopy(template));self.run_case(root,'invalid')

    def test_deferred_and_carry_clocks_remain_explicitly_unsupported(self):
        for kind in ['deferred_assessment','provisional_carry']:
            root=ex.root(self.initial);root['operations'][0]['operation']={'kind':kind,'event':{}}
            self.run_case(root,'unsupported')

    def test_prior_direct_payment_decision_cases_preserve_financial_results(self):
        old=ex.load('assessment_prior_mixed','data/accounting-master/mixed-event-timeline-20261025/examples.py')
        for first in [True,False]:
            body=old.root(self.initial,first);baseline=api.prior.run(self.initial,body)
            new=deepcopy(body);new['profile']=api.PROFILE;r=self.run_case(new)
            for key in ['after','calendar','timeline_cursor','remaining_actions','stop']:
                self.assertEqual(r[key],baseline[key])
            for step,expected in zip(r['trace'],baseline['trace']):
                self.assertEqual(step['request'],expected['request'])
                if step['entry']['kind']=='native_operation':
                    self.assertEqual(step['result']['transition'],expected['result']['transition'])
                else:self.assertEqual(step['result'],expected['result'])

    def test_actual_64_mixed_boundary_with_assessments(self):
        root=ex.root(self.initial);template=root['operations'][0]
        root['operations']=[deepcopy(template) for _ in range(32)]
        for i,row in enumerate(root['operations']):
            row.update(id='assessment-entry-'+str(i),priority=i)
            row['operation']['event'].update(id='assessment-'+str(i),mode='first' if i==0 else 'replace')
        schedule=root['schedules'][0];schedule['priority']=100
        schedule['template']['bindings']['enabled']['value']=False
        schedule['calendar']={'kind':'every_days','start':'2027-01-02','end_exclusive':'2027-02-03','step_days':1}
        r=self.run_case(root);self.assertEqual(len(r['trace']),64)
        self.assertTrue(all(row['result']['status']=='no_action' for row in r['trace'][32:]))
        schedule['calendar']['end_exclusive']='2027-02-04';self.run_case(root,'invalid')

if __name__=='__main__':unittest.main()
