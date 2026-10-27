"""Read-only replay; one-time documentary completion with preflighted controls."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
from fractions import Fraction
from reference import check
import subprocess
import sys
import time

U = Path(__file__).resolve().parent
R = U.parents[2]
PLAN = R / 'docs/plans/accounting-r05-asset-scale-candidates-20261023.md'
REVIEW = R / 'data/accounting-master/readability-repair-20261022-theta'
SUPPLEMENT = REVIEW / 'r05-asset-scale-candidates-supplement.json'
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
    candidates = load(U / 'candidates.json')
    assert len(candidates['rows']) == 9
    expected = {'apple','caterpillar','jpmorgan','henkel','hsbc','munich_re','saic_motor','ping_an','midea'}
    assert {r['issuer_id'] for r in candidates['rows']} == expected
    anchor_count = 0
    for row in candidates['rows']:
        for key in ('original', 'text'):
            assert sha(R / row[key]['path']) == row[key]['sha256']
        lines = (R / row['text']['path']).read_text().split('\n')
        for anchor in row['anchors']:
            assert '\n'.join(lines[anchor['start_line']-1:anchor['end_line']]) == anchor['quote']
            anchor_count += 1
        assert Fraction(row['reported_total_assets']) > 0
        assert Fraction(row['amount_in_currency_units']) == Fraction(row['reported_total_assets'])*row['unit_multiplier']
        assert row['selected_for_actual_cutoff'] is False and row['as_of_admission'] is False
        assert row['selected_byte_available_at'] is None
    image = candidates['actually_viewed_source_page']
    assert sha(R / image['path']) == image['sha256']
    assert image['physical_page'] == 226 and image['total_assets_eur_million'] == '279934'
    assert candidates['cross_company_currency_conversion_required'] is False
    assert candidates['within_company_compatible_currency_and_units_required'] is True
    vintage = load(R / 'data/accounting-master/r05-vintage-admission-20261018/reconciliation.json')
    assert len(vintage['rows']) == 192 and all(r['as_of_admission'] is False for r in vintage['rows'])
    cases = check()
    a, o = load(REVIEW / 'assessment-successor.json'), load(REVIEW / 'operation-successor.json')
    assert (len(a['rows']), len(a['interactions']), len(o['rows'])) == (53, 6, 46)
    assert a['readiness'] == o['readiness'] == 'not_ready'
    checks = {'candidate_scales': 9, 'source_anchors': anchor_count, 'actually_viewed_pages': 1,
        'passed_case_count': cases['passed_case_count'],
        'protected_files': len(p['protected']), 'tracked_dirty_paths': len(dirty),
        'actual_cutoff_scale_admissions': 0, 'historical_vintage_admissions': 0,
        'empirical_execution': False, 'whole_rows_closed': 0, 'readiness': 'not_ready'}
    return p, cases, checks


HEADER = """## 23 October 2026 — E3 total-assets candidates checked

Current question: future OCF predictive accuracy for the same nine companies,
next full fiscal year, pre-start cutoff and equal company weights. Nine annual
consolidated asset-scale candidates now have dates, units and source anchors.
They are examples, not admitted cutoff inputs. Each correctly normalised
loss is dimensionless; no cross-company exchange rate is required.
Next: latest interim scale candidates and exact availability evidence, with
EU legal-text and company2027 policy gaps retained. No user choice is pending.

"""
FRONTIER = """The total-assets scale inquiry is complete at
data/accounting-master/r05-asset-scale-candidates-20261023/: nine FY2025
annual consolidated totals,24 anchors and one actually viewed source page.
Parent/group, reporting date, units and comparative revisions are distinct.
Seven exact cases check unit/currency cancellation and supplied-date selection.
The initial cross-company currency prerequisite was wrong and repaired before
calculation: compatible loss/asset ratios are dimensionless. Future reporting-
currency changes still require an explicit transformation. No actual cutoff
scale or historical-byte admission follows.

Next E3 dependency: map latest retained interim total-assets candidates beside
their existing timing-role evidence, then follow concrete exact-version release
leads. The EU regulation and issuer2027 classifications remain specific source
questions. Future law, refit/service, inference and resources remain open.
All192 historical-byte admissions remain false. No whole row closes or empirical
study runs. Safe replay: verify.py without flags; completed stages frozen.
No user choice is pending and no global continuation veto has fired.

"""


def edits(p):
    result = []
    for n in p['controls']:
        before = (U / 'controls-before' / n).read_text()
        assert (R / n).read_bytes() == (U / 'controls-before' / n).read_bytes(), n
        marker = 'Next E3 dependency: inspect same-perimeter positive total-assets scale\n'
        assert before.count(marker) == 1, n
        start = before.index(marker)
        end = before.index('Completed review evidence:', start)
        after = before[:start] + FRONTIER + before[end:]
        start = after.index('## 23 October 2026 — E3 UK adoption source checked')
        end = after.index('## 22 October 2026', start)
        result.append((n, after[:start] + HEADER + after[end:]))
    return result


def record(p, cases, checks, seconds):
    for n in ('reference-results.json', 'checks.json', 'run-manifest.json', 'completion.json', 'controls-after'):
        assert not (U / n).exists(), n
    assert not SUPPLEMENT.exists()
    changes = edits(p)
    for n in ('proposal.md', 'result.md', 'review.md'):
        assert (U / n).is_file()
    write(U / 'reference-results.json', cases)
    write(U / 'checks.json', checks)
    prefix = 'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B '
    supporting_commands = ['pdftoppm -f 226 -l 226 -r 110 -singlefile -png data/financial-report-benchmark/documents/munich_re/munich_re-2025-annual/original.pdf ' + rel(U / 'munich-balance-sheet-page226')]
    now = datetime.now(timezone.utc)
    write(U / 'run-manifest.json', {'git_commit': p['head'], 'branch': p['branch'],
        'environment': sys.executable, 'python': platform.python_version(),
        'cpu_gpu': 'CPU only; GPU devices intentionally hidden; standard library reference',
        'data_version': 'Retained FY2025 annual statements; candidates.json exact source bindings',
        'random_seeds': 'N/A deterministic exact scale identities and fictional selection', 'started_utc': p['started_utc'],
        'recorded_utc': now.isoformat(), 'wall_time_seconds': (now - datetime.fromisoformat(p['started_utc'])).total_seconds(),
        'wall_time_scope': 'preparation through completion including analysis', 'verification_seconds': seconds,
        'commands': [prefix + rel(U / n) for n in ('prepare.py', 'record_candidates.py', 'reference.py', 'verify.py')]
            + [prefix + rel(U / 'verify.py') + ' --record'],
        'source_acquisition_extraction_render_commands': supporting_commands,
        'visual_inspection': 'tools.view_image on munich-balance-sheet-page226.png; actually viewed',
        'plan': rel(PLAN), 'result': rel(U / 'result.md'), 'review': rel(U / 'review.md'),
        'output_paths': [rel(U), rel(SUPPLEMENT)], 'read_only_replay': prefix + rel(U / 'verify.py')})
    write(SUPPLEMENT, {'scope': 'annual total-assets source candidates and compatible scale semantics',
        'plan': bind(PLAN), 'proposal': bind(U / 'proposal.md'), 'result': bind(U / 'result.md'),
        'review': bind(U / 'review.md'), 'checks': checks, 'candidate_version': '3.48',
        'readiness': 'not_ready', 'whole_rows_closed': 0, 'independent_human_acceptance': 'pending'})
    for n, after in changes:
        snapshot = U / 'controls-after' / n
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        with snapshot.open('x') as f:
            f.write(after)
        (R / n).write_text(after)
    assert check_all()[1:] == (cases, checks)
    paths = [p for p in U.rglob('*') if p.is_file() and '__pycache__' not in p.parts] + [PLAN, SUPPLEMENT]
    write(U / 'completion.json', {'status': 'complete_documentary_asset_scale_candidates', 'checks': checks,
        'bindings': {rel(p): sha(p) for p in sorted(paths)},
        'replay_policy': 'Read only; immutable snapshots; no rewriting completed hashes'})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    start = time.monotonic()
    p, cases, checks = check_all()
    if args.record:
        record(p, cases, checks, time.monotonic() - start)
    if (U / 'completion.json').exists():
        complete = load(U / 'completion.json')
        assert complete['checks'] == load(U / 'checks.json') == checks
        assert load(U / 'reference-results.json') == cases
        for n, d in complete['bindings'].items():
            assert sha(R / n) == d, n
        status = 'recorded and verified' if args.record else 'read-only replay passed'
    else:
        edits(p)
        status = 'read-only preflight passed; not recorded'
    print(json.dumps({'status': status, **checks}))


if __name__ == '__main__':
    main()
