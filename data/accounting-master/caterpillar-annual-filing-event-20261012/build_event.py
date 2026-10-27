"""Separate the SEC 2024 10-K event from the selected annual-report wrapper."""
import hashlib
import json
import re
import time
from datetime import datetime
from pathlib import Path

import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
START = time.monotonic()
SEC_SHA = 'e6def01c8247684bdcbbfa010ed5c9e621d42177961ada3904629c2f1e455d45'
SELECTED_SHA = '3a38651c724016bca792bef165fd42bb09d9b033d23718372a2599378768e925'
URL = 'https://data.sec.gov/submissions/CIK0000018230.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not (OUT / 'completion.json').exists(), 'Closed unit stays frozen'
    source = ROOT / 'data/financial-report-benchmark/landing/caterpillar' / (SEC_SHA + '.json')
    pdf = ROOT / 'data/financial-report-benchmark/documents/caterpillar/caterpillar-2024-annual/original.pdf'
    source_access = json.loads((ROOT / 'data/financial-report-benchmark/source-access.json').read_text())
    inventory = json.loads((ROOT / 'data/accounting-master/publication-evidence-20261011/selected-date-inventory.json').read_text())
    coverage = json.loads((ROOT / 'data/financial-report-benchmark/coverage.json').read_text())
    submissions = json.loads(source.read_text())
    recent = submissions['filings']['recent']
    access = [r for r in source_access if r.get('url') == URL]
    selected = [r for r in inventory if r['document_id'] == 'caterpillar-2024-annual']
    covered = [r for r in coverage['rows'] if r['document_id'] == 'caterpillar-2024-annual']
    checks = []

    def ck(name, value):
        checks.append({'name': name, 'passed': bool(value)})

    ck('official SEC source identity', sha(source) == SEC_SHA)
    ck('official SEC access record', len(access) == 1 and access[0]['http_status'] == 200
       and access[0]['status'] == 'ok' and access[0]['sha256'] == SEC_SHA)
    ck('Caterpillar CIK identity', int(submissions['cik']) == 18230
       and submissions['name'].upper().startswith('CATERPILLAR INC'))
    forms = recent['form']
    indices = [i for i, form in enumerate(forms) if form in ('10-K', '10-K/A')
               and recent['reportDate'][i] == '2024-12-31']
    original = [i for i in indices if forms[i] == '10-K']
    ck('one original target 10-K', len(original) == 1)
    ck('no target-year amendment in inspected recent rows', len(indices) == 1)
    i = original[0] if original else None
    event = ({k: recent[k][i] for k in ['form', 'reportDate', 'filingDate', 'acceptanceDateTime',
                                        'accessionNumber', 'primaryDocument']} if i is not None else {})
    ck('dated official filing event', event.get('filingDate') == '2025-02-14'
       and event.get('accessionNumber') == '0000018230-25-000008'
       and event.get('primaryDocument') == 'cat-20241231.htm')
    try:
        acceptance = datetime.fromisoformat(event['acceptanceDateTime'].replace('Z', '+00:00'))
    except (KeyError, ValueError):
        acceptance = None
    ck('separate acceptance clock', acceptance is not None
       and event.get('acceptanceDateTime') == '2025-02-14T19:36:30.000Z')
    ck('one selected inventory row', len(selected) == 1 and selected[0]['selected_date_status'] == 'not_verified')
    ck('one selected coverage row', len(covered) == 1 and covered[0]['source_url'].startswith('https://www.annualreports.com/'))
    ck('selected PDF hash', sha(pdf) == SELECTED_SHA and selected[0]['selected_sha256'] == SELECTED_SHA
       and covered[0]['sha256'] == SELECTED_SHA)
    with fitz.open(pdf) as doc:
        ck('selected annual wrapper 112 pages', len(doc) == 112)
        pages = {n: ' '.join(doc[n-1].get_text().split()) for n in [1, 3, 10, 11, 110, 111]}
        (OUT / 'rendered').mkdir(exist_ok=True)
        renders = []
        for n in [3, 11, 110]:
            image = OUT / 'rendered' / f'selected-page-{n}.png'
            doc[n-1].get_pixmap(matrix=fitz.Matrix(1.35, 1.35)).save(image)
            renders.append({'pdf_page': n, 'image': str(image.relative_to(ROOT)), 'sha256': sha(image)})
    ck('annual wrapper before 10-K cover', '2024 ANNUAL REPORT' in pages[1].upper()
       and 'FORM 10-K' not in pages[1].upper() and 'FORM 10-K' not in pages[10].upper())
    ck('embedded 10-K begins at PDF 11', 'FORM 10-K' in pages[11].upper()
       and 'CATERPILLAR INC.' in pages[11].upper()
       and 'For the fiscal year ended December 31, 2024' in pages[11])
    ck('signed 10-K identifies February chief executive',
       'FORM 10-K Signatures' in pages[110] and 'February 14, 2025' in pages[110]
       and 'D. James Umpleby III Chairman of the Board and Chief Executive Officer' in pages[110])
    ck('undated wrapper identifies another CEO', 'CEO MESSAGE' in pages[3]
       and 'Joseph E. Creed Chief Executive Officer' in pages[3])
    ck('later annual-report wrapper after form signatures', 'CORPORATE GOVERNANCE' in pages[111]
       and 'Joseph E. Creed CEO of Caterpillar Inc.' in pages[111])
    ck('no selected-file date promotion', selected[0]['selected_date'] is None)
    failed = [r['name'] for r in checks if not r['passed']]
    ledger = {
        'official_source': {'url': URL, 'path': str(source.relative_to(ROOT)),
                            'sha256': SEC_SHA, 'captured_at': access[0]['captured_at'] if access else None},
        'event': event,
        'selected_report': {'path': str(pdf.relative_to(ROOT)), 'sha256': SELECTED_SHA,
                            'source_url': covered[0]['source_url'] if covered else None,
                            'date_status_before': selected[0]['selected_date_status'] if selected else None,
                            'whole_file_publication_date': 'not_verified',
                            'byte_as_of_admission': 'none'},
        'page_boundaries': {'annual_wrapper_before_form_pdf_pages': [1, 10],
                            'embedded_10k_cover_pdf_page': 11,
                            'embedded_10k_signatures_pdf_page': 110,
                            'annual_wrapper_after_form_pdf_page': 111},
        'mixed_content_observation': 'Annual wrapper names Joseph E. Creed CEO; embedded 10-K signatures dated 2025-02-14 name D. James Umpleby III CEO. Exact wrapper publication date is not inferred.',
        'renders': renders, 'frozen_date_inventory_counts_unchanged': {'verified': 56, 'unverified': 136},
    }
    (OUT / 'event.json').write_text(json.dumps(ledger, indent=2) + '\n')
    (OUT / 'checks.json').write_text(json.dumps({'checks': checks, 'passed': len(checks)-len(failed),
                                                 'failed': failed, 'wall_seconds': time.monotonic()-START}, indent=2) + '\n')
    print(json.dumps({'passed': len(checks)-len(failed), 'failed': failed,
                      'filing_date': event.get('filingDate'), 'selected_date': 'not_verified'}))
    raise SystemExit(bool(failed))


if __name__ == '__main__':
    main()
