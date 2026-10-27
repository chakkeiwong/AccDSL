"""One-time extraction of newly retained official HTML; no network."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys


class Readable(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts, self.links, self.skip = [], [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip += 1
        if tag in ('p', 'div', 'li', 'tr', 'h1', 'h2', 'h3', 'h4', 'br'):
            self.parts.append('\n')
        if tag == 'a':
            attr = dict(attrs)
            if attr.get('href'):
                self.links.append(attr['href'])

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip -= 1
        if tag in ('p', 'div', 'li', 'tr', 'h1', 'h2', 'h3', 'h4', 'td'):
            self.parts.append('\n' if tag != 'td' else ' | ')

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def main():
    source = Path(sys.argv[1])
    target, links = source.with_suffix('.txt'), source.with_suffix('.links.json')
    assert not target.exists() and not links.exists()
    parser = Readable()
    parser.feed(source.read_text())
    rows = [re.sub(r'\s+', ' ', line).strip() for line in ''.join(parser.parts).split('\n')]
    with target.open('x') as f:
        f.write('\n'.join(line for line in rows if line) + '\n')
    with links.open('x') as f:
        json.dump(sorted(set(parser.links)), f, indent=2)
        f.write('\n')
    print(json.dumps({'source': str(source), 'lines': sum(bool(x) for x in rows),
                      'links': len(set(parser.links))}))


if __name__ == '__main__':
    main()
