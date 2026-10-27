"""Advance active controls after exact native-reference replay and review."""
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REL = HERE.relative_to(ROOT).as_posix()
NEXT = 'docs/plans/accounting-populated-source-contracts-20261025.md'
PRIOR = 'data/accounting-master/conditional-continuation-coverage-20261025/inventory.json'
COVER = ROOT / 'data/accounting-master/sector-reference-binding-coverage-20261025'

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
    previous = json.loads(ROOT / PRIOR).read_text() if False else json.loads((ROOT / PRIOR).read_text())
    advanced = {'MC06','MC07','MC19','MC20','MC21','MC22','MC24','MC26','MC27','MC28','MC30','MC32','MC34','MC35'}
    inventory = {'schema':'accdsl.coverage.references.v1','date':'2026-10-25','candidate':'4.20',
                 'readiness':'not_ready','baseline':{'path':PRIOR,'sha256':sha(ROOT / PRIOR)},
                 'next_plan':NEXT,'whole_rows_closed':0}
    for group, count in [('obligations',53),('interactions',6),('operations',46)]:
        assert len(previous[group]) == len({row['id'] for row in previous[group]}) == count
        inventory[group] = []
        for row in previous[group]:
            changed = group == 'obligations' and row['id'] in advanced
            inventory[group].append({'id':row['id'],'prior_ref':{'path':PRIOR,'collection':group,'id':row['id'],'sha256':digest(row)},
                'assessment':'scoped_advance_remaining_open' if changed else 'prior_scope_retained_not_reaudited',
                'advance':'Native bank/insurance references are bound to exact records, schemas, source blobs and views while preserving sector-specific state and unresolved obligations.' if changed else 'No new evidence assigned.',
                'residual':'Populated source contracts, actual source admission, account mapping, posting, complete sector methods and full design acceptance remain open.',
                'evidence':[REL+'/checks.json',REL+'/evidence.json',REL+'/result.md',REL+'/replay-observation.json'] if changed else [],
                'full_requirement_closed':False,'acceptance':'not_promoted'})
    COVER.mkdir(); dump(COVER/'inventory.json',inventory)
    bound={PRIOR:sha(ROOT/PRIOR),build['pdf']:build['pdf_sha256']}
    for name in ['checks.json','evidence.json','source-lock.json','run-manifest.json','replay-observation.json','integration-verification.json','render-review.json','result.md','review.md']:
        bound[REL+'/'+name]=sha(HERE/name)
    dump(COVER/'source-lock.json',bound)
    dump(COVER/'checks.json',{'passed':True,'coverage':[53,6,46],'updated_obligations':len(advanced),'whole_rows_closed':0,'bound_files':len(bound)})
    (COVER/'result.md').write_text('# Sector reference binding coverage\n\nAll 53 obligations, 6 interactions and 46 operations retain exact predecessor references. Fourteen obligations advance only within the checked native-reference scope. No whole requirement closes. Version 4.20 remains not_ready.\n')
    note=f'''## Sector reference binding checked — 25 October 2026

Version 4.20: {build['pages']} pages, not_ready. PDF: {build['pdf']}.
SHA256: {build['pdf_sha256']}.
10 focused tests, 13 company-world regressions and exact native replay pass.
The selected closures retain 34 bank records/21 blobs and 11 insurer records/6 blobs.
The bank state contains balances; the insurer state is an accounting head with a balances digest.
Both native assessment profiles declare no accounting effect. All 174 predecessor sources,
370 labels, 150 references and 740 citation occurrences remain protected; rendered pages
401–402 plus cover and adjacent pages 400 and 403 were inspected.
All 53 obligations, 6 interactions and 46 operations remain; no whole requirement closes.
Result: {REL}/result.md. Next: {NEXT}.
S1–S5 partial; S6 held; S7 deferred. Forecasting remains deferred.

'''
    phase='''Mission: represent disclosed company histories and alternatives, then simulate
explicit economic events into coherent journals, statements and notes.

| Phase | Remaining work | Status |
|---|---|---|
| S1 Research | Consequential source inspection and reuse evidence | Partial |
| S2 Architecture | Populated source contracts, group/bank/insurance composition and common interfaces | Partial |
| S3 Language | Revisions, claim identity, broader measurements, method authoring and fiscal policies | Partial |
| S4 Conformance | Source-backed whole-company cases, integrated group/bank/insurance and recovery | Partial |
| S5 Governing design | Full manuscript, independent implementability/domain/human review | Partial |
| S6 Product implementation | Await sufficiently settled governing specification | Held |
| S7 Predictive evaluation | Saved E3 choices retained; simulator design comes first | Deferred |

Current question: can repeated source-backed claims retain their own evidence,
revisions, settlement state and period results in one declared book?
Next action: execute docs/plans/accounting-populated-source-contracts-20261025.md.
The native sector reference boundary is checked; it performs no posting or consolidation.
Preserve frozen evidence and unrelated work. No background campaign or paid outreach.
'''
    names=['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md','data/accounting-master/next-plan.md','data/accounting-master/simulator-session-20261023.md','scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json']
    before={}
    for name in names:
        p=ROOT/name; before[name]=sha(p); backup=HERE/'control-before'/name; backup.parent.mkdir(parents=True,exist_ok=True); backup.write_bytes(p.read_bytes())
        if p.suffix=='.md':
            title,rest=p.read_text().split('\n',1)
            if name.endswith('accounting-master-current.md') or name.endswith('accounting-current-program-20261025.md') or name.endswith('simulator-session-20261023.md'):
                rest=phase
            p.write_text(title+'\n\n'+note+rest.lstrip('\n'))
    p=ROOT/'data/accounting-master/next-plan.json'; data=json.loads(p.read_text()); active=data['active_execution']; active.update(updated='2026-10-25',active_work_plan=NEXT,latest_result=REL+'/result.md')
    active['current_candidate']={'version':'4.20','pages':build['pages'],'status':'not_ready','pdf':build['pdf'],'sha256':build['pdf_sha256']}
    if REL+'/result.md' not in active['latest_results']: active['latest_results'].append(REL+'/result.md')
    active['completed_increments'].append('CompanyWorld/1 and sector reference binding: 10 focused, 13 regressions, 34/11 selected records; Version 4.20')
    active['next'][0]='Execute populated source contracts with revisions, claim identity and multi-period carry'
    dump(p,data)
    p=ROOT/'scripts/accounting_master_catalog.json'; catalog=json.loads(p.read_text()); note_obj=catalog['active_execution_note']; note_obj.update(updated='2026-10-25',latest_result=REL+'/result.md',active_work_plan=NEXT,current_candidate='4.20;515 pages;not_ready'); dump(p,catalog)
    dump(HERE/'control-refresh.json',{'before':before,'after':{name:sha(ROOT/name) for name in names},'legacy_json_fields_preserved':True})
    print(json.dumps({'candidate':'4.20','pages':build['pages'],'controls':len(names),'coverage':[53,6,46],'next':NEXT}))

if __name__=='__main__': main()
