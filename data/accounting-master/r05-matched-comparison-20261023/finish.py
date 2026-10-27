"""Record the finite comparison audit and refresh the next internal task."""
from datetime import datetime,timezone
import json
import platform
import sys
from verify import U,R,sha,load,check

PLAN=R/'docs/plans/accounting-r05-matched-comparison-20261023.md'
SUPPLEMENT=R/'data/accounting-master/readability-repair-20261022-theta/r05-matched-comparison-supplement.json'
rel=lambda p:str(p.relative_to(R))
HEADER='''## 23 October 2026 — E3 comparison mechanism clarified

The user selected historical development then prospective confirmation of
future OCF predictive accuracy for the same nine companies, pre-start full-year
forecasts and equal company contributions. The primary paired comparison stays
against a locked fixed interpretation. A new exact derivation separates it
from CRPS's automatic mixture-versus-averaged-score advantage.
Next: concrete historical-version archive leads; continue the forecast-weight,
selector/fitting and inference proposals. All 192 historical admissions remain
false. No empirical run, whole-row closure or user question is pending.

'''
FRONTIER='''The matched-comparison inquiry is complete at
data/accounting-master/r05-matched-comparison-20261023/: a conditional CDF
derivation, twelve exact cases, twenty independent score calculations and four
invalid-weight refusals. The mixture's advantage over averaged component scores
does not order it against the locked fixed law. Conserved mass survives duplicate
encodings; equal encoding weights change the law. The proposal separates strict
shared-state ablation from comparison of separately fitted procedures.

Next E3 dependency: investigate distinct exact-version archival leads while
developing justified history weights, a fixed selector and matched fitting.
Then specify future Q/grid, time weights, service/fallback, inference,
confidence/multiplicity and sample/resources. No actual forecast law or empirical
ranking is admitted. Safe replay:
data/accounting-master/r05-matched-comparison-20261023/verify.py. Completed
records remain immutable; no global continuation veto or pending user question.

'''

def write(path,value):
    with path.open('x') as f:json.dump(value,f,indent=2);f.write('\n')

def main():
    assert not (U/'completion.json').exists() and not (U/'run-manifest.json').exists()
    assert not (U/'reference-results.json').exists() and not SUPPLEMENT.exists()
    cases,checks=check();start=load(U/'start.json');edits=[]
    for name in start['controls']:
        raw=(U/'controls-before'/name).read_bytes();assert (R/name).read_bytes()==raw,name
        before=raw.decode();marker='Next E3 dependency: develop the concrete matched-comparator/fitting policy and\n'
        assert before.count(marker)==1
        a=before.index(marker);b=before.index('Completed review evidence:',a)
        after=before[:a]+FRONTIER+before[b:]
        a=after.index('## 23 October 2026 — E3 evidence route selected');b=after.index('## 22 October 2026',a)
        edits.append((name,after[:a]+HEADER+after[b:]))
    now=datetime.now(timezone.utc)
    prefix='env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B '
    write(U/'reference-results.json',cases)
    write(U/'run-manifest.json',{'git_commit':start['head'],'branch':start['branch'],
        'environment':sys.executable,'python':platform.python_version(),
        'cpu_gpu':'CPU only; GPU intentionally hidden; rational standard-library calculations',
        'data_version':'Fictional finite laws only; inherited CRPS helper preserved',
        'random_seeds':'N/A; exact full-support calculation, no sampling',
        'started_utc':start['started_utc'],'completed_utc':now.isoformat(),
        'wall_time_seconds':(now-datetime.fromisoformat(start['started_utc'])).total_seconds(),
        'commands':[prefix+rel(U/n) for n in ('prepare.py','reference.py','verify.py','finish.py')],
        'plan':rel(PLAN),'result':rel(U/'result.md'),'proposal':rel(U/'proposal.md'),
        'output_paths':[rel(U),rel(SUPPLEMENT)],'empirical_execution':False})
    write(SUPPLEMENT,{'scope':'matched history-preservation comparison and finite CRPS identity',
        'result':rel(U/'result.md'),'result_sha256':sha(U/'result.md'),'checks':checks,
        'candidate_version':'3.48','whole_rows_closed':0,'readiness':'not_ready'})
    for name,after in edits:
        path=U/'controls-after'/name;path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('x') as f:f.write(after)
        (R/name).write_text(after)
    dependencies=[R/'data/accounting-master/r05-ocf-measurement-20261023/reference.py',
                  R/'data/accounting-master/r05-ocf-measurement-20261023/target-contract.md']
    paths=[p for p in U.rglob('*') if p.is_file()]+[PLAN,SUPPLEMENT]+dependencies
    write(U/'completion.json',{'status':'complete_finite_comparison_audit','checks':checks,
        'bindings':{rel(p):sha(p) for p in sorted(paths)},'replay':'verify.py; read only'})
    assert check()==(cases,checks)
    print(json.dumps({'status':'completed and verified',**checks}))

if __name__=='__main__':main()
