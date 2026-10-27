"""Record the user's evidence-route choice and advance the active plan once."""
from datetime import datetime,timezone
import json
import platform
import sys
from verify import U,R,sha,load,check

PLAN=R/'docs/plans/accounting-r05-prospective-inputs-20261023.md'
SUPPLEMENT=R/'data/accounting-master/readability-repair-20261022-theta/r05-prospective-inputs-supplement.json'
rel=lambda p:str(p.relative_to(R))
HEADER='''## 23 October 2026 — E3 evidence route selected

The user chose historical development followed by prospective confirmation.
The target remains future OCF predictive accuracy for the same nine companies,
next complete fiscal years, pre-start cutoffs and equal company contributions.
Annual/interim asset candidates and EU/UK cash-flow transition sources are
checked within their recorded scope. All 192 originals now have a current
local-possession observation; all historical admissions remain false.
Next: specify the matched comparator and fitting policy, then the inference
proposal and resource/sample rationale. Continue precise historical source
leads independently. No empirical run or user question is pending.

'''
FRONTIER='''The evidence-route and current-possession unit is complete at
data/accounting-master/r05-prospective-inputs-20261023/: the user's exact fifth
choice selects historical development then prospective confirmation. All 192
coverage-selected originals matched their hashes during a recorded 23 October
2026 UTC observation. This proves local possession within the stated clock
assumption, not earlier public release. Historical admission remains false;
prospective information policy and forecast issuance are also unadmitted.
The stage proposal distinguishes exposed development, historical simulation,
prospective locks, sequential refitting and later uncertainty analysis.

Next E3 dependency: develop the concrete matched-comparator/fitting policy and
an inference proposal for the selected two-stage route. Q, actual origin grid,
time weights, service/fallback, inference, confidence, multiplicity and
resources remain open. Continue precise historical-version source work in
parallel when independent. Safe replay:
data/accounting-master/r05-prospective-inputs-20261023/verify.py. No whole row
closes, no global continuation veto fires and no user question is pending.

'''

def write(path,value):
    with path.open('x') as f:json.dump(value,f,indent=2);f.write('\n')

def main():
    assert not (U/'completion.json').exists() and not (U/'run-manifest.json').exists()
    assert not SUPPLEMENT.exists()
    checks=check();start=load(U/'start.json');edits=[]
    for name in start['controls']:
        raw=(U/'controls-before'/name).read_bytes();assert (R/name).read_bytes()==raw,name
        before=raw.decode();marker='Next E3 dependency: investigate concrete exact-version release leads and\n'
        assert before.count(marker)==1
        a=before.index(marker);b=before.index('Completed review evidence:',a)
        after=before[:a]+FRONTIER+before[b:]
        a=after.index('## 23 October 2026 — E3 EU legal-text source resolved');b=after.index('## 22 October 2026',a)
        edits.append((name,after[:a]+HEADER+after[b:]))
    now=datetime.now(timezone.utc)
    prefix='env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B '
    write(U/'run-manifest.json',{'git_commit':start['head'],'branch':start['branch'],
        'environment':sys.executable,'python':platform.python_version(),
        'cpu_gpu':'CPU only; GPU intentionally hidden; standard library',
        'data_version':'192 coverage-selected original paths and hashes; observations.json',
        'random_seeds':'N/A; deterministic identity/timing checks',
        'started_utc':start['started_utc'],'completed_utc':now.isoformat(),
        'wall_time_seconds':(now-datetime.fromisoformat(start['started_utc'])).total_seconds(),
        'commands':[prefix+rel(U/n) for n in ('prepare.py','observe.py','verify.py','finish.py')],
        'clock_tool':'clock.curr_time, before and after; clock-crosscheck.json',
        'plan':rel(PLAN),'result':rel(U/'result.md'),'proposal':rel(U/'stage-proposal.md'),
        'output_paths':[rel(U),rel(SUPPLEMENT)],'empirical_execution':False})
    write(SUPPLEMENT,{'scope':'selected evidence route and current source observation',
        'result':rel(U/'result.md'),'result_sha256':sha(U/'result.md'),
        'checks':checks,'candidate_version':'3.48','whole_rows_closed':0,'readiness':'not_ready'})
    for name,after in edits:
        path=U/'controls-after'/name;path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('x') as f:f.write(after)
        (R/name).write_text(after)
    paths=[p for p in U.rglob('*') if p.is_file()]+[PLAN,SUPPLEMENT]
    write(U/'completion.json',{'status':'complete_route_and_source_observation','checks':checks,
        'bindings':{rel(p):sha(p) for p in sorted(paths)},'replay':'verify.py; read only'})
    assert check()==checks
    print(json.dumps({'status':'completed and verified',**checks}))

if __name__=='__main__':main()
