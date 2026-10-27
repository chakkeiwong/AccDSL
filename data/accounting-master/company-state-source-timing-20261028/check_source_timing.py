"""Retained source identity and raw timing evidence; no historical admission."""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import argparse
import json
import subprocess
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[3]
PLAN = 'docs/plans/company-state-recovery-continuation-20261028.md'
HERE = 'data/accounting-master/company-state-source-timing-20261028'
P02 = 'docs/design/cases/apple/p02-v1/'
SOURCES = 'docs/design/cases/apple/continuation-20261007/sources/'


def bind(payload, receipt, path, url, kind):
    """Validate exact transport evidence without converting metadata into clocks."""
    if receipt.get('path') != path:
        return dict(status='invalid', reason='receipt_path')
    if receipt.get('sha256') != sha256(payload).hexdigest():
        return dict(status='invalid', reason='receipt_bytes')
    if receipt.get('url') != url or receipt.get('final_url') != url:
        return dict(status='invalid', reason='document_url')
    if receipt.get('http_status') != 200:
        return dict(status='unavailable_response', reason='http_status',
                    http_status=receipt.get('http_status'))
    if kind == 'json':
        try:
            parsed = json.loads(payload)
        except (ValueError, UnicodeDecodeError):
            return dict(status='invalid', reason='not_json')
        if type(parsed) is not dict or type(parsed.get('GetEdgarFilingListResult')) is not list:
            return dict(status='invalid', reason='feed_structure')
    if kind == 'zip' and not payload.startswith(b'PK'):
        return dict(status='invalid', reason='not_zip')
    if kind not in ('json', 'zip', 'html'):
        return dict(status='invalid', reason='unsupported_media')
    try:
        stamp = datetime.fromisoformat(receipt['retrieved_at'])
        if stamp.utcoffset() is None:
            raise ValueError('timezone absent')
    except (KeyError, ValueError, TypeError):
        return dict(status='unresolved', reason='acquisition_timestamp')
    return dict(status='retained_bytes_bound', path=path, url=url,
                sha256=receipt['sha256'], recorded_acquisition=receipt['retrieved_at'],
                acquisition_trust='saved receipt claim; not independent time attestation',
                historical_byte_availability=None, public_available_at=None,
                actor_receipt_at=None, source_admission=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    checks = []
    def check(name, actual, expected):
        checks.append(dict(name=name, passed=actual == expected, actual=actual, expected=expected))
    inputs = [Path(__file__), ROOT / PLAN]
    def read(path):
        inputs.append(ROOT / path)
        return json.loads((ROOT / path).read_text())
    def payload(path):
        inputs.append(ROOT / path)
        return (ROOT / path).read_bytes()

    acquisition = read(P02 + 'acquisition.json')
    feed_path = P02 + 'issuer-2024-feed.json'
    html_path = P02 + 'annual-2024-official.html'
    receipts = {}
    for path in (feed_path, html_path):
        matches = [r for r in acquisition['records'] if r.get('path') == path]
        check('unique receipt ' + path, len(matches), 1)
        if len(matches) != 1:
            raise ValueError('nonunique retained receipt')
        receipts[path] = matches[0]
    feed_raw = payload(feed_path)
    feed_receipt = receipts[feed_path]
    feed_binding = bind(feed_raw, feed_receipt, feed_path, feed_receipt['url'], 'json')
    check('valid feed binding', feed_binding['status'], 'retained_bytes_bound')
    rows = json.loads(feed_raw)['GetEdgarFilingListResult']
    matches = [r for r in rows if r.get('FilingId') == 17933082]
    check('unique filing', len(matches), 1)
    row = matches[0]
    for key, expected in [('StockSymbol', '0000320193'), ('FilingAgentName', 'APPLE INC.'),
                          ('FilingTypeMnemonic', '10-K'), ('EdgarFilingId', 11311336),
                          ('FilingDate', '11/01/2024 00:00:00'),
                          ('ReceivedDate', '11/01/2024 05:05:37')]:
        check('retained ' + key, row[key], expected)
    documents = row['DocumentList']
    check('unique document identities', len({d['FilingDocumentId'] for d in documents}), len(documents))
    routes = {}
    for kind in ('HTML', 'XBRL'):
        choices = [d for d in documents if d['DocumentType'] == kind]
        check('unique route ' + kind, len(choices), 1)
        routes[kind] = choices[0]['Url']
    html_binding = bind(payload(html_path), receipts[html_path], html_path, routes['HTML'], 'html')
    check('official HTML route binding', html_binding['status'], 'retained_bytes_bound')
    zip_path = SOURCES + 'annual-2024-taxonomy-trusted-v1.zip'
    zip_receipt = read(SOURCES + 'annual-2024-taxonomy-trusted-v1.receipt.json')
    zip_raw = payload(zip_path)
    zip_binding = bind(zip_raw, zip_receipt, zip_path, routes['XBRL'], 'zip')
    check('XBRL route binding', zip_binding['status'], 'retained_bytes_bound')
    check('ZIP discovery parent', zip_receipt['discovered_from'], feed_path)
    debt_manifest = read('data/accounting-master/company-state-debt-source-20261028/attempt-01/run-manifest.json')
    debt = read('data/accounting-master/company-state-debt-source-20261028/attempt-01/source-to-state.json')
    check('same debt source ZIP', debt_manifest['inputs'][zip_path], zip_binding['sha256'])
    with zipfile.ZipFile(ROOT / zip_path) as archive:
        instance = archive.read('aapl-20240928_htm.xml')
    check('same debt instance', sha256(instance).hexdigest(), debt['instance_sha256'])
    check('debt facts retained', len(debt['facts']), 13)

    rejected = []
    for year in ('2023', '2025'):
        path = SOURCES + 'issuer-' + year + '-trusted-v1.json'
        receipt = read(path.replace('.json', '.receipt.json'))
        raw = payload(path)
        outcome = bind(raw, receipt, path, receipt['url'], 'json')
        check('HTTP failure retained ' + year, outcome,
              dict(status='unavailable_response', reason='http_status', http_status=403))
        rejected.append(dict(path=path, sha256=sha256(raw).hexdigest(), outcome=outcome))
        forged = deepcopy(receipt)
        forged['http_status'] = 200
        check('HTML challenge is not JSON ' + year,
              bind(raw, forged, path, receipt['url'], 'json')['reason'], 'not_json')

    before = deepcopy(feed_receipt)
    for name, edit, expected in [
        ('path', {'path': html_path}, 'receipt_path'),
        ('bytes', {'sha256': '0' * 64}, 'receipt_bytes'),
        ('route', {'url': routes['HTML']}, 'document_url'),
        ('redirect', {'final_url': routes['HTML']}, 'document_url'),
        ('naive timestamp', {'retrieved_at': '2026-10-02T18:30:17'}, 'acquisition_timestamp')]:
        altered = dict(feed_receipt, **edit)
        check('negative ' + name,
              bind(feed_raw, altered, feed_path, feed_receipt['url'], 'json')['reason'], expected)
    check('receipt unchanged', feed_receipt, before)
    check('changed bytes rejected', bind(feed_raw + b' ', feed_receipt, feed_path,
                                        feed_receipt['url'], 'json')['reason'], 'receipt_bytes')
    for item in (feed_binding, html_binding, zip_binding):
        for key in ('historical_byte_availability', 'public_available_at', 'actor_receipt_at'):
            check(item['path'] + ':unknown ' + key, item[key], None)
        check(item['path'] + ':no admission', item['source_admission'], False)
    dependencies = read('data/accounting-master/company-cases-current-20261028/attempt-01/current-decisions.json')
    targets = read('data/accounting-master/selected-reading-history-20261027/attempt-01/result.json')
    check('all issuer dependency rows retained', len(dependencies['rows']), 15)
    check('no issuer target ready', all(r['original_target_ready'] is False for r in dependencies['rows']), True)
    check('all target obligations retained', sum(len(a['target_obligations']) for a in targets['attachments'].values()), 180)

    card = dict(profile='RetainedIssuerTimingEvidence/1', issuer='Apple Inc.',
        status='document_identity_bound_historical_time_unresolved',
        feed_record=deepcopy(row), feed_binding=feed_binding, html_binding=html_binding,
        xbrl_binding=zip_binding, rejected_responses=rejected,
        debt_source='data/accounting-master/company-state-debt-source-20261028/attempt-01/source-to-state.json',
        observed_raw_dates={k: row[k] for k in ('FilingDate', 'ReceivedDate')},
        document_create_dates=[dict(id=d['FilingDocumentId'], raw=d['CreateDate']) for d in documents],
        interpretation='Field names are retained as vendor assertions. No field is assigned SEC acceptance, first public availability, or actor receipt semantics.',
        missing=['Authoritative timestamp semantics and timezone for vendor fields',
                 'Evidence that the exact retained bytes were available at a historical cutoff',
                 'Actor-specific delivery, access and receipt evidence',
                 'Amendment/revision authority and predecessor identities'],
        source_admission=False, accounting_admission=False, actual_actor_knowledge=False,
        forecast_admission=False, probability_model=None, policy_input=None)
    failed = [c for c in checks if not c['passed']]
    manifest = dict(git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv], environment=sys.version,
        cpu_gpu='CPU-only source validation; no accelerator imports', random_seeds='N/A deterministic',
        data_version='Retained Apple2024 issuer feed, HTML, XBRL and acquisition receipts',
        utc=datetime.now(timezone.utc).isoformat(), wall_seconds=time.monotonic()-start,
        plan_file=PLAN, result_file=HERE+'/result.md',
        source_hashes={str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in inputs})
    verification = dict(status='fail' if failed else 'pass', checks=len(checks), failed=failed)
    for name, value in [('source-time-card.json', card), ('checks.json', checks),
                        ('verification.json', verification), ('run-manifest.json', manifest)]:
        (out / name).write_text(json.dumps(value, indent=2) + '\n')
    print(json.dumps(dict(verification, output=str(out))))
    return bool(failed)


if __name__ == '__main__':
    raise SystemExit(main())
