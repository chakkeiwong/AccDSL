"""Record exact source failures and a status-preserving consumer; keep criteria."""
from copy import deepcopy
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;S=ROOT/'data/accounting-master/construction-continuation-20261028'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
def rel(p):return str(p.relative_to(ROOT))
for a in ['attempt-02','consumer-attempt-01']:assert json.loads((H/a/'verification.json').read_text())['status']=='pass'
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program)
f=S/'failure-dispositions.json';d=json.loads(f.read_text())
with (H/'navigation-before.json').open('x') as out:json.dump(dict(program=old,dispositions=d),out,indent=2)
by={r['original_row']['id']:r['original_row'] for r in json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())['rows']}
items={
'SIM-F003':('Correction published220 is excluded at219; public/system/actor clocks remain distinct. Future amount changes preserve earlier assertions and full native history.','Actual publication, ingestion and actor receipt still need source-specific evidence.'),
'SIM-F015':('Two providers carrying one disclosure retain both provenance identities, same hard constraints/history and no invented probability. Noisy evidence refuses; cross-provider supersession requires explicit links.','General signal lineage and a reviewed dependent-likelihood model remain open; hard intersection is not Bayesian deduplication.'),
'SIM-F016':('Held9 conflicts with every retained history in domain[3,8]; source/domain are retained without definition or fallback witness. Conflict-aware decision view carries outcome with observable assertions.','Distinguish source error from omitted model families; actual source admission and general policy integration remain open.')}
for ident,(comparison,next_action) in items.items():
 assert not any(r['id']==ident for r in d['rows'])
 d['rows'].append(dict(id=ident,original_row=by[ident],disposition='exact_original_scoped_source_and_native_history_evidence',comparison=comparison,evidence=[rel(H/'attempt-02/verification.json'),rel(H/'consumer-attempt-01/verification.json'),rel(H/'result.md')],next_action=next_action,original_status_unchanged=True,broad_package_closed=False))
d['rows'].sort(key=lambda r:r['id']);d['reviewed_rows']=len(d['rows']);assert len(d['rows'])==21
d['scope']='Twenty-one original rows individually reviewed;180 outside this continuation. Synthetic source views and finite native outcomes do not establish actual source, probability or actor admission.'
for r in d['rows']:assert r['original_row']==by[r['id']]
dump(f,d)
lines=['# Current original failure dispositions','','28 October2026. Twenty-one original rows reviewed;180 outside this pass. All201 original rows/statuses persist. Coverage is not closure.','','| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines+=['| '+r['id']+' | '+r['comparison']+' | '+r['next_action']+' |' for r in d['rows']];(S/'failure-dispositions.md').write_text(chr(10).join(lines)+chr(10))
for t in program['tasks']:
 if t['id'] in ['C04','T03','T08']:t['evidence'].append(rel(H/'result.md'))
 if t['id']=='C04':t['next_action']='Twenty-one original failures reviewed;180 outside this pass. Continue exact context/extraction, persistent-type, causal and joint-stress discriminators; retain source and consumer scope.'
 if t['id']=='T03':t['remaining'].append('Late-correction/source-duplication cases and conflict-aware consumer pass, but actual byte availability, provider lineage and actor receipt remain unadmitted.')
for a,b in zip(old['tasks'],program['tasks']):
 for k in ['id','status','depends_on','completion_criterion','requirements']:assert a[k]==b[k]
dump(p,program)
dump(H/'consumer-gap.json',dict(id='NEW-DETACHED-CONFLICT-STATUS-20261028',finding='Old policy_evidence subrecord omitted the full result conflict status',status='Additive conflict-aware consumer verified; no existing production caller found in scoped search',repair=rel(H/'decision_view.py'),scope='Preserves observable conflicting assertions with explicit unexecutable status; no source truth or actor admission',original201_rows_unchanged=True))
entry='''
## Original source failures and conflict-aware consumer — 28 October2026

SIM-F003/015/016 pass255 checks across22 cases and15 full history replays.
Late corrections preserve earlier knowledge; duplicate providers retain source
identity without invented probabilities; all-history contradiction stays a
conflict. A separate consumer passes315 checks, retaining all22 native results
and carrying conflict status with observable assertions. No actual source or
actor admission follows. Result: company-state-evidence-failures-20261028/result.md
under data/accounting-master.

Twenty-one original rows reviewed;180 outside this pass. All201 inherited rows,
40 task criteria/dependencies and frozen releases persist. Main reading300/831,
resume301; surveys, construction and release review remain incomplete. E3 deferred.
Continue ready work; no global continuation veto.

'''
for n in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/construction-continuation-20261028/checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/n;title,rest=p.read_text().split(chr(10),1);p.write_text(title+chr(10)+entry+rest)
for n,k in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/n;d=json.loads(p.read_text());d[k]['source_failure_continuation_20261028']=dict(result=rel(H/'result.md'),checks=255,cases=22,consumer_checks=315,reviewed_original_failures=21,outside_pass=180,scope='Conditional source/history evidence and conflict-aware consumer; no actual admission');dump(p,d)
print(json.dumps(dict(reviewed=21,outside_pass=180,statuses_preserved=True)))

