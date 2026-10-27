"""Check reused population semantics and retain read-only replay evidence."""
from hashlib import sha256
from pathlib import Path
import io
import json
import platform
import subprocess
import sys
import time
import unittest

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE))
import populations as pop

def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+chr(10))
def check(ok,msg):
    if not ok:raise RuntimeError(msg)

def main():
    start=time.monotonic();record='--record' in sys.argv
    check(set(sys.argv[1:])<={'--record'},'unknown argument')
    check(not record or not (HERE/'evidence.json').exists(),'Evidence exists; replay without --record')
    locks={}
    for directory in ['source-constrained-state-20261024','retained-receivable-boundary-20261025']:
        lock=HERE.parent/directory/'source-lock.json'
        for name,h in json.loads(lock.read_text()).items():
            check(sha(ROOT/name)==h,'protected input changed: '+name);locks[name]=h
        locks[str(lock.relative_to(ROOT))]=sha(lock)
    if not record:
        for name,h in json.loads((HERE/'source-lock.json').read_text()).items():check(sha(ROOT/name)==h,'locked input: '+name)
    tests=[];logs={}
    for pattern in ['test_partial_claim_populations.py','test_method_collections_v1.py','test_company_memory_types_v1.py']:
        output=io.StringIO();suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern=pattern)
        result=unittest.TextTestRunner(stream=output,verbosity=2).run(suite)
        check(result.wasSuccessful() and result.testsRun>0,output.getvalue())
        tests.append({'pattern':pattern,'count':result.testsRun});logs[pattern+'.log']=output.getvalue()
    cases={};summaries={}
    for view in ['annual','interim','combined']:
        body=pop.partial_state.fixture(view=view);result=pop.evaluate(body)
        check(pop.verify(body,result),'exact population replay')
        cases[view]={'request':body,'result':result}
        summaries[view]={'sha256':pop.core.digest(cases[view]),'populations':len(result['populations']),
            'preserved_constraints':len(result['partial_state']['constraints']),'executed':result['executed']}
    context={'entity':'Constructed example','scope':'declared legal book','currency':'USD','scale':'1/1'}
    row=lambda i,n:{'id':pop.known(i),'due':pop.known('2027-01-31'),'remaining':pop.known(n)}
    examples={'partial':{'status':'partial','rows':[],'reason':'Unidentified members'},
        'empty':{'status':'complete','rows':[]},
        'identified':{'status':'complete','rows':[row('a','20/1'),row('b','40/1')]}}
    constructed={k:pop.inspect(context,v) for k,v in examples.items()}
    check(constructed['partial']['claim_count']['status']=='unknown','unknown population')
    check(constructed['empty']['claim_count']==pop.known(0),'empty population')
    check(constructed['identified']['gross_remaining']==pop.known('60/1'),'independent gross total')
    evidence={'profile':pop.PROFILE,'tests':tests,'cases':summaries,'constructed':constructed,
        'scope':'Partial source measurements and existing collection semantics; no executable company state'}
    if record:
        dump(HERE/'evidence.json',evidence)
        for view,case in cases.items():dump(HERE/(view+'.json'),case)
        for name,content in logs.items():(HERE/name).write_text(content)
        for module in tuple(sys.modules.values()):
            f=getattr(module,'__file__',None)
            if f:
                path=Path(f).resolve()
                if path.suffix=='.py' and path.is_relative_to(ROOT):locks[str(path.relative_to(ROOT))]=sha(path)
        for name in ['docs/plans/accounting-partial-claim-populations-20261025.md',
            *[str((HERE/n).relative_to(ROOT)) for n in ['populations.py','verify.py','audit.md','evidence.json',*logs,*[v+'.json' for v in cases]]]]:
            locks[name]=sha(ROOT/name)
        dump(HERE/'source-lock.json',dict(sorted(locks.items())))
        dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'worktree':'Uncommitted work; exact bytes in source-lock.json',
            'command':'python3 -B data/accounting-master/partial-claim-populations-20261025/verify.py --record',
            'environment':sys.version,'platform':platform.platform(),'cpu_gpu':'CPU deterministic Python; no GPU framework imported',
            'seeds':'N/A: deterministic','wall_seconds':time.monotonic()-start,
            'data_version':'Retained Apple partial-state sources and separately constructed collection examples',
            'plan':'docs/plans/accounting-partial-claim-populations-20261025.md','result':str((HERE/'result.md').relative_to(ROOT)),
            'artifact_hashes':{n:sha(HERE/n) for n in ['source-lock.json','evidence.json',*logs,*[v+'.json' for v in cases]]}})
    else:
        check(evidence==json.loads((HERE/'evidence.json').read_text()),'evidence differs')
        for view,case in cases.items():check(case==json.loads((HERE/(view+'.json')).read_text()),'case differs: '+view)
        for name,h in json.loads((HERE/'run-manifest.json').read_text())['artifact_hashes'].items():check(sha(HERE/name)==h,'manifest artifact changed: '+name)
    print(json.dumps({'passed':True,'mode':'record' if record else 'read_only_replay',
        'focused':tests[0]['count'],'regressions':sum(t['count'] for t in tests[1:]),'source_views':3,
        'constructed_cases':3,'locked_files':len(locks) if record else len(json.loads((HERE/'source-lock.json').read_text()))}))

if __name__=='__main__':main()
