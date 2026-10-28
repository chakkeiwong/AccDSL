"""One-shot additive refresh after checking original quiet-right/scope rows."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
H=Path(__file__).resolve().parent
S=ROOT/'data/accounting-master/construction-continuation-20261028'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def rel(p):return str(p.relative_to(ROOT))
v=json.loads((H/'attempt-01/verification.json').read_text())
assert v['status']=='pass' and v['checks']==169
hashes=json.loads((H/'attempt-01/run-manifest.json').read_text())['source_hashes']
assert all(sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
p=ROOT/'data/accounting-master/unified-program-20261028/program.json'
program=json.loads(p.read_text());old=deepcopy(program)
d=json.loads((S/'failure-dispositions.json').read_text())
with (H/'navigation-before.json').open('x') as f:json.dump(dict(program=old,dispositions=d),f,indent=2)
originals={r['original_row']['id']:r['original_row'] for r in json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())['rows']}
assert len(d['rows'])==49
for ident,comparison in {
 'SIM-F045':'Two coupons5/5 preserve call rights; cost102 versus110 leaves88 versus80. Fees8/9/12 retain tie/no-exercise; quiet-only merge cannot extend. Unknown rights do not authorize exercise.',
 'SIM-F046':'Same immediate output and separate marginals hide9/10 versus1/2 signal quality. All four signal policies match full paths; green-lend means7/10 versus-1/2. Joint-law merge rejects.',
 'SIM-F049':'Cash25 at short horizon becomes3 after repayment22; covenant28 removes distribution5 and holding leaves8. Structural versus policy-result cache scope, stale/tampered reuse and Unknown are checked.'}.items():
 assert not any(r['id']==ident for r in d['rows'])
 d['rows'].append(dict(id=ident,original_row=originals[ident],disposition='original_quiet_right_information_scope_discriminator',comparison=comparison,evidence=[rel(H/'attempt-01/verification.json'),rel(H/'result.md')],next_action='Source-backed rights and observation laws, native accounting and wider query/evidence-service integration remain open; finite supplied cases do not admit actual company state.',original_status_unchanged=True,broad_package_closed=False))
d['rows'].sort(key=lambda r:r['id']);d['reviewed_rows']=52
d['scope']='52 original rows individually reviewed;149 outside this continuation. Original criteria/statuses persist; scoped finite examples are not broad closure.'
for r in d['rows']:assert r['original_row']==originals[r['id']]
dump(S/'failure-dispositions.json',d)
lines=['# Current original failure dispositions','','28 October2026. 52 original rows reviewed;149 outside this pass. All201 original rows/statuses persist. Coverage is not closure.','','| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines+=['| '+r['id']+' | '+r['comparison']+' | '+r['next_action']+' |' for r in d['rows']]
(S/'failure-dispositions.md').write_text('\n'.join(lines)+'\n')
for t in program['tasks']:
 if t['id']=='C04':
  t['evidence'].append(rel(H/'result.md'))
  t['next_action']='52 original failures reviewed;149 outside this pass. Continue approximation/numerical cases, connected source research and ordered reading from349.'
  t['remaining']=[x for x in t['remaining'] if not x.startswith('49 original rows')]
  t['remaining'].append('52 original rows individually compared;149 outside this pass. Actual rights and observation laws, broad query/service composition and complete operations remain open.')
for a,b in zip(old['tasks'],program['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']:assert a[key]==b[key]
dump(p,program)
entry='''
## Quiet rights, information and query scope — 28 October2026

SIM-F045/046/049 pass169 exact checks across26 finite models,25 full-path
comparisons and19 refusal controls. Quiet coupons preserve future call rights;
equal immediate output preserves neither signal quality nor later policy law.
Horizon/covenant changes invalidate stale reuse; structural certificates and
policy-specific results have different scopes. Result:
company-state-quiet-rights-scope-20261028/result.md under data/accounting-master.
Actual rights, source/observation laws and broad native integration remain open.

52 original failures reviewed;149 outside this pass. Main reading348/831,
resume349. Original criteria/statuses/releases persist;E3 deferred.
Continue approximation/numerical cases, source research and ordered review.

'''
for name in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/name;title,rest=p.read_text().split('\n',1);p.write_text(title+'\n'+entry+rest)
checkpoint=S/'checkpoint.md';(H/'checkpoint-before.md').write_bytes(checkpoint.read_bytes())
checkpoint.write_text('# Construction continuation checkpoint\n'+entry+'''Live program: data/accounting-master/unified-program-20261028/program.json.
40 tasks,114 acceptance rows,156 clauses,18 packages,201 original failures.
T01 definition complete; construction/research/acceptance remain incomplete.
S1–S5 partial,S6 held,E3 deferred. Selected5.55-R1/provisional5.56-D1 not_ready.
Main reading348/831;resume349. No global continuation veto.

Next: inspect original SIM-F052 persistent-type resampling, SIM-F053 importance
weights, SIM-F054 unseen rare event and SIM-F055 threshold ambiguity.
Audit exact supplied probabilities separately from any empirical simulation.
Continue independent source research and ordered review. Do not rerun completed
one-shot refresh scripts. Concurrent research edits remain separately owned.
Prior checkpoint: company-state-quiet-rights-scope-20261028/checkpoint-before.md.
''')
for name,key in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/name;data=json.loads(p.read_text())
 data[key]['quiet_rights_scope_continuation_20261028']=dict(result=rel(H/'result.md'),checks=169,finite_models=26,path_comparisons=25,reviewed_original_failures=52,outside_pass=149,scope='Exact original finite examples; source/accounting admission and broad services remain open')
 dump(p,data)
print(json.dumps(dict(reviewed=52,outside_pass=149,source_hashes_verified=len(hashes),task_statuses_preserved=True)))
