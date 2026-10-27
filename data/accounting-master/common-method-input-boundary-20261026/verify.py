"""Independent expectations and protected native verifier comparisons."""
from collections import Counter
from copy import deepcopy
from datetime import date, datetime, timezone
import importlib.util
import json
import os
import subprocess
import sys
import time
from bridge import *
import method_requirement_text_v2 as authored


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + chr(10))


def check_boundary(value):
    for key in BOUNDARY:
        assert value[key] is False, (key, value[key])


def repin_plan(link, packet):
    link['manifest_digest'] = packet['plan']['manifest_digest']
    link['binding_plan_digest'] = core.digest(packet['plan'])


def mutate_raw(packet, change):
    p = deepcopy(packet)
    old = p['plan']['records']['basis']['raw_sha256']
    record = json.loads(p['blobs'][old])
    change(record['body'])
    raw = core.canonical(record)
    new = hash_bytes(raw)
    p['blobs'] = {k: v for k, v in p['blobs'].items() if k != old}
    p['blobs'][new] = raw
    p['plan']['records']['basis']['raw_sha256'] = new
    d = deepcopy(p['manifests'][p['plan']['manifest_digest']])
    for decl in d['inputs'].values():
        decl['source_ref'] = decl['source_ref'].replace(old, new)
    dk = core.digest(d)
    p['manifests'] = {dk: d}
    p['plan']['manifest_digest'] = dk
    return p


def main():
    started = time.monotonic()
    lock = json.loads((HERE / 'source-lock.json').read_text())
    for name, digest in lock['files'].items():
        assert hash_bytes((ROOT / name).read_bytes()) == digest, name
    sys.path.insert(0, str(ATTEMPT / 'inputs'))
    spec = importlib.util.spec_from_file_location('retained_bank_audit', ATTEMPT / 'inputs/verify_exchanges.py')
    native = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(native)
    native.ROOT = ROOT  # archived script's original path has moved into inputs/
    auditor = native.Auditor(ATTEMPT)
    bridge = Bridge()
    rows, examples, negatives = [], {}, []
    native_counts, link_counts, joint = Counter(), Counter(), Counter()
    selected = [e for e in bridge.exchanges.values()
                if bridge.record(e['request_ref'])['body']['operation'] == OP]
    for e in selected:
        auditor.response(e)
        response = bridge.record(e['response_ref'])['body']
        status = response.get('disposition', 'transport_unknown')
        native_counts[status] += 1
        for version in (1, 2, 3):
            link, packet = bridge.make(e['id'], version)
            result = bridge.assess(link, packet)
            check_boundary(result)
            binding = result['binding']
            check_boundary(binding)
            assert binding['status'] == 'bound', (e['id'], binding)
            check_boundary(binding['assessment'])
            values = {k: date.fromisoformat(v['value']) for k, v in binding['values'].items()}
            expected = (values['period_start'] < values['period_end'] and
                        values['period_start'] <= values['assessment_date'] < values['period_end'] and
                        values['assessment_date'] == values['state_date'])
            assert binding['assessment']['status'] == ('requirements_satisfied' if expected else 'invalid')
            definition = packet['manifests'][packet['plan']['manifest_digest']]
            exchange = {'profile': authored.EXCHANGE, 'definition': definition,
                        'selected_digest': core.digest(definition), 'values': binding['values'],
                        'available_capabilities': packet['available_capabilities']}
            text = authored.render(exchange)
            lowered = authored.lower(text)
            assert lowered == exchange
            assert authored.assess_exchange(lowered) == binding['assessment']
            link_counts[result['status']] += 1
            joint[(binding['assessment']['status'], status)] += 1
            rows.append({'id': e['id'], 'requirements_version': version,
                         'link_status': result['status'], 'link_reason': result.get('reason'),
                         'selected_status': binding['assessment']['status'],
                         'native_disposition': status,
                         'native_diagnostics': [d['code'] for d in response.get('diagnostics', [])],
                         'native_request_digest': e['request_ref']['digest'],
                         'manifest_digest': link['manifest_digest']})
            if version == 1 and e['id'] in ['capital.final', 'capital.unknown-applicability',
                    'adverse.wrong-period-end', 'request-adverse.zero-operation-budget',
                    'request-adverse.stale-accounting-head', 'request-adverse.wrong-signature']:
                examples[e['id']] = (link, packet, result, text)
    assert joint[('requirements_satisfied', 'rejected')] > 0
    assert joint[('requirements_satisfied', 'partial')] > 0
    assert joint[('requirements_satisfied', 'transport_unknown')] > 0
    link0, packet0 = bridge.make('capital.final')

    def negative(name, mutate, expected='invalid'):
        link, packet = deepcopy(link0), deepcopy(packet0)
        mutate(link, packet)
        result = bridge.assess(link, packet)
        check_boundary(result)
        assert result['status'] == expected, (name, result)
        negatives.append({'case': name, 'status': result['status'], 'reason': result.get('reason')})

    negative('extra-link-field', lambda l, p: l.update(extra=True))
    negative('wrong-link-version', lambda l, p: l.update(profile='NativeRequirementLink/2'))
    negative('wrong-request', lambda l, p: l.update(request_ref=bridge.exchanges['capital.final.conflict']['request_ref']))
    negative('wrong-submission', lambda l, p: l.update(submission_ref=bridge.exchanges['capital.final.conflict']['submission_ref']))
    negative('wrong-profile', lambda l, p: l['profile_ref'].update(digest='0' * 64))
    negative('wrong-signature', lambda l, p: l['signature_ref'].update(digest='0' * 64))
    negative('wrong-basis', lambda l, p: l['basis_ref'].update(digest='0' * 64))
    negative('wrong-context', lambda l, p: l['context_ref'].update(digest='0' * 64))
    negative('source-substitution', lambda l, p: l['input_sources'].update(state=l['input_sources']['basis']))
    negative('wrong-manifest-link', lambda l, p: l.update(manifest_digest='0' * 64))
    negative('stale-plan', lambda l, p: l.update(binding_plan_digest='0' * 64))
    negative('missing-blob', lambda l, p: p['blobs'].clear(), 'unsupported')
    negative('missing-manifest', lambda l, p: p['manifests'].clear(), 'unsupported')
    negative('missing-schema', lambda l, p: p['schemas'].clear(), 'unsupported')
    negative('wrong-blob-bytes', lambda l, p: p['blobs'].update({next(iter(p['blobs'])): b'{}'}))

    def alter_schema(link, packet, key, value):
        ref = packet['plan']['records']['basis']
        shape = deepcopy(packet['schemas'][ref['schema_digest']])
        shape['fields']['/body/assessment_date'][key] = value
        sk = core.digest(shape)
        packet['schemas'][sk] = shape
        ref['schema_digest'] = sk
        repin_plan(link, packet)
    negative('wrong-field-role', lambda l, p: alter_schema(l, p, 'role', 'assumption'))
    negative('wrong-field-context', lambda l, p: alter_schema(l, p, 'type',
             {'kind': 'date', 'context': {'bank_id': 'Other'}}))
    negative('wrong-field-type', lambda l, p: alter_schema(l, p, 'type',
             {'kind': 'text', 'context': {}}))

    def forged_definition(link, packet):
        definition = deepcopy(packet['manifests'][packet['plan']['manifest_digest']])
        definition['requirements'] = definition['requirements'][:1]
        key = core.digest(definition)
        packet['manifests'] = {key: definition}
        packet['plan']['manifest_digest'] = key
        repin_plan(link, packet)
    negative('weakened-manifest', forged_definition)
    unknowns = []
    for version in (1, 2, 3):
        link, packet = bridge.make('capital.final', version)
        packet['available_capabilities'] = []
        result = bridge.assess(link, packet)
        assert result['status'] == 'linked_selected_requirements'
        assert result['selected_status'] == 'unsupported'
        unknowns.append({'version': version, 'case': 'missing-capability', 'status': 'unsupported'})
        packet['available_capabilities'] = [CAPABILITY]
        missing = mutate_raw(packet, lambda body: body.pop('assessment_date'))
        assessed = binder.assess_bound(**missing)
        assert assessed['assessment']['status'] == 'unresolved'
        assert assessed['values']['assessment_date']['status'] == 'unknown'
        repin_plan(link, missing)
        assert bridge.assess(link, missing)['status'] == 'invalid'
        unknowns.append({'version': version, 'case': 'derived-missing-date', 'status': 'unresolved',
                         'native_link': 'invalid', 'evidence_mode': 'derived_mutation'})
        mixed = mutate_raw(missing, lambda body: body.update(period_start='2026-04-02'))
        mixed['available_capabilities'] = []
        assessed = binder.assess_bound(**mixed)['assessment']
        assert assessed['status'] == 'invalid'
        assert assessed['missing_capabilities'] == [CAPABILITY]
        assert {'invalid', 'unresolved'} <= {f['consequence'] for f in assessed['findings']}
        unknowns.append({'version': version, 'case': 'mixed-failure', 'status': 'invalid',
                         'missing_capability_preserved': True, 'unknown_findings_preserved': True})
    out = HERE / 'examples'
    out.mkdir(exist_ok=True)
    for name, (link, packet, result, text) in examples.items():
        folder = out / name
        folder.mkdir(exist_ok=True)
        dump(folder / 'link.json', link)
        dump(folder / 'packet.json', {**packet, 'blobs': {k: v.decode() for k, v in packet['blobs'].items()}})
        dump(folder / 'result.json', result)
        (folder / 'requirements.acc').write_text(text)
    dump(HERE / 'comparisons.json', rows)
    dump(HERE / 'negative-cases.json', negatives)
    dump(HERE / 'unknown-cases.json', unknowns)
    for name, digest in lock['files'].items():
        assert hash_bytes((ROOT / name).read_bytes()) == digest, name
    checks = {'passed': True, 'native_exchanges': len(selected), 'text_typed_cases': len(rows),
              'negative_cases': len(negatives), 'unknown_capability_cases': len(unknowns),
              'protected_files': len(lock['files']), 'native_dispositions': dict(native_counts),
              'link_statuses': dict(link_counts),
              'joint_statuses': [{'selected': a, 'native': b, 'count': n}
                                 for (a, b), n in sorted(joint.items())]}
    dump(HERE / 'checks.json', checks)
    manifest = {'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                'command': 'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/common-method-input-boundary-20261026/verify.py',
                'environment': sys.version, 'cpu_gpu': 'CPU; GPU intentionally hidden with CUDA_VISIBLE_DEVICES=-1',
                'data_version': hash_bytes((ATTEMPT / 'portable-exchanges.json').read_bytes()),
                'random_seeds': 'N/A deterministic engineering checks', 'wall_seconds': time.monotonic() - started,
                'plan_file': 'docs/plans/accounting-common-method-input-boundary-20261026.md',
                'result_file': str((HERE / 'result.md').relative_to(ROOT)),
                'artifacts': ['checks.json', 'comparisons.json', 'negative-cases.json', 'unknown-cases.json', 'examples/'],
                'timestamp_utc': datetime.now(timezone.utc).isoformat(),
                'source_lock_sha256': hash_bytes((HERE / 'source-lock.json').read_bytes()),
                'implementation_sha256': hash_bytes((HERE / 'bridge.py').read_bytes()),
                'verifier_sha256': hash_bytes(Path(__file__).read_bytes())}
    dump(HERE / 'run-manifest.json', manifest)
    print(json.dumps(checks))


if __name__ == '__main__':
    main()
