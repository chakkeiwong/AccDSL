from copy import deepcopy
from pathlib import Path
import sys
import unittest
import importlib.util
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / 'scripts'))
import company_memory_types_v1 as memory


def scalar(typ): return {'node': 'scalar', 'type': deepcopy(typ)}
def record(fields): return {'node': 'record', 'fields': fields}


def fixture():
    book = {'context': {'entity': 'Example', 'book': 'legal', 'currency': 'USD', 'case_id': 'synthetic', 'mode': 'synthetic'}}
    money = memory.engine.money_type(book)
    claim = record({'due': scalar({'kind': 'date', 'context': {}}), 'remaining': scalar(money)})
    definition = {'profile': memory.PROFILE, 'root': record({'tag': scalar({'kind': 'text', 'context': {}}),
                   'claims': {'node': 'map', 'max_items': 3, 'values': claim}})}
    value = {'tag': 'preserve', 'claims': {'a/b~c': {'due': '2028-02-29', 'remaining': '10/1'}}}
    return definition, value, book


class CompanyMemoryTypesTests(unittest.TestCase):
    def test_actual_collection_opening_matches_every_existing_leaf(self):
        path = ROOT / 'data/accounting-master/declared-dynamic-collection-clock-20261025/examples.py'
        spec = importlib.util.spec_from_file_location('memory_collection_examples', path)
        ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
        for owner in ['alpha', 'beta']:
            q, _, _ = ex.fixture(owner); book = q['program']['opening']
            def declaration(value, path):
                if type(value) is dict:
                    return record({k: declaration(v, path + [k]) for k, v in value.items()})
                return scalar(book['memory_types'][memory.pointer(path)])
            d = {'profile': memory.PROFILE, 'root': declaration(book['memory'], [])}
            result = memory.derive(d, book['memory'], book)
            self.assertEqual(result['status'], 'typed', result)
            self.assertEqual(result['memory_types'], book['memory_types'])
            memory.engine.validate_book(book, q['program']['schemas'])

    def test_existing_stager_inserts_then_exact_types_are_derived(self):
        d, v, b = fixture(); before = deepcopy(v)
        state = memory.compile_schema(d, b)
        inp = memory.compile_schema({'profile': memory.PROFILE, 'root': record({
            'identity': scalar({'kind': 'text', 'context': {}})})}, b)
        schemas = {memory.core.digest(s): s for s in [state, inp]}
        operation = {'id': 'create', 'op': 'insert',
            'path': ['claims', {'input_pointer': '/identity'}],
            'value': {'kind': 'object', 'fields': {
                'due': {'kind': 'literal', 'value': '2028-03-01'},
                'remaining': {'kind': 'literal', 'value': '7/1'}}}}
        method = {'profile': memory.engine.memory.PROFILE, 'state_schema': memory.core.digest(state),
            'input_schema': memory.core.digest(inp), 'operations': [operation]}
        h = memory.core.digest(method)
        staged = memory.engine.memory.stage({h: method}, h, schemas, v, {'identity': 'new/claim~1'})
        self.assertEqual(staged['status'], 'staged', staged); self.assertEqual(v, before)
        typed = memory.derive(d, staged['after'], b)
        self.assertEqual(typed['status'], 'typed', typed)
        self.assertEqual(typed['memory_types']['/claims/new~1claim~01/remaining'], memory.engine.money_type(b))
        collision = memory.engine.memory.stage({h: method}, h, schemas, staged['after'], {'identity': 'new/claim~1'})
        self.assertEqual(collision['status'], 'invalid'); self.assertNotIn('after', collision)
        self.assertEqual(v, before)

    def test_schema_staging_alone_does_not_enforce_typed_capacity(self):
        d, v, b = fixture(); d['root']['fields']['claims']['max_items'] = 1
        value = deepcopy(v); value['claims']['extra'] = deepcopy(next(iter(v['claims'].values())))
        memory.engine.memory.validate(value, memory.compile_schema(d, b))
        self.assertIn('memory_map_capacity', memory.derive(d, value, b)['reason'])

    def test_exact_types_and_escaped_identity(self):
        definition, value, book = fixture(); before = deepcopy((definition, value, book))
        out = memory.derive(definition, value, book)
        self.assertEqual(out['status'], 'typed', out)
        self.assertEqual(out['memory_types'], {'/tag': {'kind': 'text', 'context': {}},
            '/claims/a~1b~0c/due': {'kind': 'date', 'context': {}},
            '/claims/a~1b~0c/remaining': memory.engine.money_type(book)})
        self.assertEqual(before, (definition, value, book)); self.assertTrue(memory.verify(definition, value, book, out))

    def test_empty_map_has_no_fictitious_items(self):
        d, v, b = fixture(); v['claims'] = {}; out = memory.derive(d, v, b)
        self.assertEqual(out['status'], 'typed'); self.assertEqual(set(out['memory_types']), {'/tag'})
        self.assertEqual(out['maps'][0]['items'], [])

    def test_population_growth_keeps_existing_types(self):
        d, v, b = fixture(); old = memory.derive(d, v, b)
        v['claims']['new'] = {'due': '2028-03-01', 'remaining': '5/1'}; out = memory.derive(d, v, b)
        self.assertEqual(out['status'], 'typed'); self.assertEqual(len(out['memory_types']), 5)
        for k, typ in old['memory_types'].items(): self.assertEqual(out['memory_types'][k], typ)

    def test_schema_shape_missing_extra_and_wrong_values(self):
        for mutate in [lambda v: v.update(extra='x'), lambda v: v.pop('tag'),
                       lambda v: v['claims']['a/b~c'].update(extra='x'),
                       lambda v: v['claims']['a/b~c'].update(remaining='2/2'),
                       lambda v: v['claims']['a/b~c'].update(remaining=True),
                       lambda v: v['claims']['a/b~c'].update(due='2027-02-29')]:
            d, v, b = fixture(); mutate(v); self.assertEqual(memory.derive(d, v, b)['status'], 'invalid')

    def test_map_capacity_boundary(self):
        d, v, b = fixture(); v['claims'] = {str(i): {'due': '2028-01-01', 'remaining': '0/1'} for i in range(3)}
        self.assertEqual(memory.derive(d, v, b)['status'], 'typed')
        v['claims']['3'] = deepcopy(v['claims']['0']); self.assertIn('memory_map_capacity', memory.derive(d, v, b)['reason'])

    def test_unknown_nodes_limits_and_context_refuse(self):
        mutations = [lambda d: d['root']['fields']['claims'].update(max_items=True),
                     lambda d: d['root']['fields']['claims'].update(max_items=257),
                     lambda d: d['root']['fields']['claims'].update(node='array'),
                     lambda d: d['root']['fields']['claims']['values']['fields']['remaining']['type']['context'].update(entity='Other'),
                     lambda d: d.update(extra='ignored')]
        for edit in mutations:
            d, v, b = fixture(); edit(d); self.assertEqual(memory.derive(d, v, b)['status'], 'invalid')

    def test_nested_maps_have_distinct_identity_paths(self):
        d, v, b = fixture(); child = d['root']['fields']['claims']; d['root']['fields']['claims'] = {'node': 'map', 'max_items': 2, 'values': child}
        v['claims'] = {'customer': v['claims']}; out = memory.derive(d, v, b)
        self.assertEqual(out['status'], 'typed'); self.assertIn('/claims/customer/a~1b~0c/remaining', out['memory_types'])
        self.assertEqual(len(out['maps']), 2)

    def test_scalar_fixed_record_matches_existing_book_leaf_types(self):
        d, v, b = fixture(); d['root']['fields']['claims'] = record({'a/b~c': d['root']['fields']['claims']['values']})
        out = memory.derive(d, v, b); self.assertEqual(out['status'], 'typed')
        for pointer, typ in out['memory_types'].items():
            found, value = memory.engine.binding.located(v, pointer); self.assertTrue(found)
            memory.core.scalar(value, typ['kind'])
        self.assertEqual(set(out['memory_types']), set(memory.engine.leaf_values(v)))

    def test_empty_and_control_keys_refuse(self):
        for key in ['', ' ', 'bad' + chr(10)]:
            d, v, b = fixture(); v['claims'] = {key: {'due': '2028-01-01', 'remaining': '1/1'}}
            self.assertEqual(memory.derive(d, v, b)['status'], 'invalid')

    def test_proposal_flags_and_types_cannot_be_tampered(self):
        d, v, b = fixture(); out = memory.derive(d, v, b)
        changed = deepcopy(out); changed['source_admission'] = 0; self.assertFalse(memory.verify(d, v, b, changed))
        changed = deepcopy(out); changed['memory_types'].pop('/tag'); self.assertFalse(memory.verify(d, v, b, changed))
        with patch.object(memory, 'ENGINE_SHA256', '0' * 64): self.assertEqual(memory.derive(d, v, b)['status'], 'invalid')


if __name__ == '__main__': unittest.main()
