"""Bind a historical trust-debenture lead without transferring it to 2025."""
import hashlib
import json
import re
import time
from pathlib import Path

import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
START = time.monotonic()
SELECTED_SHA = '97b65690371b2d2b77187df8154f0b5997f95d676028dd2cb8a256ede5291871'
CURRENT_SHA = 'e16cdad03ca84732dbe21b2595c112e975d5a3f27bce9f394828160275bfe79c'
CURRENT = ROOT / 'data/accounting-master/jpmorgan-complete-filings-20261011/sources/jpmorgan-2025-10k.pdf'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not (OUT / 'completion.json').exists(), 'Closed unit stays frozen'
    coverage = json.loads((ROOT / 'data/financial-report-benchmark/coverage.json').read_text())
    matches = [r for r in coverage['rows'] if r['document_id'] == 'jpmorgan-2018-annual']
    assert len(matches) == 1
    row = matches[0]
    older = ROOT / row['local_path']
    checks = []

    def ck(name, value):
        checks.append({'name': name, 'passed': bool(value)})

    ck('selected corpus source identity', row['sha256'] == sha(older) == SELECTED_SHA)
    ck('selected corpus status', row['status'] == 'revalidated_verified')
    ck('retained 2025 source identity', sha(CURRENT) == CURRENT_SHA)
    with fitz.open(older) as doc:
        ck('selected 2018 page count', len(doc) == 342)
        page = doc[259]
        text = ' '.join(page.get_text().split())
        (OUT / 'rendered').mkdir(exist_ok=True)
        image = OUT / 'rendered/selected-2018-page-260.png'
        page.get_pixmap(matrix=fitz.Matrix(1.35, 1.35)).save(image)
    phrases = [
        'Junior subordinated deferrable interest debentures',
        'last remaining issuer of outstanding trust preferred securities',
        'was liquidated',
        '$475 million of trust preferred securities',
        '$15 million of trust common securities',
        'debentures previously held by the trust issuer were distributed pro rata',
        'The carrying value of the junior subordinated debt was $659 million',
        'December 31, 2018',
    ]
    for phrase in phrases:
        ck('2018 direct phrase ' + phrase[:42], phrase in text)
    ck('2018 printed page 258', re.search(r'\b258\b', text) is not None)
    with fitz.open(CURRENT) as doc:
        current_hits = {term: [i + 1 for i, p in enumerate(doc)
                               if term.lower() in ' '.join(p.get_text().split()).lower()]
                        for term in ['Junior subordinated debt', 'trust preferred securities',
                                     'junior subordinated deferrable interest debentures']}
        current_note = ' '.join(doc[282].get_text().split())
    ck('2025 junior term only at Note 20 table', current_hits['Junior subordinated debt'] == [283])
    ck('2025 trust-preferred and deferrable phrases absent in selected search',
       not current_hits['trust preferred securities'] and
       not current_hits['junior subordinated deferrable interest debentures'])
    ck('2025 junior band differs from dated 2018 carrying amount',
       '1,594' in current_note and 1594 != 659)
    ck('2025 current table still separately headed', 'Junior subordinated debt:' in current_note)
    failed = [x['name'] for x in checks if not x['passed']]
    evidence = {
        'historical_source': {'path': row['local_path'], 'sha256': SELECTED_SHA,
                              'issuer_url': row['source_url'], 'pdf_page': 260,
                              'printed_page': 258, 'render': str(image.relative_to(ROOT)),
                              'render_sha256': sha(image)},
        'current_source': {'path': str(CURRENT.relative_to(ROOT)), 'sha256': CURRENT_SHA,
                           'pdf_page': 283, 'printed_page': 281},
        'historical_observation': 'The last issuer trust was liquidated in September 2018; its previously held junior debentures were distributed to trust-security holders. The dated carrying value was USD 659 million at 2018 year-end.',
        'current_search_hits': current_hits,
        'boundary': 'The 2018 passage neither identifies every 2025 junior instrument nor explains the 2025 parent-only balance. The 2025 carrying amount is USD 1,594 million, not the dated 2018 amount.',
    }
    (OUT / 'evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    (OUT / 'checks.json').write_text(json.dumps({'checks': checks, 'passed': len(checks)-len(failed),
                                                 'failed': failed, 'wall_seconds': time.monotonic()-START}, indent=2) + '\n')
    print(json.dumps({'passed': len(checks)-len(failed), 'failed': failed,
                      'current_hits': current_hits}))
    raise SystemExit(bool(failed))


if __name__ == '__main__':
    main()
