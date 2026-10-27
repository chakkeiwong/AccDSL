from copy import deepcopy
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch
import importlib.util
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import state_decision_events_v1 as m
spec = importlib.util.spec_from_file_location('decision_examples', ROOT/'data/accounting-master/state-decision-events-20261025/examples.py')
e = importlib.util.module_from_spec(spec); spec.loader.exec_module(e)


class StateDecisionTests(unittest.TestCase):
    def proposal(self, state, request, status='proposed'):
        old_state, old_request = deepcopy(state), deepcopy(request)
        result = m.propose(state, request)
        self.assertEqual(result['status'], status, result)
        self.assertEqual(state, old_state); self.assertEqual(request, old_request)
        self.assertTrue(all(result[key] is False for key in m.FLAGS))
        return result

    def applied(self, state, request, status='applied_provisional'):
        proposal = self.proposal(state, request)
        before = deepcopy((state, request, proposal))
        result = m.apply(state, request, proposal)
        self.assertEqual(result['status'], status, result)
        self.assertEqual((state, request, proposal), before)
        return result

    def test_exact_manual_operation_and_complete_transition(self):
        state = e.start(); request = e.request(state)
        proposal = self.proposal(state, request)
        operation = e.native.sale('decision-1-sale', '3/2', '45/2')
        self.assertEqual(proposal['operation'], operation)
        result = self.applied(state, request)
        native = m.runtime.transition(state, operation)
        self.assertEqual(result['transition'], native)
        self.assertEqual(result['after'], native['after'])

    def test_independent_single_sale_arithmetic(self):
        state = e.start(); result = self.applied(state, e.request(state))
        after = result['after']['after']; lot = after['lots']['recovered']
        self.assertEqual(lot['units'], '1/2')
        self.assertEqual(lot['carrying'], '5/1')
        self.assertEqual(lot['tax_base'], '5/1')
        self.assertEqual(Fraction(after['balances']['cash']), Fraction(452)+Fraction(3,2)*15)
        self.assertEqual(Fraction(state['after']['lots']['recovered']['carrying'])-Fraction(lot['carrying']), 15)

    def test_repeated_decisions_match_manual_sequence_and_full_statements(self):
        state = e.start(); requests = e.repeated(); original = deepcopy((state, requests))
        result = m.run_sequence(state, requests)
        self.assertEqual(result['status'], 'complete_decision_sequence', result)
        manual = deepcopy(state)
        for operation in [e.native.sale('decision-1-sale'), e.native.sale('decision-2-sale','1/2','15/2','2027-01-03')]:
            manual = m.runtime.transition(manual, operation)['after']
        self.assertEqual(result['after'], manual)
        report = m.runtime.annual.root.carry.statements(manual['opening'],manual['after'],manual['account_classes'])
        for name, value in report.items():
            if name not in ['scope','unresolved']: self.assertEqual(result['recorded_statements'][name], value)
        self.assertIn('not a complete fiscal event population', result['recorded_statements']['scope'])
        self.assertEqual(result['recorded_statements']['unresolved'], m.runtime.annual.UNRESOLVED)
        self.assertEqual([row['result']['status'] for row in result['trace']], ['applied_provisional','applied_provisional','no_action'])
        self.assertEqual(manual['after']['lots']['recovered']['units'], '1/2')
        self.assertEqual(manual['after']['lots']['recovered']['carrying'], '5/1')
        self.assertEqual(manual['after']['balances']['cash'], '949/2')
        self.assertEqual(result['decision_cursor'], '2027-01-04')
        self.assertFalse(result['fiscal_complete']); self.assertEqual(result['remaining_requests'], [])
        self.assertEqual((state, requests), original)

    def test_false_guard_does_not_require_unused_unknown_inputs(self):
        state = e.start()
        for name in ['demand','price']:
            for availability in ['unknown','2027-01-03']:
                request = e.request(state, enabled=False)
                request['bindings'][name]['available_on'] = availability
                proposal = self.proposal(state, request, 'no_action')
                self.assertEqual(proposal['input_observations'][name]['value_used'], 'unknown')
                self.assertEqual(proposal['input_observations'][name]['binding'], request['bindings'][name])
                self.assertEqual(m.apply(state, request, proposal)['after'], state)

    def test_unknown_guard_and_selected_values_remain_unresolved(self):
        state = e.start()
        for name in ['enabled','demand','price']:
            request = e.request(state); request['bindings'][name]['value'] = 'unknown'
            self.proposal(state, request, 'unresolved')

    def test_unavailable_model_is_unresolved_even_for_false_guard(self):
        state = e.start()
        for availability in ['unknown','2027-01-03']:
            request = e.request(state, enabled=False); request['model']['available_on'] = availability
            result = self.proposal(state, request, 'unresolved')
            self.assertEqual(result['reason'], 'model_not_available')

    def test_reserve_above_stock_and_zero_demand_do_nothing(self):
        state = e.start()
        for kwargs in [{'reserve':'3/1'}, {'demand':'0/1'}, {'reserve':'2/1'}]:
            request = e.request(state, **kwargs); proposal = self.proposal(state, request, 'no_action')
            self.assertEqual(m.apply(state,request,proposal)['after'], state)

    def test_static_invalidity_not_hidden_by_false_guard_or_unavailable_model(self):
        state = e.start()
        for unavailable in [False, True]:
            request = e.request(state, enabled=False)
            if unavailable: request['model']['available_on'] = 'unknown'
            request['model']['program']['nodes'].append({'id':'bad','op':'div','args':['missing','missing']})
            self.proposal(state, request, 'invalid')

    def test_invalid_dates_and_event_chronology(self):
        state = e.start()
        for value in ['20270102','2027-02-30','',None,True]:
            for location in ['model','binding','decision']:
                request = e.request(state)
                if location == 'model': request['model']['available_on'] = value
                elif location == 'binding': request['bindings']['price']['available_on'] = value
                else: request['decision_date'] = value
                self.proposal(state, request, 'invalid')
        for value in ['2026-12-31','2028-01-01']:
            request = e.request(state, date=value); self.proposal(state,request,'invalid')
        request = e.request(state); request['event']['date']='2027-01-03'
        self.proposal(state,request,'unsupported')

    def test_units_currency_entity_and_context_mismatches(self):
        state = e.start()
        for mutation in ['quantity','currency','entity','binding_context']:
            request = e.request(state)
            if mutation == 'quantity': request['bindings']['demand']['type']['dimensions']={'USD':1}
            elif mutation == 'currency': request['bindings']['price']['type']['dimensions']={'EUR':1,'unit':-1}
            elif mutation == 'entity': request['context']['entity']='Other'
            else: request['bindings']['price']['type']['context']='Other'
            self.proposal(state,request,'invalid')

    def test_closed_input_and_output_populations(self):
        state = e.start()
        for mutation in ['missing_binding','extra_binding','missing_output','extra_output','duplicate_map','bad_map']:
            request = e.request(state)
            if mutation == 'missing_binding': del request['bindings']['price']
            elif mutation == 'extra_binding': request['bindings']['extra']=deepcopy(request['bindings']['price'])
            elif mutation == 'missing_output': del request['model']['program']['outputs']['proceeds']
            elif mutation == 'extra_output': request['model']['program']['outputs']['extra']='proceeds'
            elif mutation == 'duplicate_map': request['output_map']['sold_units']='proceeds'
            else: request['output_map']['proceeds']='absent'
            self.proposal(state,request,'invalid')

    def test_placeholders_and_canonical_values_required(self):
        state = e.start(); request = e.request(state)
        request['model']['program']['inputs']['price']['value']='15/1'
        self.proposal(state,request,'invalid')
        for value in [15,True,'2/2','1/0',0.5]:
            request=e.request(state);request['bindings']['price']['value']=value
            self.proposal(state,request,'invalid')

    def test_state_cash_projection_and_selected_lot_binding(self):
        state=e.start();request=e.request(state)
        request['model']['program']['inputs']['cash']={'type':m.types(state)['cash'],'value':'unknown'}
        request['model']['program']['nodes'].append({'id':'cash_value','op':'input','target':'cash'})
        request['model']['program']['outputs']['proceeds']='cash_value'
        request['bindings']['cash']={'kind':'state_cash'}
        self.assertEqual(self.proposal(state,request)['operation']['event']['proceeds'],'452/1')
        request['bindings']['stock']['lot_id']='absent';self.proposal(state,request,'invalid')

    def test_stale_state_request_and_rehashed_tampering(self):
        state=e.start();request=e.request(state);proposal=self.proposal(state,request)
        new_state=self.applied(state,request)['after']
        self.proposal(new_state,request,'invalid')
        changed=deepcopy(request);changed['bindings']['price']['value']='16/1'
        self.assertEqual(m.apply(state,changed,proposal)['status'],'invalid')
        for field in ['operation','observation','hash']:
            changed=deepcopy(proposal)
            if field=='operation':
                changed['operation']['event']['proceeds']='999/1'
                changed['operation_sha256']=m.digest(changed['operation'])
            elif field=='observation': changed['input_observations']['price']['value_used']='16/1'
            else: changed['state_sha256']='0'*64
            self.assertEqual(m.apply(state,request,changed)['status'],'invalid')

    def test_native_findings_unknown_false_and_malformed(self):
        state=e.start()
        for value,status in [({'status':'unknown','reason':'Not supplied'},'unresolved'),(m.runtime.partial.known(False),'unsupported')]:
            request=e.request(state);request['event']['findings']['homogeneous_units']=value
            result=self.applied(state,request,status)
            self.assertEqual(result['decision']['status'],'proposed')
            self.assertEqual(result['decision']['operation']['event']['findings']['homogeneous_units'],value)
        request=e.request(state);request['event']['findings']['homogeneous_units']['provenance']=''
        self.proposal(state,request,'invalid')

    def test_native_oversale_negative_proceeds_and_duplicate_event(self):
        state=e.start();request=e.request(state)
        request['bindings']['reserve']['value']='-1/1';request['bindings']['demand']['value']='3/1'
        self.applied(state,request,'invalid')
        request=e.request(state);request['bindings']['price']['value']='-1/1'
        self.applied(state,request,'invalid')
        state=self.applied(state,e.request(state))['after']
        request=e.request(state,reserve='0/1')
        self.applied(state,request,'invalid')

    def test_example_domain_is_explicit_not_a_generic_restriction(self):
        state=e.start()
        for name in ['demand','reserve','price']:
            with self.assertRaisesRegex(ValueError,'negative_example_assumption'):
                e.request(state,**{name:'-1/1'})
        request=e.request(state);request['bindings']['demand']['value']='-1/1'
        self.proposal(state,request,'no_action')

    def test_successful_prefix_and_remaining_requests_retained(self):
        state=e.start();requests=e.repeated()
        requests[1]['event']['findings']['homogeneous_units']={'status':'unknown','reason':'Missing finding'}
        result=m.run_sequence(state,requests)
        self.assertEqual(result['status'],'stopped_provisional')
        self.assertEqual(result['stop']['index'],1)
        self.assertEqual(result['stop']['outcome']['status'],'unresolved')
        self.assertEqual(len(result['trace']),1)
        self.assertEqual(result['remaining_requests'],requests[1:])
        self.assertEqual(result['after'],self.applied(state,requests[0])['after'])

    def test_no_action_cursor_rejects_later_backward_date(self):
        state=e.start();first=e.request(state,date='2027-01-04',enabled=False)
        second=e.request(state,'second',date='2027-01-03')
        result=m.run_sequence(state,[first,second])
        self.assertEqual(result['stop']['outcome']['reason'],'backward_decision_date')
        self.assertEqual(result['decision_cursor'],'2027-01-04')
        self.assertEqual(result['after'],state)

    def test_duplicate_decisions_and_empty_sequence(self):
        state=e.start();request=e.request(state,enabled=False)
        result=m.run_sequence(state,[request,deepcopy(request)])
        self.assertEqual(result['stop']['outcome']['reason'],'duplicate_decision')
        result=m.run_sequence(state,[])
        self.assertEqual(result['status'],'complete_decision_sequence')
        self.assertEqual(result['after'],state);self.assertFalse(result['fiscal_complete'])

    def test_sequence_limit_and_input_limit(self):
        state=e.start()
        requests=[e.request(state,'d'+str(i),enabled=False) for i in range(64)]
        self.assertEqual(m.run_sequence(state,requests)['status'],'complete_decision_sequence')
        self.assertEqual(m.run_sequence(state,requests+[requests[0]])['reason'],'decision_sequence_limit')
        request=e.request(state,enabled=False)
        for i in range(27):
            key='extra'+str(i)
            request['model']['program']['inputs'][key]={'type':m.types(state)['boolean'],'value':'unknown'}
            request['bindings'][key]={'kind':'scenario','type':m.types(state)['boolean'],'value':True,'available_on':'2027-01-01','provenance':'Boundary test'}
        self.proposal(state,request,'no_action')
        request['model']['program']['inputs']['extra27']=deepcopy(request['model']['program']['inputs']['extra0'])
        request['bindings']['extra27']=deepcopy(request['bindings']['extra0'])
        self.proposal(state,request,'invalid')

    def test_protected_dependency_failure(self):
        state=e.start();request=e.request(state)
        with patch.dict(m.PINS,{'annual_inventory_program_v1.py':'0'*64}):
            result=self.proposal(state,request,'invalid')
            self.assertIn('dependency_hash',result['reason'])

    def test_empty_and_unexpected_exceptions_have_explicit_invalid_result(self):
        for exc in [ValueError(),m.Refused('unexpected','Unsupported status')]:
            result=m.failure(exc)
            self.assertEqual(result['status'],'invalid');self.assertTrue(result['reason'])

    def test_complete_disposal_prevents_further_sale(self):
        state=e.start();request=e.request(state,demand='2/1',reserve='0/1')
        after=self.applied(state,request)['after']
        self.assertTrue(after['after']['lots']['recovered']['disposed'])
        request=e.request(after,'second',date='2027-01-03',reserve='0/1')
        self.proposal(after,request,'no_action')

    def test_native_assessed_interval_still_refuses(self):
        state=e.start()
        assessment=e.native.previous.assessment(state,'8/1','midyear')
        state=m.runtime.transition(state,assessment)['after']
        request=e.request(state,date=state['after']['date'])
        result=self.applied(state,request,'invalid')
        self.assertEqual(result['reason'],'event_inside_assessed_interval')

    def test_selected_invalid_arithmetic_and_unused_arithmetic(self):
        state=e.start()
        for enabled,status in [(True,'invalid'),(False,'no_action')]:
            request=e.request(state,enabled=enabled);program=request['model']['program']
            program['nodes'] += [e.expressions.literal('zero_scalar','0/1'),e.expressions.node('bad_proceeds','div','proceeds','zero_scalar')]
            program['outputs']['proceeds']='bad_proceeds'
            self.proposal(state,request,status)

    def test_malformed_inputs_return_invalid_without_exception(self):
        state=e.start()
        for request in [None,[],{},e.request(state)|{'extra':True}]: self.proposal(state,request,'invalid')
        for request in [None,{},[None]]:
            self.assertIn(m.run_sequence(state,request)['status'],['invalid','stopped_provisional'])
        request=e.request(state);request['id']='x'*4097;self.proposal(state,request,'invalid')
        request=e.request(state);request['model']['provenance']='x'*300000;self.proposal(state,request,'invalid')

    def test_sequence_same_day_is_ordered_and_has_no_durability_claim(self):
        state=e.start();first=e.request(state,demand='1/1')
        after=self.applied(state,first)['after']
        second=e.request(after,'second',demand='1/1')
        result=m.run_sequence(state,[first,second])
        self.assertEqual(result['status'],'complete_decision_sequence')
        self.assertEqual(len(result['trace']),2)
        self.assertTrue(all(result[key] is False for key in m.FLAGS))


if __name__ == '__main__': unittest.main()
