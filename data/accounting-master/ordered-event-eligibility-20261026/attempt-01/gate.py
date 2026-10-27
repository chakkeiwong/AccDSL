"""Ordered, explicitly bound eligibility; no native lifecycle dependency."""
from copy import deepcopy
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'parameterized-method-construction-20261026'))
import constructor as c
import method_requirements_v3 as guarded

core, base = c.core, c.base
BOOL, TEXT, DATE = core.BOOL, c.TEXT, c.DATE
PROFILE = 'OrderedEventEligibility/1'
CALL = 'OrderedEligibilityCall/1'
FLAGS = dict(executed=False, source_admission=False, accounting_admission=False,
             production_ready=False, full_lifecycle_portable=False)


def make_call(template, book, event, schemas, definition):
    return dict(profile=CALL, operation=template['operation'],
                template_sha256=core.digest(template), state_sha256=core.digest(book),
                event_sha256=core.digest(event), schemas_sha256=core.digest(schemas),
                definition_sha256=core.digest(definition))


def schema_node(definition, pointer):
    node = definition['root']
    for part in base.binding.pointer_parts(pointer):
        c.need(node['node'] == 'record' and part in node['fields'], 'declared_source_path')
        node = node['fields'][part]
    return node


def compile_template(template, book, definition):
    c.closed(template, ['profile', 'context', 'operation', 'input_types', 'stages',
                        'residuals'], 'eligibility_template_fields')
    c.need(template['profile'] == PROFILE, 'eligibility_profile')
    c.need(template['context'] == book['context'], 'context_mismatch')
    base.text(template['operation'], 'operation')
    c.need(type(template['input_types']) is dict and bool(template['input_types']), 'input_types')
    for name, typ in template['input_types'].items():
        base.text(name, 'input_name'); base.scalar_type(typ, book)
    core.identifiers(template['residuals'], 'residuals', True)
    c.need(type(template['stages']) is list and 0 < len(template['stages']) <= 64, 'stage_limit')
    previous, proofs = set(), {}

    def infer(source, depth=0):
        c.need(depth <= core.MAX_DEPTH, 'binding_depth')
        c.need(type(source) is dict, 'source_record')
        kind = source.get('kind')
        if kind == 'event_input':
            c.closed(source, ['kind', 'name'], 'event_source')
            c.need(type(source['name']) is str and source['name'] in template['input_types'], 'undeclared_event_source')
            return template['input_types'][source['name']]
        if kind == 'event_metadata':
            c.closed(source, ['kind', 'field'], 'metadata_source')
            c.need(source['field'] in ('id', 'date'), 'metadata_field')
            return DATE if source['field'] == 'date' else TEXT
        if kind in ('book_date', 'period_end'):
            c.closed(source, ['kind'], 'book_date_source'); return DATE
        if kind == 'memory_leaf':
            c.closed(source, ['kind', 'pointer'], 'memory_source')
            node = schema_node(definition, source['pointer'])
            c.need(node['node'] == 'scalar', 'memory_scalar_required')
            return node['type']
        if kind in ('map_contains', 'map_field'):
            keys = ['kind', 'pointer', 'key_input']
            if kind == 'map_field': keys += ['field', 'after_stage']
            c.closed(source, keys, 'map_source')
            c.need(template['input_types'].get(source['key_input']) == TEXT, 'map_key_text_type')
            node = schema_node(definition, source['pointer'])
            c.need(node['node'] == 'map' and node['values']['node'] == 'record', 'declared_record_map')
            if kind == 'map_contains': return BOOL
            c.need(source['after_stage'] in previous, 'forward_or_missing_presence_stage')
            c.need(proofs.get(source['after_stage']) == (source['pointer'], source['key_input']), 'unproved_row_presence')
            fields = node['values']['fields']
            c.need(source['field'] in fields and fields[source['field']]['node'] == 'scalar', 'row_scalar_field')
            return fields[source['field']]['type']
        if kind == 'calendar_adjacent':
            c.closed(source, ['kind', 'left', 'right'], 'calendar_source')
            c.need(infer(source['left'], depth+1) == DATE and infer(source['right'], depth+1) == DATE, 'calendar_date_type')
            return BOOL
        raise c.Refusal('invalid', 'unsupported_source_kind')

    for stage in template['stages']:
        c.closed(stage, ['id', 'manifest', 'bindings', 'reason'], 'stage_fields')
        name = stage['id']; base.text(name, 'stage_id'); base.text(stage['reason'], 'stage_reason')
        c.need(name not in previous, 'duplicate_stage')
        manifest = stage['manifest']; guarded.compile_manifest(manifest)
        c.need(len(manifest['requirements']) == 1, 'one_predicate_per_stage')
        c.need(type(stage['bindings']) is dict and set(stage['bindings']) == set(manifest['inputs']), 'exact_stage_bindings')
        for key, source in stage['bindings'].items():
            typ = infer(source)
            c.need(manifest['inputs'][key]['type'] == base.dimensions.encoded(typ), 'binding_type_mismatch')
            c.need(manifest['inputs'][key]['role'] != 'caller_finding', 'caller_finding_disallowed')
        # A selected-row lookup is only well-founded after an unconditional
        # single membership predicate for precisely the same map and key.
        req = manifest['requirements'][0]; pred = req['predicate']
        if req['guard'] == {'op': 'const', 'type': BOOL, 'value': True} and pred.get('op') == 'ref':
            source = stage['bindings'][pred['id']]
            if source['kind'] == 'map_contains':
                proofs[name] = (source['pointer'], source['key_input'])
        previous.add(name)
    return template


def resolve(source, book, event):
    kind = source['kind']
    if kind == 'event_input': return deepcopy(event['inputs'][source['name']]['value'])
    if kind == 'event_metadata': return base.known(event[source['field']])
    if kind == 'book_date': return base.known(book['date'])
    if kind == 'period_end': return base.known(book['period']['end_exclusive'])
    if kind == 'memory_leaf':
        found, value = base.binding.located(book['memory'], source['pointer'])
        c.need(found, 'missing_memory_leaf'); return base.known(deepcopy(value))
    if kind in ('map_contains', 'map_field'):
        key = event['inputs'][source['key_input']]['value']
        if key['status'] == 'unknown': return deepcopy(key)
        found, population = base.binding.located(book['memory'], source['pointer'])
        c.need(found and type(population) is dict, 'map_population')
        if kind == 'map_contains': return base.known(key['value'] in population)
        c.need(key['value'] in population, 'presence_prerequisite_failed')
        return base.known(deepcopy(population[key['value']][source['field']]))
    if kind == 'calendar_adjacent':
        left, right = resolve(source['left'], book, event), resolve(source['right'], book, event)
        if left['status'] == 'unknown': return left
        if right['status'] == 'unknown': return right
        a, b = core.scalar(left['value'], 'date'), core.scalar(right['value'], 'date')
        return base.known(b.toordinal() - a.toordinal() == 1)
    raise c.Refusal('invalid', 'unsupported_source_kind')


def assess(template, book, event, schemas, definition, call):
    stage = 'structure'; trace = []
    result = dict(profile=PROFILE, **FLAGS, method_eligible=False)
    try:
        for value in (template, book, event, schemas, definition, call):
            base.memory.bounded(value); c.exact(value)
            c.need(len(core.canonical(value)) <= core.MAX_BYTES, 'record_size_limit')
        c.closed(call, ['profile', 'operation', 'template_sha256', 'state_sha256',
                        'event_sha256', 'schemas_sha256', 'definition_sha256'], 'call_fields')
        c.need(call['profile'] == CALL, 'call_profile')
        for name, value in [('template', template), ('state', book), ('event', event),
                            ('schemas', schemas), ('definition', definition)]:
            c.need(call[name+'_sha256'] == core.digest(value), 'stale_'+name)
        c.need(call['operation'] == template['operation'], 'operation_mismatch')
        result.update({k: call[k] for k in call if k.endswith('_sha256')})
        c.frontend.v2.typed_book(book, definition, schemas)
        stage = 'compile'; compile_template(template, book, definition)
        stage = 'event_structure'
        base.closed(event, ['id', 'date', 'inputs']); base.text(event['id'], 'command_id')
        c.need(event['id'] not in book['seen'], 'duplicate_command')
        stage = 'chronology'
        c.need(book['date'] <= core.scalar(event['date'], 'date').isoformat() < book['period']['end_exclusive'], 'event_chronology')
        stage = 'full_inputs'
        c.need(type(event['inputs']) is dict and set(event['inputs']) == set(template['input_types']), 'exact_event_inputs')
        unknown = []
        for name, record in event['inputs'].items():
            base.closed(record, ['type', 'value', 'provenance'])
            c.need(record['type'] == template['input_types'][name], 'event_type:'+name)
            base.text(record['provenance'], 'event_provenance')
            core.validate_values({'inputs': {name: {'type': base.dimensions.encoded(record['type'])}}}, {name: record['value']})
            if record['value']['status'] == 'unknown': unknown.append(name)
        if unknown:
            return dict(result, status='unresolved', reason='unknown_event_inputs',
                        failed_stage=stage, inputs=unknown, trace=trace)
        for item in template['stages']:
            stage = item['id']
            values = {key: resolve(source, book, event) for key, source in item['bindings'].items()}
            manifest = item['manifest']; digest = core.digest(manifest)
            checked = guarded.assess({digest: manifest}, digest, values, [])
            trace.append(dict(stage=stage, values=values, result=checked))
            if checked['status'] != 'requirements_satisfied':
                status = checked['status'] if checked['status'] in ('invalid', 'unsupported', 'unresolved') else 'invalid'
                reason = item['reason'] if checked['status'] != 'no_active_requirements' else 'no_active_requirements'
                return dict(result, status=status, reason=reason, failed_stage=stage, trace=trace)
        return dict(result, status='eligible', failed_stage=None, trace=trace,
                    scope='Selected ordered full-intent rules; state invariants remain separate prerequisites')
    except (ValueError, TypeError, KeyError, IndexError, RecursionError, OverflowError) as exc:
        return dict(result, status=getattr(exc, 'status', 'invalid'),
                    reason=str(exc)[:300] or type(exc).__name__, failed_stage=stage, trace=trace)
