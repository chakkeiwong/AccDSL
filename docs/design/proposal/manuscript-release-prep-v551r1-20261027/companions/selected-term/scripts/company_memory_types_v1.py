"""Explicit finite memory types; derive current scalar leaves, execute no effects."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import company_book_transition_v1 as engine

core = engine.core
PROFILE = 'CompanyMemoryTypes/1'
MAX_ITEMS = 256
ENGINE_SHA256 = '3f46df2d4c7b65f344c0a1234177503a0869b9162b4a85bdda224c2eddbea8ff'


def protected():
    core.need(sha256(Path(engine.__file__).read_bytes()).hexdigest() == ENGINE_SHA256, 'book_dependency_hash')
    engine.protected()


def pointer(path):
    return ''.join('/' + token.replace('~', '~0').replace('/', '~1') for token in path)


def compile_schema(definition, book):
    protected(); engine.memory.bounded(definition)
    engine.closed(definition, ['profile', 'root'])
    core.need(definition['profile'] == PROFILE, 'memory_type_profile')
    nodes = [0]
    def visit(node, depth):
        nodes[0] += 1
        core.need(nodes[0] <= core.MAX_NODES and depth <= core.MAX_DEPTH, 'memory_type_limit')
        core.need(type(node) is dict, 'memory_type_node')
        kind = node.get('node')
        if kind == 'scalar':
            engine.closed(node, ['node', 'type']); typ = node['type']
            engine.scalar_type(typ, book)
            if typ['kind'] == 'boolean': return {'type': 'boolean'}
            return {'type': 'string', 'minLength': 1, 'maxLength': core.MAX_SCALAR, 'x-exact-kind': typ['kind']}
        if kind == 'record':
            engine.closed(node, ['node', 'fields']); fields = node['fields']
            core.need(type(fields) is dict, 'memory_record_fields')
            for key in fields: engine.text(key, 'memory_field')
            return {'type': 'object', 'properties': {k: visit(v, depth + 1) for k, v in fields.items()},
                    'required': list(fields), 'additionalProperties': False}
        core.need(kind == 'map', 'memory_node_kind')
        engine.closed(node, ['node', 'max_items', 'values'])
        core.need(type(node['max_items']) is int and 0 < node['max_items'] <= MAX_ITEMS, 'memory_map_limit')
        return {'type': 'object', 'propertyNames': {'type': 'string', 'minLength': 1, 'maxLength': core.MAX_SCALAR},
                'additionalProperties': visit(node['values'], depth + 1)}
    core.need(definition['root'].get('node') == 'record', 'root_record_required')
    shape = visit(definition['root'], 0); engine.memory.check_schema(shape)
    return shape


def derive(definition, value, book):
    """Every current leaf has one declared type; an empty map has no items."""
    try:
        shape = compile_schema(definition, book)
        engine.memory.validate(value, shape)
        leaves = {}; maps = []
        def visit(node, item, path):
            kind = node['node']
            if kind == 'scalar':
                typ = node['type']; core.scalar(item, typ['kind'])
                if typ['kind'] == 'rational': engine.monetary.rational(item)
                leaves[pointer(path)] = deepcopy(typ)
            elif kind == 'record':
                for name, child in node['fields'].items(): visit(child, item[name], path + [name])
            else:
                core.need(len(item) <= node['max_items'], 'memory_map_capacity:' + pointer(path))
                maps.append({'pointer': pointer(path), 'items': list(item), 'max_items': node['max_items']})
                for key, child in item.items():
                    engine.text(key, 'memory_map_key'); visit(node['values'], child, path + [key])
        visit(definition['root'], value, [])
        core.need(set(leaves) == set(engine.leaf_values(value)), 'complete_memory_type_population')
        return {'profile': PROFILE, 'status': 'typed', 'definition_sha256': core.digest(definition),
                'value_sha256': core.digest(value), 'schema': shape, 'schema_sha256': core.digest(shape),
                'memory_types': leaves, 'maps': maps, 'executed': False, 'source_admission': False,
                'accounting_admission': False, 'committed': False,
                'implementation_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
                'engine_sha256': ENGINE_SHA256,
                'scope': 'Current typed memory only; no journal, transition, claim lifecycle or durability'}
    except Exception as exc:
        return {'profile': PROFILE, 'status': 'invalid', 'reason': str(exc)[:300],
                'executed': False, 'source_admission': False, 'accounting_admission': False, 'committed': False}


def verify(definition, value, book, result):
    try: return core.canonical(derive(definition, value, book)) == core.canonical(result)
    except Exception: return False
