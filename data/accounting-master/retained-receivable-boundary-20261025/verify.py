"""Retained-source comparison: record once and replay without mutation."""
from hashlib import sha256
from pathlib import Path
import importlib.metadata
import io
import json
import platform
import subprocess
import sys
import time
import unittest

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE))
import boundary

def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+chr(10))
def check(ok,msg):
    if not ok:raise RuntimeError(msg)

def main():
    start=time.monotonic();record='--record' in sys.argv
    check(set(sys.argv[1:])<={'--record'},'unknown argument')
    check(not record or not (HERE/'evidence.json').exists(),'Evidence exists; replay without --record')
    locks={};sources=['real-company-input-readiness-20261024','populated-source-contracts-20261025']
    for name in sources:
        path=HERE.parent/name/'source-lock.json'
        for filename,expected in json.loads(path.read_text()).items():
            check(sha(ROOT/filename)==expected,'protected input changed: '+filename);locks[filename]=expected
        locks[str(path.relative_to(ROOT))]=sha(path)
    if not record:
        for name,h in json.loads((HERE/'source-lock.json').read_text()).items():check(sha(ROOT/name)==h,'locked input: '+name)
    output=io.StringIO();suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_retained_receivable_boundary.py')
    tests=unittest.TextTestRunner(stream=output,verbosity=2).run(suite)
    check(tests.wasSuccessful() and tests.testsRun==7,output.getvalue())
    cases={};summaries={}
    for view in ['annual','interim','combined']:
        request=boundary.fixture(view);result=boundary.evaluate(request)
        check(boundary.verify(request,result),'exact source-boundary replay')
        cases[view]={'request':request,'result':result}
        summaries[view]={'sha256':boundary.readiness.digest(cases[view]),'observations':len(result['observations']),
            'notes':len(result['notes']),'fields':len(result['field_mapping']),'executed':result['executed']}
    original=json.loads((boundary.PRIOR/'readiness.json').read_text())[boundary.readiness.OPS]
    replay=boundary.readiness.evaluate(boundary.readiness.fixture())
    check(original==replay,'retained readiness changed')
    evidence={'profile':boundary.PROFILE,'tests':tests.testsRun,'cases':summaries,
        'prior_readiness_equal':True,'scope':'Source-bound partial representation; identified-claim execution remains unsupported'}
    if record:
        dump(HERE/'evidence.json',evidence);(HERE/'tests.log').write_text(output.getvalue())
        for view,case in cases.items():dump(HERE/(view+'.json'),case)
        for module in tuple(sys.modules.values()):
            f=getattr(module,'__file__',None)
            if f:
                p=Path(f).resolve()
                if p.suffix=='.py' and p.is_relative_to(ROOT):locks[str(p.relative_to(ROOT))]=sha(p)
        for name in ['docs/plans/accounting-retained-receivable-boundary-20261025.md',
                     *[str((HERE/n).relative_to(ROOT)) for n in ['boundary.py','verify.py','audit.md','evidence.json','tests.log',*[v+'.json' for v in cases]]],
                     str((boundary.PRIOR/'readiness.json').relative_to(ROOT))]:
            locks[name]=sha(ROOT/name)
        dump(HERE/'source-lock.json',dict(sorted(locks.items())))
        dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'worktree':'Uncommitted local work; exact bytes in source-lock.json',
            'command':'python3 -B data/accounting-master/retained-receivable-boundary-20261025/verify.py --record',
            'environment':sys.version,'platform':platform.platform(),
            'packages':{p:importlib.metadata.version(p) for p in ['PyMuPDF','beautifulsoup4','jsonschema']},
            'cpu_gpu':'CPU file/JSON/PDF/HTML processing; no GPU framework imported',
            'seeds':'N/A: deterministic','wall_seconds':time.monotonic()-start,
            'data_version':boundary.readiness.PACKET_SHA,'plan':'docs/plans/accounting-retained-receivable-boundary-20261025.md',
            'result':str((HERE/'result.md').relative_to(ROOT)),
            'artifact_hashes':{n:sha(HERE/n) for n in ['evidence.json','source-lock.json','tests.log',*[v+'.json' for v in cases]]}})
    else:
        check(evidence==json.loads((HERE/'evidence.json').read_text()),'evidence differs')
        for view,case in cases.items():check(case==json.loads((HERE/(view+'.json')).read_text()),'case differs: '+view)
        for name,h in json.loads((HERE/'run-manifest.json').read_text())['artifact_hashes'].items():
            check(sha(HERE/name)==h,'manifest artifact differs: '+name)
    print(json.dumps({'passed':True,'mode':'record' if record else 'read_only_replay','tests':tests.testsRun,
        'views':3,'combined_observations':12,'requirements':18,'locked_files':len(locks) if record else len(json.loads((HERE/'source-lock.json').read_text()))}))

if __name__=='__main__':main()
