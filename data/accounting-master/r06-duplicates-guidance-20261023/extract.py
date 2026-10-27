"""Retain visible text and structural metadata once; no reading credit."""
from html.parser import HTMLParser
from pathlib import Path
import hashlib
import json
import sys

U = Path(__file__).resolve().parent


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts, self.links, self.images, self.headings = [], [], [], []
        self.skip, self.heading, self.table_count = 0, None, 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ('script', 'style'):
            self.skip += 1
        if tag == 'a' and a.get('href'):
            self.links.append(a['href'])
        if tag == 'img':
            self.images.append(a)
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self.heading = {'tag': tag, 'id': a.get('id'), 'parts': []}
        if tag == 'table':
            self.table_count += 1

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip -= 1
        if self.heading and tag == self.heading['tag']:
            self.headings.append({**self.heading, 'text': ' '.join(self.heading['parts'])})
            self.heading = None

    def handle_data(self, text):
        if not self.skip and text.strip():
            t = ' '.join(text.split())
            self.parts.append(t)
            if self.heading:
                self.heading['parts'].append(t)


def main():
    ident = sys.argv[1]
    assert ident in ('01-note', '02-status', '03-history')
    body = U / 'sources' / (ident + '.body')
    visible = U / 'sources' / (ident + '.visible.txt')
    structure = U / 'sources' / (ident + '.structure.json')
    assert not visible.exists() and not structure.exists()
    parser = Text()
    parser.feed(body.read_text())
    with visible.open('x') as stream:
        stream.write('\n'.join(parser.parts) + '\n')
    value = {'body_sha256': hashlib.sha256(body.read_bytes()).hexdigest(),
             'visible_sha256': hashlib.sha256(visible.read_bytes()).hexdigest(),
             'links': parser.links, 'images': parser.images, 'headings': parser.headings,
             'table_count': parser.table_count, 'reading_credit': 'none from extraction'}
    with structure.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'id': ident, 'visible_lines': len(parser.parts),
                      'images': len(parser.images), 'tables': parser.table_count,
                      'links': len(parser.links)}))


if __name__ == '__main__':
    main()
