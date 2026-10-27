"""Advance active controls without changing frozen release evidence."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
NEXT='docs/plans/accounting-compatible-book-composition-20261025.md'
RESULT='data/accounting-master/native-group-binding-20261025/result.md'
NOTE='''## Native group reference binding checked — 25 October2026

11 focused tests/23 regressions and exact replay pass against116 locked files.
Initial closure:5 records/5 blobs; final:109 records/5 blobs. The native681-check
result and14 inputs are preserved, not rerun. Typed member selectors retain
the full shared group state; no independent book or posting admission follows.
Version4.21 remains517 pages,not_ready; the new reference evidence is not yet
integrated into that frozen manuscript. S1–S5 partial; S6 held; S7 deferred.
All53 obligations/6 interactions/46 operations remain; no whole requirement closes.
Result: data/accounting-master/native-group-binding-20261025/result.md.
Next: docs/plans/accounting-compatible-book-composition-20261025.md.

'''
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
                rest=rest[:rest.index('Current question:')]+'Current question: can separately valid synthetic books compose through explicit paired eliminations?\nNext action: execute '+NEXT+'.\nForecasting remains deferred. Preserve frozen evidence and unrelated work.\n'
            p.write_text(title+'\n\n'+NOTE+rest.lstrip('\n'))
    p=ROOT/'data/accounting-master/next-plan.json';d=json.loads(p.read_text());a=d['active_execution']
    a.update(updated='2026-10-25',active_work_plan=NEXT,latest_result=RESULT)
    if RESULT not in a['latest_results']:a['latest_results'].append(RESULT)
    a['completed_increments'].append('Native group selectors:11 focused/23 regression tests; exact initial/final replay; shared state preserved')
    a['next'][0]='Compose separately valid synthetic books with explicit common-chart maps and paired elimination entries';dump(p,d)
    p=ROOT/'scripts/accounting_master_catalog.json';d=json.loads(p.read_text())
    d['active_execution_note'].update(updated='2026-10-25',latest_result=RESULT,active_work_plan=NEXT);dump(p,d)
    dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names}})
    for name in names:assert NEXT in (ROOT/name).read_text(),name
    print(json.dumps({'controls_refreshed':len(names),'next':NEXT}))
if __name__=='__main__':run()
