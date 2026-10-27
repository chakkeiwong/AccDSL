"""Typed finite map growth in a provisional company book; no durable mutation."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import company_book_transition_v1 as base
import company_memory_types_v1 as types

core = base.core
PROFILE = 'CompanyBookTransition/2'
FLAGS = base.FLAGS


def typed_book(book, definition, schemas):
    result = types.derive(definition, book['memory'], book)
    core.need(result['status'] == 'typed', 'typed_memory:' + result.get('reason', 'invalid'))
    core.need(result['schema_sha256'] == book['memory_schema'], 'typed_memory_schema')
    core.need(result['memory_types'] == book['memory_types'], 'typed_memory_leaf_map')
    base.validate_book(book, schemas)
    return result


def input_types(book, method):
    amounts = method['monetary']['definition']
    calculations = {row['id']: row['type'] for row in amounts['calculations']}
    result = {}
    for key, source in method['memory']['input_bindings'].items():
        kind, name = source['kind'], source['name']
        if kind == 'monetary_input': typ = amounts['inputs'][name]['type']
        elif kind == 'calculation': typ = calculations[name]
        else: typ = {'kind': 'date' if name == 'date' else 'text', 'context': {}}
        result[types.pointer([key])] = typ
    return result


def memory_contract(book, method, definition):
    """Validate every destination and template, including unexecuted branches."""
    inputs = input_types(book, method)

    def walk(path):
        node = definition['root']; parent = None
        for token in path:
            parent = node
            if node['node'] == 'record':
                core.need(type(token) is str and token in node['fields'], 'record_write_field')
                node = node['fields'][token]
            elif node['node'] == 'map':
                if type(token) is dict:
                    core.need(inputs.get(token['input_pointer']) == {'kind': 'text', 'context': {}},
                              'dynamic_key_text_type')
                else: base.text(token, 'map_key')
                node = node['values']
            else: raise core.Invalid('scalar_write_parent')
        return parent, node

    def check_value(template, target):
        if target['node'] == 'scalar':
            core.need(template['kind'] in ['read', 'literal'], 'scalar_memory_template')
            typ = target['type']
            if template['kind'] == 'literal':
                core.scalar(template['value'], typ['kind'])
                if typ['kind'] == 'rational': base.monetary.rational(template['value'])
            else:
                population = book['memory_types'] if template['source'] == 'before' else inputs
                core.need(population.get(template['pointer']) == typ, 'memory_write_type_mismatch')
            return
        core.need(template['kind'] == 'object', 'complete_object_template_required')
        fields = template['fields']
        if target['node'] == 'record':
            core.need(set(fields) == set(target['fields']), 'complete_record_fields')
            for name, value in fields.items(): check_value(value, target['fields'][name])
        else:
            core.need(len(fields) <= target['max_items'], 'memory_map_capacity')
            for name, value in fields.items():
                base.text(name, 'map_key'); check_value(value, target['values'])

    for operation in method['memory']['definition']['operations']:
        core.need(operation['op'] in ['replace', 'insert'], 'typed_write_operation')
        parent, target = walk(operation['path'])
        if operation['op'] == 'insert': core.need(parent['node'] == 'map', 'insert_map_only')
        else: core.need(target['node'] == 'scalar', 'replace_scalar_only')
        check_value(operation['value'], target)


def prepare(book, request):
    types.protected(); base.memory.bounded(request)
    base.closed(request, ['profile', 'expected_state_sha256', 'expected_method_sha256',
                         'method', 'event', 'schemas', 'memory_definition'])
    core.need(request['profile'] == PROFILE, 'request_profile')
    core.need(request['expected_state_sha256'] == core.digest(book), 'stale_state')
    core.need(request['expected_method_sha256'] == core.digest(request['method']), 'method_hash')
    typed_book(book, request['memory_definition'], request['schemas'])
    # Validate common contracts using the frozen engine. Never execute this copy.
    projected = deepcopy(request); projected.pop('memory_definition')
    projected['profile'] = base.PROFILE
    projected['method']['memory']['definition']['operations'] = []
    projected['expected_method_sha256'] = core.digest(projected['method'])
    base.prepare(book, projected)
    method = request['method']
    base.memory.compile_definition(method['memory']['definition'], request['schemas'])
    memory_contract(book, method, request['memory_definition'])
    return method, request['event'], request['schemas']


def invalid(exc):
    return {'profile': PROFILE, **FLAGS, 'status': 'invalid', 'reason': str(exc)[:300] or type(exc).__name__}


def propose(book, request):
    try:
        method, event, schemas = prepare(book, request)
        result = {'profile': PROFILE, **FLAGS, 'before_sha256': core.digest(book),
            'request_sha256': core.digest(request), 'method_sha256': core.digest(method),
            'implementation_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
            'type_implementation_sha256': sha256(Path(types.__file__).read_bytes()).hexdigest(),
            'engine_sha256': types.ENGINE_SHA256, 'dependency_sha256': deepcopy(base.PINS),
            'memory_definition_sha256': core.digest(request['memory_definition']),
            'residual_prerequisites': deepcopy(method['residual_prerequisites'])}
        pre = base.assessment(book, event, method, method['preconditions']); result['preconditions'] = pre
        if pre['status'] not in ['requirements_satisfied', 'no_active_requirements']:
            return {**result, 'status': pre['status'], 'reason': 'preconditions'}
        definition = method['monetary']['definition']
        values = base.values_for(book, event, method, definition['inputs'], method['monetary']['bindings'])
        h = core.digest(definition); amounts = base.monetary.derive({h: definition}, h, values)
        result['monetary'] = amounts
        if amounts['status'] != 'derived': return {**result, 'status': amounts['status'], 'reason': 'monetary'}
        calculations = {row['id']: row['binding']['value'] for row in amounts['diagnostics']['calculations']}
        inputs = {}
        for key, source in method['memory']['input_bindings'].items():
            name = source['name']
            inputs[key] = (values[name]['value'] if source['kind'] == 'monetary_input' else
                           calculations[name] if source['kind'] == 'calculation' else event[name])
        memdef = method['memory']['definition']; h = core.digest(memdef)
        staged = base.memory.stage({h: memdef}, h, schemas, book['memory'], inputs)
        result['memory'] = staged
        if staged['status'] != 'staged': return {**result, 'status': staged['status'], 'reason': 'memory'}
        derived = types.derive(request['memory_definition'], staged['after'], book)
        core.need(derived['status'] == 'typed', 'typed_after:' + derived.get('reason', 'invalid'))
        after = deepcopy(book); after['memory'] = staged['after']; after['memory_types'] = derived['memory_types']
        journal = {key: '0/1' for key in book['accounts']}
        for role, value in amounts['journal'].items():
            key = method['account_map'][role]; journal[key] = value
            after['balances'][key] = base.monetary.fmt(base.monetary.bounded(
                base.monetary.rational(book['balances'][key]) + base.monetary.rational(value)))
        flows = [{'id': core.digest([event['id'], row['id']]), 'entity': book['context']['entity'],
            'book': book['context']['book'], 'currency': book['context']['currency'], 'event_id': event['id'],
            'date': event['date'], 'activity': row['activity'], 'origin': row['origin'], 'amount': row['amount']}
            for row in amounts['flows']]
        after['date'] = event['date']; after['seen'].append(event['id']); after['flows'].extend(flows)
        typed_book(after, request['memory_definition'], schemas)
        post = base.assessment(after, event, method, method['postconditions']); result['postconditions'] = post
        if post['status'] not in ['requirements_satisfied', 'no_active_requirements']:
            return {**result, 'status': post['status'], 'reason': 'postconditions'}
        return {**result, 'status': 'proposed', 'after': after, 'journal': journal,
                'flows': flows, 'after_sha256': core.digest(after)}
    except Exception as exc: return invalid(exc)


def apply(book, request, proposal):
    try:
        base.memory.bounded(proposal)
        expected = propose(book, request)
        core.need(core.canonical(expected) == core.canonical(proposal), 'proposal_recomputation_mismatch')
        if expected['status'] != 'proposed': return expected
        return {**deepcopy(expected), 'status': 'applied_provisional'}
    except Exception as exc: return invalid(exc)
