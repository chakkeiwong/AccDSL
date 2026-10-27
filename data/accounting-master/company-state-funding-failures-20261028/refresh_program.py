"""Append exact original funding dispositions, retaining the criteria."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
STATE=ROOT/'data/accounting-master/construction-continuation-20261028'
f=STATE/'failure-dispositions.json';d=json.loads(f.read_text())
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';program=json.loads(p.read_text());old=deepcopy(program)
with (HERE/'navigation-before.json').open('x') as out:
    json.dump(dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),failure_dispositions=d,task_C04=next(x for x in old['tasks'] if x['id']=='C04')),out,indent=2);out.write('\n')
original=json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())
by={x['original_row']['id']:x['original_row'] for x in original['rows']}
evidence=str((HERE/'attempt-01/verification.json').relative_to(ROOT))
assert json.loads((ROOT/evidence).read_text())['status']=='pass'
comparisons={
 'SIM-F022':'Bridge principal cap30 less fee1 supplies29 for need30; the declared family is infeasible. Removing the fee changes the answer.',
 'SIM-F023':'No admitted bridge/term offer constrains its draw to zero; an absent offer cannot finance the payment. Real offer authentication remains outside this synthetic case.',
 'SIM-F024':'A day5 term issue cannot fund the day4 payment; every dated cash prefix is required even where final cash is positive.'}
for identifier,comparison in comparisons.items():
    assert not any(x['id']==identifier for x in d['rows'])
    d['rows'].append(dict(id=identifier,original_row=by[identifier],disposition='exact_original_scoped_funding_constraints',comparison=comparison,evidence=[evidence],
        next_action='Connect real admission, nonanticipative policy and full typed event/accounting execution separately; this is an explicit finite solver encoding.',original_status_unchanged=True,broad_package_closed=False))
d['rows'].sort(key=lambda x:x['id']);d['reviewed_rows']=len(d['rows']);assert d['reviewed_rows']==15
d['scope']='Fifteen original rows individually reviewed;186 outside this continuation. Finite funding constraints do not close source admission or the general event engine.'
for x in d['rows']:assert x['original_row']==by[x['id']]
f.write_text(json.dumps(d,indent=2)+'\n')
lines=['# Current original failure dispositions','','28 October2026. Fifteen original rows reviewed;186 outside this continuation. All201 original rows/statuses remain unchanged. Coverage is not closure.','',
 '| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines += ['| '+x['id']+' | '+x['comparison']+' | '+x['next_action']+' |' for x in d['rows']]
lines += ['','Latest funding result: data/accounting-master/company-state-funding-failures-20261028/result.md. Previous dispositions remain in navigation-before.json there.','']
(STATE/'failure-dispositions.md').write_text('\n'.join(lines))
result=str((HERE/'result.md').relative_to(ROOT))
for t in program['tasks']:
    if t['id']=='C04':
        t['evidence'].append(result);t['next_action']='Fifteen original rows reviewed;186 remain outside this pass. Continue exact targets, paired information-constrained policies and hidden-contract family expansion; preserve finite encoding limits.'
for a,b in zip(old['tasks'],program['tasks']):
    for k in ['id','status','depends_on','completion_criterion','requirements']:assert a[k]==b[k]
p.write_text(json.dumps(program,indent=2)+'\n')
entry='''
## Exact funding failure constraints — 28 October2026

SIM-F022/023/024 have98 passing checks across14 finite cases and3
target-changing controls. The existing rational solver preserves fee/cap,
admitted-offer and every dated cash-prefix constraint. Day5 cash cannot
fund day4 maturity; full sale removes term eligibility; half-sale H2 reaches
the exact price53/80 boundary. This is a new explicit finite encoding, not
general event execution or a tested nonanticipative policy. Result:
data/accounting-master/company-state-funding-failures-20261028/result.md.

Fifteen original failure rows are reviewed;186 remain outside this pass.
All201 original statuses and40 task criteria persist. Main reading is288/831;
resume289. T01 remains definition-complete, C04/R04 in_progress, releases
not_ready and empirical E3 deferred. Continue ready internal work.

'''
paths=['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md',
 'data/accounting-master/construction-continuation-20261028/checkpoint.md','data/accounting-master/next-plan.md',
 'docs/plans/company-state-research-release-program-20261028.md']
for path in paths:
    q=ROOT/path;title,rest=q.read_text().split('\n',1);q.write_text(title+'\n'+entry+rest)
for path,key in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
    q=ROOT/path;j=json.loads(q.read_text());j[key]['funding_failure_continuation_20261028']=dict(result=result,reviewed_failure_rows=15,original_failure_rows=201,remaining_outside_pass=186,scope='Exact finite funding constraints; no general event-engine or policy admission')
    q.write_text(json.dumps(j,indent=2)+'\n')
print(json.dumps(dict(reviewed=15,outside_pass=186,original_statuses_preserved=True)))
