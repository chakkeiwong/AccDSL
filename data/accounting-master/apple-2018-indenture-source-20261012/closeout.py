"""Bind the four observed retrievals without admitting a contract body."""
import datetime
import hashlib
import json
import platform
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SRC = OUT / 'sources'
assert not (OUT / 'completion.json').exists()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
b = json.loads((OUT / 'baseline.json').read_text())
checks = []
def ck(name, value):
    checks.append({'name': name, 'passed': bool(value)})

observed = [
    ('justia-index', 'html', 'https://contracts.justia.com/companies/apple-inc-102/', 403, 5450, 0.927957, 'challenge; index identity not established'),
    ('exact-title-search', 'html', 'https://www.google.com/search?q=%22Apple%22+%22November+5%2C+2018%22+%22Indenture%22', 200, 92794, 0.341155, 'JavaScript/redirection page; no inspectable contract lead'),
    ('exact-title-bing', 'xml', 'https://www.bing.com/search?q=%22Apple%22+%22November+5%2C+2018%22+%22Indenture%22&format=rss', 200, 5469, 0.389061, 'nonresponsive gym results; not negative search evidence'),
    ('onecle-index', 'html', 'https://contracts.onecle.com/apple/', 403, 358, 0.967853, 'access forbidden; index identity not established'),
]
attempts = []
for name, ext, url, status, size, seconds, verdict in observed:
    body, headers = SRC / (name + '.' + ext), SRC / (name + '.headers')
    ck(name + ' response size', body.stat().st_size == size)
    ck(name + ' HTTP status', int(re.findall(r'HTTP/\S+ (\d+)', headers.read_text())[-1]) == status)
    command = ['curl', '--location', '--silent', '--show-error', '--connect-timeout', '8', '--max-time', '25',
        '--max-filesize', '12000000', '--dump-header', str(headers.relative_to(ROOT)),
        '--output', str(body.relative_to(ROOT)), '--write-out',
        '%{http_code} %{content_type} %{size_download} %{time_total} %{url_effective}\n', url]
    attempts.append({'name': name, 'url': url, 'command': command, 'execution': 'trusted exec; recorded from observed tool result',
        'exit_code': 0, 'http_status': status, 'response_bytes': size, 'curl_wall_seconds': seconds,
        'body': str(body.relative_to(ROOT)), 'sha256': sha(body), 'headers': str(headers.relative_to(ROOT)),
        'headers_sha256': sha(headers), 'response_saved_at_utc': datetime.datetime.fromtimestamp(body.stat().st_mtime, datetime.timezone.utc).isoformat(),
        'time_scope': 'filesystem response save time, not publication or filing time', 'disposition': verdict})
    if ext == 'html':
        text = BeautifulSoup(body.read_bytes(), 'html.parser').get_text(' ', strip=True)
        (SRC / (name + '.txt')).write_text(text + '\n')
save('attempts.json', attempts)
target = json.loads((OUT / 'target.json').read_text())
ck('exact target remains unresolved', target['id'] == 'annual.exhibit.4.19' and target['document_status'] == 'unresolved_target')
ck('target accession and filename', '0001193125-18-317844' in target['target_links'][0] and 'd644900dex41_htm' in target['target_links'][0])
ck('four discovery requests', len(attempts) == 4)
ck('no old source route retried', all('sec.gov/Archives' not in a['url'] and 'edgar-online.com' not in a['url'] for a in attempts))
ck('no refused host retried', len({a['url'].split('/')[2] for a in attempts}) == 4)
ck('Justia challenge is not target', 'Just a moment' in (SRC / 'justia-index.txt').read_text())
ck('Google parsed page has no target', 'Indenture' not in (SRC / 'exact-title-search.txt').read_text())
search = json.loads((SRC / 'exact-title-bing.json').read_text())
ck('Bing results nonresponsive', bool(search) and all('snapfitness' in r['link'] for r in search))
ck('Onecle refused body', '403 Forbidden' in (SRC / 'onecle-index.txt').read_text())
for p, h in b['inputs'].items():
    ck('protected input ' + p, sha(ROOT / p) == h)
case = json.loads((ROOT / 'docs/design/cases/apple/continuation-20261007/case-supplement-v1.json').read_text())
ck('frozen forty target count', sum(r['document_status'] == 'unresolved_target' for r in case['reference_frontier']) == 40)
failed = [r['name'] for r in checks if not r['passed']]
save('source-checks.json', {'checks': checks, 'passed': len(checks)-len(failed), 'failed': failed,
     'scope': 'Identity/preservation/access-result checks, not successful source acquisition'})
assert not failed, failed
old = '''Seek the exact Apple 5 November 2018 indenture, incorporated as annual
Exhibit 4.19 from S-3 accession 0001193125-18-317844, through a new public
contract-index source. Distinguish mirror identity from official-byte
equivalence; do not retry the failed SEC or EDGAR Online routes. Preserve
Version 2.46 and the frozen forty-target frontier. Plan:
`docs/plans/accounting-apple-2018-indenture-source-20261012.md`.'''
new = '''Inspect the retained AASB 17 direct-participation and variable-fee provisions,
including guarantees and the distinction between payoff, fulfilment cash flows
and CSM. Preserve the historical edition boundary and Version 2.46. The Apple
2018 indenture still lacks inspectable text; its four new discovery requests
yielded no usable lead. Continue under:
`docs/plans/accounting-insurance-vfa-source-20261012.md`.'''
note = '''## Latest Apple 2018 indenture source attempt

Four bounded discovery requests yielded two access refusals, a JavaScript page
and unrelated RSS results. No contract body or usable body link was acquired;
the old SEC and EDGAR Online routes were not repeated. Exhibit 4.19 and the
frozen forty-target frontier remain unresolved. This is a source-specific
acquisition failure, not evidence that the document or its terms are absent.
Version 2.46 and not_ready remain; continue retained-source insurance work.
Result: `data/accounting-master/apple-2018-indenture-source-20261012/result.md`.

'''
prepared = []
for r in b['pointer_snapshots']:
    p = ROOT / r['live']
    assert sha(p) == r['sha256'] == sha(ROOT / r['snapshot'])
    s = p.read_text()
    anchor = '## Latest OTSL source inquiry\n\n'
    assert s.count(anchor) == 1
    s = s.replace(anchor, note + anchor, 1)
    if p.name != 'accounting-continuation-requirements-20261007.md':
        assert s.count(old) == 1
        s = s.replace(old, new, 1)
    if p.name == 'accounting-master-current.md':
        s = s.replace('next unit seeks the exact Apple 2018 indenture through a new source',
            'Apple indenture access attempt complete without a body; next unit inspects retained AASB 17 variable-fee conditions', 1)
        s = s.replace('Seek the exact 5 November 2018 Apple indenture through a new public source, preserving mirror/official identity limits.',
            'The exact 5 November 2018 Apple indenture remains source-blocked after four new discovery requests; require a usable new lead before retrying.', 1)
        s = s.replace('the next rotation seeks the exact Apple 2018 debt contract.',
            'the Apple debt-contract inquiry remains blocked; the next rotation inspects retained direct-participation and guarantee conditions.', 1)
        s = s.replace('1. Follow the direct next plan: seek the exact Apple 2018 indenture through\n   a new public source after the completed Version 2.46 integration.',
            '1. Follow the direct next plan: inspect retained AASB 17 direct-participation,\n   guarantee and variable-fee conditions after the Apple source-specific block.', 1)
    prepared.append((p, r, s))
rows = []
for p, r, s in prepared:
    p.write_text(s)
    q = OUT / 'pointers-after' / r['live'];q.parent.mkdir(parents=True, exist_ok=True);q.write_bytes(p.read_bytes())
    rows.append({'live': r['live'], 'snapshot': str(q.relative_to(ROOT)), 'sha256': sha(q)})
save('controls-after.json', rows)
plans = ['docs/plans/accounting-apple-2018-indenture-source-20261012.md', 'docs/plans/accounting-insurance-vfa-source-20261012.md']
paths = [p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts] + [ROOT / p for p in plans]
now = datetime.datetime.now(datetime.timezone.utc)
m = {'git_commit': b['git_commit'], 'started_utc': b['started_utc'], 'closed_utc': now.isoformat(),
    'plans': plans, 'result': str((OUT / 'result.md').relative_to(ROOT)),
    'commands': 'attempts.json contains the four actual trusted curl commands; closeout via python3 ' + str(Path(__file__).relative_to(ROOT)),
    'environment': {'python': sys.executable, 'version': platform.python_version(), 'parsing': 'BeautifulSoup and stdlib ElementTree'},
    'cpu_gpu': 'CPU-only file/HTML processing; no ML framework imported or device probe',
    'data_version': 'Frozen FY2024 Apple exhibit frontier and four new public responses',
    'random_seeds': 'N/A: deterministic source inspection',
    'wall_seconds': {'retrieval_sum': sum(a['curl_wall_seconds'] for a in attempts), 'elapsed_including_review': (now-datetime.datetime.fromisoformat(b['started_utc'])).total_seconds()},
    'input_hashes': b['inputs'], 'artifact_hashes': {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(paths))},
    'source_acquired': False, 'readiness': 'not_ready', 'next_plan': plans[-1]}
save('run-manifest.json', m)
for p, h in (m['input_hashes'] | m['artifact_hashes']).items(): assert sha(ROOT / p) == h
save('completion.json', {'status': 'bounded source inquiry complete; exact target remains blocked', 'source_checks': len(checks), 'failed': 0,
    'source_acquired': False, 'manifest_sha256': sha(OUT / 'run-manifest.json'), 'bound_artifacts': len(m['artifact_hashes']),
    'readiness': 'not_ready', 'next_plan': plans[-1]})
print(json.dumps({'checks': len(checks), 'artifacts': len(m['artifact_hashes']), 'source_acquired': False, 'readiness': 'not_ready'}))
