"""Record original face/proceeds evidence without changing acceptance criteria."""
from copy import deepcopy
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3]; H=Path(__file__).resolve().parent
S=ROOT/'data/accounting-master/construction-continuation-20261028'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
def rel(p):return str(p.relative_to(ROOT))
v=json.loads((H/'attempt-02/verification.json').read_text()); assert v['status']=='pass'
p=ROOT/'data/accounting-master/unified-program-20261028/program.json'; program=json.loads(p.read_text()); before=deepcopy(program)
f=S/'failure-dispositions.json'; d=json.loads(f.read_text())
with (H/'navigation-before.json').open('x') as out:json.dump(dict(program=program,dispositions=d),out,indent=2)
original=json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text()); by={x['original_row']['id']:x['original_row'] for x in original['rows']}
assert not any(x['id']=='SIM-F021' for x in d['rows'])
d['rows'].append(dict(id='SIM-F021',original_row=by['SIM-F021'],disposition='exact_original_scoped_native_recording_and_pricing_oracle',comparison='Face100/default1/10/recovery40/gross21/20 yields proceeds1880/21. Native issue records proceeds and face separately; three inconsistent quote inputs refuse. A self-consistent wrong quote passes native identity but fails the independent lender law by11.',evidence=[rel(H/'attempt-02/verification.json'),rel(H/'result.md')],next_action='Bind justified pricing measure, payoffs, dates and actual offers at an appropriate T07 caller; supplied quote arithmetic does not establish market pricing.',original_status_unchanged=True,broad_package_closed=False))
d['rows'].sort(key=lambda x:x['id']);d['reviewed_rows']=len(d['rows']);assert len(d['rows'])==18
d['scope']='Eighteen original rows individually reviewed;183 outside this continuation. Scoped recording and synthetic pricing do not establish market or source admission.'
for x in d['rows']:assert x['original_row']==by[x['id']]
dump(f,d)
lines=['# Current original failure dispositions','','28 October2026. Eighteen original rows reviewed;183 outside this pass. All201 original rows/statuses persist. Coverage is not closure.','','| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines+=['| '+x['id']+' | '+x['comparison']+' | '+x['next_action']+' |' for x in d['rows']]
(S/'failure-dispositions.md').write_text(chr(10).join(lines)+chr(10))
for t in program['tasks']:
 if t['id']=='C04':
  t['evidence'].append(rel(H/'result.md'));t['next_action']='Eighteen original rows reviewed;183 outside this pass. Continue exact source/context/revision and signal-dependence failures; real actor/source admission remains open.'
 if t['id']=='T07':
  t['evidence'].append(rel(H/'result.md'));t['remaining'].append('SIM-F021 native recording preserves face versus cash; supplied quote identity cannot enforce a creditor pricing law. Bind justified measure/payoff/date/offer inputs after survey prerequisites.')
for a,b in zip(before['tasks'],program['tasks']):
 for k in ['id','status','depends_on','completion_criterion','requirements']:assert a[k]==b[k]
dump(p,program)
entry='''
## Face, proceeds and pricing scope — 28 October2026

SIM-F021 passes198 checks across13 native cases. Face100 with default1/10,
recovery40 and gross return21/20 yields proceeds1880/21, stored separately
from face. Inconsistent supplied quotes refuse; a self-consistent wrong quote
still requires the independent lender-law check. This is the native method's
explicit conditional-input limit, not admitted pricing. T07 remains planned.
Result: company-state-face-proceeds-failure-20261028/result.md under
data/accounting-master. Failed harness attempt01 is retained; attempt02 passes.

Eighteen original rows reviewed;183 outside this pass. All201 original rows,
40 task criteria/dependencies and frozen releases persist. Main reading300/831,
resume301; source/survey/construction/review work remains. E3 stays deferred.
Continue ready work; no global continuation veto.

'''
for n in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/construction-continuation-20261028/checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/n;title,rest=p.read_text().split(chr(10),1);p.write_text(title+chr(10)+entry+rest)
for n,k in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/n;d=json.loads(p.read_text());d[k]['face_proceeds_continuation_20261028']=dict(result=rel(H/'result.md'),checks=v['checks'],cases=v['cases'],reviewed_original_failures=18,outside_pass=183,scope='Native recording plus independent synthetic pricing law; no market admission');dump(p,d)
print(json.dumps(dict(reviewed=18,outside_pass=183,statuses_preserved=True)))

