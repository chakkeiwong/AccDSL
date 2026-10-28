"""Preserve original rows while adding four exact relational discriminators."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;S=ROOT/'data/accounting-master/construction-continuation-20261028'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def rel(p):return str(p.relative_to(ROOT))
v=json.loads((H/'attempt-01/verification.json').read_text());assert v['status']=='pass' and v['checks']==87
hashes=json.loads((H/'attempt-01/run-manifest.json').read_text())['source_hashes']
assert all(sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program)
d=json.loads((S/'failure-dispositions.json').read_text())
with (H/'navigation-before.json').open('x') as fh:json.dump(dict(program=old,dispositions=d),fh,indent=2)
originals={r['original_row']['id']:r['original_row'] for r in json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())['rows']}
assert len(d['rows'])==45
for ident,comparison in {
 'SIM-F047':'x=z+1,z in[0,2] gives attained x bounds[1,3], exact member checks and direct affine elimination equivalence; dropping constraints wrongly admits0/4. Generic projection service unclaimed.',
 'SIM-F048':'Persistent paths(0,10)/(10,0) each total10. Independent period types enlarge support to include(10,10),total20; exact support and bounds distinguish the models.',
 'SIM-F050':'Shared x-x on[0,1] is[0,0]. Independent copy produces[-1,1]; restoring identity returns0. Outer enclosure is not the original exact range.',
 'SIM-F051':'Grid endingalpha.9 gives loss1-alpha minimum.1; truealpha1 gives0. Unsampled region has attained lower0/unattained upper.1; zero-budget Unknown retains formula.'}.items():
 assert not any(r['id']==ident for r in d['rows'])
 d['rows'].append(dict(id=ident,original_row=originals[ident],disposition='original_exact_relational_bound_discriminator',comparison=comparison,evidence=[rel(H/'attempt-01/verification.json'),rel(H/'result.md')],next_action='Source-supported relations, broad query/service composition and nonlinear/large-domain completeness remain open; exact small examples do not admit an issuer model.',original_status_unchanged=True,broad_package_closed=False))
d['rows'].sort(key=lambda r:r['id']);d['reviewed_rows']=49;d['scope']='49 original rows individually reviewed;152 outside this continuation. Original criteria/statuses persist; scoped exact examples are not broad closure.'
for r in d['rows']:assert r['original_row']==originals[r['id']]
dump(S/'failure-dispositions.json',d)
lines=['# Current original failure dispositions','','28 October2026. 49 original rows reviewed;152 outside this pass. All201 original rows/statuses persist. Coverage is not closure.','','| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines+=['| '+r['id']+' | '+r['comparison']+' | '+r['next_action']+' |' for r in d['rows']]
(S/'failure-dispositions.md').write_text('\n'.join(lines)+'\n')
for t in program['tasks']:
 if t['id']=='C04':
  t['evidence'].append(rel(H/'result.md'));t['next_action']='49 original failures reviewed;152 outside this pass. Continue quiet rights, information-state equivalence/cache and scenario cases, source dependencies and ordered reading from349.'
  t['remaining']=[x for x in t['remaining'] if not x.startswith('45 original rows')]
  t['remaining'].append('49 original rows individually compared;152 outside this pass. Actual relations/rights, query-service composition, broad numerical fragments and complete operations remain open.')
for a,b in zip(old['tasks'],program['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']:assert a[key]==b[key]
dump(p,program)
entry='''
## Projection, dependence and sampled bounds — 28 October2026

SIM-F047/048/050/051 pass87 checks across25 solver calls plus direct affine
elimination. Implied x bounds, persistent paths, shared variables and unsampled
endpoints remain distinct from dropped/rectangular/independent/sample shortcuts.
Zero-budget Unknown retains the question. Result:
company-state-relational-bounds-20261028/result.md under data/accounting-master.
Broad projection/query services and actual source relations remain open.

49 original failures reviewed;152 outside this pass. Main reading348/831,
resume349. Original criteria/statuses/releases persist;E3 deferred.
Continue quiet rights/information/cache cases, source and ordered review.

'''
for name in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/name;title,rest=p.read_text().split('\n',1);p.write_text(title+'\n'+entry+rest)
checkpoint=S/'checkpoint.md';(H/'checkpoint-before.md').write_bytes(checkpoint.read_bytes())
checkpoint.write_text('# Construction continuation checkpoint\n'+entry+'''Live program: data/accounting-master/unified-program-20261028/program.json.
40 tasks,114 acceptance rows,156 clauses,18 packages,201 original failures.
T01 definition complete; construction/research/acceptance remain incomplete.
S1–S5 partial,S6 held,E3 deferred. Selected5.55-R1/provisional5.56-D1 not_ready.
Main reading348/831;resume349. No global continuation veto.

Next: original SIM-F045 quiet call rights, SIM-F046 same immediate output but
different later signal quality, SIM-F049 cache invalidation when horizon or
covenants change. Inspect retained sources/implementations before auditing
next plan; preserve all original populations. Continue independent source
research and ordered review. Do not rerun completed one-shot refresh scripts.
Concurrent research edits remain separately owned; stage only exact changes.
Prior checkpoint: company-state-relational-bounds-20261028/checkpoint-before.md.
''')
for name,key in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/name;data=json.loads(p.read_text());data[key]['relational_bounds_continuation_20261028']=dict(result=rel(H/'result.md'),checks=87,solver_cases=25,reviewed_original_failures=49,outside_pass=152,scope='Exact original relational examples; no broad query service or actual admission');dump(p,data)
print(json.dumps(dict(reviewed=49,outside_pass=152,source_hashes_verified=len(hashes),task_statuses_preserved=True)))
