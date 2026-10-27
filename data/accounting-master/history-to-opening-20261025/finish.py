"""Advance active controls after replay, additive build and actual rendered review."""
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]; REL = HERE.relative_to(ROOT).as_posix()
NEXT = 'docs/plans/accounting-conditional-continuation-20261025.md'
PRIOR = 'data/accounting-master/declared-receivable-lifecycle-coverage-20261025/inventory.json'
COVER = ROOT / 'data/accounting-master/conditional-opening-coverage-20261025'


def sha(path): return sha256(path.read_bytes()).hexdigest()
def digest(value): return sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
def dump(path, value): path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def main():
    assert not (HERE / 'control-refresh.json').exists() and not COVER.exists()
    checks = json.loads((HERE / 'checks.json').read_text())
    replay = json.loads((HERE / 'replay-observation.json').read_text())
    build = json.loads((HERE / 'integration-verification.json').read_text())
    review = json.loads((HERE / 'render-review.json').read_text())
    assert checks['passed'] and replay['passed'] and build['passed'] and review['author_review_complete']
    assert build['pdf_sha256'] == review['pdf_sha256'] == sha(ROOT / build['pdf'])
    for name, expected in json.loads((HERE / 'source-lock.json').read_text()).items(): assert sha(ROOT / name) == expected, name
    previous = json.loads((ROOT / PRIOR).read_text()); advanced = {'MC02','MC05','MC11','MC13','MC15','MC17','MC24','MC25','MC26','MC27','MC28','MC34','MC35'}
    inventory = {'schema': 'accdsl.coverage.references.v1', 'date': '2026-10-25', 'candidate': '4.18',
        'readiness': 'not_ready', 'baseline': {'path': PRIOR, 'sha256': sha(ROOT / PRIOR)},
        'next_plan': NEXT, 'whole_rows_closed': 0}
    for group, count in [('obligations', 53), ('interactions', 6), ('operations', 46)]:
        assert len(previous[group]) == len({r['id'] for r in previous[group]}) == count
        inventory[group] = []
        for row in previous[group]:
            changed = group == 'obligations' and row['id'] in advanced
            inventory[group].append({'id': row['id'], 'prior_ref': {'path': PRIOR, 'collection': group,
                'id': row['id'], 'sha256': digest(row)},
                'assessment': 'scoped_advance_remaining_open' if changed else 'prior_scope_retained_not_reaudited',
                'advance': 'Rechecked conditional history mapped to a complete provisional opening with preserved alternatives and obligations.' if changed else 'No new evidence assigned.',
                'residual': 'Conditional history-to-opening attachment, populated source contracts, measurement/sector integration and full design acceptance remain open.',
                'evidence': [REL + '/checks.json', REL + '/result.md', REL + '/replay-observation.json'] if changed else [],
                'full_requirement_closed': False, 'acceptance': 'not_promoted'})
    COVER.mkdir(); dump(COVER / 'inventory.json', inventory)
    bound = {PRIOR: sha(ROOT / PRIOR), build['pdf']: build['pdf_sha256']}
    for name in ['checks.json','source-lock.json','comparison.json','run-manifest.json','replay-observation.json',
                 'integration-verification.json','render-review.json','result.md','review.md']:
        bound[REL + '/' + name] = sha(HERE / name)
    dump(COVER / 'source-lock.json', bound)
    dump(COVER / 'checks.json', {'passed': True, 'coverage': [53,6,46], 'updated_obligations': len(advanced),
                               'whole_rows_closed': 0, 'bound_files': len(bound)})
    (COVER / 'result.md').write_text('# Conditional-opening coverage\n\nAll 53 obligations, 6 interactions and 46 operations retain exact predecessor references. Thirteen obligations advance within the checked conditional-opening scope. No whole requirement closes. Version 4.18 remains not_ready.\n')
    note = f'''## Conditional history opening checked — 25 October 2026

Version 4.18: {build['pages']} pages, not_ready. PDF: {build['pdf']}.
SHA256: {build['pdf_sha256']}.
11 focused tests, 74 regressions and 36 named comparisons pass; read-only replay agrees.
Two histories retain different memory at equal closing cash on two charts.
Context, dates, units and unresolved obligations remain explicit. All 174 predecessor sources
remain protected; rendered pages 389–391 and the cover were inspected.
All 53 obligations, 6 interactions and 46 operations remain; no whole requirement closes.
Result: {REL}/result.md. Next: {NEXT}.
S1–S5 partial; S6 held; S7 deferred. Forecasting remains deferred.

'''
    phase = '''Mission: represent disclosed company histories and alternatives, then simulate
explicit economic events into coherent journals, statements and notes.

| Phase | Remaining work | Status |
|---|---|---|
| S1 Research | Consequential source inspection and reuse evidence | Partial |
| S2 Architecture | Conditional financial continuation, populated contracts, common sector interfaces | Partial |
| S3 Language | Broader measurements, revised terms, complete method authoring and fiscal policies | Partial |
| S4 Conformance | Source-backed whole-company cases, integrated group/bank/insurance and recovery | Partial |
| S5 Governing design | Full manuscript, independent implementability/domain/human review | Partial |
| S6 Product implementation | Await sufficiently settled governing specification | Held |
| S7 Predictive evaluation | Saved E3 choices retained; simulator design comes first | Deferred |

Current question: preserve conditional history provenance through one explicit
financial continuation, retaining unresolved obligations and alternate histories.
Next action: audit and compose the rechecked opening with a declared method,
then compare exact journal, cash flow and report effects on both charts.
Preserve frozen evidence and unrelated work. No background campaign or paid outreach.
'''
    names = ['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md',
        'docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md',
        'docs/plans/accounting-product-design-checkpoint.md','data/accounting-master/next-plan.md',
        'data/accounting-master/simulator-session-20261023.md','data/accounting-master/next-plan.json',
        'scripts/accounting_master_catalog.json']
    before = {}
    for name in names:
        p = ROOT / name; before[name] = sha(p); backup = HERE / 'control-before' / name
        backup.parent.mkdir(parents=True, exist_ok=True); backup.write_bytes(p.read_bytes())
        if p.suffix == '.md':
            title, rest = p.read_text().split('\n', 1)
            if 'master-current' in name or 'simulator-session' in name: rest = phase
            p.write_text(title + '\n\n' + note + rest.lstrip('\n'))
    for name, key in [('data/accounting-master/next-plan.json','active_execution'),
                      ('scripts/accounting_master_catalog.json','active_execution_note')]:
        p = ROOT / name; data = json.loads(p.read_text()); retained = {k:v for k,v in data.items() if k != key}
        active = data[key]; active.update(updated='2026-10-25', active_work_plan=NEXT, latest_result=REL + '/result.md')
        if key == 'active_execution':
            active['current_candidate'] = {'version':'4.18','pages':build['pages'],'status':'not_ready','pdf':build['pdf'],'sha256':build['pdf_sha256']}
            active['latest_results'].append(REL + '/result.md')
            active['completed_increments'].append('Conditional opening: 11 focused, 74 regressions, 36 comparisons; Version 4.18')
            active['next'][0] = 'Compose a rechecked conditional opening with explicit financial methods while retaining evidence obligations'
        else: active['current_candidate'] = '4.18;514 pages;not_ready'
        dump(p, data); assert retained == {k:v for k,v in json.loads(p.read_text()).items() if k != key}
    dump(HERE / 'control-refresh.json', {'before': before, 'after': {name:sha(ROOT/name) for name in names}, 'legacy_json_fields_preserved': True})
    print(json.dumps({'candidate':'4.18','pages':build['pages'],'controls':len(names),'coverage':[53,6,46],'next':NEXT}))


if __name__ == '__main__': main()
