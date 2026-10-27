from hashlib import sha256
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
REL=HERE.relative_to(ROOT).as_posix();NEXT='docs/plans/accounting-partial-claim-populations-20261025.md'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+chr(10))

def main():
    assert not (HERE/'control-refresh.json').exists()
    for kind in ['record','replay']:
        d=json.loads(Path('/tmp/accdsl-retained-receivable-'+kind+'.log').read_text());assert d['passed']
        dump(HERE/('checks.json' if kind=='record' else 'replay-observation.json'),d)
    for name,h in json.loads((HERE/'source-lock.json').read_text()).items():assert sha(ROOT/name)==h,name
    note='''## Retained receivable boundary checked — 25 October 2026

Seven tests and exact replay pass: three source views, 12 combined observations,
two inspected receivable notes, 18 input requirements and 185 locked files.
Actual claim IDs, due dates, gross consideration and legal allocation remain
unresolved. Vendor non-trade receivables require a different accounting method
from the declared credit-sale lifecycle. The partial source representation is
useful; it returns no executable claims and makes no impossibility claim.
The preceding constructed-source reference passed 20 focused/85 regression tests.
Version 4.20 remains 515 pages and not_ready; these additions await integration.
All 53 obligations, 6 interactions and 46 operations remain; no whole requirement closes.
Result: data/accounting-master/retained-receivable-boundary-20261025/result.md.
Next: docs/plans/accounting-partial-claim-populations-20261025.md.
S1–S5 partial; S6 held; S7 deferred. Forecasting remains deferred.

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
            if name.endswith(('accounting-master-current.md','accounting-current-program-20261025.md','simulator-session-20261023.md')):
                rest=rest[rest.index('Mission:'):]
                rest=rest.replace('Current question: which identified-claim requirements can the retained real\ndisclosures support, and which must remain unresolved?',
                    'Current question: how can unidentified claim populations retain aggregate\nsource measurements without being mistaken for empty executable collections?')
                rest=rest.replace('docs/plans/accounting-retained-receivable-boundary-20261025.md',NEXT)
            p.write_text(title+chr(10)*2+note+rest.lstrip(chr(10)))
    p=ROOT/'data/accounting-master/next-plan.json';d=json.loads(p.read_text());a=d['active_execution']
    a.update(active_work_plan=NEXT,latest_result=REL+'/result.md')
    a['latest_results'].append(REL+'/result.md')
    a['completed_increments'].append('Retained receivable boundary: three views, 12 observations, 18 explicit requirements; vendor method mismatch and unknown claim state preserved')
    a['next'][0]='Reuse partial-state and collection semantics to distinguish unidentified claim populations from known empty ones'
    dump(p,d)
    p=ROOT/'scripts/accounting_master_catalog.json';d=json.loads(p.read_text())
    d['active_execution_note'].update(active_work_plan=NEXT,latest_result=REL+'/result.md');dump(p,d)
    dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names},'whole_rows_closed':0,'legacy_json_fields_preserved':True})
    print(json.dumps({'passed':True,'controls':len(names),'next':NEXT}))

if __name__=='__main__':main()
