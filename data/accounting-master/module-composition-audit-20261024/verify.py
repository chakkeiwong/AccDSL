from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,json,platform,subprocess,sys,time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')
def main():
    start=time.monotonic();mode=sys.argv[1] if len(sys.argv)>1 else '--check'
    assert mode in ['--check','--record','--replay']
    if mode=='--record':assert not (HERE/'manifest.json').exists(),'already recorded'
    r=json.loads(subprocess.run([sys.executable,'-B',str(HERE/'probe.py'),'--replay'],cwd=ROOT,capture_output=True,text=True,check=True).stdout)
    assert r['passed'] and r['checks']==44
    inv=json.loads((HERE/'capabilities.json').read_text());checks=0
    assert len(inv['modules'])==8 and len({m['id'] for m in inv['modules']})==8;checks+=1
    for m in inv['modules']:
        a=m['source_anchor'];t=ast.parse((ROOT/a['path']).read_text())
        n=next(n for n in ast.walk(t) if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==a['function'])
        assert (n.lineno,n.end_lineno)==(a['start_line'],a['end_line']);checks+=1
        assert m['source_admission_inferred'] is False and m['general_composition_established'] is False;checks+=1
    runtime=json.loads((HERE/'probe-results.json').read_text())['executed_local_code_sha256']
    for name,digest in runtime.items():assert sha(ROOT/name)==digest,name;checks+=1
    report={'passed':True,'probe_checks':44,'inventory_and_runtime_checks':checks,'modules':8,'findings':6,
            'protected_inputs':26,'runtime_local_files':len(runtime),'whole_requirements_closed':0}
    if mode=='--replay':
        assert report==json.loads((HERE/'checks.json').read_text())
        for name,digest in json.loads((HERE/'manifest.json').read_text())['files'].items():assert sha(ROOT/name)==digest,name
    elif mode=='--record':
        names=['source-lock.json','capabilities.json','probe.py','probe-plan.md','probe-results.json','probe-checks.json','verify.py','finish.py','result.md','review.md']
        hashes={str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in names}
        hashes.update(runtime)
        dump('checks.json',report);dump('manifest.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),
             'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
             'command':'python3 -B '+str((HERE/'verify.py').relative_to(ROOT))+' --record',
             'environment':{'python':platform.python_version(),'executable':sys.executable},
             'cpu_gpu':'CPU-only rational checks and code inspection; no GPU framework imported',
             'random_seeds':'N/A: deterministic original-context capability probes',
             'wall_seconds':time.monotonic()-start,'data_version':'source-lock.json and executed-code hashes',
             'plan':'docs/plans/accounting-module-composition-audit-20261024.md','result':str((HERE/'result.md').relative_to(ROOT)),
             'files':hashes})
    print(json.dumps(report))
if __name__=='__main__':main()
