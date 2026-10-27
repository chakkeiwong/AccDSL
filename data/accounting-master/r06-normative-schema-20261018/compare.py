"""Restricted extraction for this retained RTF slice, not a general RTF parser."""
from collections import Counter
import difflib
import hashlib
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
RETAINED = ROOT / 'data/accounting-master/taxonomy-reuse-20261007/sources/import-03-trusted.body'
FORMATTING = set('hich af dbch loch f pard ltrpar ql li ri widctlpar wrapdefault pn pnlvlcont ilvl ls pnrnot pndec aspalpha aspnum faauto adjustright rin lin itap pararsid rtlch fcs ltrch cs expnd expndtw insrsid charrsid fi'.split())


def digest(b):
    return hashlib.sha256(b).hexdigest()


def rtf_decode(raw):
    # This slice is ASCII, with only inspected formatting words and paragraph
    # breaks. Fail closed on revision/deletion, Unicode, escapes or destinations
    # not explicitly covered. The pn destinations have formatting controls only.
    assert raw.isascii(), 'non-ASCII RTF slice'
    out, controls = [], Counter()
    i = 0
    while i < len(raw):
        c = raw[i]
        if c in '\r\n{}':
            i += 1
        elif c == '\\':
            if raw[i:i+2] == '\\*':
                assert raw[i:].startswith(chr(92) + "*" + chr(92) + "pn "), "unknown starred destination"
                i += 2
                continue
            m = re.match(r'\\([A-Za-z]+)(-?\d+)? ?', raw[i:])
            assert m, ('unhandled RTF escape', raw[i:i+30])
            word = m.group(1)
            assert word == 'par' or word in FORMATTING, ('unknown RTF control', word)
            controls[word] += 1
            if word == 'par':
                out.append('\n')
            i += len(m.group(0))
        else:
            out.append(c)
            i += 1
    return ''.join(out), dict(sorted(controls.items()))


class Paragraphs(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.paragraphs, self.parts = [], None
    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            assert self.parts is None, 'nested paragraphs'
            self.parts = []
        elif tag == 'br' and self.parts is not None:
            self.parts.append('\n')
        elif tag in ('del', 's', 'strike'):
            raise AssertionError('HTML deleted text needs explicit treatment')
    def handle_data(self, data):
        if self.parts is not None:
            self.parts.append(data)
    def handle_endtag(self, tag):
        if tag == 'p' and self.parts is not None:
            # Word HTML wraps source lines; HTML collapses these to spaces.
            self.paragraphs.append(re.sub(r'[ \t\r\n]+', ' ', ''.join(self.parts)).replace('\xa0', ' '))
            self.parts = None


def extraction():
    rtf = (UNIT / 'sources/05-normative.body').read_bytes()
    assert rtf.startswith(b'{\\rtf1') and b'\\ansicpg1252' in rtf[:100]
    mark = b'\\bkmkstart instance_schema_filename'
    assert rtf.count(mark) == 1
    start = rtf.index(b'<?xml', rtf.index(mark))
    end = rtf.index(b'</schema>', start) + len(b'</schema>')
    raw = rtf[start:end].decode('ascii')
    normative, controls = rtf_decode(raw)
    html_bytes = (UNIT / 'sources/04-specification.body').read_bytes()
    # The Word file declares windows-1252 in its meta tag despite the HTTP
    # UTF-8 label. Decode bytes without replacement; record that discrepancy.
    assert b'charset=windows-1252' in html_bytes[:2000].lower()
    html = html_bytes.decode('cp1252')
    a = html.index('<h2><a name="_xbrl-instance-2003-12-31.xsd"')
    z = html.index('<h2><a name="_xbrl-linkbase-2003-12-31.xsd"', a)
    parser = Paragraphs(); parser.feed(html[a:z]); parser.close()
    visible = '\n'.join(parser.paragraphs)
    first, last = visible.index('<?xml'), visible.index('</schema>') + len('</schema>')
    html_schema = visible[first:last]
    retained = RETAINED.read_bytes().decode('utf-8').replace('\r\n', '\n')
    return normative, html_schema, retained, {
        'rtf_slice_start_byte': start, 'rtf_slice_end_exclusive_byte': end,
        'rtf_slice_sha256': digest(rtf[start:end]), 'rtf_controls': controls,
        'rtf_non_ascii_bytes': 0, 'html_slice_start_byte': a, 'html_slice_end_exclusive_byte': z,
        'html_slice_sha256': digest(html_bytes[a:z]), 'html_paragraphs': len(parser.paragraphs),
        'html_encoding': 'file meta windows-1252; HTTP UTF-8 disagrees; decoded cp1252 without replacement',
    }


def remove_header_comment(s):
    m = re.match(r'(<\?xml[^>]*>\s*)<!--.*?-->', s, re.S)
    assert m, 'expected exactly one leading prolog comment'
    return s[:m.start()] + m.group(1) + s[m.end():]


def structure(s):
    assert '<!DOCTYPE' not in s and '<!ENTITY' not in s, 'external/entity declaration forbidden'
    pending, stack, nodes = [], [], []
    for event, value in ET.iterparse(io.StringIO(s), events=('start', 'end', 'start-ns')):
        if event == 'start-ns':
            pending.append(value)
        elif event == 'start':
            scope = dict(stack[-1]) if stack else {}
            scope.update(pending); pending.clear(); stack.append(scope)
            nodes.append((value, tuple(sorted(scope.items()))))
        else:
            stack.pop()
    # Preserve element order, all attribute values and effective namespace
    # bindings. Whitespace normalization is only the stated presentation
    # comparison; do not call this validation or semantic equivalence.
    return [(e.tag, tuple(sorted(e.attrib.items())), ns,
             ' '.join((e.text or '').split()), ' '.join((e.tail or '').split())) for e, ns in nodes]


def comparison():
    normative, html_schema, retained, meta = extraction()
    ns, hs, rs = structure(normative), structure(html_schema), structure(retained)
    n = remove_header_comment(normative)
    r = remove_header_comment(retained)
    delta = list(difflib.unified_diff(r.splitlines(), n.splitlines(), fromfile='retained', tofile='normative-RTF', lineterm=''))
    report = {
        'extraction': meta, 'normative_text_sha256': digest(normative.encode()),
        'html_text_sha256': digest(html_schema.encode()), 'retained_normalized_sha256': digest(retained.encode()),
        'raw_bytes_equal': RETAINED.read_bytes() == normative.encode(),
        'after_crlf_and_leading_comment_only_equal': r == n,
        'all_xml_whitespace_removed_equal': re.sub(r'\s+', '', r) == re.sub(r'\s+', '', n),
        'namespace_sensitive_structure_equal': rs == ns,
        'html_and_rtf_structure_equal': hs == ns,
        'retained_nodes': len(rs), 'normative_nodes': len(ns), 'html_nodes': len(hs),
        'delta_lines': len(delta),
        'structure_differences': [{'position': i, 'retained': list(x), 'normative': list(y)}
                                  for i,(x,y) in enumerate(zip(rs,ns)) if x != y],
    }
    return report, normative, html_schema, '\n'.join(delta) + '\n'


def check():
    report, normative, html_schema, delta = comparison()
    exact = json.loads((UNIT / 'exact-correspondence.json').read_text())
    retained = RETAINED.read_bytes().decode().replace(chr(13)+chr(10), chr(10))
    assert remove_header_comment(normative)+chr(10) == remove_header_comment(retained)
    assert exact['exact_equal_after_these_only'] is True
    assert exact['normalised_sha256'] == digest(remove_header_comment(retained).encode())
    assert json.loads((UNIT / 'comparison.json').read_text()) == report
    for name, text in [('normative-instance.xsd', normative), ('html-instance.xsd', html_schema), ('text-differences.diff', delta)]:
        assert (UNIT / name).read_bytes() == text.encode(), name
    baseline = structure(normative)
    cases = {
        'namespace_binding': normative.replace('xmlns:xbrli="http://www.xbrl.org/2003/instance"', 'xmlns:xbrli="urn:wrong"', 1),
        'target_namespace': normative.replace('targetNamespace="http://www.xbrl.org/2003/instance"', 'targetNamespace="urn:wrong"', 1),
        'element_form': normative.replace('elementFormDefault="qualified"', 'elementFormDefault="unqualified"', 1),
        'import_location': normative.replace('schemaLocation="xbrl-linkbase-2003-12-31.xsd"', 'schemaLocation="other.xsd"', 1),
        'declaration_name': normative.replace('name="periodType"', 'name="periodTypeChanged"', 1),
        'enumeration_value': normative.replace('value="instant"', 'value="period"', 1),
        'annotation': normative.replace('Taxonomy schema for XBRL.', 'Changed schema.', 1),
        'qname_value': normative.replace('base="token"', 'base="string"', 1),
        'child_order': normative.replace('<enumeration value="instant" />', '<enumeration value="TEMP" />', 1).replace('<enumeration value="duration" />', '<enumeration value="instant" />', 1).replace('<enumeration value="TEMP" />', '<enumeration value="duration" />', 1),
    }
    rejected = []
    for name, altered in cases.items():
        assert altered != normative, name
        assert structure(altered) != baseline, name
        rejected.append(name)
    for name, bad in [('rtf_deleted', '\\deleted omitted'), ('rtf_unicode', '\\u60?'),
                      ('rtf_unknown_destination', '{\\*\\unknown words}'), ('rtf_hex', "\\'a0")]:
        try: rtf_decode(bad)
        except AssertionError: rejected.append(name)
        else: raise AssertionError(name)
    assert rtf_decode('a\\par b\\f2 c')[0] == 'a\nbc'
    ledger = json.loads((UNIT / 'source-ledger.json').read_text())
    for row in ledger['acquisitions']:
        for key in ('body', 'headers'):
            item = row.get(key)
            if item: assert digest((ROOT / item['path']).read_bytes()) == item['sha256']
    assert len(ledger['acquisitions']) == 6
    assert len({r['url'] for r in ledger['acquisitions']}) == 5
    s = UNIT / 'sources'
    assert 'href="specifications-full-index.html"' in (s/'01-navigation-trusted.body').read_text()
    assert 'href="release-history-base-spec-xbrl-2.1.html"' in (s/'02-index.body').read_text()
    assert ledger['acquisitions'][4]['url'] in (s/'03-history.body').read_text()
    html = (s/'04-specification.body').read_bytes().decode('cp1252')
    assert 'is a non-normative version of this' in html
    assert 'specification. The NORMATIVE version is in the file' in html
    assert 'XBRL-RECOMMENDATION-2003-12-31+Corrected-Errata-2008-07-02.rtf' in html
    assert 'name="correction_date"' in html and 'as of 2008-07-02' in html
    return {'status': 'finite source comparison checked', 'acquisitions': 6, 'unique_urls': 5,
            'normative_nodes': report['normative_nodes'],
            'namespace_sensitive_structure_equal': report['namespace_sensitive_structure_equal'],
            'html_and_rtf_structure_equal': report['html_and_rtf_structure_equal'],
            'leading_comment_normalized_exact_equal': report['after_crlf_and_leading_comment_only_equal'],
            'exact_equal_after_three_declared_adjustments': True,
            'rejected_fixtures': rejected, 'runtime_admissions': 0, 'whole_rows_closed': 0}


if __name__ == '__main__':
    if sys.argv[1:] == ['--extract']:
        report, normative, html_schema, delta = comparison()
        for name, text in [('comparison.json', json.dumps(report, indent=2) + '\n'),
                           ('normative-instance.xsd', normative), ('html-instance.xsd', html_schema), ('text-differences.diff', delta)]:
            with (UNIT / name).open('x', encoding='utf-8') as handle: handle.write(text)
        print(json.dumps({k:v for k,v in report.items() if k not in ('extraction','structure_differences')}))
        print(json.dumps({'structure_differences': report['structure_differences'][:5]}))
    else:
        print(json.dumps(check()))
