"""Refresh live next actions after common-contract and sequencing review."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json,shutil
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
U='data/accounting-master/unified-program-20261028/'
RESULT='data/accounting-master/company-state-native-operation-coverage-20261028/result.md'
CONTRACT='docs/design/research/company-state-program-20261028/native-construction-contract-v1.md'
REVIEW='data/accounting-master/construction-continuation-20261028/common-contract-review.md'
NEXT=[
 'Bind the reviewed common construction request to exact native owners, with typed state/history/actor requirements and unsupported-join refusal; preserve native partial outcomes and unknown populations.',
 'Continue actual source/actor admission at T03/C01 and sector/basis implementation at T05 after its prerequisites; do not loop those implementation tasks back into T01 definition.',
 'Continue the remaining original failure dispositions, REA extensions/competitors and ordered manuscript review; original acceptance requirements remain unchanged.'
]
SUMMARY='''## Common construction contract and sequencing repair — 28 October 2026

All14 native company-operation kinds now have a source-reviewed dependency
inventory;45 checks and10 new guard controls pass. The first interest probe
was corrected for its two-day accrual and retained. The common implementer
draft is native-construction-contract-v1.md under
docs/design/research/company-state-program-20261028/.

The program review repairs a practical loop in T01's remaining-work prose:
sector/basis implementation belongs to dependent T05, and actual source/actor
admission to T03/C01. Every original criterion, dependency and status remains.
T01 stays in_progress: its next deliverable is a typed common request bound
to exact native owners, historical queries and actor requirements, with
unsupported joins and unknown population scope preserved.

Current review: data/accounting-master/construction-continuation-20261028/common-contract-review.md.
The full checkpoint is checkpoint.md in that directory. S1-S5 remain partial,
S6 held, E3 deferred; both selected/provisional release statuses are unchanged.

'''
def main():
    paths=[U+'program.json',U+'current-requirement-decisions.json',U+'current-requirement-decisions.md',
        'data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json',
        'MISSION_CONTROL.md','data/accounting-master/next-plan.md','docs/plans/accounting-master-current.md',
        'docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-mission-requirements.md',U+'reset-memo.md',
        'docs/plans/company-state-research-release-program-20261028.md']
    backup=HERE/'common-contract-navigation-before';backup.mkdir(exist_ok=False)
    for p in paths:
        q=backup/p;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/p,q)
    def read(p):return json.loads((ROOT/p).read_text())
    def write(p,d):(ROOT/p).write_text(json.dumps(d,indent=2)+chr(10))
    d=read(paths[0]);old=deepcopy(d)
    for t in d['tasks']:
        adds={'T01':[RESULT,CONTRACT,REVIEW],'C04':[RESULT]}.get(t['id'],[])
        for e in adds:
            if e not in t['evidence']:t['evidence'].append(e)
        if t['id']=='T01':
            t['next_action']=NEXT[0]
            t['remaining']=['A bounded native contract and14-kind source-inspected inventory are delivered; define the common typed state/history/actor request and exact owner projection, with explicit unsupported joins.',
                'Review the common contract against the unchanged original criterion; sector implementation and actual source resolution remain T05/T03/C01 responsibilities.']
    stable=lambda p:[{k:v for k,v in t.items() if k not in ['evidence','next_action','remaining']} for t in p['tasks']]
    assert stable(d)==stable(old);write(paths[0],d)
    d=read(paths[1]);old=deepcopy(d)
    for row in d['rows']:
        if row['id'] in ['MC08','MC09','MC13','MC18','MC19','MC28','MC33','MC35']:
            for e in [RESULT,CONTRACT,REVIEW]:
                if e not in row.setdefault('latest_evidence',[]):row['latest_evidence'].append(e)
        if row['id']=='MC18':row['remaining_action']=NEXT[0]+' '+NEXT[1]
    assert [r['original_condition'] for r in d['rows']]==[r['original_condition'] for r in old['rows']];write(paths[1],d)
    row=next(r for r in d['rows'] if r['id']=='MC18');p=ROOT/paths[2]
    p.write_text(chr(10).join(('| MC18 | '+', '.join(row['current_tasks'])+' | '+row['remaining_action']+' |') if line.startswith('| MC18 |') else line for line in p.read_text().splitlines())+chr(10))
    for path,key in [(paths[3],'active_execution'),(paths[4],'active_execution_note')]:
        d=read(path);old=deepcopy(d);a=d[key];a.update(updated=datetime.now(timezone.utc).isoformat(),next=NEXT,latest_internal_result=RESULT)
        a['common_contract_20261028']=dict(result=RESULT,contract=CONTRACT,review=REVIEW,checks=45,kinds=14,status='T01 remains in_progress')
        if path==paths[3]:
            for e in [RESULT,CONTRACT,REVIEW]:
                if e not in a['latest_results']:a['latest_results'].append(e)
        assert {k:v for k,v in d.items() if k!=key}=={k:v for k,v in old.items() if k!=key};write(path,d)
    for path in paths[5:]:
        p=ROOT/path;s=p.read_text();head,_,tail=s.partition(chr(10))
        if SUMMARY.splitlines()[0] not in s:p.write_text(head+chr(10)*2+SUMMARY+tail.lstrip(chr(10)))
    (HERE/'common-contract-navigation-changes.json').write_text(json.dumps({p:dict(before=sha256((backup/p).read_bytes()).hexdigest(),after=sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths},indent=2)+chr(10))
    print(json.dumps(dict(updated_paths=len(paths),criteria_dependencies_statuses_preserved=True)))
if __name__=='__main__':main()
