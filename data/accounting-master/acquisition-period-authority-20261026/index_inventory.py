"""Associate standards with their adjacent amendment rows without index counts."""
from pathlib import Path
from html.parser import HTMLParser
from hashlib import sha256
import json,re
H=Path(__file__).resolve().parent
class Parser(HTMLParser):
    def __init__(self):super().__init__();self.depth=0;self.row=None;self.rows=[]
    def handle_starttag(self,tag,attrs):
        if tag=='tr':
            if not self.depth:self.row={'text':[],'links':[],'class':dict(attrs).get('class','')}
            self.depth+=1
        if tag=='a' and self.row is not None:
            href=dict(attrs).get('href')
            if href:self.row['links'].append(href)
    def handle_data(self,data):
        if self.row is not None:self.row['text'].append(data)
    def handle_endtag(self,tag):
        if tag=='tr' and self.depth:
            self.depth-=1
            if not self.depth:
                self.row['text']=' '.join(' '.join(self.row['text']).split());self.rows.append(self.row);self.row=None
out=H/'index-inventory-01';out.mkdir(exist_ok=False);items=[]
for path in sorted(H.glob('*/accounting-index*.html')):
    parser=Parser();parser.feed(path.read_text());selected=[];labels=[]
    for i,row in enumerate(parser.rows):
        if re.match(r'^AASB \d',row['text']):labels.append(row['text'])
        if re.match(r'^AASB (3|10|127)\b',row['text']):
            amendments=parser.rows[i+1] if i+1<len(parser.rows) and 'amend-box' not in row['class'] and 'amend' in parser.rows[i+1]['class'] else None
            selected.append(dict(standard=row,amendments=amendments))
    items.append(dict(source=str(path.relative_to(H)),sha256=sha256(path.read_bytes()).hexdigest(),selected=selected,standards=labels))
    print(json.dumps(dict(file=path.name,standards=labels,selected=selected),ensure_ascii=False))
(out/'inventory.json').write_text(json.dumps(items,indent=2)+'\n')
