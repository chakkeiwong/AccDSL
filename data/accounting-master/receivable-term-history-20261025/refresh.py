"""Advance active controls without changing frozen release evidence."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
NEXT='docs/plans/accounting-term-history-integration-20261025.md'
RESULT='data/accounting-master/receivable-term-history-20261025/result.md'
NOTE='## Prospective receivable term history checked — 25 October 2026\n\n14 focused tests/38 regressions and two complete nine-event/carry cases replay\nagainst61 locked files. Earlier overdue20 retains its old terms; extensions,\nnew assessments, receipts and carry preserve both old and current meanings.\nNo real contract-modification or complete term-history admission follows.\nVersion4.23 remains519 pages,not_ready; term history awaits manuscript integration.\nPDF: docs/design/proposal/manuscript-group-period-20261025/accounting-product-proposal.pdf\nSHA256: deba809ec568e5686fe04d2fdc7598bd8f9f6270d0d31fd94dd2d1f1c2ca25e2.\nResult: data/accounting-master/receivable-term-history-20261025/result.md.\nAll53 obligations/6 interactions/46 operations remain; no whole requirement closes.\nS1–S5 partial; S6 held; S7 deferred. Forecasting remains deferred.\nNext: docs/plans/accounting-term-history-integration-20261025.md.\n\n'
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
                rest=rest[:rest.index('Current question:')]+'Current question: how should prospective terms and historical assessment bases enter the governing design?\nNext action: execute '+NEXT+'.\nForecasting remains deferred. Preserve frozen evidence and unrelated work.\n'
            p.write_text(title+'\n\n'+NOTE+rest.lstrip('\n'))
    p=ROOT/'data/accounting-master/next-plan.json';d=json.loads(p.read_text());a=d['active_execution']
    a.update(updated='2026-10-25',active_work_plan=NEXT,latest_result=RESULT)
    if RESULT not in a['latest_results']:a['latest_results'].append(RESULT)
    a['completed_increments'].append('Prospective term history:14 focused/38 regression tests; two charts, repeated extensions, receipts and carry checked')
    a['next'][0]='Integrate prospective term versions and assessment basis into an additive manuscript successor';dump(p,d)
    p=ROOT/'scripts/accounting_master_catalog.json';d=json.loads(p.read_text())
    d['active_execution_note'].update(updated='2026-10-25',latest_result=RESULT,active_work_plan=NEXT);dump(p,d)
    dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names}})
    for name in names:assert NEXT in (ROOT/name).read_text(),name
    print(json.dumps({'controls_refreshed':len(names),'next':NEXT}))
if __name__=='__main__':run()
