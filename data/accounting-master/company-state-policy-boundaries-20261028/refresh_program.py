"""One-shot policy-boundary reconciliation; preserve original acceptance."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
S=ROOT/'data/accounting-master/construction-continuation-20261028'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
def rel(p):return str(p.relative_to(ROOT))
v=json.loads((H/'attempt-01/verification.json').read_text());assert v['passed'] and v['checks']==288
hashes=json.loads((H/'attempt-01/source-hashes.json').read_text())
assert all(sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program)
d=json.loads((S/'failure-dispositions.json').read_text());assert len(d['rows'])==75
with (H/'navigation-before.json').open('x') as f:json.dump(dict(program=old,dispositions=d),f,indent=2)
originals={r['original_row']['id']:r['original_row'] for r in json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())['rows']}
comparisons={'LIT-F006': ('Exact binary issuance refuses a fractional action; explicit feasible lifts preserve cash/unpaid consequences and refuse hidden-history dependence.', 'General discrete-action approximation and source-backed feasible lifts remain open.'), 'LIT-F007': ('Tiny cash errors can flip default. Supplied finite couplings satisfy boundary-mass plus coupling-error bounds; unweighted histories retain a boundary set.', 'Actual approximation algorithms must justify coupling/error premises.'), 'LIT-F008': ('Equal optimized values conceal exact regret100. Common-class uniform bounds pass162 finite comparisons; missing policies/classes and false bounds refuse.', 'Production feasibility, information preservation and policy transfer remain open.'), 'LIT-F009': ('Distinct sampled observations yield stopping cost-1/2, pooled histories0; independent-increment comparator gives0 for every feasible policy. Future-conditioned actions refuse.', 'Local finite illustration only; source Example7.1 is Gaussian. General adapted estimation and dependent issuer data remain open.')}
for ident,(comparison,next_action) in comparisons.items():
 assert not any(r['id']==ident for r in d['rows'])
 d['rows'].append(dict(id=ident,original_row=originals[ident],disposition='original_literature_policy_boundary_discriminator',comparison=comparison,evidence=[rel(H/'attempt-01/verification.json'),rel(H/'result.md')],next_action=next_action,original_status_unchanged=True,broad_package_closed=False))
d['rows'].sort(key=lambda r:r['id']);d['reviewed_rows']=79
d['scope']='79 original rows individually reviewed;122 outside this continuation. Original criteria/statuses persist; scoped exact examples are not broad closure.'
for r in d['rows']:assert r['original_row']==originals[r['id']]
dump(S/'failure-dispositions.json',d)
lines=['# Current original failure dispositions','','28 October2026. 79 original rows reviewed;122 outside this pass. All201 original rows/statuses persist. Coverage is not closure.','','| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines+=['| '+r['id']+' | '+r['comparison']+' | '+r['next_action']+' |' for r in d['rows']]
(S/'failure-dispositions.md').write_text(chr(10).join(lines)+chr(10))
for t in program['tasks']:
 if t['id']=='C04':
  t['evidence'].append(rel(H/'result.md'));t['next_action']='79 original failures reviewed;122 outside this pass. Continue ordered manuscript reading361 and inspect next uncovered literature failures; preserve finite-policy limits and continue connected sources.'
  t['remaining']=[x for x in t['remaining'] if not x.startswith('75 original rows')]
  t['remaining'].append('79 original rows individually compared;122 outside this pass. Actual policy/coupling/information premises, remaining literature cases, source-backed construction and independent evaluation remain open.')
for a,b in zip(old['tasks'],program['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']:assert a[key]==b[key]
dump(p,program)
entry='\n## Policy feasibility and approximation boundaries — 28 October2026\n\nLIT-F006–009 pass288 exact checks with18 result groups,16 refusal controls\nand162 finite policy comparisons. Fractional actions, threshold errors, close\nminima and sampled future information remain distinct. General approximation,\nsource-backed policies and adapted-estimation guarantees remain open.\nResult: company-state-policy-boundaries-20261028/result.md under data/accounting-master.\n\n79 original failures reviewed;122 outside this pass. Main reading360/831,\nresume361. Original criteria/statuses/releases persist;E3 deferred.\nContinue ordered review and remaining literature/source work.\n\n'
for name in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/name;title,rest=p.read_text().split(chr(10),1);p.write_text(title+chr(10)+entry+rest)
checkpoint=S/'checkpoint.md';(H/'checkpoint-before.md').write_bytes(checkpoint.read_bytes())
checkpoint.write_text('# Construction continuation checkpoint'+chr(10)+entry+'''Live program: data/accounting-master/unified-program-20261028/program.json.
40 tasks,114 acceptance rows,156 clauses,18 packages,201 original failures.
T01 definition complete; construction/research/acceptance remain incomplete.
S1–S5 partial,S6 held,E3 deferred. Selected5.55-R1/provisional5.56-D1 not_ready.
No global continuation veto. Main review360/831;next361.

Next: ordered reading361–366, then remaining original literature failures.
Keep discrete feasibility, threshold/coupling premises, common policy identities
and sampled information separate. Source-backed construction/research remain
open. READ-0358-0360-01 awaits successor repair after diagnosis. Do not rerun
completed one-shot scripts. Concurrent edits stay separate; prior checkpoint
is in this unit/checkpoint-before.md.
''')
for name,key in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/name;data=json.loads(p.read_text());data[key]['policy_boundaries_continuation_20261028']=dict(result=rel(H/'result.md'),checks=288,result_groups=18,refusal_controls=16,finite_policy_comparisons=162,reviewed_original_failures=79,outside_pass=122,scope='Finite policy/information examples; no general approximation or source admission');dump(p,data)
print(json.dumps(dict(reviewed=79,outside_pass=122,source_hashes_verified=len(hashes),task_statuses_preserved=True)))
