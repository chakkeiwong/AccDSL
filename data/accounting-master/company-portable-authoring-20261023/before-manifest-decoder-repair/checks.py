"""Deterministic conformance checks with explicit semantic counterexamples."""
from copy import deepcopy
from hashlib import sha256
import json
from assemble import assemble
from portable import Builder, canonical, decode, dependencies, legacy_bytes, legacy_digest, record_digest
from validate import validate


def rehash(packet):
    old = packet['record_registry']; new = {}; visiting = set()
    def walk(value):
        if type(value) is dict:
            if set(value) == {'kind', 'schema', 'digest'}:
                return visit(value)
            return {k: walk(v) for k, v in value.items()}
        if type(value) is list:
            return [walk(v) for v in value]
        return value
    def visit(ref):
        key = ref['digest']
        if key in visiting:
            raise ValueError('test cannot rehash a cyclic graph')
        visiting.add(key)
        record = deepcopy(old[key]); record['body'] = walk(record['body'])
        record['dependencies'] = dependencies(record['body'])
        h = record_digest(record); new[h] = record
        visiting.remove(key)
        return {**ref, 'digest': h}
    root = visit(packet['root_ref'])
    return {**packet, 'root_ref': root, 'record_registry': new}


def conformance(raw, source, trusted):
    checks, witnesses = [], {}
    def check(name, value):
        checks.append({'name': name, 'passed': bool(value)})
    def refused(name, fn):
        try:
            fn(); accepted = True
        except Exception:
            accepted = False
        check(name, not accepted)
    packet, blobs = assemble(raw, source, trusted['family'])
    before = canonical(packet)
    binding = validate(packet, blobs, trusted)
    replay = validate(packet, blobs, trusted, True)
    check('content_binding_passes', binding['status'] == 'validated_synthetic_authoring')
    check('trusted_replay_passes', replay['status'] == 'validated_synthetic_authoring')
    check('binding_is_not_semantic_admission', binding.get('verification_level') == 'content_binding_only' and binding.get('replayed_family_members') == 0)
    check('six_members_two_partial', replay.get('members') == 6 and replay.get('partial_members') == 2)
    check('all_admissions_remain_false', replay.get('admission') and all(x is False for x in replay['admission'].values()))
    check('validator_preserves_input', before == canonical(packet))
    check('portable_packet_json_roundtrip', canonical(decode(canonical(packet))) == canonical(packet))
    for role, original in raw.items():
        check('original_bytes_'+role, sha256(original).hexdigest() in blobs and blobs[sha256(original).hexdigest()] == original)
    for i, bad in enumerate([b'{"a":1,"a":2}', b'{"a":{"b":1,"b":2}}',
        b'{"x":1.0}', b'{"x":1e2}', b'{"x":NaN}', b'{"x":Infinity}',
        b'{"x":"\ud800"}', b'{"x":"\udfff"}', b'\xff', b'{"\u00e9":1}',
        b'\xef\xbb\xbf{}']):
        refused('strict_decode_rejects_'+str(i), lambda bad=bad: decode(bad))
    check('boolean_not_integer_identity', legacy_digest({'x': True}) != legacy_digest({'x': 1}))
    check('large_integer_preserved', decode(b'{"x":9007199254740993}')['x'] == 9007199254740993)
    a = b'{"name":"Caf\u00e9"}'; z = '{"name":"Café"}'.encode()
    b = Builder(); r1 = b.imported('u', a, 'UnicodeFixture/1'); r2 = b.imported('u', z, 'UnicodeFixture/1')
    d1, d2 = b.records[r1['digest']]['body'], b.records[r2['digest']]['body']
    check('unicode_same_decoded_draft', d1['decoded_sha256'] == d2['decoded_sha256'])
    check('unicode_same_portable_content', d1['content_ref'] == d2['content_ref'])
    check('unicode_distinct_raw_imports', r1 != r2 and d1['raw_blob'] != d2['raw_blob'])
    r3 = b.imported('u', '{"name":"Café"}'.encode(), 'UnicodeFixture/1')
    check('unicode_no_normalization', b.records[r3['digest']]['body']['content_ref'] != d1['content_ref'])
    check('surrogate_pair_same_scalar', decode(b'{"x":"\ud83d\ude00"}') == {'x': '😀'})
    def bad_packet(name, edit, rewrite=False):
        p, bs = deepcopy(packet), dict(blobs); edit(p, bs)
        if rewrite:
            p = rehash(p)
        verdict = validate(p, bs, trusted)
        witnesses[name] = verdict; check(name, verdict['status'] == 'invalid')
    root = lambda p: p['record_registry'][p['root_ref']['digest']]['body']
    bad_packet('missing_record', lambda p, bs: p['record_registry'].pop(root(p)['family_ref']['digest']))
    bad_packet('missing_blob', lambda p, bs: bs.pop(next(iter(bs))))
    bad_packet('altered_blob', lambda p, bs: bs.__setitem__(next(iter(bs)), b'{}'))
    bad_packet('orphan_record', lambda p, bs: p['record_registry'].__setitem__('f'*64, deepcopy(next(iter(p['record_registry'].values())))))
    bad_packet('unmanifested_blob', lambda p, bs: bs.__setitem__(sha256(b'extra').hexdigest(), b'extra'))
    bad_packet('manifest_boolean_length', lambda p, bs: next(iter(p['blobs'].values())).__setitem__('byte_length', True))
    bad_packet('extra_packet_field', lambda p, bs: p.__setitem__('execute', 'untrusted.py'))
    bad_packet('wrong_reference_kind', lambda p, bs: root(p)['family_ref'].__setitem__('kind', 'Member'), True)
    bad_packet('false_temporal_admission', lambda p, bs: root(p)['admission'].__setitem__('temporal_admission', True), True)
    bad_packet('false_durability', lambda p, bs: root(p)['admission'].__setitem__('physical_durability', True), True)
    def alter(kind, field, value):
        def edit(p, bs):
            next(r for r in p['record_registry'].values() if r['kind'] == kind)['body'][field] = value
        return edit
    bad_packet('renamed_member_mismatch', alter('Member', 'name', 'forged-name'), True)
    bad_packet('changed_annual_period', alter('AnnualOutcome', 'period', {'start': '2000-01-01', 'end_exclusive': '2001-01-01'}), True)
    bad_packet('changed_dependency_names', alter('ExpressionPolicy', 'declared_inputs', {}), True)
    bad_packet('false_checkpoint_index', alter('Recovery', 'next_index', True), True)
    bad_packet('missing_dependency_list', lambda p, bs: p['record_registry'][p['root_ref']['digest']].__setitem__('dependencies', []))
    bad_packet('wrong_content_decoder', alter('DraftContent', 'decoder', 'execute-python'), True)
    bad_packet('changed_import_pointer', alter('DraftImport', 'pointer', '/missing'), True)
    # Recompute every affected identity. A hash-consistent cash lie must still fail execution.
    forged = {k: decode(v) for k, v in raw.items()}
    member = forged['family_result']['members'][0]
    year = member['result']['years'][-1]
    year['report']['lines']['cash']['value'] = '0/1'
    year['result_sha256'] = legacy_digest({k: v for k, v in year.items() if k != 'result_sha256'})
    member['result_sha256'] = legacy_digest(member['result'])
    forged['recovery_response']['checkpoint']['completed'] = deepcopy(forged['family_result']['members'])
    forged['recovery_response']['family_result'] = deepcopy(forged['family_result'])
    forged_raw = {k: legacy_bytes(v) for k, v in forged.items()}
    fp, fb = assemble(forged_raw, source, trusted['family'])
    fbind = validate(fp, fb, trusted); freplay = validate(fp, fb, trusted, True)
    witnesses['forged_cash'] = {'binding': fbind, 'replay': freplay}
    check('rehashed_cash_can_pass_content_binding', fbind['status'] == 'validated_synthetic_authoring')
    check('rehashed_cash_rejected_by_execution', freplay['status'] == 'invalid' and 'family trusted replay' in freplay.get('detail', ''))
    # Representation can vary while exact decoded model content stays fixed.
    spaced = dict(raw)
    spaced['program'] = json.dumps(decode(raw['program']), indent=4, ensure_ascii=False).encode()
    sp, sb = assemble(spaced, source, trusted['family'])
    check('alternate_whitespace_import_replays', validate(sp, sb, trusted, True)['status'] == 'validated_synthetic_authoring')
    def original_content(p, role):
        return next(r['body']['content_ref'] for r in p['record_registry'].values()
            if r['kind'] == 'DraftImport' and r['body']['role'] == role)
    check('whitespace_same_content_record', original_content(packet, 'program') == original_content(sp, 'program'))
    check('whitespace_different_exchange_identity', packet['root_ref'] != sp['root_ref'])
    # Equal paths under distinct names retain their authored multiplicity.
    duplicate = {k: decode(v) for k, v in raw.items()}
    extra = deepcopy(duplicate['family_draft']['members'][0]); extra['id'] = 'same_path_different_name'
    duplicate['family_draft']['members'].append(extra)
    extra_result = deepcopy(duplicate['family_result']['members'][0]); extra_result['id'] = extra['id']
    duplicate['family_result']['members'].append(extra_result)
    duplicate['family_result']['family_sha256'] = legacy_digest(duplicate['family_draft'])
    duplicate['recovery_fixture'] = deepcopy(duplicate['family_draft'])
    dr = duplicate['recovery_response']
    dr['checkpoint']['family_sha256'] = legacy_digest(duplicate['family_draft'])
    dr['checkpoint']['completed'] = deepcopy(duplicate['family_result']['members'])
    dr['checkpoint']['next_index'] = 7; dr['newly_evaluated_members'] += 1
    dr['family_result'] = deepcopy(duplicate['family_result'])
    dp, db = assemble({k: legacy_bytes(v) for k, v in duplicate.items()}, source, trusted['family'])
    dv = validate(dp, db, trusted, True)
    witnesses['duplicate_path_distinct_name'] = dv
    check('duplicate_path_names_preserved', dv['status'] == 'validated_synthetic_authoring' and dv.get('members') == 7)
    check('duplicate_paths_do_not_gain_probability', dv.get('admission', {}).get('forecast_admission') is False)
    # Unknowns remain present; there is no partial-to-complete coercion.
    result_values = decode(raw['family_result'])
    unknown = next(m for m in result_values['members'] if m['id'] == 'unknown_middle_payroll')
    check('unknown_middle_year_is_partial', unknown['status'] == 'partial' and bool(unknown['result']['unexecuted']))
    partial_records = [r['body'] for r in packet['record_registry'].values()
                       if r['kind'] == 'AnnualOutcome' and r['body']['outcome'] == 'partial']
    check('partial_records_have_no_closing_memory', len(partial_records) == 2 and all(r['closing_memory_ref'] is None for r in partial_records))
    # External callers must supply the same trusted method descriptor.
    altered_trust = dict(trusted); altered_trust['method'] = {**trusted['method'], 'extra.py': 'f'*64}
    check('changed_caller_method_rejected', validate(packet, blobs, altered_trust)['status'] == 'invalid')
    check('wrong_source_bytes_rejected', validate(packet, {**blobs, root(packet)['source_blob']['digest']: source+b' '}, trusted)['status'] == 'invalid')
    return {'passed': all(x['passed'] for x in checks), 'checks': checks,
            'binding': binding, 'replay': replay, 'adverse': witnesses}, packet, blobs
