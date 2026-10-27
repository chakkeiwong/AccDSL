"""Replay retained credit cases and preserve a dependence counterexample."""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as Q
from copy import deepcopy
import importlib.util
import json
import platform
import subprocess
import sys
import time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
NATIVE=ROOT/'data/accounting-master/dated-credit-schedules-20261016'
sys.path.insert(0,str(NATIVE))
spec=importlib.util.spec_from_file_location('credit_representation_native',NATIVE/'reference.py')
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
import bounds
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')


def main():
    record='--record' in sys.argv;start=time.monotonic()
    if record:assert not (HERE/'evidence.json').exists()
    locks={}
    def lock(p,expected=None):
        p=p if isinstance(p,Path) else ROOT/p;actual=sha(p)
        if expected is not None:assert actual==expected,str(p)
        locks[str(p.relative_to(ROOT))]=actual
    earlier=json.loads((ROOT/'data/accounting-master/sector-posting-boundary-20261025/source-lock.json').read_text())
    for name,expected in earlier.items():
        if 'dated-credit-schedules-20261016/' in name:lock(name,expected)
    for row in json.loads((NATIVE/'input-lock.json').read_text())['files']:lock(row['path'],row['sha256'])
    for name in ['reference.py','bounds.py','authored-cases.json','input-lock.json','verify.py']:
        assert (NATIVE/name).read_bytes()==(NATIVE/'attempt-01'/name).read_bytes(),name
        lock(NATIVE/name);lock(NATIVE/'attempt-01'/name)
    for p in [NATIVE/'attempt-01/exchanges.json',NATIVE/'attempt-01/run-manifest.json',
              NATIVE/'semantic-contract.md',NATIVE/'source-reading.md',HERE/'audit.md',Path(__file__),
              ROOT/'docs/plans/accounting-credit-posting-representation-20261025.md',
              ROOT/'scripts/company_book_transition_v1.py',ROOT/'scripts/company_book_transition_v2.py',
              ROOT/'scripts/method_monetary_effects_v1.py',
              ROOT/'docs/design/proposal/manuscript-insurance-statement-20261025/chapters/06-language.tex',
              ROOT/'docs/design/proposal/manuscript-insurance-statement-20261025/chapters/07-execution.tex']:
        lock(p)
    rows=json.loads((NATIVE/'attempt-01/exchanges.json').read_text());cases=[]
    monetary=['gross','allowance','net','cash','interest','impairment','catchup','profit','equity','direct_gross','direct_net']
    for row in rows:
        q=deepcopy(row['request']);before=deepcopy(q);r=native.calculate(q)
        assert r==row['result'] and q==before and r['posts'] is False and r['mutations']==[],row['id']
        nonpoint=sum(v['lower']!=v['upper'] for j in r['journals'] for v in j['entries'].values())
        nonpoint_states=sum(s[k]['lower']!=s[k]['upper'] for s in r['stages'] for k in monetary)
        for j in r['journals']:
            lo=sum(Q(v['lower']) for v in j['entries'].values());hi=sum(Q(v['upper']) for v in j['entries'].values())
            assert lo<=0<=hi
        if not nonpoint:
            assert nonpoint_states==0
            assert all(sum(Q(v['lower']) for v in j['entries'].values())==0 for j in r['journals'])
        cases.append({'id':row['id'],'request_sha256':sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            'journal_count':len(r['journals']),'nonpoint_entries':nonpoint,'nonpoint_state_fields':nonpoint_states,
            'all_recorded_journals_and_states_exact':nonpoint==nonpoint_states==0,'replay_equal':True})
    selected=next(r for r in rows if r['id']=='partial-early-writeoff')
    journal=next(j for j in selected['result']['journals'] if j['id']=='july_accrual')
    upper={k:v['upper'] for k,v in journal['entries'].items()}
    residual=sum(Q(x) for x in upper.values());assert residual==Q(1,10**16)
    f=bounds.factor(Q(1,10),181,18);target=Q(11,10)**181
    assert f.lo**365<=target<=f.hi**365
    mid=(f.lo+f.hi)/2;assert mid**365!=target
    assert Q(100)+Q(0)-Q(100)==0
    witness={'case':'partial-early-writeoff','journal':journal,'independent_all_upper':upper,
        'all_upper_sum':str(residual),'shared_expressions':{'gross':'100*(F-1)','allowance':'0','interest':'-100*(F-1)'},
        'shared_coefficient_sum':'0','factor':f.wire(),'factor_equation':'F^365=(11/10)^181; F>0',
        'integer_power_bounds_pass':True,'midpoint':str(mid),'midpoint_satisfies_factor_equation':False,
        'meaning':'Independent endpoints fail exact balance; an enclosed midpoint is not the specified exact factor. No point posted.'}
    evidence={'cases':cases,'native_replays':len(cases),
        'rationally_exact_cases':[r['id'] for r in cases if r['all_recorded_journals_and_states_exact']],
        'dependent_interval_cases':[r['id'] for r in cases if not r['all_recorded_journals_and_states_exact']],
        'witness':witness,'scope':'Representation diagnostic only; no accounting or exact-book admission'}
    if record:
        dump(HERE/'evidence.json',evidence);lock(HERE/'evidence.json');dump(HERE/'source-lock.json',locks)
        dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B data/accounting-master/credit-posting-representation-20261025/verify.py --record',
            'environment':sys.version,'platform':platform.platform(),'cpu_gpu':'CPU exact rational arithmetic; no GPU framework imported',
            'seeds':'N/A deterministic','data_version':'Nine retained dated-credit attempt-01 exchanges','wall_seconds':time.monotonic()-start,
            'plan':'docs/plans/accounting-credit-posting-representation-20261025.md','result':str((HERE/'result.md').relative_to(ROOT)),
            'artifacts':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['evidence.json','source-lock.json']}})
    else:
        assert evidence==json.loads((HERE/'evidence.json').read_text())
        saved=json.loads((HERE/'source-lock.json').read_text())
        for n,h in saved.items():assert sha(ROOT/n)==h,n
        for n,h in locks.items():assert saved[n]==h,n
        for n,h in json.loads((HERE/'run-manifest.json').read_text())['artifacts'].items():assert sha(ROOT/n)==h,n
    print(json.dumps({'passed':True,'mode':'record' if record else 'read_only_replay','native_replays':len(cases),
        'exact_cases':evidence['rationally_exact_cases'],'nonpoint_cases':len(evidence['dependent_interval_cases']),
        'independent_endpoint_imbalance':str(residual),'midpoint_is_exact':False,
        'locked_files':len(json.loads((HERE/'source-lock.json').read_text()))}))


if __name__=='__main__':main()
