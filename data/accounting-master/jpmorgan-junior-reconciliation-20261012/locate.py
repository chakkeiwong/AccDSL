"""Bounded page locator for the retained 2025 complete filing."""
import hashlib
import json
import re
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PDF = ROOT / 'data/accounting-master/jpmorgan-complete-filings-20261011/sources/jpmorgan-2025-10k.pdf'
EXPECTED = 'e16cdad03ca84732dbe21b2595c112e975d5a3f27bce9f394828160275bfe79c'
TERMS = {
    'junior_subordinated': r'junior[\s\-]+subordinated',
    'trust_preferred': r'trust[\s\-]+preferred',
    'capital_trust': r'capital[\s\-]+trust',
    'trust_issued': r'trust[\s\-]+issued',
    'parent_only': r'parent[\s\-]+company[\s\-]+only',
    'equity_method': r'equity[\s\-]+method',
}


def main():
    digest = hashlib.sha256(PDF.read_bytes()).hexdigest()
    assert digest == EXPECTED
    hits = []
    with fitz.open(PDF) as doc:
        for number, page in enumerate(doc, 1):
            normalized = ' '.join(page.get_text().split())
            for name, pattern in TERMS.items():
                matches = list(re.finditer(pattern, normalized, re.I))
                for match in matches[:8]:
                    a, b = match.span()
                    hits.append({'pdf_page': number, 'term': name,
                                 'excerpt': normalized[max(0, a - 125):min(len(normalized), b + 160)]})
    output = {'source': str(PDF.relative_to(ROOT)), 'sha256': digest,
              'search_terms': TERMS, 'excerpt_limit_per_term_per_page': 8,
              'hits': hits}
    (OUT / 'hit-index.json').write_text(json.dumps(output, indent=2) + '\n')
    counts = {name: len({h['pdf_page'] for h in hits if h['term'] == name}) for name in TERMS}
    pages = {name: sorted({h['pdf_page'] for h in hits if h['term'] == name}) for name in TERMS}
    print(json.dumps({'page_counts': counts, 'pages': pages}))


if __name__ == '__main__':
    main()
