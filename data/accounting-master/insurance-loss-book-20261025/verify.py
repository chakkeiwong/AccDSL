"""Record/replay the complete insurer proposals and their native correspondence."""
from pathlib import Path
from hashlib import sha256
import io
import importlib.util
import json
import platform
import subprocess
import sys
import time
import unittest

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(HERE))
import examples
import insurance_loss_book_v1 as bridge
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,separators=(',',':'))+'\n')

def main():
    record='--record' in sys.argv;started=time.monotonic()
    if record:assert not (HERE/'evidence.json').exists()
    # Capture fixtures loaded outside sys.modules, and data read by regressions.
    reads=set();tracking={'active':False}
    def capture(event,args):
        if event!='open' or not tracking['active'] or not isinstance(args[0],(str,bytes)):return
        name,mode,flags=args
        if mode is not None and 'r' not in mode and '+' not in mode:return
        if mode is None and flags & 3 == 1:return
        p=Path(name.decode() if isinstance(name,bytes) else name).resolve()
        if p.suffix=='.pyc':
            try:p=Path(importlib.util.source_from_cache(str(p)))
            except ValueError:return
        if p.is_relative_to(ROOT) and p.is_file():reads.add(p)
    sys.addaudithook(capture)
    patterns=['test_insurance_loss_book_v1.py','test_company_book_transition_v1.py',
              'test_company_method_clock_v1.py','test_company_book_reports_v1.py']
    tests=[]
    for pattern in patterns:
        tracking['active']=True
        stream=io.StringIO();suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern=pattern)
        r=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
        tracking['active']=False
        assert r.wasSuccessful() and r.testsRun,stream.getvalue()
        tests.append({'pattern':pattern,'count':r.testsRun})
        if record:(HERE/(pattern+'.log')).write_text(stream.getvalue())
        print(json.dumps({'tests':pattern,'passed':r.testsRun}),flush=True)
    folder=HERE/'cases';folder.mkdir(exist_ok=True);cases=[]
    for chart in ['named','numbered']:
        for case in bridge.CASES:
            for complement in [False,True]:
                name=chart+'.'+case+('.complement' if complement else '.isolated')
                tracking['active']=True
                row=examples.checked_case(chart,case,complement)
                tracking['active']=False
                p=folder/(name+'.json')
                if record:assert not p.exists();dump(p,row)
                else:assert row==json.loads(p.read_text()),name
                cases.append({'name':name,'path':str(p.relative_to(ROOT)),'sha256':sha(p)})
                print(json.dumps({'case':name,'passed':True}),flush=True)
    locks={}
    def lock(p,expected=None):
        p=p if isinstance(p,Path) else ROOT/p;actual=sha(p)
        if expected is not None:assert actual==expected,str(p)
        locks[str(p.relative_to(ROOT))]=actual
    for module in list(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name and Path(name).resolve().parent==ROOT/'scripts' and Path(name).suffix=='.py':lock(Path(name).resolve())
    for p in sorted(reads):lock(p)
    for name,expected in bridge.PINS.items():lock(name,expected)
    for row in json.loads((ROOT/(bridge.NATIVE+'input-lock-v2.json')).read_text())['files']:lock(row['path'],row['sha256'])
    for p in [Path(__file__),HERE/'examples.py',HERE/'audit.md',ROOT/'docs/plans/accounting-insurance-loss-book-20261025.md',
              ROOT/'data/accounting-master/company-book-transition-20261025/examples.py',
              ROOT/'data/accounting-master/company-method-clock-20261025/examples.py']:
        lock(p)
    for pattern in patterns:lock(ROOT/'tests'/pattern)
    evidence={'tests':tests,'cases':cases,'case_count':len(cases),'native_cases':2,'journals_per_case':6,
        'loss_origins_per_case':6,'reports_per_case':2,'scope':'Exact retained insurer proposals; no domain/source or fiscal-completeness admission'}
    if record:
        dump(HERE/'evidence.json',evidence);lock(HERE/'evidence.json')
        for pattern in patterns:lock(HERE/(pattern+'.log'))
        dump(HERE/'source-lock.json',locks)
        dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B data/accounting-master/insurance-loss-book-20261025/verify.py --record',
            'environment':sys.version,'platform':platform.platform(),'cpu_gpu':'CPU exact rational replay; no GPU frameworks imported',
            'seeds':'N/A deterministic','data_version':'Two retained InsuranceOrigins/1 cases, two charts and complement variants',
            'wall_seconds':time.monotonic()-started,'plan':'docs/plans/accounting-insurance-loss-book-20261025.md',
            'result':str((HERE/'result.md').relative_to(ROOT)),
            'provenance':'Git base plus hashes of exact executed uncommitted sources',
            'artifacts':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['evidence.json','source-lock.json']}})
    else:
        assert evidence==json.loads((HERE/'evidence.json').read_text())
        saved=json.loads((HERE/'source-lock.json').read_text())
        for name,expected in saved.items():assert sha(ROOT/name)==expected,name
        for name,expected in locks.items():assert saved[name]==expected,name
        for name,expected in json.loads((HERE/'run-manifest.json').read_text())['artifacts'].items():assert sha(ROOT/name)==expected,name
    print(json.dumps({'passed':True,'mode':'record' if record else 'read_only_replay','focused':tests[0]['count'],
        'regressions':sum(r['count'] for r in tests[1:]),'cases':len(cases),'locked_files':len(json.loads((HERE/'source-lock.json').read_text()))}),flush=True)

if __name__=='__main__':main()
