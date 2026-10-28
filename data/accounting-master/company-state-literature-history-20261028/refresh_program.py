"""One-shot literature history reconciliation; preserve original acceptance."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
S=ROOT/'data/accounting-master/construction-continuation-20261028'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
def rel(p):return str(p.relative_to(ROOT))
v=json.loads((H/'attempt-01/verification.json').read_text());assert v['passed'] and v['checks']==316
hashes=json.loads((H/'attempt-01/source-hashes.json').read_text())
assert all(sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program)
d=json.loads((S/'failure-dispositions.json').read_text());assert len(d['rows'])==71
with (H/'navigation-before.json').open('x') as f:json.dump(dict(program=old,dispositions=d),f,indent=2)
originals={r['original_row']['id']:r['original_row'] for r in json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())['rows']}
comparisons={
 'LIT-F001':('Exact saved fixed/floating/interior histories share debt100 and historical interest5 but retain different futures; full nonjournal terms persist.','Source-backed real-company construction and population completeness remain open.'),
 'LIT-F002':('Separate support-bound authored weights retain provenance. Correct duplicate splitting preserves the full law and mean80; equal syntax weights give260/3. Absent measures stay unweighted.','Provenance labels do not justify an issuer prior; broader measure semantics remain open.'),
 'LIT-F003':('Explicit prospective amendment changes coupon5 to7 with revision1, leaves prior records unchanged and final cash8 rather than10. Date/approval/revision controls and scoped carry-policy validation refuse silent changes.','Actual modification accounting, authenticated histories and general nonrectangular control remain open; generic carry can accept declared resets.'),
 'LIT-F005':('Saved complete joint successor/observation/output laws distinguish equal marginals with policy values7/10 and-1/2; exact full-path oracle reused.','Large-state runtime, actual observation/transition laws and broad integration remain open.')}
for ident,(comparison,next_action) in comparisons.items():
 assert not any(r['id']==ident for r in d['rows'])
 d['rows'].append(dict(id=ident,original_row=originals[ident],disposition='original_literature_history_measure_discriminator',comparison=comparison,evidence=[rel(H/'attempt-01/verification.json'),rel(H/'result.md')],next_action=next_action,original_status_unchanged=True,broad_package_closed=False))
d['rows'].sort(key=lambda r:r['id']);d['reviewed_rows']=75
d['scope']='75 original rows individually reviewed;126 outside this continuation. Original criteria/statuses persist; scoped exact examples are not broad closure.'
for r in d['rows']:assert r['original_row']==originals[r['id']]
dump(S/'failure-dispositions.json',d)
lines=['# Current original failure dispositions','','28 October2026. 75 original rows reviewed;126 outside this pass. All201 original rows/statuses persist. Coverage is not closure.','','| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines+=['| '+r['id']+' | '+r['comparison']+' | '+r['next_action']+' |' for r in d['rows']]
(S/'failure-dispositions.md').write_text(chr(10).join(lines)+chr(10))
for t in program['tasks']:
 if t['id']=='C04':
  t['evidence'].append(rel(H/'result.md'));t['next_action']='75 original failures reviewed;126 outside this pass. Audit LIT-F006–009 discrete actions, boundary error, policy transfer and sampled information against original evidence; continue sources and ordered reading361.'
  t['remaining']=[x for x in t['remaining'] if not x.startswith('71 original rows')]
  t['remaining'].append('75 original rows individually compared;126 outside this pass. Actual amendment/measure premises, remaining literature cases, source-backed construction and independent evaluation remain open.')
for a,b in zip(old['tasks'],program['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']:assert a[key]==b[key]
dump(p,program)
entry='''
## Literature histories and explicit amendment — 28 October2026

LIT-F001/002/003/005 pass316 checks with14 saved native results,18 refusal
controls and three separate authored measures. A dated amendment preserves the
prior year and changes final cash10 to8; generic carry and provenance limits
remain explicit. Four retained units are reused by content and source hashes.
Result: company-state-literature-history-20261028/result.md under data/accounting-master.

75 original failures reviewed;126 outside this pass. Main reading360/831,
resume361. Original criteria/statuses/releases persist;E3 deferred.
Continue discrete-action/policy-information cases, sources and ordered review.

'''
for name in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/name;title,rest=p.read_text().split(chr(10),1);p.write_text(title+chr(10)+entry+rest)
checkpoint=S/'checkpoint.md';(H/'checkpoint-before.md').write_bytes(checkpoint.read_bytes())
checkpoint.write_text('# Construction continuation checkpoint'+chr(10)+entry+'''Live program: data/accounting-master/unified-program-20261028/program.json.
40 tasks,114 acceptance rows,156 clauses,18 packages,201 original failures.
T01 definition complete; construction/research/acceptance remain incomplete.
S1–S5 partial,S6 held,E3 deferred. Selected5.55-R1/provisional5.56-D1 not_ready.
No global continuation veto. Main review360/831;next361.

Next: inspect LIT-F006–009 exact requirements and retained source evidence.
Continuous action relaxation, boundary default errors, common-policy transfer
and empirical future leakage need separate discriminators. Continue connected
sources and ordered reading361. READ-0358-0360-01 remains for successor repair
after diagnosis. Do not rerun completed one-shot scripts; concurrent edits stay
separate. Prior checkpoint is in this unit/checkpoint-before.md.
''')
for name,key in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/name;data=json.loads(p.read_text());data[key]['literature_history_continuation_20261028']=dict(result=rel(H/'result.md'),checks=316,native_programs=14,refusal_controls=18,separate_measures=3,reviewed_original_failures=75,outside_pass=126,scope='Finite amendment and measure representation; retained joint-history/kernel evidence; no source or accounting admission');dump(p,data)
print(json.dumps(dict(reviewed=75,outside_pass=126,source_hashes_verified=len(hashes),task_statuses_preserved=True)))
