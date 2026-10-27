"""Refresh active controls once, preserving the prior bytes and release."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
NEXT='docs/plans/accounting-gentry-excluded-leaves-20261025.md'
RESULT=str((HERE/'result.md').relative_to(ROOT))
NOTE='''## Post-fiscal dependencies reassessed — 25 October 2026

Version 4.39 remains 534 pages, not_ready; its PDF hash is verified.
All 53 obligations, six interactions and 46 operations retain their original
records through 43 verified coverage files. Completed source/history, population, sector, fiscal and recovery compositions are retained.
Next: inspect four excluded Gentry scan leaves using the retained archive identity;
actual transactions, legal accounts and full-source compatibility stay unknown.
Result: data/accounting-master/post-fiscal-reassessment-20261025/result.md.
S1-S5 partial; S6 held; S7/E3 deferred. No whole requirement closes.
Next plan: docs/plans/accounting-gentry-excluded-leaves-20261025.md.

'''
NAMES=['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md',
       'docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md',
       'docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md',
       'data/accounting-master/next-plan.md','data/accounting-master/simulator-session-20261023.md',
       'data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
def sha(path): return sha256(path.read_bytes()).hexdigest()
def dump(path,value): path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def main():
    assert (HERE/'continuity.json').exists() and (ROOT/NEXT).exists()
    assert not (HERE/'control-refresh.json').exists()
    before={}
    for name in NAMES:
        p=ROOT/name; before[name]=sha(p); q=HERE/'control-before'/name
        q.parent.mkdir(parents=True,exist_ok=True); q.write_bytes(p.read_bytes())
        if p.suffix=='.md':
            title,rest=p.read_text().split('\n',1)
            if name.endswith(('accounting-master-current.md','accounting-current-program-20261025.md','simulator-session-20261023.md')):
                rest=rest[rest.index('Mission:'):]
                rest=rest[:rest.index('Current question:')]+'Current question: do excluded source-scan leaves contain the missing Gentry derivation?\nNext action: execute '+NEXT+'.\nPreserve frozen evidence and unrelated work. Forecasting remains deferred.\n'
            p.write_text(title+'\n\n'+NOTE+rest.lstrip('\n'))
    p=ROOT/'data/accounting-master/next-plan.json'; d=json.loads(p.read_text()); a=d['active_execution']
    a.update(updated='2026-10-25',active_work_plan=NEXT,latest_result=RESULT)
    a['latest_results'].append(RESULT)
    a['completed_increments'].append('Post-fiscal reassessment:53/6/46 IDs through43 coverage files; excluded-source scan selected')
    a['next'][0]='Inspect the four excluded Gentry scan leaves before current-design reconciliation'; dump(p,d)
    p=ROOT/'scripts/accounting_master_catalog.json'; d=json.loads(p.read_text())
    d['active_execution_note'].update(updated='2026-10-25',latest_result=RESULT,active_work_plan=NEXT); dump(p,d)
    for name in NAMES: assert NEXT in (ROOT/name).read_text(),name
    dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in NAMES}})
    print(json.dumps({'controls_refreshed':len(NAMES),'next':NEXT}))
if __name__=='__main__': main()
