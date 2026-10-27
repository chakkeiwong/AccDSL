"""Add verified local evidence without closing original mission requirements."""
from datetime import datetime, timezone
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
import json
import shutil

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
U = 'data/accounting-master/unified-program-20261028/'
TIMING = 'data/accounting-master/company-state-source-timing-20261028/result.md'
DEBT = 'data/accounting-master/company-state-debt-measurement-20261028/result.md'
DEPS = 'data/accounting-master/company-state-operation-dependencies-20261028/result.md'
NEXT = [
    'Extend native affine dependency inspection to operation populations and industry/basis composition, preserving guards, accounting memory and unresolved scope.',
    'Connect supported issuer quantities to legal instruments and histories; actual source timing, authority and actor access remain unresolved.',
    'Continue the nine survey branches, full failure dispositions and ordered manuscript review before independent release acceptance.'
]
SUMMARY = '''## Actual-source measurements and operation dependencies — 28 October 2026

The program review reuses the completed certified temporal/native join rather
than rebuilding it. New retained Apple feed/HTML/XBRL timing evidence passes
45 checks, with historical publication and actor receipt still unresolved.
The source-backed debt adapter passes124 checks: twelve native reported
quantities from thirteen occurrences, three printed reconciliations, and a
separate issuance-period reading. Exact issuer-extension meaning is preserved;
reported totals do not become legal instruments or a complete company opening.

Native affine dependency inspection passes264 checks over42 queries,11 event
prefixes and all three full retained histories. It separates output dependencies
from feasibility constraints and removes no variables. Failed attempts and
repairs are retained. Results are under data/accounting-master/:
company-state-source-timing-20261028/result.md,
company-state-debt-measurement-20261028/result.md, and
company-state-operation-dependencies-20261028/result.md.

The forty-task master and all original acceptance conditions remain active.
Selected5.55-R1 stays not_ready;5.56-D1 stays an unselected provisional draft.
Next: operation/population and industry/basis construction; source-backed legal
instruments, authority/access; primary/competing survey, full failure review and
ordered reading. Empirical E3 remains deferred. No global continuation veto.

'''


def main():
    paths = [U+'program.json', U+'current-requirement-decisions.json', U+'current-requirement-decisions.md',
             'data/accounting-master/next-plan.json', 'scripts/accounting_master_catalog.json',
             'MISSION_CONTROL.md', 'data/accounting-master/next-plan.md',
             'docs/plans/accounting-master-current.md', 'docs/plans/accounting-master-checkpoint.md',
             'docs/plans/accounting-mission-requirements.md', U+'reset-memo.md']
    backup = HERE/'navigation-before'
    backup.mkdir(exist_ok=False)
    for path in paths:
        dest = backup/path
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/path, dest)
    def read(path): return json.loads((ROOT/path).read_text())
    def write(path, value): (ROOT/path).write_text(json.dumps(value,indent=2)+chr(10))
    program = read(U+'program.json')
    original_tasks = deepcopy(program['tasks'])
    additions = {'T01':[DEBT,DEPS], 'T03':[TIMING,DEBT,DEPS], 'C01':[TIMING,DEBT], 'C04':[TIMING,DEBT,DEPS]}
    for task in program['tasks']:
        for evidence in additions.get(task['id'], []):
            if evidence not in task['evidence']: task['evidence'].append(evidence)
        if task['id']=='T01':
            task['next_action']=NEXT[0]
            task['remaining']=['Affine dependency inspection is delivered; general operation/population construction, nonlinear guards and industry/basis composition remain incomplete.']
        if task['id']=='T03':
            task['next_action']=NEXT[1]
            task['remaining']=['Actual-source reported debt measurements are typed; complete legal-book/history mapping remains unresolved.',
                               'Supported source chronology, authority, actor access and probabilistic reliability/dependence.',
                               'Common actor observations/actions and retrospective/prospective accounting consequences.']
    assert [t['status'] for t in program['tasks']]==[t['status'] for t in original_tasks]
    write(U+'program.json',program)
    decisions=read(U+'current-requirement-decisions.json')
    original=[deepcopy(r['original_condition']) for r in decisions['rows']]
    for row in decisions['rows']:
        ev=[]
        if row['id'] in ['MC03','MC04','MC05','MC06','MC07','MC25','MC27']:ev += [TIMING,DEBT]
        if row['id'] in ['MC08','MC09','MC10','MC11','MC13','MC18','MC19','MC20','MC28','MC33']:ev += [DEBT,DEPS]
        for e in ev:
            if e not in row.setdefault('latest_evidence',[]):row['latest_evidence'].append(e)
        if row['id']=='MC05':row['remaining_action']='Extend supported issuer quantity meanings to full histories and actual chronology/authority/access. Retained links and typed reported measurements are delivered; raw vendor dates do not establish historical availability.'
        if row['id']=='MC18':row['remaining_action']='Extend exact native affine dependency inspection to complete operation populations, nonlinear guards, sector/basis memory and source-backed construction; no state reduction or company completeness follows from the bounded adapter.'
    assert original==[r['original_condition'] for r in decisions['rows']]
    write(U+'current-requirement-decisions.json',decisions)
    p=ROOT/(U+'current-requirement-decisions.md')
    text=p.read_text()
    for row in decisions['rows']:
        prefix='| '+row['id']+' |'
        if row['id'] in ['MC05','MC18']:
            lines=text.splitlines()
            lines=[('| '+row['id']+' | '+', '.join(row['current_tasks'])+' | '+row['remaining_action']+' |') if line.startswith(prefix) else line for line in lines]
            text=chr(10).join(lines)+chr(10)
    p.write_text(text)
    now=datetime.now(timezone.utc).isoformat()
    for path,key in [('data/accounting-master/next-plan.json','active_execution'),('scripts/accounting_master_catalog.json','active_execution_note')]:
        d=read(path);a=d[key]
        a['updated']=now;a['next']=NEXT;a['latest_internal_result']=DEPS
        a['construction_continuation_20261028']=dict(source_timing=TIMING,debt_measurement=DEBT,
            operation_dependencies=DEPS,checks=[45,124,264],release_status='not_ready',
            checkpoint='data/accounting-master/construction-continuation-20261028/checkpoint.md')
        if path.endswith('next-plan.json'):
            for e in [TIMING,DEBT,DEPS]:
                if e not in a.setdefault('latest_results',[]):a['latest_results'].append(e)
        write(path,d)
    for path in paths[5:]:
        p=ROOT/path;text=p.read_text();head,sep,tail=text.partition(chr(10))
        if SUMMARY.splitlines()[0] not in text:p.write_text(head+chr(10)+chr(10)+SUMMARY+tail.lstrip(chr(10)))
    changes={path:{'before':sha256((backup/path).read_bytes()).hexdigest(),
                   'after':sha256((ROOT/path).read_bytes()).hexdigest()} for path in paths}
    (HERE/'navigation-changes.json').write_text(json.dumps(changes,indent=2)+chr(10))
    print(json.dumps({'updated_paths':len(paths),'task_statuses_unchanged':True,'original_conditions_unchanged':True}))


if __name__=='__main__':main()
