"""Record original context evidence and refresh stale next-action references."""
from copy import deepcopy
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;S=ROOT/'data/accounting-master/construction-continuation-20261028'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
def rel(p):return str(p.relative_to(ROOT))
assert json.loads((H/'attempt-02/verification.json').read_text())['status']=='pass'
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program)
f=S/'failure-dispositions.json';d=json.loads(f.read_text())
with (H/'navigation-before.json').open('x') as out:json.dump(dict(program=old,dispositions=d),out,indent=2)
by={r['original_row']['id']:r['original_row'] for r in json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())['rows']}
assert not any(r['id']=='SIM-F001' for r in d['rows'])
d['rows'].append(dict(id='SIM-F001',original_row=by['SIM-F001'],disposition='exact_original_scoped_context_discriminator',comparison='Eight actual repeated concept occurrences preserve dates, units and dimensions. Existing native context/temporal code refuses wrong unit/currency/scale/sign/date/period; selected total duplicates retain provenance without addition.',evidence=[rel(H/'attempt-02/verification.json'),rel(H/'result.md')],next_action='General ambiguity-preserving extraction and source-to-quantity/contract admission remain open; the selected historical card is not a general extractor.',original_status_unchanged=True,broad_package_closed=False))
d['rows'].sort(key=lambda r:r['id']);d['reviewed_rows']=len(d['rows']);assert len(d['rows'])==22
d['scope']='Twenty-two original rows individually reviewed;179 outside this continuation. Scoped context/source/native checks do not close whole-company or general extraction obligations.'
for r in d['rows']:assert r['original_row']==by[r['id']]
dump(f,d)
lines=['# Current original failure dispositions','','28 October2026. Twenty-two original rows reviewed;179 outside this pass. All201 original rows/statuses persist. Coverage is not closure.','','| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines+=['| '+r['id']+' | '+r['comparison']+' | '+r['next_action']+' |' for r in d['rows']];(S/'failure-dispositions.md').write_text(chr(10).join(lines)+chr(10))
for t in program['tasks']:
 if t['id'] in ['C04','T03']:t['evidence'].append(rel(H/'result.md'))
 if t['id']=='C04':t['next_action']='Twenty-two original failures reviewed;179 outside this pass. Continue exact persistent-type, causal, joint-stress and remaining source-contract discriminators; retain explicit runtime/source scope.'
 if t['id']=='T05':t['next_action']='After T01/S07 prerequisites, reuse the current27-profile owner review and16 compatibility edges, including the five-profile sector annex; develop source-backed same-basis joins with explicit economic and memory ownership.'
 if t['id']=='S09':
  t['next_action']='Reconcile retained Arelle/ACTUS/QuantLib/Z3 and official-method audits before new reading. ACTUS fixture arithmetic is already checked; matched core/version/runtime admission remains open. Do not repeat that fixture arithmetic as external runtime evidence.'
  t['evidence'].append('data/accounting-master/literature-closure-20261026/software-audit.md')
  t['remaining']=['Current connected comparative synthesis, exact version/dependency/terms boundaries and source-specific omissions; existing static or arithmetic evidence does not establish runtime reuse.']
for a,b in zip(old['tasks'],program['tasks']):
 for k in ['id','status','depends_on','completion_criterion','requirements']:assert a[k]==b[k]
dump(p,program)
entry='''
## Repeated source contexts and phase refresh — 28 October2026

SIM-F001 passes51 checks across8 retained repeated-concept occurrences and20
native results. Dates, units, scale, sign and dimensional scope stay distinct;
selected duplicate totals keep both provenance pointers without double counting.
The failed generic-error-code expectation is retained and repaired. Result:
company-state-context-failure-20261028/result.md under data/accounting-master.

T05 next action now names the current27-profile owner review, replacing a stale
18-profile reference. S09 now reuses the retained official-code audit and retains
ACTUS matched-runtime limitations. No criterion, dependency or status changes.
Twenty-two original failure rows reviewed;179 outside this pass. Main reading
300/831, resume301. Releases remain not_ready; E3 deferred. Continue ready work.

'''
for n in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/construction-continuation-20261028/checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/n;title,rest=p.read_text().split(chr(10),1);p.write_text(title+chr(10)+entry+rest)
for n,k in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/n;d=json.loads(p.read_text());d[k]['context_failure_continuation_20261028']=dict(result=rel(H/'result.md'),checks=51,reviewed_original_failures=22,outside_pass=179,scope='Retained source context and native refusal evidence; no general extraction admission');dump(p,d)
print(json.dumps(dict(reviewed=22,outside_pass=179,statuses_preserved=True,refreshed_actions=['T05','S09'])))

