"""One-shot additive refresh after finite model-scope and measure checks."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
S=ROOT/'data/accounting-master/construction-continuation-20261028'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
def rel(p):return str(p.relative_to(ROOT))
v=json.loads((H/'attempt-01/verification.json').read_text());assert v['passed'] and v['checks']==105
hashes=json.loads((H/'attempt-01/source-hashes.json').read_text())
assert all(sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program)
d=json.loads((S/'failure-dispositions.json').read_text());assert len(d['rows'])==66
with (H/'navigation-before.json').open('x') as f:json.dump(dict(program=old,dispositions=d),f,indent=2)
originals={r['original_row']['id']:r['original_row'] for r in json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())['rows']}
for ident,comparison in {
 'SIM-F067':'An exact clear-only model misses supplied guarantee/withdrawal shortfalls10/15 and a private distribution restriction. Expanded finite paths preserve these mechanisms, explicit exclusions, unresolved candidates and budget frontier without claiming real population completeness.',
 'SIM-F008':'Supplied masses1/2 on outcomes100/60 retain mean80 when duplicated high syntax splits mass1/4+1/4. Equal encoding weights change mean to260/3; false economic alias rejects and unweighted support stays unchanged.'
}.items():
 assert not any(r['id']==ident for r in d['rows'])
 d['rows'].append(dict(id=ident,original_row=originals[ident],disposition='original_model_scope_measure_discriminator',comparison=comparison,evidence=[rel(H/'attempt-01/verification.json'),rel(H/'result.md')],next_action='Actual source-backed mechanisms, economic identities and probability measures remain open. Finite scope/equivalence is not whole-company coverage or actual admission.',original_status_unchanged=True,broad_package_closed=False))
d['rows'].sort(key=lambda r:r['id']);d['reviewed_rows']=68
d['scope']='68 original rows individually reviewed;133 outside this continuation. Original criteria/statuses persist; scoped exact examples are not broad closure.'
for r in d['rows']:assert r['original_row']==originals[r['id']]
dump(S/'failure-dispositions.json',d)
lines=['# Current original failure dispositions','','28 October2026. 68 original rows reviewed;133 outside this pass. All201 original rows/statuses persist. Coverage is not closure.','','| Original row | Current comparison | Residual / next action |','| --- | --- | --- | --- |']
lines[-1]='| --- | --- | --- |'
lines+=['| '+r['id']+' | '+r['comparison']+' | '+r['next_action']+' |' for r in d['rows']]
(S/'failure-dispositions.md').write_text(chr(10).join(lines)+chr(10))
for t in program['tasks']:
 if t['id']=='C04':
  t['evidence'].append(rel(H/'result.md'));t['next_action']='68 original failures reviewed;133 outside this pass. Continue manager/analyst information, conditioning/intervention and dependent joint stress cases, source research and ordered reading from355.'
  t['remaining']=[x for x in t['remaining'] if not x.startswith('66 original rows')]
  t['remaining'].append('68 original rows individually compared;133 outside this pass. Actual model populations, economic identities, information/causal semantics and independent evaluation remain open.')
for a,b in zip(old['tasks'],program['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']:assert a[key]==b[key]
dump(p,program)
entry='''
## Model scope and duplicate measures — 28 October2026

SIM-F067/008 pass105 exact checks across13 models and16 path/scope results.
Expanded supplied mechanisms preserve shortfalls10/15 and private covenant
restrictions. Correct duplicate mass splitting preserves mean80; equal encoding
weights instead produce260/3. Real population completeness remains unproved.
Result: company-state-model-scope-20261028/result.md under data/accounting-master.

68 original failures reviewed;133 outside this pass. Main reading354/831,
resume355. Original criteria/statuses/releases persist;E3 deferred.
Continue information/causal/dependent-stress cases, sources and ordered review.

'''
for name in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/name;title,rest=p.read_text().split(chr(10),1);p.write_text(title+chr(10)+entry+rest)
checkpoint=S/'checkpoint.md';(H/'checkpoint-before.md').write_bytes(checkpoint.read_bytes())
checkpoint.write_text('# Construction continuation checkpoint'+chr(10)+entry+'''Live program: data/accounting-master/unified-program-20261028/program.json.
40 tasks,114 acceptance rows,156 clauses,18 packages,201 original failures.
T01 definition complete; construction/research/acceptance remain incomplete.
S1–S5 partial,S6 held,E3 deferred. Selected5.55-R1/provisional5.56-D1 not_ready.
Main reading354/831;resume355. No global continuation veto.

Next: ordered main review355–360. Next uncovered original cases SIM-F013,
SIM-F017 and SIM-F020 concern actor knowledge, intervention and joint stress.
Reuse existing information/causal evidence before designing discriminators.
Continue source research. Do not rerun one-shot scripts; concurrent edits stay separate.
Prior checkpoint: company-state-model-scope-20261028/checkpoint-before.md.
''')
for name,key in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/name;data=json.loads(p.read_text());data[key]['model_scope_continuation_20261028']=dict(result=rel(H/'result.md'),checks=105,models=13,path_results=16,refusal_controls=5,reviewed_original_failures=68,outside_pass=133,scope='Finite omitted-mechanism and duplicate-measure cases; no real completeness or source admission');dump(p,data)
print(json.dumps(dict(reviewed=68,outside_pass=133,source_hashes_verified=len(hashes),task_statuses_preserved=True)))
