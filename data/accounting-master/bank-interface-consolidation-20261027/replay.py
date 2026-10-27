"""Replay retained bank exchanges from a locked copy; never generate expectations."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
read = lambda p: json.loads(p.read_text())
digest = lambda p: sha256(p.read_bytes()).hexdigest()

def write(path, value):
    with path.open('x') as f:
        json.dump(value, f, indent=2); f.write(chr(10))

def module(path, name):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

def component(unit, output):
    folder = ROOT / unit['folder']
    native = module(folder / 'verify_exchanges.py', 'bank_replay_' + unit['id'].replace('-', '_'))
    a = native.Auditor(folder / unit['attempt'])
    before = digest(folder / unit['attempt'] / 'portable-exchanges.json')
    a.audit('sources_schemas_input_snapshots', a.source_checks)
    shape = a.shape if unit['id'] == 'bank-assessment' else a.record_shape
    for h, record in a.reg.items():
        a.audit('record:' + record['key'], lambda h=h, record=record: shape(record, h))
    a.audit('reference_closure', lambda: a.closure(list(a.alias.values())))
    if unit['id'] == 'bank-assessment':
        for case in a.packet['cases']:
            a.audit('independent:' + case['id'], lambda case=case: a.output(case['operation'], case['input_ref'], a.body(case['output_ref'])))
        for exchange in a.packet['exchanges']:
            a.audit('exchange:' + exchange['id'], lambda exchange=exchange: a.response(exchange))
        for case in a.packet['crash_cuts']:
            a.audit('crash:' + case['id'], lambda case=case: a.crash(case))
        for case in a.packet['challenges']:
            a.audit('challenge:' + case['id'], lambda case=case: a.challenge(case))
        roles = {'publication', 'exact_replay', 'replay_before_freshness', 'lost_ack',
                 'lost_ack_exact_recovery', 'lost_ack_before_publication', 'lost_ack_retry_publication',
                 'identity_conflict', 'new_stale_request'}
        for case in a.packet['cases']:
            a.audit('exchange_coverage:' + case['id'], lambda case=case: native.need(
                {e['role'] for e in a.packet['exchanges'] if e['id'] == case['id'] or e['id'].startswith(case['id'] + '.')} >= roles,
                'missing_exchange_role'))
    else:
        for key, ref in a.alias.items():
            a.audit('alias:' + key, lambda key=key, ref=ref: native.require(a.record(ref)['key'] == key, 'alias_key_mismatch'))
        for exchange in a.packet['exchanges']:
            a.audit('exchange:' + exchange['id'], lambda exchange=exchange: a.exchange(exchange))
        for case in a.packet['recoveries']:
            a.audit('recovery:' + case['retry_without_commit'], lambda case=case: a.recovery(case))
        for case in a.packet['validation_challenges']:
            a.audit('challenge:' + case['id'], lambda case=case: a.challenge(case))
        a.audit('predecessor_closed_profile_refusals', a.offers)
        a.audit('method_and_period_coverage', a.coverage)
    failed = [r for r in a.checks if not r['passed']]
    assert digest(folder / unit['attempt'] / 'portable-exchanges.json') == before
    report = dict(unit=unit['id'], profile=unit['profile'], checks=a.checks, failures=failed,
                  exchanges=len(a.packet['exchanges']), historical_git_preservation='excluded, not replaced')
    write(output / (unit['id'] + '.json'), report)
    print(json.dumps(dict(unit=unit['id'], checks=len(a.checks), failures=len(failed), exchanges=report['exchanges'])), flush=True)
    return not failed

def exact_component(folder, output):
    successor = module(ROOT / folder / 'successor.py', 'bank_exact_replay')
    native = successor.n
    old = native.Auditor(successor.prior.ATT)
    cases, controls = [], []

    def need(ok, code):
        if not ok:
            raise AssertionError(code)

    def outcome(fn):
        try:
            fn(); return 'accepted'
        except native.Refusal as exc:
            return exc.code

    def walk(value, mapping):
        if isinstance(value, dict):
            if set(value) == {'kind', 'schema', 'digest'}:
                return deepcopy(mapping.get(value['digest'], value))
            return {k: native.unique(walk(v, mapping)) if k == 'dependency_refs' else walk(v, mapping) for k, v in value.items()}
        if isinstance(value, list):
            return [walk(v, mapping) for v in value]
        return value

    for p in sorted((ROOT / folder / 'examples').glob('*.json')):
        packet = read(p)
        need(digest(ROOT / packet['base_packet']) == packet['base_packet_sha256'], 'base_packet_identity')
        a = successor.Auditor(packet)
        ex = packet['exchange']
        snapshot = native.sha(native.enc(dict(records=a.reg, blobs=a.blobs, exchange=ex)))
        for h, record in packet['records'].items():
            a.shape(record, h)
        request_outcome = outcome(lambda: a.request(ex['request_ref'], ex['submission_ref'], ex['world_before']))
        need(request_outcome == packet['expected_request_result'], 'request_outcome:' + p.stem)
        a.response(ex)
        if 'replay' in packet:
            a.response(packet['replay'])
        for key in ['accounting_heads', 'journals', 'unrelated_owners']:
            need(ex['world_before'][key] == ex['world_after'][key], 'accounting_mutation:' + key)
        if request_outcome == 'accepted':
            base = next(e for e in old.packet['exchanges'] if e['id'] == packet['template_id'] and e['role'] == 'publication')
            old_response = old.body(base['response_ref'])
            new_response = a.body(ex['response_ref'])
            need(new_response == walk(old_response, packet['reference_map']), 'full_response_correspondence:' + p.stem)
            expected_output = walk(old.body(old_response['payload']['result_refs'][0]), packet['reference_map'])
            need(a.body(new_response['payload']['result_refs'][0]) == expected_output, 'full_output_correspondence:' + p.stem)
            need(all(ex['world_after']['query_index'][k] == v for k, v in base['world_after']['query_index'].items()), 'old_queries_changed')
        else:
            need(ex['world_after'] == ex['world_before'], 'refusal_world_mutation')
        need(native.sha(native.enc(dict(records=a.reg, blobs=a.blobs, exchange=ex))) == snapshot, 'checker_mutation')
        cases.append(dict(case=p.stem, outcome=request_outcome, replay='replay' in packet,
                          complete_response_checked=True, accounting_unchanged=True))
        if p.stem in ['capital.final', 'loss.original', 'policy.describe']:
            def refused(label, fn, expected):
                actual = outcome(fn)
                need(actual == expected, label + ':' + actual)
                controls.append(dict(case=p.stem + ':' + label, actual=actual))
            bad = deepcopy(ex); bad['world_after']['journals'].append({'forged': 'posting'})
            refused('query_changes_accounting', lambda: a.response(bad), 'non_atomic_or_accounting_publication')
            bad = deepcopy(ex); bad['world_after']['query_index'].pop(a.identity(ex['request_ref']))
            refused('missing_query_index', lambda: a.response(bad), 'non_atomic_or_accounting_publication')
            bad = deepcopy(ex['world_before'])
            next(iter(bad['accounting_heads'].values()))['generation'] += 1
            refused('stale_head', lambda: a.request(ex['request_ref'], ex['submission_ref'], bad), 'stale_accounting_head')
            refused('legacy_request_on_successor', lambda: a.request(base['request_ref'], base['submission_ref'], base['world_after']), 'successor_request_schema')
    need(len(cases) == 63, 'saved_case_population')
    report = dict(unit='exact-time', cases=cases, controls=controls, exchanges=len(cases),
                  exact_replays=sum(r['replay'] for r in cases), failures=[],
                  comparison='full response/output; references substituted and dependency sets canonically ordered; no numeric normalization')
    write(output / 'exact-time.json', report)
    print(json.dumps(dict(unit='exact-time', cases=len(cases), exact_replays=report['exact_replays'], controls=len(controls))), flush=True)
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--component')
    parser.add_argument('--only')
    args = parser.parse_args()
    assert args.root.resolve() == ROOT
    manifest = read(ROOT / 'bank-manifest.json')
    if args.component:
        ok = exact_component(manifest['exact_folder'], args.output) if args.component == 'exact-time' else component(
            next(u for u in manifest['units'] if u['id'] == args.component), args.output)
        raise SystemExit(0 if ok else 1)
    started = time.monotonic()
    args.output.mkdir(parents=True, exist_ok=False)
    def verify_inputs():
        for name, row in manifest['entries'].items():
            p = (ROOT / name).resolve()
            assert p.is_relative_to(ROOT) and digest(p) == row['sha256'], name
    verify_inputs()
    commands = []
    selected = [args.only] if args.only else [u['id'] for u in manifest['units']] + ['exact-time']
    env = dict(os.environ, CUDA_VISIBLE_DEVICES='-1', PYTHONDONTWRITEBYTECODE='1')
    env.pop('PYTHONPATH', None)
    for key in selected:
        command = [sys.executable, '-B', str(Path(__file__).resolve()), '--root', str(ROOT),
                   '--output', str(args.output), '--component', key]
        begin = time.monotonic()
        result = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True, timeout=240)
        (args.output / (key + '.log')).write_text(result.stdout + result.stderr)
        commands.append(dict(component=key, command=command, exit_code=result.returncode, wall_seconds=time.monotonic()-begin))
        print(result.stdout.strip() or json.dumps(dict(component=key, exit_code=result.returncode)), flush=True)
        if result.returncode:
            print(result.stderr[-1800:], flush=True)
    verify_inputs()
    passed = all(r['exit_code'] == 0 for r in commands)
    write(args.output / 'run-manifest.json', dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),
          command=sys.argv, components=commands, environment=sys.version,
          jsonschema_version=importlib.metadata.version('jsonschema'), cpu_gpu='CPU; GPU intentionally hidden',
          random_seeds='N/A deterministic', git_commit='unavailable; historical Git preservation not repeated',
          data_version=digest(ROOT/'bank-manifest.json'), wall_seconds=time.monotonic()-started,
          plan_file='docs/plans/accounting-bank-consolidation-20261027.md',
          result_file='data/accounting-master/bank-interface-consolidation-20261027/result.md',
          artifacts=[str(args.output)], passed=passed))
    write(args.output / 'checks.json', dict(passed=passed, copied_inputs_verified=len(manifest['entries']),
          components=selected, failures=[r['component'] for r in commands if r['exit_code']],
          historical_git_preservation_rerun=False, full_mc21_closed=False))
    print(json.dumps(dict(passed=passed, components=len(commands), copied_inputs=len(manifest['entries']))), flush=True)
    raise SystemExit(0 if passed else 1)

if __name__ == '__main__':
    main()
