"""Close the bounded author reassessment; preserve historical evidence."""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
if (UNIT / 'completion.json').exists():
    raise SystemExit('Completed unit; preserve evidence.')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    (UNIT / name).write_text(json.dumps(value, indent=2) + '\n')


baseline = json.loads((UNIT / 'baseline.json').read_text())
integrity = json.loads((UNIT / 'integrity-checks.json').read_text())
assessment = json.loads((UNIT / 'assessment.json').read_text())
index = subprocess.check_output(['git', 'diff', '--cached', '--raw', '--no-abbrev'], cwd=ROOT)
checks = {
    'integrity_passed': not integrity['failed'] and integrity['passed'] == 173,
    'readiness_negative': not assessment['ready'] and assessment['status'] == 'not_ready',
    'prior_assessment_preserved': sha(ROOT / baseline['prior_assessment']) == baseline['prior_assessment_sha256'],
    'frozen_p19_preserved': sha(ROOT / 'data/accounting-master/deliverables/P19/readiness.json') == baseline['historical_p19_sha256'],
    'candidate_preserved': sha(ROOT / baseline['candidate'] / 'accounting-product-proposal.pdf') == baseline['candidate_pdf_sha256'],
    'unrelated_index_preserved': index == (UNIT / 'unrelated-index-before.txt').read_bytes(),
    '100_staged_entries_preserved': len(index.splitlines()) == 100,
    'queue_and_result_exist': all((UNIT / n).is_file() for n in ['queue-decision.md', 'result.md']),
}
for control in baseline['controls']:
    checks['snapshot:' + control['live']] = sha(ROOT / control['snapshot']) == control['sha256']
    content = (ROOT / control['live']).read_text()
    checks['next_plan:' + control['live']] = 'accounting-apple-statement-network-20261013.md' in content
failed = [key for key, value in checks.items() if not value]
save('closeout-checks.json', {'checks': checks, 'passed': sum(checks.values()), 'failed': failed})
if failed:
    raise SystemExit(str(failed))
finished = datetime.now(timezone.utc)
manifest = {
    'git_commit': baseline['git_commit'],
    'commands': ['python3 data/accounting-master/post-insurance-readiness-20261013/build_assessment.py',
                 'python3 data/accounting-master/post-insurance-readiness-20261013/closeout.py'],
    'environment': {'python': sys.executable, 'python_version': sys.version, 'libraries': 'Python standard library'},
    'cpu_gpu': 'CPU-only document/hash processing; no GPU libraries imported or devices probed',
    'random_seeds': 'N/A: deterministic document assessment',
    'data_version': baseline['prior_assessment_sha256'],
    'started_at': baseline['started_at'], 'finished_at': finished.isoformat(),
    'wall_time_seconds': (finished - datetime.fromisoformat(baseline['started_at'])).total_seconds(),
    'wall_time_scope': 'Elapsed unit interval including review, writing and session handoff; not a benchmark',
    'plan': 'docs/plans/accounting-post-insurance-readiness-20261013.md',
    'result': str((UNIT / 'result.md').relative_to(ROOT)),
    'outputs': {str(p.relative_to(ROOT)): sha(p) for p in sorted(UNIT.rglob('*')) if p.is_file()
                and p.name not in {'run-manifest.json', 'completion.json'}},
    'controls': {c['live']: sha(ROOT / c['live']) for c in baseline['controls']},
}
save('run-manifest.json', manifest)
save('completion.json', {'status': 'complete_within_author_reassessment_scope', 'readiness': 'not_ready',
                        'finished_at': finished.isoformat(), 'manifest_sha256': sha(UNIT / 'run-manifest.json'),
                        'next_plan': assessment['next_plan']})
print(json.dumps({'passed': sum(checks.values()), 'failed': failed, 'unrelated_staged_entries': 100}))
