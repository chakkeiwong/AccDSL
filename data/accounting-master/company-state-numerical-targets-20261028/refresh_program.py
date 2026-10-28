"""One-shot additive refresh after exact numerical-target checks."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
S=ROOT/'data/accounting-master/construction-continuation-20261028'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def rel(p):return str(p.relative_to(ROOT))
v=json.loads((H/'attempt-01/verification.json').read_text());assert v['status']=='pass' and v['checks']==138
hashes=json.loads((H/'attempt-01/run-manifest.json').read_text())['source_hashes']
assert all(sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program)
d=json.loads((S/'failure-dispositions.json').read_text())
with (H/'navigation-before.json').open('x') as f:json.dump(dict(program=old,dispositions=d),f,indent=2)
originals={r['original_row']['id']:r['original_row'] for r in json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())['rows']}
assert len(d['rows'])==56
for ident,comparison in {
 'SIM-F056':'Exact single-draw objective minimizes at1/2 with residual-1/2; intended squared expectation and independent two-draw product minimize at1. Same-draw reuse changes target.',
 'SIM-F057':'Constrained optimum0 has derivative/multiplier2; interior root-1 is infeasible. Exact global polynomial and KKT controls pass only for the supplied convex case.',
 'SIM-F058':'Supplied pi=2-a,price=a*pi has full derivative2-2a versus frozen2-a. Exact central differences verify both quantities and the missed policy path.',
 'SIM-F059':'Reuses hash-verified F029 evidence: true capacity100 versus false-tail need110 root10140; original state payoffs leave10 unfunded. No new independent benchmark.',
 'SIM-F060':'Supplied polynomial has exact roots1/3 and no third. Newton from0/4 approaches different roots; start2 has zero derivative and remains unresolved; no economic selection.'
}.items():
 assert not any(r['id']==ident for r in d['rows'])
 d['rows'].append(dict(id=ident,original_row=originals[ident],disposition='original_numerical_target_discriminator',comparison=comparison,evidence=[rel(H/'attempt-01/verification.json'),rel(H/'result.md')],next_action='Admitted economic laws, coupled numerical services and independent validation remain open; exact local targets do not establish general solver or issuer correctness.',original_status_unchanged=True,broad_package_closed=False))
d['rows'].sort(key=lambda r:r['id']);d['reviewed_rows']=61
d['scope']='61 original rows individually reviewed;140 outside this continuation. Original criteria/statuses persist; scoped exact examples are not broad closure.'
for r in d['rows']:assert r['original_row']==originals[r['id']]
dump(S/'failure-dispositions.json',d)
lines=['# Current original failure dispositions','','28 October2026. 61 original rows reviewed;140 outside this pass. All201 original rows/statuses persist. Coverage is not closure.','','| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines+=['| '+r['id']+' | '+r['comparison']+' | '+r['next_action']+' |' for r in d['rows']]
(S/'failure-dispositions.md').write_text('\n'.join(lines)+'\n')
for t in program['tasks']:
 if t['id']=='C04':
  t['evidence'].append(rel(H/'result.md'));t['next_action']='61 original failures reviewed;140 outside this pass. Continue unit/horizon/evaluation distinctions, connected source research and ordered reading from349.'
  t['remaining']=[x for x in t['remaining'] if not x.startswith('56 original rows')]
  t['remaining'].append('61 original rows individually compared;140 outside this pass. Actual economic/model assumptions, numerical coupling, full company construction and independent validation remain open.')
for a,b in zip(old['tasks'],program['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']:assert a[key]==b[key]
dump(p,program)
entry='''
## Numerical targets and solution scope — 28 October2026

SIM-F056–060 pass138 checks,11 direct polynomial SMT cases and five retained
pricing-result checks. Expected-residual objectives, constrained optima, total
derivatives, original funding capacity and multiple roots retain their distinct
targets. Existing F059 pricing evidence is reused explicitly. Result:
company-state-numerical-targets-20261028/result.md under data/accounting-master.
Actual economic models and broad numerical services remain open.

61 original failures reviewed;140 outside this pass. Main reading348/831,
resume349. Original criteria/statuses/releases persist;E3 deferred.
Continue unit/horizon/evaluation distinctions, source research and ordered review.

'''
for name in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/name;title,rest=p.read_text().split('\n',1);p.write_text(title+'\n'+entry+rest)
checkpoint=S/'checkpoint.md';(H/'checkpoint-before.md').write_bytes(checkpoint.read_bytes())
checkpoint.write_text('# Construction continuation checkpoint\n'+entry+'''Live program: data/accounting-master/unified-program-20261028/program.json.
40 tasks,114 acceptance rows,156 clauses,18 packages,201 original failures.
T01 definition complete; construction/research/acceptance remain incomplete.
S1–S5 partial,S6 held,E3 deferred. Selected5.55-R1/provisional5.56-D1 not_ready.
Main reading348/831;resume349. No global continuation veto.

Next: original SIM-F061 unit invariance, SIM-F062 terminal obligations and
SIM-F063–065 validation/threshold/unresolved-mass distinctions. This is design
and exact conformance work; E3 forecasting remains deferred. Resume ordered
main reading from349 in a bounded independent slice.
Continue independent source research and ordered review. Do not rerun completed
one-shot refresh scripts. Concurrent research edits remain separately owned.
Prior checkpoint: company-state-numerical-targets-20261028/checkpoint-before.md.
''')
for name,key in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/name;data=json.loads(p.read_text())
 data[key]['numerical_targets_continuation_20261028']=dict(result=rel(H/'result.md'),checks=138,direct_smt_cases=11,retained_solver_cases=5,reviewed_original_failures=61,outside_pass=140,scope='Exact numerical target examples; economic admission and broad services remain open')
 dump(p,data)
print(json.dumps(dict(reviewed=61,outside_pass=140,source_hashes_verified=len(hashes),task_statuses_preserved=True)))
