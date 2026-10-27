"""Read-only verification by default; one-time completion with live preflight."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from reference import ISSUERS, check

U = Path(__file__).resolve().parent
R = U.parents[2]
PLAN = R / 'docs/plans/accounting-r05-ocf-measurement-20261023.md'
REVIEW = R / 'data/accounting-master/readability-repair-20261022-theta'
SUPPLEMENT = REVIEW / 'r05-ocf-measurement-supplement.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(R))
bind = lambda p: {'path': rel(p), 'sha256': sha(p)}


def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def check_all():
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    p = load(U / 'protection.json')
    for name, digest in p['protected'].items():
        assert sha(R / name) == digest, name
    assert sha(R / '.git/index') == p['index_sha256']
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip() == p['head']
    raw = subprocess.check_output(['git', 'status', '--porcelain=v1', '--untracked-files=no', '-z'], cwd=R, text=True)
    dirty = [row for row in raw.split('\0') if row]
    assert all(row[:2] == ' M' for row in dirty)
    assert {row[3:] for row in dirty} == set(p['tracked_dirty'])
    for name, digest in p['tracked_dirty'].items():
        if name not in p['controls']:
            assert sha(R / name) == digest, name
    for name in p['controls']:
        assert sha(U / 'controls-before' / name) == p['tracked_dirty'][name]
    m = load(U / 'measurement-map.json')
    assert {r['issuer_id'] for r in m['rows']} == set(ISSUERS) and len(m['rows']) == 9
    assert sha(R / m['coverage']['path']) == m['coverage']['sha256']
    coverage = load(R / m['coverage']['path'])
    anchors = 0
    for row in m['rows']:
        original = coverage['rows'][int(row['coverage_pointer'].split('/')[-1])]
        assert original['issuer_id'] == row['issuer_id'] and original['document_id'] == row['document_id']
        assert original['source_url'] == row['source_url']
        assert original['local_path'] == row['original']['path']
        assert original['period_year'] == 2025 and original['report_class'] == 'annual'
        for field in ('original', 'text'):
            assert sha(R / row[field]['path']) == row[field]['sha256']
        lines = (R / row['text']['path']).read_text().split('\n')
        for a in row['anchors']:
            assert '\n'.join(lines[a['start_line'] - 1:a['end_line']]) == a['quote']
            anchors += 1
        for flag in ('first_release_admitted', 'historical_vintage_admitted',
                     'accounting_harmonization_admitted', 'independent_gold'):
            assert row[flag] is False
        Fraction(row['reported_value']['amount'])
    image = m['rendered_source_review']
    assert sha(R / image['path']) == image['sha256']
    assert image['physical_page'] == 232 and image['observed_2025_ocf_eur_million'] == '4906'
    target = load(U / 'target.json')
    assert target['user_selected']['issuer_weights'] == {i: '1/9' for i in ISSUERS}
    old = load(R / 'data/accounting-master/r05-predictive-accuracy-target-20261023/decision.json')
    assert target['purpose_answer_verbatim'] == old['purpose']['answer']
    assert target['proposed_measurement']['target_id'] == 'operating_cash_flow'
    assert target['proposed_measurement']['material_or_economic_margin'] is None
    for flag in ('runtime_admitted', 'inference_admitted', 'empirical_execution'):
        assert target[flag] is False
    vintage = load(R / 'data/accounting-master/r05-vintage-admission-20261018/reconciliation.json')
    assert len(vintage['rows']) == 192
    assert all(r['as_of_admission'] is False and r['selected_byte_available_at'] is None for r in vintage['rows'])
    assess, operations = load(REVIEW / 'assessment-successor.json'), load(REVIEW / 'operation-successor.json')
    assert (len(assess['rows']), len(assess['interactions']), len(operations['rows'])) == (53, 6, 46)
    assert assess['readiness'] == operations['readiness'] == 'not_ready'
    cases = check()
    return p, cases, {'mapping_candidates': 9, 'source_anchors': anchors, 'source_pages_previously_viewed_in_unit': 1,
        'passed_case_count': cases['passed_case_count'], 'rejected_case_count': cases['rejected_case_count'],
        'protected_files': len(p['protected']), 'tracked_dirty_paths': len(dirty),
        'first_release_admissions': 0, 'historical_vintage_admissions': 0,
        'whole_rows_closed': 0, 'readiness': 'not_ready', 'manuscript_changed': False,
        'empirical_execution': False, 'inference_admitted': False}


HEADER = '''## 23 October 2026 — E3 measurement and target repair

Current E3 purpose: future predictive accuracy for the same nine companies,
next complete fiscal year, named pre-start cutoff, equal company weights.
The OCF measurement unit is complete: nine reported-basis candidates, explicit
Delta/D correction, ten exact cases and twelve refusals. No first-release or
historical-byte admission follows. Details: data/accounting-master/r05-ocf-measurement-20261023/.
Next: release-aware temporal grouping and refit feasibility; then dated
reporting transitions and dependence-aware inference. No user choice is pending.

'''
FRONTIER = '''The E3 OCF measurement and target repair is complete at
data/accounting-master/r05-ocf-measurement-20261023/: nine FY2025 reported
consolidated OCF mapping candidates, 39 LF source anchors and one actually
viewed source page. Parent/subgroup alternatives, signs, units and reporting
basis are explicit. These are not first-release outcomes or independent gold.
IFRS18/IAS7 disclosures create a dated transition dependency for 2027 onward.

The successor preserves and corrects the completed predictive-accuracy unit:
Delta is expected future loss difference; D is the finite realised estimator;
actual named issuers replace fixture aliases; the old seven-refusal count was
wrong (five were executed). Ten exact cases and twelve refusals now cover
finite-law CRPS, unit scaling, unequal-origin equal-company aggregation,
unweighted sets, invalid weights, duplicate origins and undefined zero-weight
cells. These checks establish no forecast ranking or inference.

Next E3 dependency: propose release-aware temporal grouping and refit
feasibility, followed by dated reporting-transition and first-release source
work. The user's research purpose supports a directional zero-boundary
comparison; a material/economic margin is a separate conditional claim.
Future law, time weights, refit/service, scale admissions, confidence,
multiplicity, sample/resources and inference remain unresolved. All 192
historical byte admissions remain false. Completed one-time stages are frozen;
safe replay is verify.py without flags. No user choice is pending.

'''
CURRENT = '''E3 selects future predictive accuracy for the nine named companies,
next full fiscal years and equal company weights. A reported-basis OCF mapping
is proposed, with target/scale/source admissions and reporting transitions
still open. Future law, temporal grouping, refit/service and inference remain
to specify. Zero is the proposed directional research boundary; material
economic improvement is a separate conditional claim. All 192 historical-byte
admissions remain false. These gaps block dependent empirical work while
internal preparation continues. Runtime/controller, installations, empirical
runs, acquired-code execution, commits, outreach, publication and fees remain
held. Earlier dated records below retain their historical scope.

'''


def prepare_edits(p):
    """Check all exact live inputs before any record/control write."""
    edits = []
    for name in p['controls']:
        before = (U / 'controls-before' / name).read_text()
        assert (R / name).read_bytes() == (U / 'controls-before' / name).read_bytes(), name
        exact = 'Next E3 dependency: specify a source-bound target/perimeter and future-origin\n'
        assert before.count(exact) == 1, name
        start = 'The user has selected research comparison of predictive accuracy for the first'
        assert before.count(start) == 1
        a = before.index(start)
        b = before.index('Completed review evidence:', a)
        after = before[:a] + FRONTIER + before[b:]
        a = after.index('## 23 October 2026 — E3 decisions and timing feasibility')
        b = after.index('## 22 October 2026', a)
        after = after[:a] + HEADER + after[b:]
        a = after.index('E3 selects named-company future dates, full fiscal years and equal issuer')
        b = after.index('## 20 October 2026', a)
        after = after[:a] + CURRENT + after[b:]
        edits.append((name, after))
    return edits


def record(p, cases, checks, elapsed):
    for name in ('reference-results.json', 'checks.json', 'run-manifest.json', 'completion.json', 'controls-after'):
        assert not (U / name).exists(), name
    assert not SUPPLEMENT.exists()
    for name in ('errata.md', 'target-contract.md', 'measurement-proposal.md', 'result.md', 'review.md'):
        assert (U / name).is_file()
    edits = prepare_edits(p)
    now = datetime.now(timezone.utc)
    write(U / 'reference-results.json', cases)
    write(U / 'checks.json', checks)
    prefix = 'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B '
    write(U / 'run-manifest.json', {
        'git_commit': p['head'], 'branch': p['branch'], 'environment': sys.executable,
        'python': platform.python_version(), 'cpu_gpu': 'CPU only; GPU devices intentionally hidden; standard library only',
        'data_version': 'Retained FY2025 annual reports bound by measurement-map.json; source examples only',
        'random_seeds': 'N/A deterministic exact reference', 'started_utc': p['started_utc'],
        'recorded_utc': now.isoformat(), 'wall_time_seconds': (now - datetime.fromisoformat(p['started_utc'])).total_seconds(),
        'wall_time_scope': 'elapsed preparation-to-completion interval, including source reading and recovery',
        'verification_seconds': elapsed,
        'commands': [prefix + rel(U / x) for x in ('prepare.py', 'record_measurements.py', 'reference.py', 'verify.py')]
                    + [load(U / 'measurement-map.json')['rendered_source_review']['render_command'], prefix + rel(U / 'verify.py') + ' --record'],
        'plan': rel(PLAN), 'result': rel(U / 'result.md'), 'review': rel(U / 'review.md'), 'output_paths': [rel(U), rel(SUPPLEMENT)],
        'verification_replay': prefix + rel(U / 'verify.py')})
    write(SUPPLEMENT, {'scope': 'OCF source-bound measurement proposal and additive E3 target/checker repair',
        'plan': bind(PLAN), 'target': bind(U / 'target.json'), 'measurement_map': bind(U / 'measurement-map.json'),
        'result': bind(U / 'result.md'), 'review': bind(U / 'review.md'), 'checks': checks,
        'candidate_version': '3.48', 'whole_rows_closed': 0, 'readiness': 'not_ready',
        'independent_human_acceptance': 'pending', 'manuscript_changed': False, 'runtime_admitted': False})
    for name, after in edits:
        snap = U / 'controls-after' / name
        snap.parent.mkdir(parents=True, exist_ok=True)
        with snap.open('x') as stream:
            stream.write(after)
        (R / name).write_text(after)
    assert check_all()[1:] == (cases, checks)
    files = [x for x in U.rglob('*') if x.is_file() and '__pycache__' not in x.parts] + [PLAN, SUPPLEMENT]
    write(U / 'completion.json', {'status': 'complete_documentary_ocf_measurement_target_repair', 'checks': checks,
        'bindings': {rel(x): sha(x) for x in sorted(files)},
        'control_replay_policy': 'Immutable before/after snapshots; live controls may advance in a successor'})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--record', action='store_true')
    args = ap.parse_args()
    start = time.monotonic()
    p, cases, checks = check_all()
    if args.record:
        record(p, cases, checks, time.monotonic() - start)
    if (U / 'completion.json').exists():
        complete = load(U / 'completion.json')
        assert complete['checks'] == load(U / 'checks.json') == checks
        assert load(U / 'reference-results.json') == cases
        for name, digest in complete['bindings'].items():
            assert sha(R / name) == digest, name
        status = 'recorded and verified' if args.record else 'read-only replay passed'
    else:
        prepare_edits(p)
        status = 'read-only preflight passed; not recorded'
    print(json.dumps({'status': status, **checks}))


if __name__ == '__main__':
    main()
