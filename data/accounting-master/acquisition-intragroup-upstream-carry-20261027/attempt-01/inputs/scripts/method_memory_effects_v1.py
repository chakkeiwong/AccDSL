"""Closed typed memory staging; no source admission or durable mutation."""
from copy import deepcopy
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError
import method_requirements_v1 as core
import method_input_binding_v1 as binding

PROFILE = 'MethodMemoryEffects/1'
MAX_OPERATIONS = 256
PATTERNS = {
    r'^(0|-?[1-9][0-9]*)/[1-9][0-9]*$',
    r'^/record_registry/[0-9a-f]{64}/body(?:/(?:[^~/]|~[01])*)*$',
    r'^[0-9a-f]{64}$', r'^[A-Za-z][A-Za-z0-9_-]*$',
    r'^\d{4}-\d{2}-\d{2}$',
}
BOUNDARY = {'executed':False, 'committed':False, 'method_eligible':False,
            'source_admission':False, 'accounting_admission':False,
            'scope':'selected_typed_memory_staging_only'}


def bounded(value):
    core.need(len(core.canonical(value)) <= core.MAX_BYTES, 'record_size_limit')
    binding.bounded(value)


def check_schema(shape):
    """Finite closed subset; never resolve refs or admit arbitrary regexes."""
    bounded(shape)
    Draft202012Validator.check_schema(shape)
    def walk(rule):
        core.need(type(rule) is dict and bool(rule), 'closed_schema_required')
        r = dict(rule)
        if '$schema' in r:
            core.need(r.pop('$schema') == 'https://json-schema.org/draft/2020-12/schema', 'schema_draft')
        if 'oneOf' in r:
            core.closed(r, ['oneOf'], 'union_schema')
            core.need(type(r['oneOf']) is list and 1 < len(r['oneOf']) <= 16, 'schema_union_limit')
            for child in r['oneOf']: walk(child)
            return
        if set(r) == {'const'}:
            core.need(type(r['const']) in [str,bool], 'scalar_constant_schema')
            if type(r['const']) is str: core.text(r['const'], 'schema_const')
            return
        if set(r) == {'enum'}:
            core.identifiers(r['enum'], 'schema_enum', nonempty=True)
            return
        kind = r.get('type')
        core.need(type(kind) is str, 'schema_type')
        if kind == 'object':
            if 'properties' in r:
                core.closed(r, ['type','properties','required','additionalProperties'], 'record_schema')
                core.need(r['additionalProperties'] is False, 'closed_record_required')
                core.need(type(r['properties']) is dict, 'schema_properties')
                core.identifiers(r['required'], 'required')
                core.need(set(r['required']) == set(r['properties']), 'all_record_fields_required')
                for key, child in r['properties'].items():
                    core.text(key, 'schema_property'); walk(child)
            else:
                core.closed(r, ['type','propertyNames','additionalProperties'], 'map_schema')
                walk(r['propertyNames'])
                core.need(r['propertyNames'].get('type') == 'string', 'map_key_schema')
                walk(r['additionalProperties'])
        elif kind == 'array':
            core.closed(r, ['type','items'], 'array_schema'); walk(r['items'])
        elif kind == 'boolean':
            core.need(set(r) <= {'type','const'}, 'boolean_schema_fields')
            core.need('const' not in r or type(r['const']) is bool, 'boolean_const')
        elif kind == 'string':
            core.need(set(r) <= {'type','minLength','maxLength','pattern','format','x-exact-kind','not'}, 'string_schema_fields')
            if 'pattern' in r: core.need(r['pattern'] in PATTERNS, 'unsupported_schema_pattern')
            if 'format' in r: core.need(r['format'] == 'date', 'unsupported_schema_format')
            if 'x-exact-kind' in r: core.need(r['x-exact-kind'] in ['rational','date','text'], 'exact_scalar_kind')
            if 'not' in r:
                core.closed(r['not'], ['const'], 'excluded_scalar'); core.text(r['not']['const'], 'excluded_scalar')
            for key in ['minLength','maxLength']:
                if key in r: core.need(type(r[key]) is int and 0 <= r[key] <= core.MAX_SCALAR, 'schema_string_bound')
        else: raise core.Invalid('unsupported_schema_type:'+kind)
    walk(shape)
    return shape


def validate(value, shape):
    bounded(value)
    error = next(Draft202012Validator(shape, format_checker=FormatChecker()).iter_errors(value), None)
    if error is not None: raise core.Invalid('structure:'+str(list(error.absolute_path))+':'+error.message[:180])
    def walk(item, rule):
        if 'oneOf' in rule:
            matching = [r for r in rule['oneOf'] if Draft202012Validator(r, format_checker=FormatChecker()).is_valid(item)]
            core.need(len(matching) == 1, 'ambiguous_schema_union')
            return walk(item, matching[0])
        if 'x-exact-kind' in rule: core.scalar(item, rule['x-exact-kind'])
        if type(item) is dict:
            for key, child in item.items():
                core.text(key, 'record_key')
                walk(child, rule.get('properties',{}).get(key, rule.get('additionalProperties',{})))
        elif type(item) is list:
            for child in item: walk(child, rule['items'])
        elif type(item) is str:
            core.text(item, 'record_text')
            core.need(not any(c in item for c in '\x85\u2028\u2029'), 'single_line_scalar')
        else: core.need(type(item) is bool, 'record_scalar_type')
    walk(value, shape)


def template(node, counter, depth=0):
    counter[0] += 1
    core.need(counter[0] <= core.MAX_NODES and depth <= core.MAX_DEPTH, 'template_limit')
    core.need(type(node) is dict and type(node.get('kind')) is str, 'value_template')
    kind = node['kind']
    if kind == 'literal':
        core.closed(node, ['kind','value'], 'literal')
        core.need(type(node['value']) in [str,bool], 'literal_scalar')
        if type(node['value']) is str: core.text(node['value'], 'literal')
    elif kind == 'read':
        core.closed(node, ['kind','source','pointer'], 'read')
        core.need(type(node['source']) is str and node['source'] in ['before','inputs'], 'read_source')
        binding.pointer_parts(node['pointer'])
    elif kind == 'object':
        core.closed(node, ['kind','fields'], 'object_template')
        core.need(type(node['fields']) is dict, 'object_fields')
        for key, child in node['fields'].items():
            core.text(key, 'object_key'); template(child, counter, depth+1)
    elif kind == 'array':
        core.closed(node, ['kind','items'], 'array_template')
        core.need(type(node['items']) is list, 'array_items')
        for child in node['items']: template(child, counter, depth+1)
    else: raise core.Invalid('unsupported_value_template:'+kind)


def compile_definition(definition, schemas):
    bounded(definition)
    core.closed(definition, ['profile','state_schema','input_schema','operations'], 'memory_definition')
    core.need(definition['profile'] == PROFILE, 'profile')
    state_shape = binding.record(schemas, definition['state_schema'], 'state_schema')
    input_shape = binding.record(schemas, definition['input_schema'], 'input_schema')
    check_schema(state_shape); check_schema(input_shape)
    core.need(type(definition['operations']) is list and len(definition['operations']) <= MAX_OPERATIONS, 'operation_limit')
    ids, counter = set(), [0]
    for operation in definition['operations']:
        core.closed(operation, ['id','op','path','value'], 'operation')
        core.text(operation['id'], 'operation_id')
        core.need(operation['id'] not in ids, 'duplicate_operation_id'); ids.add(operation['id'])
        core.need(type(operation['op']) is str and operation['op'] in ['replace','insert','append'], 'unsupported_memory_operation')
        path = operation['path']
        core.need(type(path) is list and 0 < len(path) <= core.MAX_DEPTH, 'write_path')
        for token in path:
            if type(token) is str: core.text(token, 'path_token')
            else:
                core.closed(token, ['input_pointer'], 'dynamic_path_token')
                binding.pointer_parts(token['input_pointer'])
        template(operation['value'], counter)
    return state_shape, input_shape


def read(record, pointer):
    found, value = binding.located(record, pointer)
    core.need(found, 'missing_read:'+pointer)
    return deepcopy(value)


def materialize(node, before, inputs):
    if node['kind'] == 'literal': return deepcopy(node['value'])
    if node['kind'] == 'read': return read(before if node['source'] == 'before' else inputs, node['pointer'])
    if node['kind'] == 'object': return {key:materialize(child,before,inputs) for key,child in node['fields'].items()}
    return [materialize(child,before,inputs) for child in node['items']]


def locate_tokens(record, path):
    value = record
    for token in path:
        core.need(type(value) is dict and token in value, 'missing_or_nonobject_write_parent')
        value = value[token]
    return value


def stage(registry, selected_digest, schemas, before, inputs):
    try:
        definition = binding.record(registry, selected_digest, 'memory_definition')
        state_shape, input_shape = compile_definition(definition, schemas)
        validate(before, state_shape); validate(inputs, input_shape)
        resolved = []
        for operation in definition['operations']:
            path = [token if type(token) is str else read(inputs,token['input_pointer']) for token in operation['path']]
            for token in path: core.text(token, 'resolved_path_token')
            for prior, prior_path in resolved:
                overlap = path[:len(prior_path)] == prior_path or prior_path[:len(path)] == path
                repeated_append = path == prior_path and prior['op'] == operation['op'] == 'append'
                core.need(not overlap or repeated_append, 'conflicting_memory_paths')
            resolved.append((operation,path))
        after, findings = deepcopy(before), []
        for operation, path in resolved:
            value = materialize(operation['value'], before, inputs); bounded(value)
            if operation['op'] == 'append':
                target = locate_tokens(after,path)
                core.need(type(target) is list, 'append_target_not_array'); target.append(value)
            else:
                target = locate_tokens(after,path[:-1])
                core.need(type(target) is dict, 'write_parent_not_object')
                exists = path[-1] in target
                core.need(exists if operation['op']=='replace' else not exists,
                          'replace_target_absent' if operation['op']=='replace' else 'insert_target_exists')
                target[path[-1]] = value
            bounded(after)
            findings.append({'id':operation['id'], 'op':operation['op'], 'resolved_path':path})
        validate(after,state_shape)
        return {**BOUNDARY,'profile':PROFILE,'status':'staged','selected_digest':selected_digest,
                'before_sha256':core.digest(before),'inputs_sha256':core.digest(inputs),
                'state_schema':definition['state_schema'],'input_schema':definition['input_schema'],
                'after_sha256':core.digest(after),'after':after,'operations':findings}
    except binding.Unavailable as exc:
        return {**BOUNDARY,'status':'unsupported','reason':str(exc)[:250]}
    except (ValueError,TypeError,KeyError,RecursionError,OverflowError,SchemaError) as exc:
        return {**BOUNDARY,'status':'invalid','reason':str(exc)[:250]}
