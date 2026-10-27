"""Typed references to legacy company drafts; no supplied code is executed."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import re

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('company_portable_admission',
    HERE.parent / 'company-path-admission-20261023/admission.py')
admission = importlib.util.module_from_spec(spec)
spec.loader.exec_module(admission)
canonical = admission.canonical
record_digest = admission.record_digest
dependencies = admission.dependencies
closed = admission.closed
PROFILE = 'CompanyPortableAuthoringDraft/1'
DECODER = 'strict-json-utf8-legacy-ascii-canonical/1'
KINDS = ['DraftContent', 'DraftImport', 'AnnualOutcome', 'Member', 'Family',
         'ExpressionPolicy', 'Recovery', 'AuthoringExchange']
IDS = {k: 'accdsl.companyauthoring.' + k.lower() + '.draft1' for k in KINDS}
FLAGS = {k: False for k in ['historical_admission', 'temporal_admission',
    'forecast_admission', 'real_behavior_evidence', 'physical_durability',
    'accounting_commit', 'normalized_language_ir']}


def legacy_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('utf-8')


def legacy_digest(value):
    return sha256(legacy_bytes(value)).hexdigest()


def strict_values(value):
    if value is None or type(value) in (bool, int):
        return
    if type(value) is str:
        value.encode('utf-8', errors='strict')
    elif type(value) is list:
        for item in value:
            strict_values(item)
    elif type(value) is dict:
        for key, item in value.items():
            if type(key) is not str or not key.isascii():
                raise ValueError('non-ASCII or non-string object key')
            strict_values(item)
    else:
        raise ValueError('unsupported JSON value type')


def decode(raw):
    if type(raw) is not bytes:
        raise ValueError('bytes required')
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise ValueError('duplicate JSON key')
            out[key] = value
        return out
    def reject(token):
        raise ValueError('non-exact JSON number: ' + token)
    value = json.loads(raw.decode('utf-8', errors='strict'),
        object_pairs_hook=pairs, parse_float=reject, parse_constant=reject)
    strict_values(value)
    return value


def select(value, pointer):
    if pointer == '':
        return deepcopy(value)
    if not isinstance(pointer, str) or not pointer.startswith('/'):
        raise ValueError('JSON pointer required')
    for token in pointer[1:].split('/'):
        if re.search(r'~(?![01])', token):
            raise ValueError('invalid pointer escape')
        token = token.replace('~1', '/').replace('~0', '~')
        if type(value) is list:
            if not re.fullmatch(r'0|[1-9][0-9]*', token):
                raise ValueError('canonical array index required')
            value = value[int(token)]
        else:
            value = value[token]
    return deepcopy(value)


def schemas():
    text = {'type': 'string', 'minLength': 1}
    h = {'type': 'string', 'pattern': '^[0-9a-f]{64}$'}
    nat = {'type': 'integer', 'minimum': 0}
    arr = lambda item: {'type': 'array', 'items': item}
    ref = lambda kind: closed({'kind': {'const': kind},
        'schema': {'const': IDS[kind]}, 'digest': h})
    nullable = lambda item: {'oneOf': [{'type': 'null'}, item]}
    blob = closed({'kind': {'const': 'blob'}, 'algorithm': {'const': 'sha256'},
                   'digest': h, 'byte_length': nat})
    period = closed({'start': {'type': 'string', 'format': 'date'},
                    'end_exclusive': {'type': 'string', 'format': 'date'}})
    common = closed({'source_sha256': h, 'opening_sha256': h,
                     'periods': arr(period)})
    imp = ref('DraftImport')
    defs = {}
    defs['DraftContent'] = closed({'decoder': {'const': DECODER},
        'declared_profile': text, 'canonical_blob': blob, 'decoded_sha256': h})
    defs['DraftImport'] = closed({'role': text, 'decoder': {'const': DECODER},
        'declared_profile': text, 'raw_blob': blob, 'decoded_sha256': h,
        'content_ref': ref('DraftContent'),
        'origin': {'enum': ['original_file', 'extracted_value']},
        'parent_ref': nullable(imp), 'pointer': {'type': 'string'}})
    defs['AnnualOutcome'] = closed({'index': nat, 'period': period,
        'year_ref': imp, 'report_ref': imp, 'outcome':
        {'enum': ['complete_conditional', 'partial']},
        'closing_memory_ref': nullable(imp), 'historical_admission': {'const': False}})
    defs['Member'] = closed({'name': text, 'path_ref': imp, 'result_ref': imp,
        'context_ref': imp, 'opening_sha256': h, 'year_refs': arr(ref('AnnualOutcome')),
        'unexecuted_ref': imp, 'status': {'enum': ['complete_conditional', 'partial']}})
    defs['Family'] = closed({'draft_ref': imp, 'result_ref': imp,
        'member_refs': arr(ref('Member')), 'common': common,
        'meaning': {'const': 'authored_exogenous_scenarios'},
        'weighting': {'const': 'unweighted'}, 'coverage': {'const': 'authored_members_only'}})
    defs['ExpressionPolicy'] = closed({**{k: imp for k in [
        'program_ref', 'base_policy_ref', 'parent_path_ref', 'output_map_ref',
        'evaluated_policy_ref', 'materialization_ref', 'child_path_ref', 'result_ref']},
        'declared_inputs': {'type': 'object', 'additionalProperties': arr(text)},
        'evaluated_inputs': {'type': 'object', 'additionalProperties': arr(text)},
        'matching_members': arr(ref('Member')), 'temporal_admission': {'const': False}})
    defs['Recovery'] = closed({'family_ref': ref('Family'),
        'fixture_ref': imp, 'method_ref': imp, 'checkpoint_ref': imp,
        'response_ref': imp, 'next_index': nat, 'completed_members': arr(ref('Member')),
        'physical_durability': {'const': False}, 'accounting_commit': {'const': False}})
    defs['AuthoringExchange'] = closed({'profile': {'const': PROFILE},
        'source_blob': blob, 'family_ref': ref('Family'),
        'expression_ref': ref('ExpressionPolicy'), 'recovery_ref': ref('Recovery'),
        'original_imports': arr(imp), 'admission': closed({k: {'const': v} for k, v in FLAGS.items()})})
    return {'schema_ids': IDS, '$defs': defs}


class Builder:
    def __init__(self):
        self.records, self.blobs, self.values = {}, {}, {}

    def blob(self, raw):
        h = sha256(raw).hexdigest()
        self.blobs[h] = raw
        return {'kind': 'blob', 'algorithm': 'sha256', 'digest': h, 'byte_length': len(raw)}

    def record(self, kind, key, body):
        item = {'kind': kind, 'schema': IDS[kind], 'key': key, 'revision': 0,
                'body': body, 'dependencies': dependencies(body)}
        strict_values(item)
        h = record_digest(item)
        self.records[h] = item
        return {'kind': kind, 'schema': IDS[kind], 'digest': h}

    def imported(self, role, raw, profile, parent=None, pointer=''):
        value = decode(raw)
        if parent is not None and canonical(value) != canonical(select(self.values[parent['digest']], pointer)):
            raise ValueError('extracted value differs from original bytes')
        content = self.record('DraftContent', 'content/'+legacy_digest(value), {
            'decoder': DECODER, 'declared_profile': profile,
            'canonical_blob': self.blob(canonical(value)), 'decoded_sha256': legacy_digest(value)})
        body = {'role': role, 'decoder': DECODER, 'declared_profile': profile,
            'raw_blob': self.blob(raw), 'decoded_sha256': legacy_digest(value),
            'content_ref': content,
            'origin': 'original_file' if parent is None else 'extracted_value',
            'parent_ref': parent, 'pointer': pointer}
        ref = self.record('DraftImport', role, body)
        self.values[ref['digest']] = value
        return ref

    def extract(self, role, parent, pointer, profile):
        value = select(self.values[parent['digest']], pointer)
        return self.imported(role, legacy_bytes(value), profile, parent, pointer)

    def packet(self, root):
        return {'profile': PROFILE, 'root_ref': root, 'record_registry': self.records,
            'blobs': {h: {'byte_length': len(raw)} for h, raw in sorted(self.blobs.items())}}
