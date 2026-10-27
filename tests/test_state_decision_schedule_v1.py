from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import importlib.util
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import state_decision_schedule_v1 as m
spec=importlib.util.spec_from_file_location('schedule_examples',ROOT/'data/accounting-master/state-decision-schedule-20261025/examples.py')
e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)


class StateDecisionScheduleTests(unittest.TestCase):
    def run_case(self,state,root,status='complete_scheduled_decisions'):
        before=deepcopy((state,root));result=m.run(state,root)
        self.assertEqual(result['status'],status,result);self.assertEqual((state,root),before)
        self.assertTrue(all(result[key] is False for key in m.FLAGS))
        return result

    def test_exact_manual_requests_and_complete_decision_sequence(self):
        state=e.start();root=e.root(state);result=self.run_case(state,root)
        manual_state=deepcopy(state);requests=[];outcomes=[]
        for index,date in enumerate(['2027-01-02','2027-01-03','2027-01-04']):
            token=m.digest(['stock-calendar','daily-sale',index])
            request=e.decision_examples.request(manual_state,'scheduled-decision:'+token,date,demand='1/1')
            request['event']['id']='scheduled-event:'+token
            proposal=m.decision.propose(manual_state,request)
            outcome=m.decision.apply(manual_state,request,proposal)
            requests.append(request);outcomes.append(outcome);manual_state=outcome['after']
        self.assertEqual([row['request'] for row in result['trace']],requests)
        self.assertEqual([row['result'] for row in result['trace']],outcomes)
        native=m.decision.run_sequence(state,requests)
        for key in ['after','decision_cursor','recorded_statements','fiscal_complete']:
            self.assertEqual(result[key],native[key])
        self.assertEqual(result['after']['after']['balances']['cash'],'949/2')
        self.assertEqual(result['after']['after']['lots']['recovered']['carrying'],'5/1')
        self.assertEqual([x['result']['status'] for x in result['trace']],['applied_provisional','applied_provisional','no_action'])

    def test_explicit_and_recurring_calendars_have_identical_execution(self):
        state=e.start();a=self.run_case(state,e.root(state));b=self.run_case(state,e.root(state,'explicit_dates'))
        for key in ['calendar','trace','after','decision_cursor','recorded_statements']:self.assertEqual(a[key],b[key])
        self.assertNotEqual(a['schedule_sha256'],b['schedule_sha256'])

    def test_reordered_schedule_inputs_do_not_change_priority_order(self):
        state=e.start();root=e.root(state)
        second=deepcopy(root['schedules'][0]);second.update(id='other',priority=20)
        second['calendar']={'kind':'explicit_dates','dates':['2027-01-02']}
        root['schedules'].append(second);a=self.run_case(state,root)
        root['schedules'].reverse();b=self.run_case(state,root)
        self.assertEqual(a['calendar'],b['calendar']);self.assertEqual(a['trace'],b['trace']);self.assertEqual(a['after'],b['after'])
        self.assertEqual([x['schedule_id'] for x in a['calendar'][:2]],['daily-sale','other'])

    def test_ambiguous_same_day_order_has_no_executed_prefix(self):
        state=e.start();root=e.root(state);other=deepcopy(root['schedules'][0]);other['id']='other';root['schedules'].append(other)
        with patch.object(m.decision,'apply',wraps=m.decision.apply) as applied:
            result=self.run_case(state,root,'unresolved');self.assertEqual(applied.call_count,0)
        self.assertEqual(result['reason'],'ambiguous_same_day_priority')

    def test_malformed_later_policy_checked_before_earlier_unknown_model(self):
        state=e.start();root=e.root(state);root['schedules'][0]['template']['model']['available_on']='unknown'
        other=deepcopy(root['schedules'][0]);other.update(id='later',priority=20)
        other['calendar']={'kind':'explicit_dates','dates':['2027-01-06']}
        other['template']['model']['program']['outputs']['proceeds']='missing';root['schedules'].append(other)
        with patch.object(m.decision,'apply',wraps=m.decision.apply) as applied:
            self.run_case(state,root,'invalid');self.assertEqual(applied.call_count,0)

    def test_future_model_and_future_selected_input_stop_explicitly(self):
        state=e.start()
        for target in ['model','price']:
            root=e.root(state)
            record=root['schedules'][0]['template']['model'] if target=='model' else root['schedules'][0]['template']['bindings']['price']
            record['available_on']='2027-01-03'
            result=self.run_case(state,root,'stopped_provisional')
            self.assertEqual(result['stop']['outcome']['status'],'unresolved')
            self.assertEqual(result['trace'],[]);self.assertEqual(result['after'],state)
            self.assertEqual(result['remaining_occurrences'],result['calendar'])

    def test_refusal_retains_successful_prefix_and_exact_pending_request(self):
        state=e.start();root=e.root(state)
        root['schedules'][0]['calendar']={'kind':'explicit_dates','dates':['2027-01-02']}
        second=deepcopy(root['schedules'][0]);second['id']='unknown-finding'
        second['calendar']['dates']=['2027-01-03','2027-01-04']
        second['template']['event']['findings']['homogeneous_units']={'status':'unknown','reason':'Not supplied'}
        root['schedules'].append(second);result=self.run_case(state,root,'stopped_provisional')
        self.assertEqual(len(result['trace']),1);self.assertEqual(result['stop']['index'],1)
        self.assertEqual(result['stop']['request']['expected_state_sha256'],m.digest(result['after']))
        self.assertEqual(result['stop']['outcome']['decision']['status'],'proposed')
        self.assertEqual(result['remaining_occurrences'],result['calendar'][1:])

    def test_disabled_rule_ignores_future_unused_price_and_advances_cursor(self):
        state=e.start();root=e.root(state,enabled=False)
        root['schedules'][0]['template']['bindings']['price']['available_on']='unknown'
        result=self.run_case(state,root)
        self.assertEqual(result['after'],state);self.assertEqual(result['decision_cursor'],'2027-01-04')
        self.assertEqual(result['after']['after']['date'],'2027-01-01')

    def test_stale_root_context_and_extra_fields_refuse(self):
        state=e.start()
        for kind in ['hash','context','extra']:
            root=e.root(state)
            if kind=='hash':root['expected_state_sha256']='0'*64
            elif kind=='context':root['context']['currency']='EUR'
            else:root['extra']=True
            self.run_case(state,root,'invalid')

    def test_duplicate_ids_invalid_priorities_and_template_event_fields(self):
        state=e.start();root=e.root(state);root['schedules'].append(deepcopy(root['schedules'][0]));self.run_case(state,root,'invalid')
        for value in [True,-1,'1']:
            root=e.root(state);root['schedules'][0]['priority']=value;self.run_case(state,root,'invalid')
        root=e.root(state);root['schedules'][0]['template']['event']['id']='caller-event';self.run_case(state,root,'invalid')

    def test_calendar_leap_day_and_exclusive_end(self):
        financial={'date':'2028-01-01','period':{'end_exclusive':'2029-01-01'}}
        calendar={'kind':'every_days','start':'2028-02-28','end_exclusive':'2028-03-02','step_days':1}
        self.assertEqual(m.dates(calendar,financial),['2028-02-28','2028-02-29','2028-03-01'])
        calendar['step_days']=2;self.assertEqual(m.dates(calendar,financial),['2028-02-28','2028-03-01'])
        calendar['step_days']=10**20;self.assertEqual(m.dates(calendar,financial),['2028-02-28'])

    def test_calendar_errors_and_unsupported_conventions(self):
        state=e.start()
        calendars=[{'kind':'explicit_dates','dates':[]},{'kind':'explicit_dates','dates':['2027-01-03','2027-01-02']},{'kind':'explicit_dates','dates':['2027-01-02']*2},{'kind':'explicit_dates','dates':['2027-02-29']},{'kind':'explicit_dates','dates':['2028-01-01']},{'kind':'explicit_dates','dates':['2026-12-31']}]
        calendars += [{'kind':'every_days','start':'2027-01-02','end_exclusive':'2027-01-05','step_days':value} for value in [0,-1,True,'1']]
        for calendar in calendars:
            root=e.root(state);root['schedules'][0]['calendar']=calendar;self.run_case(state,root,'invalid')
        root=e.root(state);root['schedules'][0]['calendar']={'kind':'monthly'};self.run_case(state,root,'unsupported')

    def test_calendar_and_sequence_limits(self):
        state=e.start();root=e.root(state,enabled=False)
        root['schedules'][0]['calendar']={'kind':'every_days','start':'2027-01-02','end_exclusive':'2027-03-07','step_days':1}
        result=self.run_case(state,root);self.assertEqual(len(result['trace']),64)
        root['schedules'][0]['calendar']['end_exclusive']='2027-03-08';self.run_case(state,root,'invalid')
        root=e.root(state,enabled=False);template=root['schedules'][0]
        root['schedules']=[deepcopy(template) for _ in range(33)]
        for i,row in enumerate(root['schedules']):row.update(id=str(i),priority=i);row['calendar']={'kind':'explicit_dates','dates':['2027-01-02']}
        self.run_case(state,root,'invalid')
        root['schedules'].pop();self.assertEqual(len(self.run_case(state,root)['trace']),32)

    def test_empty_schedule_is_complete_only_for_its_empty_population(self):
        state=e.start();root=e.root(state);root['schedules']=[];result=self.run_case(state,root)
        self.assertEqual(result['trace'],[]);self.assertEqual(result['after'],state);self.assertFalse(result['fiscal_complete'])

    def test_dependency_and_malformed_inputs_fail_closed(self):
        state=e.start()
        with patch.object(m,'DEPENDENCY_SHA256','0'*64):self.run_case(state,e.root(state),'invalid')
        for root in [None,[],{}, {'profile':m.PROFILE}]:self.run_case(state,root,'invalid')

    def test_full_stock_depletion_and_no_action_read_the_new_book(self):
        state=e.start();root=e.root(state)
        root['schedules'][0]['template']['bindings']['reserve']['value']='0/1'
        result=self.run_case(state,root)
        self.assertEqual([x['result']['status'] for x in result['trace']],['applied_provisional','applied_provisional','no_action'])
        self.assertTrue(result['after']['after']['lots']['recovered']['disposed'])
        self.assertEqual(result['after']['after']['balances']['cash'],'482/1')
        self.assertEqual(result['after']['after']['lots']['recovered']['carrying'],'0/1')

    def test_invalid_intervals_and_total_occurrence_limit(self):
        state=e.start()
        for start,end in [('2027-01-02','2027-01-02'),('2027-01-03','2027-01-02'),('2027-12-31','2028-01-02')]:
            root=e.root(state);root['schedules'][0]['calendar'].update(start=start,end_exclusive=end)
            self.run_case(state,root,'invalid')
        root=e.root(state,enabled=False)
        template=root['schedules'][0]
        root['schedules']=[deepcopy(template) for _ in range(22)]
        for i,row in enumerate(root['schedules']):row.update(id=str(i),priority=i)
        self.run_case(state,root,'invalid')

    def test_request_byte_limit_is_checked_before_execution(self):
        state=e.start();root=e.root(state);root['scenario']['premise']='x'*2000001
        with patch.object(m.decision,'apply',wraps=m.decision.apply) as applied:
            self.run_case(state,root,'invalid');self.assertEqual(applied.call_count,0)


if __name__=='__main__':unittest.main()
