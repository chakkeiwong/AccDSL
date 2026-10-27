"""Refresh active controls only after exact evidence, build and rendered review."""
from hashlib import sha256
from pathlib import Path
import json
import subprocess

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
REL = HERE.relative_to(ROOT).as_posix()
NEXT = 'docs/plans/accounting-declared-collection-state-growth-20261025.md'
PRIOR = 'data/accounting-master/declared-financing-schedules-coverage-20261025/inventory.json'
COVER = ROOT / 'data/accounting-master/declared-collection-clock-coverage-20261025'


def sha(path): return sha256(path.read_bytes()).hexdigest()
def digest(x): return sha256(json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
def dump(path, value): path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + chr(10))


def main():
    assert not (HERE / 'control-refresh.json').exists()
    checks = json.loads((HERE / 'checks.json').read_text()); assert checks['passed']
    build = json.loads((HERE / 'integration-verification.json').read_text()); assert build['passed']
    review = json.loads((HERE / 'render-review.json').read_text())
    assert review['author_review_complete'] and review['pdf_sha256'] == build['pdf_sha256']
    assert (HERE / 'result.md').exists() and (HERE / 'review.md').exists()
    for name, h in json.loads((HERE / 'source-lock.json').read_text()).items(): assert sha(ROOT / name) == h, name
    assert sha(ROOT / build['pdf']) == build['pdf_sha256']
    baseline = json.loads((ROOT / PRIOR).read_text())
    resolved = json.loads((ROOT / 'data/accounting-master/post-collection-mission-reassessment-20261025/resolved-inventory.json').read_text())
    advanced = {'MC02','MC05','MC11','MC13','MC15','MC17','MC24','MC25','MC26','MC28','MC32','MC34','MC35'}
    inventory = {'schema': 'accdsl.coverage.references.v1', 'date': '2026-10-25', 'candidate': '4.16',
        'readiness': 'not_ready', 'baseline': {'path': PRIOR, 'sha256': sha(ROOT / PRIOR)},
        'next_plan': NEXT, 'whole_rows_closed': 0,
        'scope': 'Finite declared collection and state-only dated assessment; fixed population; no source or accounting admission'}
    named = []
    for group, count in [('obligations', 53), ('interactions', 6), ('operations', 46)]:
        assert len(baseline[group]) == len({r['id'] for r in baseline[group]}) == count
        assert [r['id'] for r in baseline[group]] == [r['id'] for r in resolved[group]]
        inventory[group] = []
        for row in baseline[group]:
            changed = group == 'obligations' and row['id'] in advanced
            inventory[group].append({'id': row['id'], 'prior_ref': {'path': PRIOR, 'collection': group, 'id': row['id'], 'sha256': digest(row)},
                'assessment': 'scoped_advance_remaining_open' if changed else 'prior_scope_retained_not_reaudited',
                'advance': 'Named receivable receipts, explicit due-date assessments, preserved carry and exact prefix/text replay.' if changed else 'No new evidence assigned.',
                'residual': 'Dynamic claim creation, source-backed histories, whole-company and sector integration, independent/domain/human acceptance remain open.',
                'evidence': [REL + '/result.md', REL + '/checks.json'] if changed else [],
                'full_requirement_closed': False, 'acceptance': 'not_promoted'})
            named.append({'name': 'prior_record:' + group + ':' + row['id'], 'passed': True})
    COVER.mkdir(exist_ok=False)
    dump(COVER / 'inventory.json', inventory)
    bound = {PRIOR: sha(ROOT / PRIOR), build['pdf']: build['pdf_sha256']}
    for name in ['checks.json', 'comparison.json', 'source-lock.json', 'run-manifest.json', 'integration-verification.json',
                 'render-review.json', 'result.md', 'review.md']:
        bound[REL + '/' + name] = sha(HERE / name)
    for name, h in bound.items():
        named.append({'name': 'evidence:' + name, 'passed': sha(ROOT / name) == h})
    assert all(r['passed'] for r in named)
    dump(COVER / 'source-lock.json', bound)
    dump(COVER / 'checks.json', {'passed': True, 'coverage': [53, 6, 46], 'updated_obligations': len(advanced),
        'whole_rows_closed': 0, 'named_checks': named})
    (COVER / 'result.md').write_text('# Collection-clock coverage result' + chr(10)*2 +
        'All 53 obligations, 6 interactions and 46 operations retain exact predecessor records. '+
        'Thirteen obligations receive bounded evidence; none closes. Version 4.16 remains not_ready. '+
        'The broader audit selected typed claim creation as the next structural dependency. '+
        'Source histories, sector methods and full design acceptance remain open.' + chr(10))
    note = f'''## Collection clocks checked — 25 October 2026

Version 4.16: {build['pages']} pages, not_ready. PDF: {build['pdf']}.
SHA256: {build['pdf_sha256']}.
{checks['focused_tests']} focused tests, {checks['regression_tests']} regressions and {checks['comparison_checks']} named comparisons pass.
Two charts preserve due dates, state-only assessments, carry, stopped prefixes and matched text.
The assessment metadata-binding defect was repaired before final evidence recording.
All 174 predecessor sources remain protected; bounded rendered review passes.
All 53 obligations, 6 interactions and 46 operations remain; no whole requirement closes.
Result: {REL}/result.md. Next: {NEXT}.
S1–S5 partial; S6 held; S7 deferred. Forecasting remains deferred.

'''
    names = ['docs/plans/accounting-master-current.md', 'docs/plans/accounting-master-checkpoint.md',
        'docs/plans/accounting-master-program.md', 'docs/plans/accounting-mission-requirements.md',
        'docs/plans/accounting-product-design-checkpoint.md', 'data/accounting-master/next-plan.md',
        'data/accounting-master/simulator-session-20261023.md', 'data/accounting-master/next-plan.json',
        'scripts/accounting_master_catalog.json']
    before = {}
    for name in names:
        p = ROOT / name; before[name] = sha(p); backup = HERE / 'control-before' / name
        backup.parent.mkdir(parents=True, exist_ok=True); backup.write_bytes(p.read_bytes())
        if p.suffix == '.md':
            title, rest = p.read_text().split(chr(10), 1)
            if 'master-current' in name or 'simulator-session' in name:
                rest = '''Mission: represent disclosed company histories and alternatives, then execute explicit
economic events into coherent journals, statements and notes.

| Phase | Remaining work | Status |
|---|---|---|
| S1 Research | Consequential simulator sources, versions and inspected reuse evidence | Partial |
| S2 Architecture | Dynamic economic collections, source-history attachment, common sector interfaces | Partial |
| S3 Language/semantics | Credit-sale claim creation, broader measurements, full method authoring and fiscal policies | Partial |
| S4 Conformance | Whole-company/source-backed cases, integrated group/bank/insurance and recovery | Partial |
| S5 Governing design | Full manuscript and independent implementability/domain/human review | Partial |
| S6 Product implementation | Await sufficiently settled governing specification; prototypes are bounded design evidence | Held |
| S7 Predictive evaluation | Saved E3 choices retained; simulator design comes first | Deferred |

Immediate work: audit typed claim creation versus a separate receivable component,
then connect a credit sale to identified collection, assessment and carry.
Preserve frozen evidence and unrelated dirty work. No commit, background campaign,
paid outreach or forecast study. Current commands are tracked in the phase progress note.
'''
            p.write_text(title + chr(10)*2 + note + rest.lstrip(chr(10)))
    for name, key in [('data/accounting-master/next-plan.json', 'active_execution'),
                      ('scripts/accounting_master_catalog.json', 'active_execution_note')]:
        p = ROOT / name; data = json.loads(p.read_text()); retained = {k: v for k, v in data.items() if k != key}
        active = data[key]; active.update(updated='2026-10-25', active_work_plan=NEXT, latest_result=REL + '/result.md')
        if key == 'active_execution':
            active['current_candidate'] = {'version': '4.16', 'pages': build['pages'], 'status': 'not_ready', 'pdf': build['pdf'], 'sha256': build['pdf_sha256']}
            active['latest_results'].append(REL + '/result.md')
            active['completed_increments'].append(f"Declared collection clocks: {checks['focused_tests']} focused, {checks['regression_tests']} regressions, {checks['comparison_checks']} comparisons; Version 4.16")
            active['next'][0] = 'Audit typed economic identity creation, then connect credit sales to identified receivable collection and assessment'
        else: active['current_candidate'] = f"4.16;{build['pages']} pages;not_ready"
        dump(p, data); assert retained == {k: v for k, v in json.loads(p.read_text()).items() if k != key}
    dump(HERE / 'control-refresh.json', {'before': before, 'after': {n: sha(ROOT / n) for n in names}, 'legacy_json_fields_preserved': True})
    print(json.dumps({'candidate': '4.16', 'pages': build['pages'], 'controls': len(names), 'coverage': [53, 6, 46], 'next': NEXT}))


if __name__ == '__main__': main()
