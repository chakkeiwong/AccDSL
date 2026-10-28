"""Append exact nonanticipativity dispositions and retain the support-loss gap."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
import json,subprocess
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;S=ROOT/'data/accounting-master/construction-continuation-20261028'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
def rel(p):return str(p.relative_to(ROOT))
assert json.loads((H/'attempt-01/verification.json').read_text())['status']=='pass'
assert json.loads((H/'admission-attempt-01/verification.json').read_text())['status']=='pass'
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program)
f=S/'failure-dispositions.json';d=json.loads(f.read_text())
with (H/'navigation-before.json').open('x') as out:json.dump(dict(program=old,dispositions=d),out,indent=2);out.write(chr(10))
original=json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text());by={x['original_row']['id']:x['original_row'] for x in original['rows']}
for ident in ['SIM-F012','LIT-F004']:
 assert not any(x['id']==ident for x in d['rows'])
 d['rows'].append(dict(id=ident,original_row=by[ident],disposition='exact_scoped_information_timing_discriminator',
 comparison='Future demand changed with current information fixed: hidden/late exact-match policy set is empty; early information changes the problem. Viable overstock and independent targets preserve common first actions. Full native/oracle/hand sets agree across18 cases.',
 evidence=[rel(H/'attempt-01/verification.json'),rel(H/'admission-attempt-01/verification.json'),rel(H/'result.md')],
 next_action='Actual actor/source admission and broader policies remain open. Use externally bound complete requests; raw observable-cell coverage does not establish all hidden world/action rows.',original_status_unchanged=True,broad_package_closed=False))
d['rows'].sort(key=lambda x:x['id']);d['reviewed_rows']=len(d['rows']);assert len(d['rows'])==17
d['scope']='Seventeen original rows individually reviewed;184 outside this continuation. Scoped finite tests and admission guard do not close general actor/source or engine enforcement.'
for x in d['rows']:assert x['original_row']==by[x['id']]
dump(f,d)
lines=['# Current original failure dispositions','','28 October2026. Seventeen original rows reviewed;184 outside this pass. All201 original rows/statuses persist. Coverage is not closure.','','| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines+=['| '+x['id']+' | '+x['comparison']+' | '+x['next_action']+' |' for x in d['rows']]
(S/'failure-dispositions.md').write_text(chr(10).join(lines)+chr(10))
gap=dict(id='NEW-FUTURE-POLICY-SUPPORT-20261028',failure='Bare policy solver can admit a false-feasible policy after a hidden-world refusal row is removed',
 witness=rel(H/'admission-attempt-01/missing-refusal-witness.json'),repair=rel(H/'bound_request.py'),
 status='Scoped bound adapter verified; raw/general callers still require external complete-support admission',
 next_action='Bind caller-owned full request identities at supported owner entrypoints; preserve unknown-world scope and prove coverage separately',original201_rows_unchanged=True)
dump(H/'new-gap.json',gap)
for t in program['tasks']:
 if t['id']=='C04':
  t['evidence'].extend([rel(H/'result.md'),rel(H/'new-gap.json')]);t['next_action']='Seventeen original rows reviewed;184 outside this pass. Continue exact failures and bind complete policy input support at supported caller entrypoints; real actor admission/general scope remain open.'
  t['remaining'].append('New support-loss gap: bare observable-cell action coverage can miss a hidden-world refusal; scoped external-identity adapter verified, broader callers not yet audited')
for a,b in zip(old['tasks'],program['tasks']):
 for k in ['id','status','depends_on','completion_criterion','requirements']:assert a[k]==b[k]
dump(p,program)
entry='''
## Future information and finite-policy admission — 28 October2026

SIM-F012/LIT-F004 pass79 checks across18 full-set native/oracle/hand cases.
A later missing-refusal probe exposes false feasibility at the bare input
boundary. BoundFinitePolicyRequest/1 now preserves all18 cases and rejects12
altered requests under69 checks, using an externally held complete-request
identity. Native code stays unchanged; real-source and general caller
admission remain open. Result: company-state-future-demand-failures-20261028/result.md
under data/accounting-master. The new support-loss gap is retained separately.

Seventeen original failure rows reviewed;184 outside this pass. Original201
rows/statuses and40 task criteria persist. Main reading300/831, resume301;
S06/S02 and C04 remain in_progress. Releases not_ready; E3 deferred.
Continue independent ready work; no global continuation veto.

'''
for n in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/construction-continuation-20261028/checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/n;title,rest=p.read_text().split(chr(10),1);p.write_text(title+chr(10)+entry+rest)
for n,k in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/n;d=json.loads(p.read_text());d[k]['future_demand_continuation_20261028']=dict(result=rel(H/'result.md'),reviewed_original_failures=17,outside_pass=184,original_rows=201,policy_checks=79,admission_checks=69,scope='External complete-input identity required; no general admission');dump(p,d)
print(json.dumps(dict(reviewed=17,outside_pass=184,policy_checks=79,admission_checks=69,original_statuses_preserved=True)))

