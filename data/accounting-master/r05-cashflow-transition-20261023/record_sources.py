"""Record inspected new official sources and LF anchors once."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

U = Path(__file__).resolve().parent
R = U.parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
bind = lambda p: {'path': str(p.relative_to(R)), 'sha256': sha(p)}


def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    assert not (U / 'source-record.json').exists()
    definitions = [
        ('aasb18-page', 'html', 'https://standards.aasb.gov.au/aasb-18-jun-2024', 587827,
         [(392, 397, 'official origin and equivalence statement'),
          (413, 428, 'amendments, application and comparison with IFRS'),
          (1184, 1207, 'B30-B36 specified main business activities'),
          (1208, 1217, 'B37-B41 group assessment and prospective changes'),
          (1663, 1685, 'C1-C6 application and transition')]),
        ('aasb18-appendix-d', 'pdf', 'https://standards.aasb.gov.au/sites/default/files/2024-06/AASB18_06-24_AppendixD_0.pdf', 1467786,
         [(1385, 1388, 'AASB107 edition and redline convention'),
          (1402, 1428, 'cash-flow categories and operating examples'),
          (1484, 1514, 'paragraphs18/20 indirect-method amendment'),
          (1518, 1538, 'paragraphs31/32 and deleted33/34; new33A'),
          (1539, 1566, 'new34A-34D classifications'),
          (1563, 1566, 'paragraph35 income tax'),
          (1588, 1590, 'paragraph64 linked application')])]
    sources = []
    for stem, ext, url, size, spans in definitions:
        original = U / 'sources' / f'{stem}.{ext}'
        text = U / 'sources' / f'{stem}.txt'
        headers = U / 'sources' / f'{stem}.headers'
        assert original.stat().st_size == size
        lines = text.read_text().split('\n')
        sources.append({'id': stem, 'requested_url': url, 'effective_url': url,
            'http_status': 200, 'download_bytes': size, 'original': bind(original),
            'text': bind(text), 'response_headers': bind(headers),
            'anchors': [{'start_line': a, 'end_line': b, 'purpose': purpose,
                         'quote': '\n'.join(lines[a-1:b])} for a, b, purpose in spans]})
    value = {'scope': 'June2024 AASB18 and AppendixD technical cash-flow amendment inquiry',
        'recorded_utc': datetime.now(timezone.utc).isoformat(), 'requests': sources,
        'line_convention': 'one-based LF lines; PDF form feeds retained',
        'actually_viewed_pages': [dict(bind(U / 'sources' / f'amendments-page-{n:03}.png'),
                                      physical_page=n, printed_page=n+52,
                                      purpose='verify deleted and underlined text in cash-flow amendments') for n in (27, 28)],
        'existing_ifrs_background_only': bind(R / 'docs/design/research/standards/ifrs18.txt'),
        'jurisdiction_limit': 'AASB technical requirements and attributed IFRS correspondence; EU/UK endorsement and issuer policies not established',
        'new_requests': 2, 'source_claims_qualified': True, 'empirical_execution': False}
    with (U / 'source-record.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(json.dumps({'official_sources': len(sources), 'anchors': sum(len(x['anchors']) for x in sources),
                      'actually_viewed_pages': 2, 'issuer_applicability_admissions': 0}))


if __name__ == '__main__':
    main()
