"""Preserve unsuccessful source discovery without an absence inference."""
import hashlib
import json
import platform
import subprocess
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2) + '\n')

def main():
    start = time.monotonic()
    assert not (OUT / 'completion.json').exists()
    baseline = json.loads((OUT / 'baseline.json').read_text())
    request_rows = [
        ('discovery-trusted', 'https://www.bing.com/search', {'q': '"财会〔2025〕12号" site:gov.cn'}, 200, 'nonresponsive unrelated history links', 1.193637),
        ('title-search', 'https://www.google.com/search', {'q': '"关于进一步贯彻落实新保险合同会计准则的通知"'}, 200, 'JavaScript/retry page', .423423),
        ('government-search', 'https://sousuo.www.gov.cn/sousuo/search.shtml', {'searchWord': '关于进一步贯彻落实新保险合同会计准则的通知'}, 200, 'unexecuted client template, not zero verified matches', 1.216719),
        ('government-search-script', 'https://sousuo.www.gov.cn/sousuo/search.js?7ccf1b283456b56c1ff0', {}, 200, 'public search script only; query not executed', .623479),
        ('discovery-rss', 'https://www.bing.com/search', {'q': '进一步贯彻落实 新保险合同 会计准则 财会 2025 12', 'format': 'rss'}, 200, 'nonresponsive unrelated numerical-zero links', 2.150665),
        ('discovery-html', 'https://html.duckduckgo.com/html/', {'q': '"关于进一步贯彻落实新保险合同会计准则的通知"'}, 202, 'challenge; no results obtained', .671388),
    ]
    checks = []
    def ck(name, ok):
        checks.append({'name': name, 'passed': bool(ok)})
        assert ok, name
    sources = OUT / 'sources'
    receipts = []
    for prefix, url, query, status, finding, seconds in request_rows:
        headers = (sources / (prefix + '.headers')).read_text()
        ck(prefix + ' response status', str(status) in headers.splitlines()[0])
        bodies = [p for p in sources.glob(prefix + '.*') if p.suffix in ['.html', '.xml', '.js']]
        ck(prefix + ' one retained body', len(bodies) == 1 and bodies[0].stat().st_size <= 5000000)
        receipts.append({'method': 'GET', 'base_url': url, 'query': query, 'http_status': status,
                         'body': str(bodies[0].relative_to(ROOT)), 'body_sha256': sha(bodies[0]),
                         'execution': 'trusted', 'max_time_seconds': 45, 'max_bytes': 5000000,
                         'transfer_seconds': seconds, 'disposition': finding})
    ck('challenge retained', 'challenge-form' in (sources / 'discovery-html.html').read_text())
    for old in baseline['pointer_snapshots']:
        ck('snapshot ' + old['live'], sha(ROOT / old['snapshot']) == old['sha256'])
        ck('current result pointer ' + old['live'], 'asbe25-operative-notice-20261012/result.md' in (ROOT / old['live']).read_text())
    candidate = ROOT / 'docs/design/proposal/manuscript-junior-classification-20261012/accounting-product-proposal.pdf'
    ck('candidate unchanged', sha(candidate) == baseline['current_candidate_sha256'])
    write('access-receipts.json', {'requests': receipts, 'distinct_urls': 6, 'attempts': 7,
          'sandbox_attempt': {'route': 'discovery', 'exit_code': 6, 'error': 'Could not resolve host: www.bing.com', 'disposition': 'sandbox evidence; trusted retry completed'},
          'operative_source_obtained': False, 'source_absence_established': False})
    write('checks.json', {'checks': checks, 'passed': len(checks), 'failed': 0,
                          'meaning': 'access-record and preservation checks, not notice-source validity'})
    plan = 'docs/plans/accounting-asbe25-operative-notice-20261012.md'
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in OUT.rglob('*') if p.is_file() and p.suffix != '.pyc'}
    hashes[plan] = sha(ROOT / plan)
    write('run-manifest.json', {'recorded_at': '2026-10-12', 'git_commit': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
          'plan': plan, 'result': str((OUT / 'result.md').relative_to(ROOT)),
          'environment': {'python': platform.python_version(), 'cpu_gpu': 'CPU-only source inspection; no framework import or device detection', 'seeds': 'N/A deterministic documentary inquiry'},
          'data_version': 'six exact retained public discovery responses; body hashes in access-receipts.json',
          'command': 'python3 data/accounting-master/asbe25-operative-notice-20261012/closeout.py',
          'network_commands': 'bounded curl GETs with exact queries and limits in access-receipts.json; headers and available curl transfer JSON retained',
          'wall_seconds': {'successful_transfers': sum(r[-1] for r in request_rows), 'closeout_before_manifest': time.monotonic()-start},
          'artifact_hashes': hashes, 'controls_at_closeout': {r['live']: sha(ROOT / r['live']) for r in baseline['pointer_snapshots']},
          'operative_source_obtained': False, 'readiness': 'not_ready'})
    write('completion.json', {'status': 'closed_bounded_source_route_unresolved', 'record_checks': len(checks), 'failed': 0,
                              'manifest_sha256': sha(OUT / 'run-manifest.json'), 'readiness': 'not_ready'})
    print(json.dumps({'record_checks': len(checks), 'operative_source_obtained': False, 'failed': 0}))

if __name__ == '__main__':
    main()
