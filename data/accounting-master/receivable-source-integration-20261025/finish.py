"""Advance active controls after additive verification and rendered review."""
from hashlib import sha256
from pathlib import Path
import json
import platform
import runpy
import subprocess
import sys

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];REL=HERE.relative_to(ROOT).as_posix()
NEXT='docs/plans/accounting-native-group-binding-20261025.md'
PRIOR='data/accounting-master/populated-source-contracts-20261025/coverage.json'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+chr(10))

def main():
    assert not (HERE/'control-refresh.json').exists()
    check=runpy.run_path(str(HERE/'integrate.py'))['verify']()
    assert check==json.loads((HERE/'integration-verification.json').read_text())
    dump(HERE/'replay-observation.json',{'passed':True,'mode':'read_only_integration_verification',
        'pdf_sha256':check['pdf_sha256'],'source_files':check['protected_sources']})
    images={str((HERE/('page-'+str(p)+'.png')).relative_to(ROOT)):sha(HERE/('page-'+str(p)+'.png')) for p in [1,398,399,400,401]}
    dump(HERE/'render-review.json',{'author_review_complete':True,'independent_reader_pending':True,
        'whole_document_review':False,'pages':[1,398,399,400,401],'pdf_sha256':check['pdf_sha256'],'images':images,
        'review':REL+'/review.md','review_sha256':sha(HERE/'review.md')})
    prior=json.loads((ROOT/PRIOR).read_text())
    advanced={'MC02','MC04','MC05','MC08','MC11','MC13','MC16','MC24','MC25','MC26','MC27','MC28','MC30','MC32','MC34','MC35'}
    inventory={'schema':'accdsl.coverage.references.v1','date':'2026-10-25','candidate':'4.21',
        'readiness':'not_ready','baseline':{'path':PRIOR,'sha256':sha(ROOT/PRIOR)},'next_plan':NEXT,'whole_rows_closed':0}
    for group,count in [('obligations',53),('interactions',6),('operations',46)]:
        assert len(prior[group])==len({r['id'] for r in prior[group]})==count
        inventory[group]=[]
        for row in prior[group]:
            changed=group=='obligations' and row['id'] in advanced
            inventory[group].append({'id':row['id'],'prior_ref':{'path':PRIOR,'collection':group,'id':row['id'],
                'sha256':sha256(json.dumps(row,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()},
                'assessment':'scoped_advance_remaining_open' if changed else 'prior_scope_retained_not_reaudited',
                'advance':'Checked claim evidence, retained disclosure limitations and partial populations integrated in 4.21.' if changed else 'No new evidence assigned.',
                'residual':'Actual claims, complete methods, group/sector composition and full design acceptance remain open.',
                'evidence':[REL+'/result.md',REL+'/integration-verification.json',REL+'/review.md'] if changed else [],
                'full_requirement_closed':False,'acceptance':'not_promoted'})
    dump(HERE/'coverage.json',inventory)
    note=f'''## Claim evidence integrated — 25 October 2026

Version 4.21: {check['pages']} pages, not_ready.
PDF: {check['pdf']}
SHA256: {check['pdf_sha256']}.
Constructed-source contracts: 20 focused/85 regression tests and four cases.
Retained disclosures: seven tests, three views, 12 observations and 18 requirements.
Partial populations: eight focused/23 regression tests; three source views and
three constructed examples. All exact replays pass. Source and actual execution
admission stay false. Vendor non-trade treatment differs from the credit-sale method.
All 174 predecessor sources and existing mathematics/citations remain protected.
Cover and pages 398–401 were viewed; no new warnings remain. Five inherited
underfull notices remain. Whole-document and independent/domain/human review are pending.
All 53 obligations, 6 interactions and 46 operations remain; zero whole requirements close.
Result: {REL}/result.md. Next: {NEXT}.
S1–S5 partial; S6 held; S7 deferred. Forecasting remains deferred.

'''
    phase='''Mission: represent disclosed company histories and alternatives, then simulate
explicit economic events into coherent journals, statements and notes.

| Phase | Remaining work | Status |
|---|---|---|
| S1 Research | Consequential source inspection and build/reuse comparison | Partial |
| S2 Architecture | Native group binding, broader sector composition and actual claim state | Partial |
| S3 Language | Amendments, broader measurements, method authoring and fiscal policies | Partial |
| S4 Conformance | Real-source whole-company cases, integrated sector methods and recovery | Partial |
| S5 Governing design | Full implementability, source, domain and human review | Partial |
| S6 Product implementation | Await sufficiently settled governing specification | Held |
| S7 Predictive evaluation | Saved E3 choices retained; simulator design comes first | Deferred |

Current question: which native group records can bind to the company-world
interface without substituting a consolidated state for a legal book?
Next action: execute docs/plans/accounting-native-group-binding-20261025.md.
Preserve frozen evidence and unrelated work. No background campaign or paid outreach.
'''
    names=['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md',
        'docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md',
        'docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md',
        'data/accounting-master/next-plan.md','data/accounting-master/simulator-session-20261023.md',
        'data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
    before={}
    for name in names:
        p=ROOT/name;before[name]=sha(p);b=HERE/'control-before'/name;b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes(p.read_bytes())
        if p.suffix=='.md':
            title,rest=p.read_text().split(chr(10),1)
            if name.endswith(('accounting-master-current.md','accounting-current-program-20261025.md','simulator-session-20261023.md')):rest=phase
            p.write_text(title+chr(10)*2+note+rest.lstrip(chr(10)))
    p=ROOT/'data/accounting-master/next-plan.json';data=json.loads(p.read_text());active=data['active_execution']
    active.update(updated='2026-10-25',active_work_plan=NEXT,latest_result=REL+'/result.md',
        current_candidate={'version':'4.21','pages':check['pages'],'status':'not_ready','pdf':check['pdf'],'sha256':check['pdf_sha256']})
    for name in ['partial-claim-populations-20261025',HERE.name]:
        result='data/accounting-master/'+name+'/result.md'
        if result not in active['latest_results']:active['latest_results'].append(result)
    active['completed_increments'].append('Partial claim populations reuse existing collections; Version 4.21 integrates three checked increments, preserves 174 sources, and passes bounded rendered review')
    active['next'][0]='Audit and bind retained native group/legal-book records without flattening sector state'
    dump(p,data)
    p=ROOT/'scripts/accounting_master_catalog.json';data=json.loads(p.read_text())
    data['active_execution_note'].update(updated='2026-10-25',latest_result=REL+'/result.md',active_work_plan=NEXT,current_candidate='4.21;517 pages;not_ready');dump(p,data)
    dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names},'legacy_json_fields_preserved':True})
    artifact_names=['integration-baseline.json','integration-verification.json','build.json','build.log','source-lock.json',
        'replay-observation.json','render-review.json','review.md','result.md','coverage.json','surface.json','addition-surface.json','control-refresh.json','finish.py']
    dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'worktree':'Uncommitted local work; source/evidence locks identify executed bytes',
        'command':'python3 -B data/accounting-master/receivable-source-integration-20261025/integrate.py prepare; build; verify; finish.py',
        'environment':sys.version,'platform':platform.platform(),'cpu_gpu':'CPU Python/LuaLaTeX; GPU intentionally hidden for build',
        'seeds':'N/A: deterministic','wall_seconds':json.loads((HERE/'build.json').read_text())['wall_seconds'],
        'data_version':'Three locked receivable reference increments',
        'plan':'docs/plans/accounting-receivable-source-integration-20261025.md','result':REL+'/result.md',
        'artifact_hashes':{n:sha(HERE/n) for n in artifact_names},'pdf_sha256':check['pdf_sha256']})
    print(json.dumps({'passed':True,'candidate':'4.21','pages':check['pages'],'coverage':[53,6,46],'controls':len(names),'next':NEXT}))

if __name__=='__main__':main()
