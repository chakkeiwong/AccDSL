"""One-time request/reading record for the UK/EU adoption inquiry."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import fitz

U = Path(__file__).resolve().parent
R = U.parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
bind = lambda p: {'path': str(p.relative_to(R)), 'sha256': sha(p)}

REQUESTS = [
 ('ukeb-project', 'html', 'https://www.endorsement-board.uk/ifrs-18-presentation-and-disclosure-in-financial-statements',
  'https://www.endorsement-board.uk/ifrs-18-presentation-and-disclosure-in-financial-statements/', 404, 74880),
 ('efrag-status', 'html', 'https://www.efrag.org/en/financial-reporting/endorsement-status', None, 200, 236102),
 ('ukeb-status', 'html', 'https://www.endorsement-board.uk/standards/adoption-status-report/', None, 200, 93044),
 ('efrag-report', 'pdf', 'https://www.efrag.org/sites/default/files/media/document/2026-09/EFRAG%20Endorsement%20Status%20Report%2024%20September%202026.pdf', None, 200, 347671),
 ('ukeb-report', 'pdf', 'https://www.endorsement-board.uk/documents/2454/Adoption_Status_Report_30th_September_2026.pdf',
  'https://media.endorsement-board.uk/documents/Adoption_Status_Report_30th_September_2026.pdf', 200, 281959),
 ('ukeb-by-standard', 'html', 'https://www.endorsement-board.uk/standards/text-by-standard/', None, 200, 83149),
 ('eurlex-search', 'html', 'https://eur-lex.europa.eu/search.html?scope=EURLEX&text=%22IFRS%2018%22&lang=en&type=quick', None, 202, 0),
 ('ukeb-2026', 'html', 'https://www.endorsement-board.uk/standards/text-by-standard/text-by-standard-2026/', None, 200, 149254),
 ('ukeb-adoptions', 'html', 'https://www.endorsement-board.uk/standards/list-of-uk-adoptions/', None, 200, 82262),
 ('ukeb-2025-adoptions', 'html', 'https://www.endorsement-board.uk/standards/list-of-uk-adoptions/2025-list-of-uk-adoptions/', None, 200, 96464),
 ('ukeb-decision', 'pdf', 'https://www.endorsement-board.uk/documents/2032/4.1_Adoption_Statement_-_IFRS_18_Presentation_and_Disclosure_in_Financial_Statements.pdf',
  'https://media.endorsement-board.uk/documents/4.1_Adoption_Statement_-_IFRS_18_Presentation_and_Disclosure_in_Financial_Statements.pdf', 200, 168302),
 ('ukeb-annex', 'pdf', 'https://www.endorsement-board.uk/documents/2026/4._Annex_-_IFRS_18_Presentation_and_Disclosure_in_Financial_Statements.pdf',
  'https://media.endorsement-board.uk/documents/4._Annex_-_IFRS_18_Presentation_and_Disclosure_in_Financial_Statements.pdf', 200, 1275304)]

SPANS = {
 'efrag-status': [(85, 89, 'dated status report'), (163, 177, 'EU endorsement status and dates')],
 'ukeb-report': [(62, 76, 'UK adoption/publication/application date roles')],
 'ukeb-2025-adoptions': [(80, 95, 'decision and annex links with publication date')],
 'ukeb-decision': [(10, 26, 'authority and adoption of IFRS18'), (74, 82, 'IAS7 included'),
                   (199, 208, 'application and annex'), (211, 250, 'approval and date')],
 'ukeb-annex': [(2535, 2614, 'B30-B36 main-business evidence, first span'),
                (2615, 2688, 'B36 continuation through B41 group/dated assessments'),
                (4543, 4564, 'C1-C3 date and retrospective transition'),
                (6719, 6723, 'IAS7 amendment scope'), (6896, 6957, 'IAS7.18/20 indirect reconciliation'),
                (6961, 6991, 'IAS7.31-34A first span'), (7001, 7039, 'IAS7.34A-D continuation'),
                (7072, 7078, 'IAS7.64 linked application')]
}


def anchors(path, ranges):
    lines = path.read_text().split('\n')
    return [{'start_line': a, 'end_line': b, 'purpose': purpose,
             'quote': '\n'.join(lines[a-1:b])} for a, b, purpose in ranges]


def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    assert not (U / 'source-record.json').exists()
    requests = []
    for stem, ext, url, effective, status, size in REQUESTS:
        original, text = U / 'sources' / f'{stem}.{ext}', U / 'sources' / f'{stem}.txt'
        assert original.stat().st_size == size
        requests.append({'id': stem, 'requested_url': url, 'effective_url': effective or url,
            'http_status': status, 'bytes': size, 'original': bind(original),
            'headers': bind(U / 'sources' / f'{stem}.headers'),
            'text': bind(text) if text.exists() else None,
            'anchors': anchors(text, SPANS.get(stem, [])) if text.exists() else [],
            'source_role': 'no substantive source' if status != 200 else
                'adoption decision' if stem == 'ukeb-decision' else
                'adopted technical text' if stem == 'ukeb-annex' else 'status or discovery'})
    previous = R / 'data/accounting-master/r05-ocf-measurement-20261023/measurement-map.json'
    mapping = json.loads(previous.read_text())
    ranges = {'henkel': [(19907, 19924, 'operating/investing boundary and financing components'),
                          (19953, 19963, 'financing subtotal'), (20836, 20844, 'attributed impact expectation')],
              'hsbc': [(21866, 21897, 'dividend classification across cash-flow categories'),
                        (22248, 22254, 'three reporting bases'), (22297, 22299, 'impact under evaluation')],
              'munich_re': [(14396, 14403, 'financing components'), (15929, 15944, '2027 starting-point disclosure')]}
    issuers = [{'issuer_id': r['issuer_id'], 'original': r['original'], 'text': r['text'],
                'anchors': anchors(R / r['text']['path'], ranges[r['issuer_id']]),
                'first_release_admitted': False, '2027_policy_selected': False}
               for r in mapping['rows'] if r['issuer_id'] in ranges]
    value = {'recorded_utc': datetime.now(timezone.utc).isoformat(),
        'scope': 'UK adoption and selected adopted IAS7 text; EU endorsement-status evidence only',
        'requests': requests, 'issuer_sources': issuers, 'prior_measurement_map': bind(previous),
        'actually_viewed_pages': [dict(bind(U / 'sources' / f'ukeb-redline-{n}.png'),
                                      physical_page=n, printed_page=n) for n in (134, 135)],
        'line_convention': 'one-based LF lines; form feeds retained',
        'pdf_annotation_inspection': {'package': 'PyMuPDF', 'version': fitz.VersionBind,
                                     'files': [bind(U / 'sources' / (stem + '.annotations.json')) for stem in ('efrag-report', 'ukeb-report')]},
        'jurisdiction_status': {'uk': 'official adoption statement and linked selected technical paragraphs inspected',
                                'eu': 'EFRAG endorsement status inspected; actual EU regulation not recovered'},
        'issuer_2027_policy_admissions': 0, 'historical_vintage_admissions': 0, 'empirical_execution': False}
    with (U / 'source-record.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(json.dumps({'requests': len(requests), 'http_200': sum(r['http_status'] == 200 for r in requests),
                      'official_anchors': sum(len(r['anchors']) for r in requests),
                      'issuer_anchors': sum(len(r['anchors']) for r in issuers), 'viewed_pages': 2}))


if __name__ == '__main__':
    main()
