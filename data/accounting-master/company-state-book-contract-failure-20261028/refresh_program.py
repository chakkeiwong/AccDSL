"""One-shot book-to-contract evidence refresh; preserve original requirements."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
S=ROOT/'data/accounting-master/construction-continuation-20261028'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
def rel(p):return str(p.relative_to(ROOT))
v=json.loads((H/'attempt-01/verification.json').read_text());assert v['status']=='pass' and v['checks']==109
hashes=json.loads((H/'attempt-01/run-manifest.json').read_text())['source_hashes']
assert all(sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program)
f=S/'failure-dispositions.json';d=json.loads(f.read_text())
with (H/'navigation-before.json').open('x') as out:json.dump(dict(program=old,dispositions=d),out,indent=2)
originals={r['original_row']['id']:r['original_row'] for r in json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())['rows']}
assert len(d['rows'])==27 and not any(r['id']=='SIM-F026' for r in d['rows'])
d['rows'].append(dict(id='SIM-F026',original_row=originals['SIM-F026'],disposition='exact_original_scoped_book_contract_discriminator',comparison='Finite supplied book100 bridge retains face100/discount0 and face110/discount10 until evidence selects. Two native account maps report identical books but retain different promises. Under supplied gross21/20, face110 values at2200/21; book-as-face is wrong by200/21.',evidence=[rel(H/'attempt-01/verification.json'),rel(H/'result.md')],next_action='Inspect supported issuer principal/carrying/adjustment evidence. Real source, contract population and measurement admission remain open; no native amortization or repayment inferred.',original_status_unchanged=True,broad_package_closed=False))
d['rows'].sort(key=lambda r:r['id']);d['reviewed_rows']=len(d['rows'])
d['scope']='Twenty-eight original rows individually reviewed;173 outside this continuation. Original criteria/statuses persist; scoped evidence is not whole-company closure.'
for r in d['rows']:assert r['original_row']==originals[r['id']]
dump(f,d)
lines=['# Current original failure dispositions','','28 October2026. Twenty-eight original rows reviewed;173 outside this pass. All201 original rows/statuses persist. Coverage is not closure.','','| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines+=['| '+r['id']+' | '+r['comparison']+' | '+r['next_action']+' |' for r in d['rows']]
(S/'failure-dispositions.md').write_text(chr(10).join(lines)+chr(10))
for t in program['tasks']:
 if t['id']=='C04':
  t['evidence'].append(rel(H/'result.md'))
  t['next_action']='Twenty-eight original failures reviewed;173 outside this pass. Continue supported issuer principal/carrying/adjustment mapping with T03, remaining original failures, and ordered reading from337.'
  t['remaining']=[x for x in t['remaining'] if not x.startswith('Twenty-seven original rows')]
  t['remaining'].append('Twenty-eight original rows have individual current comparisons;173 remain outside this continuation. Real source/contract/recognition and arbitrary method completeness remain open.')
 if t['id']=='T03':
  t['evidence'].append(rel(H/'result.md'))
  t['next_action']='Existing Apple Note9 principal/carrying/adjustment aggregates are already typed. Inspect retained instrument/exhibit evidence for supported contractual links and preserve residual population, adjustment allocation, source timing and actor-access unknowns.'
for a,b in zip(old['tasks'],program['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']:assert a[key]==b[key]
dump(p,program)
entry='''
## Book debt and contractual promise — 28 October2026

SIM-F026 passes109 exact checks across21 solver and6 native report cases.
Book100 retains face100/discount0 or face110/discount10 in the supplied finite
bridge. With gross21/20, face110 values at2200/21; substituting book as promise
misprices by200/21. Native reports preserve different contract memory behind
identical statements. Result: company-state-book-contract-failure-20261028/result.md
under data/accounting-master. No actual contract or native repayment admission.

Twenty-eight original rows reviewed;173 outside this pass. Main reading336/831,
resume337. Original criteria/statuses and releases persist. E3 deferred.
Continue T03 issuer principal/carrying/adjustment mapping and independent ready work.

'''
for name in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/construction-continuation-20261028/checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/name;title,rest=p.read_text().split(chr(10),1);p.write_text(title+chr(10)+entry+rest)
for name,key in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/name;d=json.loads(p.read_text());d[key]['book_contract_continuation_20261028']=dict(result=rel(H/'result.md'),checks=109,solver_cases=21,native_report_cases=6,reviewed_original_failures=28,outside_pass=173,scope='Explicit finite measurement bridge and native reports; no real-source, pricing or repayment admission');dump(p,d)
print(json.dumps(dict(reviewed=28,outside_pass=173,source_hashes_verified=len(hashes),task_statuses_preserved=True)))

