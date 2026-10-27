"""Read-only by default; record this target-definition unit once."""
import argparse
from datetime import datetime,timezone
import hashlib,json,os,platform,subprocess,sys,time
from pathlib import Path
from reference import check

U=Path(__file__).resolve().parent; R=U.parents[2]
PLAN=R/'docs/plans/accounting-r05-predictive-accuracy-target-20261023.md'
REVIEW=R/'data/accounting-master/readability-repair-20261022-theta'
SUPPLEMENT=REVIEW/'r05-predictive-accuracy-target-supplement.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest(); load=lambda p:json.loads(p.read_text())
rel=lambda p:str(p.relative_to(R)); bind=lambda p:{'path':rel(p),'sha256':sha(p)}
CONTROLS=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md',
          'docs/plans/accounting-mission-requirements.md','data/accounting-master/next-plan.md']


def write(p,v):
    with p.open('x') as f: json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')


def check_all():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    p=load(U/'protection.json')
    for n,d in p['protected'].items(): assert sha(R/n)==d,n
    assert sha(R/'.git/index')==p['index_sha256']
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==p['head']
    raw=subprocess.check_output(['git','status','--porcelain=v1','--untracked-files=no','-z'],cwd=R,text=True)
    rows=[r for r in raw.split('\0') if r]; assert all(r[:2]==' M' for r in rows)
    assert {r[3:] for r in rows}==set(p['tracked_dirty'])
    for n,d in p['tracked_dirty'].items():
        if n not in CONTROLS: assert sha(R/n)==d,n
    for n in CONTROLS: assert sha(U/'controls-before'/n)==p['tracked_dirty'][n]
    d=load(U/'decision.json'); assert d['selected_target']['effect']=='candidate_minus_locked_comparator'
    assert d['selected_target']['direction']=='negative is better'
    assert d['selected_target']['research_boundary']=='Delta < 0; equality at zero is the directional comparison boundary'
    assert d['promotion']['material_improvement'].endswith('not selected')
    assert d['historical_vintage_admissions']==0 and d['empirical_execution'] is False
    timing=load(R/'data/accounting-master/r05-source-timing-feasibility-20261023/matrix.json')
    assert timing['counts']['byte_admissions']==0
    expected=check(); assert expected==load(U/'reference-results.json')
    assert (U/'contract.md').read_text().count('1/9')>=2
    a,o=load(REVIEW/'assessment-successor.json'),load(REVIEW/'operation-successor.json')
    assert (len(a['rows']),len(a['interactions']),len(o['rows']))==(53,6,46)
    assert a['readiness']==o['readiness']=='not_ready'
    return p,{'fixtures':expected,'protected_files':len(p['protected']),'tracked_dirty_paths':len(rows),
      'whole_rows_closed':0,'readiness':'not_ready','manuscript_changed':False,
      'runtime_admitted':False,'inference_admitted':False,'empirical_execution':False,
      'material_margin_selected':False,'historical_vintage_admissions':0}


FRONTIER='''The E3 predictive-accuracy target is recorded at
data/accounting-master/r05-predictive-accuracy-target-20261023/: the user
selected research comparison of predictive accuracy. The primary directional
estimand is candidate-minus-locked-comparator operating-cash-flow CRPS after
common positive as-of asset scaling; negative is better and zero is the
equality boundary. This does not select economic value or a material negative
margin. Exact point-law, scaling, equal-issuer denominator, lock-order and
invalid-input fixtures pass without empirical observations or inference.

Next E3 dependency: specify a source-bound target/perimeter and future-origin
refit design, then match a dependence-aware inference procedure to that law.
Within-issuer time weights, asynchronous grouping, financial mapping, service,
margin, confidence, multiplicity, replication and sample/resource policy
remain unresolved. All 192 historical byte admissions remain false. Completed
one-time stages are frozen; safe replay is verify.py without flags.

'''


def record(p,checks,elapsed):
    for x in ('checks.json','run-manifest.json','completion.json'):
        assert not (U/x).exists()
    assert not SUPPLEMENT.exists() and not (U/'controls-after').exists()
    edits=[]
    for n in p['controls']:
        b=(U/'controls-before'/n).read_text(); marker='Next E3 dependency:'
        assert b.count(marker)==1; i=b.index(marker); j=b.index('Completed review evidence:',i)
        after=b[:i]+FRONTIER+b[j:]
        edits.append((n,after))
    write(U/'checks.json',checks)
    prefix='env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B '
    write(U/'run-manifest.json',{'git_commit':p['head'],'branch':p['branch'],'environment':sys.executable,
      'python':platform.python_version(),'cpu_gpu':'CPU only; GPU devices intentionally hidden; standard library fixtures only',
      'data_version':'Successor source-timing matrix plus frozen E3 target records','seeds':'N/A exact rational fixtures',
      'started_utc':p['started_utc'],'recorded_utc':datetime.now(timezone.utc).isoformat(),
      'wall_time_seconds':elapsed,'commands':[prefix+rel(U/'prepare.py'),prefix+rel(U/'record_decision.py'),
        prefix+rel(U/'reference.py'),prefix+rel(U/'verify.py'),prefix+rel(U/'verify.py')+' --record',prefix+rel(U/'verify.py')],
      'plan':rel(PLAN),'result':rel(U/'result.md'),'review':rel(U/'review.md'),'output':rel(U)})
    write(SUPPLEMENT,{'scope':'E3 predictive-accuracy target definition and exact fixtures','decision':bind(U/'decision.json'),
      'contract':bind(U/'contract.md'),'result':bind(U/'result.md'),'review':bind(U/'review.md'),'plan':bind(PLAN),
      'checks':checks,'candidate_version':'3.48','whole_rows_closed':0,'readiness':'not_ready',
      'manuscript_changed':False,'runtime_admitted':False,'inference_admitted':False,'empirical_execution':False,
      'independent_human_acceptance':'pending'})
    for n,after in edits:
        snap=U/'controls-after'/n;snap.parent.mkdir(parents=True,exist_ok=True)
        with snap.open('x') as f:f.write(after)
        (R/n).write_text(after)
    assert check_all()[1]==checks
    files=[x for x in U.rglob('*') if x.is_file() and '__pycache__' not in x.parts]+[PLAN,SUPPLEMENT]
    write(U/'completion.json',{'status':'complete_documentary_predictive_accuracy_target','checks':checks,
      'bindings':{rel(x):sha(x) for x in sorted(files)},
      'control_replay_policy':'Immutable before/after snapshots; never rewrite completed hashes'})


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--record',action='store_true');a=ap.parse_args();start=time.monotonic()
    p,checks=check_all()
    if a.record: record(p,checks,time.monotonic()-start)
    if (U/'completion.json').exists():
        c=load(U/'completion.json'); assert c['checks']==checks==load(U/'checks.json')
        for n,d in c['bindings'].items(): assert sha(R/n)==d,n
        status='recorded and verified' if a.record else 'read-only replay passed'
    else: status='read-only preflight passed; not recorded'
    print(json.dumps({'status':status,**checks}))


if __name__=='__main__':main()
