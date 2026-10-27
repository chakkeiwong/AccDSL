from copy import deepcopy
from pathlib import Path
import importlib.util
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / 'scripts'))
import declared_operating_methods_v1 as operations
spec = importlib.util.spec_from_file_location('operating_examples', ROOT / 'data/accounting-master/declared-operating-cycle-20261025/examples.py')
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)


class DeclaredOperatingMethodsTests(unittest.TestCase):
    def stopped(self, body, index):
        original = deepcopy(body); result = ex.program.run(body)
        self.assertEqual(result['status'], 'stopped_provisional', result)
        self.assertEqual(result['stop']['index'], index); self.assertEqual(len(result['trace']), index)
        self.assertEqual(body, original)
        previous = result['trace'][-1]['after_sha256'] if index else ex.program.digest(body['opening'])
        self.assertEqual(ex.program.digest(result['current']), previous)
        return result

    def test_complete_native_and_independent_cycle_comparisons(self):
        result = ex.compare()
        self.assertEqual(len(result['checks']), 110)
        self.assertEqual([r['name'] for r in result['checks'] if not r['passed']], [])

    def test_no_native_callback_computes_the_declared_result(self):
        body, _, _, _ = ex.fixture()
        with patch.object(ex.native.Engine, 'apply', side_effect=AssertionError('native is comparator only')):
            result = ex.program.run(body)
            self.assertEqual(result['status'], 'complete_provisional')
            self.assertEqual(result['current']['balances']['cash'], '107/1')

    def test_credit_purchase_and_delivery_do_not_create_cash(self):
        body, _, _, _ = ex.fixture(); result = ex.program.run(body)
        for row in result['trace'][:2]:
            self.assertEqual(row['result']['transition']['flows'], [])
            self.assertEqual(row['result']['transition']['after']['balances']['cash'], '100/1')
        self.assertEqual(result['trace'][0]['result']['transition']['after']['balances']['payables'], '-30/1')
        self.assertEqual(result['trace'][1]['result']['transition']['after']['balances']['receivables'], '50/1')

    def test_unknown_and_false_applicability_for_each_method(self):
        for index in range(6):
            for binding, status in [({'status': 'unknown', 'reason': 'Missing economic fact'}, 'unresolved'),
                                    ({'status': 'known', 'value': False}, 'unsupported')]:
                body, _, _, _ = ex.fixture(); body['commands'][index]['event']['inputs']['approved']['value'] = binding
                result = self.stopped(body, index)
                self.assertEqual(result['stop']['status'], status)

    def test_inventory_collection_and_payable_overruns_are_refused(self):
        for index, key, value in [(1, 'units', '11/1'), (2, 'amount', '51/1'), (3, 'amount', '31/1'), (5, 'amount', '11/1')]:
            body, _, _, _ = ex.fixture();body['commands'][index]['event']['inputs'][key]['value']['value'] = value
            self.assertEqual(self.stopped(body, index)['stop']['status'], 'invalid')

    def test_negative_amounts_and_units_refuse_before_effects(self):
        for index in range(6):
            body, _, _, _ = ex.fixture(); inputs = body['commands'][index]['event']['inputs']
            key = 'units' if index < 2 else 'amount';inputs[key]['value']['value'] = '-1/1'
            self.assertEqual(self.stopped(body, index)['stop']['status'], 'invalid')

    def test_funding_failure_diagnostic_is_distinct_from_invalid_input(self):
        body, spec, events, _ = ex.fixture();body['opening']['balances'].update(cash='5/1', capital='-25/1')
        body['commands'] = [body['commands'][0], body['commands'][3]]
        result = self.stopped(body, 1); call = result['stop']['result']
        diagnostic = operations.refusal_diagnostic(call)
        self.assertEqual(diagnostic['category'], 'economic_funding_failure')
        self.assertEqual(diagnostic['primitive_status'], 'invalid')
        self.assertEqual(diagnostic['result_sha256'], ex.program.digest(call))
        spec['opening'].update(cash='5/1', capital='-25/1'); baseline = ex.native.Engine(spec)
        self.assertEqual(baseline.apply(events[0])['status'], 'Applied')
        failed = deepcopy(events[3]);failed['depends'] = [events[0]['id']]
        before = baseline.snapshot(); outcome = baseline.apply(failed)
        self.assertEqual(outcome['status'], 'EconomicFundingDefault');self.assertEqual(before, baseline.snapshot())
        self.assertEqual(result['current']['balances']['cash'], '5/1')

    def test_funding_diagnostic_cannot_hide_other_failed_conditions(self):
        body, _, _, _ = ex.fixture();body['opening']['balances'].update(cash='5/1', capital='-25/1')
        body['commands'] = [body['commands'][0], body['commands'][3]]
        body['commands'][1]['event']['inputs']['amount']['value']['value'] = '31/1'
        result = self.stopped(body, 1)
        self.assertEqual(operations.refusal_diagnostic(result['stop']['result'])['category'], 'invalid')

    def test_unit_cost_requires_positive_price_dimensions_and_context(self):
        for change in ['dimension', 'context', 'zero', 'negative', 'absent']:
            body, _, _, mapping = ex.fixture(); book = body['opening'];pointer = '/stock/unit_cost'
            if change == 'dimension':book['memory_types'][pointer]['dimensions'] = {'currency:USD': 1}
            elif change == 'context':book['memory_types'][pointer]['context']['entity'] = 'different'
            elif change == 'zero':book['memory']['stock']['unit_cost'] = '0/1'
            elif change == 'negative':book['memory']['stock']['unit_cost'] = '-5/1'
            else:pointer = '/unknown'
            with self.assertRaises(ValueError):operations.build(book, body['schemas'], {k: mapping[k] for k in operations.CLASSES}, pointer)

    def test_quantity_input_cannot_be_relabelled_as_money(self):
        body, _, _, _ = ex.fixture()
        body['commands'][0]['event']['inputs']['units']['type'] = ex.program.engine.money_type(body['opening'])
        self.assertEqual(ex.program.run(body)['status'], 'invalid')

    def test_registry_rechecks_current_unit_cost_after_construction(self):
        body, _, _, _ = ex.fixture();body['opening']['memory']['stock']['unit_cost'] = '0/1'
        self.assertEqual(self.stopped(body, 0)['stop']['status'], 'invalid')
        body, _, _, _ = ex.fixture();body['opening']['memory']['stock']['unit_cost'] = '6/1'
        result = ex.program.run(body);self.assertEqual(result['status'], 'complete_provisional')
        self.assertEqual(result['trace'][0]['result']['transition']['journal']['inventory'], '36/1')
        self.assertEqual(result['trace'][1]['result']['transition']['journal']['cost_of_sales'], '30/1')

    def test_zero_activity_matches_native_and_preserves_memory(self):
        body, spec, events, _ = ex.fixture();body['commands'] = [body['commands'][0]]
        body['commands'][0]['event']['inputs']['units']['value']['value'] = '0/1';events[0]['params']['units'] = '0/1'
        result = ex.program.run(body);base = ex.native.Engine(spec);outcome = base.apply(events[0])
        self.assertEqual(result['status'], 'complete_provisional');self.assertEqual(outcome['status'], 'Applied')
        self.assertEqual(result['current']['balances'], body['opening']['balances'])
        self.assertEqual(result['current']['memory'], body['opening']['memory'])
        self.assertEqual(result['current']['seen'], ['op.1'])

    def test_exact_role_map_and_classification_are_required(self):
        for change in ['missing', 'overlap', 'class', 'cash']:
            body, _, _, mapping = ex.fixture();roles = {k: mapping[k] for k in operations.CLASSES}
            if change == 'missing':del roles['payroll']
            elif change == 'overlap':roles['receivables'] = roles['cash']
            elif change == 'class':roles['payables'] = 'retained'
            else:roles['cash'], roles['receivables'] = roles['receivables'], roles['cash']
            with self.assertRaises(ValueError):operations.build(body['opening'], body['schemas'], roles, '/stock/unit_cost')

    def test_builder_input_immutability_and_deterministic_definitions(self):
        body, _, _, mapping = ex.fixture();roles = {k: mapping[k] for k in operations.CLASSES}
        original = deepcopy(body);first = operations.build(body['opening'], body['schemas'], roles, '/stock/unit_cost')
        second = operations.build(body['opening'], body['schemas'], roles, '/stock/unit_cost')
        self.assertEqual(first, second);self.assertEqual(body, original)
        self.assertEqual(set(first['entries']), set(operations.KINDS))

    def test_stale_method_and_changed_result_do_not_verify(self):
        body, _, _, _ = ex.fixture();result = ex.program.run(body)
        bad = deepcopy(result);bad['current']['balances']['cash'] = '108/1'
        self.assertFalse(ex.program.verify(body, bad))
        body['registry']['entries']['collect']['method']['monetary']['definition']['flows'][0]['activity'] = 'financing'
        self.assertEqual(ex.program.run(body)['status'], 'invalid')

    def test_nonzero_assets_debt_and_native_cohorts_remain_untouched(self):
        body, spec, events, mapping = ex.fixture()
        changes = {'plant_cost': '100/1', 'accum_depreciation': '-20/1', 'debt': '-30/1', 'retained': '-50/1'}
        body['opening']['balances'].update(changes);spec['opening'].update(changes)
        spec['assets'] = [{'id': 'untouched-plant', 'cost': '100/1', 'life_years': '10/1', 'in_service': '2025-01-01', 'accumulated': '20/1'}]
        result = ex.program.run(body);self.assertEqual(result['status'], 'complete_provisional')
        baseline = ex.native.Engine(spec); assets = baseline.snapshot()['assets']
        for event in events:self.assertEqual(baseline.apply(event)['status'], 'Applied')
        self.assertEqual(baseline.snapshot()['assets'], assets)
        self.assertEqual(result['current']['balances'], {mapping[k]: ex.fmt(v) for k, v in baseline.snapshot()['balances'].items()})
        for key, value in changes.items():self.assertEqual(result['current']['balances'][key], value)
        self.assertEqual(result['current']['memory'], body['opening']['memory'])

    def test_builder_dependency_pin_is_checked(self):
        body, _, _, mapping = ex.fixture()
        with patch.object(operations, 'BINDER_SHA256', '0' * 64):
            with self.assertRaisesRegex(ValueError, 'binder_dependency_hash'):
                operations.build(body['opening'], body['schemas'], {k: mapping[k] for k in operations.CLASSES}, '/stock/unit_cost')


if __name__ == '__main__':unittest.main()
