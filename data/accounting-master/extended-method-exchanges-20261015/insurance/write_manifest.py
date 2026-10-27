"""Record a verified immutable P4a build without replacing any prior artifact."""
from pathlib import Path
import hashlib
import json
import platform
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    attempt = HERE / 'attempt-01'
    build = json.loads((attempt / 'build-result.json').read_text())
    audit = json.loads((attempt / 'independent-checks.json').read_text())
    lock = json.loads((HERE / 'predecessor-lock.json').read_text())
    assert audit['passed'] and audit['failures'] == 0
    files = [p for p in sorted(HERE.rglob('*')) if p.is_file()
             and '__pycache__' not in p.parts and p.name != 'run-manifest.json']
    manifest = dict(
        git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        commands=[build['command'], audit['command']], interpreter=audit['interpreter'],
        python_version=platform.python_version(), environment='existing tfgpu Python; stdlib/jsonschema only',
        cpu_gpu='CPU exact arithmetic; no GPU framework imported',
        data_version='InsuranceComponents/1; retained EU2023 IFRS17; synthetic supplied facts',
        random_seeds='N/A: deterministic exact cases',
        wall_seconds=build['wall_seconds'] + audit['wall_seconds'],
        plan='docs/plans/accounting-insurance-component-exchanges-20261015.md',
        result=str((HERE / 'result.md').relative_to(ROOT)),
        artifact=str(attempt.relative_to(ROOT)), passed=True,
        summary={k: build[k] for k in ('profile', 'methods', 'cases', 'records', 'exchanges', 'crash_worlds', 'challenges', 'packet_sha256')},
        independent_checks=audit['checks'], predecessor_lock_sha256=sha(HERE / 'predecessor-lock.json'),
        original_inputs=204, predecessor_files=len(lock['predecessor_files']), staged_entries=100,
        files=[dict(path=str(p.relative_to(ROOT)), sha256=sha(p)) for p in files],
        limits=['documentary specification', 'conditional synthetic accounting', 'historical source',
                'P4b transition/process and P5 composition remain open', 'not_ready'])
    target = HERE / 'run-manifest.json'
    with target.open('x') as f:
        f.write(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(dict(path=str(target.relative_to(ROOT)), files=len(files), passed=True, sha256=sha(target))))

if __name__ == '__main__':
    main()
