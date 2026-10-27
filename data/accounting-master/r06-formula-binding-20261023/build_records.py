"""Write exact documentary anchors and reading records once; no new reading."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path

U = Path(__file__).resolve().parent
R = U.parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: str(p.relative_to(R))
bind = lambda p: {'path': rel(p), 'sha256': sha(p)}
norm = lambda s: ' '.join(s.split())


def write(name, value):
    with (U / name).open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')


SPANS = {
    '01-variables': [[1, 225], [487, 612], [1223, 1358], [1440, 1540],
                     [1638, 1970], [2735, 2785], [2840, 2998],
                     [3240, 3290], [3820, 3930]],
    '02-formula': [[1, 80], [1608, 1685], [2890, 2944], [3245, 3272]],
    '03-valueassertions': [[1, 247], [325, 461]],
    '04-variablehistory': [[1, 56]],
    '05-formulahistory': [[1, 41]],
    '06-assertionhistory': [[1, 41]],
    '07-implicitfilters': [[1, 430], [437, 476]],
    '08-validation': [[1, 125], [319, 392], [727, 802]],
    '09-implicithistory': [[1, 41]],
    '10-validationhistory': [[1, 41]],
    '11-xdm': [[1, 94], [532, 557], [608, 650], [4110, 4137], [7135, 7196]],
    '12-xdm20': [[1, 135], [520, 595], [5145, 5275]],
    '13-xdmerrata': [[1, 24]],
    'note2018': [[170, 195]],
}
TITLES = {
    '01-variables': 'XBRL Variables 1.0; Recommendation corrected through 18 November 2013',
    '02-formula': 'XBRL Formula 1.0; Recommendation 22 June 2009',
    '03-valueassertions': 'XBRL Value Assertions 1.0; Recommendation 22 June 2009',
    '04-variablehistory': 'XBRL Variables release history',
    '05-formulahistory': 'XBRL Formula release history',
    '06-assertionhistory': 'XBRL Value Assertions release history',
    '07-implicitfilters': 'XBRL Implicit Filters 1.0; Recommendation 22 June 2009',
    '08-validation': 'XBRL Validation 1.0; Recommendation 22 June 2009',
    '09-implicithistory': 'XBRL Implicit Filters release history',
    '10-validationhistory': 'XBRL Validation release history',
    '11-xdm': 'XQuery and XPath Data Model 3.1; Recommendation 21 March 2017',
    '12-xdm20': 'XQuery 1.0 and XPath 2.0 Data Model, Second Edition; 14 December 2010, revised 7 September 2015',
    '13-xdmerrata': 'Errata for XQuery 1.0 and XPath 2.0 Data Model, Second Edition; placeholder',
    'note2018': 'Handling duplicate facts in XBRL and Inline XBRL 1.0; 19 April 2018 note',
}
paths = {ident: U / 'sources' / (ident + '.visible.txt') for ident in SPANS if ident != 'note2018'}
paths['note2018'] = R / 'data/accounting-master/r06-duplicates-guidance-20261023/sources/01-note.visible.txt'
lines = {key: p.read_text().splitlines() for key, p in paths.items()}
anchors = []


def anchor(ident, source, first, last, section, kind='PRIMARY_TECHNICAL_SUPPORT'):
    assert any(a <= first <= last <= b for a, b in SPANS[source]), ident
    quote = norm('\n'.join(lines[source][first - 1:last]))
    before = norm('\n'.join(lines[source][:first - 1]))
    start = len(before) + bool(before)
    assert norm(paths[source].read_text())[start:start + len(quote)] == quote
    anchors.append({'id': ident, 'source': source, 'section': section,
                    'visible_lines': [first, last], 'quote': quote,
                    'normalized_character_span': [start, start + len(quote)],
                    'support_class': kind})


anchor('N-bind', 'note2018', 175, 185, '5.2', 'ATTRIBUTED_GUIDANCE')
anchor('V-status', '01-variables', 1, 65, 'Title/status')
anchor('V-aspects', '01-variables', 487, 612, '2 aspects and aspect matching')
anchor('V-filter', '01-variables', 1250, 1358, '3.4–3.4.1')
anchor('V-implicit', '01-variables', 1638, 1685, '3.5.3')
anchor('V-precondition', '01-variables', 1686, 1722, '3.5.4')
anchor('V-eval', '01-variables', 1753, 1814, '4, evaluation and special cases')
anchor('V-identical', '01-variables', 1807, 1835, '4, identity and dependencies')
anchor('V-single', '01-variables', 1851, 1865, '4.1, single facts versus sequences')
anchor('V-sequence', '01-variables', 1866, 1893, '4.1, sequence constraints')
anchor('V-empty', '01-variables', 1894, 1932, '4.2')
anchor('V-schema-status', '01-variables', 1933, 1946, 'Appendix A normative introduction and embedded comment')
anchor('V-schema-implicit', '01-variables', 2735, 2785, 'Appendix A, variableSet implicitFiltering')
anchor('V-schema-fact', '01-variables', 2875, 2990, 'Appendix A, factVariable attributes')
anchor('V-xdm-reference', '01-variables', 3240, 3290, 'Appendix B selected dependencies')
anchor('V-errata', '01-variables', 3865, 3922, 'Appendix F, header and 2013 entry')
anchor('F-status', '02-formula', 1, 80, 'Title/status')
anchor('F-eval', '02-formula', 1608, 1633, '3 processing model')
anchor('F-references', '02-formula', 2890, 2944, 'Appendix B')
anchor('F-errata', '02-formula', 3270, 3272, 'Appendix F')
anchor('A-status', '03-valueassertions', 1, 50, 'Title/status')
anchor('A-datasets', '03-valueassertions', 194, 218, '3 processing model')
anchor('A-references', '03-valueassertions', 349, 391, 'Appendix B')
anchor('A-errata', '03-valueassertions', 459, 461, 'Appendix F')
anchor('I-status', '07-implicitfilters', 1, 100, 'Title/status')
anchor('I-rule', '07-implicitfilters', 215, 270, '2 inferred matching filters')
anchor('I-wording', '07-implicitfilters', 270, 294, '2.1 table and dimensional wording')
anchor('I-references', '07-implicitfilters', 375, 428, 'Appendix A')
anchor('I-errata', '07-implicitfilters', 474, 476, 'Appendix E')
anchor('T-status', '08-validation', 1, 65, 'Title/status')
anchor('T-may', '08-validation', 319, 367, '3 processing model')
anchor('T-errata', '08-validation', 800, 802, 'Appendix F')
for ident in ('04-variablehistory', '05-formulahistory', '06-assertionhistory',
              '09-implicithistory', '10-validationhistory'):
    anchor('H-' + ident[:2], ident, 1, len(lines[ident]), 'Complete retained release-history text', 'DOCUMENT_STATUS')
anchor('X31-edition', '11-xdm', 1, 94, 'Title/status', 'DOCUMENT_STATUS')
anchor('X31-reference', '11-xdm', 4110, 4137, 'Normative references to the older XDM', 'DOCUMENT_STATUS')
anchor('X20-edition', '12-xdm20', 1, 114, 'Title/status including 2015 revision', 'DOCUMENT_STATUS')
anchor('X20-identity', '12-xdm20', 533, 540, '2.3 Node Identity')
anchor('X20-sequence', '12-xdm20', 569, 577, '2.5 Sequences')
anchor('X20-changes', '12-xdm20', 5153, 5240, 'Appendix G selected change summary', 'DOCUMENT_STATUS')
anchor('X20-errata', '13-xdmerrata', 1, 24, 'Complete retained placeholder', 'DOCUMENT_STATUS')


class Context(HTMLParser):
    def __init__(self, needles):
        super().__init__(convert_charrefs=True)
        self.stack, self.needles, self.captures = [], needles, []

    def handle_starttag(self, tag, attrs):
        if tag not in ('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                       'link', 'meta', 'param', 'source', 'track', 'wbr'):
            self.stack.append({'tag': tag, 'attrs': dict(attrs)})

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]['tag'] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        for needle in self.needles:
            if needle in norm(data):
                self.captures.append({'needle': needle, 'text_node': norm(data),
                                      'ancestors': list(self.stack)})


html = []
for source, needles in {
    '01-variables': ['Two evaluations of a fact variable are',
                     'No fact occurs more than once in the evaluation result.',
                     'include all possible facts from the source sequence'],
    '02-formula': ['A prerequisite for a formula evaluation'],
    '08-validation': ['be evaluated once for each'],
    '12-xdm20': ['Each node has a unique identity.',
                 'When a node is added to a sequence its identity remains the same.'],
}.items():
    p = U / 'sources' / (source + '.body')
    parser = Context(needles)
    parser.feed(p.read_text())
    html.append({'source': source, 'body': bind(p), 'needles': needles,
                 'captures': parser.captures,
                 'limit': 'Local text-node/ancestor inspection only; no whole-HTML validation.'})

CLAIMS = [
    ('FB01', 'The note gives an unconditional four-evaluation example; its performance/error statements remain attributed.',
     ['N-bind'], 'ATTRIBUTED_GUIDANCE', 'Qualify the binding assumptions; do not report measured cost or error repetition.'),
    ('FB02', 'Fact variables select source facts through nil policy, filters and complements.',
     ['V-filter'], 'PRIMARY_TECHNICAL_SUPPORT', 'Presence in an input instance is not sufficient for binding.'),
    ('FB03', 'Implicit filtering is an explicit variable-set choice and can constrain combinations by uncovered aspects.',
     ['V-implicit', 'I-rule', 'V-schema-implicit'], 'PRIMARY_TECHNICAL_SUPPORT', 'Use explicit false in the local example; no assumed default.'),
    ('FB04', 'Satisfied preconditions and the three special cases govern whether a variable-set evaluation occurs.',
     ['V-precondition', 'V-eval', 'V-empty'], 'PRIMARY_TECHNICAL_SUPPORT', 'Failure to evaluate is not automatically duplicate elimination.'),
    ('FB05', 'Variable-set identity compares fact-variable evaluations; sequence order alone does not distinguish them.',
     ['V-identical', 'V-sequence'], 'PRIMARY_TECHNICAL_SUPPORT', 'Do not replace fact identity with numeric equality.'),
    ('FB06', 'Without sequence binding, each selected nonempty fact sequence permits individual facts, subject to evaluation rules.',
     ['V-single', 'V-eval'], 'PRIMARY_TECHNICAL_SUPPORT', 'This supports the conditional four-data-set example.'),
    ('FB07', 'Sequence binding has same-uncovered-aspect-set/equivalence, occurrence, maximality and matches constraints.',
     ['V-sequence', 'V-aspects'], 'PRIMARY_TECHNICAL_SUPPORT', 'Sequence binding alone does not universally collapse duplicates.'),
    ('FB08', 'With matches omitted or false, aspect-matched facts cannot occur together in a sequence-bound result.',
     ['V-sequence'], 'PRIMARY_TECHNICAL_SUPPORT', 'The all-duplicates sequence example must state matches=true.'),
    ('FB09', 'Empty sources without fallback cannot evaluate; fallback expressions cannot reference fact/general variables.',
     ['V-empty'], 'PRIMARY_TECHNICAL_SUPPORT', 'Fallback does not make the simple product unconditional.'),
    ('FB10', 'Different variable-set evaluations form different value-assertion data sets; their tests are effective Boolean values.',
     ['A-datasets'], 'PRIMARY_TECHNICAL_SUPPORT', 'Different data sets need not produce different Boolean results.'),
    ('FB11', 'Validation says an assertion MAY be evaluated once for each data set; this is not a mandatory call count.',
     ['T-may', 'A-datasets'], 'PRIMARY_TECHNICAL_SUPPORT', 'No conclusion about a particular processor or conformance suite.'),
    ('FB12', 'Formula-expression evaluation and optional output-fact construction are separate from value-assertion tests.',
     ['F-eval', 'A-datasets'], 'PRIMARY_TECHNICAL_SUPPORT', 'Do not conflate Formula output facts with assertion errors.'),
    ('FB13', 'The retained XPath2 XDM gives each node unique identity and preserves it in sequences.',
     ['X20-identity', 'X20-sequence', 'X20-edition'], 'PRIMARY_TECHNICAL_SUPPORT', 'Numeric equality and author-assigned XML IDs do not establish node identity.'),
    ('FB14', 'The undated XDM route returns3.1; the dated2.0 source says2010 revised2015 and the errata page is a placeholder.',
     ['X31-edition', 'X31-reference', 'X20-edition', 'X20-errata'], 'DOCUMENT_STATUS', 'No2009/2010/2015 byte-equivalence or worldwide no-errata claim.'),
    ('FB15', 'Retained histories identify Variables2013 and the other four2009 recommendations; embedded errata claims are dated.',
     ['H-04', 'H-05', 'H-06', 'H-09', 'H-10', 'V-errata', 'F-errata', 'A-errata', 'I-errata', 'T-errata'],
     'DOCUMENT_STATUS', 'The Variables header/body date drift is preserved; no latest-worldwide claim.'),
    ('FB16', 'Four possible singleton fact-variable pairs yield four different data sets under the stated hypotheses.',
     ['V-identical', 'V-single', 'V-eval', 'A-datasets', 'X20-identity'], 'PROJECT_DERIVATION',
     'A conditional logical derivation, not a processor trace or an economic-history count.'),
    ('FB17', 'For two aspect-matched duplicates per variable, sequence=true and matches=true permit one maximal pair of sequences.',
     ['V-sequence', 'V-aspects', 'V-eval', 'A-datasets'], 'PROJECT_DERIVATION',
     'Changing matches to false restores singleton choices in this narrowly defined example.'),
    ('FB18', 'Removing an occurrence can change sequence cardinality and a test that observes it.',
     ['V-sequence', 'A-datasets', 'X20-sequence'], 'PROJECT_DERIVATION',
     'There is no general result-preserving de-duplication recommendation.'),
]

images = []
for source in SPANS:
    if source == 'note2018':
        continue
    meta = json.loads((U / 'sources' / (source + '.structure.json')).read_text())
    for image in meta['images']:
        logo = source.endswith('history') or image.get('alt') == 'W3C'
        images.append({'source': source, 'image': image,
                       'classification': 'navigation_logo' if logo else 'technical_not_used',
                       'actually_viewed_in_this_unit': False,
                       'reason': 'No technical claim from a logo.' if logo else
                       'Type hierarchy/example model is outside the selected identity/sequence argument; not acquired or used.'})

reading_rows = []
for source, spans in SPANS.items():
    reading_rows.append({'source': source, 'binding': bind(paths[source]),
                         'visible_lines': len(lines[source]), 'actually_read_spans': spans,
                         'whole_document_read_in_this_unit': spans == [[1, len(lines[source])]],
                         'credit_basis': 'Resumed recorded technical reading plus the bounded successor reads; extraction/search alone gives no credit.'})

source_rows = {}
new_documents = {}
for source in SPANS:
    source_rows[source] = {**bind(paths[source]), 'title': TITLES[source]}
    if source != 'note2018':
        new_documents[source] = bind(U / 'sources' / (source + '.body'))

claims = [{'id': ident, 'claim': claim, 'support': support,
           'support_class': kind, 'disposition': disposition}
          for ident, claim, support, kind, disposition in CLAIMS]
rules = [{**row, 'target': '2018 note5.2, qualified against the retained normative sources',
          'installed_behavior_checked': False} for row in claims]

assumptions = []
for choice, provenance, justification, failure, diagnostic, status in [
    ('Exact dated normative editions', 'retained official index, histories and source headers',
     'Rules can be anchored to an inspected document.', 'Undated links change editions.',
     'Header/status plus bounded dated-XDM and errata repair.', 'reviewed default within this documentary inquiry'),
    ('Two distinct nonnil duplicate nodes per variable', '2018 note5.2, made explicit as a symbolic example',
     'Isolates occurrence identity.', 'Numeric equality confused with node identity or actual filing validity.',
     'XDM2.3; explicit distinctness and no validity claim.', 'baseline illustration'),
    ('Explicit bindAsSequence=false and implicitFiltering=false', 'local controlled example, not inherited policy',
     'Isolates four independent singleton choices.', 'A hidden sequence/filter setting changes the answer.',
     'Variables4.1 and embedded required attributes; compare sequence variants.', 'hypothesis'),
    ('No preconditions, fallbacks, dependencies or ambiguous aspects', 'local controlled example',
     'Keeps the Variables4 special cases from applying.', 'Product pairs may not be evaluable.',
     'List these conditions and give failed-precondition/empty-source countercases.', 'hypothesis'),
    ('Aspect-matched duplicates and matches=true in the sequence variant', 'explicit local variant under Variables2/4.1',
     'Makes maximal same-aspect sequences eligible.', 'Omitted/false matches prevents joint membership.',
     'Read every sequence constraint; retain the matches=false comparison.', 'hypothesis'),
    ('No timed processor experiment', 'proposal-only authority and held runtime work',
     'The question concerns source semantics.', 'Logical pair counts mistaken for measured invocations.',
     'Label every example symbolic; preserve Validation MAY.', 'scope constraint'),
]:
    assumptions.append(dict(choice=choice, provenance=provenance, justification=justification,
                            failure_mode=failure, early_diagnostic=diagnostic, promotion_status=status))

example = {
    'kind': 'conditional symbolic derivation; not executable XML, XPath or a processor trace',
    'nodes': ['A1', 'A2', 'B1', 'B2'],
    'hypotheses': ['All four nodes are distinct; A1/A2 are aspect-matched duplicates, as are B1/B2.',
                   'The fixed filtered sources are exactly (A1,A2) and (B1,B2); all facts are nonnil.',
                   'implicitFiltering=false is explicit. No dependencies, fallbacks, preconditions or ambiguous aspects.',
                   'Each variable uses its own concept; no actual filing, filter implementation or XPath schema is validated.'],
    'cases': [
        {'id': 'singletons', 'bindAsSequence': False,
         'possible_bindings': [['A1', 'B1'], ['A1', 'B2'], ['A2', 'B1'], ['A2', 'B2']],
         'distinct_possible_data_sets': 4,
         'reason': 'Each source has two eligible singleton node choices. Every pair differs in a fact-variable node identity.'},
        {'id': 'sequence_matches_true', 'bindAsSequence': True, 'matches': True,
         'possible_bindings': [[['A1', 'A2'], ['B1', 'B2']]],
         'distinct_possible_data_sets': 1,
         'reason': 'All facts within each source satisfy the equivalence and aspect-set constraints. Maximality includes both; order alone adds no evaluation.'},
        {'id': 'sequence_matches_false', 'bindAsSequence': True, 'matches': False,
         'possible_bindings': [[['A1'], ['B1']], [['A1'], ['B2']], [['A2'], ['B1']], [['A2'], ['B2']]],
         'distinct_possible_data_sets': 4,
         'reason': 'No result can contain the two aspect-matched facts together; each singleton is maximal under that restriction.'},
        {'id': 'failed_precondition', 'change_from': 'singletons', 'distinct_possible_data_sets': 0,
         'reason': 'A precondition false for every pair prevents a variable-set evaluation.'},
        {'id': 'empty_A_no_fallback', 'change_from': 'singletons', 'distinct_possible_data_sets': 0,
         'reason': 'An empty A source without fallback cannot evaluate.'},
    ],
    'cardinality_witness': {
        'mathematical_test': 'The length of the A binding equals2; this is mathematical notation, not a tested XPath expression.',
        'before': 'In sequence_matches_true, the A binding has length2 and the test is true.',
        'after_removing_A2': 'The only A binding has length1 and the test is false.',
        'conclusion': 'General observational equivalence under occurrence removal does not follow.',
    },
    'mandatory_processor_call_count': 'not established', 'performance_or_error_count': 'not measured',
    'support': ['V-single', 'V-sequence', 'V-eval', 'V-identical', 'A-datasets', 'T-may', 'X20-identity'],
}

outputs = {
    'source-ledger.json': {'sources': source_rows, 'new_documents': new_documents,
                           'anchors': anchors, 'discovery_index': bind(R / 'data/accounting-master/r06-normative-schema-20261018/sources/02-index.body'),
                           'earlier_note_inquiry': bind(R / 'data/accounting-master/r06-duplicates-guidance-20261023/completion.json')},
    'reading-ledger.json': {'whole_specification_read': False, 'whole_formula_family_read': False,
                            'sources': reading_rows, 'images': images,
                            'limit': 'Selected local rules, dependencies and histories only. Prior manuscript/source diagnoses are not repeated.'},
    'html-inspection.json': {'rows': html, 'method': 'Static HTML text-node and ancestor inspection; no acquired code execution.'},
    'claim-support-ledger.json': {'claims': claims},
    'rule-comparison.json': {'rows': rules},
    'assumption-audit.json': {'rows': assumptions},
    'binding-example.json': example,
}
assert len({a['id'] for a in anchors}) == len(anchors)
assert all(set(row['support']) <= {a['id'] for a in anchors} for row in claims)
assert all(not (U / name).exists() for name in outputs)
for name, value in outputs.items():
    write(name, value)
print(json.dumps({'documents': len(new_documents), 'anchors': len(anchors),
                  'claims': len(claims), 'symbolic_cases': len(example['cases']),
                  'html_captures': [len(row['captures']) for row in html], 'writes_once': len(outputs)}))
