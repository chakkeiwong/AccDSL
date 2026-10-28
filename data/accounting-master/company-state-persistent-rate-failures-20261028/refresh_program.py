"""One-shot persistent-type/reset evidence and next-phase refresh."""
from copy import deepcopy
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;S=ROOT/'data/accounting-master/construction-continuation-20261028'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
def rel(p):return str(p.relative_to(ROOT))
assert json.loads((H/'attempt-01/verification.json').read_text())['status']=='pass'
hashes=json.loads((H/'attempt-01/run-manifest.json').read_text())['source_hashes']
assert all(sha256((ROOT/p).read_bytes()).hexdigest()==v for p,v in hashes.items())
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program)
f=S/'failure-dispositions.json';d=json.loads(f.read_text())
with (H/'navigation-before.json').open('x') as out:json.dump(dict(program=old,dispositions=d),out,indent=2)
by={r['original_row']['id']:r['original_row'] for r in json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())['rows']}
for ident,comparison,next_action in [
 ('SIM-F011','Existing rational solver retains exactly(5,5)/(7,7); mixed paths and total12 reject. Native annual carry and two coupon years preserve full state/reports; contract-specific guards refuse redrawn types.','General source/contract admission, amendments and actor-dependent reconstruction remain open; no prior is inferred.'),
 ('SIM-F018','Separate exact ACT/365 schedule and independent daily sums preserve reset timing and fixed/spread distinctions. Same shock ID twice refuses; different aliases can still duplicate economic meaning.','Native floating schedule, calendar and semantic shock-lineage admission remain open; do not equate schedule arithmetic with external/native adapter execution.')]:
 assert not any(r['id']==ident for r in d['rows'])
 d['rows'].append(dict(id=ident,original_row=by[ident],disposition='exact_original_scoped_persistence_or_timing_discriminator',comparison=comparison,evidence=[rel(H/'attempt-01/verification.json'),rel(H/'result.md')],next_action=next_action,original_status_unchanged=True,broad_package_closed=False))
d['rows'].sort(key=lambda r:r['id']);d['reviewed_rows']=len(d['rows']);assert len(d['rows'])==25
d['scope']='Twenty-five original rows individually reviewed;176 outside this continuation. Original criteria/statuses persist; scoped evidence is not whole-company closure.'
for r in d['rows']:assert r['original_row']==by[r['id']]
dump(f,d)
lines=['# Current original failure dispositions','','28 October2026. Twenty-five original rows reviewed;176 outside this pass. All201 original rows/statuses persist. Coverage is not closure.','','| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines+=['| '+r['id']+' | '+r['comparison']+' | '+r['next_action']+' |' for r in d['rows']];(S/'failure-dispositions.md').write_text(chr(10).join(lines)+chr(10))
for t in program['tasks']:
 if t['id']=='C04':
  t['evidence'].append(rel(H/'result.md'))
  t['next_action']='Twenty-five original failures reviewed;176 outside this pass. Continue exact causal, joint-stress and source-contract cases after connected S09 reuse reconciliation; retain separate native and schedule scope.'
  t['remaining']=[x for x in t['remaining'] if not x.startswith('Twenty-three original rows')]
  t['remaining'].append('Twenty-five original rows have individual current comparisons;176 remain outside this continuation. Semantic shock aliases and general contract/source admission remain open.')
 if t['id']=='S09':
  t['evidence'].append(rel(H/'result.md'))
  t['next_action']='Reconcile retained Arelle/ACTUS/QuantLib/Z3 and official-method audits against source, history, state and schedule needs. Reuse existing ACTUS fixture evidence; distinguish native typed execution from the separate SIM-F018 schedule diagnostic and semantic-shock admission gap.'
for a,b in zip(old['tasks'],program['tasks']):
 for k in ['id','status','depends_on','completion_criterion','requirements']:assert a[k]==b[k]
dump(p,program)
entry='''
## Persistent contract and reset failures — 28 October2026

SIM-F011/018 pass216 checks across13 solver cases,9 native programs and18
schedule/negative cases. Exact persistent paths(5,5)/(7,7) survive native
annual carry; mixed paths reject. Dated reset arithmetic distinguishes fixed
coupon, reference rate, spread and applicable days. Semantic shock aliases
remain a caller obligation. Result: company-state-persistent-rate-failures-20261028/result.md
under data/accounting-master. Native floating schedule admission is not claimed.

Twenty-five original rows reviewed;176 outside this pass. S09 next action
now connects retained software evidence to these limits. Main reading312/831,
resume313; all40 criteria/dependencies/statuses and frozen releases persist.
E3 deferred. Continue software/source synthesis and independent ready work.

'''
for n in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/construction-continuation-20261028/checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/n;title,rest=p.read_text().split(chr(10),1);p.write_text(title+chr(10)+entry+rest)
for n,k in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/n;d=json.loads(p.read_text());d[k]['persistent_rate_continuation_20261028']=dict(result=rel(H/'result.md'),checks=216,solver_cases=13,native_cases=9,schedule_cases=18,reviewed_original_failures=25,outside_pass=176,scope='Exact persistent loan and separate reset diagnostic; no general floating contract admission');dump(p,d)
print(json.dumps(dict(reviewed=25,outside_pass=176,source_hashes_verified=len(hashes),statuses_preserved=True)))

