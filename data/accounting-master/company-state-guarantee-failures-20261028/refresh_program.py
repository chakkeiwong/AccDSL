"""Record scoped guarantee evidence without changing original criteria/statuses."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
STATE=ROOT/'data/accounting-master/construction-continuation-20261028'
original=json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())
by={x['original_row']['id']:x['original_row'] for x in original['rows']}
f=STATE/'failure-dispositions.json';d=json.loads(f.read_text());before=deepcopy(d)
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program)
backup=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    failure_dispositions=before,task_C04=next(x for x in old['tasks'] if x['id']=='C04'))
with (HERE/'navigation-before.json').open('x') as out:json.dump(backup,out,indent=2);out.write('\n')
evidence=[str((HERE/x/'verification.json').relative_to(ROOT)) for x in ['attempt-01','inspection-attempt-01']]
for e in evidence:assert json.loads((ROOT/e).read_text())['status']=='pass'
updates={
 'SIM-F004':('exact_original_scoped_input_inspection',
 'Exact omitted guarantee fields refuse without zero imputation. The separate inspector preserves omitted/null pointers and entire native outcomes; explicit zero stays known. Native null ECL/service inputs remain unsupported.',
 'Connect disclosed unknowns to a declared reconstruction family; the finite inspector neither admits sources nor constructs unknown contracts.'),
 'SIM-F010':('partial_known_unpaid_contract_control',
 'A disclosed external guarantee with no settlement cash retains opening6 and liabilities7/3. This does not test adding a hidden guarantee to an admissible history family.',
 'Execute the original hidden-contract alternative within a declared company family and retain structural completeness limits.')}
for identifier,(disposition,comparison,action) in updates.items():
    row=dict(id=identifier,original_row=by[identifier],disposition=disposition,comparison=comparison,
        evidence=evidence,next_action=action,original_status_unchanged=True,broad_package_closed=False)
    existing=next((i for i,x in enumerate(d['rows']) if x['id']==identifier),None)
    if existing is None:d['rows'].append(row)
    else:d['rows'][existing]=row
d['rows'].sort(key=lambda x:x['id']);d['reviewed_rows']=len(d['rows'])
assert d['reviewed_rows']==12
d['scope']='Twelve original rows individually reviewed;189 remain outside this continuation. Guarantee omission has scoped input evidence; hidden-contract expansion remains open.'
for row in d['rows']:assert row['original_row']==by[row['id']]
f.write_text(json.dumps(d,indent=2)+'\n')
lines=['# Current original failure dispositions','','28 October2026. Twelve original rows reviewed;189 outside this continuation. All201 original rows/statuses remain unchanged. Counts are coverage, not closure.','',
 '| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines += ['| '+x['id']+' | '+x['comparison']+' | '+x['next_action']+' |' for x in d['rows']]
lines += ['','Latest guarantee result: data/accounting-master/company-state-guarantee-failures-20261028/result.md. The prior11-row supplement is preserved in navigation-before.json there.','']
(STATE/'failure-dispositions.md').write_text('\n'.join(lines))
result=str((HERE/'result.md').relative_to(ROOT))
for t in program['tasks']:
    if t['id']=='C04':
        t['evidence'].append(result)
        t['next_action']='Twelve original rows reviewed;189 remain outside this pass. Continue exact targets and hidden-contract family expansion; scoped guarantee input inspection does not close structural completeness.'
for a,b in zip(old['tasks'],program['tasks']):
    for k in ['id','status','depends_on','completion_criterion','requirements']:assert a[k]==b[k]
p.write_text(json.dumps(program,indent=2)+'\n')
entry='''
## Guarantee omission and unpaid-contract review — 28 October2026

The unchanged SectorCompany/1 reference passes244 checks across46 cases.
Missing guarantee fields never become zero, but native null ECL/service
inputs remain unsupported. A separate pinned input inspector passes313
checks across35 cases, retaining omitted/null pointers and full native
outcomes; source refusal takes precedence. A known never-paid guarantee
remains a liability. Hidden-contract family expansion remains unimplemented.
Result: data/accounting-master/company-state-guarantee-failures-20261028/result.md.

Twelve original failure rows are individually reviewed;189 remain outside
this pass. Original records, statuses and all40 task criteria are unchanged.
Ordered main reading is288/831; resume289. T01 is definition-complete;
C04/R04 remain in_progress, release not_ready and empirical E3 deferred.
Continue ready failure, source/survey and manuscript work. No global veto.

'''
paths=['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md',
 'docs/plans/accounting-master-checkpoint.md','data/accounting-master/construction-continuation-20261028/checkpoint.md',
 'data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']
for path in paths:
    q=ROOT/path;title,rest=q.read_text().split('\n',1);q.write_text(title+'\n'+entry+rest)
for path,key in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
    q=ROOT/path;j=json.loads(q.read_text())
    j[key]['guarantee_failure_continuation_20261028']=dict(result=result,reviewed_failure_rows=12,original_failure_rows=201,remaining_outside_pass=189,scope='Exact missing-input controls; hidden-contract population expansion remains open')
    q.write_text(json.dumps(j,indent=2)+'\n')
print(json.dumps(dict(reviewed=12,outside_pass=189,original_statuses_preserved=True)))
