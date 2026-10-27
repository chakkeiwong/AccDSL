"""Construct the unfinished documentary unit once; never execute acquired code."""
import importlib.util
import json
from pathlib import Path

U = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('textblock_dependencies', U / 'compare.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
R, B = m.R, m.B

def write(name, value):
    with (U / name).open('x', encoding='utf-8') as handle:
        json.dump(value, handle, indent=2)
        handle.write('\n')

targets = ['dependencies.json', 'source-ledger.json', 'acquisitions.json',
           'source-support-ledger.json', 'citation-venue-ledger.json',
           'backward-snowball-ledger.json', 'forward-snowball-ledger.json',
           'claim-support-ledger.json', 'omission-risk-ledger.json']
assert not any((U / name).exists() for name in targets), 'one successful construction only'
value = m.derive()
paths = {U / 'compare.py', U / 'build_records.py', U / 'dependency-plan-addendum.md',
         m.VALIDATOR, m.COMMAND, m.CONTROLLER, m.DISCLOSURE,
         B / 'r06-textblock-fragments-20261020/occurrences.json',
         m.P / 'result.md',
         R / 'docs/design/proposal/manuscript-early-conversion-20261018/sections/adapter-methods.tex'}
paths.update(p for p in (U / 'sources').iterdir() if p.is_file())
paths.update(m.P / 'sources' / (name + '-sandbox.body')
             for name in ('edbody.dtd', 'xhtml1-strict-ix.dtd'))
spans = [
    (m.CONTROLLER, [(22,29), (309,318)]),
    (m.COMMAND, [(1804,1821)]),
    (m.source('ModelManager'), [(1,16), (206,217)]),
    (m.source('Validate'), [(45,83), (144,159)]),
    (m.source('ValidateXbrl'), [(129,165), (440,453)]),
    (m.source('FERC'), [(20,36), (39,85), (221,234)]),
    (m.source('FERC-config'), [(1,54)]),
    (m.source('disclosuresystems'), [(1,55)]),
    (m.DISCLOSURE, [(135,156), (203,205), (245,282)]),
    (m.source('ModelDocument'), [(30,45)]),
    (m.source('ModelDocumentType'), [(1,34)]),
    (m.VALIDATOR, [(360,378), (424,429), (524,577)]),
    (m.P / 'sources/edbody.dtd-sandbox.body', [(1,45)]),
    (m.P / 'sources/xhtml1-strict-ix.dtd-sandbox.body', [(1,39)]),
]
for name in ('xhtml-lat1', 'xhtml-symbol', 'xhtml-special'):
    path = m.source(name)
    spans.append((path, [(1, len(path.read_text().splitlines()))]))
anchors = []
for path, ranges in spans:
    lines = path.read_text().splitlines()
    for first, last in ranges:
        assert 1 <= first <= last <= len(lines), (path.name, first, last, len(lines))
        anchors.append({'source': m.bind(path), 'first_line': first, 'last_line': last,
                        'excerpt': '\n'.join(lines[first-1:last])})

write('source-ledger.json', {
    'bindings': [m.bind(path) for path in sorted(paths)], 'anchors': anchors,
    'scope': 'Exact-pin caller/configuration spans and finite entity-resource grammar; no installed or generic validity claim',
})
write('dependencies.json', value)
receipts = sorted((U / 'sources').glob('*-receipt.json'))
write('acquisitions.json', {'attempts': [m.bind(path) for path in receipts],
                            'commit': m.PIN, 'upstream_code_execution': False})
write('source-support-ledger.json', {
    'classification': 'IMPLEMENTATION_OR_SOFTWARE', 'commit': m.PIN,
    'sources': [row['git_path'] for row in value['identities']['verified_blobs']],
    'technical_read': 'source-ledger.json anchors; complete simple entity files statically inventoried',
    'allowed': ['one concrete guarded caller', 'two active FERC profiles',
                'six DTD/entity edges', '253 entity declarations', 'whitelist name mismatch',
                'source-conditional inline/document-set DTD distinction'],
    'forbidden': ['global caller completeness', 'Apple profile applicability', 'installed correspondence',
                  'generic XHTML/DTR validity', 'issuer content invalidity', 'runtime impact'],
    'publication_status': 'pinned official source, not an academic-paper or latest-policy inquiry',
    'quarantine_status': 'no source identity conflict observed; upstream correctness not presumed',
})
write('citation-venue-ledger.json', {
    'citation_count': 'not applicable to this software-source inquiry',
    'venue': 'official Arelle source at the retained exact pin',
    'metadata_is_not_correctness_evidence': True,
})
write('backward-snowball-ledger.json', {
    'resolved': ['both DTDs three external entity declarations',
                 'manager/dispatch/core hook path', 'one FERC caller and its config',
                 'ModelDocument.Type alias and ModelDocumentType constants'],
    'open': ['inlineXbrlDocumentSet dependency', 'configuration schema',
             'UTR resources', 'plugin enumeration/loading dependencies'],
    'dependency_closure': 'finite DTD/entity slice only; whole processor remains open',
})
write('forward-snowball-ledger.json', {
    'scope': 'exact selected commit; no latest-version, external-plugin or filing-policy survey',
    'tree': {'commit': m.PIN, 'entries': value['identities']['tree_entries'], 'truncated': False},
    'limit': 'path metadata cannot establish repository-wide content/caller absence',
})
write('claim-support-ledger.json', {
    'claims': [
        {'claim': 'the checker has a concrete profile-conditional caller',
         'support': 'FERC lines39-85/221-234 and manager/core anchors', 'role': 'source-specific evidence'},
        {'claim': 'equal entity counts conceal different names',
         'support': 'ValidateFilingText line371 and xhtml-symbol line183; dependencies.json inventories',
         'role': 'source-specific evidence'},
        {'claim': 'document-set treatment differs between caller and DTD selector',
         'support': 'FERC lines70-75; loadDTD lines524-533; checked alias and constants',
         'role': 'conditional source inference; not an executed behavior'},
        {'claim': 'the two differing names have a bounded retained-content occurrence diagnostic',
         'support': 'dependencies.json retained_name_occurrences', 'role': 'explanatory only'},
    ],
})
write('omission-risk-ledger.json', {
    'open': ['external/installed plugins and actual selected disclosure system',
             'real fact f.value correspondence', 'full XHTML/schema/DTS validation',
             'DTD engine and external-resolution behavior', 'cache lifetime/config-directory changes',
             'actual build/native/transitive identity', 'rendered financial meaning'],
    'effect': 'dependent admission remains unestablished; preserve all original disclosures',
    'no_professional_referral': 'continue feasible internal work under MC35; no outreach or fees',
})
print(json.dumps({'anchors': len(anchors), 'bindings': len(paths),
                  'entity_declarations': value['entities']['unique_entities'],
                  'source_findings': len(value['caller']['findings']), 'acquisitions': len(receipts),
                  'literal_name_occurrences': value['retained_name_occurrences']['names']}))
