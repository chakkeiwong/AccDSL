"""Bounded native assessment timeline conformance and byte-pinned replay."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import argparse,json,platform,subprocess,sys,time,unittest
import examples as ex

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def rel(p):return p.resolve().relative_to(ROOT).as_posix()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')

def record():
    assert not (HERE/'manifest.json').exists()
    started=datetime.now(timezone.utc).isoformat();start=time.monotonic()
    patterns=['test_mixed_event_timeline_v2.py','test_mixed_event_timeline_v1.py',
              'test_state_decision_schedule_v1.py','test_annual_period_book_v1.py']
    suite=unittest.TestSuite()
    for p in patterns:
        selected=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern=p)
        assert selected.countTestCases()>0,p;suite.addTests(selected)
    with (HERE/'tests.log').open('w') as log:result=unittest.TextTestRunner(stream=log,verbosity=1).run(suite)
    assert result.wasSuccessful(),'Inspect tests.log'
    rows=[]
    for name,(state,body,expected) in ex.cases().items():
        response=ex.timeline.run(state,body);assert response['status']==expected,name
        rows.append({'name':name,'state':state,'request':body,'expected':expected,'response':response})
    dump(HERE/'exchanges.json',rows)
    # Retain complete manual transitions and actual-turn request, not totals alone.
    state=ex.start();body=ex.root(state);request=ex.manual_decision(state,body)
    decision=ex.timeline.decision.apply(state,request,ex.timeline.decision.propose(state,request))
    native=ex.timeline.runtime.transition(decision['after'],body['operations'][0]['operation'])
    row=next(r for r in rows if r['name']=='sale_then_assessment')['response']
    assert row['trace'][0]['request']==request and row['trace'][0]['result']==decision
    assert row['trace'][1]['result']['transition']==native and row['after']==native['after']
    dump(HERE/'manual-comparator.json',{'request':request,'decision':decision,'native_assessment':native})
    paths={HERE/'examples.py',HERE/'verify.py',ROOT/'docs/plans/accounting-assessment-timeline-20261025.md'}
    paths.update(ROOT/'tests'/p for p in patterns)
    for module in list(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name:
            p=Path(name).resolve()
            if p.is_relative_to(ROOT) and p.is_file() and p.suffix=='.py':paths.add(p)
        folder,lock=getattr(module,'HERE',None),getattr(module,'LOCK',None)
        if isinstance(folder,Path) and isinstance(lock,str):
            p=folder/'source-lock.json'
            if p.is_file() and p.is_relative_to(ROOT):
                paths.add(p);d=json.loads(p.read_text())
                if type(d) is dict:
                    for key,value in d.items():
                        q=ROOT/key
                        if isinstance(value,str) and len(value)==64 and q.is_file():
                            assert sha(q)==value,key;paths.add(q)
    inputs={rel(p):sha(p) for p in sorted(paths)}
    manifest={'started_utc':started,'wall_seconds':time.monotonic()-start,
        'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'command':'CUDA_VISIBLE_DEVICES=-1 python3 -B data/accounting-master/assessment-timeline-20261025/verify.py --record',
        'environment':{'python':sys.version,'executable':sys.executable,'platform':platform.platform()},
        'cpu_gpu':'CPU only; GPUs intentionally hidden by CUDA_VISIBLE_DEVICES=-1; no TensorFlow import',
        'data_version':'Retained synthetic annual-book fixtures and source locks; no issuer tax inputs',
        'random_seeds':'N/A: exact deterministic conformance; no stochastic comparison',
        'plan':'docs/plans/accounting-assessment-timeline-20261025.md',
        'result':'data/accounting-master/assessment-timeline-20261025/result.md',
        'tests':result.testsRun,'focused_tests':12,'regressions':result.testsRun-12,'cases':len(rows),
        'inputs':inputs,'outputs':{rel(HERE/n):sha(HERE/n) for n in ['tests.log','exchanges.json','manual-comparator.json']}}
    dump(HERE/'manifest.json',manifest)
    return {'passed':True,'tests':result.testsRun,'focused_tests':12,'cases':len(rows),'inputs':len(inputs)}

def replay():
    m=json.loads((HERE/'manifest.json').read_text())
    for p,h in {**m['inputs'],**m['outputs']}.items():assert sha(ROOT/p)==h,p
    for row in json.loads((HERE/'exchanges.json').read_text()):
        assert ex.timeline.run(row['state'],row['request'])==row['response'],row['name']
    return {'passed':True,'cases':m['cases'],'tests_recorded':m['tests'],'inputs':len(m['inputs'])}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--record',action='store_true')
    print(json.dumps(record() if p.parse_args().record else replay()))
