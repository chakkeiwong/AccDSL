"""Refresh live construction and failure work after verified cohort results."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json,shutil

ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
U='data/accounting-master/unified-program-20261028/'
COHORT='data/accounting-master/company-state-asset-cohort-dependencies-20261028/result.md'
FAIL='data/accounting-master/construction-continuation-20261028/failure-dispositions.md'
SPEC='docs/design/research/company-state-program-20261028/native-population-construction.md'
NEXT=[
 'Extend the now-checked claim and fixed-asset population dependencies to other native resource/contract operations and supported sector/basis memory; actual identities and coverage remain unresolved.',
 'Continue original failure dispositions individually beyond the eight-row pass; reuse the exact Machine20 test and preserve original case distinctions.',
 'Continue REA extensions/competitors, issuer rights/source chronology/actor access and ordered manuscript review; all original release requirements remain.'
]
SUMMARY='''## Asset cohorts and original failure review — 28 October 2026

Native fixed-asset construction now passes 120 checks over nine cohorts, six
additions and 21 annual cohort reads. Equal current reports can imply different
future depreciation when lives or service dates differ. The original Machine20
failure discriminator passes 11 additional checks: equal carrying value20, then
charges10 versus20. Eight original failure rows are individually dispositioned;
193 remain outside this pass. Related examples are not substituted for the
original guarantee, refinancing or source-admission tests.

The live specification now includes native-population-construction.md under
docs/design/research/company-state-program-20261028/. Cohort results are in
data/accounting-master/company-state-asset-cohort-dependencies-20261028/result.md.
Current failure review and recovery state are in
data/accounting-master/construction-continuation-20261028/.

Next: remaining resource/contract populations, source-backed sector/basis
construction, original failure dispositions, primary competitors and ordered
review. No broad task or release status changes. Selected 5.55-R1 remains
not_ready; 5.56-D1 remains unselected/not_ready; empirical E3 remains deferred.

'''

def main():
    paths=[U+'program.json',U+'current-requirement-decisions.json',U+'current-requirement-decisions.md',
        'data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json',
        'MISSION_CONTROL.md','data/accounting-master/next-plan.md','docs/plans/accounting-master-current.md',
        'docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-mission-requirements.md',
        U+'reset-memo.md','docs/plans/company-state-research-release-program-20261028.md']
    backup=HERE/'cohort-navigation-before';backup.mkdir(exist_ok=False)
    for p in paths:
        q=backup/p;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/p,q)
    def read(p):return json.loads((ROOT/p).read_text())
    def write(p,d):(ROOT/p).write_text(json.dumps(d,indent=2)+chr(10))
    d=read(paths[0]);old=deepcopy(d)
    for t in d['tasks']:
        additions={'T01':[COHORT,SPEC],'C04':[COHORT,FAIL]}.get(t['id'],[])
        for e in additions:
            if e not in t['evidence']:t['evidence'].append(e)
        if t['id']=='T01':
            t['next_action']=NEXT[0]
            t['remaining']=['Affine, trade-claim/policy and fixed-asset cohort inspections are delivered; other operation populations, industry/basis composition, full guards and supported actual identity/access remain incomplete.']
        if t['id']=='C04':
            t['next_action']=NEXT[1]
            t['remaining']=['Eight original failure rows have individual current comparisons;193 rows remain outside this continuation. SIM-F043 exact native discriminator is executed; related mechanisms do not close different original cases.']
    stable=lambda p:[{k:v for k,v in t.items() if k not in ['evidence','next_action','remaining']} for t in p['tasks']]
    assert stable(d)==stable(old);write(paths[0],d)
    d=read(paths[1]);old=deepcopy(d)
    for row in d['rows']:
        adds=[]
        if row['id'] in ['MC08','MC09','MC13','MC18','MC19','MC20','MC28','MC33']:adds+=[COHORT,SPEC]
        if row['id'] in ['MC28','MC33','MC35']:adds+=[FAIL]
        for e in adds:
            if e not in row.setdefault('latest_evidence',[]):row['latest_evidence'].append(e)
        if row['id']=='MC18':row['remaining_action']=NEXT[0]
    assert [r['original_condition'] for r in d['rows']]==[r['original_condition'] for r in old['rows']];write(paths[1],d)
    p=ROOT/paths[2];lines=p.read_text().splitlines();row=next(r for r in d['rows'] if r['id']=='MC18')
    lines=[('| MC18 | '+', '.join(row['current_tasks'])+' | '+row['remaining_action']+' |') if line.startswith('| MC18 |') else line for line in lines]
    p.write_text(chr(10).join(lines)+chr(10))
    for path,key in [(paths[3],'active_execution'),(paths[4],'active_execution_note')]:
        d=read(path);old=deepcopy(d);a=d[key]
        a.update(updated=datetime.now(timezone.utc).isoformat(),next=NEXT,latest_internal_result=COHORT)
        a['cohort_continuation_20261028']=dict(result=COHORT,specification=SPEC,failure_dispositions=FAIL,
            checks=[120,11],original_failure_rows_reviewed=8,original_failure_population=201,
            checkpoint='data/accounting-master/construction-continuation-20261028/checkpoint.md')
        if path==paths[3]:
            for e in [COHORT,FAIL,SPEC]:
                if e not in a.setdefault('latest_results',[]):a['latest_results'].append(e)
        assert {k:v for k,v in d.items() if k!=key}=={k:v for k,v in old.items() if k!=key};write(path,d)
    for path in paths[5:]:
        p=ROOT/path;text=p.read_text();head,_,tail=text.partition(chr(10))
        if SUMMARY.splitlines()[0] not in text:p.write_text(head+chr(10)*2+SUMMARY+tail.lstrip(chr(10)))
    changes={p:dict(before=sha256((backup/p).read_bytes()).hexdigest(),after=sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths}
    (HERE/'cohort-navigation-changes.json').write_text(json.dumps(changes,indent=2)+chr(10))
    print(json.dumps(dict(updated=len(paths),statuses_and_original_conditions_preserved=True)))

if __name__=='__main__':main()
