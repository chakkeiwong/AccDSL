"""Conditional constructed-document readings into a frozen receivable program."""
from copy import deepcopy
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import json
import re
import context_chronology_v1 as chronology
import declared_receivable_lifecycle_v1 as life

core = life.core
PROFILE = 'ReceivableSourceContract/1'
FLAGS = {**life.FLAGS, 'historical_execution_established': False,
         'temporal_admission': False, 'real_source_admission': False}
PINS = {'context_chronology_v1.py': '64878e62fa8784f666017252208229cc86111a000219b6fa24da52239f6d1d62',
        'declared_receivable_lifecycle_v1.py': 'd16b7b53f1509aaecc3ad682b23b2e16e694a20b4412f6e0f692d524a9468672'}
READING_FIELDS = ['claim_id', 'customer', 'sale_event', 'issued', 'units', 'consideration', 'due']
MISSING = {'not_disclosed', 'unreadable', 'unresolved_meaning', 'withheld', 'not_applicable'}


def closed(value, keys, label): core.closed(value, keys, label)
def text(value, label): life.engine.text(value, label)
def protected():
    for name, expected in PINS.items():
        core.need(sha256((Path(__file__).parent / name).read_bytes()).hexdigest() == expected, 'source_dependency:' + name)
    life.protected()


def instant(value):
    text(value, 'instant')
    core.need(re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z', value) is not None, 'utc_instant_required')
    try: datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError: raise core.Invalid('invalid_utc_instant')


def pairs(items):
    result = {}
    for name, value in items:
        core.need(name not in result, 'duplicate_source_key'); result[name] = value
    return result


def forbidden_number(value): raise core.Invalid('source_numeric_literal_forbidden')


def validate_reading(value):
    closed(value, READING_FIELDS, 'claim_reading')
    for name in ['claim_id', 'customer', 'sale_event']: text(value[name], name)
    core.scalar(value['issued'], 'date')
    for name in ['units', 'consideration', 'due']:
        item = value[name]; core.need(type(item) is dict, 'reading_value')
        if item.get('status') == 'known':
            closed(item, ['status', 'value'], 'known_reading')
            scalar = core.scalar(item['value'], 'date' if name == 'due' else 'rational')
            if name != 'due': core.need(scalar >= 0, 'negative_source_amount')
        else:
            closed(item, ['status', 'reason'], 'missing_reading')
            core.need(item['status'] == 'unknown' and item['reason'] in MISSING, 'missing_reading_tag')


def prepare(request):
    protected(); life.engine.memory.bounded(request)
    closed(request, ['profile', 'template', 'documents', 'assertions', 'sale_bindings', 'view', 'mapping_premise'], 'source_contract')
    core.need(request['profile'] == PROFILE, 'source_contract_profile')
    text(request['mapping_premise'], 'mapping_premise'); life.validate(request['template'])
    view = request['view']; closed(view, ['mode', 'cutoff', 'system_as_of'], 'source_view')
    core.need(view['mode'] in ['original', 'latest_available'], 'source_view_mode')
    instant(view['cutoff']); instant(view['system_as_of'])
    documents = request['documents']
    core.need(type(documents) is dict and 0 < len(documents) <= 32, 'document_population')
    for digest, document in documents.items():
        closed(document, ['content', 'origin', 'available', 'ingested'], 'constructed_document')
        core.need(document['origin'] == 'constructed_fixture', 'constructed_scope_only')
        core.need(type(document['content']) is str, 'source_text')
        core.need(sha256(document['content'].encode('utf-8')).hexdigest() == digest, 'document_digest')
        for field in ['available', 'ingested']:
            if document[field] != 'unknown': instant(document[field])
    assertions = request['assertions']
    core.need(type(assertions) is list and 0 < len(assertions) <= 128, 'assertion_population')
    book_context = request['template']['opening']['context']
    expected_context = {key: book_context[key] for key in ['entity', 'book', 'currency']}
    expected_context.update(basis='synthetic_declared_sale', unit='currency_unit', calendar='gregorian')
    rows, identity_by_lineage, id_records, timing_unknown = [], {}, {}, []
    for assertion in assertions:
        closed(assertion, ['id', 'lineage', 'supersedes', 'context', 'span', 'reading'], 'source_assertion')
        text(assertion['id'], 'assertion_id'); text(assertion['lineage'], 'lineage')
        core.need(assertion['id'] not in id_records, 'duplicate_assertion')
        id_records[assertion['id']] = assertion
        core.identifiers(assertion['supersedes'], 'supersedes')
        core.need(assertion['context'] == expected_context, 'assertion_context')
        span = assertion['span']; closed(span, ['document', 'start', 'end_exclusive', 'sha256'], 'source_span')
        core.need(span['document'] in documents, 'source_document_missing')
        document = documents[span['document']]; raw = document['content'].encode('utf-8')
        start, end = span['start'], span['end_exclusive']
        core.need(type(start) is int and type(end) is int and 0 <= start < end <= len(raw), 'source_span_bounds')
        selected = raw[start:end]
        core.need(sha256(selected).hexdigest() == span['sha256'], 'source_span_digest')
        decoded = json.loads(selected.decode('utf-8'), object_pairs_hook=pairs,
                             parse_float=forbidden_number, parse_int=forbidden_number, parse_constant=forbidden_number)
        core.need(core.canonical(decoded) == core.canonical(assertion['reading']), 'source_reading_mismatch')
        reading = assertion['reading']; validate_reading(reading)
        identity = tuple(reading[k] for k in ['claim_id', 'customer', 'sale_event', 'issued'])
        lineage = assertion['lineage']
        core.need(lineage not in identity_by_lineage or identity_by_lineage[lineage] == identity, 'revision_claim_identity')
        identity_by_lineage[lineage] = identity
        if 'unknown' in [document['available'], document['ingested']]: timing_unknown.append(assertion['id'])
        rows.append({'id': assertion['id'], 'source': span['document'], 'supersedes': assertion['supersedes'],
                     'lineage': lineage, 'context': assertion['context'], 'concept': 'identified_credit_sale',
                     'period': {'at': reading['issued']}, 'available': document['available'] if document['ingested'] != 'unknown' else 'unknown',
                     'ingested': document['ingested'], 'historical_byte_vintage': 'unknown'})
    core.need(len({i[0] for i in identity_by_lineage.values()}) == len(identity_by_lineage), 'duplicate_claim_lineage')
    selection = chronology.select_evidence(rows, view['cutoff'], mode=view['mode'],
                                           system_as_of=view['system_as_of'], require_known_bytes=False)
    for assertion in assertions:
        available = documents[assertion['span']['document']]['available']
        for parent_id in assertion['supersedes']:
            parent = id_records[parent_id]
            earlier = documents[parent['span']['document']]['available']
            if 'unknown' not in (available, earlier):
                core.need(earlier <= available, 'supersession_availability_order')
    bindings = request['sale_bindings']; core.need(type(bindings) is dict, 'sale_bindings')
    sales = [c for c in request['template']['commands'] if c.get('kind') == 'event' and c.get('method_key') == 'sale']
    sale_ids = [c['event']['id'] for c in sales]
    core.need(len(set(sale_ids)) == len(sale_ids), 'duplicate_sale_event')
    core.need(set(bindings) == set(sale_ids), 'complete_sale_bindings')
    core.need(all(type(v) is str and v in identity_by_lineage for v in bindings.values()), 'unknown_sale_lineage')
    core.need(len(set(bindings.values())) == len(bindings), 'lineage_used_twice')
    return selection, id_records, identity_by_lineage, timing_unknown


def compile_program(request):
    try:
        selection, assertions, identities, timing_unknown = prepare(request)
        result = {'profile': PROFILE, **FLAGS, 'request_sha256': core.digest(request),
                  'source_evidence': deepcopy({k: request[k] for k in ['documents','assertions','view','mapping_premise']}),
                  'selection': selection, 'implementation_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
                  'dependency_sha256': deepcopy(PINS), 'source_admission_basis': 'constructed_sources_and_supplied_timestamps_only',
                  'revision_semantics': 'Reconstruct a separate full history from the same opening; never amend the prior book'}
        missing, selected = [], {}
        for event_id, lineage in request['sale_bindings'].items():
            candidates = [row['id'] for row in selection['selected'] if row['lineage'] == lineage]
            uncertain = [key for key in timing_unknown if assertions[key]['lineage'] == lineage]
            if uncertain: missing.append({'event':event_id,'reason':'assertion_timing_unknown','assertions':uncertain})
            elif len(candidates) != 1:
                missing.append({'event':event_id,'reason':'conflicting_assertions' if candidates else 'source_unavailable', 'assertions':candidates})
            else:
                item = assertions[candidates[0]]; selected[event_id] = item
                for name in ['units','consideration','due']:
                    if item['reading'][name]['status'] == 'unknown':
                        missing.append({'event':event_id,'reason':'source_value_unknown','field':name,'missingness':item['reading'][name]['reason']})
        if missing: return {**result, 'status':'unresolved', 'unresolved':missing}
        program = deepcopy(request['template']); lineage = {}
        for command in program['commands']:
            if command.get('kind') != 'event' or command.get('method_key') != 'sale': continue
            event = command['event']; assertion = selected[event['id']]; reading = assertion['reading']
            core.need(event['id'] == reading['sale_event'] and event['date'] == reading['issued'], 'sale_event_source_identity')
            core.need(set(event['inputs']) == set(life.event_types(program['opening'], 'sale')), 'sale_template_fields')
            for name in ['claim_id','customer','due','units','consideration']:
                value = reading[name] if name in ['claim_id','customer'] else reading[name]['value']
                event['inputs'][name]['value'] = life.engine.known(value)
                event['inputs'][name]['provenance'] = 'Constructed assertion:' + assertion['id'] + ':' + assertion['span']['sha256'] + ':' + name
            lineage[event['id']] = deepcopy(assertion)
        life.validate(program)
        return {**result,'status':'compiled_conditional','program':program,'program_sha256':core.digest(program),
                'sale_lineage':lineage,'unresolved':[],
                'scope':'Constructed JSON sale readings only; receipts, assessments and policies remain declared assumptions'}
    except chronology.P06Error as exc:
        return {'profile':PROFILE,**FLAGS,'status':'invalid','reason':exc.code}
    except Exception as exc:
        return {'profile':PROFILE,**FLAGS,'status':'invalid','reason':str(exc)[:300]}


def run(request):
    compiled = compile_program(request)
    if compiled['status'] != 'compiled_conditional': return compiled
    return {**compiled, 'status':'conditional_execution', 'execution':life.run(compiled['program'])}


def verify(request, result):
    try: return core.canonical(run(request)) == core.canonical(result)
    except Exception: return False
