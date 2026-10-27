"""Read-only replay; one-time documentary completion with preflighted controls."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import subprocess
import sys
import time

U = Path(__file__).resolve().parent
R = U.parents[2]
PLAN = R / 'docs/plans/accounting-r05-ifrs18-adoption-20261023.md'
REVIEW = R / 'data/accounting-master/readability-repair-20261022-theta'
SUPPLEMENT = REVIEW / 'r05-ifrs18-adoption-supplement.json'
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
    assert len(sources['requests']) == 12
    official_anchors = issuer_anchors = 0
    for source in sources['requests']:
        for key in ('original', 'text', 'headers'):
            if source[key] is not None:
                assert sha(R / source[key]['path']) == source[key]['sha256']
        assert (R / source['original']['path']).stat().st_size == source['bytes']
        if source['text'] is not None:
            lines = (R / source['text']['path']).read_text().split('\n')
            for anchor in source['anchors']:
                assert '\n'.join(lines[anchor['start_line']-1:anchor['end_line']]) == anchor['quote']
                official_anchors += 1
    for source in sources['issuer_sources']:
        for key in ('original', 'text'):
            assert sha(R / source[key]['path']) == source[key]['sha256']
        lines = (R / source['text']['path']).read_text().split('\n')
        for anchor in source['anchors']:
            assert '\n'.join(lines[anchor['start_line']-1:anchor['end_line']]) == anchor['quote']
            issuer_anchors += 1
        assert source['first_release_admitted'] is False and source['2027_policy_selected'] is False
    for page in sources['actually_viewed_pages']:
        assert sha(R / page['path']) == page['sha256']
    decision = ' '.join((U / 'sources/ukeb-decision.txt').read_text().split())
    for phrase in ('IAS 7 Statement of Cash Flows', '10 December 2025',
                   'must be used for financial years beginning on or after 1 January 2027',
                   'set out in the annex to this statement'):
        assert phrase in decision, phrase
    efrag = (U / 'sources/efrag-status.txt').read_text()
    assert all(date in efrag for date in ('13 February 2026', '16 February 2026', '1 January 2027'))
    assert sources['jurisdiction_status']['eu'].endswith('actual EU regulation not recovered')
    vintage = load(R / 'data/accounting-master/r05-vintage-admission-20261018/reconciliation.json')
    assert len(vintage['rows']) == 192 and all(r['as_of_admission'] is False for r in vintage['rows'])
    a, o = load(REVIEW / 'assessment-successor.json'), load(REVIEW / 'operation-successor.json')
    assert (len(a['rows']), len(a['interactions']), len(o['rows'])) == (53, 6, 46)
    assert a['readiness'] == o['readiness'] == 'not_ready'
    checks = {'requests': 12, 'http_200_responses': 10, 'official_source_anchors': official_anchors,
        'issuer_source_anchors': issuer_anchors, 'actually_viewed_pages': 2,
        'protected_files': len(p['protected']), 'tracked_dirty_paths': len(dirty),
        'uk_adoption_statement_inspected': True, 'eu_regulation_inspected': False,
        'issuer_2027_policy_admissions': 0, 'historical_vintage_admissions': 0,
        'empirical_execution': False, 'whole_rows_closed': 0, 'readiness': 'not_ready'}
    return p, checks


HEADER = """## 23 October 2026 — E3 UK adoption source checked

Current question: future OCF predictive accuracy for the same nine companies,
next full fiscal year, pre-start cutoff and equal company weights. The UK
IFRS18 adoption statement and selected adopted IAS7 amendments are inspected;
EU endorsement has EFRAG status evidence, while the actual EU regulation is
still unread. Three company-policy excerpts narrow the transition questions.
Next: independent asset-scale source candidates; retain EU legal-text and
company2027 policy gaps. No user choice is pending.

"""
FRONTIER = """The IFRS18 adoption inquiry is complete at
data/accounting-master/r05-ifrs18-adoption-20261023/: twelve requests,
16 official anchors, eight issuer anchors and two viewed redline pages.
The UK decision adopts IFRS18 and IAS7 amendments on10December2025, with
publication12December and required application from1January2027, earlier
permitted. Selected adopted technical paragraphs are inspected directly.
EFRAG reports EU endorsement13February2026/publication16February; the actual
EU regulation remains unread after an empty EUR-Lex search. No failed route
was repeated. Henkel/HSBC/Munich Re current policies do not determine all
future elections or transition effects.

Next E3 dependency: inspect same-perimeter positive total-assets scale
candidates in retained reports, preserving currency, units, date and exact-byte
availability limits. EU regulation text and company2027 policies remain source
questions; follow distinct precise leads only. Future law, service/refit,
inference and resources remain open. All192 historical-byte admissions stay
false. No whole row closes. Safe replay: verify.py without flags; completed
stages frozen. No user choice is pending or global continuation veto active.

"""


def edits(p):
    result = []
    for n in p['controls']:
        before = (U / 'controls-before' / n).read_text()
        assert (R / n).read_bytes() == (U / 'controls-before' / n).read_bytes(), n
        marker = 'Next E3 dependency: inspect jurisdiction-specific adoption evidence for the\n'
        assert before.count(marker) == 1, n
        start = before.index(marker)
        end = before.index('Completed review evidence:', start)
        after = before[:start] + FRONTIER + before[end:]
        start = after.index('## 23 October 2026 — E3 cash-flow transition mechanism checked')
        end = after.index('## 22 October 2026', start)
        result.append((n, after[:start] + HEADER + after[end:]))
    return result


def record(p, checks, seconds):
    for n in ('checks.json', 'run-manifest.json', 'completion.json', 'controls-after'):
        assert not (U / n).exists(), n
    assert not SUPPLEMENT.exists()
    changes = edits(p)
    for n in ('adoption-and-policy.md', 'result.md', 'review.md'):
        assert (U / n).is_file()
    write(U / 'checks.json', checks)
    prefix = 'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B '
    supporting_commands = []
    for source in load(U / 'source-record.json')['requests']:
        supporting_commands.append('curl --location --silent --show-error --max-time 45 --max-filesize 12000000 '
            + '--dump-header ' + source['headers']['path'] + ' --output ' + source['original']['path']
            + " --write-out 'http_code=%{http_code} bytes=%{size_download} url=%{url_effective}\\n' " + shlex.quote(source['requested_url']))
    for source in load(U / 'source-record.json')['requests']:
        if source['text'] is None:
            continue
        if source['original']['path'].endswith('.html'):
            supporting_commands.append(prefix + rel(U / 'extract_html.py') + ' ' + source['original']['path'])
        else:
            supporting_commands.append('pdftotext -layout ' + source['original']['path'] + ' ' + source['text']['path'])
    supporting_commands.append('pdftoppm -f 134 -l 135 -r 100 -png ' + rel(U / 'sources/ukeb-annex.pdf') + ' ' + rel(U / 'sources/ukeb-redline'))
    now = datetime.now(timezone.utc)
    write(U / 'run-manifest.json', {'git_commit': p['head'], 'branch': p['branch'],
        'environment': sys.executable, 'python': platform.python_version(),
        'cpu_gpu': 'CPU only; GPU devices intentionally hidden; standard library plus PyMuPDF for PDF-link inspection',
        'data_version': 'Official EFRAG/UKEB responses and retained2025 issuer reports; source-record.json',
        'random_seeds': 'N/A documentary source inspection', 'started_utc': p['started_utc'],
        'recorded_utc': now.isoformat(), 'wall_time_seconds': (now - datetime.fromisoformat(p['started_utc'])).total_seconds(),
        'wall_time_scope': 'preparation through completion including analysis', 'verification_seconds': seconds,
        'commands': [prefix + rel(U / n) for n in ('prepare.py', 'record_sources.py', 'verify.py')]
            + [prefix + rel(U / 'verify.py') + ' --record'],
        'source_acquisition_extraction_render_commands': supporting_commands,
        'visual_inspection': 'tools.view_image on existing ukeb-redline-134.png and -135.png; both actually viewed',
        'annotation_inspection': load(U / 'source-record.json')['pdf_annotation_inspection'],
        'plan': rel(PLAN), 'result': rel(U / 'result.md'), 'review': rel(U / 'review.md'),
        'output_paths': [rel(U), rel(SUPPLEMENT)], 'read_only_replay': prefix + rel(U / 'verify.py')})
    write(SUPPLEMENT, {'scope': 'UK adoption/selected technical support, EU status evidence and issuer policy boundaries',
        'plan': bind(PLAN), 'proposal': bind(U / 'adoption-and-policy.md'), 'result': bind(U / 'result.md'),
        'review': bind(U / 'review.md'), 'checks': checks, 'candidate_version': '3.48',
        'readiness': 'not_ready', 'whole_rows_closed': 0, 'independent_human_acceptance': 'pending'})
    for n, after in changes:
        snapshot = U / 'controls-after' / n
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        with snapshot.open('x') as f:
            f.write(after)
        (R / n).write_text(after)
    assert check_all()[1] == checks
    paths = [p for p in U.rglob('*') if p.is_file() and '__pycache__' not in p.parts] + [PLAN, SUPPLEMENT]
    write(U / 'completion.json', {'status': 'complete_documentary_ifrs18_adoption_inquiry', 'checks': checks,
        'bindings': {rel(p): sha(p) for p in sorted(paths)},
        'replay_policy': 'Read only; immutable snapshots; no rewriting completed hashes'})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    start = time.monotonic()
    p, checks = check_all()
    if args.record:
        record(p, checks, time.monotonic() - start)
    if (U / 'completion.json').exists():
        complete = load(U / 'completion.json')
        assert complete['checks'] == load(U / 'checks.json') == checks
        for n, d in complete['bindings'].items():
            assert sha(R / n) == d, n
        status = 'recorded and verified' if args.record else 'read-only replay passed'
    else:
        edits(p)
        status = 'read-only preflight passed; not recorded'
    print(json.dumps({'status': status, **checks}))


if __name__ == '__main__':
    main()
