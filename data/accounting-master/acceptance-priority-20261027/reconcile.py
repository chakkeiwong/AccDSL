"""One-shot current acceptance index, preserving immutable predecessor records."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json, re, subprocess, sys, time
from decisions import MISSING, NEXT, EVIDENCE

H=Path(__file__).resolve().parent
R=H.parents[2]
B=H.parent
OLD=B/'gap-insurance-stage-refresh-20261027'
A=B/'release-readiness-audit-20261027'
def read(p): return json.loads(p.read_text())
def digest(p): return sha256(p.read_bytes()).hexdigest()
def dump(p,v): p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')

def main():
    start=time.monotonic()
    assert not (H/'release-acceptance.json').exists(), 'completed writer must not rerun'
    live=read(B/'next-plan.json')['active_execution']
    assert live['current_candidate']=='5.51;828 pages;not_ready'
    req=R/'docs/plans/accounting-mission-requirements.md'
    originals={}
    for number,line in enumerate(req.read_text().splitlines(),1):
        if re.match(r'^\| MC\d\d \|',line):
            fields=[v.strip() for v in line.strip().strip('|').split('|')]
            assert len(fields)==4
            originals[fields[0]]=dict(requirement=fields[1],acceptance=fields[2],historical_assessment=fields[3],line=number)
    assert set(originals)==set(MISSING)=={f'MC{i:02d}' for i in range(1,36)}
    audit=read(OLD/'audit-status.json'); packages=read(OLD/'closure-packages.json')['packages']
    cross=read(A/'requirement-crosswalk.json')['rows']
    current={r['id']:r for rows in audit['groups'].values() for r in rows}
    locks={}
    def evidence(p):
        p=Path(p); p=p if p.is_absolute() else R/p
        assert p.is_file(),p
        name=str(p.relative_to(R));locks[name]=digest(p)
        return dict(path=name,sha256=locks[name])
    for p in [req,OLD/'audit-status.json',OLD/'closure-packages.json',A/'requirement-crosswalk.json',H/'decisions.py',H/'audit-note.md',H/'reconcile.py',R/'docs/plans/accounting-release-bundle-recovery-20261027.md']:
        evidence(p)
    for k in ['current_pdf','standalone_pdf']:evidence(live[k])
    revised=[]
    for p in packages:
        step,action=NEXT[p['id']]
        q={k:p[k] for k in ['id','title','requirements','depends_on','closure_evidence','limits','status']}
        q.update(next_step=step,next_action=action,predecessor_next_action=p['next_action'],
                 predecessor=str((OLD/'closure-packages.json').relative_to(R)),
                 remaining_subcondition=action,full_package_closed=False,
                 evidence=[evidence(B/n) for n in EVIDENCE.get(p['id'],[])])
        q['design_disposition']='retained_partial_design; precise next dependency assigned'
        if p['id']=='W18':q['design_disposition']='later_product_and_empirical_execution_held; prerequisite design work remains active'
        revised.append(q)
    by={p['id']:p for p in revised}
    rows=[]
    for old in cross:
        ident=old['id']; group=old['group']; src=current.get(ident)
        row={k:old[k] for k in ['id','group','current_supported_scope','closure_packages','release_gaps','closure_steps']}
        if row['current_supported_scope'] is None:
            row['current_supported_scope']='Literature inspection is partial; use the linked original source status and current package action. This reconciliation adds no technical literature acceptance.'
        row['original_condition']=originals.get(ident,old.get('original_requirement'))
        row['historical_next_action']=old['inherited_next_action']
        row['current_actions']=[dict(package=k,step=by[k]['next_step'],action=by[k]['next_action']) for k in row['closure_packages']]
        row['owner']='internal specification/source/conformance work; independent acceptance separately pending'
        row['release_class']='design/specification/evidence'
        if ident in ['MC23','MC25','MC27','MC31','MC33','MC34','MC35']:
            row['release_class']+='; later product or empirical duties retained separately'
        if ident=='P17-08.08':row['release_class']='empirical execution deferred; protocol retained'
        refs=[]
        if src:
            refs.append(evidence(src['review_note']))
            # Preserve the first substantive residual, not the repeated stale action.
            parent=src
            while isinstance(parent.get('inherited_record'),dict):parent=parent['inherited_record']
            residual=parent.get('remaining_work_and_next_action') or src['remaining_work_and_next_action']
        else:
            residual='Complete the primary technical/source and competitor dispositions specified by the responsible package; no new literature acceptance is inferred.'
            if old.get('original_source') and (R/old['original_source']).is_file():refs.append(evidence(old['original_source']))
        row['unresolved_subcondition']=MISSING.get(ident,residual)
        row['residual_status']='current authored decision' if ident in MISSING else 'inherited detailed residual; current package action supersedes stale execution instruction'
        row['disposition']='design_partial_internal_work_required'
        if ident in ['MC06','MC17','MC19','MC21','MC22']:
            row['disposition']='design_partial_dependent_source_or_factual_admission_blocked'
        if ident=='P17-08.08':row['disposition']='empirical_held_no_run_authorized'
        for k in row['closure_packages']:refs.extend(by[k]['evidence'])
        row['evidence']=list({e['path']:e for e in refs}.values())
        row['full_requirement_closed']=False
        row['scope_waiver']=None
        row['acceptance_reason']='The retained bounded evidence supports the named subconditions only; the stated missing condition remains required. No absence of a general production engine is used to reject an already specified bounded design.'
        rows.append(row)
    assert len(rows)==114 and len({r['id'] for r in rows})==114
    assert {r['id'] for r in rows if r['group']=='obligations'}==set(r['id'] for r in audit['groups']['obligations'])
    for row in rows:
        if row['id'] in originals:
            prior=next(r for r in cross if r['id']==row['id'])['original_requirement']
            assert all(row['original_condition'][k]==prior[k] for k in ['requirement','acceptance','historical_assessment'])
        assert row['unresolved_subcondition'] and row['current_actions'] and not row['full_requirement_closed']
    scope='Current documentary acceptance decisions. All original conditions retained; no broad design acceptance or scope waiver. Complete cross-profile claim inventory and independent acceptance remain C2/C7 work.'
    dump(H/'release-acceptance.json',dict(date='2026-10-27',candidate=live['current_candidate'],scope=scope,rows=rows))
    dump(H/'closure-packages.json',dict(date='2026-10-27',scope=scope,packages=revised))
    dump(H/'source-lock.json',locks)
    lines=['# Current acceptance decisions — 27 October 2026','',scope,'',
           'The governing document remains 5.51. This index replaces stale operational directions without changing frozen evidence or the original acceptance conditions. C1 is ready; source-dependent C3 work remains local, and C2 compatibility consolidation follows the dependency repair.','']
    for row in rows:
        lines += ['## '+row['id'],'',row['current_supported_scope'],'',
                  '**Missing condition:** '+row['unresolved_subcondition'],'',
                  '**Decision:** '+row['disposition']+'. No requirement waiver.','',
                  '**Next:** '+' '.join(x['package']+'/'+x['step']+': '+x['action'] for x in row['current_actions']),'']
    (H/'release-acceptance.md').write_text('\n'.join(lines)+'\n')
    ptext=['# Current package execution queue','',scope,'']
    for p in revised:ptext += ['## '+p['id']+' — '+p['title'],'','Acceptance: '+p['closure_evidence'],'','Next ('+p['next_step']+'): '+p['next_action'],'','Limits: '+p['limits'],'']
    (H/'remaining-work.md').write_text('\n'.join(ptext)+'\n')
    assert all(digest(R/p)==h for p,h in locks.items())
    counts=dict(original_MC_conditions=35,obligations=53,interactions=6,operations=46,literature=9,packages=18,broad_closures=0)
    dump(H/'verification.json',dict(passed=True,counts=counts,protected_files=len(locks),original_wording_preserved=True,all_current_actions_assigned=True,recursive_predecessor_copies=False,scope_waivers=0,independent_acceptance=False))
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=R,capture_output=True,text=True)
    dump(H/'run-manifest.json',dict(command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/acceptance-priority-20261027/reconcile.py',git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable; existing marker is not a usable repository',environment=sys.version,cpu_gpu='CPU only; GPU intentionally hidden',data_version=locks[str((OLD/'audit-status.json').relative_to(R))],random_seeds='N/A deterministic document reconciliation',wall_seconds=time.monotonic()-start,timestamp_utc=datetime.now(timezone.utc).isoformat(),plan_file='docs/plans/accounting-master-acceptance-priority-20261027.md',result_file=str((H/'result.md').relative_to(R))))
    (H/'result.md').write_text('''# Acceptance decisions reconciled

27 October 2026. Governing candidate 5.51 is unchanged and not_ready.
All 35 original mission conditions are preserved exactly. The current index
covers 53 obligations, six interactions, 46 operations, nine literature rows
and all 18 package closure criteria. Each has a current package action; mission
rows have individually authored missing subconditions. Detailed non-mission
residuals are inherited and labelled, not represented as fresh technical audits.

Delivered source authoring, invariant and nested-term methods must not be
rebuilt. The immediate dependency is a reproducible normative bundle, followed
by cross-profile compatibility and integrated case closure. The Core 0 contract
and schema cited by 5.51 exist in the worktree but are missing from its source
directory. Execute accounting-release-bundle-recovery-20261027.md next.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Retain current acceptance index | Exact original wording, complete ID coverage and explicit next conditions pass | No lost conditions or changed protected evidence | Full compatibility inventory and independent acceptance are pending | Repair C1 bundle dependencies and continue C2 consolidation | No broad requirement/package closure or production/forecast readiness |

The strongest alternative explanation is that a detailed residual is already
satisfied by a later profile. Consequently this index forbids adding a language
primitive until the current consumer and successor evidence are checked.
The term-event frontend already executes complete rules and chained results;
its one-rule parser alone does not establish an implementation gap. Completed
coupon resume, recovery intake and insurance call-chain audit move to evidence,
not the active execution queue. Source/factual gaps continue to block only
dependent conclusions. S1–S5 remain partial; S6 held; E3 deferred.

C0's documentary reconciliation is complete within this scope; final independent
acceptance and comprehensive claim/profile inventory are still required. No
scope waiver, external engagement or new scientific ranking is introduced.
''')
    print(json.dumps(dict(passed=True,counts=counts,protected_files=len(locks),next_plan='accounting-release-bundle-recovery-20261027.md')))

if __name__=='__main__':main()
