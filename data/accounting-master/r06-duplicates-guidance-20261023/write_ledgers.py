"""One-time documentary claim and dependency records; no external code execution."""
import json
from pathlib import Path

U = Path(__file__).resolve().parent


def write(name, value):
    with (U / name).open('x') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


def main():
    assert (U / 'source-ledger.json').exists()
    assert not (U / 'claim-support-ledger.json').exists()
    rows = [
        ('D01', ['N03', 'N04', 'N05', 'O01'], 'Identity',
         'The note inherits XBRL2.1 syntactic duplicate items and excludes fractions; OIM identity requires bidirectional equality of every dimension.',
         'Different definitions/domains; no automatic identity equivalence.'),
        ('D02', ['N06', 'N07'], 'Complete occurrences',
         'The note compares value-space values plus numeric inferred decimals or effective string language; custom attributes and footnotes are ignored.',
         'Processing equality cannot authorise loss of original occurrences, attributes, footnotes or provenance.'),
        ('D03', ['N08', 'N09', 'O02', 'O03'], 'Numeric consistency',
         'The note and OIM require an underlying value compatible with all intervals; OIM explicitly warns that consistency is nontransitive.',
         'A duplicate class must not be built from transitive closure of pairwise consistency.'),
        ('D04', ['N10', 'O02'], 'Equal accuracy',
         'Both texts supplement closed intervals with equal reported values at the same accuracy.',
         'Endpoint overlap alone is insufficient for duplicate consistency.'),
        ('D05', ['N10', 'N11'], 'Rounding',
         'The note permits both endpoints and distinguishes ties under half-even versus half-away rounding.',
         'The source assertion about infinite precision is attributed only; neither its proof nor an issuer rounding policy was checked.'),
        ('D06', ['N13', 'O01', 'O04'], 'Language',
         'The note calls different-language strings multi-language duplicates; OIM makes language a dimension and calls differing-language facts alternatives.',
         'No translation-equivalence inference; terminology must retain its source model.'),
        ('D07', ['N20', 'C03'], 'Downstream reduction',
         'The note recommends keeping highest accuracy; final1.1 requires intersection of every fact interval.',
         'The frozen prior exact witness already distinguishes these quantities; no arithmetic rerun or new policy.'),
        ('D08', ['N04', 'N14', 'C01', 'O01'], 'Alignment question',
         'Historical syntactic duplicate discussion does not add the missing converse to final1.1 alignment.',
         'Section5.1 remains unresolved normatively; contextual equality stays an interpretation.'),
        ('D09', ['N08', 'O02', 'C02', 'C04'], 'Consistency reference question',
         'The note and OIM distinguish duplicate identity from value consistency, explaining the intended distinction.',
         'Neither changes final1.1 section5.4 wording referring to OIM duplicate facts; ambiguity unresolved.'),
        ('D10', ['N15', 'N16', 'N17'], 'Dependent processor claims',
         'The note describes optional complete de-duplication, old summation-item suppression and Formula combinations.',
         'These are attributed source claims; exact Inline/Formula dependencies were not independently inspected in this unit.'),
        ('D11', ['N18', 'N19', 'N20', 'N21'], 'Filing versus archival policy',
         'Storage, string variation and alternative numeric-only rejection are addressed as filing-system choices.',
         'No local rejection, normalization, deletion or accounting compliance policy selected.'),
        ('D12', ['N01', 'N02', 'N22', 'N23', 'N24'], 'Edition and status',
         'Header19April2018 and history17April2018 retained; AppendixE reports no incorporated errata and restricted internal lists.',
         'No latest-edition, global no-correction, normative status or observed access-denial conclusion.'),
    ]
    definitions = [{'id': ident, 'support': support, 'topic': topic, 'comparison': finding,
                    'disposition': limit} for ident, support, topic, finding, limit in rows]
    write('definition-comparison.json', {'rows': definitions})
    write('claim-support-ledger.json', {'claims': [
        {'id': 'K' + row['id'][1:], 'support': row['support'], 'claim': row['comparison'],
         'support_class': 'PRIMARY_TECHNICAL_SUPPORT_WITH_SCOPED_LOCAL_COMPARISON',
         'limit': row['disposition']} for row in definitions],
        'numerical_status': 'No new numerical campaign; note examples quoted, prior exact witness reused by reference only'})
    write('source-support-ledger.json', {
        'title': 'Handling Duplicate Facts in XBRL and Inline XBRL 1.0',
        'editor': 'Paul Warren', 'year': 2018, 'doi_arxiv': 'N/A official Working Group Note',
        'local': 'sources/01-note.body', 'url': 'https://www.xbrl.org/WGN/xbrl-duplicates/WGN-2018-04-19/xbrl-duplicates-WGN-2018-04-19.html',
        'classification': 'PRIMARY_OFFICIAL_TECHNICAL_GUIDANCE',
        'publication_status': 'Document19April2018; unrestricted circulation; may be superseded',
        'correction_status': 'AppendixD/E inspected; no errata incorporated in this edition; no separate history URL discovered',
        'retraction_quarantine': 'No such notice in retained note; global status not searched',
        'full_text': 'Complete1–7.4, AppendicesA–E, history table and actually viewed Figure1',
        'allowed': 'Scoped source definitions, examples and comparison with retained normative text',
        'forbidden': 'Authority transfer, latest-version inference, issuer-policy adoption or independent processor conformance'})
    write('citation-venue-ledger.json', {
        'source': 'Exact official2018 note', 'venue': 'XBRL International Working Group Note',
        'citation_count': 'not available', 'citation_source': 'not queried',
        'venue_metric': 'not available', 'access_date': '2026-10-23 Asia/Shanghai',
        'caveat': 'Bibliometric metadata is not evidence for technical correctness or authority'})
    structure = json.loads((U / 'sources/01-note.structure.json').read_text())
    dispositions = [
        ('dimensions-use', 'BACKGROUND', 'Exact2015 QName-aware context restriction dependency; not inspected here'),
        ('inlineXBRL-part0', 'SURVEY_OR_TUTORIAL', 'Exact2013 Primer is a new concrete lead; not acquired here'),
        ('inlineXBRL-part1', 'DIRECT_METHOD', 'Exact2013 processor specification is a new concrete lead; no independent confirmation here'),
        ('XBRL-2.1', 'FOUNDATIONAL', 'Corrected2013 baseline already retained; no reacquisition'),
    ]
    refs = []
    for token, classification, disposition in dispositions:
        urls = sorted({url for url in structure['links'] if token in url})
        assert urls, token
        refs.append({'urls': urls, 'classification': classification, 'disposition': disposition})
    write('backward-snowball-ledger.json', {'references': refs,
          'other_links': 'Self-version and legal navigation; no separate official status/history link discovered; no contact attempted'})
    write('forward-snowball-ledger.json', {
        'query_scope': 'Retained OIM6.2.1 and2019/2022 requirements references; no new external citation query',
        'source_date': '2026-10-23 Asia/Shanghai',
        'findings': ['OIM directly cites this exact note for numeric consistency',
                     '2019 requirements retain most-precise guidance; final1.1 section5.5 differs'],
        'limit': 'Not exhaustive forward coverage, latest-edition or no-correction evidence'})
    write('omission-risk-ledger.json', {'risks': [
        {'topic': 'Exact Inline specifications', 'status': 'inspect next under separate bounded plan',
         'objection': 'Note recommendations do not independently establish processor obligations'},
        {'topic': 'Formula processing', 'status': 'claim attributed only; specification not acquired here',
         'objection': 'Variable filtering and duplicate settings may affect the general statement'},
        {'topic': 'Dimension syntax recommendations', 'status': 'dependency not checked here',
         'objection': 'QName-aware comparison relies on restricted context content'},
        {'topic': 'Closed-interval assertion', 'status': 'source assertion only; derivation unexamined',
         'objection': 'Rounding grids and validity assumptions may matter'},
        {'topic': 'Later guidance/corrections', 'status': 'global edition search not performed',
         'objection': 'Exact linked historical note is not evidence that no later replacement exists'}]})
    print(json.dumps({'claims': len(rows), 'definition_comparisons': len(rows), 'research_ledgers': 6}))


if __name__ == '__main__':
    main()
