"""Record this bounded repair once; later calls only replay preservation."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import platform
import sys
from check_candidate import check

U=Path(__file__).resolve().parent
R=U.parents[2]
P=R/'data/accounting-master/readability-repair-20261021'
C=R/'docs/design/proposal/manuscript-readability-20261022'
PDF=C/'accounting-product-proposal.pdf'
EXPECTED='b8003bfde4755e171f057588679b6b7a3cedf95685342e6ca438408e34bdd8db'
PLAN=R/'docs/plans/accounting-readability-repair-20261022.md'
AMENDMENT=R/'docs/plans/accounting-readability-repair-20261022-amendment.md'
DELTA='Version3.47 repairs seven diagnosed prose/navigation defects and thirteen literature author-subject agreement passages. All mathematics, citations and qualifications remain. Local rendered review only; full3.47 regression and independent/domain/human acceptance remain pending. Zero whole-row closures.'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
rel=lambda p:str(p.relative_to(R))
bind=lambda p:{'path':rel(p),'sha256':sha(p)}

def write(name,value):
    with (U/name).open('x') as f:
        json.dump(value,f,indent=2,ensure_ascii=False);f.write(chr(10))

def preservation():
    old,new=load(P/'assessment-successor.json'),load(U/'assessment-successor.json')
    keys=('id','label','original_obligation','acceptance','recorded_status','historical_status')
    checks=[{'name':a['id'],'passed':all(a[k]==b[k] for k in keys)} for a,b in zip(old['rows'],new['rows'])]
    checks += [{'name':'all53','passed':len(old['rows'])==len(new['rows'])==53},
        {'name':'six-interactions','passed':len(new['interactions'])==6 and all(all(a[k]==b[k] for k in ('id','question','status')) for a,b in zip(old['interactions'],new['interactions']))}]
    a,b=load(P/'operation-successor.json'),load(U/'operation-successor.json')
    ops=[{'name':x['id'],'passed':all(x[k]==y[k] for k in ('id','operation','original_row')) and y['full_requirement_closed'] is False} for x,y in zip(a['rows'],b['rows'])]
    assert len(ops)==len(b['rows'])==46 and all(x['passed'] for x in checks+ops)
    assert new['readiness']=='not_ready' and new['candidate_pdf_sha256']==EXPECTED
    return checks,ops

def record():
    assert not any((U/n).exists() for n in ('completion.json','assessment-successor.json','operation-successor.json','rendered-review.json','run-manifest.json'))
    for name in ('review.md','result.md','execution-audit.md'):assert (U/name).stat().st_size>100
    rendered=load(U/'render-final-manifest.json')
    assert rendered['pdf_sha256']==EXPECTED and len(rendered['renders'])==26
    for row in rendered['renders']:assert sha(R/row['path'])==row['sha256']
    write('rendered-review.json',{'candidate_version':'3.47','pdf':bind(PDF),
        'ordered_local_segments':rendered['segments'],
        'provenance':'Actual final-build image calls in this continuation; all 26 pages read in local segment order',
        'renders':rendered['renders'],
        'review':bind(U/'review.md'),'full_regression':'pending','independent_reader':'pending','human_acceptance':'pending'})
    evidence=[bind(U/n) for n in ('result.md','review.md','execution-audit.md','candidate-checks.json','build-manifest.json','rendered-review.json')]
    evidence += [bind(P/'regression/completion.json'),bind(P/'regression/document-synthesis.md')]
    new=deepcopy(load(P/'assessment-successor.json'))
    new.update(date='2026-10-22',candidate_version='3.47',candidate_pdf=rel(PDF),candidate_pdf_sha256=EXPECTED,
        predecessor=rel(P/'assessment-successor.json'),predecessor_sha256=sha(P/'assessment-successor.json'),
        assessment_scope=DELTA,author_review_status='local_repairs_complete_full_3.47_regression_pending')
    new['historical_3.46_author_diagnosis']=bind(P/'regression/completion.json')
    new['prior_additive_supplements']=[*new.get('prior_additive_supplements',[]),*[bind(p) for p in sorted(P.glob('*-supplement.json'))]]
    affected={'MC04','MC18','MC23','MC25','MC29','MC30','MC32','MC33','MC34','MC35','G2','G4','G6','G7','G8','G10','G13','G16','G17'}
    for row in new['rows']:
        row.update(previous_candidate_version='3.46',candidate_version='3.47',candidate_pdf=rel(PDF),candidate_pdf_sha256=EXPECTED,
            delta_assessment=DELTA if row['id'] in affected else 'Inherited substantive assessment; bounded prose repair supplies no new method acceptance.')
        if row['id'] in affected:row.setdefault('evidence_updates',[]).extend(deepcopy(evidence))
    for row in new['interactions']:row['current_candidate_review']='Interaction assessment preserved; bounded prose/source-scope repair does not establish new cross-domain acceptance.'
    write('assessment-successor.json',new)
    ops=deepcopy(load(P/'operation-successor.json'))
    ops.update(candidate_version='3.47',candidate_pdf=rel(PDF),candidate_pdf_sha256=EXPECTED,
        recorded_utc=datetime.now(timezone.utc).isoformat(),current_increment=DELTA,
        predecessor=rel(P/'operation-successor.json'),predecessor_sha256=sha(P/'operation-successor.json'))
    write('operation-successor.json',ops)
    checks,opchecks=preservation()
    write('assessment-checks.json',{'checks':len(checks),'failures':0,'detail':checks})
    write('operation-checks.json',{'checks':len(opchecks),'failures':0,'detail':opchecks})
    protection=load(U/'protection.json')
    manifest=load(U/'build-manifest.json')
    write('run-manifest.json',{'git_commit':protection['head'],'branch':protection['branch'],
        'environment':sys.executable,'python':platform.python_version(),'cpu_gpu':'CPU only; GPU devices intentionally hidden',
        'data_version':'Protected3.46 and bounded prose-only3.47; no financial data changed',
        'seeds':'N/A deterministic document repair','wall_seconds_final_build':manifest['wall_seconds'],
        'started_utc':protection['started_utc'],'recorded_utc':datetime.now(timezone.utc).isoformat(),
        'commands':['prepare.py','build_candidate.py','check_candidate.py','render_local.py','amend_grammar.py','build_attempt2.py','render_final.py','verify.py --record','verify.py'],
        'command_scope':'All Python commands use CUDA_VISIBLE_DEVICES=-1, tfgpu python3 and -B; exact build command is bound below',
        'build':bind(U/'build-manifest.json'),'first_build':bind(U/'attempts/1/build-manifest.json'),
        'plan':bind(PLAN),'amendment':bind(AMENDMENT),'result':bind(U/'result.md'),'output':rel(U)})
    write('integration-bindings.json',{'pdf':bind(PDF),'assessment':bind(U/'assessment-successor.json'),
        'operations':bind(U/'operation-successor.json'),'evidence':evidence,'status':'not_ready','whole_rows_closed':0,
        'scope':'Completed local repair; future regression and live controls remain separate'})
    files=[p for p in U.rglob('*') if p.is_file() and not any(x in p.relative_to(U).parts for x in ('__pycache__','regression','controls-after'))]
    files += [p for p in C.rglob('*') if p.is_file()]+[PLAN,AMENDMENT]
    write('completion.json',{'bindings':{rel(p):sha(p) for p in sorted(set(files))},
        'policy':'Local repair evidence immutable; subsequent regression and control updates are additive.'})

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record',action='store_true');args=parser.parse_args()
    assert check()==load(U/'candidate-checks.json') and sha(PDF)==EXPECTED
    for name,digest in load(U/'attempts/1/preservation.json')['bindings'].items():assert sha(R/name)==digest,name
    if args.record:record()
    checks,ops=preservation()
    for name,digest in load(U/'completion.json')['bindings'].items():assert sha(R/name)==digest,name
    assert load(U/'assessment-checks.json')['detail']==checks
    assert load(U/'operation-checks.json')['detail']==ops
    print(json.dumps({'status':'recorded and verified' if args.record else 'read-only replay passed',
        'version':'3.47','pages':401,'assessment_checks':len(checks),'operations':len(ops),
        'protected_files':len(load(U/'protection.json')['protected']),'completion_bindings':len(load(U/'completion.json')['bindings']),
        'whole_rows_closed':0,'readiness':'not_ready'}))

if __name__=='__main__':main()
