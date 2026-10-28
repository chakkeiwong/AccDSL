"""Record original conversion/priority/preference cases, preserving program."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
S=ROOT/'data/accounting-master/construction-continuation-20261028'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def rel(p):return str(p.relative_to(ROOT))
v=json.loads((H/'attempt-04/verification.json').read_text());assert v['status']=='pass' and v['checks']==136
hashes=json.loads((H/'attempt-04/run-manifest.json').read_text())['source_hashes']
assert all(sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program)
f=S/'failure-dispositions.json';d=json.loads(f.read_text())
with (H/'navigation-before.json').open('x') as out:json.dump(dict(program=old,dispositions=d),out,indent=2)
originals={r['original_row']['id']:r['original_row'] for r in json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())['rows']}
assert len(d['rows'])==32
comparisons={
 'SIM-F027':'Claims40/30 share collateral50: supplied ranks yield40/10 or20/30; unknown rank retains both. Independent full recoveries40/30 overdraw by20 and conflict.',
 'SIM-F031':'Native noncash conversion extinguishes debt160 and face memory, adds16 to100 old shares, and yields4/29 ownership with assets170/equity170. Stale face can balance but fails independent contract oracle.',
 'SIM-F032':'Nonparticipating preference60 or quarter conversion at exit40/100/240/400 yields40/60/60/100. Tie retains both exclusive elections. Combined rights are wrong even when total payments conserve the pool.'}
for ident,comparison in comparisons.items():
 assert not any(r['id']==ident for r in d['rows'])
 d['rows'].append(dict(id=ident,original_row=originals[ident],disposition='exact_original_scoped_claims_conversion_discriminator',comparison=comparison,
  evidence=[rel(H/'attempt-04/verification.json'),rel(H/'result.md')],next_action='Actual rights/populations, claim priority, ownership and accounting treatment remain unadmitted; continue remaining failures and source/ordered review.',original_status_unchanged=True,broad_package_closed=False))
d['rows'].sort(key=lambda r:r['id']);d['reviewed_rows']=len(d['rows']);d['scope']='Thirty-five original rows individually reviewed;166 outside this continuation. Original criteria/statuses persist; scoped evidence is not whole-company closure.'
for r in d['rows']:assert r['original_row']==originals[r['id']]
dump(f,d)
lines=['# Current original failure dispositions','','28 October2026. Thirty-five original rows reviewed;166 outside this pass. All201 original rows/statuses persist. Coverage is not closure.','','| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines+=['| '+r['id']+' | '+r['comparison']+' | '+r['next_action']+' |' for r in d['rows']]
(S/'failure-dispositions.md').write_text('\n'.join(lines)+'\n')
for t in program['tasks']:
 if t['id'] in ['C04','T08']:t['evidence'].append(rel(H/'result.md'))
 if t['id']=='C04':
  t['next_action']='Thirty-five original failures reviewed;166 outside this pass. Continue pricing-policy/solver-limit and measurement failures, actual source dependencies with T03, and ordered reading from337.'
  t['remaining']=[x for x in t['remaining'] if not x.startswith('Thirty-two original rows')]
  t['remaining'].append('Thirty-five original rows individually compared;166 outside this pass. Actual rights/populations, general operation and claim-priority completeness remain open.')
for a,b in zip(old['tasks'],program['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']:assert a[key]==b[key]
dump(p,program)
entry='''
## Conversion and competing claims — 28 October 2026

SIM-F027/031/032 pass136 checks over12 native programs and29 solver cases.
Conversion creates16 shares beside100 and clears debt without cash. Claims40/30
share one50 pool under explicit priorities; nonparticipating preference preserves
exclusive choices, including equal-payoff ties. Unsupported arithmetic and budget
limits remain Unknown. Failed harness/encoding attempts are retained. Result:
company-state-claims-conversion-20261028/result.md under data/accounting-master.
No actual rights, priorities, accounting treatment or whole-company admission.

Thirty-five original failures reviewed;166 outside this pass. Main reading
336/831, resume337. All original criteria/statuses and releases persist.
E3 deferred. Continue pricing/measurement failures, source and ordered review.

'''
for name in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/construction-continuation-20261028/checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/name;title,rest=p.read_text().split('\n',1);p.write_text(title+'\n'+entry+rest)
for name,key in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/name;d=json.loads(p.read_text());d[key]['claims_conversion_continuation_20261028']=dict(result=rel(H/'result.md'),checks=136,native_cases=12,solver_cases=29,reviewed_original_failures=35,outside_pass=166,scope='Conditional native conversion and finite explicit rights; no actual admission');dump(p,d)
print(json.dumps(dict(reviewed=35,outside_pass=166,source_hashes_verified=len(hashes),task_statuses_preserved=True)))
