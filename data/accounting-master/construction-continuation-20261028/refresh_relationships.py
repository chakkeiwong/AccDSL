"""Attach verified reading/relationship results to live navigation only."""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import shutil

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
U='data/accounting-master/unified-program-20261028/'
REA='data/accounting-master/company-state-rea-reading-20261028/result.md'
REL='data/accounting-master/company-state-relationship-dependencies-20261028/result.md'
POL='data/accounting-master/company-state-relationship-dependencies-20261028/policy-result.md'
NOTE='docs/design/research/company-state-program-20261028/rea-state-relationships.md'
NEXT=[
    'Extend existing operation dependency inspection to resource cohorts, contract populations and sector/basis memory; preserve claim identities, partial execution and missing counterparties.',
    'Continue REA policy/commitment extensions and direct competitors; source-backed issuer rights, chronology, authority and actor access remain unresolved.',
    'Continue individual failure dispositions and ordered document review; original requirements remain open and empirical E3 deferred.'
]
SUMMARY='''## Relationship construction and policy continuation — 28 October 2026

The REA primary reading is complete for the retained 1982 article; later
extensions and competitors remain open. Existing native claim operations now
have a 137-check relationship inspector covering 63 events, 14 lifetime claims
and 72 creation/allocation links. Equal financial reports can retain different
claim balances. The existing policy connection passes 110 checks against its
exact price-revision parent; a fully collected claim rejects the unchanged
later collection as over-settlement. The initial wrong-parent attempt and its
repair are preserved. No counterparty, legal identity or actor access is invented.

Results: data/accounting-master/company-state-rea-reading-20261028/result.md;
company-state-relationship-dependencies-20261028/result.md and policy-result.md
under data/accounting-master. Full recovery checkpoint:
data/accounting-master/construction-continuation-20261028/checkpoint.md.

Next: resource/contract populations, sector/basis dependencies, actual issuer
rights/access, remaining primary/competing survey, failure dispositions and
ordered review. All 40 task statuses and original conditions remain unchanged.
Selected 5.55-R1 stays not_ready; 5.56-D1 stays unselected/not_ready. E3 deferred.

'''

def main():
    paths=[U+'program.json',U+'current-requirement-decisions.json',U+'current-requirement-decisions.md',
        'data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json',
        'MISSION_CONTROL.md','data/accounting-master/next-plan.md',
        'docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md',
        'docs/plans/accounting-mission-requirements.md',U+'reset-memo.md',
        'docs/plans/company-state-research-release-program-20261028.md']
    backup=HERE/'relationships-navigation-before';backup.mkdir(exist_ok=False)
    for path in paths:
        q=backup/path;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/path,q)
    def read(p):return json.loads((ROOT/p).read_text())
    def write(p,d):(ROOT/p).write_text(json.dumps(d,indent=2)+chr(10))
    d=read(paths[0]);before=deepcopy(d)
    for t in d['tasks']:
        adds={'S01':[REA,NOTE],'T01':[REA,REL,POL],'C04':[REL,POL]}.get(t['id'],[])
        for e in adds:
            assert (ROOT/e).is_file()
            if e not in t['evidence']:t['evidence'].append(e)
        if t['id']=='S01':
            t['next_action']='REA1982 full primary reading and Arya inverse reproduction are delivered; inspect policy/commitment extensions, database/user-evaluation and graph-journal competitors, preserving omitted-paper risks.'
        if t['id']=='T01':
            t['next_action']=NEXT[0]
            t['remaining']=['Affine and scoped native claim/policy dependencies are delivered; resource cohorts, nonlinear guards, industry/basis composition, changing populations and actual identity/access remain incomplete.']
        if t['id']=='C04':
            t['next_action']='Disposition all original failures individually; reuse new zero-allocation endpoint, wrong policy parent, same-total/different-claim and downstream over-settlement controls without treating the supplement as complete coverage.'
    stable=lambda x:[{k:v for k,v in t.items() if k not in ['evidence','next_action','remaining']} for t in x['tasks']]
    assert stable(d)==stable(before)
    write(paths[0],d)
    decisions=read(paths[1]);original=deepcopy(decisions)
    updates={'MC18':NEXT[0], 'MC29':NEXT[1]}
    for row in decisions['rows']:
        adds=[]
        if row['id'] in ['MC08','MC13','MC18','MC19','MC28','MC29','MC30','MC32','MC35']:adds+=[REA]
        if row['id'] in ['MC08','MC09','MC13','MC18','MC19','MC28','MC33']:adds+=[REL,POL]
        for e in adds:
            if e not in row.setdefault('latest_evidence',[]):row['latest_evidence'].append(e)
        if row['id'] in updates:row['remaining_action']=updates[row['id']]
    assert [r['original_condition'] for r in decisions['rows']]==[r['original_condition'] for r in original['rows']]
    write(paths[1],decisions)
    p=ROOT/paths[2];lines=p.read_text().splitlines()
    for row in decisions['rows']:
        if row['id'] in updates:
            lines=[('| '+row['id']+' | '+', '.join(row['current_tasks'])+' | '+row['remaining_action']+' |')
                   if line.startswith('| '+row['id']+' |') else line for line in lines]
    p.write_text(chr(10).join(lines)+chr(10))
    for path,key in [(paths[3],'active_execution'),(paths[4],'active_execution_note')]:
        d=read(path);frozen=deepcopy(d);a=d[key]
        a.update(updated=datetime.now(timezone.utc).isoformat(),next=NEXT,latest_internal_result=POL)
        a['relationship_continuation_20261028']=dict(rea=REA,relationships=REL,policy=POL,
            checks=[137,110],checkpoint='data/accounting-master/construction-continuation-20261028/checkpoint.md')
        if path==paths[3]:
            for e in [REA,REL,POL]:
                if e not in a.setdefault('latest_results',[]):a['latest_results'].append(e)
        assert {k:v for k,v in d.items() if k!=key}=={k:v for k,v in frozen.items() if k!=key}
        write(path,d)
    for path in paths[5:]:
        p=ROOT/path;text=p.read_text();head,_,tail=text.partition(chr(10))
        if SUMMARY.splitlines()[0] not in text:p.write_text(head+chr(10)*2+SUMMARY+tail.lstrip(chr(10)))
    changes={p:dict(before=sha256((backup/p).read_bytes()).hexdigest(),after=sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths}
    (HERE/'relationships-navigation-changes.json').write_text(json.dumps(changes,indent=2)+chr(10))
    print(json.dumps(dict(updated_paths=len(paths),task_definitions_and_statuses_preserved=True,original_conditions_preserved=True,frozen_catalog_preserved=True)))

if __name__=='__main__':main()
