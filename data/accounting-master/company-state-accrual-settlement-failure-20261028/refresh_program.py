"""One-shot SIM-F036 disposition; retain original task and failure criteria."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
S=ROOT/'data/accounting-master/construction-continuation-20261028'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
def rel(p):return str(p.relative_to(ROOT))
v=json.loads((H/'attempt-01/verification.json').read_text());assert v['status']=='pass' and v['checks']==221
hashes=json.loads((H/'attempt-01/run-manifest.json').read_text())['source_hashes']
assert all(sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program)
f=S/'failure-dispositions.json';d=json.loads(f.read_text())
with (H/'navigation-before.json').open('x') as out:json.dump(dict(program=old,dispositions=d),out,indent=2)
originals={r['original_row']['id']:r['original_row'] for r in json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())['rows']}
assert len(d['rows'])==25 and not any(r['id']=='SIM-F036' for r in d['rows'])
d['rows'].append(dict(id='SIM-F036',original_row=originals['SIM-F036'],disposition='exact_original_scoped_accrual_carry_settlement_discriminator',comparison='Unchanged methods accrue5 without cash, preserve payable and retained loss on annual carry, then pay5 without new expense; two account maps and two explicit cash classifications agree. Balanced re-expensing mutation fails independent economic criterion.',evidence=[rel(H/'attempt-01/verification.json'),rel(H/'result.md')],next_action='Source/treatment admission and broader contracts remain open; payment-date2028 report is partial. Continue borrowing classification and remaining original failures.',original_status_unchanged=True,broad_package_closed=False))
d['rows'].sort(key=lambda r:r['id']);d['reviewed_rows']=len(d['rows'])
d['scope']='Twenty-six original rows individually reviewed;175 outside this continuation. Original criteria/statuses persist; scoped evidence is not whole-company closure.'
for r in d['rows']:assert r['original_row']==originals[r['id']]
dump(f,d)
lines=['# Current original failure dispositions','','28 October2026. Twenty-six original rows reviewed;175 outside this pass. All201 original rows/statuses persist. Coverage is not closure.','','| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines+=['| '+r['id']+' | '+r['comparison']+' | '+r['next_action']+' |' for r in d['rows']]
(S/'failure-dispositions.md').write_text(chr(10).join(lines)+chr(10))
for t in program['tasks']:
 if t['id']=='C04':
  t['evidence'].append(rel(H/'result.md'))
  t['next_action']='Twenty-six original failures reviewed;175 outside this pass. Audit borrowing-versus-revenue discrimination with unchanged declared financing methods; continue source/contract cases and ordered review from325.'
  t['remaining']=[x for x in t['remaining'] if not x.startswith('Twenty-five original rows')]
  t['remaining'].append('Twenty-six original rows have individual current comparisons;175 remain outside this continuation. Economic method admission requires independent event-specific expectations; generic balance/replay is insufficient.')
for a,b in zip(old['tasks'],program['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']:assert a[key]==b[key]
dump(p,program)
entry='''
## Accrual and following-period settlement — 28 October2026

SIM-F036 passes221 exact checks across14 native programs and one carry-tamper
case. Expense5 and payable5 arise in2027; annual carry preserves the payable,
and January1,2028 payment clears it without a second expense. Two account maps
and two explicit cash classifications agree. A balanced re-expensing mutation
is rejected by independent economic expectations. Result:
company-state-accrual-settlement-failure-20261028/result.md under data/accounting-master.

Twenty-six original rows reviewed;175 outside this pass. All original criteria,
statuses and frozen releases persist. Main reading324/831, resume325; S09 and
R04 remain in_progress, E3 deferred. Continue borrowing-classification failure,
source/construction work and ordered reading. No global continuation veto.

'''
for name in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/construction-continuation-20261028/checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/name;title,rest=p.read_text().split(chr(10),1);p.write_text(title+chr(10)+entry+rest)
for name,key in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/name;d=json.loads(p.read_text());d[key]['accrual_settlement_continuation_20261028']=dict(result=rel(H/'result.md'),checks=221,native_cases=14,carry_tamper_cases=1,reviewed_original_failures=26,outside_pass=175,scope='Separate native accrual/carry/settlement; no source admission or full2028 statements');dump(p,d)
print(json.dumps(dict(reviewed=26,outside_pass=175,source_hashes_verified=len(hashes),task_statuses_preserved=True)))

