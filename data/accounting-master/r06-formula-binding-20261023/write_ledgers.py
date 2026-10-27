"""Write the remaining five research ledgers once; claim ledger already exists."""
import json
from pathlib import Path

U = Path(__file__).resolve().parent
d = json.loads((U / 'source-ledger.json').read_text())
reading = json.loads((U / 'reading-ledger.json').read_text())


def write(name, value):
    with (U / name).open('x') as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
        f.write('\n')


sources = []
for ident, value in d['sources'].items():
    history = ident.endswith('history')
    w3c = ident in ('11-xdm', '12-xdm20', '13-xdmerrata')
    if ident == 'note2018':
        url = json.loads((U.parent / 'r06-duplicates-guidance-20261023/sources/01-note.receipt.json').read_text())['url']
        status = 'Frozen2018 guidance, not a normative Formula specification.'
    else:
        url = json.loads((U / 'sources' / (ident + '.receipt.json')).read_text())['url']
        status = ('Official release-history metadata, not technical rules.' if history else
                  'W3C errata placeholder; no entries in the retained24-line text.' if ident == '13-xdmerrata' else
                  'W3C Recommendation; actual title/revision boundary retained.' if w3c else
                  'XBRL Recommendation, normative subject to locally marked non-normative material.')
    sources.append({'id': ident, 'title': value['title'],
                    'corporate_author_or_publisher': 'W3C' if w3c else 'XBRL International',
                    'individual_authors_editors': 'Credits retained in local header; not independently disambiguated in this ledger.',
                    'year': '2010; source revised2015' if ident == '12-xdm20' else
                            '2017' if ident == '11-xdm' else '2010' if ident == '13-xdmerrata' else
                            '2018' if ident == 'note2018' else '2009; corrected2013' if ident == '01-variables' else
                            '2009' if not history else 'See retained release table; access2026-10-23',
                    'doi_arxiv': 'N/A official technical publication', 'url': url, 'local': value,
                    'publication_status': status,
                    'retraction_quarantine': 'No notice in inspected header/history; not a global search.',
                    'correction_check': 'Five retained histories; four2009 embedded no-incorporated-errata statements; Variables2010-header/2013-entry drift; dated XDM status/change summary and separate placeholder.',
                    'full_text_status': 'Complete retained body; only recorded spans credited as read.',
                    'inspected_spans': next(row['actually_read_spans'] for row in reading['sources'] if row['source'] == ident),
                    'technical_anchors': [a['id'] for a in d['anchors'] if a['source'] == ident],
                    'allowed': 'Scoped documentary claims and separately labelled local derivations.',
                    'forbidden': 'Installed processor behavior, timings, historical byte equivalence, full conformance or policy promotion.'})

refs = [
    ('2018 duplicate-facts note5.2', 'DIRECT_METHOD', 'Frozen exact comparator reused; no Formula technical reference in its previously inspected AppendixA. Official index is the independent discovery source.'),
    ('Variables, Formula, Value Assertions, Implicit Filters, Validation', 'FOUNDATIONAL', 'Acquired once and selected governing rules inspected; not the complete Formula suite.'),
    ('Five official release histories', 'BACKGROUND', 'Complete retained text read; dates/status only, no global latest claim.'),
    ('XPath2 XDM', 'FOUNDATIONAL', 'Undated route returned3.1; dated2010 Second Edition revised2015 read locally; errata placeholder checked. Original2007/2009 bytes not acquired.'),
    ('XBRL2.1 and XBRL Dimensions', 'FOUNDATIONAL', 'Existing source evidence remains frozen. No new full-specification validation or DTS/schema execution.'),
    ('Match/Concept/Dimension/Period Filters', 'DIRECT_METHOD', 'References screened in Implicit Filters AppendixA. Exact filter implementation is outside the symbolic fixed-source example; no full match-predicate derivation claimed.'),
    ('XBRL function registry, Function Definitions and instance functions', 'DIRECT_METHOD', 'Variables cross-references retained. No XPath engine invocation or custom-function validation.'),
    ('XPath2, XML, XML Names, XML Schema, XLink and generic links', 'FOUNDATIONAL', 'Relevant references screened from selected appendices; full language/link/schema conformance not evaluated.'),
    ('RFC2119 and publication-process conventions', 'BACKGROUND', 'Requirement wording retained exactly; no process-certification claim.'),
    ('Existence/consistency assertions, Formula conformance suites and processor code', 'IMPLEMENTATION_OR_SOFTWARE', 'Other assertion families and installed behavior remain outside this value-assertion inquiry; runtime/acquired-code work is held.'),
]
outputs = {
    'source-support-ledger.json': {'scope': 'Official documentary inquiry; selected reading only', 'sources': sources},
    'citation-venue-ledger.json': {'rows': [
        {'id': row['id'], 'access_date': '2026-10-23 Asia/Shanghai; observed UTC brackets in receipts',
         'citation_count': 'not available; not queried', 'citation_source': 'No citation-metadata service queried',
         'venue': row['corporate_author_or_publisher'] + ' technical publications',
         'venue_metric': 'N/A standards/guidance; no journal ranking inference',
         'caveat': 'Source authority follows checked document status, not citation counts.'} for row in sources]},
    'backward-snowball-ledger.json': {'scope': 'Relevant selected technical cross-references and reference appendices; not a complete citation survey',
        'rows': [{'work': work, 'classification': cls, 'disposition': disposition} for work, cls, disposition in refs]},
    'forward-snowball-ledger.json': {'rows': [
        {'source': ident, 'query': 'Complete retained official release-history table',
         'access_date': '2026-10-23 Asia/Shanghai',
         'disposition': 'Variables2013; Formula/ValueAssertions/ImplicitFilters/Validation2009 in these tables only; no global no-successor claim.'}
        for ident in ('04-variablehistory', '05-formulahistory', '06-assertionhistory', '09-implicithistory', '10-validationhistory')]
        + [{'source': 'W3C XDM', 'query': 'Undated route, exposed dated reference and exact second-edition errata link',
            'disposition': 'Actual3.1 and2010/revised2015 identities preserved; placeholder is not a worldwide no-errata result.'},
           {'source': 'Scholarly citing works', 'query': 'not performed',
            'disposition': 'Normative-rule comparison only; no scholarly coverage or citation-ranking claim.'}]},
    'omission-risk-ledger.json': {'rows': [
        {'omission': work, 'reason': disposition,
         'reviewer_risk': 'A broader claim would need the omitted governing source or execution evidence.',
         'status': 'acceptable only within the explicit local scope'} for work, _, disposition in refs[4:]]
        + [{'omission': 'Original XPath2 XDM2007/2009 byte equivalence and2015 revision diff',
            'reason': 'No original-byte reconstruction claimed; the exact returned dated source is identified.',
            'reviewer_risk': 'Cannot infer what every original2009 processor saw.', 'status': 'blocks historical equivalence claim only'},
           {'omission': 'Technical XDM figures', 'reason': 'Not used for the identity/sequence argument; recorded as not viewed.',
            'reviewer_risk': 'No type-hierarchy or worked-model claim allowed.', 'status': 'acceptable selected-reading scope'},
           {'omission': 'Calculations1.1 sections5.1/5.4 source tensions',
            'reason': 'Separate frozen inquiry; Formula text cannot resolve it.',
            'reviewer_risk': 'Do not import the2018 reduction recommendation into final1.1.', 'status': 'still unresolved'}]},
}
assert all(not (U / name).exists() for name in outputs)
for name, value in outputs.items():
    write(name, value)
print(json.dumps({'additional_research_ledgers': len(outputs), 'total_research_ledgers': 6,
                  'source_rows': len(sources), 'new_reading_credit_from_this_script': 0}))
