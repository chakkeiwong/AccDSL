"""Add original loss-vintage discriminator without admitting actual tax rights."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
S=ROOT/'data/accounting-master/construction-continuation-20261028'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def rel(p):return str(p.relative_to(ROOT))
v=json.loads((H/'attempt-01/verification.json').read_text());assert v['status']=='pass' and v['checks']==211
hashes=json.loads((H/'attempt-01/run-manifest.json').read_text())['source_hashes']
assert all(sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program)
d=json.loads((S/'failure-dispositions.json').read_text())
with (H/'navigation-before.json').open('x') as fh:json.dump(dict(program=old,dispositions=d),fh,indent=2)
originals={r['original_row']['id']:r['original_row'] for r in json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())['rows']}
assert len(d['rows'])==42 and not any(r['id']=='SIM-F042' for r in d['rows'])
d['rows'].append(dict(id='SIM-F042',original_row=originals['SIM-F042'],disposition='original_scoped_legal_loss_vintage_discriminator',comparison='Retained engine preserves40->10->0 under income30/30, taxable20 and conditional tax5; negative10 adds a distinct vintage. Duplicate/expiry/unknown controls and independent prior-state binding detect double use and coherent invented history.',evidence=[rel(H/'attempt-01/verification.json'),rel(H/'result.md')],next_action='Actual eligibility/cap/expiry, source-backed taxable income, immutable predecessor binding and native financial carry remain open; conditional conservation is not authenticity.',original_status_unchanged=True,broad_package_closed=False))
d['rows'].sort(key=lambda r:r['id']);d['reviewed_rows']=43;d['scope']='43 original rows individually reviewed;158 outside this continuation. Original criteria/statuses persist; scoped evidence is not broad closure.'
for r in d['rows']:assert r['original_row']==originals[r['id']]
dump(S/'failure-dispositions.json',d)
lines=['# Current original failure dispositions','','28 October2026. 43 original rows reviewed;158 outside this pass. All201 original rows/statuses persist. Coverage is not closure.','','| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines+=['| '+r['id']+' | '+r['comparison']+' | '+r['next_action']+' |' for r in d['rows']]
(S/'failure-dispositions.md').write_text('\n'.join(lines)+'\n')
for t in program['tasks']:
 if t['id']=='C04':
  t['evidence'].append(rel(H/'result.md'));t['next_action']='43 original failures reviewed;158 outside this pass. Continue collateral/contractual-clock and information/scenario cases, source dependencies and ordered reading from337.'
  t['remaining']=[x for x in t['remaining'] if not x.startswith('42 original rows')]
  t['remaining'].append('43 original rows individually compared;158 outside this pass. Source-backed rights, exact predecessor binding, linked settlement and complete operations remain open.')
for a,b in zip(old['tasks'],program['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']:assert a[key]==b[key]
dump(p,program)
entry='''
## Loss identity and dated carryforward — 28 October 2026

SIM-F042 passes211 checks over28 proposals and11 apply checks. Loss40 carries
through income30/30 as40->10->0; negative10 creates a separate vintage. Unknowns,
expiry and double-use controls retain their meanings. A coherent invented
history requires independent prior-state/source binding. Result:
company-state-loss-vintages-20261028/result.md under data/accounting-master.
Actual tax admission and native annual financial carry remain open.

43 original failures reviewed;158 outside this pass. Main reading336/831,
resume337. Original criteria/statuses/releases persist;E3 deferred.
Continue collateral/contractual-clock cases, source and ordered review.

'''
for name in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/name;title,rest=p.read_text().split('\n',1);p.write_text(title+'\n'+entry+rest)
checkpoint=S/'checkpoint.md';(H/'checkpoint-before.md').write_bytes(checkpoint.read_bytes())
checkpoint.write_text('# Construction continuation checkpoint\n'+entry+'''Live program: data/accounting-master/unified-program-20261028/program.json.
40 tasks,114 acceptance rows,156 clauses,18 packages,201 original failures.
T01 definition complete; construction/research/acceptance remain incomplete.
S1–S5 partial,S6 held,E3 deferred. Selected5.55-R1/provisional5.56-D1 not_ready.
Main reading336/831;resume337. No global continuation veto.

Next: continue ordered main review from337 and ready source/failure work.
SIM-F041 collateral6/subsidiary4/parent2 and SIM-F044 fee2/interest5/payment6
with cure timing are original unreviewed targets. Preserve original populations.
Do not rerun completed one-shot refresh scripts. Concurrent goal-alignment
edits remain separately owned; stage only the exact continuation changes.
Prior checkpoint: company-state-loss-vintages-20261028/checkpoint-before.md.
''')
for name,key in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/name;data=json.loads(p.read_text());data[key]['loss_vintages_continuation_20261028']=dict(result=rel(H/'result.md'),checks=211,proposal_cases=28,apply_cases=11,reviewed_original_failures=43,outside_pass=158,scope='Conditional legal loss ledger and exact prior-state oracle; no tax/source admission or financial carry');dump(p,data)
print(json.dumps(dict(reviewed=43,outside_pass=158,source_hashes_verified=len(hashes),task_statuses_preserved=True)))
