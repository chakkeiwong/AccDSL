"""Resolve two retained assessment references; never execute or post a method."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
from jsonschema import Draft202012Validator, FormatChecker
import company_world_envelope_v1 as world

core = world.core
ROOT = Path(__file__).resolve().parents[1]
PROFILE = 'SectorReferenceBinding/1'
WORLD_SHA256 = 'a048be2290e1d6631e40887f625d387608191c400e96b0bb5300f6c52fb73b2a'
FLAGS = {**world.FLAGS, 'selected_references_resolved': False, 'method_recomputed': False}
CATALOG = {
    'bank': {'directory': 'data/accounting-master/extended-method-exchanges-20261015/bank-assessment/attempt-03',
             'packet_sha256': 'e53feca755ab605ba89b6abdbf0a03ae363118be07a186fd8e9f8421b0db0c58',
             'schema_sha256': '9bf626291f43b3d6a5bf91468e27300ed3684b3229c1f26295d6d236438b347f',
             'case': 'capital.final'},
    'insurance': {'directory': 'data/accounting-master/extended-method-exchanges-20261015/insurance-assessment/attempt-02',
                  'packet_sha256': '2843f7e19eed935a9c29c83a559ca5af235b6eae3d8e91142675a4fd73da31f1',
                  'schema_sha256': 'eb122506a550838d5f8bcd437ec6b11b7dcd1f2268fc7350107218d44f3c2f50',
                  'case': 'route.full'}}


def load_native(sector):
    entry = CATALOG[sector]; folder = ROOT / entry['directory']
    values = []
    for name, field in [('portable-exchanges.json', 'packet_sha256'), ('record-schemas.json', 'schema_sha256')]:
        path = folder / name
        core.need(path.stat().st_size <= 32_000_000, 'native_file_size')
        raw = path.read_bytes()
        core.need(sha256(raw).hexdigest() == entry[field], 'native_' + field)
        values.append(json.loads(raw))
    return tuple(values)


def references(value, blob=False):
    if type(value) is dict:
        fields = {'kind', 'algorithm', 'digest', 'byte_length'} if blob else {'kind', 'schema', 'digest'}
        if set(value) == fields and (not blob or value['kind'] == 'blob'):
            yield value
        else:
            for child in value.values(): yield from references(child, blob)
    elif type(value) is list:
        for child in value: yield from references(child, blob)


def checked_blob(reference, index):
    core.need(reference['algorithm'] == 'sha256', 'blob_algorithm')
    digest = reference['digest']; core.need(digest in index, 'missing_blob')
    item = index[digest]; path = (ROOT / item['path']).resolve()
    core.need(path.is_relative_to(ROOT.resolve()), 'blob_outside_workspace')
    core.need(type(reference['byte_length']) is int and 0 <= reference['byte_length'] <= 128_000_000, 'blob_size_limit')
    core.need(item['byte_length'] == reference['byte_length'] == path.stat().st_size, 'blob_length')
    checksum = sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''): checksum.update(block)
    core.need(checksum.hexdigest() == digest, 'blob_digest')
    return {'path': item['path'], 'sha256': digest, 'byte_length': reference['byte_length']}


def resolve_closure(packet, schemas, roots):
    """Original portable identity and closed native body schemas, read only."""
    registry = packet['record_registry']; found = {}; active = set(); blobs = {}
    def visit(ref, depth=0):
        core.closed(ref, ['kind', 'schema', 'digest'], 'native_reference')
        digest = ref['digest']; core.need(digest in registry, 'missing_native_record')
        record = registry[digest]
        core.need((ref['kind'], ref['schema']) == (record['kind'], record['schema']), 'native_reference_type')
        core.need(digest not in active, 'native_reference_cycle')
        if digest in found: return
        core.need(depth <= 48 and len(found) + len(active) < 4096, 'native_closure_limit')
        core.closed(record, ['kind', 'schema', 'key', 'revision', 'body', 'dependencies'], 'native_record')
        core.need(type(record['revision']) is int and record['revision'] == 0, 'native_revision')
        world.text(record['key'], 'native_key')
        core.need(record['kind'] in schemas['schema_ids'] and record['schema'] == schemas['schema_ids'][record['kind']], 'native_schema')
        raw = ('accdsl.portable.v1/' + record['schema']).encode() + b'\0' + core.canonical(record)
        core.need(sha256(raw).hexdigest() == digest, 'native_record_digest')
        errors = Draft202012Validator(schemas['$defs'][record['kind']], format_checker=FormatChecker()).iter_errors(record['body'])
        core.need(next(errors, None) is None, 'native_body_schema')
        deps = {core.canonical(item): item for item in references(record['body'])}
        core.need(record['dependencies'] == [deps[key] for key in sorted(deps)], 'native_dependency_list')
        active.add(digest)
        for child in record['dependencies']: visit(child, depth + 1)
        for blob in references(record['body'], blob=True):
            if blob['digest'] not in blobs:
                blobs[blob['digest']] = checked_blob(blob, packet['blobs'])
            else:
                core.need(blobs[blob['digest']]['byte_length'] == blob['byte_length'], 'blob_length')
        active.remove(digest); found[digest] = deepcopy(record)
    for root in roots: visit(root)
    return {key: found[key] for key in sorted(found)}, {key: blobs[key] for key in sorted(blobs)}


def native_selection(packet, sector, case_id):
    core.need(case_id == CATALOG[sector]['case'], 'unsupported_native_case')
    cases = [row for row in packet['cases'] if row['id'] == case_id]
    core.need(len(cases) == 1, 'native_case_identity')
    case = cases[0]; registry = packet['record_registry']
    def body(ref): return registry[ref['digest']]['body']
    request_ref = case['request_ref']; request = body(request_ref)
    basis_ref = case['input_ref'] if sector == 'bank' else case['basis_ref']
    basis = body(basis_ref)
    state_ref = basis['state_ref'] if sector == 'bank' else basis['expected_head']
    source_ref = basis['rule_ref'] if sector == 'bank' else basis['source_ref']
    return {'request': request_ref, 'basis': basis_ref, 'state': state_ref, 'source': source_ref,
            'view': basis['view_ref'], 'context': basis['context_ref'], 'profile': request['profile_ref']}


def bind(request):
    try:
        core.need(sha256(Path(world.__file__).read_bytes()).hexdigest() == WORLD_SHA256, 'world_dependency_hash')
        core.closed(request, ['profile', 'world', 'component_id', 'case_id'], 'sector_binding')
        core.need(request['profile'] == PROFILE, 'binding_profile')
        world.validate(request['world']); world.text(request['component_id'], 'component_id')
        world.text(request['case_id'], 'case_id')
        core.need(request['component_id'] in request['world']['components'], 'missing_component')
        component = request['world']['components'][request['component_id']]
        sector = component['sector']; core.need(sector in CATALOG, 'unsupported_sector_projection')
        core.need(request['case_id'] == CATALOG[sector]['case'], 'unsupported_native_case')
        packet, schemas = load_native(sector)
        selection = native_selection(packet, sector, request['case_id'])
        def body(role): return packet['record_registry'][selection[role]['digest']]['body']
        book = request['world']['books'][component['owner']]; context = body('context')
        for field, role in [('state_ref','state'), ('source_ref','source'), ('view_ref','view')]:
            core.need(component[field] == selection[role]['digest'], 'native_' + field + '_binding')
        entity = context['bank_id'] if sector == 'bank' else context['entity_id']
        core.need(book['entity'] == entity and book['book'] == context['book_id'], 'native_owner_binding')
        core.need(book['currency'] == context['currency'], 'native_currency_binding')
        core.need(body('profile')['profile_id'] == component['profile'], 'native_profile_binding')
        core.need(body('profile')['accounting_effect'] == 'none', 'native_assessment_effect')
        core.need(body('state')['context_ref'] == selection['context'], 'native_state_context')
        core.need(body('request')['view_ref'] == selection['view'], 'native_request_view')
        if sector == 'bank':
            core.need(body('request')['arguments']['value']['basis_ref'] == selection['basis'], 'native_request_basis')
            core.need(body('request')['expected_head']['state_ref'] == selection['state'], 'native_request_head')
        else:
            core.need(body('request')['basis_ref'] == selection['basis'], 'native_request_basis')
            core.need(body('request')['expected_head'] == selection['state'], 'native_request_head')
        records, blobs = resolve_closure(packet, schemas, list(selection.values()))
        return {'profile': PROFILE, **FLAGS, 'selected_references_resolved': True,
                'status': 'assessment_reference_resolved', 'request_sha256': core.digest(request),
                'world': deepcopy(request['world']), 'selection': selection,
                'native_context': deepcopy(context), 'native_state_kind': selection['state']['kind'],
                'native_state_contains_balances': sector == 'bank',
                'native_accounting_effect': 'none', 'component_status': component['status'],
                'unresolved_obligations': deepcopy(request['world']['obligations']),
                'records': records, 'blobs': blobs, 'native_identity': deepcopy(CATALOG[sector]),
                'scope': 'Two retained assessment cases; selected references only; no common ledger, method execution, source admission or posting',
                'implementation_sha256': sha256(Path(__file__).read_bytes()).hexdigest(), 'world_sha256': WORLD_SHA256}
    except Exception as exc:
        return {'profile': PROFILE, **FLAGS, 'status': 'invalid', 'reason': str(exc)[:350]}


def verify(request, result):
    try: return core.canonical(bind(request)) == core.canonical(result)
    except Exception: return False
