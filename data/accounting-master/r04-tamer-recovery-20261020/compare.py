"""Read-only identity/access disposition; no paper content inferred."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path

U=Path(__file__).resolve().parent
R=U.parents[2]
OLD=R/'data/accounting-master/tamer-source-recovery-20261013'
DOI='https://doi.org/10.1146/annurev.economics.050708.143401'
FINAL='https://www.annualreviews.org/doi/10.1146/annurev.economics.050708.143401'


def load(p):return json.loads(p.read_text())


def bind(p):return {'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}


class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.title=[];self.in_title=False;self.links=[];self.feed(text)
    def handle_starttag(self,tag,attrs):
        if tag=='title':self.in_title=True
        if tag=='a' and dict(attrs).get('href'):self.links.append(dict(attrs)['href'])
    def handle_endtag(self,tag):
        if tag=='title':self.in_title=False
    def handle_data(self,data):
        if self.in_title:self.title.append(data)


def derive():
    institutional=Page((R/'docs/design/research/raw/tamer-landing.html').read_text())
    assert DOI in institutional.links
    out=[]
    for label,stem in [('ordinary sandbox','publisher-sandbox'),('trusted elevated','publisher-trusted')]:
        receipt=load(U/'sources'/('publisher-receipt.json' if label=='ordinary sandbox' else 'publisher-trusted-receipt.json'))
        data=json.loads(receipt['result']['output'])
        body=U/'sources'/(stem+'.body');headers=U/'sources'/(stem+'.headers')
        assert receipt['result']['exit_code']==data['exitcode']==0
        assert data['http_code']==403 and data['num_redirects']==1
        assert data['url']==DOI and data['url_effective']==FINAL
        assert body.stat().st_size==data['size_download']==5551
        assert 'cf-mitigated: challenge' in headers.read_text().lower()
        assert not body.read_bytes().startswith(b'%PDF')
        title=''.join(Page(body.read_text()).title)
        assert title=='Just a moment...'
        out.append({'context':label,'request':DOI,'final_url':FINAL,'http':403,'title':title,
                    'body':bind(body),'headers':bind(headers),'receipt':bind(U/'sources'/('publisher-receipt.json' if label=='ordinary sandbox' else 'publisher-trusted-receipt.json'))})
    return {'attempts':out,'distinct_source_route':1,'source_status':'SOURCE_BLOCKED',
            'technical_sections_read':[],'allowed_technical_claims':[],
            'old_harvard_routes':'preserved; not retried or bypassed',
            'restriction':'publisher challenge in both ordinary and trusted contexts',
            'not_concluded':['global source absence','paper invalidity','source identity verified from full text',
                             'current correction/retraction clearance','E3 inferential design']}


def check():
    value=derive();assert value==load(U/'comparison.json')
    ledger=load(U/'source-ledger.json')
    for item in ledger['bindings']:assert bind(R/item['path'])==item,item['path']
    for a in ledger['anchors']:
        text=(R/a['source']['path']).read_text()
        assert bind(R/a['source']['path'])==a['source']
        assert text[a['start']:a['end']]==a['excerpt']
    return {'status':'blocked publisher route and protected sources verified',
            'attempts':2,'distinct_routes':1,'http403':2,'source_bindings':len(ledger['bindings']),
            'anchors':len(ledger['anchors']),'technical_reading':False,'whole_rows_closed':0}
