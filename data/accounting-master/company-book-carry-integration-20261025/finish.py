"""Record the reviewed successor and preserve historical control fields."""
from pathlib import Path
from hashlib import sha256
import json,platform,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];REL=HERE.relative_to(ROOT).as_posix()
PLAN='docs/plans/accounting-company-book-carry-coverage-20261025.md'
PDF='docs/design/proposal/manuscript-company-carry-20261025/accounting-product-proposal.pdf'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def main():
    assert not (HERE/'control-refresh.json').exists()
    from verify import verify
    v=verify();assert v==json.loads((HERE/'verification.json').read_text()) and v['passed']
    arithmetic=json.loads((HERE/'evidence-check.json').read_text());assert arithmetic['passed']
    review=json.loads((HERE/'render-review-final.json').read_text());assert review['pdf_sha256']==v['pdf_sha256'] and review['author_review_complete']
    assert (HERE/'result.md').exists() and (HERE/'review.md').exists()
    for name,h in arithmetic['protected_evidence'].items():assert sha(ROOT/name)==h,name
    assert (ROOT/PLAN).exists()
    names=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md',
        'docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md',
        'docs/plans/accounting-product-design-checkpoint.md','data/accounting-master/next-plan.md',
        'data/accounting-master/simulator-session-20261023.md','data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
    note='\n'.join(['## Current candidate Version 4.09 — 25 October 2026','',
        'Version 4.09 is 507 pages, not_ready. PDF: '+PDF+'.',
        'SHA256: '+v['pdf_sha256']+'.',
        'Explicit provisional carry closes temporary balances and preserves declared memory policies.',
        'Source:15 focused and39 regression methods;43 comparisons across4 cases pass.',
        'All 174 predecessor sources and its PDF remain protected; 370 labels,',
        '150 references, 740 citations and 289 exact displays remain unchanged.',
        'Clean build and bounded rendered author review pass; whole-document,',
        'independent/domain/human acceptance remain pending.',
        'Result: '+REL+'/result.md.','',
        'Next: '+PLAN+'.',
        'Refresh all 53 obligations, six interactions and 46 operations,',
        'then execute the next substantive repair without drifting into forecasting.',
        'S1–S5 partial; S6 held; S7 deferred. No whole requirement closes.','',''])
    before={}
    for name in names:
        p=ROOT/name;before[name]=sha(p);dest=HERE/'control-before'/name
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
        if name.endswith('.md'):
            title,rest=p.read_text().split('\n',1)
            if 'simulator-session' in name or 'master-current' in name:rest='No command running. Preserve recorded packages and dirty work.\nNo commit/subagents/controller campaign/outreach/forecast experiment.\n'
            p.write_text(title+'\n\n'+note+rest.lstrip('\n'))
    for name,key in [('data/accounting-master/next-plan.json','active_execution'),('scripts/accounting_master_catalog.json','active_execution_note')]:
        p=ROOT/name;d=json.loads(p.read_text());old={k:x for k,x in d.items() if k!=key};a=d[key]
        a.update(active_work_plan=PLAN,latest_result=REL+'/result.md',updated='2026-10-25')
        if key=='active_execution':
            a['current_candidate']={'version':'4.09','pages':507,'status':'not_ready','pdf':PDF,'sha256':v['pdf_sha256']}
            a['latest_results'].append(REL+'/result.md')
            a['completed_increments'].append('Version4.09:507 pages;174 protected predecessor sources;bounded rendered review;not_ready')
            a['next'][0]='Refresh complete coverage and select the next distinct simulator dependency'
        else:a['current_candidate']='4.09;507 pages;not_ready'
        dump(p,d);assert old=={k:x for k,x in json.loads(p.read_text()).items() if k!=key}
    dump(HERE/'render-review.json',{'pdf_sha256':v['pdf_sha256'],'pages_inspected':[1,389,390,391,392],
        'continuous_segments':[[389,390,391,392]],'review':'review.md','reviewer':'author',
        'whole_document_review':'pending','independent_reader':'pending','human_acceptance':'pending'})
    dump(HERE/'coverage-delta.json',{'advanced':['MC02','MC06','MC11','MC13','MC14','MC15','MC16','MC18','MC23','MC24','MC25','MC26','MC28','MC32','MC34','MC35'],'whole_rows_closed':0,
        'remaining':'broader language/module coverage,real-source historical feasibility,latent state and independent/domain/human acceptance'})
    dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names},'legacy_json_fields_unchanged':True})
    build=json.loads((HERE/'build.json').read_text())
    dump(HERE/'run-manifest.json',{'git_commit':'03fea070f089821f4759e49a4466a3399b7fc078',
        'command':build['command'],'environment':{'python':platform.python_version(),**build['environment']},
        'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A: deterministic build',
        'data_version':json.loads((HERE/'baseline.json').read_text()),'wall_seconds':build['wall_seconds'],
        'output_artifacts':{PDF:sha(ROOT/PDF),**{str(p.relative_to(ROOT)):sha(p) for p in (ROOT/PDF).parent.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark']},**{str(p.relative_to(ROOT)):sha(p) for p in HERE.iterdir() if p.suffix in ['.py','.json','.md','.tex','.png'] and p.name!='run-manifest.json'}},
        'plan':'docs/plans/accounting-company-book-carry-integration-20261025.md','result':REL+'/result.md'})
    print(json.dumps({'candidate':'4.09','pages':507,'controls':len(names),'next':PLAN}))
if __name__=='__main__':main()
