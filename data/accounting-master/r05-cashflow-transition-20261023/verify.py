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
from reference import check

U = Path(__file__).resolve().parent
R = U.parents[2]
PLAN = R / 'docs/plans/accounting-r05-cashflow-transition-20261023.md'
REVIEW = R / 'data/accounting-master/readability-repair-20261022-theta'
SUPPLEMENT = REVIEW / 'r05-cashflow-transition-supplement.json'
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
    sources = load(U / 'source-record.json')
    assert len(sources['requests']) == 2
    anchor_count = 0
    for source in sources['requests']:
        for key in ('original', 'text', 'response_headers'):
            assert sha(R / source[key]['path']) == source[key]['sha256']
        assert (R / source['original']['path']).stat().st_size == source['download_bytes']
        lines = (R / source['text']['path']).read_text().split('\n')
        for anchor in source['anchors']:
            assert '\n'.join(lines[anchor['start_line'] - 1:anchor['end_line']]) == anchor['quote']
            anchor_count += 1
    assert '35        Cash flows' in sources['requests'][1]['anchors'][-2]['quote']
    assert '64           AASB 18' in sources['requests'][1]['anchors'][-1]['quote']
    for page in sources['actually_viewed_pages']:
        assert sha(R / page['path']) == page['sha256']
    vintage = load(R / 'data/accounting-master/r05-vintage-admission-20261018/reconciliation.json')
    assert len(vintage['rows']) == 192 and all(r['as_of_admission'] is False for r in vintage['rows'])
    cases = check()
    a, o = load(REVIEW / 'assessment-successor.json'), load(REVIEW / 'operation-successor.json')
    assert (len(a['rows']), len(a['interactions']), len(o['rows'])) == (53, 6, 46)
    assert a['readiness'] == o['readiness'] == 'not_ready'
    checks = {'official_sources': 2, 'source_anchors': anchor_count, 'actually_viewed_pages': 2,
        'exact_example_count': cases['exact_example_count'],
        'protected_files': len(p['protected']), 'tracked_dirty_paths': len(dirty),
        'issuer_applicability_admissions': 0, 'historical_vintage_admissions': 0,
        'empirical_execution': False, 'whole_rows_closed': 0, 'readiness': 'not_ready'}
    return p, cases, checks


HEADER = """## 23 October 2026 — E3 cash-flow transition mechanism checked

Current question: future OCF predictive accuracy for the same nine companies,
next full fiscal year, pre-start cutoff and equal company weights. Source-bound
measurement and conditional temporal/refit feasibility are documented. The
AASB18 AppendixD inquiry now distinguishes reconciliation changes from cash-flow
reclassification, with 12 anchors, two viewed pages and five exact examples.
Next: EU/UK adoption evidence and company classification policies; then exact
source/scale availability and inference. No user choice is pending.

"""
FRONTIER = """The cash-flow transition technical inquiry is complete at
data/accounting-master/r05-cashflow-transition-20261023/: two official AASB
sources, 12 anchors and two actually viewed redline pages. New107.33A/34A-D
can change reported OCF through interest/dividend classification while total
cash stays fixed; a changed indirect-reconciliation starting point alone
establishes no net-OCF change. Specified-business and group-level assessments
are preserved. Five exact synthetic examples pass. The Australian technical
text and attributed IFRS correspondence establish no EU/UK or issuer admission.

Next E3 dependency: inspect jurisdiction-specific adoption evidence for the
EU/UK reporters and then their actual cash-flow policies. Preserve dated
first-release targets and later comparative revisions separately. Exact source
and scale availability, future law, refit/service, inference and resources
remain open. All192 historical-byte admissions remain false. No empirical
ranking or whole-row promotion. Read-only replay: verify.py; completed one-time
stages frozen. No user choice is pending; no global continuation veto fired.

"""


def edits(p):
    result = []
    for n in p['controls']:
        before = (U / 'controls-before' / n).read_text()
        assert (R / n).read_bytes() == (U / 'controls-before' / n).read_bytes(), n
        marker = 'Next E3 dependency: inspect dated IFRS18/IAS7 technical amendments and their\n'
        assert before.count(marker) == 1, n
        start = before.index(marker)
        end = before.index('Completed review evidence:', start)
        after = before[:start] + FRONTIER + before[end:]
        start = after.index('## 23 October 2026 — E3 temporal feasibility checked')
        end = after.index('## 22 October 2026', start)
        result.append((n, after[:start] + HEADER + after[end:]))
    return result


def record(p, cases, checks, seconds):
    for n in ('reference-results.json', 'checks.json', 'run-manifest.json', 'completion.json', 'controls-after'):
        assert not (U / n).exists(), n
    assert not SUPPLEMENT.exists()
    changes = edits(p)
    for n in ('comparison.md', 'result.md', 'review.md'):
        assert (U / n).is_file()
    write(U / 'reference-results.json', cases)
    write(U / 'checks.json', checks)
    prefix = 'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B '
    supporting_commands = []
    for source in load(U / 'source-record.json')['requests']:
        supporting_commands.append('curl --location --silent --show-error --max-time 45 --max-filesize 12000000 '
            + '--dump-header ' + source['response_headers']['path'] + ' --output ' + source['original']['path']
            + " --write-out 'http_code=%{http_code} bytes=%{size_download} url=%{url_effective}\\n' " + source['requested_url'])
    supporting_commands += [prefix + rel(U / 'extract_html.py') + ' ' + rel(U / 'sources/aasb18-page.html'),
        'pdftotext -layout ' + rel(U / 'sources/aasb18-appendix-d.pdf') + ' ' + rel(U / 'sources/aasb18-appendix-d.txt'),
        'pdftoppm -f 27 -l 28 -r 115 -png ' + rel(U / 'sources/aasb18-appendix-d.pdf') + ' ' + rel(U / 'sources/amendments-page')]
    now = datetime.now(timezone.utc)
    write(U / 'run-manifest.json', {'git_commit': p['head'], 'branch': p['branch'],
        'environment': sys.executable, 'python': platform.python_version(),
        'cpu_gpu': 'CPU only; GPU devices intentionally hidden; standard library only',
        'data_version': 'June2024 AASB18 official page and AppendixD; exact source-record.json bindings',
        'random_seeds': 'N/A exact rational identities', 'started_utc': p['started_utc'],
        'recorded_utc': now.isoformat(), 'wall_time_seconds': (now - datetime.fromisoformat(p['started_utc'])).total_seconds(),
        'wall_time_scope': 'preparation through completion including analysis', 'verification_seconds': seconds,
        'commands': [prefix + rel(U / n) for n in ('prepare.py', 'reference.py', 'record_sources.py', 'verify.py')]
            + [prefix + rel(U / 'verify.py') + ' --record'],
        'source_acquisition_extraction_render_commands': supporting_commands,
        'visual_inspection': 'tools.view_image on existing amendments-page-027.png and -028.png; both actually viewed',
        'plan': rel(PLAN), 'result': rel(U / 'result.md'), 'review': rel(U / 'review.md'),
        'output_paths': [rel(U), rel(SUPPLEMENT)], 'read_only_replay': prefix + rel(U / 'verify.py')})
    write(SUPPLEMENT, {'scope': 'cash-flow amendments technical source comparison and exact identities',
        'plan': bind(PLAN), 'proposal': bind(U / 'comparison.md'), 'result': bind(U / 'result.md'),
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
    write(U / 'completion.json', {'status': 'complete_documentary_cashflow_transition_source', 'checks': checks,
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
