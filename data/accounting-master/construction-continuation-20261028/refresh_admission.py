"""Point live construction work to the guarded population entrypoint."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json,shutil
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
U='data/accounting-master/unified-program-20261028/'
RESULT='data/accounting-master/company-state-population-admission-20261028/result.md'
SUMMARY='''## Unresolved opening admission repaired — 28 October 2026

The guarded population entrypoint passes 114 checks, preserving native unknown
opening inputs, invalid/unsupported outcomes, complete earlier years and
unexecuted suffixes. Use company-state-population-admission-20261028/admission.py
under data/accounting-master when opening executability is unknown. The earlier
claim/cohort inspectors require an executable opening. Failed probes and the
source-refusal ordering repair remain recorded; successful prior outputs match.

Current result: data/accounting-master/company-state-population-admission-20261028/result.md.
The full checkpoint and remaining work are in
data/accounting-master/construction-continuation-20261028/checkpoint.md.
All broad task/release statuses are unchanged; empirical E3 remains deferred.

'''
def main():
    paths=[U+'program.json',U+'current-requirement-decisions.json','data/accounting-master/next-plan.json',
        'scripts/accounting_master_catalog.json','MISSION_CONTROL.md','data/accounting-master/next-plan.md',
        'docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md',
        'docs/plans/accounting-mission-requirements.md',U+'reset-memo.md',
        'docs/plans/company-state-research-release-program-20261028.md']
    backup=HERE/'admission-navigation-before';backup.mkdir(exist_ok=False)
    for p in paths:
        q=backup/p;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/p,q)
    def read(p):return json.loads((ROOT/p).read_text())
    def write(p,d):(ROOT/p).write_text(json.dumps(d,indent=2)+chr(10))
    d=read(paths[0]);old=deepcopy(d)
    for t in d['tasks']:
        if t['id'] in ['T01','T03','C04'] and RESULT not in t['evidence']:t['evidence'].append(RESULT)
        if t['id']=='T01':t['next_action']='Use guarded population admission for unresolved openings; extend remaining resource/contract operations, industry/basis memory and source-supported identities beyond checked claim/cohort populations.'
    assert [{k:v for k,v in t.items() if k not in ['evidence','next_action']} for t in d['tasks']]==[{k:v for k,v in t.items() if k not in ['evidence','next_action']} for t in old['tasks']];write(paths[0],d)
    d=read(paths[1]);original=[r['original_condition'] for r in d['rows']]
    for r in d['rows']:
        if r['id'] in ['MC04','MC08','MC09','MC13','MC18','MC19','MC28','MC33','MC35'] and RESULT not in r.setdefault('latest_evidence',[]):r['latest_evidence'].append(RESULT)
    assert original==[r['original_condition'] for r in d['rows']];write(paths[1],d)
    for path,key in [(paths[2],'active_execution'),(paths[3],'active_execution_note')]:
        d=read(path);before=deepcopy(d);a=d[key];a.update(updated=datetime.now(timezone.utc).isoformat(),latest_internal_result=RESULT)
        a['population_admission_20261028']=dict(result=RESULT,checks=114,entrypoint='data/accounting-master/company-state-population-admission-20261028/admission.py')
        a['next'][0]='Use guarded population admission, then '+a['next'][0][0].lower()+a['next'][0][1:]
        if path==paths[2] and RESULT not in a['latest_results']:a['latest_results'].append(RESULT)
        assert {k:v for k,v in d.items() if k!=key}=={k:v for k,v in before.items() if k!=key};write(path,d)
    for path in paths[4:]:
        p=ROOT/path;s=p.read_text();head,_,tail=s.partition(chr(10))
        if SUMMARY.splitlines()[0] not in s:p.write_text(head+chr(10)*2+SUMMARY+tail.lstrip(chr(10)))
    (HERE/'admission-navigation-changes.json').write_text(json.dumps({p:dict(before=sha256((backup/p).read_bytes()).hexdigest(),after=sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths},indent=2)+chr(10))
    print(json.dumps(dict(paths_updated=len(paths),original_conditions_and_statuses_preserved=True)))
if __name__=='__main__':main()
