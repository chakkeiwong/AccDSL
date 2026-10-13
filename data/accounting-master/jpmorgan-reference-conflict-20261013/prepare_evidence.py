"""Bind the real source evidence and cross-check the authored dependency example."""
import hashlib
import json
from pathlib import Path

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
if (UNIT / 'completion.json').exists():
    raise SystemExit('Completed unit; preserve evidence.')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(name, obj):
    (UNIT / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')

old = ROOT / 'data/accounting-master/accounting-package-semantic-annotation-20261011/annotations.json'
annotations = json.loads(old.read_text())
names = ['2023-financial-statement-reference', '2023-item8-range', '2023-wrong-target', '2023-actual-auditor']
quotes = [q for q in annotations['quotes'] if q['id'] in names]
checks = {}
checks['all_four_exact_anchors'] = len(quotes) == 4
for q in quotes:
    p = ROOT / q['source_text']
    text = ' '.join(p.read_text().split())
    checks[q['id'] + '_hash'] = sha(p) == q['source_text_sha256']
    checks[q['id'] + '_exact_slice'] = text[q['normalized_start']:q['normalized_end']] == q['quote']
baseline = json.loads((UNIT / 'baseline.json').read_text())
pages = json.loads((UNIT / 'source-pages.json').read_text())
checks['source_identity'] = sha(ROOT / baseline['source_pdf']) == baseline['source_pdf_sha256'] == pages['source_sha256']
observations = {
    38: 'Printed footer 36. Item8 names financial statements, notes and auditor report on pages 163–309.',
    42: 'Printed footer 40. Item15 explicitly says the set listed in Item8 commences on page156; 156 is visible in the source.',
    158: 'Printed footer156; heading Management’s discussion and analysis. Page is not the start of the auditor report.',
    165: 'Printed footer163; heading Report of Independent Registered Public Accounting Firm; PwC report begins here.'
}
for p in pages['pages']:
    checks['page_' + str(p['pdf_page']) + '_files'] = sha(ROOT / p['text']) == p['text_sha256'] and sha(ROOT / p['image']) == p['image_sha256']
    p['author_inspection'] = 'inspected in current continuation'
    p['observation'] = observations[p['pdf_page']]
save('source-pages.json', pages)
fixture = json.loads((UNIT / 'review-fixture.json').read_text())
heading = 'Report of Independent Registered Public Accounting Firm'
checks['bounded_search_before_false'] = heading not in (UNIT / 'source-pages/page-158.txt').read_text()
checks['bounded_search_after_true'] = heading in (UNIT / 'source-pages/page-165.txt').read_text()
checks['offset_does_not_resolve_disagreement'] = 158 - 156 == 165 - 163 == 2 and 156 != 163
dependencies = fixture['dependencies']
known = set(dependencies) | {x for refs in dependencies.values() for x in refs}
assert set(fixture['changed_inputs']) <= known
affected = set(fixture['changed_inputs'])
while True:
    expanded = affected | {node for node, refs in dependencies.items() if set(refs) & affected}
    if expanded == affected:
        break
    affected = expanded
stale = affected - set(fixture['changed_inputs'])
checks['dependency_closure_matches_expected'] = stale == set(fixture['expected_stale_for_new_view'])
checks['raw_and_independent_values_reusable'] = not (stale & set(fixture['expected_reusable_if_other_dependencies_unchanged']))
checks['negative_query_depends_on_candidate_set'] = 'candidate_page_set' in dependencies['bounded_negative_query']
checks['annotated_literal_has_review_dependency'] = 'conflict_disposition' in dependencies['annotated_literal_query']
checks['no_human_runtime_or_measurement_promotion'] = fixture['actual_human_adjudication'] == 'pending' and not fixture['runtime_workflow_executed'] and not fixture['financial_measurement_conflict'] and not fixture['full_e05_closed']
support = {'source_pdf': baseline['source_pdf'], 'source_sha256': baseline['source_pdf_sha256'],
           'prior_annotations': {'path': str(old.relative_to(ROOT)), 'sha256': sha(old)},
           'anchors': quotes, 'source_verdict': 'The printed Item15 start reference is wrong relative to its explicit Item8 target',
           'competing_explanations': {'extraction_error': 'rejected by current renders', 'printed_vs_physical_numbering': 'same +2 offset; does not reconcile the targets', 'different_version': 'both clauses in identical retained bytes', 'broader_mdna_target': 'Item15 explicitly identifies Item8 target', 'publisher_erratum': 'not checked; no erratum asserted', 'financial_measurement_conflict': 'not established'},
           'proposed_navigation': {'printed_page': 163, 'physical_page': 165},
           'review_class': 'author source inspection and authored expected-behaviour fixture'}
save('source-support.json', support)
save('source-checks.json', {'checks': checks, 'passed': sum(checks.values()), 'failed': [k for k, v in checks.items() if not v],
                            'computed_stale_nodes': sorted(stale), 'role': 'Source integrity and finite dependency cross-check; not production workflow execution'})
print(json.dumps({'passed': sum(checks.values()), 'failed': [k for k, v in checks.items() if not v]}))
if not all(checks.values()):
    raise SystemExit(1)
