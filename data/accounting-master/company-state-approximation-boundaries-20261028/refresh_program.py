"""One-shot additive refresh after exact approximation-boundary checks."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
S=ROOT/'data/accounting-master/construction-continuation-20261028'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def rel(p):return str(p.relative_to(ROOT))
v=json.loads((H/'attempt-01/verification.json').read_text());assert v['status']=='pass' and v['checks']==80
hashes=json.loads((H/'attempt-01/run-manifest.json').read_text())['source_hashes']
assert all(sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program)
d=json.loads((S/'failure-dispositions.json').read_text())
with (H/'navigation-before.json').open('x') as f:json.dump(dict(program=old,dispositions=d),f,indent=2)
originals={r['original_row']['id']:r['original_row'] for r in json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())['rows']}
assert len(d['rows'])==52
for ident,comparison in {
 'SIM-F052':'Fixed resampling can lose rare type despite ESS100. Another offset retains it; original two-type family remains intact. ESS does not certify exact support or diversity.',
 'SIM-F053':'Target tail.001/proposal.1/severity1000 has weighted expectation1 versus unweighted100. Two-draw ordinary expectation1 differs from self-normalized325/28; invalid support refuses.',
 'SIM-F054':'No event in100 iid draws has exact probability.904792 for p.001. Zero-event95% upper endpoint.029513 is rationally bracketed; fixed-design binomial coverage checked only at supplied p.',
 'SIM-F055':'Exact interval funding witnesses distinguish safe, unsafe and unresolved, including lower/upper threshold contact. Small point error can reverse guard; zero budget retains Unknown.'}.items():
 assert not any(r['id']==ident for r in d['rows'])
 d['rows'].append(dict(id=ident,original_row=originals[ident],disposition='original_approximation_boundary_discriminator',comparison=comparison,evidence=[rel(H/'attempt-01/verification.json'),rel(H/'result.md')],next_action='Actual probability/error-bound admission, target-specific approximation validation and wider query integration remain open; exact examples do not admit an issuer model.',original_status_unchanged=True,broad_package_closed=False))
d['rows'].sort(key=lambda r:r['id']);d['reviewed_rows']=56
d['scope']='56 original rows individually reviewed;145 outside this continuation. Original criteria/statuses persist; scoped exact examples are not broad closure.'
for r in d['rows']:assert r['original_row']==originals[r['id']]
dump(S/'failure-dispositions.json',d)
lines=['# Current original failure dispositions','','28 October2026. 56 original rows reviewed;145 outside this pass. All201 original rows/statuses persist. Coverage is not closure.','','| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines+=['| '+r['id']+' | '+r['comparison']+' | '+r['next_action']+' |' for r in d['rows']]
(S/'failure-dispositions.md').write_text('\n'.join(lines)+'\n')
for t in program['tasks']:
 if t['id']=='C04':
  t['evidence'].append(rel(H/'result.md'));t['next_action']='56 original failures reviewed;145 outside this pass. Continue numerical-objective/derivative cases, connected source research and ordered reading from349.'
  t['remaining']=[x for x in t['remaining'] if not x.startswith('52 original rows')]
  t['remaining'].append('56 original rows individually compared;145 outside this pass. Actual probability/error assumptions, target-specific approximation and broad numerical/query-service composition remain open.')
for a,b in zip(old['tasks'],program['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']:assert a[key]==b[key]
dump(p,program)
entry='''
## Approximation and funding boundaries — 28 October2026

SIM-F052/053/054/055 pass80 exact checks and15 solver calls. ESS100 can hide
lost persistent types; weighted target loss1 differs from proposal loss100.
Empty samples retain rare-event uncertainty; threshold-touching intervals
preserve safe/unsafe/unresolved meanings. Result:
company-state-approximation-boundaries-20261028/result.md under data/accounting-master.
Actual probability/error assumptions and broader approximation remain open.

56 original failures reviewed;145 outside this pass. Main reading348/831,
resume349. Original criteria/statuses/releases persist;E3 deferred.
Continue numerical-objective/derivative cases, source research and ordered review.

'''
for name in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/name;title,rest=p.read_text().split('\n',1);p.write_text(title+'\n'+entry+rest)
checkpoint=S/'checkpoint.md';(H/'checkpoint-before.md').write_bytes(checkpoint.read_bytes())
checkpoint.write_text('# Construction continuation checkpoint\n'+entry+'''Live program: data/accounting-master/unified-program-20261028/program.json.
40 tasks,114 acceptance rows,156 clauses,18 packages,201 original failures.
T01 definition complete; construction/research/acceptance remain incomplete.
S1–S5 partial,S6 held,E3 deferred. Selected5.55-R1/provisional5.56-D1 not_ready.
Main reading348/831;resume349. No global continuation veto.

Next: inspect original SIM-F056 squared sampled residual, SIM-F057 boundary
first-order conditions, SIM-F058 total derivative, SIM-F059 false extrapolated
funding and SIM-F060 local versus global root claims. Audit stated targets and
independent algebra before running exact finite diagnostics.
Continue independent source research and ordered review. Do not rerun completed
one-shot refresh scripts. Concurrent research edits remain separately owned.
Prior checkpoint: company-state-approximation-boundaries-20261028/checkpoint-before.md.
''')
for name,key in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/name;data=json.loads(p.read_text())
 data[key]['approximation_boundaries_continuation_20261028']=dict(result=rel(H/'result.md'),checks=80,solver_cases=15,reviewed_original_failures=56,outside_pass=145,scope='Exact approximation examples; actual model/error admission and broad services remain open')
 dump(p,data)
print(json.dumps(dict(reviewed=56,outside_pass=145,source_hashes_verified=len(hashes),task_statuses_preserved=True)))
