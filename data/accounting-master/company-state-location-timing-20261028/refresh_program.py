"""Append scoped location/timing evidence; preserve original requirements."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
S=ROOT/'data/accounting-master/construction-continuation-20261028'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def rel(p):return str(p.relative_to(ROOT))
v=json.loads((H/'attempt-03/verification.json').read_text());assert v['status']=='pass' and v['checks']==244
hashes=json.loads((H/'attempt-03/run-manifest.json').read_text())['source_hashes']
assert all(sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program)
d=json.loads((S/'failure-dispositions.json').read_text())
with (H/'navigation-before.json').open('x') as fh:json.dump(dict(program=old,dispositions=d),fh,indent=2)
originals={r['original_row']['id']:r['original_row'] for r in json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())['rows']}
assert len(d['rows'])==40
for ident,comparison in {
 'SIM-F039':'Exact cap10 limits parent cash5 to15 below maturity20 despite group35. Cap15 boundary, cumulative6+6 refusal, unknown permission and matched conditional legal-book legs retained; atomic group execution unclaimed.',
 'SIM-F040':'Native EUR receipt before/after maturity, explicit same-day orders and future-reordering refusal retain intermediate cash needs. Wrong currency/entity types refuse; supplied extra EUR30 cannot be justified by pooled USD cash.'}.items():
 assert not any(r['id']==ident for r in d['rows'])
 d['rows'].append(dict(id=ident,original_row=originals[ident],disposition='original_scoped_entity_currency_timing_discriminator',comparison=comparison,evidence=[rel(H/'attempt-03/verification.json'),rel(H/'result.md')],next_action='Actual entity/transfer/FX authority, cap vintages and atomic linked settlement remain open; conditional feasibility does not establish company insolvency.',original_status_unchanged=True,broad_package_closed=False))
d['rows'].sort(key=lambda r:r['id']);d['reviewed_rows']=len(d['rows']);d['scope']='42 original rows individually reviewed;159 outside this continuation. Original criteria/statuses persist; scope is not whole-company closure.'
for r in d['rows']:assert r['original_row']==originals[r['id']]
dump(S/'failure-dispositions.json',d)
lines=['# Current original failure dispositions','','28 October2026. 42 original rows reviewed;159 outside this pass. All201 original rows/statuses persist. Coverage is not closure.','','| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines+=['| '+r['id']+' | '+r['comparison']+' | '+r['next_action']+' |' for r in d['rows']]
(S/'failure-dispositions.md').write_text('\n'.join(lines)+'\n')
for t in program['tasks']:
 if t['id']=='C04':
  t['evidence'].append(rel(H/'result.md'))
  t['next_action']='42 original failures reviewed;159 outside this pass. Continue loss-vintage/collateral/contractual-clock and information/scenario cases, source dependencies and ordered reading from337.'
  t['remaining']=[x for x in t['remaining'] if not x.startswith('40 original rows')]
  t['remaining'].append('42 original rows individually compared;159 outside this pass. Actual entity/rights/FX/measurement admission, linked settlement and complete operations remain open.')
for a,b in zip(old['tasks'],program['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']:assert a[key]==b[key]
dump(p,program)
entry='''
## Entity cash and settlement timing — 28 October 2026

SIM-F039/040 pass244 checks across34 native programs and seven solver cases.
Parent5 plus capped transfer10 cannot pay20 despite group35; EUR receipts
after maturity cannot fund earlier payments. Cumulative limits, typed context
and explicit same-day order retain their meaning. Result:
company-state-location-timing-20261028/result.md under data/accounting-master.
Actual rights/FX admission and atomic cross-book settlement remain open.

42 original failures reviewed;159 outside this pass. Main reading336/831,
resume337. Original criteria/statuses/releases persist. E3 deferred.
Continue loss-vintage, collateral and contractual-clock cases, sources and review.

'''
for name in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/name;title,rest=p.read_text().split('\n',1);p.write_text(title+'\n'+entry+rest)
checkpoint=S/'checkpoint.md';(H/'checkpoint-before.md').write_bytes(checkpoint.read_bytes())
checkpoint.write_text('# Construction continuation checkpoint\n'+entry+'''Current live program: data/accounting-master/unified-program-20261028/program.json.
40 tasks,114 acceptance rows,156 clauses,18 packages,201 original failures.
T01 definition complete; construction/surveys/acceptance remain incomplete.
S1–S5 partial,S6 held,E3 deferred. Selected5.55-R1/provisional5.56-D1 not_ready.
Main reading336/831;resume337. No global continuation veto.

Next: audit original SIM-F042 loss40 followed by income30,30 or loss10 against
conditional_tax_losses_v1. Preserve loss-lot identity, intervals, eligibility,
unknowns and separate financial measurement. Continue independent sources,
collateral/cure-clock and ordered review. No repeated finished refresh scripts.
Concurrent goal-alignment work remains separate; stage only owned changes.
Prior checkpoint: company-state-location-timing-20261028/checkpoint-before.md.
''')
for name,key in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/name;data=json.loads(p.read_text());data[key]['location_timing_continuation_20261028']=dict(result=rel(H/'result.md'),checks=244,native_cases=34,solver_cases=7,reviewed_original_failures=42,outside_pass=159,scope='Conditional legal-book and exact cash feasibility; no source or atomic group admission');dump(p,data)
print(json.dumps(dict(reviewed=42,outside_pass=159,source_hashes_verified=len(hashes),task_statuses_preserved=True)))
