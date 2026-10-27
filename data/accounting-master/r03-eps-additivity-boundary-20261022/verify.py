"""Freeze once, refresh four live controls once, otherwise verify read-only."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

U = Path(__file__).resolve().parent
R = U.parents[2]
A = R / 'data/accounting-master/readability-repair-20261022-theta'
PLAN = R / 'docs/plans/accounting-r03-eps-additivity-boundary-20261022.md'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(R))
bind = lambda p: dict(path=rel(p), sha256=sha(p))


def write(name, value):
    with (U / name).open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


def check():
    p = load(U / 'protection.json')
    for name, digest in p['protected'].items():
        assert sha(R / name) == digest, name
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip() == p['head']
    assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=R, text=True).strip() == p['branch']
    assert sha(R / '.git/index') == p['index_sha256']
    rows = [x for x in subprocess.check_output(['git', 'status', '--porcelain=v1', '--untracked-files=no', '-z'], cwd=R, text=True).split('\0') if x]
    assert all(x[:2] == ' M' for x in rows) and {x[3:] for x in rows} == set(p['tracked_dirty'])
    for name, digest in p['tracked_dirty'].items():
        if name not in p['controls']:
            assert sha(R / name) == digest, name
    a, o = load(A / 'assessment-successor.json'), load(A / 'operation-successor.json')
    assert len(a['rows']) == 53 and len(a['interactions']) == 6 and len(o['rows']) == 46
    assert a['readiness'] == 'not_ready' and all(not row['full_requirement_closed'] for row in o['rows'])
    assert sha(R / a['candidate_pdf']) == a['candidate_pdf_sha256']
    c, m = load(U / 'checks.json'), load(U / 'calculation-manifest.json')
    assert c['status'] == 'pass' and len(c['fixtures']) == 21 and len(c['invalid_controls']) == 10
    assert c['grid']['models'] == 4320 and c['grid']['additive'] == 3952 and c['grid']['nonadditive'] == 368
    assert c['grid']['worlds'] == 27972 and c['grid']['additive_selector_comparisons'] == 7904
    assert all(row['rejected_before_world_evaluation'] for row in c['invalid_controls'])
    assert all(row['final_accounting_selection'] == 'not_admitted' for row in c['fixtures'])
    for name, digest in (m['input_bindings'] | m['outputs']).items():
        assert sha(R / name) == digest, name
    return p, a


def record(p, a):
    assert not any((U / n).exists() for n in ('completion.json', 'run-manifest.json', 'r08-supplement.json'))
    for name, digest in p['tracked_dirty'].items():
        assert sha(R / name) == digest, name
    write('r08-supplement.json', dict(candidate_version='3.48', candidate_pdf=a['candidate_pdf'],
        candidate_pdf_sha256=a['candidate_pdf_sha256'], readiness='not_ready',
        obligations=bind(A / 'assessment-successor.json'), operations=bind(A / 'operation-successor.json'),
        counts=dict(obligations=53, interactions=6, operations=46, whole_rows_closed=0),
        addressed_requirements=['MC17','MC24','MC26','MC28','MC29','MC32','MC33','MC34','MC35'],
        operation='P17-05.04', scope='Necessary-and-sufficient additivity boundary for the supplied threshold-bonus numerator',
        method_status='general_nonadditive_selection_not_evaluated',
        evidence=[bind(U / name) for name in ('derivation.md','fixtures.json','checks.json','attempts.md','result.md')],
        next_action='Fresh ordered Version 3.48 chapter/cumulative/document regression; no inherited reading credit'))
    calc = load(U / 'calculation-manifest.json')
    write('run-manifest.json', dict(git_commit=p['head'], branch=p['branch'], environment=sys.executable,
        cpu_gpu=calc['cpu_gpu'], seeds=calc['seeds'], data_version=calc['data_version'],
        started_utc=p['started_utc'], recorded_utc=datetime.now(timezone.utc).isoformat(),
        wall_seconds_calculation=calc['wall_seconds'], failed_attempt=bind(U / 'attempts.md'),
        exact_calculation=bind(U / 'calculation-manifest.json'),
        commands=['prepare.py (already completed)',calc['command'],'verify.py --record','verify.py --refresh','verify.py'],
        plan=bind(PLAN), result=bind(U / 'result.md'),
        outputs=[bind(U / n) for n in ('derivation.md','checks.json','r08-supplement.json')]))
    files = [f for f in U.rglob('*') if f.is_file() and '__pycache__' not in f.parts] + [PLAN]
    write('completion.json', dict(status='scoped_additivity_boundary_complete',
                                  bindings={rel(f): sha(f) for f in sorted(files)}))


def refresh(p):
    assert not (U / 'controls-after').exists()
    old = '''Next: derive and check the exact additive boundary of the supplied threshold-
bonus EPS model under a new audited plan. This can establish when the existing
additive method's premises hold; it cannot choose a general nonadditive selector.
Preserve P80 and both strict ordering/stability discriminators.'''
    new = '''The exact EPS additivity boundary is complete at
data/accounting-master/r03-eps-additivity-boundary-20261022/: a two-direction
proof, 21 exact fixtures, 10 rejected outside-domain controls and a predeclared
4,320-model diagnostic pass. The four conditions include the single-positive-
saving exception and both threshold equalities. Pair checks alone can miss a
triple interaction. P80/P90 and both strict three-series witnesses remain
nonadditive; general final selection remains not_evaluated. One draft example
expectation failed and was repaired transparently. No runtime, source authority
or whole-row closure follows. Safe replay: verify.py without flags.

Next: perform a fresh ordered Version 3.48 chapter/cumulative/document
regression under an audited plan, with small page segments and honest reading
receipts. Prior Version 3.47 review and six local Version 3.48 page inspections
do not supply full successor reading credit.'''
    changes = []
    for name in p['controls']:
        path = R / name
        before = path.read_text()
        assert sha(path) == sha(U / 'controls-before' / name) and before.count(old) == 1, name
        changes.append((name, before.replace(old, new, 1)))
    (U / 'controls-after').mkdir()
    for name, after in changes:
        (R / name).write_text(after)
        dest = U / 'controls-after' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(after)
    with (U / 'controls-after/manifest.json').open('x') as f:
        json.dump(dict(files=[bind(R / name) for name, _ in changes]), f, indent=2)
        f.write('\n')


parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument('--record', action='store_true')
group.add_argument('--refresh', action='store_true')
args = parser.parse_args()
p, a = check()
if args.record:
    record(p, a)
completion = load(U / 'completion.json')
for name, digest in completion['bindings'].items():
    assert sha(R / name) == digest, name
if args.refresh:
    refresh(p)
if (U / 'controls-after/manifest.json').exists():
    for item in load(U / 'controls-after/manifest.json')['files']:
        assert sha(U / 'controls-after' / item['path']) == item['sha256'], item['path']
print(json.dumps(dict(status='recorded' if args.record else 'controls refreshed' if args.refresh else 'read-only replay passed',
    protected_files=len(p['protected']), bindings=len(completion['bindings']), fixtures=21, finite_models=4320,
    whole_rows_closed=0, readiness='not_ready')))
