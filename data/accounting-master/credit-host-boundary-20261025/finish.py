"""Accept the exact host-boundary diagnostic and advance current controls."""
from pathlib import Path
from hashlib import sha256
import json
import shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];REL=HERE.relative_to(ROOT).as_posix()
NEXT='docs/plans/accounting-credit-linked-book-20261025.md'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
assert not (HERE/'acceptance-manifest.json').exists()
locks=json.loads((HERE/'source-lock.json').read_text());assert len(locks)==340
for n,h in locks.items():assert sha(ROOT/n)==h,n
for n,h in json.loads((HERE/'run-manifest.json').read_text())['artifacts'].items():assert sha(ROOT/n)==h,n
for mode in ['record','replay']:
    p=Path('/tmp/accdsl-credit-host-'+mode+'.log');o=json.loads(p.read_text().strip().splitlines()[-1])
    assert o['passed'] and o['cases']==9 and o['locked_files']==340
    shutil.copyfile(p,HERE/(mode+'.log'))
dump(HERE/'replay-observation.json',o)
note=f'''## Exact credit host boundary checked — 25 October 2026

Nine schedules replay. Of929 monetary occurrences,169 lack certified rational
projections. The unchanged host rejects expression balances with text:rational;
three fully rational cases remain representable. No type default is changed.
Result: {REL}/result.md. Next: {NEXT}.
Version4.31 remains528 pages,not_ready; the manuscript is unchanged.
All53 obligations,6 interactions,46 operations remain. No whole row closes.
S1-S5 partial,S6 held,S7/E3 deferred.

'''
names=['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md',
 'docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md',
 'docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md',
 'data/accounting-master/next-plan.md','data/accounting-master/simulator-session-20261023.md',
 'data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
before={}
for n in names:
    p=ROOT/n;before[n]=sha(p);saved=HERE/'control-before'/n
    saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(p.read_bytes())
    if p.suffix=='.md':
        title,rest=p.read_text().split('\n',1)
        if n.endswith(('accounting-master-current.md','accounting-current-program-20261025.md','simulator-session-20261023.md')):
            rest='Mission:'+rest.split('Mission:',1)[1]
            rest=rest.replace('docs/plans/accounting-credit-host-boundary-20261025.md',NEXT)
        p.write_text(title+'\n\n'+note+rest.lstrip('\n'))
p=ROOT/'data/accounting-master/next-plan.json';d=json.loads(p.read_text());a=d['active_execution']
a.update(updated='2026-10-25',active_work_plan=NEXT,latest_result=REL+'/result.md')
a['latest_results'].append(REL+'/result.md')
a['completed_increments'].append('Exact credit host type boundary checked across nine complete schedules')
a['next'][0]='Implement optional single-root credit journal projection and cumulative balance/profit reports'
dump(p,d)
p=ROOT/'scripts/accounting_master_catalog.json';d=json.loads(p.read_text())
d['active_execution_note'].update(updated='2026-10-25',active_work_plan=NEXT,latest_result=REL+'/result.md');dump(p,d)
for n in names:assert NEXT in (ROOT/n).read_text(),n
dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names}})
files=['audit.md','verify.py','evidence.json','source-lock.json','run-manifest.json','result.md',
 'record.log','replay.log','replay-observation.json','control-refresh.json','finish.py']
dump(HERE/'acceptance-manifest.json',{'status':'accepted_type_boundary_only','next_plan':NEXT,
 'artifacts':{REL+'/'+n:sha(HERE/n) for n in files}})
print(json.dumps({'accepted':True,'controls':len(names),'next':NEXT}))
