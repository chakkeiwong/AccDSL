"""One-shot additive refresh after units/horizon/evaluation checks."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
S=ROOT/'data/accounting-master/construction-continuation-20261028'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def rel(p):return str(p.relative_to(ROOT))
v=json.loads((H/'attempt-01/verification.json').read_text());assert v['status']=='pass' and v['checks']==194
hashes=json.loads((H/'attempt-01/run-manifest.json').read_text())['source_hashes']
assert all(sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program)
d=json.loads((S/'failure-dispositions.json').read_text())
with (H/'navigation-before.json').open('x') as f:json.dump(dict(program=old,dispositions=d),f,indent=2)
originals={r['original_row']['id']:r['original_row'] for r in json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())['rows']}
assert len(d['rows'])==61
for ident,comparison in {
 'SIM-F061':'Currency scaling changes a raw mixed-unit residual compromise; scaling monetary normalizer consistently restores minimizer1/2 under exact square completion.',
 'SIM-F062':'Native borrowing20 carries across a one-day2027 stub and pays22 inJanuary. Opening cash3 leaves1; cash1 stops principal with shortfall1 and debt20 preserved. Balanced debt-erasure tampering refuses.',
 'SIM-F063':'Hash-verified original histories all fit imposed interest5 while future interest differs5/7/6. Reconstruction fit is not empirical forecast validation; no probability inferred.',
 'SIM-F064':'Declared uniform cash has mean89 and breach.7; endpoint law has mean89 and breach.5. Midpoint and strict/inclusive boundary cases retain queried event meaning.',
 'SIM-F065':'Successful mass.7 and unresolved.3 retain contribution62, conditional mean620/7, breach bounds[.1,.4] and conditional cash-range mean bounds[62,92]. Omission/false unknown values refuse.'
}.items():
 assert not any(r['id']==ident for r in d['rows'])
 d['rows'].append(dict(id=ident,original_row=originals[ident],disposition='original_units_horizon_evaluation_discriminator',comparison=comparison,evidence=[rel(H/'attempt-01/verification.json'),rel(H/'result.md')],next_action='Actual contract schedules, admitted laws and broader interaction/evaluation remain open; these conditional cases are not empirical forecasting or whole-company acceptance.',original_status_unchanged=True,broad_package_closed=False))
d['rows'].sort(key=lambda r:r['id']);d['reviewed_rows']=66
d['scope']='66 original rows individually reviewed;135 outside this continuation. Original criteria/statuses persist; scoped exact examples are not broad closure.'
for r in d['rows']:assert r['original_row']==originals[r['id']]
dump(S/'failure-dispositions.json',d)
lines=['# Current original failure dispositions','','28 October2026. 66 original rows reviewed;135 outside this pass. All201 original rows/statuses persist. Coverage is not closure.','','| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines+=['| '+r['id']+' | '+r['comparison']+' | '+r['next_action']+' |' for r in d['rows']]
(S/'failure-dispositions.md').write_text('\n'.join(lines)+'\n')
for t in program['tasks']:
 if t['id']=='C04':
  t['evidence'].append(rel(H/'result.md'));t['next_action']='66 original failures reviewed;135 outside this pass. Continue module interaction and model-family coverage cases, connected source research and ordered reading from355.'
  t['remaining']=[x for x in t['remaining'] if not x.startswith('61 original rows')]
  t['remaining'].append('66 original rows individually compared;135 outside this pass. Actual terms/laws, complete module interactions, model-family coverage and independent evaluation remain open.')
for a,b in zip(old['tasks'],program['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']:assert a[key]==b[key]
dump(p,program)
entry='''
## Units, terminal obligations and evaluation — 28 October2026

SIM-F061–065 pass194 checks across eight native programs and four carry
tamper controls. Unit normalization preserves targets; year-end borrowing20
retains repayment22. Historical reconciliation, threshold probability and
conditional successful execution remain different evidence. Result:
company-state-units-horizon-evaluation-20261028/result.md under data/accounting-master.
Actual terms/laws and broader interactions remain open; no E3 forecast occurs.

66 original failures reviewed;135 outside this pass. Main reading354/831,
resume355. Original criteria/statuses/releases persist;E3 deferred.
Continue module interaction/model-family cases, source research and ordered review.

'''
for name in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/name;title,rest=p.read_text().split('\n',1);p.write_text(title+'\n'+entry+rest)
checkpoint=S/'checkpoint.md';(H/'checkpoint-before.md').write_bytes(checkpoint.read_bytes())
checkpoint.write_text('# Construction continuation checkpoint\n'+entry+'''Live program: data/accounting-master/unified-program-20261028/program.json.
40 tasks,114 acceptance rows,156 clauses,18 packages,201 original failures.
T01 definition complete; construction/research/acceptance remain incomplete.
S1–S5 partial,S6 held,E3 deferred. Selected5.55-R1/provisional5.56-D1 not_ready.
Main reading354/831;resume355. No global continuation veto.

Next: inspect SIM-F066 refinancing interactions and stale tax/ownership
dependencies, then SIM-F067 omitted guarantees/covenants/behavior. Match actual
retained modules before designing a test; a cache checksum alone cannot close
the complete interaction case. Continue ordered main reading from355.
Continue independent source research and ordered review. Do not rerun completed
one-shot refresh scripts. Concurrent research edits remain separately owned.
Prior checkpoint: company-state-units-horizon-evaluation-20261028/checkpoint-before.md.
''')
for name,key in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/name;data=json.loads(p.read_text())
 data[key]['units_horizon_evaluation_continuation_20261028']=dict(result=rel(H/'result.md'),checks=194,native_programs=8,carry_tamper_controls=4,reviewed_original_failures=66,outside_pass=135,scope='Exact unit/horizon/evaluation cases; no empirical forecast or actual admission')
 dump(p,data)
print(json.dumps(dict(reviewed=66,outside_pass=135,source_hashes_verified=len(hashes),task_statuses_preserved=True)))
