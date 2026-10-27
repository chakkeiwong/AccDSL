"""Read-only source/protection replay; --record completes once."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

U = Path(__file__).resolve().parent
R = U.parents[2]
PLAN = R / 'docs/plans/accounting-r05-conditional-predictive-source-20261023.md'
REVIEW = R / 'data/accounting-master/readability-repair-20261022-theta'
SUPPLEMENT = REVIEW / 'r05-conditional-predictive-source-supplement.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(R))
bind = lambda p: {'path': rel(p), 'sha256': sha(p)}


def write(path, value):
    with path.open('x') as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
        f.write('\n')


def binding(value):
    path = R / value['path']
    assert sha(path) == value['sha256'], value['path']
    if 'bytes' in value:
        assert path.stat().st_size == value['bytes']


def check():
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    p = load(U / 'protection.json')
    for name, digest in p['protected'].items():
        assert sha(R / name) == digest, name
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip() == p['head']
    assert sha(R / '.git/index') == p['index_sha256']
    raw = subprocess.check_output(['git', 'status', '--porcelain=v1', '--untracked-files=no', '-z'], cwd=R, text=True)
    rows = [row for row in raw.split('\0') if row]
    assert all(row[:2] == ' M' for row in rows)
    assert {row[3:] for row in rows} == set(p['tracked_dirty'])
    for name, digest in p['tracked_dirty'].items():
        if name not in p['controls']:
            assert sha(R / name) == digest, name
    for name in p['controls']:
        assert sha(U / 'controls-before' / name) == p['tracked_dirty'][name]
    s = load(U / 'source-record.json')
    for b in [s['paper'], s['download'], s['text']] + s['rendered_bindings'] + s['generated_not_viewed'] + s['precedents']:
        binding(b)
    assert s['paper']['sha256'] == s['download']['sha256'] == '712ea4b631759231a36a7c6680131a4ce65d1500da5ebb7135e56989d85be2df'
    assert s['physical_pages'] == 38 and s['text_pages_inspected'] == list(range(1,39))
    assert s['rendered_pages_inspected'] == [11,12,14,24,33,34]
    assert len(s['rendered_bindings']) == 6 and len(s['generated_not_viewed']) == 1
    assert s['source_description_only'] and s['inference_admitted'] is False
    assert s['final_edition_equality'] == 'not_verified'
    text = (R / s['text']['path']).read_text()
    assert len(text.split('\f')) == 39 and 'This version: April 2003' in text
    assert len(s['anchors']) == 25
    for a in s['anchors']:
        first, last = a['character_span']
        assert text[first:last] == a['quote']
        assert text[:first].count('\f')+1 == a['page']
        assert a['lines_by_newline'] == [text[:first].count('\n')+1, text[:last].count('\n')+1]
    receipts = load(U / 'request-receipts.json')
    assert receipts['http_requests'] == len(receipts['requests']) == 8
    assert receipts['budget_exhausted'] is True
    assert receipts['local_invocation_failure']['http_request_sent'] is False
    assert [v['http_status'] for v in receipts['requests']] == [200,404,200,0,202,200,403,200]
    for row in receipts['requests']:
        binding(row['headers'])
        if row['body']:
            binding(row['body'])
            assert row['body']['bytes'] == row['download_bytes']
        else:
            assert row['id'] == 'bc-working-paper' and row['curl_exit'] == 28
        assert row['request_started_utc'] is None
        assert row['command_argv'][-1] == row['requested_url']
    cr = load(U / 'sources/crossref.body')['message']
    oa = load(U / 'sources/openalex.body')
    fw = load(U / 'sources/forward-metadata.body')['results']
    assert cr['title'] == ['Tests of Conditional Predictive Ability']
    assert [a['family'] for a in cr['author']] == ['Giacomini','White']
    assert oa['id'] == 'https://openalex.org/W2135150595' and oa['cited_by_count'] == 1664
    assert len(fw) == 8
    ledgers = ['source-support-ledger.md', 'citation-venue-ledger.md', 'backward-snowball-ledger.md',
               'forward-snowball-ledger.md', 'claim-support-ledger.md', 'omission-risk-register.md']
    for name in ledgers + ['source-reading.md', 'result.md', 'review.md']:
        assert (U / name).read_text().strip()
    choice = load(R / 'data/accounting-master/r05-repeated-origins-20261023/choice.json')
    assert choice['selected_design'] == 'repeated_origins' and choice['issuer_weights']['values'] is None
    assert all(choice['forecast_task'][k] is None for k in ('interval','cutoff','origin_grouping'))
    v = load(R / 'data/accounting-master/r05-vintage-admission-20261018/reconciliation.json')
    assert len(v['rows']) == 192 and all(x['as_of_admission'] is False for x in v['rows'])
    a, o = load(REVIEW / 'assessment-successor.json'), load(REVIEW / 'operation-successor.json')
    assert (len(a['rows']), len(a['interactions']), len(o['rows'])) == (53,6,46)
    assert a['readiness'] == o['readiness'] == 'not_ready'
    return p, {'http_requests': 8, 'technical_papers': 1, 'source_pages': 38,
               'viewed_pages': 6, 'source_anchors': 25, 'research_ledgers': 6, 'forward_metadata_items': 8,
               'protected_files': len(p['protected']), 'tracked_dirty_paths': len(rows),
               'vintage_admissions': 0, 'whole_rows_closed': 0, 'readiness': 'not_ready',
               'manuscript_changed': False, 'inference_admitted': False, 'runtime_admitted': False}


def record(p, checks):
    for path in (U / 'completion.json', U / 'checks.json', U / 'run-manifest.json', SUPPLEMENT):
        assert not path.exists() and path.parent.is_dir() and os.access(path.parent, os.W_OK), path
    assert not (U / 'controls-after').exists()
    replacement = '''The bounded conditional predictive-ability inquiry is complete at
data/accounting-master/r05-conditional-predictive-source-20261023/: the full
38-page April2003 Giacomini–White draft, both appendices, six actual page images,
25 anchors and six research ledgers. Its conditional-equality test and finite
estimation-window assumptions do not directly supply E3's one-sided margin
bound. Three literal draft details and unverified2006-edition equality remain.
Eight public requests are retained; publisher access failed. No inference,
empirical, manuscript or whole-row promotion. Read-only replay: verify.py.

Next: inspect the untried UCL institutional record already identified in the
retained OpenAlex locations as a specific published/accepted-edition lead.
Keep failed Cemmap/BC/UC/publisher routes bounded. Pending forecast-period and
company-weight choices still determine E3's next protocol; no answer, numerical
default or future law is inferred. Continue independent internal preparation.

'''
    marker = 'Next: use the pending forecast-period and company-weight answers to finalise'
    edits = []
    for name in p['controls']:
        target = R / name
        assert target.read_bytes() == (U / 'controls-before' / name).read_bytes()
        assert not target.is_symlink() and os.access(target, os.W_OK)
        text = target.read_text()
        assert text.count(marker) == 1
        first = text.index(marker)
        last = text.index('Completed review evidence:', first)
        edits.append((name, text[:first] + replacement + text[last:]))
    prefix = 'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B '
    write(U / 'checks.json', checks)
    write(U / 'run-manifest.json', {
        'git_commit': p['head'], 'branch': p['branch'], 'environment': sys.executable,
        'python': platform.python_version(), 'cpu_gpu': 'CPU only; GPU devices intentionally hidden for Python; no scientific framework imported',
        'data_version': 'April2003 working paper and exact retained HTTP responses; source-record.json/request-receipts.json',
        'seeds': 'N/A documentary reading; no stochastic computation', 'started_utc': p['started_utc'],
        'recorded_utc': datetime.now(timezone.utc).isoformat(),
        'wall_time': 'Whole reading/editing session not measured; per-request curl elapsed values in receipts; no wall time inferred from timestamps',
        'commands': [prefix+rel(U/'prepare.py'), 'Eight trusted curl commands retained as argv in request-receipts.json',
                     'One local curl option failure before network, recorded in receipts',
                     'pdftotext -layout sources/munich-working-paper.body sources/munich-working-paper.txt (paths rooted at unit)',
                     'pdfinfo sources/munich-working-paper.body (path rooted at unit)',
                     'pdftoppm -f 11 -l 14 -scale-to 1400 -png sources/munich-working-paper.body sources/theory (paths rooted at unit)',
                     'pdftoppm -f 24 -l 24 -scale-to 1400 -singlefile -png sources/munich-working-paper.body sources/proof-24 (paths rooted at unit)',
                     'pdftoppm -f 33 -l 34 -scale-to 1400 -png sources/munich-working-paper.body sources/figures (paths rooted at unit)',
                     prefix+rel(U/'record_sources.py'), prefix+rel(U/'verify.py'),
                     prefix+rel(U/'verify.py')+' --record', prefix+rel(U/'verify.py')],
        'stage_provenance': 'Preparation/acquisition/extraction/render/source recording completed once; preflight then one completion; default replay separately',
        'plan': rel(PLAN), 'result': rel(U/'result.md'), 'output': rel(U)})
    write(SUPPLEMENT, {
        'scope': 'Primary April2003 conditional predictive-ability source reading; no procedure selection',
        'candidate_version': '3.48', 'candidate_pdf': bind(R/'docs/design/proposal/manuscript-readability-20261022-theta/accounting-product-proposal.pdf'),
        'protected_assessment': bind(REVIEW/'assessment-successor.json'),
        'protected_operations': bind(REVIEW/'operation-successor.json'),
        'completed_author_review': bind(REVIEW/'regression/completion.json'),
        'all_original_obligations': 53, 'interactions': 6, 'operations': 46,
        'whole_rows_closed': 0, 'readiness': 'not_ready', 'plan': bind(PLAN),
        'result': bind(U/'result.md'), 'review': bind(U/'review.md'), 'checks': checks,
        'manuscript_changed': False, 'runtime_admitted': False,
        'inference_admitted': False, 'independent_human_acceptance': 'pending'})
    for name, after in edits:
        snapshot = U/'controls-after'/name
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        with snapshot.open('x') as f:
            f.write(after)
        (R/name).write_text(after)
    assert check()[1] == checks
    source = load(U/'source-record.json')
    files = [path for path in U.rglob('*') if path.is_file() and '__pycache__' not in path.parts] + [PLAN,SUPPLEMENT,R/source['paper']['path']]
    write(U/'completion.json', {'status': 'complete_source_reading_no_inference_admission', 'checks': checks,
        'bindings': {rel(path):sha(path) for path in sorted(files)},
        'control_replay_policy': 'Immutable before/after snapshots; live controls may advance in successor units'})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    p, checks = check()
    if args.record:
        record(p, checks)
    if (U/'completion.json').exists():
        c = load(U/'completion.json')
        for name, digest in c['bindings'].items():
            assert sha(R/name) == digest, name
        assert c['checks'] == checks == load(U/'checks.json')
        status = 'recorded and verified' if args.record else 'read-only replay passed'
    else:
        status = 'read-only preflight passed; not yet recorded'
    print(json.dumps({'status':status, **checks}))


if __name__ == '__main__':
    main()
