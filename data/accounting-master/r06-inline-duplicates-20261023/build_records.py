"""Author exact source records once; imported source code is never executed."""
import difflib
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
U = Path(__file__).resolve().parent
R = U.parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
bind = lambda p: {'path': str(p.relative_to(R)), 'sha256': sha(p)}
load = lambda p: json.loads(p.read_text())


def write(name, value):
    with (U / name).open('x') as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
        f.write('\n')


IDS = ('01-primer2013', '02-spec2013', '03-primer2026', '04-spec2026',
       '05-spechistory', '06-primerhistory')
sources = {k: bind(U / 'sources' / (k + '.visible.txt')) for k in IDS}
sources['note2018'] = bind(R / 'data/accounting-master/r06-duplicates-guidance-20261023/sources/01-note.visible.txt')
texts = {k: ' '.join((R / v['path']).read_text().split()) for k, v in sources.items()}
anchors = []


def a(ident, source, section, quote, status='PRIMARY_TECHNICAL_SUPPORT'):
    q = ' '.join(quote.split())
    start = texts[source].index(q)
    anchors.append({'id': ident, 'source': source, 'section': section,
                    'quote': q, 'normalized_character_span': [start, start + len(q)],
                    'support_class': status})


for key in ('01-primer2013', '03-primer2026'):
    suffix = key[-4:]
    a('P' + suffix + '-status', key, 'Abstract',
      'Inline XBRL Part 0: Primer is a non-normative document intended to provide an easily readable description of Inline XBRL.')
    a('P' + suffix + '-option', key, '5.2',
      'therefore allows de-duplication to be carried out at the discretion of the Processor.')
    a('P' + suffix + '-custom', key, '5.2',
      'In addition, because it is possible to add user-defined (non-Inline XBRL) attributes to Inline XBRL Elements, output elements which are XBRL-s-equal may actually contain different attribute-level information.')
    a('P' + suffix + '-different', key, '5.2',
      'In some cases, either because of different rounding conventions or by mistake, a pair of facts may match as to element name, context and {target} property, but may have different values.')
    a('P' + suffix + '-tuple', key, '5.2',
      'For this reason, duplicate tuple children are removed prior to mapping. To keep the Processor as light-weight as possible, duplicates for these purposes are defined as those with the same tuple order value.')
    a('P' + suffix + '-ancestor', key, '5.12',
      'elements (or their ancestor elements ) can be assigned a language which will be carried through to the XBRL facts in the Target Document.')
a('P2013-discourage', '01-primer2013', '5.2', 'Avoid including matching facts with different values in the IXDS.')
a('P2026-guidance', '03-primer2026', '5.2',
  'can create problems for consuming applications. The Handling Duplicate Facts in XBRL and Inline XBRL Working Group Note [DUPLICATES-WGN] contains specific recommendations for the handling of duplicates in an Inline XBRL filing environment.')
a('P2026-revision', '03-primer2026', 'Appendix D',
  '17 November 2015 Removed recommendation relating to duplicate facts, and include reference to new XBRL Duplicates WGN')
a('P2026-ixds', '03-primer2026', '2.2.1',
  'Where Report Packages are not used, the identification of files that should be treated as an IXDS is application dependent.')
a('H-primer-date', '06-primerhistory', 'release table', 'Part 0: Primer 2015-12-09 Supports Recommendation')
a('H-spec-current', '05-spechistory', 'release table', 'Part 1: Specification 2026-07-14 Recommendation')
for key in ('02-spec2013', '04-spec2026'):
    suffix = key[-4:]
    a('S' + suffix + '-norm', key, 'Status',
      'Circulation of this Recommendation is unrestricted. This document is normative.')
    a('S' + suffix + '-target', key, '3.2',
      'For each unique value of the {target} property on such Inline XBRL Elements there MUST exist a Target Document containing all the XBRL facts and [XLINK] -specified relationships which are required by the mapping rules prescribed in this Specification for the Inline XBRL Elements with that value of the {target} property .')
    a('S' + suffix + '-dts', key, '3.3.2',
      'This Specification does not require a Conformant Processor or a Validating Conformant Processor to access the DTS of the Target Document whilst processing.')
a('S2026-exist', '04-spec2026', '10.2',
  'For each ix:nonFraction element , there MUST exist in the Target Document identified by the {target} property an element which has the following XML properties :')
a('S2026-accuracy', '04-spec2026', '10.2.2',
  'The value of the decimals attribute MUST be equal to the value of the {decimals} property , unless that value is absent , when the attribute MUST NOT be present.')
a('S2026-precision', '04-spec2026', '10.2.2',
  'The value of the precision attribute MUST be equal to the value of the {precision} property , unless that value is absent , when the attribute MUST NOT be present.')
a('S2026-id', '04-spec2026', '10.2.2; repeated in11.2.2/15.2.2',
  'The value of the id attribute MUST be equal to the value of the {id} property , unless that value is absent .')
a('S2026-other', '04-spec2026', '10.2.2; repeated in11.2.2/15.2.2',
  'For each of the attributes in the {other attributes} property , the value is equal to the {other attribute value} property .')
a('S2026-value', '04-spec2026', '10.2.3',
  'The text content is equal to the result of applying the {format transformation} property (if present) to the {value} property , multiplying by the {scale} property , if present, and changing the sign of the result if the {sign} property is true.')
a('S2026-lang', '04-spec2026', '11.2.2 nonNormativeNote',
  'It should be noted that unlike <ix:footnote> elements, there is no special handling for in scope @xml:lang declarations on <ix:nonNumeric> elements.', 'SOURCE_CLARIFICATION_NON_NORMATIVE')
a('S2026-lang-root', '04-spec2026', '11.2.2 nonNormativeNote',
  'Reports that need to apply an @xml:lang declaration to the target of an <ix:nonNumeric> element must either declare it explicitly on the element, or declare an @xml:lang attribute on the <ix:references> element, which will be mapped to a corresponding attribute on the root element of the target document, and thus be in scope for the target element.', 'SOURCE_CLARIFICATION_NON_NORMATIVE')
a('S2026-tuple-unique', '04-spec2026', '15.1',
  'The set of Inline XBRL Elements in the {apparent content} property , such that each element has a unique {tuple order} property .')
a('S2026-tuple-equality', '04-spec2026', '15.1.2',
  'Each element in the {tuple content} property with the same {tuple order} property MUST have the same Whitespace Normalized Value .')
a('S2026-tuple-literal', '04-spec2026', '15.1 explanation',
  'The Whitespace Normalized Value of an element is the normalized value as defined in [XML Schema Structures] of that element and its attributes and determined as though the value of the whiteSpace facet were collapse .')
a('S2026-tuple-map', '04-spec2026', '15.2.3',
  'The child elements are the {tuple content} property , ordered in accordance with the {tuple order} property .')
a('S2026-relation', '04-spec2026', '13.2',
  'where both facts satisfy the applicable mapping rules prescribed in this Specification for F and N respectively,')
a('S2013-relation', '02-spec2013', '13.2',
  'where both facts satisfy the applicable mapping rules prescribed in this Specification for f and F respectively,')
a('S2026-validation', '04-spec2026', '3.3.1',
  'in conformance with the rules described herein except those documented as being non-validatable ; and')
a('S2026-registry', '04-spec2026', '16.2.1',
  'have the same functionality for any input that is valid for the earlier version.')
a('N2018-complete', 'note2018', '2.1',
  'Despite the name, the definition above ignores custom attributes (i.e. those not defined by the XBRL specification) and also any footnotes attached to the facts.')
a('N2018-processing', 'note2018', '4',
  'allows, but does not require, processors to de-duplicate facts that are complete duplicates when transforming from Inline XBRL to XBRL.')

sections = [('3 Structure', '3.1.1 Constraints on the Inline XBRL Document Set'),
            ('3.2 The Target Document', '3.3 Processors'),
            ('3.3 Processors', '3.4 The schema'),
            ('10 The nonFraction element', '10.3 Example'),
            ('11 The nonNumeric element', '11.3 Example'),
            ('12 The references element', '13 The relationship element'),
            ('13 The relationship element', '14 The resources element'),
            ('15 The tuple element', '16 Transformations'),
            ('16.2 The Transformation Rules Registry', 'Appendix A References')]
diffs = []
for first, last in sections:
    blocks = []
    for ident in ('02-spec2013', '04-spec2026'):
        lines = (U / 'sources' / (ident + '.visible.txt')).read_text().splitlines()
        start = lines.index(first)
        end = lines.index(last, start + 1)
        blocks.append(lines[start:end])
    diff = list(difflib.unified_diff(*blocks, fromfile='2013', tofile='2026', n=2, lineterm=''))
    diffs.append({'section': first, 'until_exclusive': last,
                  'equal_visible_text': blocks[0] == blocks[1], 'diff': diff})
assert len(anchors) == 42
assert len({x['id'] for x in anchors}) == len(anchors)
assert sum(x['equal_visible_text'] for x in diffs) == 4
body = (U / 'sources/04-spec2026.body').read_text()
start = body.index('It should be noted that unlike')
assert body.rfind('<div class="nonNormativeNote">', 0, start) > body.rfind('</div>', 0, start)
write('source-ledger.json', {'sources': sources, 'anchors': anchors,
                            'new_documents': {k: bind(U / 'sources' / (k + '.body')) for k in IDS},
                            'clarification_html_class': 'nonNormativeNote'})
write('version-comparison.json', {'scope': 'Selected retained visible-text blocks; not a global specification equivalence proof', 'rows': diffs})
print(json.dumps({'anchors': len(anchors), 'version_blocks': len(diffs), 'equal_selected_blocks': 4}))
