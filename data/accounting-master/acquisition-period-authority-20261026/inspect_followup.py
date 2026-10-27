"""Extract selected index rows and preserve the additional appendix text."""
from pathlib import Path
from html.parser import HTMLParser
from hashlib import sha256
import json,re,fitz
H=Path(__file__).resolve().parent
class Rows(HTMLParser):
    def __init__(self):super().__init__();self.stack=[];self.rows=[]
    def handle_starttag(self,tag,attrs):
        if tag=='tr':self.stack.append(dict(parts=[],links=[]))
        if tag=='a':
            href=dict(attrs).get('href')
            if href:
                for r in self.stack:r['links'].append(href)
    def handle_data(self,data):
        for r in self.stack:r['parts'].append(data)
    def handle_endtag(self,tag):
        if tag=='tr' and self.stack:
            r=self.stack.pop();r['text']=' '.join(' '.join(r.pop('parts')).split());self.rows.append(r)
out=H/'followup-inspection';out.mkdir(exist_ok=False);rows=[]
for path in [H/'index-attempt-02/accounting-index.html',H/'source-attempt-02/accounting-index-second.html']:
    parser=Rows();parser.feed(path.read_text())
    matches=[r for r in parser.rows if re.match(r'^AASB (3|10|127)\b',r['text'])]
    rows.append(dict(source=str(path.relative_to(H)),sha256=sha256(path.read_bytes()).hexdigest(),rows=matches))
    print(json.dumps(dict(source=path.name,rows=matches),ensure_ascii=False))
(out/'standard-index-rows.json').write_text(json.dumps(rows,indent=2)+'\n')
p=H/'source-attempt-02/aasb1061-appendix-c.pdf';doc=fitz.open(p);summary=[]
for i,page in enumerate(doc):
    t=page.get_text();(out/('aasb1061-appendix-c-page-'+str(i+1)+'.txt')).write_text(t)
    if re.search(r'AASB\s+(3\b|10\b|127\b)|1 January|1 July|annual reporting periods',t):
        summary.append(dict(page=i+1,headings=[line for line in t.splitlines() if re.search(r'AASB\s+(3\b|10\b|127\b)|1 January|1 July|annual reporting periods',line)][:8]))
(out/'appendix-index.json').write_text(json.dumps(dict(pages=len(doc),sha256=sha256(p.read_bytes()).hexdigest(),relevant=summary),indent=2)+'\n')
print(json.dumps(dict(file=p.name,pages=len(doc),relevant=summary)))
