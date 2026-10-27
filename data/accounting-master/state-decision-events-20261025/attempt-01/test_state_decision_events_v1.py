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
        for name, value in report.items(): self.assertEqual(result['recorded_statements'][name], value)
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


if __name__ == '__main__': unittest.main()
