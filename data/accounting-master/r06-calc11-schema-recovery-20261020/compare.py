"""Compare a recovered schema with its appendix; never validate a filing."""
import hashlib
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

U = Path(__file__).resolve().parent
R = U.parents[2]
B = R / 'data/accounting-master'
PRIOR = B / 'r06-calculations11-source-20261020'
HTML = PRIOR / 'sources/02-calc11-trusted.body'
VISIBLE = PRIOR / 'sources/02-calc11.visible.txt'
SCHEMA = U / 'sources/schema-sandbox.body'
URL = 'https://www.xbrl.org/2023/calculation-1.1.xsd'
XS = 'http://www.w3.org/2001/XMLSchema'
LINK = 'http://www.xbrl.org/2003/linkbase'

def load(path):
    return json.loads(path.read_text())

def bind(path):
    return {'path':str(path.relative_to(R)), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

class CodeBlocks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.active = False
        self.blocks = []
        self.parts = []
    def handle_starttag(self,tag,attrs):
        if tag == 'code':
            assert not self.active
            self.active = True
            self.parts = []
    def handle_endtag(self,tag):
        if tag == 'code' and self.active:
            self.blocks.append(''.join(self.parts))
            self.active = False
    def handle_data(self,value):
        if self.active:
            self.parts.append(value)

def appendix():
    reader = CodeBlocks()
    reader.feed(HTML.read_text())
    hits = [x for x in reader.blocks if 'targetNamespace="https://xbrl.org/2023/calculation-1.1"' in x]
    assert len(hits) == 1 and '<?xml' in hits[0]
    return hits[0]

def profile(raw):
    text = raw.decode('utf-8') if isinstance(raw,bytes) else raw
    assert '<!DOCTYPE' not in text and '<!ENTITY' not in text
    assert len(text.encode('utf-8')) < 100000
    pending = {}
    stack = []
    scopes = {}
    for event,item in ET.iterparse(io.StringIO(text),events=('start-ns','start','end')):
        if event == 'start-ns':
            prefix,uri = item
            pending[prefix] = uri
        elif event == 'start':
            scope = dict(stack[-1]) if stack else {'xml':'http://www.w3.org/XML/1998/namespace'}
            scope.update(pending)
            pending.clear()
            stack.append(scope)
            scopes[id(item)] = scope
        else:
            root = item
            stack.pop()
    assert root.tag == '{'+XS+'}schema', 'wrong root'
    def node(e):
        text = (e.text or '').strip()
        if e.tag == '{'+LINK+'}usedOn':
            assert re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.-]*:[A-Za-z_][A-Za-z0-9_.-]*',text)
            prefix,local = text.split(':')
            assert prefix in scopes[id(e)], 'unbound usedOn prefix'
            text = '{'+scopes[id(e)][prefix]+'}'+local
        assert not (e.tail or '').strip(), 'unexpected mixed content'
        return {'tag':e.tag, 'attributes':dict(sorted(e.attrib.items())),
                'text':text, 'children':[node(c) for c in e]}
    parsed = node(root)
    return {'tree':parsed, 'elements':sum(1 for _ in root.iter()),
            'imports':[dict(x.attrib) for x in root.iter('{'+XS+'}import')],
            'includes':[dict(x.attrib) for x in root.iter('{'+XS+'}include')],
            'redefines':[dict(x.attrib) for x in root.iter('{'+XS+'}redefine')]}

def fixtures(raw):
    baseline = profile(raw)
    alias = raw.replace('xmlns:link=', 'xmlns:lb=').replace('<link:', '<lb:').replace('</link:', '</lb:').replace('>link:calculationArc<','>lb:calculationArc<')
    assert profile(alias) == baseline
    whitespace = raw.replace('<xsd:annotation>', '<xsd:annotation>\n    ')
    assert profile(whitespace) == baseline
    changes = [
        raw.replace('https://xbrl.org/2023/calculation-1.1','https://www.xbrl.org/2023/calculation-1.1'),
        raw.replace('https://xbrl.org/2023/arcrole/summation-item','https://www.xbrl.org/2023/arcrole/summation-item'),
        raw.replace('cyclesAllowed="undirected"','cyclesAllowed="any"'),
        raw.replace('id="summation-item"','id="other"'),
        raw.replace('>link:calculationArc<','>link:presentationArc<'),
        raw.replace('xmlns:link="'+LINK+'"','xmlns:link="urn:other"'),
        raw.replace('Calculation v1.1 summation-item arcrole','different definition'),
        raw.replace('<xsd:annotation>','<xsd:import namespace="urn:other" schemaLocation="remote"/><xsd:annotation>'),
    ]
    assert all(profile(x) != baseline for x in changes)
    bad = [raw.replace('>link:calculationArc<','>unbound:calculationArc<'),
           '<!DOCTYPE schema SYSTEM "remote">'+raw,
           '<!ENTITY x "y">'+raw, raw.replace('</xsd:schema>','')]
    for candidate in bad:
        try:
            profile(candidate)
        except (AssertionError,ET.ParseError):
            pass
        else:
            raise AssertionError('unsupported input accepted')
    return {'equivalent_variants':2, 'different_declarations':len(changes), 'rejected_inputs':len(bad)}

def derive():
    raw = SCHEMA.read_text()
    embedded = appendix()
    actual, convenience = profile(raw), profile(embedded)
    assert actual == convenience
    assert actual['elements'] == 6 and not any(actual[k] for k in ('imports','includes','redefines'))
    schema = actual['tree']
    assert schema['attributes'] == {'attributeFormDefault':'unqualified','elementFormDefault':'qualified',
                                    'targetNamespace':'https://xbrl.org/2023/calculation-1.1'}
    arc = schema['children'][0]['children'][0]['children'][0]
    assert arc['tag'] == '{'+LINK+'}arcroleType'
    assert arc['attributes'] == {'arcroleURI':'https://xbrl.org/2023/arcrole/summation-item',
                                'cyclesAllowed':'undirected','id':'summation-item'}
    assert arc['children'][1]['text'] == '{'+LINK+'}calculationArc'
    notice = re.search(r'<!--(.*?)-->',raw,re.S).group(1)
    embedded_notice = re.search(r'<!--(.*?)-->',embedded,re.S).group(1)
    assert ' '.join(notice.split()) == ' '.join(embedded_notice.split())
    text = VISIBLE.read_text()
    assert 'A non-normative copy of each document is included in this appendix' in text
    assert 'alternative hosts and schemes' in text and URL in text
    old = load(PRIOR/'sources/05-schema-trusted.receipt.json')
    assert old['exit_code'] == 28 and old['url'] == URL
    receipt = load(U/'sources/schema-receipt.json')
    meta = json.loads(receipt['result']['output'])
    assert receipt['result']['exit_code'] == 0 and meta['http_code'] == 200
    assert meta['url'] == meta['url_effective'] == URL and meta['num_redirects'] == 0
    assert meta['size_download'] == SCHEMA.stat().st_size
    return {'publication_url':URL,'retrieved_bytes':SCHEMA.stat().st_size,'publication':bind(SCHEMA),
            'appendix_source':bind(HTML),'source_roles_distinct':True,
            'exact_utf8_equal':SCHEMA.read_bytes()==embedded.encode('utf-8'),
            'namespace_aware_profile_equal':True,'copyright_notice_whitespace_normalized_equal':True,
            'profile':actual,'fixtures':fixtures(raw),'prior_failed_receipt':bind(PRIOR/'sources/05-schema-trusted.receipt.json'),
            'publication_copy_duty':'recovered_and_source_compared',
            'schema_validation':'not_run','DTS_discovery':'not_run','report_adoption':False,
            'rounding_policy':'unselected','duplicate_cross_reference':'unresolved_contextual_reading_preserved',
            'whole_rows_closed':0}

def check():
    ledger=load(U/'source-ledger.json');count=0
    for row in ledger['bindings']:
        assert bind(R/row['path'])==row;count+=1
    for row in ledger['anchors']:
        p=R/row['source']['path']; assert bind(p)==row['source'];count+=1
        assert '\n'.join(p.read_text().splitlines()[row['first_line']-1:row['last_line']])==row['excerpt'];count+=1
    actual=derive()
    assert actual==load(U/'comparison.json');count+=1
    assert appendix()==(U/'appendix-schema.xml').read_text();count+=1
    count+=sum(actual['fixtures'].values())
    assert load(U/'acquisitions.json')['new_attempts']==1;count+=1
    return {'checks':count,'source_anchors':len(ledger['anchors']),'input_bindings':len(ledger['bindings']),
            'acquisitions':1,'schema_bytes':actual['retrieved_bytes'],'schema_elements':actual['profile']['elements'],
            'namespace_aware_equal':True,'exact_bytes_equal':actual['exact_utf8_equal'],
            'fixtures':actual['fixtures'],'runtime_admitted':False,'whole_rows_closed':0}
