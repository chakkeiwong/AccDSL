"""Create distinct readable views, excluding explicit inline-hidden text."""
from html.parser import HTMLParser
from pathlib import Path
import json

U=Path(__file__).resolve().parent
VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
BREAK={'h1','h2','h3','h4','h5','p','div','li','tr','br','pre'}

class Visible(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.stack=[];self.parts=[];self.hidden=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs);style=a.get('style','').replace(' ','').lower()
        hidden=(self.stack and self.stack[-1][1]) or tag in ('script','style') or 'display:none' in style
        if hidden and not (self.stack and self.stack[-1][1]):self.hidden+=1
        if not hidden and tag in BREAK:self.parts.append('\n')
        if tag not in VOID:self.stack.append((tag,bool(hidden)))
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in VOID:self.handle_endtag(tag)
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:
                hidden=self.stack[i][1];del self.stack[i:]
                if not hidden and tag in BREAK:self.parts.append('\n')
                break
    def handle_data(self,data):
        if not self.stack or not self.stack[-1][1]:self.parts.append(data)
    def text(self):
        return '\n'.join(' '.join(s.split()) for s in ''.join(self.parts).splitlines() if s.strip())+'\n'

if __name__=='__main__':
    results=[]
    for name in ('01-enumerations','02-dimensions','03-xbrl21'):
        t=Visible();t.feed((U/'sources'/f'{name}.body').read_text())
        with (U/'sources'/f'{name}.visible.txt').open('x') as f:f.write(t.text())
        results.append({'name':name,'lines':len(t.text().splitlines()),'hidden_subtrees_excluded':t.hidden})
    print(json.dumps(results))
