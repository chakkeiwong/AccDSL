"""Content binding and semantic replay are deliberately distinct verdicts."""
from copy import deepcopy
from hashlib import sha256
from assemble import FILES, assemble
from portable import (PROFILE, FLAGS, IDS, canonical, decode, legacy_digest,
                      select, schemas, strict_values, admission)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def same(a, b, message):
    require(canonical(a) == canonical(b), message)


def validate(packet, blobs, trusted, replay=False):
    try:
        strict_values(packet)
        require(set(packet) == {'profile', 'root_ref', 'record_registry', 'blobs'}, 'packet fields')
        require(packet['profile'] == PROFILE and packet['root_ref']['kind'] == 'AuthoringExchange', 'root profile')
        records = packet['record_registry']
        structural = admission.validate_registry(records, [packet['root_ref']], schemas(), blobs)
        require(structural['status'] == 'validated', 'record closure: '+str(structural['errors']))
        require(set(structural['record_digests']) == set(records), 'orphan record')
        require(set(structural['blob_digests']) == set(packet['blobs']) == set(blobs), 'blob closure')
        for h, meta in packet['blobs'].items():
            require(set(meta) == {'byte_length'} and type(meta['byte_length']) is int and meta['byte_length'] == len(blobs[h]), 'blob manifest')
        root = records[packet['root_ref']['digest']]['body']
        getbody = lambda ref: records[ref['digest']]['body']
        get = lambda ref: decode(blobs[getbody(ref)['raw_blob']['digest']])
        imports, decoded = {}, {}
        for h, record in records.items():
            if record['kind'] != 'DraftImport':
                continue
            body = record['body']; value = decode(blobs[body['raw_blob']['digest']])
            require(body['decoded_sha256'] == legacy_digest(value), 'decoded legacy identity')
            content = getbody(body['content_ref'])
            require(content['declared_profile'] == body['declared_profile'] and content['decoder'] == body['decoder'], 'decoder/profile correspondence')
            require(content['decoded_sha256'] == body['decoded_sha256'], 'content identity')
            require(blobs[content['canonical_blob']['digest']] == canonical(value), 'canonical content bytes')
            if body['origin'] == 'original_file':
                require(body['parent_ref'] is None and body['pointer'] == '', 'original file origin')
                require(body['role'] not in imports, 'duplicate original role')
                imports[body['role']] = {'kind': 'DraftImport', 'schema': IDS['DraftImport'], 'digest': h}
            else:
                require(body['parent_ref'] is not None, 'extraction parent required')
                same(value, select(get(body['parent_ref']), body['pointer']), 'extraction mismatch')
            decoded[h] = value
        require(set(imports) == set(FILES), 'original import roles')
        same(root['original_imports'], list(imports[role] for role in FILES), 'root original imports')
        raw_files = {role: blobs[getbody(ref)['raw_blob']['digest']] for role, ref in imports.items()}
        values = {role: decoded[ref['digest']] for role, ref in imports.items()}
        source = blobs[root['source_blob']['digest']]
        require(sha256(source).hexdigest() == values['family_draft']['common']['source_sha256'], 'source identity')
        expected_packet, expected_blobs = assemble(raw_files, source, trusted['family'])
        same(packet, expected_packet, 'typed record correspondence')
        require(blobs == expected_blobs, 'raw byte correspondence')
        draft = values['family_draft']; result = values['family_result']
        for authored, outcome in zip(draft['members'], result['members']):
            require(trusted['engine'].verify_chain(authored['path'], outcome['result']), 'path result chain')
        same(values['recovery_fixture'], draft, 'recovery family differs')
        same(values['recovery_method'], trusted['method'], 'untrusted recovery method descriptor')
        response = values['recovery_response']; cp = response['checkpoint']
        require(cp['family_sha256'] == legacy_digest(draft) and cp['source_sha256'] == sha256(source).hexdigest(), 'checkpoint dependencies')
        require(cp['engine_sha256'] == legacy_digest(trusted['method']), 'checkpoint method identity')
        same(cp['completed'], result['members'][:cp['next_index']], 'checkpoint prefix binding')
        require(cp['next_index'] == len(cp['completed']), 'checkpoint count')
        same(result, trusted['recovery'].final_result(draft, source, result['members']), 'family result fields')
        for key in ['validation_replayed_members', 'newly_evaluated_members']:
            require(type(response[key]) is int and response[key] >= 0, 'recovery work count type')
        require(response['validation_replayed_members'] + response['newly_evaluated_members'] == cp['next_index'], 'recovery work counts')
        require(type(cp['next_index']) is int, 'checkpoint index type')
        complete = cp['next_index'] == len(draft['members'])
        require(response['status'] == ('work_complete' if complete else 'work_suspended'), 'recovery completion meaning')
        same(response['family_result'], result if complete else None, 'recovery final result binding')
        require(response['physical_durability_established'] is False and response['accounting_commit'] is False, 'false publication admission')
        replayed = 0
        if replay:
            same(trusted['family'].execute(draft, source, trusted['engine']), result, 'family trusted replay')
            expression = getbody(root['expression_ref'])
            expected = trusted['materialize'](values['program'], get(expression['parent_path_ref']),
                values['base_policy'], get(expression['output_map_ref']), trusted['generate'])
            same(expected, values['expression_materialization'], 'expression trusted replay')
            require(expected['status'] == 'materialized_expression_policy', 'expression unresolved')
            child = expected['materialization']['path']
            same(trusted['engine'].wire(trusted['engine'].execute(child, source)), values['expression_result'], 'expression accounting replay')
            start = response['validation_replayed_members']
            before = deepcopy(cp); before['next_index'] = start; before['completed'] = before['completed'][:start]
            resumed = trusted['recovery'].resume(draft, source, cp['engine_sha256'], before,
                response['newly_evaluated_members'], trusted['engine'])
            same(resumed, response, 'recovery trusted replay')
            replayed = len(result['members'])
        return {'status': 'validated_synthetic_authoring',
            'verification_level': 'trusted_local_semantic_replay' if replay else 'content_binding_only',
            'records': len(records), 'blobs': len(blobs), 'members': len(result['members']),
            'partial_members': sum(m['status'] == 'partial' for m in result['members']),
            'replayed_family_members': replayed, 'admission': dict(FLAGS)}
    except Exception as exc:
        return {'status': 'invalid', 'detail': type(exc).__name__ + ': ' + str(exc).splitlines()[0][:500]}
