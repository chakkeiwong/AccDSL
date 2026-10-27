"""Exact source inventory and preserved historical cases; no method reexecution."""
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json,os,platform,subprocess,sys,time
os.environ['CUDA_VISIBLE_DEVICES']='-1'
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
from inventory import build,FILES,EVIDENCE
PLAN='docs/plans/accounting-complete-method-coverage-20261024.md'
NEXT='docs/plans/accounting-dimensional-requirements-20261024.md'


def sha(p):
    return sha256(p.read_bytes()).hexdigest()


def dump(p,value):
    p.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')


def conformance():
    value=build()
    checks=[]
    def check(name,condition):
        checks.append({'name':name,'passed':bool(condition)})
    identities=[]
    for file in value['files']:
        check(file['file']+'.identity',sha(ROOT/file['file'])==file['sha256'])
        for row in file['anchors']:
            identities.append(row['id'])
            check(row['id']+'.meaning_preserved',bool(row['source']) and bool(row['category']) and
                  row['declarative_coverage']=='not_promoted_by_source_enumeration')
    check('unique_anchors',len(identities)==len(set(identities)))
    for package,entry in value['prior_evidence'].items():
        original=json.loads((ROOT/entry['file']).read_text())
        check(package+'.exact_prior_record',original==entry['prior_record'])
        check(package+'.every_adverse_case',set(original['adverse'])==set(entry['adverse_dispositions']))
        check(package+'.no_reexecution_claim',entry['reexecuted'] is False)
    check('no_whole_closure',value['whole_requirements_closed']==0 and not value['method_eligible'])
    previous=HERE.parent/'method-input-binding-20261024'
    prior=json.loads((previous/'manifest.json').read_text())
    locks={}
    for group in ['inputs','implementation','outputs']:
        locks.update(prior[group])
    paths=[ROOT/PLAN,ROOT/NEXT,previous/'manifest.json',ROOT/'scripts/core0_ir_v1.py',
           ROOT/'scripts/reconstruction_v1.py']+[ROOT/name for name in FILES]
    for package in EVIDENCE:
        for name in ['checks.json','verify.py','manifest.json']:
            paths.append(HERE.parent/package/name)
    packet=HERE.parent/'company-composition-20261016/attempt-03/portable-exchanges.json'
    dependency=json.loads(packet.read_text())['input_snapshots']['financial_checks.py']
    check('surrounding_method_dependency_identity',sha(ROOT/dependency['path'])==dependency['sha256'])
    value['pinned_external_method']={**dependency,'coverage':'dependency identity only; internals outside selected six-file audit'}
    paths.extend([packet,ROOT/dependency['path']])
    for path in sorted(set(paths)):
        name=str(path.relative_to(ROOT))
        if name in locks:
            check('consistent_lock:'+name,locks[name]==sha(path))
        else:
            locks[name]=sha(path)
    for name,h in locks.items():
        check('protected_input:'+name,sha(ROOT/name)==h)
    summary={'passed':all(c['passed'] for c in checks),'checks':checks,'anchors':len(identities),
             'files':len(value['files']),'functions':sum(len(f['functions']) for f in value['files']),
             'prior_adverse_cases':sum(len(e['prior_record']['adverse']) for e in value['prior_evidence'].values()),
             'prior_checks':sum(len(e['prior_record']['checks']) for e in value['prior_evidence'].values())}
    return summary,value,locks


def main():
    mode=sys.argv[1] if len(sys.argv)==2 else '--check'
    assert mode in ['--check','--record','--replay']
    assert mode!='--record' or not (HERE/'manifest.json').exists(),'record exists'
    started=datetime.now(timezone.utc).isoformat()
    clock=time.monotonic()
    if mode=='--replay':
        manifest=json.loads((HERE/'manifest.json').read_text())
        for group in ['inputs','implementation','outputs']:
            for name,h in manifest[group].items():
                assert sha(ROOT/name)==h,name
    result,value,locks=conformance()
    observation={'mode':mode,'passed':result['passed'],'checks':len(result['checks']),
                 'anchors':result['anchors'],'functions':result['functions'],
                 'prior_adverse_cases':result['prior_adverse_cases'],'prior_checks':result['prior_checks'],
                 'protected_inputs':len(locks),'failed':[c['name'] for c in result['checks'] if not c['passed']],
                 'wall_seconds':time.monotonic()-clock}
    if not result['passed']:
        dump(HERE/('failed-'+str(time.time_ns())+'.json'),result)
    elif mode=='--record':
        for name,body in [('checks.json',result),('inventory.json',value),('source-lock.json',locks)]:
            dump(HERE/name,body)
        dump(HERE/'manifest.json',{'started_utc':started,'wall_seconds':observation['wall_seconds'],
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B '+str(HERE.relative_to(ROOT)/'verify.py')+' --record',
            'environment':'Python '+platform.python_version()+'; AST/source review',
            'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A: deterministic source audit',
            'data_version':'Six pinned method boundary files and three historical evidence packages',
            'plan':PLAN,'result':str(HERE.relative_to(ROOT)/'result.md'),'inputs':locks,
            'implementation':{str(p.relative_to(ROOT)):sha(p) for p in HERE.iterdir() if p.suffix in ['.py','.md']},
            'outputs':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['checks.json','inventory.json','source-lock.json']}})
    elif mode=='--replay':
        assert result==json.loads((HERE/'checks.json').read_text())
        assert value==json.loads((HERE/'inventory.json').read_text())
        assert locks==json.loads((HERE/'source-lock.json').read_text())
    print(json.dumps(observation))
    return 0 if result['passed'] else 1


if __name__=='__main__':
    sys.exit(main())
