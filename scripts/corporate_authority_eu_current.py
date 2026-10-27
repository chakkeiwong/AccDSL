"""Validate retained EU preparation without granting accounting admission.

Typed RDF relations establish document relationships. Quote and pin checks
establish integrity. Pending applicability decisions remain admission vetoes.
"""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
REGISTER = 'docs/design/research/p08-v6/source-disposition.json'
PREVIOUS = ('docs/design/research/p08-v3/authority-register.json',
            'docs/design/research/p08-v4/source-inspection.json',
            'docs/design/research/p08-v5/source-inspection.json')
RDF = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'
CDM = 'http://publications.europa.eu/ontology/cdm#'
RELATIONS = {'cited_by': 'citation', 'work_cited_by_work': 'citation',
             'amended_by': 'amendment', 'resource_legal_amended_by_resource_legal': 'amendment',
             'corrected_by': 'correction', 'resource_legal_corrected_by_resource_legal': 'correction'}
SOURCES = {
    'docs/design/research/p08-v3-preparation/eu-2023-1803-metadata.rdf': {
        'http://publications.europa.eu/resource/celex/32023R1803',
        'http://publications.europa.eu/resource/celex/32023R1803R%2801%29'},
    'docs/design/research/p08-v4/scope-work.rdf': {
        'http://publications.europa.eu/resource/celex/32002R1606'},
}
EEA = {'202500572', '202500768', '202501358', '202600237', '202600240', '202600593'}
CONTEXT = {
    'jurisdiction': 'EU Member State; not an EEA extension determination',
    'periods': ['2024', '2025'], 'original_period_reports': True,
    'early_adoption': False, 'later_comparative_restatement': False,
    'existing_ifrs_preparer': True,
    'eligibility': 'hypothetical Member State-law company; securities admitted on a regulated market in a Member State; consolidated reporting',
    'currency': 'AUD denomination, functional and presentation currency',
    'group_terms': 'external holders; no additional guarantees or settlement arrangements',
    'instrument': 'maturity-only fixed-for-fixed nonputtable ordinary shares; no contingent/net-cash option terms or other embedded derivatives',
}


def validate_disposition(root=ROOT, records=None):
    root = Path(root).resolve()
    def path(name):
        if not isinstance(name, str) or not name:
            raise ValueError('invalid disposition path')
        p = Path(name); target = root / p
        if (p.is_absolute() or '..' in p.parts or p.as_posix() != name
                or target.is_symlink() or not target.resolve().is_relative_to(root)):
            raise ValueError('unsafe disposition path')
        return target
    def read(name):
        return json.loads(path(name).read_text())
    d = read(REGISTER) if records is None else deepcopy(records)
    if not isinstance(d, dict) or d.get('schema_version') != 'accdsl.p08.eu_source_disposition.v6':
        raise ValueError('disposition schema')
    if d.get('admission_allowed') is not False or d.get('status') != 'partial_preparation_semantic_review_pending':
        raise ValueError('preparation cannot grant admission')
    if d.get('reporting_context') != CONTEXT:
        raise ValueError('unsupported or contradictory reporting assumptions')
    pins = d.get('source_pins', [])
    if not isinstance(pins, list) or not pins:
        raise ValueError('missing source pins')
    hashes = {}
    for pin in pins:
        name = pin['path']
        if name in hashes:
            raise ValueError('duplicate source pin')
        hashes[name] = sha256(path(name).read_bytes()).hexdigest()
        if hashes[name] != pin['sha256']:
            raise ValueError('stale source pin: ' + name)
    previous = [read(name) for name in PREVIOUS]
    required = set(PREVIOUS) | set(SOURCES)
    required.update(pin['path'] for doc in previous for pin in doc['source_pins'])
    correction_access = 'docs/design/research/p08-v6/portuguese-correction-access.json'
    access = read(correction_access)
    required.add(correction_access)
    for source in [*access['sources'], access['extraction']]:
        required.add(source['path'])
        if hashes.get(source['path']) != source['sha256']:
            raise ValueError('correction evidence pin')
    if not required <= hashes.keys():
        raise ValueError('missing transitive source pin')

    expected = set()
    for source, subjects in SOURCES.items():
        tree = ElementTree.fromstring(path(source).read_bytes())
        for node in tree:
            subject = node.get(RDF + 'about')
            if subject not in subjects:
                continue
            for predicate in node:
                name = predicate.tag.removeprefix('{' + CDM + '}')
                obj = predicate.get(RDF + 'resource')
                if name in RELATIONS and obj:
                    expected.add((source, subject, CDM + name, obj, RELATIONS[name]))
    observed = set()
    for relation in d.get('relationships', []):
        item = tuple(relation[k] for k in ('source', 'subject', 'predicate', 'object', 'classification'))
        if item in observed or hashes.get(relation['source']) != relation['sha256']:
            raise ValueError('duplicate relationship or stale RDF pin')
        observed.add(item)
    if not expected or observed != expected:
        raise ValueError('relationship coverage or exact subject/predicate classification')
    if set(d.get('eea_citations', [])) != EEA or len(d['eea_citations']) != len(EEA):
        raise ValueError('EEA citation coverage')
    base = 'http://publications.europa.eu/resource/celex/32023R1803'
    for document in EEA:
        target = 'http://publications.europa.eu/resource/oj/L_' + document
        rows = [r for r in observed if r[1] == base and r[3] == target]
        if not rows or any(r[4] != 'citation' for r in rows):
            raise ValueError('EEA incorporation is not an EU regulation amendment')

    texts = {}
    def anchor(a):
        name = a['text']
        if name not in hashes or not (a.get('paragraph') or a.get('section')) or not a.get('quote', '').strip():
            raise ValueError('missing or unpinned anchor')
        if name not in texts:
            texts[name] = path(name).read_text()
        text = texts[name]
        if 'pdf_page' in a:
            pages = text.split('\f'); page = a['pdf_page']
            if type(page) is not int or not 1 <= page <= len(pages):
                raise ValueError('invalid anchor page')
            text = pages[page - 1]
        if ' '.join(a['quote'].split()) not in ' '.join(text.split()):
            raise ValueError('unresolved source quotation')
    claims = d.get('claims', [])
    original_claims = {c['id']: c for c in previous[0]['claims']}
    if len(claims) != len(original_claims) or {c['id'] for c in claims} != original_claims.keys():
        raise ValueError('required claim coverage')
    for claim in claims:
        if claim['anchor'] != original_claims[claim['id']]['anchor']:
            raise ValueError('claim anchor differs from retained primary inspection')
        anchor(claim['anchor'])
        if (claim.get('decision') != 'primary_passage_retained_applicability_review_pending'
                or not claim.get('remaining_uncertainty') or not claim.get('dependencies')
                or claim.get('effective_period') != CONTEXT['periods']
                or set(claim.get('reporting_assumptions', [])) != CONTEXT.keys()):
            raise ValueError('claim applicability must remain explicitly pending')
        for field, links in [('affected_events', previous[0]['operation_dependencies']),
                             ('affected_notes', previous[0]['note_links'])]:
            if set(claim.get(field, [])) != {name for name, ids in links.items() if claim['id'] in ids}:
                raise ValueError('claim operation/note dependency coverage')
    history = d.get('historical_inspection_rows', [])
    history_ids = {x.get('document', x.get('id')) for x in history}
    required_history = {x['document'] for x in previous[0]['amendment_matrix']} | {x['id'] for x in previous[1]['sources']}
    if (len(history) != len(history_ids) or history_ids != required_history
            or not d.get('historical_inspection_boundary') or 'retained_amendment_decisions' in d):
        raise ValueError('historical inspections cannot assign current amendment status')
    inspections = d.get('inspections', [])
    expected_inspections = {x['id'] for x in previous[2]['inspections']} | {'scope-corr-2003-portuguese'}
    if len(inspections) != len(expected_inspections) or {x['id'] for x in inspections} != expected_inspections:
        raise ValueError('omitted correction or eligibility inspection')
    for row in [*history, *inspections]:
        for a in ([row['anchor']] if 'anchor' in row else row.get('anchors', [])):
            anchor(a)
    correction = d.get('correction_2003', {})
    if (correction.get('affected') != ['recital 7', 'recital 9', 'Article 2']
            or correction.get('article_4_changed') is not False or correction.get('access_resolved') is not True
            or correction.get('inspection') not in hashes):
        raise ValueError('Portuguese correction disposition')
    correction_text = path(access['extraction']['path']).read_text()
    if any(phrase not in correction_text for phrase in ('no considerando 7', 'no considerando 9', 'no artigo 2.o')):
        raise ValueError('Portuguese corrected provisions not grounded')
    unresolved = d.get('unresolved_dependencies', [])
    expected_unresolved = {'claim-specific-applicability': 'promotion_veto',
                           'transition-decisions': 'promotion_veto', 'eu-lifecycle': 'deferred_implementation'}
    if (len(unresolved) != len(expected_unresolved)
            or {r['id']: r['role'] for r in unresolved} != expected_unresolved
            or any(not r.get('work', '').strip() for r in unresolved)):
        raise ValueError('missing unresolved admission dependency')
    return d
