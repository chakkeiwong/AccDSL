"""Bounded successor index; never executes or republishes financial events."""
from copy import deepcopy
from hashlib import sha256
import json
import re

FORMAT = 'accdsl.insurance-component-request-index.v2'
ID = re.compile(r'[A-Za-z0-9_.:@/-]+', re.ASCII)


class Refusal(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')


def pair_key(client_id, request_id):
    for value in (client_id, request_id):
        if not isinstance(value, str) or ID.fullmatch(value) is None:
            raise Refusal('invalid_identity_field')
    return canonical([client_id, request_id]).decode('utf-8')


def checked_record(ref, registry, kind=None):
    if not isinstance(ref, dict) or set(ref) != {'kind', 'schema', 'digest'}:
        raise Refusal('invalid_reference')
    if not all(isinstance(ref[k], str) for k in ref):
        raise Refusal('invalid_reference')
    if re.fullmatch(r'[0-9a-f]{64}', ref['digest']) is None:
        raise Refusal('invalid_reference')
    if kind is not None and ref['kind'] != kind:
        raise Refusal('wrong_reference_kind')
    record = registry.get(ref['digest'])
    if not isinstance(record, dict):
        raise Refusal('missing_record')
    if record.get('kind') != ref['kind'] or record.get('schema') != ref['schema']:
        raise Refusal('reference_binding')
    digest = sha256(('accdsl.portable.v1/' + ref['schema']).encode() +
                    b'\x00' + canonical(record)).hexdigest()
    if digest != ref['digest']:
        raise Refusal('record_digest_mismatch')
    return record['body']


def request_pair(request_ref, registry, profile_ref):
    profile = checked_record(profile_ref, registry, 'Profile')
    if profile.get('profile_id') != 'InsuranceComponents/1':
        raise Refusal('unsupported_profile')
    request = checked_record(request_ref, registry, 'OperationRequest')
    if request_ref['schema'] != 'accdsl.insurance-components.operationrequest.v1':
        raise Refusal('unsupported_request_schema')
    if request.get('profile_ref') != profile_ref:
        raise Refusal('profile_mismatch')
    pair_key(request.get('client_id'), request.get('request_id'))
    return request['client_id'], request['request_id']


def checked_decision(entry, registry, profile_ref):
    names = {'request_ref', 'response_ref', 'output_ref', 'receipt_ref'}
    if not isinstance(entry, dict) or set(entry) != names:
        raise Refusal('incomplete_decision')
    pair = request_pair(entry['request_ref'], registry, profile_ref)
    response = checked_record(entry['response_ref'], registry, 'OperationResult')
    receipt = checked_record(entry['receipt_ref'], registry, 'Receipt')
    checked_record(entry['output_ref'], registry)
    if any(response.get(k) != entry[k] for k in ('request_ref', 'output_ref', 'receipt_ref')):
        raise Refusal('response_binding')
    if any(receipt.get(k) != entry[k] for k in ('request_ref', 'output_ref')):
        raise Refusal('receipt_binding')
    return pair


def migrate_legacy(legacy_index, retained_decisions, registry, profile_ref):
    """Return a new index or refuse; every input remains unchanged.

    retained_decisions is caller-supplied immutable decision history, not all
    proposed requests. Its completeness cannot be established by this helper.
    A collision anywhere in that supplied history refuses migration even if
    only one of the colliding entries survived in legacy_index.
    """
    if not isinstance(legacy_index, dict) or not isinstance(retained_decisions, list):
        raise Refusal('invalid_index_input')
    histories = {}
    entries = {}
    for entry in retained_decisions:
        pair = checked_decision(entry, registry, profile_ref)
        old_key = pair[0] + '/' + pair[1]
        key = pair_key(*pair)
        if old_key in histories and histories[old_key][0] != pair:
            raise Refusal('ambiguous_legacy_key')
        if key in entries and entries[key] != entry:
            raise Refusal('conflicting_decision_history')
        histories[old_key] = (pair, entry)
        entries[key] = deepcopy(entry)
    if set(histories) != set(legacy_index):
        raise Refusal('incomplete_index_history')
    for old_key, (_, entry) in histories.items():
        if legacy_index[old_key] != entry:
            raise Refusal('legacy_index_binding')
    # Validate even the empty history's profile; no unbound empty index.
    profile = checked_record(profile_ref, registry, 'Profile')
    if profile.get('profile_id') != 'InsuranceComponents/1':
        raise Refusal('unsupported_profile')
    return {'format': FORMAT, 'profile_ref': deepcopy(profile_ref),
            'entries': {key: entries[key] for key in sorted(entries)}}


def lookup(index, request_ref, registry):
    """Lookup only: 'absent' grants no permission to execute or publish."""
    if not isinstance(index, dict) or set(index) != {'format', 'profile_ref', 'entries'}:
        raise Refusal('invalid_index')
    if index['format'] != FORMAT or not isinstance(index['entries'], dict):
        raise Refusal('invalid_index')
    pair = request_pair(request_ref, registry, index['profile_ref'])
    key = pair_key(*pair)
    if key not in index['entries']:
        return {'disposition': 'absent', 'decision': None}
    entry = index['entries'][key]
    if checked_decision(entry, registry, index['profile_ref']) != pair:
        raise Refusal('index_key_binding')
    if entry['request_ref'] != request_ref:
        return {'disposition': 'identity_conflict', 'decision': None}
    return {'disposition': 'replay', 'decision': deepcopy(entry)}
