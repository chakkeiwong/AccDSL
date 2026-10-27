"""Fresh bounded compatibility checks; historical writers are never run."""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import ast
import gzip
import importlib.util
import json
import os
import platform
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = HERE.parent


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def module(name, path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def main():
    assert len(sys.argv) == 2, 'Supply a fresh attempt directory name'
    attempt = Path(sys.argv[1])
    assert len(attempt.parts) == 1 and attempt.name not in {'.', '..'}
    out = HERE / attempt
    out.mkdir(exist_ok=False)
    start = time.monotonic()
    checks, artifacts, lock = [], [], {}

    def check(label, actual, expected=True):
        checks.append({'label': label, 'passed': actual == expected})
        assert actual == expected, label

    def protect(path, expected=None):
        key = str(path.relative_to(ROOT))
        actual = digest(path)
        if expected is not None:
            check('locked identity:' + key, actual, expected)
        if key in lock:
            check('consistent identity:' + key, lock[key], actual)
        lock[key] = actual

    def save(name, value):
        path = out / (name + '.json.gz')
        payload = json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()
        path.write_bytes(gzip.compress(payload, mtime=0))
        check('roundtrip:' + name, json.loads(gzip.decompress(path.read_bytes())), value)
        artifacts.append({'path': path.name, 'sha256': digest(path), 'bytes': path.stat().st_size})

    success = False
    try:
        check('CPU-only declaration', os.environ.get('CUDA_VISIBLE_DEVICES'), '-1')
        import z3
        check('recorded solver environment', z3.get_version_string(), '4.16.0')
        for relative in ['registry.json', 'source-lock.json', 'compatibility.md', 'verify.py']:
            protect(HERE / relative)
        protect(ROOT / 'docs/plans/accounting-compatibility-reconciliation-20261028.md')
        for relative in ['source-lock.json', '../selected-term-program-20261027/attempt-01/source-lock.json',
                         '../selected-reading-history-20261027/attempt-01/source-lock.json']:
            source = (HERE / relative).resolve()
            protect(source)
            for name, expected in read(source).items():
                protect(ROOT / name, expected)
        registry = read(HERE / 'registry.json')
        rows = registry['interfaces']
        check('profile population', len(rows), 18)
        check('distinct profiles', len({row['profile'] for row in rows}), 18)
        ids = {row['id'] for row in rows}
        for row in rows:
            definitions = {n.name: ast.unparse(n.args) for n in ast.parse((ROOT / row['implementation']).read_text()).body
                           if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
            for name, signature in row['signatures'].items():
                check(row['profile'] + ':' + name + ' signature', definitions[name], signature)
            for field in ['inputs', 'context_and_clocks', 'effect_owner', 'outcomes', 'refusals', 'successors']:
                check(row['profile'] + ':' + field, isinstance(row[field], str) and bool(row[field]))
        for edge in registry['edges']:
            check('known edge:' + edge['source'] + ':' + edge['target'],
                  edge['source'] in ids | {'historical_core0'} and edge['target'] in ids)
        for source, target in [('term_event', 'term_program'), ('selected_reading', 'selected_history')]:
            check('delivered successor:' + source, any(e['source'] == source and e['target'] == target and e['status'] == 'implemented' for e in registry['edges']))

        program = module('current_compat_term_program', BASE / 'selected-term-program-20261027/program.py')
        term_dir = BASE / 'selected-term-program-20261027/attempt-01'
        for chart in ['alpha', 'beta']:
            paths = [term_dir / (chart + suffix) for suffix in ['-program.json', '-selection.json', '-result.json']]
            for path in paths:
                protect(path)
            body, selection_record, expected = [read(p) for p in paths]
            selection = selection_record['selection']
            check(chart + ':external selection identity', program.core.digest(selection), selection_record['expected_sha256'])
            before = deepcopy(body)
            result = program.execute(body, selection, selection_record['expected_sha256'])
            check(chart + ':complete native result', result, expected)
            check(chart + ':order-sensitive full result', program.source.full.p.order_digest(result), program.source.full.p.order_digest(expected))
            check(chart + ':request unchanged', body, before)
            check(chart + ':ten successful commands', result['successful_commands'], 10)
            book, roles = result['after']['book'], result['after']['roles']
            check(chart + ':cash from retained independent oracle', book['balances'][roles['cash']], '130/1')
            check(chart + ':claims from retained independent oracle', book['balances'][roles['receivables']], '0/1')
            check(chart + ':carried period', book['period'], {'start': '2028-01-01', 'end_exclusive': '2029-01-01'})
            save(chart + '-term-result', result)
            if chart == 'alpha':
                baseline, original, chosen = result, body, selection
        changed = deepcopy(original)
        changed['rule_sources']['carry'] += '\n'
        refused = program.execute(changed, chosen, program.core.digest(chosen))
        check('unselected source change rejected before execution', (refused['status'], refused['executed']), ('invalid_program', False))
        save('unselected-source-change', {'request': changed, 'selection': chosen, 'result': refused})
        for name, index, field, value in [('stale-state', 4, 'expected_state_sha256', '0' * 64),
                                          ('unsupported-report', 3, 'profile', 'StandaloneReport/1')]:
            changed = deepcopy(original)
            changed['commands'][index]['request'][field] = value
            # This test author explicitly supplies a new selection; the runtime never does.
            selection = dict(profile=program.SELECTION, **program.identities(changed), term_selection=chosen['term_selection'])
            before = deepcopy(changed)
            result = program.execute(changed, selection, program.core.digest(selection))
            check(name + ':partial refusal', result['status'], 'partial')
            check(name + ':exact full prefix', result['steps'], baseline['steps'][:index])
            check(name + ':unchanged last state', result['after'], baseline['steps'][index - 1]['result']['execution']['after'])
            check(name + ':exact remaining commands', result['remaining_commands'], changed['commands'][index + 1:])
            check(name + ':input unchanged', changed, before)
            save(name, {'request': changed, 'selection': selection, 'result': result})

        history = module('current_compat_selected_history', BASE / 'selected-reading-history-20261027/compose.py')
        independent = module('current_compat_independent_history', BASE / 'selected-reading-history-20261027/independent_check.py')
        source_dir = BASE / 'selected-reading-history-20261027/attempt-01'
        for name in ['request.json', 'result.json']:
            protect(source_dir / name)
        body, old = read(source_dir / 'request.json'), read(source_dir / 'result.json')
        before = deepcopy(body)
        result = history.assess(body)
        check('history input unchanged', body, before)
        for name in ['profile', 'status', 'selected_source', 'budget', 'selected_observations', 'selected_relations', 'context_count', 'joint_cross_context_history', 'whole_statement_history_complete', 'executable_opening']:
            check('history retained:' + name, result[name], old[name])
        check('history population', (result['selected_observations'], result['selected_relations'], result['context_count']), (236, 101, 2))
        obligations = 0
        for key, child in result['attachments'].items():
            for name in ['status', 'definition', 'target_obligations', 'unmapped_observations', 'target_existence']:
                check('history context:' + key + ':' + name, child[name], old['attachments'][key][name])
            verdict = independent.check(child['definition'], child['witness'], child['replay'])
            check('independent history:' + key, verdict['accounts'] == 19 and verdict['events'] == 2)
            obligations += len(child['target_obligations'])
        check('all target obligations retained', obligations, 180)
        for flag in ['executed', 'source_admission', 'accounting_admission', 'joint_cross_context_history', 'whole_statement_history_complete']:
            check('no promotion:' + flag, result[flag], False)
        save('selected-history-result', result)
        sys.path.insert(0, str(ROOT / 'scripts'))
        import conditional_company_opening_v1 as opening
        import conditional_company_continuation_v1 as continuation
        import company_book_carry_v1 as carry
        for name, value in [('selected-history-wrapper', result), ('temporal-definition', result['selected_source']['definition'])]:
            output = opening.map_opening(deepcopy(value))
            check(name + ':not opening input', output['status'], 'invalid')
            save(name + '-refusal', {'input': value, 'result': output})
        changed = deepcopy(body)
        changed['histories'].pop(next(iter(changed['histories'])))
        output = history.assess(changed)
        check('missing source context refused', output['status'], 'invalid')
        save('missing-context', {'request': changed, 'result': output})
        changed = deepcopy(body)
        changed['reading'] = None
        output = history.assess(changed)
        check('missing reading unresolved', (output['status'], output['history_assessment_started'], output['attachments']), ('unresolved', False, {}))
        save('missing-reading', {'request': changed, 'result': output})
        cases_path = BASE / 'source-opening-compatibility-20261027/attempt-01/cases.json'
        protect(cases_path)
        replayed = []
        for case in read(cases_path):
            label = case['case']
            if label.startswith('opening:') or label.startswith('boundary:') and label.split(':', 1)[1] in ['temporal_definition_is_not_history', 'missing_premise', 'missing_memory', 'wrong_entity', 'wrong_scale', 'target_obligation', 'unmapped_observation']:
                operation = opening.map_opening
            elif label.startswith(('continuation:', 'blocked_continuation:')):
                operation = continuation.run
            elif label.startswith('carry:'):
                operation = carry.propose
            else:
                continue
            request = deepcopy(case['request'])
            before = deepcopy(request)
            actual = operation(request)
            check('complete opening/report/carry replay:' + label, actual, case['result'])
            check('unchanged replay request:' + label, request, before)
            replayed.append({'case': label, 'request': request, 'result': actual})
        check('replayed connected/invalid cases', len(replayed), 21)
        save('opening-continuation-carry-cases', replayed)
        package = ROOT / 'docs/design/proposal/manuscript-reference-v555r1-20261027'
        manifest = read(package / 'package-manifest.json')
        protect(package / 'package-manifest.json')
        for row in manifest['files']:
            protect(package / row['path'], row['sha256'])
        for name, expected in lock.items():
            check('protected after:' + name, digest(ROOT / name), expected)
        success = True
    finally:
        (out / 'checks.json').write_text(json.dumps(checks, indent=2) + '\n')
        (out / 'input-lock.json').write_text(json.dumps(lock, indent=2) + '\n')
        (out / 'artifacts.json').write_text(json.dumps(artifacts, indent=2) + '\n')
        manifest = dict(passed=success, git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                        command='CUDA_VISIBLE_DEVICES=-1 python3 -B data/accounting-master/compatibility-current-20261028/verify.py ' + attempt.name,
                        environment=dict(python=sys.version, executable=sys.executable, platform=platform.platform()), cpu_gpu='CPU only; GPU intentionally hidden',
                        random_seeds='N/A: deterministic engineering regression', data_version=digest(out / 'input-lock.json'),
                        wall_seconds=time.monotonic()-start, timestamp_utc=datetime.now(timezone.utc).isoformat(),
                        plan_file='docs/plans/accounting-compatibility-reconciliation-20261028.md',
                        result_file='data/accounting-master/compatibility-current-20261028/result.md', artifacts=artifacts,
                        scope='Bounded native interface and retained financial regression; no broad acceptance promotion')
        (out / 'run-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        print(json.dumps({'passed': success, 'checks': len(checks), 'failed': [x['label'] for x in checks if not x['passed']], 'protected_files': len(lock), 'artifacts': len(artifacts), 'wall_seconds': manifest['wall_seconds']}))


if __name__ == '__main__':
    main()
