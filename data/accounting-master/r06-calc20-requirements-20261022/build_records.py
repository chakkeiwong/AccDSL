"""Bind inspected source text, illustrations and authored dispositions once."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
import hashlib
import json

U = Path(__file__).resolve().parent
R = U.parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: str(p.relative_to(R))
load = lambda p: json.loads(p.read_text())
bind = lambda p: {'path': rel(p), 'sha256': sha(p)}


def write(name, value):
    with (U / name).open('x') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts, self.links, self.images, self.skip = [], [], [], 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ('script', 'style'):
            self.skip += 1
        if tag == 'a' and a.get('href'):
            self.links.append(a['href'])
        if tag == 'img':
            self.images.append(a)

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip -= 1

    def handle_data(self, text):
        if not self.skip and text.strip():
            self.parts.append(' '.join(text.split()))


def main():
    assert not (U / 'source-ledger.json').exists(), 'One-time stage already ran'
    sources, normalized, parsers = [], {}, {}
    for ident, scope in [
        ('01-product', 'Complete visible product index and its actual links'),
        ('02-requirements', 'Complete sections 1–5.6, tables, Figures 1–20 and Appendices A–B'),
        ('03-history', 'Complete visible requirements release history and links')]:
        body = U / 'sources' / (ident + '.body')
        parser = Text()
        parser.feed(body.read_text())
        parsers[ident] = parser
        normalized[ident] = ' '.join(parser.parts)
        visible = U / 'sources' / (ident + '.visible.txt')
        text = '\n'.join(parser.parts) + '\n'
        if visible.exists():
            assert visible.read_text() == text, ident
        else:
            with visible.open('x') as stream:
                stream.write(text)
        receipt = load(U / 'sources' / (ident + '.receipt.json'))
        assert receipt['exit_code'] == 0 and receipt['metrics']['http_code'] == 200
        assert body.stat().st_size == receipt['metrics']['size_download']
        sources.append({'id': ident, 'url': receipt['url'], 'scope_read': scope,
                        'body': bind(body), 'visible': bind(visible),
                        'links': parser.links,
                        'receipt': rel(U / 'sources' / (ident + '.receipt.json'))})
    prior = R / 'data/accounting-master/r06-calc11-conformance-source-20261022/source-ledger.json'
    old = load(prior)
    for source in old['sources']:
        if source['id'] == '02-requirements':
            p = R / source['visible']['path']
            assert sha(p) == source['visible']['sha256']
            normalized['prior-11-requirements'] = ' '.join(p.read_text().split())
            prior_req = bind(p)
    p = R / old['prior_recommendation']['path']
    assert sha(p) == old['prior_recommendation']['sha256']
    normalized['prior-recommendation'] = ' '.join(p.read_text().split())
    anchors = []
    for a in load(U / 'anchor-spec.json'):
        text = normalized[a['source']]
        assert a['quote'] in text, (a['id'], a['quote'])
        offset = text.index(a['quote'])
        anchors.append({**a, 'normalized_character_span': [offset, offset + len(a['quote'])]})
    index = load(U / 'image-index.json')
    assert len(index) == len(parsers['02-requirements'].images) == 20
    figures = []
    for image, actual in zip(index, parsers['02-requirements'].images):
        assert image['src'] == actual['src']
        assert image['url'] == urljoin(sources[1]['url'], actual['src'])
        assert not actual.get('alt', '').strip()
        n = image['index']
        receipt = U / 'sources' / f'image-{n:02d}.receipt.json'
        rec = load(receipt)
        original = U / image['local']
        assert rec['url'] == image['url'] and rec['exit_code'] == 0
        assert rec['metrics']['http_code'] == 200
        assert original.stat().st_size == rec['metrics']['size_download'] <= 2097152
        row = {**image, 'original': bind(original), 'receipt': rel(receipt)}
        if n >= 3:
            view = U / 'views' / f'image-{n:02d}.json'
            meta = load(view)
            assert sha(original) == meta['original_sha256']
            assert sha(U / meta['view']) == meta['view_sha256']
            row.update({'view': bind(U / meta['view']), 'view_provenance': bind(view)})
        figures.append(row)
    write('source-ledger.json', {'sources': sources, 'anchors': anchors,
          'figures': figures, 'prior_11_requirements': prior_req,
          'prior_recommendation': bind(p),
          'status': '2019 requirements; history labels Supports Public Working Draft; no adopted algorithm inferred'})
    annotations = {key: load(U / ('findings-' + key + '.json'))
                   for key in ('claims', 'relationships', 'image_reading', 'risks')}
    ids = {a['id'] for a in anchors}
    for group in ('claims', 'relationships'):
        for row in annotations[group]:
            assert set(row['support']) <= ids and row['support']
    assert [i['figure'] for i in annotations['image_reading']] == list(range(1, 21))
    write('claim-support-ledger.json', {'claims': annotations['claims'],
          'manuscript_changed': False, 'normative_policy_selected': False})
    write('scope-prerequisites.json', {'relationships': annotations['relationships'],
          'conclusion': 'Reporting relations need verified company-specific premises before history constraints'})
    write('reading-ledger.json', {'text': [
          {'source': s['id'], 'read': s['scope_read'], 'binding': s['visible']} for s in sources],
          'image_reading': annotations['image_reading'],
          'sequence': 'Text 1–285 and figures 1–3 before recovery; text 286–464 and figures 4–20 after recovery; technical text revisited',
          'credit': 'Actual source inspection; preparation, extraction and counts do not confer reading credit',
          'limits': 'Embedded source illustrations only; original issuer filings and workbooks not revalidated'})
    write_ledgers(sources, parsers, annotations)
    print(json.dumps({'documents': 3, 'figures_read': 20, 'anchors': len(anchors),
                      'claims': len(annotations['claims']), 'relationships': len(annotations['relationships'])}))


def write_ledgers(sources, parsers, annotations):
    write('source-support-ledger.json', {'sources': [
          {'id': s['id'], 'local': s['body'], 'classification': 'PRIMARY_STANDARDS_REQUIREMENTS' if s['id'] == '02-requirements' else 'OFFICIAL_DISCOVERY_METADATA',
           'full_text': s['scope_read'], 'status': 'Requirements 6 February 2019' if s['id'] == '02-requirements' else 'Official index',
           'correction_check': 'Official product and release history inspected; no exhaustive absence-of-correction claim'} for s in sources],
          'figures': 'All 20 actually inspected; originals hashed separately from display derivatives',
          'allowed': 'Documentary scope and prerequisite mapping',
          'forbidden': 'Normative algorithm, adoption, installed support, issuer error or history identification'})
    write('citation-venue-ledger.json', {'scope': 'Official standards requirements, not an academic-paper survey',
          'editors': ['Herm Fischer', 'Paul Warren'], 'year': 2019,
          'citation_counts': 'not available and not used', 'venue_ranking': 'not applicable',
          'technical_status': 'Requirements Document; history says Supports Public Working Draft'})
    links = sorted({x for x in parsers['02-requirements'].links if urlparse(x).scheme in ('http', 'https')})
    refs = []
    for link in links:
        if 'calculation-requirements-2.0' in link:
            disposition = 'This retained edition; completely read'
        elif 'XBRL-2.1' in link:
            disposition = 'Normative baseline retained and read in predecessor; not reacquired'
        elif 'open-information-model' in link and 'filing-indicators' not in link:
            disposition = 'Existing dependency; no new OIM semantics promoted here'
        elif 'duplicates' in link.lower():
            disposition = 'Linked rounding dependency; exact note edition not acquired in this unit; no tie policy adopted'
        elif 'formula' in link.lower():
            disposition = 'Source comparison lead; Formula itself not inspected here; capability statement attributed to requirements only'
        elif 'xbrl-xml' in link.lower():
            disposition = 'Historical OIM syntax restriction dependency; exact edition not inspected here'
        elif 'filing-indicators' in link:
            disposition = 'Out-of-scope mechanism in section 5.5; no claim about present implementation'
        elif '/legal' in link:
            disposition = 'Legal navigation; Appendix A read, no rights clearance inferred'
        else:
            disposition = 'Illustrated issuer filing or regulatory workbook; not acquired; no independent source validation'
        refs.append({'url': link, 'disposition': disposition})
    write('backward-snowball-ledger.json', {'references': refs,
          'scope': 'Every distinct external technical/example link in the retained requirements considered; email and fragment navigation excluded'})
    write('forward-snowball-ledger.json', {'scope': 'Official product and requirements release history; not a citation search',
          'checked': [sources[0]['url'], sources[2]['url']],
          'result': 'Index lists supporting requirements only; history has the 2019 requirements row; no global nonexistence claim',
          'later_comparator': 'Retained corrected Calculations 1.1 explicitly excludes new cross-context functionality'})
    write('omission-risk-ledger.json', {'risks': annotations['risks'],
          'next_leads': 'Resolve a specific dependency only under a separately bounded audited plan; do not repeat exhausted routes'})


if __name__ == '__main__':
    main()
