"""Record the reviewed successor and preserve historical control fields."""
from pathlib import Path
from hashlib import sha256
import json,platform,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];REL=HERE.relative_to(ROOT).as_posix()
PLAN='docs/plans/accounting-method-input-binding-20261024.md'
PDF='docs/design/proposal/manuscript-method-requirements-20261024/accounting-product-proposal.pdf'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def main():
    assert not (HERE/'control-refresh.json').exists()
    from verify import verify
    v=verify();assert v==json.loads((HERE/'verification.json').read_text()) and v['passed']
    names=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md',
        'docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md',
        'docs/plans/accounting-product-design-checkpoint.md','data/accounting-master/next-plan.md',
        'data/accounting-master/simulator-session-20261023.md','data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
    note='\n'.join(['## Current candidate Version 3.59 — 24 October 2026','',
        'Version 3.59 is 429 pages, not_ready. PDF: '+PDF+'.',
        'SHA256: '+v['pdf_sha256']+'.',
        'Reusable typed method requirements and matched text/exchange are integrated.',
        'Core:197 checks and 35 selected comparisons; authoring:139 checks, 19 unit methods.',
        'All 154 predecessor sources and its PDF remain protected; 320 labels,',
        '111 references, 738 citations and 227 exact displays are retained.',
        'Clean build and bounded rendered author review pass; whole-document,',
        'independent/domain/human acceptance remain pending.',
        'Result: '+REL+'/result.md.','',
        'Next: '+PLAN+'.',
        'Bind requirements to explicit typed records with immutable source identity,',
        'context and unknown conventions; preserve residual full-method prerequisites.',
        'S1–S5 partial; S6 held; S7 deferred. No whole requirement closes.','',''])
    before={}
    for name in names:
        p=ROOT/name;before[name]=sha(p);dest=HERE/'control-before'/name
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
        if name.endswith('.md'):
            title,rest=p.read_text().split('\n',1)
            if 'simulator-session' in name:rest='No command running. Preserve recorded packages and dirty work.\nNo commit/subagents/controller campaign/outreach/forecast experiment.\n'
            p.write_text(title+'\n\n'+note+rest.lstrip('\n'))
    for name,key in [('data/accounting-master/next-plan.json','active_execution'),('scripts/accounting_master_catalog.json','active_execution_note')]:
        p=ROOT/name;d=json.loads(p.read_text());old={k:x for k,x in d.items() if k!=key};a=d[key]
        a.update(active_work_plan=PLAN,latest_result=REL+'/result.md',updated='2026-10-24')
        if key=='active_execution':
            a['current_candidate']={'version':'3.59','pages':429,'status':'not_ready','pdf':PDF,'sha256':v['pdf_sha256']}
            a['latest_results'].append(REL+'/result.md')
            a['completed_increments'].append('Version3.59:429 pages;154 protected predecessor sources;bounded rendered review;not_ready')
            a['next'][0]='Declarative requirement-input binding with pinned record identity and explicit context/unknown semantics'
        else:a['current_candidate']='3.59;429 pages;not_ready'
        dump(p,d);assert old=={k:x for k,x in json.loads(p.read_text()).items() if k!=key}
    dump(HERE/'render-review.json',{'pdf_sha256':v['pdf_sha256'],'pages_inspected':[1,98,400,401,402,403],
        'continuous_segments':[[400,401,402,403]],'review':'review.md','reviewer':'author',
        'whole_document_review':'pending','independent_reader':'pending','human_acceptance':'pending'})
    dump(HERE/'coverage-delta.json',{'advanced':['MC05','MC10','MC13','MC15','MC17','MC24','MC26','MC27','MC31','MC32','MC33','MC34'],'whole_rows_closed':0,
        'remaining':'general input binding,full method applicability,latent state and independent/domain/human acceptance'})
    dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names},'legacy_json_fields_unchanged':True})
    build=json.loads((HERE/'build.json').read_text())
    dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'command':build['command'],'environment':{'python':platform.python_version(),**build['environment']},
        'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A: deterministic build',
        'data_version':json.loads((HERE/'baseline.json').read_text()),'wall_seconds':build['wall_seconds'],
        'output_artifacts':{PDF:sha(ROOT/PDF),**{str(p.relative_to(ROOT)):sha(p) for p in HERE.iterdir() if p.suffix in ['.py','.json','.md'] and p.name!='run-manifest.json'}},
        'plan':'docs/plans/accounting-method-requirement-integration-20261024.md','result':REL+'/result.md'})
    print(json.dumps({'candidate':'3.59','pages':429,'controls':len(names),'next':PLAN}))
if __name__=='__main__':main()
