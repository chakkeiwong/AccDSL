"""Refresh current manuscript and next work while preserving legacy controls."""
from pathlib import Path
from hashlib import sha256
import json
import platform
import subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];REL=HERE.relative_to(ROOT).as_posix()
PLAN='docs/plans/accounting-company-return-schema-20261023.md'
PDF='docs/design/proposal/manuscript-company-modules-20261023/accounting-product-proposal.pdf'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def main():
    assert not (HERE/'control-refresh.json').exists()
    v=json.loads((HERE/'verification.json').read_text());assert v['passed'] and v['candidate_version']=='3.55'
    assert sha(ROOT/PDF)==v['pdf_sha256']
    from verify import verify
    assert verify()==v
    render={'pdf_sha256':v['pdf_sha256'],'pages_inspected':[1,98,108,382,383,384,385,386,387],
        'continuous_segments':[[383,384,385],[386,387]],'baseline_pages_inspected':[99,382,383],
        'review':'review.md','reviewer':'author','whole_document_review':'pending','independent_reader':'pending','human_acceptance':'pending'}
    dump(HERE/'render-review.json',render)
    names=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md',
        'docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md',
        'docs/plans/accounting-product-design-checkpoint.md','data/accounting-master/next-plan.md',
        'data/accounting-master/simulator-session-20261023.md','data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
    note=('## Current candidate Version 3.55 — portable and module design integrated\n\n'
        'Version 3.55 is 419 pages, not_ready. PDF: '+PDF+'.\n'
        'SHA256: '+v['pdf_sha256']+'.\n'
        'All 150 predecessor sources and its PDF remain protected; 308 labels,\n'
        '95 references, 729 citations and 219 exact displays are retained.\n'
        'Build/preservation and bounded rendered author review pass. Full\n'
        'successor, independent, domain and human acceptance remain pending.\n'
        'Result: '+REL+'/result.md.\n\n'
        'The candidate integrates portable legacy identity (62 checks), a finite\n'
        'shared-book return boundary (43), and native return-state design with\n'
        'the retained legal-book/tax/cash trace (93), all replayed. The indirect\n'
        'cash bridge explicitly includes 10 of opening interest paid. Native\n'
        'return parser/schema/execution remains unfinished; no whole row closes.\n\n'
        'Next: '+PLAN+'.\n'
        'Specify closed component/lot/tax records and matched typed/text\n'
        'authoring, preserving legacy scenarios. S1–S5 partial; S6 held;\n'
        'S7 deferred. Earlier entries below are historical checkpoints.\n\n')
    before={}
    for name in names:
        p=ROOT/name;before[name]=sha(p);dest=HERE/'control-before'/name
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
        if name.endswith('.md'):
            title,rest=p.read_text().split('\n',1)
            if 'simulator-session' in name:
                rest=('No active command. Preserve dirty work and all one-time recordings.\n'
                    'No commit/subagents/controller campaign/outreach/forecast experiment.\n'
                    'Read native-return-design/specification.md before new schema or code.\n'
                    'Portable:558 protected files. Module:22. Native design:19.\n'
                    'Preserved failures: helper collision, metadata decoder, report API shape,\n'
                    'and missing opening-interest cash-bridge term. All repaired and replayed.\n')
            p.write_text(title+'\n\n'+note+rest.lstrip('\n'))
    p=ROOT/'data/accounting-master/next-plan.json';d=json.loads(p.read_text());old={k:x for k,x in d.items() if k!='active_execution'}
    a=d['active_execution'];a.update(active_work_plan=PLAN,latest_result=REL+'/result.md',
        current_candidate={'version':'3.55','pages':419,'status':'not_ready','pdf':PDF,'sha256':v['pdf_sha256']})
    for result in ['data/accounting-master/company-native-return-design-20261023/result.md',REL+'/result.md']:
        if result not in a['latest_results']:a['latest_results'].append(result)
    a['completed_increments'] += ['Native return design:93 checks/replay;full retained legal trace;opening-interest bridge repaired',
        'Version3.55:419 pages;150 baseline sources and protected mathematics/citations retained;bounded rendered review;not_ready']
    a['next'][0]='Native return schema, exact typed/text authoring and capability conformance before reference engine integration'
    dump(p,d);assert old=={k:x for k,x in json.loads(p.read_text()).items() if k!='active_execution'}
    p=ROOT/'scripts/accounting_master_catalog.json';d=json.loads(p.read_text());old={k:x for k,x in d.items() if k!='active_execution_note'}
    d['active_execution_note'].update(active_work_plan=PLAN,latest_result=REL+'/result.md',current_candidate='3.55;419 pages;not_ready')
    dump(p,d);assert old=={k:x for k,x in json.loads(p.read_text()).items() if k!='active_execution_note'}
    dump(HERE/'coverage-delta.json',{'advanced':['MC08','MC10','MC13','MC18','MC24','MC25','MC28','MC34'],
        'whole_rows_closed':0,'evidence':REL+'/verification.json','remaining':'native integration,broader methods,real source admission,durability,independent/domain/human acceptance'})
    native=HERE.parent/'company-native-return-design-20261023'
    dump(native/'replay-observation.json',{'passed':True,'checks':93,'protected_files':19,'wall_seconds':0.05483943101717159,'read_only_replay':True})
    dump(native/'coverage-delta.json',{'whole_rows_closed':0,'evidence':'checks.json','integrated_candidate':'3.55',
        'remaining':'native schema/parser/executor integration and broader tax/lot methods'})
    dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names},'legacy_json_fields_unchanged':True,'whole_rows_closed':0})
    build=json.loads((HERE/'build.json').read_text())
    dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'command':build['command'],'environment':{'python':platform.python_version(),**build['environment']},
        'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A: deterministic document build',
        'data_version':json.loads((HERE/'baseline.json').read_text()),'wall_seconds':build['wall_seconds'],
        'output_artifacts':{PDF:sha(ROOT/PDF),**{str(p.relative_to(ROOT)):sha(p) for p in HERE.iterdir() if p.suffix in ['.py','.json','.md'] and p.name!='run-manifest.json'}},
        'plan':'docs/plans/accounting-company-module-integration-20261023.md','result':REL+'/result.md'})
    print(json.dumps({'candidate':'3.55','pages':419,'controls':len(names),'next':PLAN,'legacy_fields_unchanged':True}))
if __name__=='__main__':main()
