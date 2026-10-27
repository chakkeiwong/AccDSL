"""Record once; subsequent replay never rewrites preserved evidence."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import os
import platform
import re
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
REL = HERE.relative_to(ROOT).as_posix()


def sha(path): return sha256(path.read_bytes()).hexdigest()
def dump(path, data): path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def main():
    assert sys.argv[1:] in [[], ['--record']]
    record = bool(sys.argv[1:]); start = time.monotonic(); started = datetime.now(timezone.utc).isoformat()
    if record: assert not (HERE / 'checks.json').exists(), 'already recorded'
    env = {**os.environ, 'CUDA_VISIBLE_DEVICES': '-1', 'PYTHONDONTWRITEBYTECODE': '1'}
    before = {}
    paths = [ROOT / 'scripts' / (name + '.py') for name in [
        'declared_collection_clock_v1', 'declared_company_program_v2', 'declared_company_text_v2',
        'company_method_clock_v1', 'company_method_clock_v2', 'company_book_transition_v1',
        'company_book_reports_v1', 'company_book_carry_v1', 'declared_operating_methods_v1',
        'declared_financing_methods_v1', 'declared_financing_schedules_v1',
        'method_collections_v1', 'method_state_assessment_v1', 'annual_period_book_v1',
        'shared_deferred_assessment_v1']]
    paths += [ROOT / 'tests/test_declared_collection_clock_v1.py', HERE / 'examples.py', HERE / 'audit.md',
              HERE / 'design.md', HERE / 'verify.py',
              ROOT / 'docs/plans/accounting-declared-dynamic-collection-clock-20261025.md',
              ROOT / 'data/accounting-master/declared-operating-cycle-20261025/examples.py',
              ROOT / 'data/accounting-master/declared-financing-schedules-validation-20261025/checks.json',
              ROOT / 'data/accounting-master/declared-financing-schedules-validation-20261025/source-lock.json',
              ROOT / 'docs/design/proposal/manuscript-financing-schedules-repair-20261025/accounting-product-proposal.pdf']
    for p in paths: before[p.relative_to(ROOT).as_posix()] = sha(p)
    if not record:
        saved = json.loads((HERE / 'source-lock.json').read_text()); assert before == saved, 'changed source population or hashes'
    commands, runs, checks = [], [], []
    for pattern, name in [('test_declared_collection_clock_v1.py', 'focused'),
                          ('test_declared_operating_methods_v1.py', 'operating_regression'),
                          ('test_declared_company_program_v1.py', 'program_regression'),
                          ('test_company_book_carry_v1.py', 'carry_regression')]:
        cmd = [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', pattern]
        began = time.monotonic(); run = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, timeout=300)
        log = run.stdout + run.stderr; match = re.search(r'Ran (\d+) tests', log)
        count = int(match[1]) if match else 0
        checks.append({'name': name, 'passed': run.returncode == 0 and count > 0 and log.rstrip().endswith('OK')})
        commands.append(cmd); runs.append({'name': name, 'tests': count, 'returncode': run.returncode, 'wall_seconds': time.monotonic() - began})
        if record: (HERE / (name + '.log')).write_text(log)
        if not checks[-1]['passed']: raise AssertionError(log[-3000:])
    sys.path.insert(0, str(ROOT / 'scripts'))
    spec = importlib.util.spec_from_file_location('collection_evidence_examples', HERE / 'examples.py')
    examples = importlib.util.module_from_spec(spec); spec.loader.exec_module(examples)
    comparison = examples.compare(); checks.extend(comparison['checks'])
    assert len({r['name'] for r in checks}) == len(checks), 'duplicate check names'
    checks.append({'name': 'protected_sources_unchanged', 'passed': all(sha(ROOT / k) == v for k, v in before.items())})
    assert all(r['passed'] for r in checks), [r for r in checks if not r['passed']]
    compact = [{'case': c['case'], 'checks': c['checks'], 'request_sha256': examples.program.digest(c['request']),
                'result_sha256': examples.program.digest(c['result']), 'observation': c['result']['observation'],
                'successful_commands': c['result']['successful_commands']} for c in comparison['cases']]
    summary = {'passed': True, 'focused_tests': runs[0]['tests'],
               'regression_tests': sum(r['tests'] for r in runs[1:]), 'comparison_checks': len(comparison['checks']),
               'named_checks': len(checks), 'cases': len(compact), 'protected_files': len(before)}
    if record:
        dump(HERE / 'checks.json', {**summary, 'checks': checks})
        dump(HERE / 'comparison.json', {'cases': compact, 'checks': comparison['checks']})
        dump(HERE / 'source-lock.json', before)
        dump(HERE / 'run-manifest.json', {'started_utc': started,
             'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
             'command': commands, 'environment': {'python': sys.version, 'executable': sys.executable,
             'platform': platform.platform(), 'CUDA_VISIBLE_DEVICES': '-1', 'PYTHONDONTWRITEBYTECODE': '1'},
             'cpu_gpu': 'CPU only; GPU intentionally hidden; no GPU libraries imported',
             'random_seeds': 'N/A: deterministic exact arithmetic', 'data_version': before,
             'wall_seconds': time.monotonic() - start, 'runs': runs, 'plan': 'docs/plans/accounting-declared-dynamic-collection-clock-20261025.md',
             'result': REL + '/result.md', 'output_artifacts': [REL + '/checks.json', REL + '/comparison.json']})
    else:
        assert json.loads((HERE / 'comparison.json').read_text()) == {'cases': compact, 'checks': comparison['checks']}, 'replay mismatch'
        assert json.loads((HERE / 'checks.json').read_text()) == {**summary, 'checks': checks}, 'check replay mismatch'
    print(json.dumps({**summary, 'mode': 'record' if record else 'read_only_replay'}))


if __name__ == '__main__': main()
