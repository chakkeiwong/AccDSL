"""One-shot, original-population-preserving SIM-F006 navigation update."""
from copy import deepcopy
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
S=ROOT/'data/accounting-master/construction-continuation-20261028'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
def rel(p):return str(p.relative_to(ROOT))
assert json.loads((H/'attempt-01/verification.json').read_text())['status']=='pass'
hashes=json.loads((H/'attempt-01/run-manifest.json').read_text())['source_hashes']
assert all(sha256((ROOT/p).read_bytes()).hexdigest()==v for p,v in hashes.items())
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program)
f=S/'failure-dispositions.json';d=json.loads(f.read_text())
with (H/'navigation-before.json').open('x') as out:json.dump(dict(program=old,dispositions=d),out,indent=2)
by={r['original_row']['id']:r['original_row'] for r in json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())['rows']}
assert not any(r['id']=='SIM-F006' for r in d['rows'])
d['rows'].append(dict(id='SIM-F006',original_row=by['SIM-F006'],disposition='exact_original_scoped_declared_history_discriminator',comparison='Both original gross equity histories execute with equal net cash60/shares20, distinct gross flows and complete native states/reports. A separately authored synthetic retirement method reuses unchanged typed execution. Missing share write is detected independently.',evidence=[rel(H/'attempt-01/verification.json'),rel(H/'result.md')],next_action='General repurchase rights, accounting treatment and source/history admission remain open; retain nonmonetary update checks beyond balanced statements.',original_status_unchanged=True,broad_package_closed=False))
d['rows'].sort(key=lambda r:r['id']);d['reviewed_rows']=len(d['rows']);assert len(d['rows'])==23
d['scope']='Twenty-three original rows individually reviewed;178 outside this continuation. Original criteria/statuses persist; scoped evidence is not whole-company closure.'
for r in d['rows']:assert r['original_row']==by[r['id']]
dump(f,d)
lines=['# Current original failure dispositions','','28 October2026. Twenty-three original rows reviewed;178 outside this pass. All201 original rows/statuses persist. Coverage is not closure.','','| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines+=['| '+r['id']+' | '+r['comparison']+' | '+r['next_action']+' |' for r in d['rows']]
(S/'failure-dispositions.md').write_text(chr(10).join(lines)+chr(10))
for t in program['tasks']:
 if t['id']=='C04':
  t['evidence'].append(rel(H/'result.md'))
  t['next_action']='Twenty-three original failures reviewed;178 outside this pass. Audit exact two-year persistent-type and shock/reset discriminators next; retain original runtime/source scope and separate gross equity history evidence.'
  t['remaining']=[x for x in t['remaining'] if not x.startswith('Eight original failure rows')]
  t['remaining'].append('Twenty-three original rows have individual current comparisons;178 remain outside this continuation. No count-based closure; operation-specific nonmonetary checks remain necessary.')
for a,b in zip(old['tasks'],program['tasks']):
 for k in ['id','status','depends_on','completion_criterion','requirements']:assert a[k]==b[k]
dump(p,program)
entry='''
## Gross equity histories and current-count repair — 28 October2026

SIM-F006 passes197 checks across15 native executions and11 finite-note cases.
Issue20 at3 and issue30 at4 followed by retirement10 at6 preserve equal net
cash/shares and distinct gross histories. A separate synthetic retirement
method uses unchanged typed execution. Balanced statements miss a deleted
share-memory update; the independent share oracle detects it. Result:
company-state-gross-equity-history-20261028/result.md under data/accounting-master.

Twenty-three original rows reviewed;178 outside this pass. C04's stale eight-row
remaining field is repaired. All40 criteria/dependencies/statuses and original
failure records persist. Main reading312/831, resume313. Releases not_ready;
E3 deferred. Continue persistent-type/reset and independent ready work.

'''
for n in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/construction-continuation-20261028/checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/n;title,rest=p.read_text().split(chr(10),1);p.write_text(title+chr(10)+entry+rest)
for n,k in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/n;d=json.loads(p.read_text());d[k]['gross_equity_continuation_20261028']=dict(result=rel(H/'result.md'),checks=197,native_runs=15,note_cases=11,reviewed_original_failures=23,outside_pass=178,scope='Declared synthetic gross histories, not general share-register/source admission');dump(p,d)
print(json.dumps(dict(reviewed=23,outside_pass=178,source_hashes_verified=len(hashes),statuses_preserved=True)))

