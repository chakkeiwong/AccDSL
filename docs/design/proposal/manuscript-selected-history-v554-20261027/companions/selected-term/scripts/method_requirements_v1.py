"""Pure typed precondition assessment; no method execution or authority admission."""
from datetime import date
from fractions import Fraction
from hashlib import sha256
import json
import re

PROFILE = 'MethodRequirements/1'
BOOL = {'kind': 'boolean', 'context': {}}
KINDS = {'boolean', 'text', 'date', 'rational'}
ROLES = {'state', 'reported_measurement', 'assumption', 'caller_finding'}
MAX_BYTES = 1_000_000
MAX_NODES = 4096
MAX_DEPTH = 48
MAX_SCALAR = 4096


class Invalid(ValueError):
    pass


def need(condition, reason):
    if not condition:
        raise Invalid(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')


def digest(value):
    return sha256(canonical(value)).hexdigest()


def closed(value, keys, name):
    need(type(value) is dict and set(value) == set(keys), 'fields:' + name)


def text(value, name):
    need(type(value) is str and 0 < len(value) <= MAX_SCALAR, 'text:' + name)
    need(not any(ord(c) < 32 or ord(c) == 127 for c in value), 'control:' + name)


def identifiers(value, name, nonempty=False):
    need(type(value) is list, 'list:' + name)
    for item in value:
        text(item, name)
    need(len(set(value)) == len(value), 'duplicate:' + name)
    need(not nonempty or bool(value), 'empty:' + name)


def typed(value):
    closed(value, ['kind', 'context'], 'type')
    need(type(value['kind']) is str and value['kind'] in KINDS, 'type_kind')
    need(type(value['context']) is dict, 'type_context')
    for key, item in value['context'].items():
        text(key, 'context_key')
        text(item, 'context_value')
    return value


def scalar(value, kind):
    if kind == 'boolean':
        need(type(value) is bool, 'boolean_value')
        return value
    text(value, kind)
    if kind == 'rational':
        need(re.fullmatch(r'(0|-?[1-9][0-9]*)/[1-9][0-9]*', value) is not None,
             'rational_syntax')
        q = Fraction(value)
        need(value == f'{q.numerator}/{q.denominator}', 'noncanonical_rational')
        return q
    if kind == 'date':
        d = date.fromisoformat(value)
        need(d.isoformat() == value, 'date_format')
        return d
    return value


def expression(node, inputs, counter=None, depth=0):
    """Return exact type and declared dependencies without evaluating facts."""
    if counter is None:
        counter = [0]
    counter[0] += 1
    need(counter[0] <= MAX_NODES and depth <= MAX_DEPTH, 'expression_limit')
    need(type(node) is dict and type(node.get('op')) is str, 'expression')
    op = node['op']
    if op == 'ref':
        closed(node, ['op', 'id'], op)
        text(node['id'], 'input_id')
        need(node['id'] in inputs, 'undeclared_input:' + node['id'])
        return inputs[node['id']]['type'], {node['id']}
    if op == 'const':
        closed(node, ['op', 'type', 'value'], op)
        t = typed(node['type'])
        scalar(node['value'], t['kind'])
        return t, set()
    if op in {'eq', 'le', 'lt', 'add', 'sub'}:
        closed(node, ['op', 'left', 'right'], op)
        a, ar = expression(node['left'], inputs, counter, depth+1)
        b, br = expression(node['right'], inputs, counter, depth+1)
        need(a == b, 'type_or_context_mismatch')
        if op in {'add', 'sub'}:
            need(a['kind'] == 'rational', 'numeric_type')
        if op in {'le', 'lt'}:
            need(a['kind'] in {'rational', 'date'}, 'ordered_type')
        return (a if op in {'add', 'sub'} else BOOL), ar | br
    if op in {'all', 'any'}:
        closed(node, ['op', 'args'], op)
        need(type(node['args']) is list and bool(node['args']), 'nonempty_args')
        refs = set()
        for child in node['args']:
            t, r = expression(child, inputs, counter, depth+1)
            need(t['kind'] == 'boolean', 'boolean_operand')
            refs |= r
        return BOOL, refs
    if op == 'not':
        closed(node, ['op', 'arg'], op)
        t, refs = expression(node['arg'], inputs, counter, depth+1)
        need(t['kind'] == 'boolean', 'boolean_operand')
        return BOOL, refs
    raise Invalid('unsupported_operator:' + op)


def validate_manifest(manifest):
    need(len(canonical(manifest)) <= MAX_BYTES, 'manifest_size_limit')
    closed(manifest, ['profile', 'method_id', 'version', 'inputs', 'requirements',
                      'capabilities', 'residual_prerequisites'], 'manifest')
    need(manifest['profile'] == PROFILE, 'profile')
    text(manifest['method_id'], 'method_id')
    text(manifest['version'], 'version')
    inputs = manifest['inputs']
    need(type(inputs) is dict, 'inputs')
    for key, declaration in inputs.items():
        text(key, 'input_id')
        closed(declaration, ['type', 'role', 'source_ref'], 'input_declaration')
        t = typed(declaration['type'])
        need(type(declaration['role']) is str and declaration['role'] in ROLES, 'role')
        need(declaration['role'] != 'caller_finding' or t['kind'] == 'boolean',
             'finding_boolean_required')
        text(declaration['source_ref'], 'source_ref')
    requirements = manifest['requirements']
    need(type(requirements) is list and bool(requirements), 'requirements')
    ids, used, counter = set(), set(), [0]
    for req in requirements:
        closed(req, ['id', 'predicate', 'requires', 'admission_refs',
                     'on_false', 'on_unknown'], 'requirement')
        text(req['id'], 'requirement_id')
        need(req['id'] not in ids, 'duplicate_requirement')
        ids.add(req['id'])
        t, refs = expression(req['predicate'], inputs, counter)
        need(t['kind'] == 'boolean', 'predicate_boolean_required')
        identifiers(req['requires'], 'requires')
        need(set(req['requires']) == refs, 'inexact_dependency_declaration')
        used |= refs
        identifiers(req['admission_refs'], 'admission_refs')
        need(req['on_false'] in ['invalid', 'unsupported'], 'false_consequence')
        need(req['on_unknown'] == 'unresolved', 'unknown_consequence')
    need(used == set(inputs), 'unused_input_declaration')
    identifiers(manifest['capabilities'], 'capabilities')
    identifiers(manifest['residual_prerequisites'], 'residual_prerequisites', True)
    return manifest


def validate_values(manifest, values):
    need(type(values) is dict and len(canonical(values)) <= MAX_BYTES, 'values')
    need(set(values) <= set(manifest['inputs']), 'undeclared_value')
    for key, item in values.items():
        need(type(item) is dict, 'binding')
        if item.get('status') == 'known':
            closed(item, ['status', 'value'], 'known_binding')
            scalar(item['value'], manifest['inputs'][key]['type']['kind'])
        elif item.get('status') == 'unknown':
            closed(item, ['status', 'reason'], 'unknown_binding')
            text(item['reason'], 'unknown_reason')
        else:
            raise Invalid('binding_status')


def _evaluate(node, manifest, values):
    """Return (known, value, unresolved dependencies), visiting every operand."""
    op = node['op']
    if op == 'ref':
        key = node['id']
        item = values.get(key, {'status': 'unknown', 'reason': 'missing_input'})
        if item['status'] == 'unknown':
            return False, None, {key: item['reason']}
        kind = manifest['inputs'][key]['type']['kind']
        return True, scalar(item['value'], kind), {}
    if op == 'const':
        return True, scalar(node['value'], node['type']['kind']), {}
    if op == 'not':
        known, value, missing = _evaluate(node['arg'], manifest, values)
        return known, not value if known else None, missing
    if op in {'all', 'any'}:
        parts = [_evaluate(child, manifest, values) for child in node['args']]
        missing = {k:v for _, _, deps in parts for k,v in deps.items()}
        decisive = False if op == 'all' else True
        if any(known and value is decisive for known, value, _ in parts):
            return True, decisive, missing
        if all(known for known, _, _ in parts):
            return True, not decisive, missing
        return False, None, missing
    ak, a, ad = _evaluate(node['left'], manifest, values)
    bk, b, bd = _evaluate(node['right'], manifest, values)
    missing = {**ad, **bd}
    if not ak or not bk:
        return False, None, missing
    if op == 'eq':
        value = a == b
    elif op == 'le':
        value = a <= b
    elif op == 'lt':
        value = a < b
    elif op == 'add':
        value = a + b
    elif op == 'sub':
        value = a - b
    else:
        raise Invalid('unsupported_operator:' + op)
    return True, value, missing


def assess(registry, selected_digest, values, available_capabilities):
    """Assess only the selected declarations; never infer full method eligibility."""
    boundary = {'executed': False, 'source_admission': False,
                'accounting_admission': False, 'method_eligible': False,
                'scope': 'selected_requirements_only'}
    try:
        need(type(registry) is dict, 'registry')
        need(type(selected_digest) is str and
             re.fullmatch('[0-9a-f]{64}', selected_digest) is not None, 'selection_digest')
        identifiers(available_capabilities, 'available_capabilities')
        if selected_digest not in registry:
            return {**boundary, 'status': 'unsupported', 'reason': 'definition_unavailable',
                    'selected_digest': selected_digest}
        manifest = registry[selected_digest]
        need(digest(manifest) == selected_digest, 'definition_digest_mismatch')
        validate_manifest(manifest)
        validate_values(manifest, values)
        missing_capabilities = sorted(set(manifest['capabilities']) - set(available_capabilities))
        consequences = ['unsupported'] if missing_capabilities else []
        findings = []
        for req in manifest['requirements']:
            known, value, missing = _evaluate(req['predicate'], manifest, values)
            truth = ('true' if value else 'false') if known else 'unknown'
            consequence = ('satisfied' if value else req['on_false']) if known else req['on_unknown']
            consequences.append(consequence)
            findings.append({'id': req['id'], 'truth': truth, 'consequence': consequence,
                             'dependencies': sorted(req['requires']), 'unresolved_inputs': missing,
                             'admission_refs': list(req['admission_refs'])})
        status = next((s for s in ['invalid', 'unsupported', 'unresolved'] if s in consequences),
                      'requirements_satisfied')
        return {**boundary, 'status': status, 'selected_digest': selected_digest,
                'method_id': manifest['method_id'], 'version': manifest['version'],
                'values_sha256': digest(values), 'findings': findings,
                'missing_capabilities': missing_capabilities,
                'input_declarations': json.loads(canonical(manifest['inputs'])),
                'residual_prerequisites': list(manifest['residual_prerequisites'])}
    except (Invalid, ValueError, TypeError, KeyError, RecursionError, OverflowError) as exc:
        return {**boundary, 'status': 'invalid', 'reason': str(exc)[:250]}
