"""Advance active controls without changing frozen release evidence."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
NEXT='docs/plans/accounting-declared-indirect-cash-20261025.md'
RESULT='data/accounting-master/simulator-gap-reassessment-20261025/result.md'
NOTE='## Simulator gaps reassessed — 25 October 2026\n\nAll 53 obligations, 6 interactions and 46 operations resolve through 28 verified\ncoverage files. Current code inspection identifies the explicit indirect cash-flow\nexplanation as the next ready reporting dependency. Actual source populations,\ngroup/sector methods, research gaps and full design review remain open.\nVersion 4.25: 521 pages, not_ready.\nPDF: docs/design/proposal/manuscript-term-authoring-20261025/accounting-product-proposal.pdf\nSHA256: d35590f4ea484616340fbcaf30eca1b69807f443d3a82f0f75b365819f955f8e.\nResult: data/accounting-master/simulator-gap-reassessment-20261025/result.md.\nS1–S5 partial; S6 held; S7/E3 deferred. No whole requirement closes.\nNext: docs/plans/accounting-declared-indirect-cash-20261025.md.\n\n'
def dump(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def sha(path):return sha256(path.read_bytes()).hexdigest()
def run():
    names=['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md',
           'docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md',
           'docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md',
           'data/accounting-master/next-plan.md','data/accounting-master/simulator-session-20261023.md',
           'data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
    assert not (HERE/'control-refresh.json').exists(),'refresh already recorded'
    before={}
    for name in names:
        p=ROOT/name;before[name]=sha(p);saved=HERE/'control-before'/name
        saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(p.read_bytes())
        if p.suffix=='.md':
            title,rest=p.read_text().split('\n',1)
            if name.endswith(('accounting-master-current.md','accounting-current-program-20261025.md','simulator-session-20261023.md')):
                rest=rest[rest.index('Mission:'):]
                rest=rest.replace('Native group binding, broader sector composition and actual claim state','Compatible book composition, broader sector methods and actual claim state')
                rest=rest[:rest.index('Current question:')]+'Current question: how can explicit journal classifications explain operating cash without a residual plug?\nNext action: execute '+NEXT+'.\nForecasting remains deferred. Preserve frozen evidence and unrelated work.\n'
            p.write_text(title+'\n\n'+NOTE+rest.lstrip('\n'))
    p=ROOT/'data/accounting-master/next-plan.json';d=json.loads(p.read_text());a=d['active_execution']
    a.update(updated='2026-10-25',active_work_plan=NEXT,latest_result=RESULT)
    if RESULT not in a['latest_results']:a['latest_results'].append(RESULT)
    a['completed_increments'].append('Broader gap reassessment preserves all53/6/46 IDs and selects explicit trace-bound indirect reporting')
    a['next'][0]='Implement explicit indirect cash-flow explanation with gross postings and per-event checks';dump(p,d)
    p=ROOT/'scripts/accounting_master_catalog.json';d=json.loads(p.read_text())
    d['active_execution_note'].update(updated='2026-10-25',latest_result=RESULT,active_work_plan=NEXT);dump(p,d)
    dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names}})
    for name in names:assert NEXT in (ROOT/name).read_text(),name
    print(json.dumps({'controls_refreshed':len(names),'next':NEXT}))
if __name__=='__main__':run()
