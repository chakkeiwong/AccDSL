"""Record this local integration once; later no-flag calls only verify."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import sys

sys.dont_write_bytecode = True
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['GIT_OPTIONAL_LOCKS'] = '0'
from check_candidate import check

U = Path(__file__).resolve().parent
R = U.parents[2]
P = R / 'data/accounting-master/early-conversion-integration-20261018'
C = R / 'docs/design/proposal/manuscript-reserve-risk-20261020'
PDF = C / 'accounting-product-proposal.pdf'
EXPECTED = '92b1ab24970cb301ba96d409edcadd3679fc778917c81e82b1c82da592e3dd0d'
PLAN = R / 'docs/plans/accounting-reserve-risk-integration-20261020.md'
DELTA = ('3.45 adds finite quantile/ES boundary mass, corrected PH weights, '
         'future-information expected-SD bounds, true-conditional-mean CDR '
         'variances and capital-charge timing. All earlier source content is '
         'preserved. Local author review covers 306–313 and separate title/contents. '
         'Full 3.45 regression and independent/domain/human acceptance remain '
         'pending. No whole-row closure.')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load(p):
    return json.loads(p.read_text())

def rel(p):
    return str(p.relative_to(R))

def bind(p):
    return {'path': rel(p), 'sha256': sha(p)}

def write(name, value):
    with (U / name).open('x') as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
        f.write(chr(10))

def preserve():
    a, b = load(P/'assessment-successor.json'), load(U/'assessment-successor.json')
    assert b['candidate_version'] == '3.45' and b['readiness'] == 'not_ready'
    assert b['candidate_pdf_sha256'] == EXPECTED and len(a['rows']) == len(b['rows']) == 53
    keys = ('id', 'label', 'original_obligation', 'acceptance', 'recorded_status', 'historical_status')
    ac = [{'name': x['id'], 'passed': all(x[k] == y[k] for k in keys)}
          for x, y in zip(a['rows'], b['rows'])]
    ac += [{'name': 'all53', 'passed': len(b['rows']) == 53},
           {'name': 'six-interactions', 'passed': len(b['interactions']) == 6 and
            all(all(x[k] == y[k] for k in ('id','question','status'))
                for x,y in zip(a['interactions'],b['interactions']))}]
    old,new = load(P/'operation-successor.json'),load(U/'operation-successor.json')
    oc = [{'name':x['id'],'passed':all(x[k]==y[k] for k in ('id','operation','original_row'))
           and y['full_requirement_closed'] is False} for x,y in zip(old['rows'],new['rows'])]
    assert len(oc)==len(new['rows'])==46 and all(x['passed'] for x in ac+oc)
    return ac,oc

def assessments(evidence):
    b=deepcopy(load(P/'assessment-successor.json'))
    b.update(date='2026-10-20',candidate_version='3.45',candidate_pdf=rel(PDF),
             candidate_pdf_sha256=EXPECTED,predecessor=rel(P/'assessment-successor.json'),
             predecessor_sha256=sha(P/'assessment-successor.json'),assessment_scope=DELTA,
             author_review_status='local_integration_complete_full_3.45_regression_pending')
    b['historical_3.44_author_regression']=bind(P/'author-regression-supplement.json')
    b['prior_additive_supplements']=[bind(p) for p in sorted(P.glob('*-supplement.json'))]
    affected={'MC10','MC11','MC12','MC18','MC22','MC26','MC29','MC30','MC32','MC33','MC34','MC35',
              'G7','G8','G10','G16','G17'}
    for row in b['rows']:
        row.update(previous_candidate_version='3.44',candidate_version='3.45',
                   candidate_pdf=rel(PDF),candidate_pdf_sha256=EXPECTED,
                   delta_assessment=DELTA if row['id'] in affected else
                   'Inherited obligation/method judgment; not freshly reviewed by this integration.')
        if row['id'] in affected: row.setdefault('evidence_updates',[]).extend(deepcopy(evidence))
    for row in b['interactions']:
        row['current_candidate_review']='Inherited interaction judgment; local finite-risk integration does not establish full cross-domain acceptance.'
    write('assessment-successor.json',b)
    new=deepcopy(load(P/'operation-successor.json'))
    new.update(candidate_version='3.45',candidate_pdf=rel(PDF),candidate_pdf_sha256=EXPECTED,
               recorded_utc=datetime.now(timezone.utc).isoformat(),current_increment=DELTA,
               predecessor=rel(P/'operation-successor.json'),predecessor_sha256=sha(P/'operation-successor.json'))
    for row in new['rows']:
        if row['id'] in ('P17-07.07','P17-07.08'):
            row['current_increment']=DELTA
            row['evidence'].extend(deepcopy(evidence))
    write('operation-successor.json',new)
    ac,oc=preserve()
    write('assessment-checks.json',{'checks':len(ac),'failures':0,'detail':ac})
    write('operation-checks.json',{'checks':len(oc),'failures':0,'detail':oc})

def record():
    names=('completion.json','assessment-successor.json','operation-successor.json',
           'rendered-review.json','run-manifest.json','integration-bindings.json',
           'assessment-checks.json','operation-checks.json')
    assert not any((U/n).exists() for n in names),'one-time recording already started'
    for n in ('review.md','result.md','execution-audit.md'):
        assert (U/n).is_file() and (U/n).stat().st_size>100
    write('rendered-review.json',{
        'candidate_version':'3.45','pdf':bind(PDF),
        'ordered_local_physical_pages':list(range(306,314)),
        'ordered_read_provenance':'Final-build 3+3+2 image calls retained in recovered conversation',
        'separate_local_physical_pages':[1,6],
        'recovery_read_provenance':'Title and contents actually viewed after recovery',
        'renders':[dict(page=n,**bind(U/'rendered'/f'page-{n:03}.png')) for n in [1,6,*range(306,314)]],
        'review':bind(U/'review.md'),'display_judgments':11,'cold_reader_answers':6,
        'whole_document_regression':'pending','independent_reader':'pending',
        'human_acceptance':'pending','readiness':'not_ready'})
    evidence=[bind(U/n) for n in ('result.md','review.md','rendered-review.json',
              'candidate-checks.json','build-manifest.json','execution-audit.md')]
    evidence += [bind(R/'data/accounting-master/r04-reserve-risk-20261020'/n)
                 for n in ('result.md','method-note.md','comparison.json','completion.json')]
    assessments(evidence)
    protection=load(U/'protection.json');snapshots={}
    for name in protection['controls']:
        p=U/'controls-after'/name
        p.parent.mkdir(parents=True,exist_ok=True)
        with p.open('xb') as f: f.write((R/name).read_bytes())
        snapshots[rel(p)]=sha(p)
    now=datetime.now(timezone.utc)
    prefix='CUDA_VISIBLE_DEVICES=-1 '+sys.executable+' -B '
    write('run-manifest.json',{
        'git_commit':protection['head'],'branch':protection['branch'],
        'environment':sys.executable,'python':platform.python_version(),
        'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1; GPU devices intentionally hidden',
        'data_version':'Protected3.44 and locked3.45; retained accepted manuscript and authored finite laws',
        'seeds':'N/A deterministic documentary integration','build':bind(U/'build-manifest.json'),
        'build_wall_seconds':load(U/'build-manifest.json')['wall_seconds'],
        'started_utc':protection['started_utc'],'recorded_utc':now.isoformat(),
        'elapsed_to_record_seconds':(now-datetime.fromisoformat(protection['started_utc'])).total_seconds(),
        'elapsed_scope':'Includes pauses and recovery; not CPU runtime',
        'commands':[prefix+rel(U/'check_candidate.py'),prefix+rel(U/'verify.py')+' --record',prefix+rel(U/'verify.py')],
        'plan':bind(PLAN),'result':bind(U/'result.md'),'output':rel(U)})
    write('integration-bindings.json',{
        'pdf':bind(PDF),'assessment':bind(U/'assessment-successor.json'),
        'operations':bind(U/'operation-successor.json'),'evidence':evidence,
        'status':'not_ready','whole_rows_closed':0,
        'scope':'Completed local integration; subsequent reading and live controls excluded'})
    excluded=('__pycache__','regression','chapter12-ordered')
    files=[p for p in U.rglob('*') if p.is_file() and not any(x in p.relative_to(U).parts for x in excluded)]
    files += [p for p in C.rglob('*') if p.is_file()]+[PLAN]
    write('completion.json',{
        'bindings':{rel(p):sha(p) for p in sorted(set(files))},
        'controls_at_completion':snapshots,
        'control_replay_policy':'Live controls may advance; immutable snapshots remain.',
        'reading_policy':'Subsequent reading evidence is additive outside this manifest.'})

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record',action='store_true');args=parser.parse_args()
    assert check()==load(U/'candidate-checks.json') and sha(PDF)==EXPECTED
    if args.record:record()
    ac,oc=preserve()
    assert load(U/'assessment-checks.json')['detail']==ac
    assert load(U/'operation-checks.json')['detail']==oc
    done=load(U/'completion.json')
    for name,h in done['bindings'].items():assert sha(R/name)==h,name
    for item in load(U/'assessment-successor.json')['prior_additive_supplements']:
        assert sha(R/item['path'])==item['sha256'],item['path']
    print(json.dumps({'status':'recorded and verified' if args.record else 'read-only replay passed',
        'version':'3.45','pages':401,'protected_files':len(load(U/'protection.json')['protected']),
        'completion_bindings':len(done['bindings']),'assessment_checks':len(ac),
        'operations_preserved':len(oc),'whole_rows_closed':0,'readiness':'not_ready'}))

if __name__=='__main__':main()
