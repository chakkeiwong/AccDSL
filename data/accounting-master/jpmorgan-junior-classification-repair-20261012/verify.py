"""Check the rendered Note 20 hierarchy and the two-year arithmetic bridge."""
import hashlib
import json
import time
from pathlib import Path

import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PDF = ROOT / 'data/accounting-master/jpmorgan-complete-filings-20261011/sources/jpmorgan-2025-10k.pdf'
OLD = ROOT / 'data/accounting-master/jpmorgan-debt-perimeter-20261012'
V236 = ROOT / 'data/accounting-master/accounting-proposal-v236-integration-20261012'
PDF_SHA = 'e16cdad03ca84732dbe21b2595c112e975d5a3f27bce9f394828160275bfe79c'
V236_SHA = '751965e694bb2f2825d49b53710753fc3797af2f646ce3f17d489767f13117c6'
START = time.monotonic()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not (OUT / 'completion.json').exists(), 'Closed unit stays frozen'
    checks = []

    def ck(name, value):
        checks.append({'name': name, 'passed': bool(value)})

    ck('retained 2025 PDF identity', sha(PDF) == PDF_SHA)
    old_manifest = json.loads((OLD / 'run-manifest.json').read_text())
    old_completion = json.loads((OLD / 'completion.json').read_text())
    ck('old source unit frozen', old_completion['manifest_sha256'] == sha(OLD / 'run-manifest.json'))
    image_rel = 'data/accounting-master/jpmorgan-debt-perimeter-20261012/rendered/page-283.png'
    ck('visually inspected page image frozen', sha(ROOT / image_rel) == old_manifest['artifact_hashes'][image_rel])
    ck('Version 2.36 PDF frozen', sha(ROOT / 'docs/design/proposal/manuscript-debt-perimeter-20261012/accounting-product-proposal.pdf') == V236_SHA)
    with fitz.open(PDF) as doc:
        page = doc[282]
        text = page.get_text()
        spans = [s for block in page.get_text('dict')['blocks'] if 'lines' in block
                 for line in block['lines'] for s in line['spans']]
    ck('correct Note and printed page', 'Note 20 – Long-term debt' in text and '\n281\n' in text)
    by_text = lambda value: [s for s in spans if s['text'].strip() == value]
    parent, subsidiaries, junior = (by_text(t) for t in
                                    ['Parent company', 'Subsidiaries', 'Junior subordinated debt:'])
    subtotals = by_text('Subtotal')
    total = [s for s in spans if s['text'].strip().startswith('Total long-term debt')]
    ck('one each of three bold table headings', all(len(x) == 1 and 'Bold' in x[0]['font']
                                                     for x in [parent, subsidiaries, junior]))
    ck('three separate subtotal rows', len(subtotals) == 3)
    if parent and subsidiaries and junior and len(subtotals) == 3 and total:
        y = lambda span: span['bbox'][1]
        ck('table hierarchy and junior band after subsidiary subtotal',
           y(parent[0]) < y(subtotals[0]) < y(subsidiaries[0]) <
           y(subtotals[1]) < y(junior[0]) < y(subtotals[2]) < y(total[0]))
        ck('three headings have same left alignment',
           max(s[0]['bbox'][0] for s in [parent, subsidiaries, junior]) -
           min(s[0]['bbox'][0] for s in [parent, subsidiaries, junior]) < 1)
    else:
        ck('table hierarchy and junior band after subsidiary subtotal', False)
        ck('three headings have same left alignment', False)
    for value in ['253,039', '238,023', '180,573', '161,792', '1,594', '1,603', '435,206', '401,418']:
        ck('Note 20 displayed ' + value, value in text)
    # Reopen the same retained PDF for the separate Note 33 page.
    with fitz.open(PDF) as doc:
        parent_debt = ' '.join(doc[311].get_text().split())
    ck('Note 33 parent-only comparator', all(v in parent_debt for v in ['Parent Company-only', '254,633', '239,626']))
    ck('2025 parent residual equals junior band', 254633 - 253039 == 1594)
    ck('2024 parent residual equals junior band', 239626 - 238023 == 1603)
    ck('2025 three-band consolidated sum', 253039 + 180573 + 1594 == 435206)
    ck('2024 three-band consolidated sum', 238023 + 161792 + 1603 == 401418)
    old_ledger = (OLD / 'source-ledger.json').read_text()
    ck('superseded ledger assigned wrong subsidiary key', 'subsidiary.junior.subtotal' in old_ledger)
    failed = [item['name'] for item in checks if not item['passed']]
    facts = {
        'source_pdf': str(PDF.relative_to(ROOT)), 'sha256': PDF_SHA,
        'note20': {'pdf_page': 283, 'printed_page': 281,
                   'bands_in_display_order': ['Parent company', 'Subsidiaries', 'Junior subordinated debt'],
                   'parent_2025_2024_usd_millions': [253039, 238023],
                   'subsidiaries_2025_2024_usd_millions': [180573, 161792],
                   'junior_separate_band_2025_2024_usd_millions': [1594, 1603],
                   'consolidated_2025_2024_usd_millions': [435206, 401418]},
        'note33': {'pdf_page': 312, 'printed_page': 310,
                   'parent_only_debt_2025_2024_usd_millions': [254633, 239626]},
        'interpretation': 'The junior band follows the Subsidiaries subtotal as a separate bold band; this table does not label it Subsidiaries. Legal issuer and accounting relation remain unverified.',
        'supersedes': 'The Subsidiaries junior-debt classification in the frozen debt-perimeter source unit and Version 2.36.'
    }
    (OUT / 'source-facts.json').write_text(json.dumps(facts, indent=2) + '\n')
    (OUT / 'checks.json').write_text(json.dumps({'checks': checks, 'passed': len(checks)-len(failed), 'failed': failed, 'wall_seconds': time.monotonic()-START}, indent=2) + '\n')
    print(json.dumps({'passed': len(checks)-len(failed), 'failed': failed}))
    raise SystemExit(bool(failed))


if __name__ == '__main__':
    main()
