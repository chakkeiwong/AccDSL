"""Repair practical task ownership while preserving original criteria."""
from copy import deepcopy
from pathlib import Path
from hashlib import sha256
import json,shutil
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
U=ROOT/'data/accounting-master/unified-program-20261028'
PLAN='docs/plans/company-state-construction-sequencing-review-20261028.md'
def main():
    p=U/'program.json';before=json.loads(p.read_text());old=deepcopy(before)
    backup=HERE/'sequencing-program-before.json'
    if backup.exists():raise FileExistsError(backup)
    shutil.copy2(p,backup)
    for t in before['tasks']:
        if t['id'] in ['U00','T01','T03','T05'] and PLAN not in t['evidence']:t['evidence'].append(PLAN)
        if t['id']=='T01':
            t['next_action']='Complete the common state-definition contract and all-kind dependency coverage for the existing reference; preserve unknowns. Sector/basis implementation belongs to T05 and actual source/actor admission to T03/C01.'
            t['remaining']=['Trace the uninspected inventory, facility, tax, report and refusal dependencies in the declared reference operation class.',
                'Consolidate economic/contract state, accounting memory, parameters, actor information, histories and changing populations into the common contract; review against the unchanged original criterion.',
                'Expose required sector/source identities and unresolved coverage without making downstream T05/T03/C01 implementation a new prerequisite for this definition task.']
        if t['id']=='T05':
            t['remaining']=['Own implementation of supported industry/basis composition and migration after T01/S07; preserve exact economic and memory ownership and refuse unsupported joins.']
        if t['id']=='T03':
            extra='Actual source/issuer identity, chronology, authority and actor access remain owned here and in C01, not a new T01 definition prerequisite.'
            if extra not in t['remaining']:t['remaining'].append(extra)
    stable=lambda d:[{k:v for k,v in t.items() if k not in ['next_action','remaining','evidence']} for t in d['tasks']]
    assert stable(before)==stable(old)
    p.write_text(json.dumps(before,indent=2)+chr(10))
    (HERE/'sequencing-review-result.json').write_text(json.dumps(dict(status='pass',
        finding='Practical task-ownership loop in remaining-work prose; graph itself is acyclic',
        plan=PLAN,task_statuses_edges_and_criteria_preserved=True,
        before=sha256(backup.read_bytes()).hexdigest(),after=sha256(p.read_bytes()).hexdigest()),indent=2)+chr(10))
    print(json.dumps(dict(status='pass',criteria_edges_statuses_preserved=True)))
if __name__=='__main__':main()
