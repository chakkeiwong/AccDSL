"""One-shot original borrowing-recognition evidence refresh."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
S=ROOT/'data/accounting-master/construction-continuation-20261028'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
def rel(p):return str(p.relative_to(ROOT))
v=json.loads((H/'attempt-01/verification.json').read_text());assert v['status']=='pass' and v['checks']==129
hashes=json.loads((H/'attempt-01/run-manifest.json').read_text())['source_hashes']
assert all(sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program)
f=S/'failure-dispositions.json';d=json.loads(f.read_text())
with (H/'navigation-before.json').open('x') as out:json.dump(dict(program=old,dispositions=d),out,indent=2)
originals={r['original_row']['id']:r['original_row'] for r in json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())['rows']}
assert len(d['rows'])==26 and not any(r['id']=='SIM-F035' for r in d['rows'])
d['rows'].append(dict(id='SIM-F035',original_row=originals['SIM-F035'],disposition='exact_original_scoped_borrowing_recognition_discriminator',comparison='Unchanged methods borrow100 and repay40 with zero profit, full liability/memory preservation and distinct financing receipt/payment origins. Balanced revenue-credit variants pass generic reconciliation but fail independent debt/profit expectations for two account maps.',evidence=[rel(H/'attempt-01/verification.json'),rel(H/'result.md')],next_action='Source-to-contract/recognition admission remains open; internal balance, replay and cash classification cannot establish economic meaning. Continue sourced construction and ordered review.',original_status_unchanged=True,broad_package_closed=False))
d['rows'].sort(key=lambda r:r['id']);d['reviewed_rows']=len(d['rows'])
d['scope']='Twenty-seven original rows individually reviewed;174 outside this continuation. Original criteria/statuses persist; scoped evidence is not whole-company closure.'
for r in d['rows']:assert r['original_row']==originals[r['id']]
dump(f,d)
lines=['# Current original failure dispositions','','28 October2026. Twenty-seven original rows reviewed;174 outside this pass. All201 original rows/statuses persist. Coverage is not closure.','','| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines+=['| '+r['id']+' | '+r['comparison']+' | '+r['next_action']+' |' for r in d['rows']]
(S/'failure-dispositions.md').write_text(chr(10).join(lines)+chr(10))
for t in program['tasks']:
 if t['id']=='C04':
  t['evidence'].append(rel(H/'result.md'))
  t['next_action']='Twenty-seven original failures reviewed;174 outside this pass. Carry economic-recognition limits into sourced T03/T08 construction, continue remaining original cases, and resume ordered review from325.'
  t['remaining']=[x for x in t['remaining'] if not x.startswith('Twenty-six original rows')]
  t['remaining'].append('Twenty-seven original rows have individual current comparisons;174 remain outside this continuation. Real source/contract/recognition and arbitrary method completeness remain open.')
for a,b in zip(old['tasks'],program['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']:assert a[key]==b[key]
dump(p,program)
entry='''
## Borrowing recognition discrimination — 28 October2026

SIM-F035 passes129 exact checks across11 native programs. Borrowing100 and
repayment40 preserve zero profit, debt60 and separate financing cash origins.
Balanced revenue-credit mutations remain economically wrong despite valid
replay, consistent debt memory and reconciled statements. Result:
company-state-borrowing-recognition-failure-20261028/result.md under data/accounting-master.

Twenty-seven original rows reviewed;174 outside this pass. All original task
criteria/statuses and frozen releases persist. Main reading324/831, resume325;
S09/R04 in_progress, E3 deferred. Continue sourced construction, remaining
failure cases and ordered reading. No global continuation veto.

'''
for name in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/construction-continuation-20261028/checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/name;title,rest=p.read_text().split(chr(10),1);p.write_text(title+chr(10)+entry+rest)
for name,key in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/name;d=json.loads(p.read_text());d[key]['borrowing_recognition_continuation_20261028']=dict(result=rel(H/'result.md'),checks=129,native_cases=11,reviewed_original_failures=27,outside_pass=174,scope='Native borrowing and repayment with independent economic controls; no source/treatment admission');dump(p,d)
print(json.dumps(dict(reviewed=27,outside_pass=174,source_hashes_verified=len(hashes),task_statuses_preserved=True)))

