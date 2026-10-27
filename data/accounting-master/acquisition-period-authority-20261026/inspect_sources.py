"""Retain searchable extraction and compact exact index/source diagnostics."""
from pathlib import Path
from html.parser import HTMLParser
from hashlib import sha256
import json,re,sys
H=Path(__file__).resolve().parent
class Index(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.current=None;self.text=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='a' and 'href' in a:self.current=dict(url=a['href'],text='',title=a.get('title',''))
    def handle_data(self,data):
        self.text.append(data)
        if self.current is not None:self.current['text']+=data
    def handle_endtag(self,tag):
        if tag=='a' and self.current is not None:self.links.append(self.current);self.current=None
if sys.argv[1]=='index':
    p=H/'index-attempt-02/accounting-index.html';a=Index();a.feed(p.read_text())
    selected=[x for x in a.links if any(t in x['url'].lower() for t in ['aasb2026-2','aasb20_','aasb1061','page=','aasb-3-','aasb-10-','aasb-127-'])]
    out=H/'index-inspection';out.mkdir(exist_ok=False)
    (out/'selected-links.json').write_text(json.dumps(selected,indent=2)+'\n')
    (out/'index.txt').write_text('\n'.join(x.strip() for x in a.text if x.strip()))
    (out/'source.json').write_text(json.dumps(dict(path=str(p),sha256=sha256(p.read_bytes()).hexdigest(),scope='Current default index page only; pagination and period filters require separate inspection'),indent=2)+'\n')
    print(json.dumps(selected,indent=2))
elif sys.argv[1]=='pdfs':
    import fitz
    source=H/sys.argv[2];out=H/'technical-inspection';out.mkdir(exist_ok=False);summaries=[]
    for p in source.glob('*.pdf'):
        doc=fitz.open(p);pages=[]
        for i,page in enumerate(doc):
            txt=page.get_text();(out/(p.stem+'-page-'+str(i+1)+'.txt')).write_text(txt)
            if re.search(r'AASB\s+(?:3\b|10\b|127\b)|Application|Compiled|Compilation|2029|2028|2027',txt,re.I):
                lines=txt.splitlines();hits=[]
                for k,line in enumerate(lines):
                    if re.search(r'AASB\s+(?:3\b|10\b|127\b)|Application|Compiled|Compilation|2029|2028|2027',line,re.I):hits.append(' '.join(lines[max(0,k-1):min(len(lines),k+3)]))
                pages.append(dict(page=i+1,hits=hits[:12]))
        summaries.append(dict(file=p.name,sha256=sha256(p.read_bytes()).hexdigest(),pages=len(doc),hits=pages))
    (out/'page-index.json').write_text(json.dumps(summaries,indent=2)+'\n')
    print(json.dumps([dict(file=s['file'],pages=s['pages'],relevant_pages=[p['page'] for p in s['hits']]) for s in summaries]))
