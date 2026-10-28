"""One-shot refresh of checked actor, causal and joint-stress discriminators."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
S=ROOT/'data/accounting-master/construction-continuation-20261028'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
def rel(p):return str(p.relative_to(ROOT))
v=json.loads((H/'attempt-01/verification.json').read_text());assert v['passed'] and v['checks']==170
hashes=json.loads((H/'attempt-01/source-hashes.json').read_text())
assert all(sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program)
d=json.loads((S/'failure-dispositions.json').read_text());assert len(d['rows'])==68
with (H/'navigation-before.json').open('x') as f:json.dump(dict(program=old,dispositions=d),f,indent=2)
originals={r['original_row']['id']:r['original_row'] for r in json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())['rows']}
for ident,comparison in {
 'SIM-F013':'Manager privately receives supplied coupon5/7 terms before the analyst. Complete reserve/payment paths use actor-visible observations; early analyst must choose a common reserve, leaving either floating arrears2 or fixed unused reserve2. Publication alone does not establish access.',
 'SIM-F017':'Conditioning on high rate selects cash40; intervention preserves the supplied confounder law and gives mean60 in one model. An observationally equivalent model gives intervention cash40. Numerical agreement with an imposed stress is not causal identification.',
 'SIM-F020':'Declared FX/demand pairs yield cash30/50 and supplied equal-mass mean40. Cartesian recombination invents cash-10/150 and mean55. Unknown dependence stays unresolved; unweighted support supplies no probability.'
}.items():
 assert not any(r['id']==ident for r in d['rows'])
 d['rows'].append(dict(id=ident,original_row=originals[ident],disposition='original_actor_causal_joint_stress_discriminator',comparison=comparison,evidence=[rel(H/'attempt-01/verification.json'),rel(H/'result.md')],next_action='Actual actor access, interpreted loan terms, causal mechanisms and economic dependence remain unverified. Connect source-backed semantics without extending these finite helpers by relabeling incompatible profiles.',original_status_unchanged=True,broad_package_closed=False))
d['rows'].sort(key=lambda r:r['id']);d['reviewed_rows']=71
d['scope']='71 original rows individually reviewed;130 outside this continuation. Original criteria/statuses persist; scoped exact examples are not broad closure.'
for r in d['rows']:assert r['original_row']==originals[r['id']]
dump(S/'failure-dispositions.json',d)
lines=['# Current original failure dispositions','','28 October2026. 71 original rows reviewed;130 outside this pass. All201 original rows/statuses persist. Coverage is not closure.','','| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines+=['| '+r['id']+' | '+r['comparison']+' | '+r['next_action']+' |' for r in d['rows']]
(S/'failure-dispositions.md').write_text(chr(10).join(lines)+chr(10))
for t in program['tasks']:
 if t['id']=='C04':
  t['evidence'].append(rel(H/'result.md'));t['next_action']='71 original failures reviewed;130 outside this pass. Reconcile remaining literature-derived failure rows against retained full evidence before adding tests; continue source research and ordered reading from361.'
  t['remaining']=[x for x in t['remaining'] if not x.startswith('68 original rows')]
  t['remaining'].append('71 original rows individually compared;130 outside this pass. Source-backed actor information, causal and joint-law assumptions, remaining literature cases and independent evaluation remain open.')
for a,b in zip(old['tasks'],program['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']:assert a[key]==b[key]
dump(p,program)
entry='''
## Actor information and joint stress — 28 October2026

SIM-F013/017/020 pass170 exact checks with seven saved full results and22
refusal controls. Private loan terms permit different policies; conditioning
and intervention answer different questions; joint scenarios retain economic
dependence. Actual knowledge, causal structure and source admission remain open.
Result: company-state-actor-causal-stress-20261028/result.md under data/accounting-master.

71 original failures reviewed;130 outside this pass. Main reading360/831,
resume361. Original criteria/statuses/releases persist;E3 deferred.
Continue literature-case reconciliation, connected sources and ordered review.

'''
for name in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/name;title,rest=p.read_text().split(chr(10),1);p.write_text(title+chr(10)+entry+rest)
checkpoint=S/'checkpoint.md';(H/'checkpoint-before.md').write_bytes(checkpoint.read_bytes())
checkpoint.write_text('# Construction continuation checkpoint'+chr(10)+entry+'''Live program: data/accounting-master/unified-program-20261028/program.json.
40 tasks,114 acceptance rows,156 clauses,18 packages,201 original failures.
T01 definition complete; construction/research/acceptance remain incomplete.
S1–S5 partial,S6 held,E3 deferred. Selected5.55-R1/provisional5.56-D1 not_ready.
No global continuation veto. Main review360/831;next361.

Next: inspect LIT-F001/002/003/005 and their exact evidence requirements.
Reuse checked history, duplicate-mass, persistent-term and joint-law results
where they answer the original question; do not infer coverage from labels.
Continue source research and reading361. Preserve READ-0358-0360-01 for
successor prose repair after diagnosis. Do not rerun completed one-shot scripts.
Concurrent edits stay separate. Prior checkpoint is in this unit/checkpoint-before.md.
''')
for name,key in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/name;data=json.loads(p.read_text());data[key]['actor_causal_stress_continuation_20261028']=dict(result=rel(H/'result.md'),checks=170,saved_results=7,refusal_controls=22,reviewed_original_failures=71,outside_pass=130,scope='Finite actor/policy and causal/joint-law distinctions; no actual source or economic admission');dump(p,data)
print(json.dumps(dict(reviewed=71,outside_pass=130,source_hashes_verified=len(hashes),task_statuses_preserved=True)))
