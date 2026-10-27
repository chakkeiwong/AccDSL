"""Publish local candidate checkpoint while preserving historical controls."""
from pathlib import Path
from hashlib import sha256
import json,platform,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];REL=HERE.relative_to(ROOT).as_posix()
PLAN='docs/plans/accounting-company-composed-profile-20261024.md'
PDF='docs/design/proposal/manuscript-company-returns-20261024/accounting-product-proposal.pdf'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def main():
    assert not (HERE/'control-refresh.json').exists()
    from verify import verify
    v=verify();assert v==json.loads((HERE/'verification.json').read_text()) and v['passed']
    names=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md',
        'docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md',
        'docs/plans/accounting-product-design-checkpoint.md','data/accounting-master/next-plan.md',
        'data/accounting-master/simulator-session-20261023.md','data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
    note=('## Current candidate Version 3.56 — 24 October 2026\n\n'
        'Version 3.56 is 421 pages, not_ready. PDF: '+PDF+'.\n'
        'SHA256: '+v['pdf_sha256']+'.\n'
        'The return authoring (107 checks) and shared-book execution reference\n'
        '(253 checks) are integrated. All 151 predecessor sources and its PDF\n'
        'remain protected; 312 labels, 101 references, 733 citations and 222\n'
        'exact displays are retained. Clean build and bounded rendered author\n'
        'review pass; whole-document, independent/domain/human acceptance pending.\n'
        'Result: '+REL+'/result.md.\n\n'
        'Next: '+PLAN+'.\n'
        'Expose source opening, complete event schedule and native/retained\n'
        'method selection in one closed typed/text company composition.\n'
        'S1–S5 partial; S6 held; S7 deferred. No whole requirement closes.\n'
        'Earlier entries below are historical checkpoints.\n\n')
    before={}
    for name in names:
        p=ROOT/name;before[name]=sha(p);dest=HERE/'control-before'/name
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
        if name.endswith('.md'):
            title,rest=p.read_text().split('\n',1)
            if 'simulator-session' in name:rest='No active command. Preserve one-time recordings and dirty work.\nNo commit/subagents/controller campaign/outreach/forecast experiment.\nAuthoring/execution failures and layout repairs are preserved.\n'
            p.write_text(title+'\n\n'+note+rest.lstrip('\n'))
    for name,key in [('data/accounting-master/next-plan.json','active_execution'),('scripts/accounting_master_catalog.json','active_execution_note')]:
        p=ROOT/name;d=json.loads(p.read_text());old={k:x for k,x in d.items() if k!=key};a=d[key]
        a.update(active_work_plan=PLAN,latest_result=REL+'/result.md',updated='2026-10-24')
        if key=='active_execution':
            a['current_candidate']={'version':'3.56','pages':421,'status':'not_ready','pdf':PDF,'sha256':v['pdf_sha256']}
            a['latest_results'].append(REL+'/result.md')
            a['completed_increments'].append('Version3.56:421 pages;151 protected predecessor sources;bounded rendered review;not_ready')
            a['next'][0]='Explicit composed-company typed/text profile with caller-bound native and retained capabilities'
        else:a['current_candidate']='3.56;421 pages;not_ready'
        dump(p,d);assert old=={k:x for k,x in json.loads(p.read_text()).items() if k!=key}
    dump(HERE/'render-review.json',{'pdf_sha256':v['pdf_sha256'],'pages_inspected':[1,98,385,386,387,388,389],
        'continuous_segments':[[386,387,388]],'review':'review.md','reviewer':'author',
        'whole_document_review':'pending','independent_reader':'pending','human_acceptance':'pending'})
    dump(HERE/'coverage-delta.json',{'advanced':['MC08','MC10','MC13','MC18','MC24','MC25','MC28','MC34'],'whole_rows_closed':0,
        'remaining':'composed company profile,broader methods,source admission,durability and independent/domain/human acceptance'})
    dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names},'legacy_json_fields_unchanged':True})
    build=json.loads((HERE/'build.json').read_text())
    dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'command':build['command'],'environment':{'python':platform.python_version(),**build['environment']},
        'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A: deterministic build',
        'data_version':json.loads((HERE/'baseline.json').read_text()),'wall_seconds':build['wall_seconds'],
        'output_artifacts':{PDF:sha(ROOT/PDF),**{str(p.relative_to(ROOT)):sha(p) for p in HERE.iterdir() if p.suffix in ['.py','.json','.md'] and p.name!='run-manifest.json'}},
        'plan':'docs/plans/accounting-company-return-integration-20261024.md','result':REL+'/result.md'})
    print(json.dumps({'candidate':'3.56','pages':421,'controls':len(names),'next':PLAN}))
if __name__=='__main__':main()
