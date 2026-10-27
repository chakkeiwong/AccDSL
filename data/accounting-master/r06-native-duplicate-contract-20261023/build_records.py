"""One-time audit records; retained sources and old checkers are read, never run."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import time
from projection import run

U = Path(__file__).resolve().parent
R = U.parents[2]
BASE = R / 'data/accounting-master'
DOC = R / 'docs/design/proposal'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(R))
bind = lambda p: {'path': rel(p), 'sha256': sha(p)}


def write(name, value):
    with (U / name).open('x') as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
        f.write('\n')


def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    names = ('comparison-ledger.json', 'examples-and-projection.json', 'recording-receipt.json')
    assert all(not (U / name).exists() for name in names)
    t0, started = time.monotonic(), datetime.now(timezone.utc).isoformat()
    # Reading spans combine the recovered session's actual reading and this
    # continuation. They are not a claim of a fresh full-document review.
    paths = {
        'evidence': ('architecture/evidence-contract-v3.md', [(1, 190)]),
        'extraction': ('architecture/extraction-contract-v1.md', None),
        'language': ('architecture/language-ir-contract-v1.md', [(1, 110)]),
        'interfaces': ('architecture/interfaces-contract-v1.md', [(95, 145)]),
        'translation': ('architecture/native-xbrl-translation-proposed-v1.md', None),
        'selected': ('architecture/native-selected-portable-proposed-v1.md', None),
        'full': ('architecture/native-full-portable-proposed-v1.md', None),
        'hazard': ('architecture/native-hazard-portable-proposed-v1.md', None),
        'offline': ('architecture/native-offline-resolution-proposed-v1.md', None),
        'loader': ('architecture/native-loader-source-delta-v1.md', None),
        'reuse': ('methods/software-reuse-methods-v1.md', None),
        'selection': ('methods/selected-reuse-20261015.md', None),
        'manuscript': ('manuscript-readability-20261022-theta/sections/selected-reuse.tex', None),
    }
    documents, anchors = {}, []
    for ident, (name, spans) in paths.items():
        p = DOC / name
        lines = p.read_text().splitlines()
        spans = spans or [(1, len(lines))]
        assert all(1 <= a <= b <= len(lines) for a, b in spans)
        documents[ident] = {**bind(p), 'lines': len(lines), 'read_spans': spans,
                           'reading_provenance': 'actual reading across recovered session and continuation; not independent review'}

    def anchor(ident, document, first, last):
        row = documents[document]
        assert any(a <= first <= last <= b for a, b in row['read_spans'])
        lines = (R / row['path']).read_text().splitlines()
        anchors.append({'id': ident, 'document': document, 'lines': [first, last],
                        'quote': '\n'.join(lines[first - 1:last])})

    for args in [
        ('D-occurrence', 'evidence', 21, 39), ('D-populations', 'evidence', 63, 75),
        ('D-alias', 'extraction', 63, 87), ('D-hash', 'language', 45, 55),
        ('D-array', 'language', 77, 100), ('D-prepare', 'interfaces', 101, 112),
        ('D-native', 'translation', 11, 40), ('D-sets', 'translation', 86, 100),
        ('D-candidates', 'translation', 126, 132), ('D-selected', 'selected', 48, 74),
        ('D-full', 'full', 9, 21), ('D-full-status', 'full', 42, 46),
        ('D-hazard', 'hazard', 16, 22), ('D-offline', 'offline', 23, 31),
        ('D-loader', 'loader', 10, 27), ('D-wording', 'reuse', 74, 86),
        ('D-no-formula', 'selection', 12, 19), ('D-selection-status', 'selection', 93, 100),
        ('D-manuscript', 'manuscript', 6, 18)]:
        anchor(*args)
    static_readings = []
    for name, spans in [
        ('native-xbrl-translation-20261018/common.py', [(21, 25), (95, 104)]),
        ('native-full-portable-20261018/check.py', [(1, 120), (139, 154)]),
        ('native-selected-portable-20261018/check.py', [(175, 200)])]:
        static_readings.append({**bind(BASE / name), 'read_spans': spans,
                                'execution_in_this_unit': False})
    reused = {}
    selected_anchors = {
        'guidance': ('r06-duplicates-guidance-20261023', ['N06', 'N07', 'N08', 'N10', 'N13', 'N18', 'N20', 'C01', 'C02', 'C03', 'O03']),
        'inline': ('r06-inline-duplicates-20261023', ['P2026-option', 'S2026-exist', 'S2026-id', 'S2026-other', 'S2026-relation', 'S2026-lang']),
        'formula': ('r06-formula-binding-20261023', ['V-single', 'V-sequence', 'V-identical', 'A-datasets', 'T-may', 'X20-identity'])}
    for ident, (name, ids) in selected_anchors.items():
        folder = BASE / name
        ledger = load(folder / 'source-ledger.json')
        found = [a for a in ledger['anchors'] if a['id'] in ids]
        assert len(found) == len(ids)
        reused[ident] = {'completion': bind(folder / 'completion.json'),
                        'source_ledger': bind(folder / 'source-ledger.json'),
                        'result': bind(folder / 'result.md'), 'anchors': found,
                        'research_ledgers': {s: bind(folder / (s + '-ledger.json')) for s in
                            ('source-support', 'citation-venue', 'backward-snowball',
                             'forward-snowball', 'claim-support', 'omission-risk')},
                        'fresh_acquisition_or_full_standard_reading': False}
    rows = [
        ('NC01', 'Occurrence identity', ['D-occurrence', 'D-native', 'D-full'], ['guidance:N18'],
         'supported preservation rule', 'Original bytes and every occurrence remain; aspects or equal text are not source identities.'),
        ('NC02', 'Content sharing', ['D-occurrence', 'D-populations', 'D-hash'], [],
         'supported preservation rule', 'A content body may be shared without collapsing occurrence locators or original source identity.'),
        ('NC03', 'Assertion aliases', ['D-alias', 'D-wording'], [],
         'confirmed wording ambiguity repaired additively', 'The R4 until clause is misleading if taken to allow occurrence deletion; E/extraction expressly preserve them after aliasing.'),
        ('NC04', 'Repeated actual facts', ['D-selected', 'D-full'], [],
         'bounded documentary evidence', 'Both selected and full records preserve f-207/f-256 and their own original-source joins; no actual loss was found.'),
        ('NC05', 'Ordered arrays and set fields', ['D-array', 'D-sets'], [],
         'supported preservation rule', 'Declared dependency sets do not authorize deduplication of occurrence lists or source spans.'),
        ('NC06', 'Inline output reduction', ['D-native', 'D-full'], ['inline:P2026-option', 'inline:S2026-exist', 'inline:S2026-id', 'inline:S2026-other', 'inline:S2026-relation', 'guidance:N07'],
         'future consumer obligation', 'Optional target reduction must satisfy every mapping obligation. First importer is native; no Inline reduction is selected.'),
        ('NC07', 'Numeric consistency', ['D-alias', 'D-full-status'], ['guidance:N08', 'guidance:N10', 'guidance:N20', 'guidance:C01', 'guidance:C02', 'guidance:C03', 'guidance:O03'],
         'future consumer obligation', 'Consistency/most-accurate/intersection differ. No universal duplicate key; Calc1.1 5.1/5.4 remain unresolved.'),
        ('NC08', 'Formula bindings', ['D-no-formula', 'D-manuscript'], ['formula:V-single', 'formula:V-sequence', 'formula:V-identical', 'formula:A-datasets', 'formula:T-may', 'formula:X20-identity'],
         'future consumer obligation', 'Disabled in selected importer; conditional 4/1/4 data sets do not imply required processor calls or preservation after deletion.'),
        ('NC09', 'Financial admission', ['D-candidates', 'D-prepare', 'D-selected', 'D-selection-status'], [],
         'supported preservation rule', 'Candidate construction, assertion alias, validation or content sharing supplies neither admission nor posting authority.'),
        ('NC10', 'Unknown semantics', ['D-hazard', 'D-full-status'], ['guidance:N13', 'inline:S2026-lang'],
         'future consumer obligation', 'Type, effective language and financial context remain unresolved; no inferred equivalence from source tokens.'),
        ('NC11', 'Original versus parser bytes', ['D-loader', 'D-offline'], [],
         'supported preservation rule', 'Parser-transformed data and actual opens remain separate; this projection cannot prove installed behavior.'),
        ('NC12', 'Manuscript disposition', ['D-manuscript', 'D-no-formula', 'D-wording'], [],
         'no confirmed manuscript defect', 'Current passage preserves equal-context differences and disables Formula; the older until ambiguity needs only an additive note.')]
    comparison = [{'id': ident, 'boundary': title, 'design_support': ds, 'source_support': ss,
                   'disposition': status, 'finding': finding} for ident, title, ds, ss, status, finding in rows]
    inputs = ['native-xbrl-translation-20261018/profile.json',
              'native-occurrence-bytes-20261018/readings.json',
              'native-selected-portable-20261018/portable-records.json',
              'native-full-portable-20261018/native-packet.json',
              'native-full-portable-20261018/portable-records.json',
              'taxonomy-reuse-20261007/archive/aapl-20240928_htm.xml',
              'r06-formula-binding-20261023/binding-example.json',
              'r06-calc11-conformance-source-20261022/exact-examples.json']
    projection = run()
    write('comparison-ledger.json', {'documents': documents, 'design_anchors': anchors,
          'static_authored_checker_readings': static_readings, 'reused_source_inquiries': reused,
          'inputs': [bind(BASE / p) for p in inputs], 'rows': comparison,
          'corrigendum': bind(DOC / 'architecture/native-duplicate-consumer-boundary-proposed-v1.md'),
          'independent_review': False, 'new_literature_survey': False})
    write('examples-and-projection.json', projection)
    write('recording-receipt.json', {'started_utc': started,
          'finished_utc': datetime.now(timezone.utc).isoformat(),
          'wall_seconds': time.monotonic() - t0, 'stage': 'audit records and scoped projection',
          'cpu_gpu': 'CPU only; GPU intentionally hidden; standard library only'})
    print(json.dumps({'comparison_rows': len(rows), 'design_anchors': len(anchors),
                      'projection_facts': 1127, 'examples': len(projection['examples']['cases']),
                      'negative_controls': len(projection['negative_controls'])}))


if __name__ == '__main__':
    main()
