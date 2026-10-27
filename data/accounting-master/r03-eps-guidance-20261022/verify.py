"""Freeze the bounded access inquiry once, or replay its hashes read-only."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

U = Path(__file__).resolve().parent
R = U.parents[2]
P = R / 'data/accounting-master/readability-repair-20261022-theta'
PLAN = R / 'docs/plans/accounting-r03-eps-guidance-20261022.md'
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
    assert sha(R / '.git/index') == p['index_sha256']
    rows = [x for x in subprocess.check_output(['git', 'status', '--porcelain=v1', '--untracked-files=no', '-z'], cwd=R, text=True).split('\0') if x]
    assert all(x[:2] == ' M' for x in rows) and {x[3:] for x in rows} == set(p['tracked_dirty'])
    for name, digest in p['tracked_dirty'].items():
        if name not in p['controls']:
            assert sha(R / name) == digest, name
    a, o = load(P / 'assessment-successor.json'), load(P / 'operation-successor.json')
    assert len(a['rows']) == 53 and len(a['interactions']) == 6 and len(o['rows']) == 46
    assert a['readiness'] == 'not_ready' and all(not x['full_requirement_closed'] for x in o['rows'])
    return p

def record(p):
    assert not any((U / n).exists() for n in ('completion.json', 'acquisition-manifest.json', 'run-manifest.json', 'r08-supplement.json'))
    entries = [
        ('discovery-1', 'https://www.google.com/search?q=IAS+33+profit+sharing+nonadditive+diluted+earnings+sequencing', 200, 93097, 0.303487, 4000000, 'navigation shell; no usable result list'),
        ('discovery-2', 'https://www.bing.com/search?q=IAS+33+%22profit-sharing%22+%22diluted%22', 200, 125399, 0.859541, 4000000, 'unrelated result list; unusable discovery'),
        ('ifrscommunity-eps', 'https://ifrscommunity.com/knowledge-base/earnings-per-share/', 403, 6078, 0.309571, 6000000, 'Cloudflare access block; no technical article')]
    receipts = []
    for stem, url, status, size, seconds, maximum, disposition in entries:
        body, headers = U / 'sources' / (stem + '.html'), U / 'sources' / (stem + '.headers')
        assert body.stat().st_size == size
        assert str(status) in headers.read_text()
        receipts.append(dict(url=url, effective_url=url, status=status, bytes=size, curl_seconds=seconds,
            body=bind(body), headers=bind(headers), disposition=disposition, technical_source_admitted=False,
            command=['curl', '--location', '--silent', '--show-error', '--max-time', '45', '--max-filesize', str(maximum),
                     '--dump-header', rel(headers), '--output', rel(body), '--write-out', '%{http_code} %{url_effective} %{size_download} %{time_total}\n', url]))
    write('acquisition-manifest.json', dict(date='2026-10-22', trusted_network=True, automatic_retries=0, requests=receipts,
        technical_sources_acquired=0, scope='Access/discovery evidence only; not a literature-absence result'))
    write('r08-supplement.json', dict(candidate_version='3.48', candidate_pdf=a_pdf(), readiness='not_ready',
        obligations=bind(P / 'assessment-successor.json'), operations=bind(P / 'operation-successor.json'),
        counts=dict(obligations=53, interactions=6, operations=46, whole_rows_closed=0),
        source_status='no_new_technical_text', method_status='general_nonadditive_selection_not_evaluated',
        evidence=[bind(U / 'result.md'), bind(U / 'acquisition-manifest.json')],
        next_action='Derive the exact additive boundary of the supplied threshold-bonus model under a new audited plan'))
    write('run-manifest.json', dict(git_commit=p['head'], branch=p['branch'], environment=sys.executable,
        cpu_gpu='CPU-only parsing; GPU devices intentionally hidden', seeds='N/A source inquiry',
        started_utc=p['started_utc'], recorded_utc=datetime.now(timezone.utc).isoformat(),
        wall_seconds_requests=sum(x['curl_seconds'] for x in receipts),
        commands=['prepare.py', *[x['command'] for x in receipts], 'verify.py --record', 'verify.py --refresh', 'verify.py'],
        data_version='Historical EPS evidence unchanged; three new response bodies', plan=bind(PLAN), result=bind(U / 'result.md'),
        outputs=[rel(U / n) for n in ('acquisition-manifest.json', 'r08-supplement.json', 'result.md')]))
    files = [f for f in U.rglob('*') if f.is_file() and '__pycache__' not in f.parts] + [PLAN]
    write('completion.json', dict(bindings={rel(f): sha(f) for f in sorted(files)}, status='bounded_source_attempt_complete'))

def a_pdf():
    a = load(P / 'assessment-successor.json')
    return dict(path=a['candidate_pdf'], sha256=a['candidate_pdf_sha256'])

def refresh(p):
    assert not (U / 'controls-after').exists()
    old = '''Next: continue independently ready internal method/source preparation, beginning
with the existing nonadditive EPS discriminators and a bounded source/theory
inquiry under a new audited plan. Preserve their refused general-selector
status until an argument addresses the actual counterexamples.'''
    new = '''The bounded EPS guidance inquiry is complete at
data/accounting-master/r03-eps-guidance-20261022/: three retained requests,
no usable technical text. Search responses were unusable and the public article
returned403. No absence-of-literature conclusion or new selection method
follows. Safe replay: verify.py without flags; do not repeat these routes.

Next: derive and check the exact additive boundary of the supplied threshold-
bonus EPS model under a new audited plan. This can establish when the existing
additive method's premises hold; it cannot choose a general nonadditive selector.
Preserve P80 and both strict ordering/stability discriminators.'''
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
p = check()
if args.record:
    record(p)
for name, digest in load(U / 'completion.json')['bindings'].items():
    assert sha(R / name) == digest, name
if args.refresh:
    refresh(p)
print(json.dumps(dict(status='recorded' if args.record else 'controls refreshed' if args.refresh else 'read-only replay passed',
    requests=3, technical_sources=0, protected_files=len(p['protected']), whole_rows_closed=0, readiness='not_ready')))
