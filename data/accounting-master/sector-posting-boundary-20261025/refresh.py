"""Advance active work from inspected sector boundaries to the exact adapter."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
NEXT='docs/plans/accounting-insurance-loss-book-20261025.md'
RESULT='data/accounting-master/sector-posting-boundary-20261025/result.md'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
assert not (HERE/'control-refresh.json').exists()
for name,expected in json.loads((HERE/'source-lock.json').read_text()).items():assert sha(ROOT/name)==expected,name
note=f'''## Sector posting boundary audited — 25 October2026

Two retained insurer loss schedules replay exactly, with six signed journals and
six loss-component origins each. The exact insurer adapter is the next ready
repair; interval-valued credit journals need a separate posting policy.
Version4.27 remains524 pages,not_ready; no new manuscript change in this audit.
Result: {RESULT}.
All53 obligations/6 interactions/46 operations remain; no whole requirement closes.
S1–S5 partial,S6 held,S7/E3 deferred. Next: {NEXT}.

'''
names=['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md',
 'docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md',
 'docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md',
 'data/accounting-master/next-plan.md','data/accounting-master/simulator-session-20261023.md',
 'data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
before={}
for name in names:
 p=ROOT/name;before[name]=sha(p);b=HERE/'control-before'/name;b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes(p.read_bytes())
 if p.suffix=='.md':
  title,rest=p.read_text().split('\n',1)
  if name.endswith(('accounting-master-current.md','accounting-current-program-20261025.md','simulator-session-20261023.md')):
   rest=rest[rest.index('Mission:'):];rest=rest[:rest.index('Current question:')]+f'Current question: can exact native insurer journals preserve host-book state and loss-component memory?\nNext action: execute {NEXT}.\nForecasting remains deferred. Preserve frozen evidence and unrelated work.\n'
  p.write_text(title+'\n\n'+note+rest.lstrip('\n'))
p=ROOT/'data/accounting-master/next-plan.json';d=json.loads(p.read_text());a=d['active_execution']
a.update(updated='2026-10-25',active_work_plan=NEXT,latest_result=RESULT)
if RESULT not in a['latest_results']:a['latest_results'].append(RESULT)
a['completed_increments'].append('Sector boundary audit selects exact insurer loss schedule after two native replays; credit interval posting stays open')
a['next'][0]='Bind exact retained insurer journals and loss-component origins to explicit declared books';dump(p,d)
p=ROOT/'scripts/accounting_master_catalog.json';d=json.loads(p.read_text())
d['active_execution_note'].update(updated='2026-10-25',latest_result=RESULT,active_work_plan=NEXT);dump(p,d)
dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names}})
for name in names:assert NEXT in (ROOT/name).read_text(),name
dump(HERE/'refresh-manifest.json',{'artifacts':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['refresh.py','control-refresh.json','run-manifest.json']}})
print(json.dumps({'controls':len(names),'next':NEXT}))
