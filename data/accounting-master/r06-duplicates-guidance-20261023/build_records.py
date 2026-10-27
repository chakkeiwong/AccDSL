"""Record already inspected source passages once; never grant reading by extraction."""
import hashlib
import json
from pathlib import Path

U = Path(__file__).resolve().parent
R = U.parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: str(p.relative_to(R))
bind = lambda p: {'path': rel(p), 'sha256': sha(p)}


def write(name, value):
    with (U / name).open('x') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


def main():
    assert not (U / 'source-ledger.json').exists()
    sources = {
        'note': U / 'sources/01-note.visible.txt',
        'calc11': R / 'data/accounting-master/r06-calculations11-source-20261020/sources/02-calc11.visible.txt',
        'oim': R / 'data/accounting-master/r06-calculations11-source-20261020/sources/03-oim.visible.txt',
        'req11': R / 'data/accounting-master/r06-calc11-conformance-source-20261022/sources/02-requirements.visible.txt',
        'req20': R / 'data/accounting-master/r06-calc20-requirements-20261022/sources/02-requirements.visible.txt',
    }
    texts = {k: ' '.join(p.read_text().split()) for k, p in sources.items()}
    anchors = []

    def anchor(ident, source, section, quote):
        t = texts[source]
        assert quote in t, ('unmatched exact passage', ident, quote)
        start = t.index(quote)
        assert t.count(quote) == 1, ident
        anchors.append({'id': ident, 'source': source, 'section': section,
                        'quote': quote, 'normalized_character_span': [start, start + len(quote)]})

    rows = [
        ('N01', 'Header', 'Document 19 April 2018'),
        ('N02', 'Status', 'Circulation of this Document is unrestricted. Other documents may supersede this document.'),
        ('N03', '1 Scope', 'References to numeric facts in ths in document refer to non-fractional numeric facts.'),
        ('N04', '2 Identity', 'All of these would be considered duplicates under the XBRL v2.1 definition of duplicate items.'),
        ('N05', '2 Future OIM', 'It is expected that the forthcoming Open Information Model specification will provide new, formal definitions of these classes of duplicates based on "aspects", rather than the syntactical definitions provided by the XBRL v2.1 specification.'),
        ('N06', '2.1 Complete', 'value equality refers to equality in the value space'),
        ('N07', '2.1 Exclusions', 'the definition above ignores custom attributes (i.e. those not defined by the XBRL specification) and also any footnotes attached to the facts.'),
        ('N08', '2.2 Numeric consistency', 'Consistency of numeric values should be established by considering the interval represented by each reported fact, and ensuring that there is overlap between all intervals.'),
        ('N09', '2.2 Source example', '2,500 (-2 d.p.) => [2450, 2550] 2,000 (-3 d.p.) => [1500, 2500]'),
        ('N10', '2.2 Ties', 'the intervals used in establishing consistency should be inclusive (or "closed"), but with the constraint that values reported to the same accuracy must have the same reported value.'),
        ('N11', '2.2 Unproved assertion', 'The approximation of using closed intervals only affects the outcome of the consistency check in the event that the exact value is also included in the report stated to infinite precision.'),
        ('N12', '2.2 Domain', 'Numeric facts that are Complete Duplicates are also considered to be Consistent Duplicates.'),
        ('N13', '2.3 Translation', 'there is no automatable way to determine if the statements being made in different languages are equivalent.'),
        ('N14', '3 Syntax issue', 'The XBRL v2.1 definition of duplicates is imperfect, as it relies on string equality when comparing the content of elements in the context definition.'),
        ('N15', '4 Attributed Inline claim', 'allows, but does not require, processors to de-duplicate facts that are complete duplicates when transforming from Inline XBRL to XBRL.'),
        ('N16', '5.1 Old calculation limitation', 'Such calculation checks are only performed if neither the total, nor any of the contributing items, have duplicates; the presence of any duplicates effectively disables calculation checks.'),
        ('N17', '5.2 Attributed Formula claim', 'Variables in formula rules will "bind" to each occurrence of a duplicate fact, causing the rules to evaluate for each combination of the duplicate facts involved in the rule.'),
        ('N18', '5.3 Storage', 'individual facts can no longer be uniquely identified by the combination of their aspects'),
        ('N19', '7.3 Non-numeric variation', '"J. Smith" vs "John Smith"'),
        ('N20', '7.4 Highest accuracy', 'When performing summation-item, XBRL Formula, or other processing on XBRL obtained from Inline XBRL, de-duplicate all complete duplicates, and remove all consistent duplicates except the fact that is stated to the highest accuracy'),
        ('N21', '7.4 Alternative', 'an alternative approach would be to only reject numeric, inconsistent duplicates, and accept that inconsistent non-numeric duplicates may be present in the XBRL.'),
        ('N22', 'Appendix D', '17 April 2018 Paul Warren Changed description of method used in establishing consistency of numeric duplicates.'),
        ('N23', 'Appendix E', 'No errata have been incorporated into this document.'),
        ('N24', 'Appendix E Access', 'Access to internal XBRL mailing lists is restricted to members of XBRL International Inc.'),
    ]
    for ident, section, quote in rows:
        anchor(ident, 'note', section, quote)
    anchor('C01', 'calc11', '5.1 Directed alignment', 'Two reported data points, a and b, are dimensionally aligned if for every dimension other than the concept core dimension in the {dimensions} property of a, the same dimension is present in b with an equal dimension value.')
    anchor('C02', 'calc11', '5.4 Reference mismatch', 'Two facts are calculation 1.1 consistent duplicates if they meet the specification for OIM duplicate facts, with the modification that the interval used to establish numeric value consistency is the fact value interval, as defined in this specification.')
    anchor('C03', 'calc11', '5.5 Intersection', 'Where consistent duplicates are present, the calculation is performed using the intersection of fact value intervals for all facts within the set.')
    anchor('C04', 'calc11', '5.4 Claimed equivalence', 'Where the rounding mode is "round-to-nearest", the definitions of calculation 1.1 consistent duplicates and OIM consistent duplicates are equivalent.')
    anchor('O01', 'oim', '6 Identity', 'Two facts, a and b, are duplicate facts if for every dimension in the {dimensions} property of a, the same dimension is present in b with an equal dimension value and vice versa.')
    anchor('O02', 'oim', '6.2.1 Consistency', 'The interval used should be inclusive ("closed"), with the additional constraint that values reported to the same precision are only considered consistent if they have the same reported value.')
    anchor('O03', 'oim', '6.2.1 Nontransitivity', 'the definition of consistency is not transitive; a fact A being consistent with both B and C does not imply that B and C are consistent.')
    anchor('O04', 'oim', '6 Alternatives', 'Unlike duplicate facts, alternative facts are dimensionally distinct, but users may wish to restrict their use as they may provide alternative, and potentially inconsistent, values for the same data point.')
    write('source-ledger.json', {
        'sources': {k: bind(p) for k, p in sources.items()},
        'new_document': {'body': bind(U / 'sources/01-note.body'),
                         'receipt': rel(U / 'sources/01-note.receipt.json'),
                         'requested_url': json.loads((U / 'sources/01-note.receipt.json').read_text())['url'],
                         'edition_url': 'http://www.xbrl.org/WGN/xbrl-duplicates/WGN-2018-04-19/xbrl-duplicates-WGN-2018-04-19.html'},
        'figure': {'original': bind(U / 'sources/02-diagram.body'),
                   'receipt': rel(U / 'sources/02-diagram.receipt.json'),
                   'src': 'images/duplicates-venn.png', 'inspection': 'actually viewed',
                   'finding': 'Complete oval inside Consistent (numeric only); separate multi-language (string only) and inconsistent ovals. Text limits the containment assertion to numeric facts; do not extend it to complete string facts.'},
        'anchors': anchors})
    write('reading-ledger.json', {
        'document': bind(sources['note']), 'visible_lines': 265,
        'coverage': 'Complete sections 1–7.4 and Appendices A–E; one history table',
        'segments': [[1, 110], [111, 140], [141, 185], [186, 225], [226, 265]],
        'recovery': 'Earlier truncated 141–265 read replaced by three complete bounded reads; 1–140 also revisited.',
        'figure': {'inspection': 'actually viewed', 'binding': bind(U / 'sources/02-diagram.body')},
        'comparators': {'calc11': '5.1–5.5 passages revisited', 'oim': '6–6.4 revisited',
                        'req11_req20': 'completed frozen inquiry findings reused; no repeated reading credit'},
        'credit_limit': 'Actual author source reading only; no independent/human acceptance'})
    print(json.dumps({'anchors': len(anchors), 'figures_actually_viewed': 1, 'new_documents': 1}))


if __name__ == '__main__':
    main()
