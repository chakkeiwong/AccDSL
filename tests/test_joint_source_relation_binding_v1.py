"""Retained source fidelity, independent arithmetic, and explicit assumptions."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import joint_source_relation_binding_v1 as adapter

BUDGET = {'max_slots': 0, 'max_formula_nodes': 10000, 'max_integer_assignments': 1,
          'max_cells': 1, 'elapsed_ms': 5000, 'solver_timeout_ms': 1000, 'solver_rlimit': 1000000}


class JointSourceBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = adapter.fixture(assume=True)
        cls.result = adapter.assess(cls.request, BUDGET)
        assert cls.result['status'] == 'conditionally_feasible', cls.result.get('reason')

    def test_preserves_complete_source_report_and_input(self):
        original = deepcopy(self.request)
        expected = adapter.statement.evaluate(self.request['statement_request'])
        self.assertEqual(self.result['preserved_report'], expected)
        self.assertEqual(len(expected['observations']), 256)
        self.assertEqual(len(expected['relations']), 143)
        self.assertEqual(len(self.result['definition']['observations']), 54)
        self.assertEqual(len(self.result['definition']['equations']), 18)
        self.assertEqual(self.request, original)
        self.assertEqual(expected['joint_latent_feasibility'], 'uncomputed')
        self.assertTrue(adapter.verify_result(self.request, BUDGET, self.result))

    def test_independent_witness_against_original_source_terms(self):
        values = {k: Q(v) for k, v in self.result['joint_assessment']['witness'].items()}
        source = self.result['preserved_report']['observations']
        for row in self.request['statement_request']['relations']:
            if row['id'] not in adapter.SUPPORTED: continue
            residual = Q(0)
            for side, sign in [('lhs', 1), ('rhs', -1)]:
                for term in row[side]:
                    item = source[term['alias']]
                    key = item['declaration']['observation_ref']['digest']
                    residual += sign * Q(term['coefficient']) * values[key]
                    amount = item['observation']['record']['body']['value']['amount']
                    displayed = Q(int(amount['n']), int(amount['d']))
                    # Independent signed half-open intervals, not the adapter helper.
                    low, high = displayed-Q(1, 2), displayed+Q(1, 2)
                    self.assertTrue(values[key] >= low if displayed > 0 else values[key] > low)
                    self.assertTrue(values[key] <= high if displayed < 0 else values[key] < high)
            self.assertEqual(residual, 0, row['id'])

    def test_shared_identity_context_and_unit_mapping(self):
        equations = self.result['definition']['equations']
        counts = {}
        for equation in equations:
            for term in equation['terms']:
                key = term['observation']; counts[key] = counts.get(key, 0)+1
                item = self.result['definition']['observations'][key]
                self.assertEqual(item['type'], equation['type'])
        self.assertTrue(any(n > 1 for n in counts.values()))
        for key, mapped in self.result['source_mapping'].items():
            typ = self.result['definition']['observations'][key]['type']
            original = mapped['original_context']
            self.assertEqual(typ['scale'], '1000000/1')
            self.assertEqual(typ['dimensions'], {'currency:USD': 1})
            self.assertEqual(original['unit'], 'USD million')
            self.assertEqual(typ['context']['instant'], mapped['measurement_time']['at'])
            self.assertEqual({k:v for k,v in typ['context'].items() if k != 'instant'},
                             {k:v for k,v in original.items() if k != 'unit'})
            self.assertEqual(key, mapped['observation_ref']['digest'])

    def test_display_only_is_unresolved(self):
        result = adapter.assess(adapter.fixture(), BUDGET)
        self.assertEqual(result['status'], 'unresolved')
        self.assertNotIn('solver_status', result['joint_assessment'])
        self.assertTrue(all(x['assessment']['status'] == 'unresolved' for x in result['local_assessments']))

    def test_each_missing_hypothesis_remains_unresolved(self):
        for missing in ['rounding', 'identity']:
            body = deepcopy(self.request)
            if missing == 'rounding': body['rounding_hypothesis'] = None
            else: body['identity_hypotheses'][adapter.SUPPORTED[0]] = None
            result = adapter.assess(body, BUDGET)
            self.assertEqual(result['status'], 'unresolved')
            self.assertNotIn('solver_status', result['joint_assessment'])

    def test_local_joint_comparison_uses_same_premises(self):
        for item in self.result['local_assessments']:
            self.assertEqual(item['identity_premise'], self.request['identity_hypotheses'][item['relation_id']])
            self.assertEqual(item['interval_premise'], self.request['rounding_hypothesis'])
            self.assertTrue(item['assessment']['zero_contained'])
        self.assertTrue(self.result['joint_assessment']['witness_checked_exactly'])

    def test_subsets_order_and_unselected_dispositions(self):
        for selected in [list(adapter.SUPPORTED[:9]), list(reversed(adapter.SUPPORTED[9:]))]:
            result = adapter.assess(adapter.fixture(selected, True), BUDGET)
            self.assertEqual(result['status'], 'conditionally_feasible')
            self.assertEqual([r['id'] for r in result['definition']['equations']], selected)
            self.assertEqual(len(result['definition']['observations']), 27)
            statuses = [x['status'] for x in result['relation_dispositions']]
            self.assertEqual(statuses.count('supported_unselected'), 9)
            self.assertEqual(statuses.count('outside_adapter_scope'), 125)

    def test_empty_selection_preserves_source_without_assertion(self):
        result = adapter.assess(adapter.fixture([]), BUDGET)
        self.assertEqual(result['status'], 'no_asserted_system')
        self.assertEqual(result['definition']['observations'], {})
        self.assertEqual(len(result['preserved_report']['relations']), 143)
        self.assertEqual(adapter.assess(adapter.fixture([]), {**BUDGET, 'max_slots': 1})['status'], 'invalid')

    def test_unsupported_and_duplicate_selections_rejected(self):
        for ids in [[adapter.SUPPORTED[0]]*2, ['annual.opening:assets'], ['annual.other_equity_movements']]:
            body = deepcopy(self.request); body['selected_relations'] = ids
            body['identity_hypotheses'] = {key: None for key in ids}
            self.assertEqual(adapter.assess(body, BUDGET)['status'], 'invalid')

    def test_source_coefficient_date_and_digest_tampering_rejected(self):
        def coefficient(body): body['statement_request']['relations'][0]['lhs'][0]['coefficient'] = '2/1'
        def time(body): body['statement_request']['observations'][0]['measurement_time'] = {'kind':'instant','at':'2000-01-01'}
        def digest(body): body['statement_request']['observations'][0]['observation_ref']['digest'] = '0'*64
        def source(body): body['statement_request']['source']['result_sha256'] = '0'*64
        for mutate in [coefficient, time, digest, source]:
            body = deepcopy(self.request); mutate(body)
            self.assertEqual(adapter.assess(body, BUDGET)['status'], 'invalid')

    def test_hypothesis_semantics_and_identity_tampering_rejected(self):
        for field, value in [('id','renamed'), ('status','admitted'), ('mode','half_even'),
                             ('quantum','2/1'), ('meaning','exact values'), ('unit','USD')]:
            body = deepcopy(self.request); body['rounding_hypothesis'][field] = value
            self.assertEqual(adapter.assess(body, BUDGET)['status'], 'invalid')
        for field in ['id', 'status', 'meaning']:
            body = deepcopy(self.request); body['identity_hypotheses'][adapter.SUPPORTED[0]][field] = 'changed'
            self.assertEqual(adapter.assess(body, BUDGET)['status'], 'invalid')

    def test_full_combined_input_and_closed_request_required(self):
        body = deepcopy(self.request); body['statement_request'] = adapter.statement.fixture(view='annual')
        self.assertEqual(adapter.assess(body, BUDGET)['status'], 'invalid')
        body = deepcopy(self.request); body['preserved_report'] = self.result['preserved_report']
        self.assertEqual(adapter.assess(body, BUDGET)['status'], 'invalid')
        body = deepcopy(self.request); body['identity_hypotheses']['extra'] = None
        self.assertEqual(adapter.assess(body, BUDGET)['status'], 'invalid')

    def test_resource_exhaustion_is_unknown(self):
        for field in ['max_cells', 'max_formula_nodes', 'elapsed_ms', 'solver_timeout_ms', 'solver_rlimit']:
            result = adapter.assess(self.request, {**BUDGET, field: 0})
            self.assertEqual(result['status'], 'unknown', (field, result.get('reason')))
            self.assertNotIn('witness', result['joint_assessment'])

    def test_replay_rejects_changed_source_definition_and_readiness(self):
        def source(r): r['preserved_report']['observations']['annual.balance.cash']['observation']['context']['issuer'] = 'Other'
        def term(r): r['definition']['equations'][0]['terms'][0]['coefficient'] = '2/1'
        def ready(r): r['executable_opening'] = {}
        def identity(r): r['definition']['equations'][0]['identity_premise']['id'] = 'renamed'
        def omit(r): r['preserved_report']['relations'].pop()
        def witness(r): r['joint_assessment']['witness'][next(iter(r['joint_assessment']['witness']))] = '0/1'
        for mutate in [source, term, ready, identity, omit, witness]:
            result = deepcopy(self.result); mutate(result)
            self.assertFalse(adapter.verify_result(self.request, BUDGET, result))

    def test_dashes_derived_subtotals_and_original_dispositions_preserved(self):
        report = self.result['preserved_report']
        self.assertEqual(sum(r['arithmetic']['status'] == 'unresolved' for r in report['relations']), 2)
        self.assertEqual(sum(r['kind'] == 'derived_subtotal' for r in report['relations']), 6)
        for row, disposition in zip(report['relations'], self.result['relation_dispositions']):
            self.assertEqual(row['id'], disposition['id'])
            self.assertEqual(adapter.core.digest(row), disposition['original_disposition_sha256'])

    def test_boundaries_remain_explicit(self):
        for result in [self.result, self.result['joint_assessment']]:
            for flag in ['executed', 'source_admission', 'accounting_admission']:
                self.assertIs(result[flag], False)
            self.assertIsNone(result['executable_opening'])
            self.assertEqual(result['actual_history'], 'unknown')

    def test_valid_alternative_witness_is_accepted(self):
        result = deepcopy(self.result)
        values = {}
        for key, item in result['source_mapping'].items():
            amount = result['preserved_report']['observations'][item['aliases'][0]]['observation']['record']['body']['value']['amount']
            value = Q(int(amount['n']), int(amount['d']))
            values[key] = f'{value.numerator}/{value.denominator}'
        adapter.joint.check_witness(result['definition'], values)
        result['joint_assessment']['witness'] = values
        result['joint_assessment']['solver_wall_seconds'] = 0.25
        self.assertTrue(adapter.verify_result(self.request, BUDGET, result))

    def test_conflicts_rechecked_by_meaning_not_label_order(self):
        from test_joint_measurement_constraints_v1 import definition, equation
        d = definition(equations=[equation('a', [('x','1/1')]), equation('b', [('x','1/1')], '1/1')])
        for labels in [['equation:a','equation:b'], ['equation:b','domain:x','equation:a']]:
            core = [{'labels':labels, 'rechecked':'unsat', 'minimal':False}]
            self.assertTrue(adapter._check_conflicts(d, BUDGET, core))
        for labels in [['equation:a'], ['unknown'], []]:
            with self.assertRaises(ValueError):
                adapter._check_conflicts(d, BUDGET, [{'labels':labels,'rechecked':'unsat','minimal':False}])


if __name__ == '__main__': unittest.main()
