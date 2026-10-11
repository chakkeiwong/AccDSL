"""Bind a regulator filing event and a distinct issuer-hosted filing copy."""
import hashlib
import json
import shutil
import time
from datetime import datetime
from pathlib import Path

import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PDF = 'docs/design/proposal/manuscript-junior-classification-20261012/accounting-product-proposal.pdf'
PDF_SHA = '9e6d0b433ebdbc30b65a17122dcbb2834b3c63d195b31ffaf2bea68eaa1fc880'
CONTROLS = ['docs/plans/accounting-master-checkpoint.md', 'docs/plans/accounting-master-current.md',
            'docs/plans/accounting-continuation-requirements-20261007.md', 'data/accounting-master/next-plan.md']
INVENTORY = 'data/accounting-master/publication-evidence-20261011/selected-date-inventory.json'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')

def main():
    start = time.monotonic()
    assert not (OUT / 'baseline.json').exists(), 'Preserve prior outputs'
    checks = []
    def ck(name, ok):
        checks.append({'name': name, 'passed': bool(ok)})
        assert ok, name
    source = OUT / 'sources/sec-submissions.json'
    issuer = OUT / 'sources/issuer-2023-20f.pdf'
    ck('retained SEC source hash', sha(source) == '16422cffcffd788aa14086c5c46e1bf64306584b41c32778d3b0a0fb46054944')
    ck('retained issuer source hash', sha(issuer) == 'ca44e0bf0f4a953e56219f557f8035f34a78952e0291b803cdf65f2bdf93dbc3')
    data = json.loads(source.read_text())
    ck('HSBC parent CIK and name', int(data['cik']) == 1089113 and data['name'] == 'HSBC HOLDINGS PLC')
    recent = data['filings']['recent']
    fields = ['form', 'reportDate', 'filingDate', 'acceptanceDateTime', 'accessionNumber', 'primaryDocument']
    ck('parallel SEC arrays', all(len(recent[f]) == 1000 for f in fields))
    matches = [i for i in range(1000) if recent['form'][i] in ('20-F', '20-F/A')
               and recent['reportDate'][i] == '2023-12-31']
    originals = [i for i in matches if recent['form'][i] == '20-F']
    amendments = [i for i in matches if recent['form'][i] == '20-F/A']
    ck('one original 2023 event', originals == [935])
    ck('no 2023 amendments in inspected recent array', not amendments)
    event = {k: recent[k][935] for k in fields}
    ck('exact accession', event['accessionNumber'] == '0001089113-24-000004')
    ck('exact primary document', event['primaryDocument'] == 'hsbc-20231231.htm')
    ck('distinct recorded clocks', event['filingDate'] == '2024-02-22'
       and event['acceptanceDateTime'] == '2024-02-23T01:38:50.000Z')
    ck('acceptance clock parseable', datetime.fromisoformat(event['acceptanceDateTime'].replace('Z', '+00:00')).tzinfo is not None)
    coverage = json.loads((ROOT / 'data/financial-report-benchmark/coverage.json').read_text())
    candidates = [r for r in coverage['rows'] if r['document_id'] == 'hsbc-2023-annual']
    ck('one selected annual report', len(candidates) == 1)
    selected = candidates[0]
    ck('selected PDF identity', sha(ROOT / selected['local_path']) == selected['sha256'])
    with fitz.open(issuer) as filing, fitz.open(ROOT / selected['local_path']) as annual:
        filing_cover = ' '.join(filing[0].get_text().split())
        annual_cover = ' '.join(annual[0].get_text().split())
        ck('issuer filing has 490 pages', len(filing) == 490)
        ck('selected annual has 450 pages', len(annual) == 450)
        ck('issuer filing cover identity', 'HSBC Holdings plc' in filing_cover and 'FORM 20-F' in filing_cover)
        ck('issuer filing cover period', 'For the fiscal year ended December 31, 2023' in filing_cover)
        ck('issuer cover filing-date statement', 'As filed with the Securities and Exchange Commission on February 22, 2024.' in filing_cover)
        ck('selected annual cover anchors; render review required', 'HSBC Holdings plc' in annual_cover
           and 'Annual Report and' in annual_cover and 'Accounts 2023' in annual_cover)
        rendered = OUT / 'rendered'
        rendered.mkdir()
        filing[0].get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False).save(rendered / 'issuer-20f-cover.png')
        annual[0].get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False).save(rendered / 'selected-annual-cover.png')
    ck('different file bytes', sha(issuer) != selected['sha256'])
    inv = json.loads((ROOT / INVENTORY).read_text())
    ck('selected annual date unverified', next(r for r in inv if r['document_id'] == 'hsbc-2023-annual')['selected_date_status'] == 'not_verified')
    ck('frozen 56/136 count', len(inv) == 192 and sum(r['selected_date_status'].startswith('not_verified') for r in inv) == 136)
    ck('candidate unchanged', sha(ROOT / PDF) == PDF_SHA)
    snapshots = []
    for rel in CONTROLS:
        dest = OUT / 'pointers-before' / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dest)
        snapshots.append({'live': rel, 'snapshot': str(dest.relative_to(ROOT)), 'sha256': sha(dest)})
    archive = 'data/financial-report-benchmark/landing/hsbc/c4207a0649d2233fd39bce12b803715ec9e70f30fa4b0246e7bbfb7bb9715bb9.html'
    frozen = ['data/financial-report-benchmark/coverage.json', INVENTORY, archive]
    write('baseline.json', {'current_pdf': PDF, 'current_pdf_sha256': PDF_SHA, 'pointer_snapshots': snapshots,
                           'frozen_sources': {rel: sha(ROOT / rel) for rel in frozen}})
    write('event.json', {'official_source': {'path': str(source.relative_to(ROOT)), 'sha256': sha(source),
                         'url': 'https://data.sec.gov/submissions/CIK0001089113.json'},
          'recent_row_index': 935, 'recent_filing_date_range': [min(recent['filingDate']), max(recent['filingDate'])],
          'recent_rows_inspected': 1000, 'event': event, 'target_amendments_in_scope': amendments,
          'selected_report': selected, 'selected_cover_text': annual_cover,
          'selected_cover_visual_review': 'Rendered cover says HSBC Holdings plc / Annual Report and / Accounts 2023; extracted 2024 is not visible in the inspected rendering',
          'issuer_filing_copy': {'path': str(issuer.relative_to(ROOT)), 'sha256': sha(issuer), 'pages': 490,
                                'url': 'https://www.hsbc.com/-/files/hsbc/investors/hsbc-results/2023/annual/pdfs/hsbc-holdings-plc/240222-hsbc-holdings-plc-form-20-f.pdf',
                                'archive_source': archive, 'archive_input_line': 8301, 'cover_text': filing_cover},
          'correspondence': 'Cover agrees with regulator issuer, form, period and filing date; full SEC-byte equivalence not checked',
          'selected_publication_date': 'not_verified', 'selected_byte_admissions': 0,
          'frozen_date_inventory_counts_unchanged': {'verified': 56, 'unverified': 136},
          'renders': [{'path': str(p.relative_to(ROOT)), 'sha256': sha(p)} for p in sorted(rendered.glob('*.png'))]})
    write('checks.json', {'checks': checks, 'passed': len(checks), 'failed': 0, 'wall_seconds': time.monotonic() - start})
    print(json.dumps({'source_checks': len(checks), 'failed': 0, 'filing_date': event['filingDate'], 'byte_admissions': 0}))

if __name__ == '__main__':
    main()
