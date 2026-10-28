"""Record three exact original equity discriminators without broad closure."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
S=ROOT/'data/accounting-master/construction-continuation-20261028'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def rel(p):return str(p.relative_to(ROOT))
v=json.loads((H/'attempt-02/verification.json').read_text());assert v['status']=='pass' and v['checks']==249
hashes=json.loads((H/'attempt-02/run-manifest.json').read_text())['source_hashes']
assert all(sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program)
f=S/'failure-dispositions.json';d=json.loads(f.read_text())
with (H/'navigation-before.json').open('x') as out:json.dump(dict(program=old,dispositions=d),out,indent=2)
originals={r['original_row']['id']:r['original_row'] for r in json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())['rows']}
assert len(d['rows'])==29
comparisons={
 'SIM-F030':'With100 old and15 new shares, ownership20/23 is identical at issue10 or8. Under explicit assets1000, old value remains1000 at10 but falls600/23 at8; value transfer conserves total.',
 'SIM-F033':'Native typed cap15 and explicit approval/offer/settlement/receipt prerequisites accept14/15, refuse16 and failed/short subscriptions, preserve unknowns and prevent duplicate posting under two account maps. Vacuous receipt rules expose balanced false cash.',
 'SIM-F034':'Book equity10/100 shares gives0.1, distinct from supplied economic assets1000/100=10. Native issue can accept supplied0.1 but does not justify that price; conditional old-value loss is2970/23.'}
for ident,comparison in comparisons.items():
 assert not any(r['id']==ident for r in d['rows'])
 d['rows'].append(dict(id=ident,original_row=originals[ident],disposition='exact_original_scoped_equity_discriminator',comparison=comparison,
  evidence=[rel(H/'attempt-02/verification.json'),rel(H/'result.md')],next_action='Actual share population, rights, authority, receipt provenance and economic valuation remain unadmitted; continue remaining original equity and financing cases.',original_status_unchanged=True,broad_package_closed=False))
d['rows'].sort(key=lambda r:r['id']);d['reviewed_rows']=len(d['rows']);d['scope']='Thirty-two original rows individually reviewed;169 outside this continuation. Original criteria/statuses persist; scoped evidence is not whole-company closure.'
for r in d['rows']:assert r['original_row']==originals[r['id']]
dump(f,d)
lines=['# Current original failure dispositions','','28 October2026. Thirty-two original rows reviewed;169 outside this pass. All201 original rows/statuses persist. Coverage is not closure.','','| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines+=['| '+r['id']+' | '+r['comparison']+' | '+r['next_action']+' |' for r in d['rows']]
(S/'failure-dispositions.md').write_text('\n'.join(lines)+'\n')
for t in program['tasks']:
 if t['id'] in ['C04','T08']:t['evidence'].append(rel(H/'result.md'))
 if t['id']=='C04':
  t['next_action']='Thirty-two original failures reviewed;169 outside this pass. Continue conversion/preference/priority and other remaining original cases, actual source dependencies with T03 and ordered reading from337.'
  t['remaining']=[x for x in t['remaining'] if not x.startswith('Twenty-nine original rows')]
  t['remaining'].append('Thirty-two original rows individually compared;169 outside this pass. Actual rights/source/receipt admission and broad operation completeness remain open.')
for a,b in zip(old['tasks'],program['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']:assert a[key]==b[key]
dump(p,program)
entry='''
## Equity authority, settlement and value — 28 October 2026

SIM-F030/033/034 pass249 checks across37 native cases. Cap15, accepted offer,
approval and receipt prerequisites preserve atomic refusal and unknowns under
two account maps. Equal ownership20/23 at issue10 or8 has different conditional
value consequences; book equity does not determine issue price. Failed harness
attempt01 and its schema-safeguard repair remain retained. Result:
company-state-equity-authorization-20261028/result.md under data/accounting-master.
All real source/rights/receipt/valuation admission remains open.

Thirty-two original failures reviewed;169 outside this pass. Main reading
336/831, resume337. All original criteria/statuses and releases persist.
E3 deferred. Continue conversion/preference/priority, source and ordered review.

'''
for name in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/construction-continuation-20261028/checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/name;title,rest=p.read_text().split('\n',1);p.write_text(title+'\n'+entry+rest)
for name,key in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/name;d=json.loads(p.read_text());d[key]['equity_authorization_continuation_20261028']=dict(result=rel(H/'result.md'),checks=249,native_cases=37,reviewed_original_failures=32,outside_pass=169,scope='Synthetic share authority/receipt and conditional ownership/value; no actual admission');dump(p,d)
print(json.dumps(dict(reviewed=32,outside_pass=169,source_hashes_verified=len(hashes),task_statuses_preserved=True)))
