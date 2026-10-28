"""Match retained index references without pretending their bodies were read."""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import time
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parents[3]
H = Path(__file__).resolve().parent
PLAN = 'docs/plans/company-state-governing-notes-20261028.md'
SUPPLEMENT = 'docs/design/cases/apple/continuation-20261007/case-supplement-v1.json'
CARDS = 'data/accounting-master/company-state-note-instruments-20261028/attempt-01/source-instruments.json'

def digest(path): return sha256(path.read_bytes()).hexdigest()
def dump(path, value): path.write_text(json.dumps(value, indent=2) + '\n')

def main():
    started = time.monotonic()
    out = H / 'attempt-01'
    out.mkdir(exist_ok=False)
    source = json.loads((ROOT / SUPPLEMENT).read_text())
    cards = json.loads((ROOT / CARDS).read_text())
    checks = []
    def ck(name, actual, expected):
        checks.append(dict(name=name, passed=actual == expected, actual=actual, expected=expected))
    numbered = {r['number']: r for r in source['reference_frontier'] if r['id'].startswith('annual.')}
    # Independent expected index selection; dates/rates/maturities come from the inspected paragraphs.
    groups = [('4.5', [3], '2014-11-10', ['1.625% Notes due 2026']),
              ('4.8', [6, 8], '2015-07-31', ['3.05% Notes due 2029', '3.60% Notes due 2042']),
              ('4.9', [4], '2015-09-17', ['2.000% Notes due 2027']),
              ('4.15', [2, 5], '2017-05-24', ['0.875% Notes due 2025', '1.375% Notes due 2029']),
              ('4.21', [1, 7], '2019-11-15', ['0.000% Notes due 2025', '0.500% Notes due 2031'])]
    selected = ['4.2', '4.5', '4.8', '4.9', '4.15', '4.19', '4.21']
    dependencies = []
    sources = {ROOT / SUPPLEMENT, ROOT / CARDS, ROOT / PLAN, Path(__file__)}
    for number in selected:
        row = numbered[number]
        span = row['reference_source']
        original, extraction = ROOT / span['original_path'], ROOT / span['extraction_path']
        ck(number + '/original hash', digest(original), span['original_sha256'])
        ck(number + '/extraction hash', digest(extraction), span['extraction_sha256'])
        ck(number + '/exact index span', extraction.read_text()[span['start']:span['end']], span['quote'])
        ck(number + '/body remains unresolved', row['document_status'], 'unresolved_target')
        ck(number + '/body not inspected', row['semantic_status'], 'not_inspected')
        sources.update([original, extraction])
        link = row['target_links'][0]
        parsed = urlparse(link)
        accession = Path(parsed.path).stem
        dest = parse_qs(parsed.query)['dest'][0]
        ck(number + '/destination suffix', dest.endswith('_htm'), True)
        sec = 'https://www.sec.gov/Archives/edgar/data/320193/' + accession.replace('-', '') + '/' + dest[:-4] + '.htm'
        dependencies.append(dict(index_record=deepcopy(row), source_span_verified=True,
            primary_url_derived_from_retained_link=sec, retrieved=False, parsed=False,
            modeled=False, governing_relationship_admitted=False))
    links = []
    for number, indices, issued, labels in groups:
        row = numbered[number]
        ck(number + '/certificate issue date', [cards['rows'][i-1]['issue_date'] for i in indices], [issued] * len(indices))
        ck(number + '/exact coupon-maturity labels', all(s in row['description'] for s in labels), True)
        links.append(dict(series_ids=[cards['rows'][i-1]['id'] for i in indices],
            referenced_certificate=row['id'], issue_date=issued, matched_labels=labels,
            relationship='proposed_from_index_and_series_summary', certificate_body_inspected=False))
    ck('all eight mapped once', sorted(x for r in links for x in r['series_ids']),
       sorted(r['id'] for r in cards['rows']))
    ck('seventy original references preserved', len(source['reference_frontier']), 70)
    ck('no substitute2023 certificate', '4.28' in selected, False)
    ck('no substitute2021 indenture', any('2021' in numbered[n]['description'] for n in ['4.2', '4.19']), False)
    sec = next(d['primary_url_derived_from_retained_link'] for d in dependencies if d['index_record']['number']=='4.21')
    receipts = []
    for stem, trusted in [('2019-certificate', False), ('2019-certificate-trusted', True)]:
        body, headers = H / 'sources' / (stem + '.html'), H / 'sources' / (stem + '.headers')
        body_text = body.read_text()
        ck(stem + '/403 in headers', '403' in headers.read_text(), True)
        ck(stem + '/not certificate', 'Request Rate Threshold Exceeded' in body_text or 'Undeclared Automated Tool' in body_text, True)
        receipts.append(dict(url=sec, exit_code=0, http_status=403, bytes=body.stat().st_size,
            body=str(body.relative_to(ROOT)), body_sha256=digest(body),
            headers=str(headers.relative_to(ROOT)), headers_sha256=digest(headers),
            trusted=trusted, classification='access_denial_not_governing_document', acquisition_date='2026-10-28'))
        sources.update([body, headers])
    headers = H / 'sources/2019-certificate-mirror.headers'
    mirror = numbered['4.21']['target_links'][0]
    receipts.append(dict(url=mirror, exit_code=28, http_status=0, bytes_received=0,
        timeout_seconds=20, trusted=True, classification='timeout_no_body',
        headers=str(headers.relative_to(ROOT)), headers_sha256=digest(headers), acquisition_date='2026-10-28'))
    sources.add(headers)
    failed = [r for r in checks if not r['passed']]
    verdict = dict(status='fail' if failed else 'pass', checks=len(checks), failed=failed,
        matched_series=8, required_documents=7, recovered_governing_bodies=0,
        source_admission=False, no_global_continuation_veto=True)
    dump(out / 'verification.json', verdict)
    dump(out / 'checks.json', checks)
    dump(out / 'dependencies.json', dict(links=links, required_documents=dependencies,
        original_reference_frontier=deepcopy(source['reference_frontier']),
        original_coverage=deepcopy(source['coverage']), receipts=receipts,
        series_to_base_indenture_allocation=None, complete_debt_population=False))
    dump(out / 'run-manifest.json', dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=ROOT).strip(),
        command=['python3','-B',str(Path(__file__).relative_to(ROOT))], environment=platform.python_version(),
        cpu_gpu='CPU-only documentary checks; no GPU imports', random_seeds='N/A deterministic',
        data_version='Retained Apple2024 index and eight-series cards; three October28 access attempts',
        utc=datetime.now(timezone.utc).isoformat(), wall_seconds=time.monotonic()-started,
        plan_file=PLAN, result_file=str((H/'result.md').relative_to(ROOT)),
        source_hashes={str(p.relative_to(ROOT)):digest(p) for p in sorted(sources)}))
    (out / 'record.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(verdict))
    return bool(failed)

if __name__ == '__main__': raise SystemExit(main())
