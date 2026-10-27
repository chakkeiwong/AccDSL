"""Advance only active master annotations after recorded read-only replay."""
from hashlib import sha256
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
REL=HERE.relative_to(ROOT).as_posix()
NEXT='docs/plans/accounting-retained-receivable-boundary-20261025.md'
PRIOR='data/accounting-master/sector-reference-binding-coverage-20261025/inventory.json'

def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+chr(10))

def main():
    if (HERE/'control-refresh.json').exists():raise SystemExit('Already refreshed')
    checks=json.loads(Path('/tmp/accdsl-source-contract-record.log').read_text())
    replay=json.loads(Path('/tmp/accdsl-source-contract-replay.log').read_text())
    assert checks['passed'] and replay['passed'] and checks['cases']==replay['cases']==4
    for name,h in json.loads((HERE/'source-lock.json').read_text()).items():assert sha(ROOT/name)==h,name
    dump(HERE/'checks.json',checks);dump(HERE/'replay-observation.json',replay)
    previous=json.loads((ROOT/PRIOR).read_text())
    advanced={'MC02','MC04','MC05','MC08','MC11','MC13','MC16','MC24','MC25','MC26','MC27','MC28','MC34','MC35'}
    inventory={'schema':'accdsl.coverage.references.v1','date':'2026-10-25','candidate':'4.20',
        'readiness':'not_ready','baseline':{'path':PRIOR,'sha256':sha(ROOT/PRIOR)},
        'next_plan':NEXT,'whole_rows_closed':0,'manuscript_integration':'pending'}
    for group,count in [('obligations',53),('interactions',6),('operations',46)]:
        assert len(previous[group])==len({r['id'] for r in previous[group]})==count
        inventory[group]=[]
        for row in previous[group]:
            changed=group=='obligations' and row['id'] in advanced
            inventory[group].append({'id':row['id'],'prior_ref':{'path':PRIOR,'collection':group,'id':row['id'],
                'sha256':sha256(json.dumps(row,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()},
                'assessment':'scoped_advance_remaining_open' if changed else 'prior_scope_retained_not_reaudited',
                'advance':'Constructed source spans, assertion revisions and multi-period claim histories checked.' if changed else 'No new evidence assigned.',
                'evidence':[REL+'/result.md',REL+'/evidence.json',REL+'/replay-observation.json'] if changed else [],
                'residual':'Actual source admission, populated opening contracts, complete methods and design acceptance remain open.',
                'full_requirement_closed':False,'acceptance':'not_promoted'})
    dump(HERE/'coverage.json',inventory)
    note='''## Constructed receivable sources checked — 25 October 2026

20 focused tests, 85 regressions, four cases and read-only replay pass against
91 locked files. Exact source spans, two claim identities, corrections, receipts,
period carry and full signed balances agree on both charts. Sources are explicitly
constructed; actual source, historical execution and temporal admission remain false.
Version 4.20 remains 515 pages and not_ready; this checked increment is not yet
integrated into a manuscript successor. All 53 obligations, 6 interactions and
46 operations remain, with zero whole requirements closed.
Result: data/accounting-master/populated-source-contracts-20261025/result.md.
Next: docs/plans/accounting-retained-receivable-boundary-20261025.md.
S1–S5 partial; S6 held; S7 deferred. Forecasting remains deferred.

'''
    phase='''Mission: represent disclosed company histories and alternatives, then simulate
explicit economic events into coherent journals, statements and notes.

| Phase | Remaining work | Status |
|---|---|---|
| S1 Research | Consequential source inspection and reuse evidence | Partial |
| S2 Architecture | Actual source contracts, partial claim populations and sector composition | Partial |
| S3 Language | Revisions, broader measurements, method authoring and fiscal policies | Partial |
| S4 Conformance | Real-source whole-company cases, integrated sector methods and recovery | Partial |
| S5 Governing design | Integrate checked additions; complete implementability, domain and human review | Partial |
| S6 Product implementation | Await sufficiently settled governing specification | Held |
| S7 Predictive evaluation | Saved E3 choices retained; simulator design comes first | Deferred |

Current question: which identified-claim requirements can the retained real
disclosures support, and which must remain unresolved?
Next action: execute docs/plans/accounting-retained-receivable-boundary-20261025.md.
Governing PDF: docs/design/proposal/manuscript-sector-reference-binding-20261025/accounting-product-proposal.pdf.
SHA256: 38c0f38be6da9872d76edd6f9044a07b150eb0d66f002d52fe4da0248a195b73.
Preserve frozen evidence and unrelated work. No background campaign or paid outreach.
'''
    names=['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md',
        'docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md',
        'docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md',
        'data/accounting-master/next-plan.md','data/accounting-master/simulator-session-20261023.md',
        'data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
    before={}
    for name in names:
        p=ROOT/name;before[name]=sha(p);backup=HERE/'control-before'/name
        backup.parent.mkdir(parents=True,exist_ok=True);backup.write_bytes(p.read_bytes())
        if p.suffix=='.md':
            title,rest=p.read_text().split(chr(10),1)
            if name.endswith(('accounting-master-current.md','accounting-current-program-20261025.md','simulator-session-20261023.md')):rest=phase
            p.write_text(title+chr(10)*2+note+rest.lstrip(chr(10)))
    p=ROOT/'data/accounting-master/next-plan.json';data=json.loads(p.read_text());a=data['active_execution']
    a.update(updated='2026-10-25',active_work_plan=NEXT,latest_result=REL+'/result.md')
    a['latest_results'].append(REL+'/result.md')
    a['completed_increments'].append('Constructed receivable sources: 20 focused tests, 85 regressions, four cases and read-only replay; real-source admission stays open')
    a['next'][0]='Compare retained actual receivable disclosures with exact claim-level source and execution requirements'
    dump(p,data)
    p=ROOT/'scripts/accounting_master_catalog.json';data=json.loads(p.read_text())
    data['active_execution_note'].update(updated='2026-10-25',active_work_plan=NEXT,latest_result=REL+'/result.md')
    dump(p,data)
    dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names},'legacy_json_fields_preserved':True})
    print(json.dumps({'passed':True,'controls':len(names),'coverage':[53,6,46],'whole_rows_closed':0,'next':NEXT}))

if __name__=='__main__':main()
