from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json
import platform
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import shared_book_authoring_v1 as m


def sha(p): return sha256(p.read_bytes()).hexdigest()
def dump(name, value): (HERE / name).write_text(json.dumps(value, indent=2) + '\n')
def same(a, b): return m.book.caller.canonical(a) == m.book.caller.canonical(b)


def main():
    start = time.monotonic()
    mode = sys.argv[1] if len(sys.argv) > 1 else '--check'
    assert mode in ['--check', '--record', '--replay']
    if mode == '--record': assert not (HERE / 'manifest.json').exists(), 'already recorded'
    m.protected(); checks = []
    def check(name, condition):
        assert condition, name
        checks.append(name)
    locks = json.loads((HERE / 'source-lock.json').read_text())
    for name, expected in locks.items(): check('protected:' + name, sha(ROOT / name) == expected)
    original = json.loads((ROOT / 'data/accounting-master/shared-book-statements-20261024/cases.json').read_text())
    rejected = {'unsupported_tax': 'unsupported_module', 'stale_opening_digest': 'opening_digest',
                'arbitrary_closing_state': 'closed_fields:request'}
    rows = []; sources = {}
    for row in original:
        name = row['case']; before = m.book.digest(row)
        if name in rejected:
            try: m.from_request(row['request'], name)
            except m.Invalid as exc: reason = str(exc)
            else: raise AssertionError('expected compiler rejection:' + name)
            check(name + ':compiler_rejection', reason == rejected[name])
            rows.append({**row, 'authoring_status': 'compile_rejected', 'reason': reason})
        else:
            p = m.from_request(row['request'], name); source = m.render(p); typed = m.lower(source)
            compiled = m.compile_text(source)
            text_result = m.execute_text(source); typed_result = m.execute_program(typed)
            check(name + ':typed_roundtrip', same(p, typed))
            check(name + ':text_roundtrip', source == m.render(typed))
            check(name + ':compiled_request', same(compiled['program']['request'], row['request']))
            check(name + ':complete_text_result', same(text_result, row['result']))
            check(name + ':complete_typed_result', same(typed_result, row['result']))
            check(name + ':explicit_limits', all(text_result[k] is False for k in m.reports.FLAGS))
            check(name + ':request_identity', compiled['request_sha256'] == m.book.digest(row['request']))
            sources[name + '.accdsl'] = source
            rows.append({**row, 'authoring_status': 'compiled', 'program': typed,
                         'compiled': compiled, 'text_result': text_result, 'typed_result': typed_result})
        check(name + ':immutable', before == m.book.digest(row))
    tests = json.loads((HERE / 'test-observation.json').read_text())
    check('tests_pass', tests['exit_code'] == 0)
    check('test_hashes', all(sha(ROOT / n) == h for n, h in tests['files'].items()))
    check('all_original_cases_preserved', len(rows) == len(original) == 19)
    report = {'passed': True, 'checks': len(checks), 'original_cases': len(rows),
        'exact_execution_matches': len(sources), 'compiler_rejections': len(rejected),
        'protected_files': len(locks), 'test_methods': tests['test_methods'],
        'regression_methods': tests['regression_methods'], 'whole_requirements_closed': 0}
    if mode == '--record':
        (HERE / 'programs').mkdir(exist_ok=False)
        for name, source in sources.items(): (HERE / 'programs' / name).write_text(source)
        dump('cases.json', rows); dump('checks.json', report); dump('check-names.json', checks)
        files = [p for p in HERE.rglob('*') if p.is_file()]
        files += [ROOT / 'scripts/shared_book_authoring_v1.py', ROOT / 'tests/test_shared_book_authoring_v1.py',
                  ROOT / 'docs/plans/accounting-shared-authoring-integration-20261024.md']
        dump('manifest.json', {'recorded_at': datetime.now(timezone.utc).isoformat(),
            'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'command': 'python3 -B data/accounting-master/shared-book-authoring-20261024/verify.py --record',
            'environment': {'python': platform.python_version(), 'executable': sys.executable},
            'cpu_gpu': 'CPU-only; no GPU framework imported', 'random_seeds': 'N/A: deterministic checks',
            'wall_seconds': time.monotonic() - start, 'data_version': 'source-lock.json',
            'plan': 'docs/plans/accounting-shared-book-authoring-20261024.md',
            'result': str((HERE / 'result.md').relative_to(ROOT)),
            'files': {str(p.relative_to(ROOT)): sha(p) for p in files}})
    elif mode == '--replay':
        assert same(report, json.loads((HERE / 'checks.json').read_text()))
        assert same(rows, json.loads((HERE / 'cases.json').read_text()))
        for name, source in sources.items(): assert source == (HERE / 'programs' / name).read_text()
        for name, expected in json.loads((HERE / 'manifest.json').read_text())['files'].items(): assert sha(ROOT / name) == expected, name
    print(json.dumps(report))


if __name__ == '__main__': main()
