"""Inspect raw HSBC archive date attributes; file publication is not established."""
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
SOURCE = ROOT / 'data/financial-report-benchmark/landing/hsbc/15b074f6222ba6ff2ec2667e19317f2dd8b3e079497d88552bf8a08f8009a13d.html'
SHA = '15b074f6222ba6ff2ec2667e19317f2dd8b3e079497d88552bf8a08f8009a13d'


class Inputs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = []

    def handle_starttag(self, tag, attrs):
        if tag == 'input':
            item = dict(attrs)
            if 'data-url' in item:
                self.items.append(item)


def main():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SHA
    parser = Inputs()
    parser.feed(SOURCE.read_text(errors='replace'))
    items = [x for x in parser.items if 'annual report and accounts' in x.get('data-title', '').lower()]
    (OUT / 'annual-item-probe.json').write_text(json.dumps({'source': str(SOURCE.relative_to(ROOT)),
                                                             'sha256': SHA, 'items': items}, indent=2) + '\n')
    print(json.dumps({'all_download_inputs': len(parser.items), 'annual_report_items': len(items),
                      'matches': [{'title': x.get('data-title'), 'date': x.get('data-date'),
                                   'url': x.get('data-url')} for x in items[:20]]}))


if __name__ == '__main__':
    main()
