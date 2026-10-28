"""One-shot refresh after complete refinancing interaction checks."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
S=ROOT/'data/accounting-master/construction-continuation-20261028'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def rel(p):return str(p.relative_to(ROOT))
v=json.loads((H/'attempt-02/verification.json').read_text());assert v['passed'] and v['checks']==293
hashes=json.loads((H/'attempt-02/source-hashes.json').read_text())
assert all(sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program)
d=json.loads((S/'failure-dispositions.json').read_text())
with (H/'navigation-before.json').open('x') as f:json.dump(dict(program=old,dispositions=d),f,indent=2)
assert len(d['rows'])==66
originals={r['original_row']['id']:r['original_row'] for r in json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())['rows']}
row=next(r for r in d['rows'] if r['id']=='SIM-F066')
row.update(disposition='original_refinancing_interaction_discriminator',
 comparison='Complete refinancing preserves old/new debt identity, dated cash, tax and share memory. Cash40.5/tax3.5/old ownership10/11 differ from balanced stale-tax cash39 and old ownership1. Two account maps, full journals/reports and dependency/refusal controls pass.',
 next_action='Extend compatible source-backed tax, rights and ownership methods. The authored immediate-deduction adapter is not the incompatible shared lease/tax schema or general native tax integration.')
row['evidence'] += [rel(H/'attempt-02/verification.json'),rel(H/'result.md')]
for r in d['rows']:
 assert r['original_row']==originals[r['id']]
 if r['id']=='SIM-F060':r['comparison']=r['comparison'].replace('roots1/3','roots1 and3')
dump(S/'failure-dispositions.json',d)
lines=['# Current original failure dispositions','','28 October2026. 66 original rows reviewed;135 outside this pass. All201 original rows/statuses persist. Coverage is not closure.','','| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines+=['| '+r['id']+' | '+r['comparison']+' | '+r['next_action']+' |' for r in d['rows']]
(S/'failure-dispositions.md').write_text('\n'.join(lines)+'\n')
for t in program['tasks']:
 if t['id']=='C04':
  t['evidence'].append(rel(H/'result.md'));t['next_action']='66 original failures reviewed;135 outside this pass. F066 now has complete scoped refinancing evidence. Continue F067 omitted mechanisms, duplicate economic encodings, source research and ordered reading from355.'
  t['remaining']=[x for x in t['remaining'] if not x.startswith('66 original rows')]
  t['remaining'].append('66 original rows individually compared;135 outside this pass. Broader compatible tax/ownership integration, model-family coverage and independent evaluation remain open.')
for a,b in zip(old['tasks'],program['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']:assert a[key]==b[key]
dump(p,program)
entry='''
## Refinancing interactions — 28 October2026

SIM-F066 now passes293 checks across11 native programs and13 dependency
controls. Complete debt/cash/tax/share sequences preserve cash40.5, tax3.5
and old ownership10/11; stale results refuse. The tax adapter is explicitly
narrow, not the incompatible shared lease/tax book. Result:
company-state-refinancing-interactions-20261028/result.md under data/accounting-master.

66 original failures reviewed;135 outside this pass. Main reading354/831,
resume355. Original criteria/statuses/releases persist;E3 deferred.
Continue omitted model mechanisms, duplicate encodings, sources and ordered review.

'''
for name in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/name;title,rest=p.read_text().split('\n',1);p.write_text(title+'\n'+entry+rest)
checkpoint=S/'checkpoint.md';(H/'checkpoint-before.md').write_bytes(checkpoint.read_bytes())
checkpoint.write_text('# Construction continuation checkpoint\n'+entry+'''Live program: data/accounting-master/unified-program-20261028/program.json.
40 tasks,114 acceptance rows,156 clauses,18 packages,201 original failures.
T01 definition complete; construction/research/acceptance remain incomplete.
S1–S5 partial,S6 held,E3 deferred. Selected5.55-R1/provisional5.56-D1 not_ready.
Main reading354/831;resume355. No global continuation veto.

Next: SIM-F067 omitted guarantee/private covenant/behavior alternatives; then
SIM-F008 duplicate economic encodings. Preserve conditional family scope and
do not infer real completeness from finite examples. Continue source research
and ordered review. Do not rerun one-shot scripts. Concurrent edits stay separate.
Prior checkpoint: company-state-refinancing-interactions-20261028/checkpoint-before.md.
''')
for name,key in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/name;data=json.loads(p.read_text());data[key]['refinancing_interactions_continuation_20261028']=dict(result=rel(H/'result.md'),checks=293,native_programs=11,dependency_controls=13,reviewed_original_failures=66,outside_pass=135,scope='Full synthetic refinancing path; no general tax integration or actual admission');dump(p,data)
print(json.dumps(dict(reviewed=66,outside_pass=135,source_hashes_verified=len(hashes),task_statuses_preserved=True)))
