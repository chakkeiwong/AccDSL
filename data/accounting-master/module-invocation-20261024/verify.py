from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
from copy import deepcopy
import importlib.util, json, platform, subprocess, sys, time

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(HERE))
import module_invocation_v1 as caller
import examples

def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(name,data):(HERE/name).write_text(json.dumps(data,indent=2)+'\n')
def original(key,p):
    if key=='typed_return':
        import typed_return_transition_v1 as native
        return native.propose(p['state_text'].encode(),p['state_raw_sha256'],p['event_text'].encode(),p['event_raw_sha256'])
    if key=='shared_lease':
        import lease_shared_book_v1 as native
        return native.propose(deepcopy(p['state']),deepcopy(p['event']))
    if key=='henkel_measurements':
        import henkel_lease_measurements_v1 as native
        return native.assess(deepcopy(p['request']),deepcopy(p['budget']))
    path=ROOT/'data/accounting-master/sector-company-composition-20261016/reference.py'
    spec=importlib.util.spec_from_file_location('direct_original_sector',path)
    native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
    return native.calculate(deepcopy(p['request']))

def main():
    start=time.monotonic();mode=sys.argv[1] if len(sys.argv)>1 else '--check'
    assert mode in ['--check','--record','--replay']
    if mode=='--record':assert not (HERE/'manifest.json').exists(),'already recorded'
    lock=caller.dependencies();checks=[]
    def check(name,ok):
        assert ok,name
        checks.append(name)
    for name,h in lock.items():check('protected:'+name,sha(ROOT/name)==h)
    rows=examples.cases();check('unique_cases',len({r['case'] for r in rows})==len(rows))
    check('registry_modules',set(caller.registry()['entries'])==set(caller.SPECS))
    saved=json.loads((HERE/'cases.json').read_text()) if mode=='--replay' else []
    if saved:check('saved_case_names',[r['case'] for r in saved]==[r['case'] for r in rows])
    else:check('saved_case_names',True)
    out=[]
    for i,row in enumerate(rows):
        name=row['case'];body=row['request'];before=deepcopy(body)
        result=caller.invoke(body)
        check(name+':status',result['status']==row['expected_status'])
        check(name+':immutable',body==before)
        check(name+':flags',all(result[k] is False for k in caller.FLAGS))
        check(name+':replay',caller.verify_result(body,result))
        if row['expected_native_status'] is not None:
            check(name+':native_status',result['native_status']==row['expected_native_status'])
            direct=original(body['module_id'],body['payload'])
            if body['module_id']=='henkel_measurements':
                import henkel_lease_measurements_v1 as h
                check(name+':original',h.verify_result(body['payload']['request'],body['payload']['budget'],result['native_result']) and direct['status']==result['native_status'])
            else:check(name+':original',direct==result['native_result'])
        else:check(name+':no_native',result['native_result'] is None)
        if mode=='--replay':
            check(name+':saved_request',saved[i]['request']==body)
            check(name+':saved_result',caller.verify_result(body,saved[i]['result']))
        else:
            check(name+':saved_request',True);check(name+':saved_result',True)
        out.append({**row,'result':result})
    tests=json.loads((HERE/'test-observation.json').read_text())
    check('tests_pass',tests['exit_code']==0)
    check('test_input_identity',all(sha(ROOT/n)==h for n,h in tests['files'].items()))
    report={'passed':True,'checks':len(checks),'saved_cases':len(rows),'protected_files':len(lock),'test_methods':tests['test_methods'],'whole_requirements_closed':0}
    if mode=='--record':
        dump('cases.json',out);dump('registry.json',caller.registry());dump('checks.json',report);dump('check-names.json',checks)
        files=list(HERE.glob('*'));files=[p for p in files if p.is_file()]
        files += [ROOT/'scripts/module_invocation_v1.py',ROOT/'tests/test_module_invocation_v1.py',ROOT/'docs/plans/accounting-shared-state-compatibility-20261024.md']
        dump('manifest.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':'python3 -B '+str((HERE/'verify.py').relative_to(ROOT))+' --record','environment':{'python':platform.python_version(),'executable':sys.executable},'cpu_gpu':'CPU-only; no GPU framework imported','random_seeds':'N/A: deterministic reference checks','wall_seconds':time.monotonic()-start,'data_version':'dependency-lock.json','plan':'docs/plans/accounting-module-invocation-20261024.md','result':str((HERE/'result.md').relative_to(ROOT)),'files':{str(p.relative_to(ROOT)):sha(p) for p in files}})
    if mode=='--replay':
        assert report==json.loads((HERE/'checks.json').read_text())
        assert checks==json.loads((HERE/'check-names.json').read_text())
        assert caller.registry()==json.loads((HERE/'registry.json').read_text())
        for name,h in json.loads((HERE/'manifest.json').read_text())['files'].items():assert sha(ROOT/name)==h,name
    print(json.dumps(report))
if __name__=='__main__':main()
