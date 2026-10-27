"""Extract retained HTML; no network access or accounting inference."""
from html.parser import HTMLParser
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent / 'sources'

class Reader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.parts = []
        self.links = []
        self.anchor = None
        self.meta = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ('script', 'style', 'noscript', 'svg'):
            self.skip += 1
        if not self.skip:
            if tag in ('p', 'div', 'li', 'h1', 'h2', 'h3', 'h4', 'tr', 'br'):
                self.parts.append('\n')
            if tag == 'a':
                self.anchor = {'href': a.get('href', ''), 'text': ''}
            if tag == 'meta':
                self.meta.append(a)

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'noscript', 'svg') and self.skip:
            self.skip -= 1
        if not self.skip:
            if tag == 'a' and self.anchor is not None:
                self.links.append(self.anchor)
                self.anchor = None
            if tag in ('p', 'div', 'li', 'h1', 'h2', 'h3', 'h4', 'tr'):
                self.parts.append('\n')

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)
            if self.anchor is not None:
                self.anchor['text'] += data

for stem in ('gt-reversal', 'gt-ias36-series'):
    reader = Reader()
    reader.feed((ROOT / (stem + '.html')).read_text())
    lines = [re.sub(r'\s+', ' ', line).strip() for line in ''.join(reader.parts).splitlines()]
    text = '\n'.join(line for line in lines if line) + '\n'
    (ROOT / (stem + '.txt')).write_text(text)
    (ROOT / (stem + '-links.json')).write_text(json.dumps(reader.links, indent=2) + '\n')
    (ROOT / (stem + '-meta.json')).write_text(json.dumps(reader.meta, indent=2) + '\n')
    print(stem, len(text), 'characters;', len(reader.links), 'links')
