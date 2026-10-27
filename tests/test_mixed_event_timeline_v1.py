from copy import deepcopy
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch
import importlib.util
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import mixed_event_timeline_v1 as m
spec=importlib.util.spec_from_file_location('mixed_examples',ROOT/'data/accounting-master/mixed-event-timeline-20261025/examples.py')
e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)


class MixedTimelineTests(unittest.TestCase):
    def outcome(self,state,root,status='complete_mixed_timeline'):
        before=deepcopy((state,root));result=m.run(state,root)
        self.assertEqual(result['status'],status,result);self.assertEqual((state,root),before)
        self.assertTrue(all(result[key] is False for key in m.FLAGS))
        return result

    def manual_request(self,state,root):
        token=m.digest([root['id'],root['schedules'][0]['id'],0])
        template=deepcopy(root['schedules'][0]['template'])
        template['event'].update(id='scheduled-event:'+token,date='2027-01-02')
        return {'profile':m.decision.PROFILE,'id':'scheduled-decision:'+token,'expected_state_sha256':m.digest(state),
                'context':deepcopy(root['context']),'decision_date':'2027-01-02','scenario':deepcopy(root['scenario']),**template}

    def test_manual_interleaved_native_and_decision_transitions_match_completely(self):
        state=e.start()
        for payment_first in [True,False]:
            root=e.root(state,payment_first);result=self.outcome(state,root);current=deepcopy(state)
            order=['native','decision'] if payment_first else ['decision','native']
            for index,kind in enumerate(order):
                if kind=='native':
                    step=m.runtime.transition(current,root['operations'][0]['operation'])
                    self.assertEqual(result['trace'][index]['result']['transition'],step);current=step['after']
                else:
                    request=self.manual_request(current,root)
                    step=m.decision.apply(current,request,m.decision.propose(current,request))
                    self.assertEqual(result['trace'][index]['request'],request)
                    self.assertEqual(result['trace'][index]['result'],step);current=step['after']
            self.assertEqual(result['after'],current)
            report=m.runtime.annual.root.carry.statements(current['opening'],current['after'],current['account_classes'])
            for key,value in report.items():
                if key not in ['scope','unresolved']:self.assertEqual(result['recorded_statements'][key],value)
            self.assertEqual(result['recorded_statements']['unresolved'],m.runtime.annual.UNRESOLVED)

    def test_independent_order_effect_and_tax_vintage_conservation(self):
        state=e.start();first=self.outcome(state,e.root(state,True));last=self.outcome(state,e.root(state,False))
        for result,cash,inventory,carrying,profit in [(first,'463/1','70/1','10/1',5),(last,'448/1','80/1','20/1',0)]:
            financial=result['after']['after'];self.assertEqual(financial['balances']['cash'],cash)
            self.assertEqual(financial['balances']['inventory'],inventory)
            self.assertEqual(financial['lots']['recovered']['carrying'],carrying)
            self.assertEqual(financial['balances']['income_tax_payable'],'-25/4')
            self.assertEqual([v['closing_payable'] for v in result['after']['period_vintages']],['5/4','5/1'])
            self.assertEqual(sum(Fraction(v['closing_payable']) for v in result['after']['period_vintages']),Fraction(25,4))
            self.assertEqual(sum(-Fraction(x['result'].get('transition',{}).get('journal',{}).get('revenue','0/1'))-Fraction(x['result'].get('transition',{}).get('journal',{}).get('cogs','0/1')) for x in result['trace']),profit)
            self.assertEqual(result['after']['historical_vintages'],state['historical_vintages'])
            self.assertFalse(result['fiscal_complete'])

    def test_unknown_and_false_native_authorization_preserve_outcome(self):
        state=e.start()
        for authorization,status in [({'status':'unknown','reason':'Not supplied'},'unresolved'),(e.scheduled.decision_examples.native.previous.known(False),'unsupported')]:
            root=e.root(state);root['operations'][0]['operation']['event']['authorization']=authorization
            result=self.outcome(state,root,'stopped_provisional')
            self.assertEqual(result['stop']['outcome']['status'],status)
            self.assertEqual(result['trace'],[]);self.assertEqual(result['after'],state)
            self.assertEqual(result['remaining_actions'],result['calendar'])
            self.assertEqual(result['stop']['entry']['operation']['event']['authorization'],authorization)

    def test_successful_native_prefix_retained_when_decision_unresolved(self):
        state=e.start();root=e.root(state)
        root['schedules'][0]['template']['bindings']['price']['available_on']='unknown'
        result=self.outcome(state,root,'stopped_provisional')
        self.assertEqual(result['stop']['index'],1);self.assertEqual(len(result['trace']),1)
        self.assertEqual(result['after']['after']['balances']['cash'],'448/1')
        self.assertEqual(result['stop']['outcome']['status'],'unresolved')
        self.assertEqual(result['stop']['request']['expected_state_sha256'],m.digest(result['after']))

    def test_bad_later_operation_shape_is_checked_before_execution(self):
        state=e.start();root=e.root(state,False);root['operations'][0]['operation']['event']['extra']=True
        with patch.object(m.runtime,'transition',wraps=m.runtime.transition) as transition:
            self.outcome(state,root,'invalid');self.assertEqual(transition.call_count,0)

    def test_native_semantic_refusal_uses_the_actual_prefix(self):
        state=e.start();root=e.root(state,False)
        root['operations'][0]['operation']['event']['allocations'][0]['vintage_id']='missing'
        result=self.outcome(state,root,'stopped_provisional')
        self.assertEqual(len(result['trace']),1);self.assertEqual(result['trace'][0]['result']['status'],'no_action')
        self.assertEqual(result['stop']['outcome']['reason'],'unknown_vintage')
        self.assertEqual(result['after'],state)

    def test_date_mismatch_and_out_of_period_rejected(self):
        state=e.start()
        for date in ['2027-01-03','20270102','2026-12-31','2028-01-01']:
            root=e.root(state);root['operations'][0]['date']=date
            if date in ['2026-12-31','2028-01-01']:root['operations'][0]['operation']['event']['date']=date
            self.outcome(state,root,'invalid')

    def test_cross_population_same_day_tie_and_event_collision(self):
        state=e.start();root=e.root(state);root['operations'][0]['priority']=10
        self.outcome(state,root,'unresolved')
        root=e.root(state);token=m.digest([root['id'],root['schedules'][0]['id'],0])
        root['operations'][0]['operation']['event']['id']='scheduled-event:'+token
        self.outcome(state,root,'invalid')

    def test_duplicate_native_entries_events_and_invalid_priorities(self):
        state=e.start()
        for change in ['entry','event']:
            root=e.root(state);other=deepcopy(root['operations'][0])
            if change=='event':other['id']='other';other['priority']=6
            root['operations'].append(other);self.outcome(state,root,'invalid')
        for value in [True,-1,'5']:
            root=e.root(state);root['operations'][0]['priority']=value;self.outcome(state,root,'invalid')

    def test_native_partial_sale_adapter_matches_unchanged_transition(self):
        state=e.start();root=e.root(state);root['schedules']=[]
        operation=e.scheduled.decision_examples.native.sale('direct-sale','1/2','15/2')
        root['operations'][0]['operation']=operation
        result=self.outcome(state,root);native=m.runtime.transition(state,operation)
        self.assertEqual(result['trace'][0]['result']['transition'],native);self.assertEqual(result['after'],native['after'])

    def test_partial_sale_unknown_and_oversale_remain_native_refusals(self):
        state=e.start()
        for kind,status in [('unknown','unresolved'),('oversale','invalid')]:
            root=e.root(state);root['schedules']=[]
            operation=e.scheduled.decision_examples.native.sale('direct-sale')
            if kind=='unknown':operation['event']['findings']['homogeneous_units']={'status':'unknown','reason':'Missing'}
            else:operation['event']['sold_units']='3/1'
            root['operations'][0]['operation']=operation
            result=self.outcome(state,root,'stopped_provisional');self.assertEqual(result['stop']['outcome']['status'],status)

    def test_unsupported_clock_shapes_are_not_guessed(self):
        state=e.start()
        for kind in ['current_assessment','deferred_assessment','provisional_carry','native']:
            root=e.root(state);root['operations'][0]['operation']={'kind':kind,'event':{}}
            result=self.outcome(state,root,'unsupported');self.assertEqual(result['reason'],'native_operation_adapter')

    def test_empty_and_decision_only_timelines_match_existing_scope(self):
        state=e.start();root=e.root(state);root['operations']=[]
        result=self.outcome(state,root);schedule={k:v for k,v in root.items() if k!='operations'};schedule['profile']=m.scheduler.PROFILE
        baseline=m.scheduler.run(state,schedule)
        self.assertEqual(result['after'],baseline['after'])
        self.assertEqual([x['result'] for x in result['trace']],[x['result'] for x in baseline['trace']])
        root['schedules']=[];empty=self.outcome(state,root);self.assertEqual(empty['after'],state);self.assertEqual(empty['trace'],[])

    def test_reordering_supplied_arrays_does_not_change_execution(self):
        state=e.start();root=e.root(state);other=deepcopy(root['operations'][0])
        other.update(id='second-payment',date='2027-01-03',priority=5)
        other['operation']['event'].update(id='second-payment',date='2027-01-03',amount='1/1')
        other['operation']['event']['allocations'][0]['amount']='1/1';root['operations'].append(other)
        a=self.outcome(state,root);root['operations'].reverse();b=self.outcome(state,root)
        self.assertEqual(a['calendar'],b['calendar']);self.assertEqual(a['trace'],b['trace']);self.assertEqual(a['after'],b['after'])

    def test_limits_and_protected_source(self):
        state=e.start();root=e.root(state)
        with patch.object(m,'MAX_ACTIONS',1):self.outcome(state,root,'invalid')
        with patch.object(m,'MAX_OPERATIONS',0):self.outcome(state,root,'invalid')
        with patch.object(m,'SCHEDULER_SHA256','0'*64):self.outcome(state,root,'invalid')
        for invalid in [None,[],{},dict(root,extra=True)]:self.outcome(state,invalid,'invalid')

    def test_actual_32_native_and_64_total_action_boundaries(self):
        state=e.start();root=e.root(state);template=root['operations'][0]
        root['operations']=[deepcopy(template) for _ in range(32)]
        for index,row in enumerate(root['operations']):
            row.update(id='payment-'+str(index),priority=index)
            row['operation']['event'].update(id='payment-'+str(index),amount='1/32')
            row['operation']['event']['allocations'][0]['amount']='1/32'
        schedule=root['schedules'][0];schedule['priority']=100
        schedule['calendar']={'kind':'every_days','start':'2027-01-02','end_exclusive':'2027-02-03','step_days':1}
        result=self.outcome(state,root);self.assertEqual(len(result['trace']),64)
        self.assertEqual(result['after']['after']['balances']['cash'],'451/1')
        self.assertEqual(result['after']['after']['balances']['income_tax_payable'],'-37/4')
        schedule['calendar']['end_exclusive']='2027-02-04';self.outcome(state,root,'invalid')
        schedule['calendar']['end_exclusive']='2027-02-03';root['operations'].append(deepcopy(root['operations'][0]));self.outcome(state,root,'invalid')

    def test_no_action_cursor_precedes_later_native_event(self):
        state=e.start();root=e.root(state,False)
        root['schedules'][0]['calendar']['dates']=['2027-01-03']
        root['operations'][0]['date']='2027-01-04';root['operations'][0]['operation']['event']['date']='2027-01-04'
        result=self.outcome(state,root)
        self.assertEqual(result['trace'][0]['result']['status'],'no_action')
        self.assertEqual(result['timeline_cursor'],'2027-01-04')
        self.assertEqual(result['after']['after']['date'],'2027-01-04')


if __name__=='__main__':unittest.main()
