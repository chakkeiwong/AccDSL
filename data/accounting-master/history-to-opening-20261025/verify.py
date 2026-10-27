from hashlib import sha256
from pathlib import Path
import argparse
import io
import json
import platform
import subprocess
import sys
import time
import unittest

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import conditional_company_opening_v1 as adapter
import test_conditional_company_opening_v1 as examples


def sha(path):return sha256(path.read_bytes()).hexdigest()
def dump(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def tests(names):
    suites=[unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern=n) for n in names]
    assert all(s.countTestCases() for s in suites)
    stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.TestSuite(suites))
    return result,stream.getvalue()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record',action='store_true');args=parser.parse_args()
    if args.record:assert not (HERE/'checks.json').exists()
    start=time.time()
    focal=['test_conditional_company_opening_v1.py']
    regression=['test_typed_history_measurement_attachment_v1.py','test_typed_affine_history_v1.py',
                'test_company_book_transition_v1.py','test_company_memory_types_v1.py']
    paths=[Path(__file__),HERE/'audit.md',ROOT/'docs/plans/accounting-history-to-opening-20261025.md']
    paths += [ROOT/'tests'/n for n in focal+regression]
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path and Path(path).suffix=='.py' and Path(path).is_relative_to(ROOT):paths.append(Path(path))
    lock={str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))}
    if not args.record:assert lock==json.loads((HERE/'source-lock.json').read_text())
    focused,flog=tests(focal);prior,rlog=tests(regression)
    if args.record:(HERE/'focused.log').write_text(flog);(HERE/'regression.log').write_text(rlog)
    assert focused.wasSuccessful(),flog[-3000:]
    assert prior.wasSuccessful(),rlog[-3000:]
    cases=[];checks=[]
    for owner in ['alpha','beta']:
        for selected,expected in [((10,2,3),'5/1'),((8,3,4),'7/1')]:
            request=examples.request(owner,selected);result=adapter.map_opening(request)
            name=owner+':'+str(selected)
            values={'conditional':result['status']=='conditional_opening',
                'all_balances':sorted(result['opening']['balances'].values())==['-15/1','15/1'],
                'memory':result['opening']['memory']['history']['sales/a~1']==expected,
                'source_date':result['provenance']['source_snapshot_date']=='2024-12-31',
                'opening_date':result['opening']['date']=='2025-01-01',
                'source_retained':result['provenance']['attachment_definition']==request['attachment'],
                'witness_retained':result['provenance']['selected_witness']==request['witness'],
                'false_flags':all(result[k] is False for k in adapter.FLAGS),
                'replay':adapter.verify(request,result)}
            checks.extend({'name':name+':'+k,'passed':bool(v)} for k,v in values.items())
            cases.append({'case':name,'request':request,'result':result})
    assert all(r['passed'] for r in checks)
    assert all(sha(ROOT/n)==h for n,h in lock.items()),'source_changed_during_run'
    summary={'passed':True,'focused_tests':focused.testsRun,'regression_tests':prior.testsRun,
             'named_comparisons':len(checks),'cases':len(cases),'protected_files':len(lock)}
    comparison={'checks':checks,'cases':cases}
    if args.record:
        dump(HERE/'source-lock.json',lock);dump(HERE/'checks.json',summary);dump(HERE/'comparison.json',comparison)
        dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B '+str(Path(__file__).relative_to(ROOT))+' --record','python':sys.version,
            'executable':sys.executable,'platform':platform.platform(),'solver_version':adapter.attachment.z3.get_version_string(),
            'cpu_gpu':'CPU-only Python/Z3; no GPU import','seeds':'N/A: exact checked witnesses',
            'data_version':'Synthetic source-locked fixtures','wall_seconds':time.time()-start,
            'plan':'docs/plans/accounting-history-to-opening-20261025.md','result':str(HERE.relative_to(ROOT)/'result.md'),
            'artifacts':['checks.json','comparison.json','source-lock.json','focused.log','regression.log']})
    else:
        assert summary==json.loads((HERE/'checks.json').read_text())
        assert adapter.core.canonical(comparison)==adapter.core.canonical(json.loads((HERE/'comparison.json').read_text()))
    print(json.dumps({**summary,'mode':'record' if args.record else 'read_only_replay'}))


if __name__=='__main__':main()
