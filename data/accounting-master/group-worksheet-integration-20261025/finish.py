"""Refresh current controls after exact preservation and rendered review."""
from pathlib import Path
from hashlib import sha256
import json
import platform
import runpy
import subprocess
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];REL=HERE.relative_to(ROOT).as_posix()
NEXT='docs/plans/accounting-simulator-source-match-20261025.md'
PRIOR='data/accounting-master/receivable-source-integration-20261025/coverage.json'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+chr(10))
def main():
    assert not (HERE/'control-refresh.json').exists()
    check=runpy.run_path(str(HERE/'integrate.py'))['verify']()
    assert check==json.loads((HERE/'integration-verification.json').read_text())
    dump(HERE/'replay-observation.json',{'passed':True,'mode':'read_only_integration_verification','pdf_sha256':check['pdf_sha256']})
    pages=[1,402,403,404,405]
    dump(HERE/'render-review.json',{'author_review_complete':True,'independent_reader_pending':True,'whole_document_review':False,
        'pages':pages,'pdf_sha256':check['pdf_sha256'],'review':REL+'/review.md',
        'images':{str((HERE/('page-'+str(n)+'.png')).relative_to(ROOT)):sha(HERE/('page-'+str(n)+'.png')) for n in pages}})
    prior=json.loads((ROOT/PRIOR).read_text());advanced={'MC04','MC06','MC08','MC10','MC11','MC12','MC13','MC16','MC19','MC20','MC21','MC22','MC24','MC25','MC26','MC27','MC28','MC30','MC32','MC33','MC34','MC35'}
    coverage={'schema':'accdsl.coverage.references.v1','date':'2026-10-25','candidate':'4.22','readiness':'not_ready',
              'baseline':{'path':PRIOR,'sha256':sha(ROOT/PRIOR)},'next_plan':NEXT,'whole_rows_closed':0}
    for group,count in [('obligations',53),('interactions',6),('operations',46)]:
        assert len(prior[group])==len({r['id'] for r in prior[group]})==count
        coverage[group]=[]
        for row in prior[group]:
            changed=group=='obligations' and row['id'] in advanced
            coverage[group].append({'id':row['id'],'prior_ref':{'path':PRIOR,'collection':group,'id':row['id'],
                'sha256':sha256(json.dumps(row,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()},
                'assessment':'scoped_advance_remaining_open' if changed else 'prior_scope_retained_not_reaudited',
                'advance':'Exact native group selectors and a constructed compatible-book worksheet integrated in4.22.' if changed else 'No new evidence assigned.',
                'residual':'Actual source/method admission, broader group/sector methods and full design review remain open.',
                'evidence':[REL+'/result.md',REL+'/integration-verification.json',REL+'/review.md'] if changed else [],
                'full_requirement_closed':False,'acceptance':'not_promoted'})
    dump(HERE/'coverage.json',coverage)
    note=f'''## Group selections and worksheet integrated — 25 October 2026

Version 4.22: {check['pages']} pages, not_ready.
PDF: {check['pdf']}
SHA256: {check['pdf_sha256']}.
Native group binding: 11 focused/23 regression tests and two exact snapshot replays.
Compatible books: 16 focused/63 regression tests and two exact worksheet replays.
All 174 predecessor sources and existing mathematics/citations remain protected.
Cover and pages 402–405 were viewed; no new warnings. Five inherited underfull
notices remain. Whole-document and independent/domain/human review remain pending.
All 53 obligations, 6 interactions and 46 operations remain; zero whole requirements close.
Result: {REL}/result.md. Next: {NEXT}.
S1–S5 partial; S6 held; S7 deferred. Forecasting remains deferred.

'''
    phase=f'''Mission: represent disclosed company histories and alternatives, then simulate
explicit economic events into coherent journals, statements and notes.

| Phase | Remaining work | Status |
|---|---|---|
| S1 Research | Consequential source/version matching and build/reuse comparison | Partial |
| S2 Architecture | Broader group/sector methods and actual claim state | Partial |
| S3 Language | Amendments, broader measurements, method authoring and fiscal policies | Partial |
| S4 Conformance | Real-source whole-company cases, integrated sector methods and recovery | Partial |
| S5 Governing design | Full implementability, source, domain and human review | Partial |
| S6 Product implementation | Await sufficiently settled governing specification | Held |
| S7 Predictive evaluation | Saved E3 choices retained; simulator design comes first | Deferred |

Current question: which unresolved source/version match can change simulator reuse?
Next action: execute {NEXT} after checking the retained correspondence notes.
Preserve frozen evidence and unrelated work. No paid outreach or background campaign.
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
    p=ROOT/'data/accounting-master/next-plan.json';d=json.loads(p.read_text());a=d['active_execution']
    a.update(updated='2026-10-25',active_work_plan=NEXT,latest_result=REL+'/result.md',
        current_candidate={'version':'4.22','pages':check['pages'],'status':'not_ready','pdf':check['pdf'],'sha256':check['pdf_sha256']})
    for folder in ['compatible-book-composition-20261025',HERE.name]:
        result='data/accounting-master/'+folder+'/result.md'
        if result not in a['latest_results']:a['latest_results'].append(result)
    a['completed_increments'].append('Native group selectors and paired elimination worksheet integrated in Version4.22; exact replay and bounded rendered review pass')
    a['next'][0]='Review retained ACTUS mismatch, then inspect distinct official source/version routes; preserve unresolved claims';dump(p,d)
    p=ROOT/'scripts/accounting_master_catalog.json';d=json.loads(p.read_text())
    d['active_execution_note'].update(updated='2026-10-25',latest_result=REL+'/result.md',active_work_plan=NEXT,current_candidate='4.22;518 pages;not_ready');dump(p,d)
    dump(HERE/'control-refresh.json',{'before':before,'after':{name:sha(ROOT/name) for name in names}})
    for name in names:assert NEXT in (ROOT/name).read_text(),name
    artifacts=['integration-baseline.json','integration-verification.json','source-lock.json','build.json','build.log','review.md',
               'result.md','coverage.json','replay-observation.json','render-review.json','addition-surface.json','surface.json','control-refresh.json','finish.py']
    dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'command':'python3 -B data/accounting-master/group-worksheet-integration-20261025/integrate.py prepare; build; verify; finish.py',
        'environment':sys.version,'platform':platform.platform(),'cpu_gpu':'CPU Python/LuaLaTeX; GPU intentionally hidden for build',
        'data_version':'Version4.21 plus locked group selector/worksheet evidence','seeds':'N/A: deterministic',
        'wall_seconds':json.loads((HERE/'build.json').read_text())['wall_seconds'],
        'plan':'docs/plans/accounting-group-worksheet-integration-20261025.md','result':REL+'/result.md',
        'provenance':'Uncommitted local work; source locks identify executed bytes',
        'artifacts':{REL+'/'+name:sha(HERE/name) for name in artifacts}})
    print(json.dumps({'candidate':'4.22','pages':check['pages'],'controls':len(names),'coverage':[len(coverage[k]) for k in ['obligations','interactions','operations']],'next':NEXT}))
if __name__=='__main__':main()
