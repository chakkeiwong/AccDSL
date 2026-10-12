"""Add located temporal evidence and a bounded annual-CFR comparison."""
import hashlib
import json
import re
import time
from pathlib import Path

import fitz
from lxml import etree

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
S = OUT / 'sources'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

def main():
    assert not (OUT / 'source-checks.json').exists()
    start = time.monotonic()
    checks = []
    def ck(name, condition):
        checks.append({'name': name, 'passed': bool(condition)})

    receipts = json.loads((OUT / 'access-receipts.json').read_text())
    for receipt in receipts['attempts']:
        for key in ['body', 'headers']:
            if key in receipt and receipt[key]:
                path = Path(receipt[key])
                path = (S if len(path.parts) == 1 else ROOT) / path
                digest = receipt[key + '_sha256']
                ck(receipt.get('id', 'sandbox') + ' ' + key,
                   (not path.exists()) if digest is None else sha(path) == digest)
    ledger = json.loads((OUT / 'source-ledger.json').read_text())
    for section in ledger['sections']:
        source = ROOT / section['source']
        node = etree.parse(str(source)).xpath(section['xpath'])[0]
        paragraphs = [' '.join(''.join(c.itertext()).split()) for c in node]
        ck('section ' + section['section'], sha(source) == section['source_sha256']
           and paragraphs == [p['text'] for p in section['paragraphs']]
           and '\n'.join(paragraphs) + '\n' == (ROOT / section['normalized_text']).read_text())
    by_section = {s['section']: s for s in ledger['sections']}
    for condition in ledger['conditions']:
        ck('condition ' + condition['id'],
           by_section[condition['section']]['paragraphs'][condition['paragraph_index']]['text'] == condition['quote'])
    renders = json.loads((OUT / 'renders.json').read_text())
    for row in renders:
        ck('source/render ' + row['raw'], all(sha(ROOT / row[k]) == row[k + '_sha256']
           for k in ['source', 'raw', 'render'])
           and fitz.open(ROOT / row['source'])[row['pdf_page'] - 1].get_text('text', sort=False)
           == (ROOT / row['raw']).read_text())

    spans = []
    def span(identifier, raw_name, first, last, meaning):
        row = next(x for x in renders if Path(x['raw']).name == raw_name)
        raw = (ROOT / row['raw']).read_text()
        begin = raw.index(first)
        end = raw.index(last, begin) + len(last)
        spans.append({'id': identifier, 'source': row['source'], 'source_sha256': row['source_sha256'],
                      'pdf_page': row['pdf_page'], 'raw': row['raw'], 'raw_sha256': row['raw_sha256'],
                      'start': begin, 'end_exclusive': end, 'quote': raw[begin:end], 'interpretation': meaning})

    span('rule-effective-and-optional-dates', 'fr-final-rule-page-1.txt',
         'Banking organizations subject to the', '1, 2026. \nFOR FURTHER INFORMATION CONTACT:',
         'The final rule permits election from 1 January 2026; its effective date is 1 April 2026. The trailing contact heading only delimits the quote.')
    span('issuer-reported-election', 'jpmorgan-2025-adoption-page-93.txt',
         'The final rule,', '1, 2026.',
         'The Firm reports its election effective 1 January. Later disclosure does not establish earlier public availability or every entity-specific fact.')
    span('occ-part6-amendment', 'fr-final-rule-page-41.txt',
         '■4. In § 6.4 revise paragraphs', 'Federal Reserve System',
         'The stated OCC amendment replaces two specified clauses. The revised well-capitalized leverage clause has 5% leverage, without the old additional 6% supplementary leverage condition. This is not the undercapitalized test.')
    span('occ-part3-payout-choice', 'fr-final-rule-page-41.txt',
         '(c) Calculation of maximum payout', '(2) Leverage buffer.',
         'For the stated bank population, maximum payout uses the lowest of two buffer-based payout ratios. Full Part 3 definitions and application remain a separate dependency.')
    span('issuer-capital-payout-warning', 'jpmorgan-2025-adoption-page-95.txt',
         'Failure to maintain an SLR equal to or greater than the', 'executive officers.',
         'The issuer separately describes payout limits. This is issuer evidence, not a complete legal computation.')
    for item in spans:
        raw = (ROOT / item['raw']).read_text()
        ck('located temporal span ' + item['id'], raw[item['start']:item['end_exclusive']] == item['quote'])

    # Remove only PDF line-wrap hyphens, page headers and punctuation for this
    # comparison. Keep all original bytes and require every paragraph to match.
    annual_raw = '\n'.join((S / f'govinfo-cfr2025-5-64-page-{i}.txt').read_text() for i in [1, 2])
    annual = re.sub(r'(?m)^(?:393|394|Comptroller of the Currency, Treasury|12 CFR Ch\. I \(1–1–25 Edition\)|§ 5\.(?:64|65))\s*$', '', annual_raw)
    def norm(text):
        text = re.sub(r'-\s*\n\s*', '', text)
        return re.sub(r'[^a-z0-9]', '', text.lower())
    annual_norm = norm(annual)
    comparisons = []
    for number in [f'5.{i}' for i in range(60, 67)]:
        for index, paragraph in enumerate(by_section[number]['paragraphs']):
            if paragraph['element'] != 'P':
                continue
            needle = norm(paragraph['text'])
            offset = annual_norm.find(needle)
            comparisons.append({'section': number, 'paragraph_index': index,
                                'annual_normalized_start': offset, 'normalized_characters': len(needle),
                                'matched': offset >= 0})
            ck(f'annual/API wording {number}/{index}', offset >= 0)
    baseline = json.loads((OUT / 'baseline.json').read_text())
    old_plan = 'docs/plans/accounting-national-bank-dividend-authority-20261012.md'
    ck('original source plan snapshot', sha(OUT / 'plan-before-adaptive-audit.md') == baseline['inputs'][old_plan])
    for rel, digest in baseline['inputs'].items():
        if rel != old_plan:
            ck('protected input ' + rel, sha(ROOT / rel) == digest)
    for row in baseline['pointer_snapshots']:
        ck('protected pointer ' + row['live'], sha(ROOT / row['snapshot']) == row['sha256'])
    save('temporal-evidence.json', {'spans': spans,
         'printed_pages': {'fr_page_1': 55248, 'fr_page_40': 55287, 'fr_page_41': 55288,
                           'issuer_page_93': 91, 'issuer_page_95': 93},
         'scope': 'Located quotations and scoped author interpretations; no bank capacity or complete legal applicability conclusion.'})
    save('annual-cfr-comparison.json', {'comparisons': comparisons,
         'annual_pdf': str((S / 'govinfo-cfr2025-5-64.pdf').relative_to(ROOT)),
         'annual_edition': '1 January 2025', 'api_requested_date': '2026-01-01',
         'normalization': 'PDF line-wrap hyphens and headers removed; lowercase alphanumerics compared. Originals retained.',
         'scope': 'Every operative P paragraph of sections 5.60–5.66; excludes 5.67, all intermediate amendments and other sections.'})
    failures = [x['name'] for x in checks if not x['passed']]
    save('source-checks.json', {'checks': checks, 'passed': len(checks) - len(failures), 'failed': failures,
                              'wall_seconds': time.monotonic() - start, 'scope': 'Documentary integrity only.'})
    print(json.dumps({'passed': len(checks) - len(failures), 'failed': failures,
                      'located_temporal_spans': len(spans), 'annual_paragraphs': len(comparisons)}))
    raise SystemExit(bool(failures))

if __name__ == '__main__':
    main()
