"""Read-only validation; --record freezes this unit once after preflight."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from build_matrix import calculate, relation

U=Path(__file__).resolve().parent
R=U.parents[2]
PLAN=R/'docs/plans/accounting-r05-source-timing-feasibility-20261023.md'
REVIEW=R/'data/accounting-master/readability-repair-20261022-theta'
SUPPLEMENT=REVIEW/'r05-source-timing-feasibility-supplement.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
rel=lambda p:str(p.relative_to(R))
bind=lambda p:{'path':rel(p),'sha256':sha(p)}


def write(p,value):
    with p.open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2)
        f.write('\n')


def check():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    p=load(U/'protection.json')
    for name,digest in p['protected'].items():
        assert sha(R/name)==digest,name
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==p['head']
    assert sha(R/'.git/index')==p['index_sha256']
    raw=subprocess.check_output(['git','status','--porcelain=v1','--untracked-files=no','-z'],cwd=R,text=True)
    rows=[r for r in raw.split('\0') if r]
    assert all(r[:2]==' M' for r in rows) and {r[3:] for r in rows}==set(p['tracked_dirty'])
    for name,digest in p['tracked_dirty'].items():
        if name not in p['controls']:
            assert sha(R/name)==digest,name
    for name in p['controls']:
        assert sha(U/'controls-before'/name)==p['tracked_dirty'][name]
    matrix=calculate()
    assert matrix==load(U/'matrix.json')
    correction=load(U/'history-repair/correction.json')
    assert correction['predecessor_mutated_by_this_recovery'] is False
    for name,digest in correction['new_recovery_files'].items():
        assert sha(R/name)==digest,name
    assert len(correction['corrections'])==4
    for r in correction['corrections']:
        assert sha(R/r['initial_reconstruction'])==r['initial_sha256']
        assert sha(R/r['current_frozen_snapshot'])==r['current_recorded_sha256']
    purpose=load(U/'research-purpose-answer.json')
    assert purpose['answer']=='Research comparison of predictive accuracy (recommended for the first study)'
    cases=[(None,'2025-12-31','unverified'),
           ('2025-12-31','2025-12-31','unverified'),
           ('2025-12-30','2025-12-31','unverified'),
           ('2025-12-01','2025-12-31','supported_for_date_role_only'),
           ('2026-02-01','2025-12-31','contradicted_for_date_role_only')]
    for a,b,want in cases:
        assert relation(a,b)==want
    try:
        relation('2025-02-30','2025-12-31')
    except ValueError:
        pass
    else:
        raise AssertionError('malformed date was not refused')
    a,o=load(REVIEW/'assessment-successor.json'),load(REVIEW/'operation-successor.json')
    assert (len(a['rows']),len(a['interactions']),len(o['rows']))==(53,6,46)
    assert a['readiness']==o['readiness']=='not_ready'
    return p,{'matrix':matrix['counts'],'date_boundary_cases':5,'invalid_date_refusals':1,
        'history_snapshots_reconciled':4,'protected_files':len(p['protected']),
        'tracked_dirty_paths':len(rows),'whole_rows_closed':0,'readiness':'not_ready',
        'manuscript_changed':False,'runtime_admitted':False,'inference_admitted':False}


FRONTIER='''The source-timing feasibility matrix is complete at
data/accounting-master/r05-source-timing-feasibility-20261023/: 27 historical
input candidates (older annual, latest interim and immediately preceding
annual for each issuer). Seven date-role events precede the hypothetical
FY2026 cutoff and five follow it; fifteen reports have no retained date role.
None has admitted selected-byte availability or prospective forecast status.
The conditional calendar and conservative date bounds are explicit proposals.
The unit also reconciles four predecessor snapshots edited after completion,
preserving reconstructed initial and observed corrected versions with exact
hashes; a passing content replay had not established immutable history.

The user has selected research comparison of predictive accuracy for the first
E3 study. The exact answer is retained in this unit. Next E3 dependency:
audit and record the directional expected-CRPS target and zero-equality
threshold, distinguish it from economic value, and match the time process,
origin weights, refitting and inference to that research purpose. Keep the
source-version and early-outcome-release gaps separate; the matrix supports
no new as-of admission. Completed one-time stages remain frozen; safe replay
is verify.py without flags.

'''


def record(p,checks,elapsed):
    targets=[U/'checks.json',U/'run-manifest.json',U/'completion.json',SUPPLEMENT]
    assert all(not x.exists() and x.parent.is_dir() for x in targets)
    assert not (U/'controls-after').exists()
    edits=[]
    for name in p['controls']:
        target=R/name
        before=(U/'controls-before'/name).read_text()
        assert target.read_text()==before and not target.is_symlink()
        marker='Next E3 dependency: establish a source-timing feasibility matrix and exact'
        assert before.count(marker)==1
        first=before.index(marker);last=before.index('Completed review evidence:',first)
        after=before[:first]+FRONTIER+before[last:]
        stale='E3 now targets repeated future origins for the named companies; five legacy\nscientific choices remain unselected and all 192 vintage admissions remain false. They block dependent empirical work, not internal\npreparation.'
        assert after.count(stale)==1
        after=after.replace(stale,'E3 selects named-company future dates, full fiscal years and equal issuer\nweights. Origin/time weights, future law/regime, refit/service, financial scope,\nmargin, confidence, inference and sample design still require specification;\nall 192 historical byte admissions remain false. These gaps block dependent\nempirical work, while internal preparation continues.')
        firstline,body=after.split('\n',1)
        latest='\n## 23 October 2026 — E3 decisions and timing feasibility\n\nThe user selected next-full-fiscal-year operating cash flow, a named pre-start\ncutoff, equal weights for the nine companies, and predictive-accuracy research.\nThe fiscal-year protocol and 27-report timing matrix are complete documentary\nunits. Exact byte availability, future origin law and inference remain open.\nThe entries below preserve the detailed evidence and earlier phase context.\n\n'
        edits.append((name,firstline+'\n'+latest+body.lstrip('\n')))
    assert all((U/x).is_file() for x in ('result.md','review.md','research-purpose-answer.json'))
    write(U/'checks.json',checks)
    prefix='env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B '
    write(U/'run-manifest.json',{'git_commit':p['head'],'branch':p['branch'],
        'environment':sys.executable,'python':platform.python_version(),
        'cpu_gpu':'CPU only; GPU devices intentionally hidden; no framework imports',
        'data_version':'Protected vintage reconciliation plus bound date-role JSON pointers and selected originals',
        'seeds':'N/A deterministic documentary checks','started_utc':p['started_utc'],
        'recorded_utc':datetime.now(timezone.utc).isoformat(),
        'wall_time':{'matrix_calculation_seconds':load(U/'matrix-run.json')['calculation_wall_seconds'],
                     'record_preflight_seconds':elapsed,'whole_session':'not measured'},
        'executed_commands':[prefix+rel(U/'prepare.py'),prefix+rel(U/'reconcile_history.py'),
                             prefix+rel(U/'build_matrix.py')+' --record',prefix+rel(U/'verify.py')],
        'completion_command':prefix+rel(U/'verify.py')+' --record',
        'next_readonly_replay':prefix+rel(U/'verify.py'),
        'plan':rel(PLAN),'result':rel(U/'result.md'),'outputs':rel(U)})
    write(SUPPLEMENT,{'scope':'Retained source-date feasibility and explicit predecessor-history correction',
        'candidate_version':'3.48','candidate_pdf':bind(R/'docs/design/proposal/manuscript-readability-20261022-theta/accounting-product-proposal.pdf'),
        'protected_assessment':bind(REVIEW/'assessment-successor.json'),
        'protected_operations':bind(REVIEW/'operation-successor.json'),
        'all_original_obligations':53,'interactions':6,'operations':46,'whole_rows_closed':0,
        'readiness':'not_ready','plan':bind(PLAN),'result':bind(U/'result.md'),'review':bind(U/'review.md'),
        'checks':checks,'manuscript_changed':False,'runtime_admitted':False,'inference_admitted':False,
        'independent_human_acceptance':'pending'})
    for name,after in edits:
        snap=U/'controls-after'/name
        snap.parent.mkdir(parents=True,exist_ok=True)
        with snap.open('x') as f:
            f.write(after)
        (R/name).write_text(after)
    assert check()[1]==checks
    files=[x for x in U.rglob('*') if x.is_file() and '__pycache__' not in x.parts]+[PLAN,SUPPLEMENT]
    write(U/'completion.json',{'status':'complete_documentary_timing_and_history_repair',
        'checks':checks,'bindings':{rel(x):sha(x) for x in sorted(files)},
        'control_replay_policy':'Immutable before/after snapshots; live controls may advance in a successor; never rewrite completed hashes'})


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--record',action='store_true');args=ap.parse_args()
    start=time.monotonic();p,checks=check()
    if args.record:
        record(p,checks,time.monotonic()-start)
    if (U/'completion.json').exists():
        c=load(U/'completion.json')
        assert c['checks']==checks==load(U/'checks.json')
        for name,digest in c['bindings'].items():
            assert sha(R/name)==digest,name
        status='recorded and verified' if args.record else 'read-only replay passed'
    else:
        status='read-only preflight passed; not recorded'
    print(json.dumps({'status':status,**checks}))


if __name__=='__main__':
    main()
