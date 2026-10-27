"""Read-only source identity and provenance checks; no accounting selector."""
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

U = Path(__file__).resolve().parent
R = U.parents[2]
P = R / 'data/accounting-master/insurance-termination-source-20261017'
S = U / 'sources'


def load(p):
    return json.loads(p.read_text())


def bind(p):
    return {'path': str(p.relative_to(R)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}


def norm(s):
    return ' '.join(s.split())


class HTML(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.links, self.visible, self.hidden = [], [], 0
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.hidden += 1
        if tag == 'a' and dict(attrs).get('href'):
            self.links.append(dict(attrs)['href'])

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data):
        if not self.hidden:
            self.visible.append(data)


def derive():
    acquisitions = []
    for path in sorted(S.glob('*-receipt.json')):
        receipt = load(path)
        response = json.loads(receipt['result']['output'])
        body = S / (receipt['name'] + '-sandbox.body')
        assert receipt['result']['exit_code'] == response['exitcode'] == 0
        assert response['http_code'] == 200
        assert body.stat().st_size == response['size_download'] <= 2000000
        assert urlparse(response['url_effective']).hostname in (
            'www.ifrs.org', 'www.aasb.gov.au', 'standards.aasb.gov.au')
        acquisitions.append({'name': receipt['name'], 'request': response['url'],
                             'final_url': response['url_effective'],
                             'http_code': response['http_code'], 'bytes': body.stat().st_size,
                             'body': bind(body), 'receipt': bind(path)})
    assert len(acquisitions) == 8
    by_name = {a['name']: a for a in acquisitions}
    edition = HTML((P / 'aasb17-edition.html').read_text())
    edition_links = {urljoin('https://standards.aasb.gov.au/', a) for a in edition.links}
    assert by_name['AASB-BC']['request'] in edition_links
    assert by_name['IASB-support']['request'] in edition_links
    assert by_name['IASB-support']['final_url'] == 'https://www.aasb.gov.au/international-visitor/'
    visitor = norm(' '.join(HTML((S / 'IASB-support-sandbox.body').read_text()).visible))
    assert 'This content is restricted to users in Australia only' in visitor
    support = HTML((P / 'ifrs-supporting.html').read_text())
    assert by_name['IFRS-amendments']['request'] in {urljoin('https://www.ifrs.org/', a) for a in support.links}
    project = (S / 'IFRS-amendments-sandbox.body').read_text()
    script = (S / 'IFRS-site-script-sandbox.body').read_text()
    tabs = re.search(r'IFRS\.tabs\(\s*[\'"]([^\'"]+)', project).group(1)
    assert by_name['IFRS-meetings']['request'] == 'https://www.ifrs.org' + tabs + '/meetings_tab.nocache.html'
    assert 'n.requestURL+"/"+s+".nocache.html"' in script
    fragment = (S / 'IFRS-meetings-sandbox.body').read_text()
    picker = re.search(r'IFRS\.projectMeetingPicker\(\s*[\'"]([^\'"]+)', fragment).group(1)
    assert by_name['IFRS-picker']['request'] == 'https://www.ifrs.org' + picker + '.model.json'
    assert 'this.requestURL=e.concat(".model.json")' in script
    model = load(S / 'IFRS-picker-sandbox.body')
    selected = urlparse(by_name['IASB-feb2019']['request']).path
    assert selected in model['eventDateRangeList']
    meeting = HTML((S / 'IASB-feb2019-sandbox.body').read_text())
    assert by_name['IASB-AP2C']['request'] in {urljoin('https://www.ifrs.org/', a) for a in meeting.links}
    aasb = (S / 'AASB-BC.txt').read_text()
    ap2c = (S / 'IASB-AP2C.txt').read_text()
    assert [int(n) for n in re.findall(r'^AusBC(\d+)\s', aasb, re.M)] == list(range(1, 33))
    assert [int(n) for n in re.findall(r'^\s*(\d+)\.\s', ap2c, re.M)] == list(range(1, 34))
    assert aasb.count('\f') == 4 and ap2c.count('\f') == 12
    assert 'substantive Australian-specific issues' in norm(aasb)
    assert 'does not represent the views of the Board' in norm(ap2c)
    assert 'C18(b)' in ap2c and 'C19(b)(ii)' in ap2c and 'C24(b)' in ap2c
    assert 'BC393' in ap2c
    assert 'B135' not in ap2c and 'B136' not in ap2c
    return {'acquisitions': acquisitions,
            'navigation': {'meeting_date_label': model['eventDateRangeList'][selected],
                           'meeting_pdf_links': [a for a in meeting.links if a.endswith('.pdf')],
                           'static_script_only': True},
            'read_scope': {'aasb': 'all AusBC1–32, four extracted pages',
                           'ap2c': 'all paragraphs1–33 and footnotes1–8, twelve extracted pages',
                           'rendered_pages': ['AASB physical1/printed90', 'AP2C1', 'AP2C12']},
            'disposition': {'aasb': 'Australian-specific adoption reasons, not IASB BC316–322',
                            'iasb_support': 'geographically restricted; no bypass attempted',
                            'ap2c': 'historical staff transition discussion; not final authority or a91/B135 example',
                            'combined_treatment': 'not established; both original readings preserved'}}


def check():
    actual = derive()
    assert actual == load(U / 'comparison.json')
    ledger = load(U / 'source-ledger.json')
    for item in ledger['bindings']:
        assert bind(R / item['path']) == item, item['path']
    for anchor in ledger['anchors']:
        text = (R / anchor['source']['path']).read_text()
        assert bind(R / anchor['source']['path']) == anchor['source']
        assert text[anchor['start']:anchor['end']] == anchor['excerpt'], anchor['id']
    return {'status': 'source identity, navigation and immutable excerpts verified',
            'acquisitions': len(actual['acquisitions']), 'http200': 8,
            'source_bindings': len(ledger['bindings']), 'anchors': len(ledger['anchors']),
            'aasb_paragraphs': 32, 'ap2c_paragraphs': 33,
            'rendered_pages': 3, 'accounting_treatment_admitted': False,
            'whole_rows_closed': 0}
