"""Bounded saved evidence for the named source adapter; exact witness replay."""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as Q
from datetime import datetime,timezone
from copy import deepcopy
import argparse,json,platform,subprocess,sys,time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import henkel_lease_measurements_v1 as h
COUNT=0

def need(value,label):
    global COUNT
    if not value:raise AssertionError(label)
    COUNT+=1

def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(name,data):(HERE/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

def scenarios():
    yield 'default',h.fixture(),h.BUDGET,'unresolved'
    yield 'all_proposed',h.fixture(assume=True),h.BUDGET,'conditionally_feasible'
    for year in [2024,2025]:
        selected=[k for k in h.SUPPORTED if k.startswith(str(year)) and not k.endswith('continuity')]
        yield str(year),h.fixture(selected,True),h.BUDGET,'conditionally_feasible'
    b=h.fixture(assume=True);b['rounding_hypothesis']=None
    yield 'missing_rounding',b,h.BUDGET,'unresolved'
    b=h.fixture(assume=True);b['identity_hypotheses'][h.SUPPORTED[0]]=None
    yield 'missing_identity',b,h.BUDGET,'unresolved'
    yield 'zero_budget',h.fixture(assume=True),{**h.BUDGET,'max_cells':0},'unknown'
    yield 'empty',h.fixture([]),h.BUDGET,'no_asserted_system'

def independent_witness(result):
    a=result['temporal_assessment'].get('joint_assessment',{})
    if 'witness' not in a:return
    v={k:Q(x) for k,x in a['witness'].items()};d=result['definition']
    need(set(v)==set(d['observations']),'witness membership')
    for key,o in d['observations'].items():
        bounds=o['interval'];x=v[key];lo=Q(bounds['lower']);hi=Q(bounds['upper'])
        need((x>=lo if bounds['lower_inclusive'] else x>lo) and (x<=hi if bounds['upper_inclusive'] else x<hi),'rational interval')
    for r in d['relations']:
        if r['kind']=='same_time':
            need(sum(Q(t['coefficient'])*v[t['observation']] for t in r['terms'])==Q(r['rhs']),'rational relation')
        else:
            need(v[r['opening']]+sum(Q(t['coefficient'])*v[t['observation']] for t in r['movements'])==v[r['closing']],'rational stock-flow')

def main():
    parser=argparse.ArgumentParser();g=parser.add_mutually_exclusive_group();g.add_argument('--record',action='store_true');g.add_argument('--replay',action='store_true');args=parser.parse_args();start=time.monotonic()
    if args.record:assert not (HERE/'checks.json').exists() and not (HERE/'manifest.json').exists(),'record once'
    locks=h.verify_dependencies()
    need(len(locks)==46,'protected inputs')
    source=json.loads(subprocess.run([sys.executable,'-B',str(h.SOURCE/'verify.py'),'--replay'],cwd=ROOT,capture_output=True,text=True,check=True).stdout)
    need(source['passed'] and source['checks']==2114,'original source audit replay')
    saved=json.loads((HERE/'cases.json').read_text()) if args.replay else []
    cases=[]
    for i,(label,body,budget,status) in enumerate(scenarios()):
        result=saved[i]['result'] if args.replay else h.assess(body,budget)
        need(result['status']==status,label+' status');need(h.verify_result(body,budget,result),label+' full replay')
        need(len(result['preserved_inventory']['observations'])==104,label+' inventory')
        need(len(result['preserved_state_dependencies']['dependencies'])==14,label+' missing state')
        need(not result['executed'] and not result['native_state_admission'] and result['executable_opening'] is None,label+' non-admission')
        independent_witness(result)
        cases.append({'label':label,'request':body,'budget':budget,'result':result})
        if args.replay:need(saved[i]['label']==label and saved[i]['request']==body and saved[i]['budget']==budget,label+' request')
    # Preserve a counterfactual separately; it does not replace any source value.
    base=h.build(h.fixture(['2024.rou_gross_net'],True),h.BUDGET);d=deepcopy(base['definition'])
    for key,o in d['observations'].items():
        a=h.rational(base['source_mapping'][key]['displayed_rational'])
        o['interval']={'lower':a,'upper':a,'lower_inclusive':True,'upper_inclusive':True}
        o['interval_premise']={'id':'counterfactual_exact_displays','status':'proposed','meaning':'Treat rounded displays as exact only to test this incompatible hypothesis.'}
    r=h.temporal.assess(d,h.BUDGET)
    need(r['status']=='conditionally_infeasible','counterfactual exact display rejection')
    need(all(c['rechecked']=='unsat' for c in r['joint_assessment']['conflicts']),'infeasibility recheck')
    report={'passed':True,'checks':COUNT-(8 if args.replay else 0),'saved_cases':8,'selected_relations':19,
            'selected_measurements':54,'preserved_numeric_observations':104,'state_dependencies':14,
            'protected_files':46,'source_audit_checks':2114,'focused_test_methods':10,'temporal_regression_methods':12,
            'whole_requirements_closed':0,'native_state_admission':False}
    if args.replay:
        need(len(saved)==8,'saved case count');need(report==json.loads((HERE/'checks.json').read_text()),'saved summary')
        for name,digest in json.loads((HERE/'manifest.json').read_text())['files'].items():need(sha(ROOT/name)==digest,'package hash '+name)
        report['saved_replay']=True
    if args.record:
        dump('cases.json',cases);dump('counterfactual-exact-display.json',{'definition':d,'assessment':r})
        names=['dependency-lock.json','design.md','verify.py','cases.json','counterfactual-exact-display.json','test-observation.json','result.md','review.md','finish.py']
        files={str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in names}
        files.update({n:sha(ROOT/n) for n in ['scripts/henkel_lease_measurements_v1.py','tests/test_henkel_lease_measurements_v1.py']})
        commit=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip()
        dump('checks.json',report);dump('manifest.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'git_commit':commit,
            'dirty_worktree':'Pre-existing work retained; file hashes preserve exact reference versions',
            'command':'python3 -B '+str((HERE/'verify.py').relative_to(ROOT))+' --record',
            'environment':{'python':platform.python_version(),'executable':sys.executable,'z3':h.temporal.joint.z3.get_version_string()},
            'cpu_gpu':'CPU-only parsing/rational/SMT; no GPU framework imported','random_seeds':'N/A: deterministic feasibility; witness choice not ranked',
            'data_version':h.INVENTORY_SHA256,'wall_seconds':time.monotonic()-start,'plan':'docs/plans/accounting-henkel-lease-measurements-20261024.md',
            'result':str((HERE/'result.md').relative_to(ROOT)),'files':files})
    print(json.dumps(report))

if __name__=='__main__':main()
