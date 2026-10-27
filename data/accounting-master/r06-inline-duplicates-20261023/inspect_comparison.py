"""Bounded read-only text comparison of selected dated provisions."""
import difflib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
U = Path(__file__).resolve().parent


def block(ident, first, last):
    lines = (U / 'sources' / (ident + '.visible.txt')).read_text().splitlines()
    a = lines.index(first)
    b = lines.index(last, a + 1)
    return lines[a:b]


for first, last in [
    ('3 Structure', '3.1.1 Constraints on the Inline XBRL Document Set'),
    ('3.2 The Target Document', '3.3 Processors'),
    ('3.3 Processors', '3.4 The schema'),
    ('10 The nonFraction element', '10.3 Example'),
    ('11 The nonNumeric element', '11.3 Example'),
    ('12 The references element', '13 The relationship element'),
    ('13 The relationship element', '14 The resources element'),
    ('15 The tuple element', '16 Transformations'),
    ('16.2 The Transformation Rules Registry', 'Appendix A References'),
]:
    a, b = [block(ident, first, last) for ident in ('02-spec2013', '04-spec2026')]
    diff = list(difflib.unified_diff(a, b, fromfile='2013', tofile='2026', n=2, lineterm=''))
    print(json.dumps({'section': first, 'equal_visible_text': a == b,
                      'diff': diff[:140], 'diff_lines': len(diff)}))
for ident in ('05-spechistory', '06-primerhistory'):
    value = json.loads((U / 'sources' / (ident + '.structure.json')).read_text())
    print(json.dumps({'source': ident, 'images': value['images']}))
