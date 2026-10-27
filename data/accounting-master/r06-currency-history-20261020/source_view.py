"""Produce lossless-source-linked text views; no scripts or network executed."""
from html.parser import HTMLParser
from pathlib import Path
import json

class View(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.parts = []
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip += 1
        for name, value in attrs:
            if name == 'href' and value:
                self.links.append(value)
    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip = max(0, self.skip - 1)
    def handle_data(self, value):
        if not self.skip and value.strip():
            self.parts.append(' '.join(value.split()))

def derive(path):
    view = View()
    view.feed(path.read_text())
    return view

if __name__ == '__main__':
    source = Path(__file__).resolve().parent / 'sources'
    for name in ('SIX-index', 'SIX-currency'):
        value = derive(source / (name + '-sandbox.body'))
        with (source / (name + '.visible.txt')).open('x') as handle:
            handle.write('\n'.join(value.parts) + '\n')
        with (source / (name + '.links.json')).open('x') as handle:
            json.dump(value.links, handle, indent=2)
            handle.write('\n')
        print(json.dumps({'source': name, 'text_lines': len(value.parts), 'links': len(value.links)}))
