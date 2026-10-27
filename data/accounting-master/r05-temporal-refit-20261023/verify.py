"""Read-only replay; one-time documentary completion with preflighted controls."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from reference import ISSUERS, check, common_start_cohorts
from record_feasibility import compute

U = Path(__file__).resolve().parent
R = U.parents[2]
PLAN = R / 'docs/plans/accounting-r05-temporal-refit-20261023.md'
REVIEW = R / 'data/accounting-master/readability-repair-20261022-theta'
SUPPLEMENT = REVIEW / 'r05-temporal-refit-supplement.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(R))
bind = lambda p: {'path': rel(p), 'sha256': sha(p)}


def write(path, value):
    with path.open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


def check_all():
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    p = load(U / 'protection.json')
    for n, d in p['protected'].items():
        assert sha(R / n) == d, n
    assert sha(R / '.git/index') == p['index_sha256']
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip() == p['head']
    raw = subprocess.check_output(['git', 'status', '--porcelain=v1', '--untracked-files=no', '-z'], cwd=R, text=True)
    dirty = [r for r in raw.split('\0') if r]
    assert all(r[:2] == ' M' for r in dirty)
    assert {r[3:] for r in dirty} == set(p['tracked_dirty'])
    for n, d in p['tracked_dirty'].items():
        if n not in p['controls']:
            assert sha(R / n) == d, n
    for n in p['controls']:
        assert sha(U / 'controls-before' / n) == p['tracked_dirty'][n]
    feasibility = load(U / 'feasibility.json')
    assert compute() == feasibility
    cohorts = [{'r': g['minimum_training_labels'], 'v': g['minimum_inner_validation_origins'],
                'possible_common_start_years': common_start_cohorts({i: g['possible_outer_year_labels_per_issuer'] for i in ISSUERS})}
               for g in feasibility['conditional_grid']]
    cases = check()
    a, o = load(REVIEW / 'assessment-successor.json'), load(REVIEW / 'operation-successor.json')
    assert (len(a['rows']), len(a['interactions']), len(o['rows'])) == (53, 6, 46)
    assert a['readiness'] == o['readiness'] == 'not_ready'
    checks = {'conditional_designs': 6, 'annual_reports': 72, 'issuers': 9,
        'passed_case_count': cases['passed_case_count'], 'rejected_case_count': cases['rejected_case_count'],
        'protected_files': len(p['protected']), 'tracked_dirty_paths': len(dirty),
        'historical_vintage_admissions': 0, 'empirical_forecasts': 0,
        'inference_admitted': False, 'window_selected': False, 'whole_rows_closed': 0, 'readiness': 'not_ready'}
    return p, cases, cohorts, checks


HEADER = '''## 23 October 2026 — E3 temporal feasibility checked

Current question: future OCF predictive accuracy for the same nine companies,
next full fiscal year, pre-start cutoff and equal company weights. Measurement
and target repairs are complete documentary units. Temporal feasibility now
shows that three training labels plus two inner validation origins leave at
most one outer year per issuer in the eight-year panel; five plus two leave
none. These are optimistic bounds, not admitted data or selected budgets.
Next: dated IFRS18/IAS7 cash-flow transition support, then concrete source,
scale and inference dependencies. No user choice is pending.

'''
FRONTIER = '''The release-aware temporal/refit inquiry is complete at
data/accounting-master/r05-temporal-refit-20261023/: the 72 annual reports
supply eight labels per company. At a strict pre-start cutoff the adjacent
preceding full year is unfinished. Six optimistic same-issuer sensitivity
designs leave zero to six outer years per company; three training labels and
two inner origins leave only 2025, and five plus two leave none. Sixteen exact
cases and six refusals pass. The proposed start-year cohort convention exposes
Apple's offset and an additional endpoint loss; it is not a selected design.

The annual fitting proposal retains timing-aware nested validation, matched
baseline information/resources, fixed original weights and explicit failures.
No window, future law, confidence, sample adequacy or inference is admitted.

Next E3 dependency: inspect dated IFRS18/IAS7 technical amendments and their
OCF implications, then continue exact source/scale availability and inference
design. The zero-boundary research question remains active; a material economic
margin is a separate conditional claim. All 192 historical-byte admissions
remain false. Read-only replay: verify.py; completed one-time stages frozen.
No user choice is pending and no global continuation veto has fired.

'''


def edits(p):
    result = []
    for n in p['controls']:
        before = (U / 'controls-before' / n).read_text()
        assert (R / n).read_bytes() == (U / 'controls-before' / n).read_bytes(), n
        marker = 'Next E3 dependency: propose release-aware temporal grouping and refit\n'
        assert before.count(marker) == 1, n
        start = before.index(marker)
        end = before.index('Completed review evidence:', start)
        after = before[:start] + FRONTIER + before[end:]
        start = after.index('## 23 October 2026 — E3 measurement and target repair')
        end = after.index('## 22 October 2026', start)
        result.append((n, after[:start] + HEADER + after[end:]))
    return result


def record(p, cases, cohorts, checks, seconds):
    for n in ('reference-results.json', 'cohort-bounds.json', 'checks.json', 'run-manifest.json', 'completion.json', 'controls-after'):
        assert not (U / n).exists(), n
    assert not SUPPLEMENT.exists()
    changes = edits(p)
    for n in ('design-proposal.md', 'result.md', 'review.md'):
        assert (U / n).is_file()
    write(U / 'reference-results.json', cases)
    write(U / 'cohort-bounds.json', {'status': 'conditional_unchanged_calendars_only', 'designs': cohorts})
    write(U / 'checks.json', checks)
    prefix = 'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B '
    now = datetime.now(timezone.utc)
    write(U / 'run-manifest.json', {'git_commit': p['head'], 'branch': p['branch'],
        'environment': sys.executable, 'python': platform.python_version(),
        'cpu_gpu': 'CPU only; GPU devices intentionally hidden; standard library only',
        'data_version': '72 retained annual reports on 2018–2025 grid, bound by feasibility.json',
        'random_seeds': 'N/A deterministic enumeration', 'started_utc': p['started_utc'],
        'recorded_utc': now.isoformat(), 'wall_time_seconds': (now - datetime.fromisoformat(p['started_utc'])).total_seconds(),
        'wall_time_scope': 'preparation through completion including analysis', 'verification_seconds': seconds,
        'commands': [prefix + rel(U / n) for n in ('prepare.py', 'reference.py', 'record_feasibility.py', 'verify.py')]
            + [prefix + rel(U / 'verify.py') + ' --record'],
        'plan': rel(PLAN), 'result': rel(U / 'result.md'), 'review': rel(U / 'review.md'),
        'output_paths': [rel(U), rel(SUPPLEMENT)], 'read_only_replay': prefix + rel(U / 'verify.py')})
    write(SUPPLEMENT, {'scope': 'conditional temporal/refit feasibility and provisional annual cohort design',
        'plan': bind(PLAN), 'proposal': bind(U / 'design-proposal.md'), 'result': bind(U / 'result.md'),
        'review': bind(U / 'review.md'), 'checks': checks, 'candidate_version': '3.48',
        'readiness': 'not_ready', 'whole_rows_closed': 0, 'independent_human_acceptance': 'pending'})
    for n, after in changes:
        snapshot = U / 'controls-after' / n
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        with snapshot.open('x') as f:
            f.write(after)
        (R / n).write_text(after)
    assert check_all()[1:] == (cases, cohorts, checks)
    paths = [p for p in U.rglob('*') if p.is_file() and '__pycache__' not in p.parts] + [PLAN, SUPPLEMENT]
    write(U / 'completion.json', {'status': 'complete_documentary_temporal_refit_feasibility', 'checks': checks,
        'bindings': {rel(p): sha(p) for p in sorted(paths)},
        'replay_policy': 'Read only; immutable snapshots; no rewriting completed hashes'})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    start = time.monotonic()
    p, cases, cohorts, checks = check_all()
    if args.record:
        record(p, cases, cohorts, checks, time.monotonic() - start)
    if (U / 'completion.json').exists():
        complete = load(U / 'completion.json')
        assert complete['checks'] == load(U / 'checks.json') == checks
        assert load(U / 'reference-results.json') == cases
        assert load(U / 'cohort-bounds.json')['designs'] == cohorts
        for n, d in complete['bindings'].items():
            assert sha(R / n) == d, n
        status = 'recorded and verified' if args.record else 'read-only replay passed'
    else:
        edits(p)
        status = 'read-only preflight passed; not recorded'
    print(json.dumps({'status': status, **checks}))


if __name__ == '__main__':
    main()
