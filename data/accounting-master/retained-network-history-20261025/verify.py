"""Retain complete source/history exchanges and verify them semantically."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from datetime import datetime,timezone
import importlib.util,io,json,os,platform,subprocess,sys,time,unittest
os.environ['CUDA_VISIBLE_DEVICES']='-1';sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
spec=importlib.util.spec_from_file_location('retained_history_record_examples',HERE/'examples.py')
examples=importlib.util.module_from_spec(spec);spec.loader.exec_module(examples)
adapter=examples.adapter;BUDGET=examples.BUDGET
PLAN='docs/plans/accounting-retained-network-history-20261025.md'
REGRESSIONS=['test_retained_statement_network_v1','test_retained_statement_history_v1','test_typed_history_measurement_attachment_v1']
def sha(path):return sha256(path.read_bytes()).hexdigest()
def dump(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def cases():
    sys.path.insert(0,str(HERE))
    from cases import cases as construct
    return construct()

def tests():
    out={}
    for label,names in [('focused',['test_retained_network_history_v1']),('regressions',REGRESSIONS)]:
        suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(n) for n in names)
        stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=1).run(suite)
        (HERE/(label+'-tests.log')).write_text(stream.getvalue())
        assert result.wasSuccessful(),stream.getvalue()[-3500:]
        out[label]=result.testsRun
    return out

def main():
    mode=sys.argv[1];assert mode in ['--record','--replay']
    started=datetime.now(timezone.utc).isoformat();start=time.monotonic()
    if mode=='--replay':
        m=json.loads((HERE/'manifest.json').read_text())
        for group in ['inputs','outputs']:
            for name,digest in m[group].items():assert sha(ROOT/name)==digest,name
        rows=[]
        for path in sorted((HERE/'exchanges').glob('*.json')):
            row=json.loads(path.read_text());assert adapter.verify_result(row['request'],row['budget'],row['result']),path.name
            rows.append(row)
        assert len(rows)==m['exchanges']
        observation={'passed':True,'mode':mode,'cases':len(rows),'locked_inputs':len(m['inputs']),'wall_seconds':time.monotonic()-start}
        dump(HERE/'replay-observation.json',observation);print(json.dumps(observation));return
    assert not (HERE/'manifest.json').exists(),'record exists'
    counts=tests();rows=cases();(HERE/'exchanges').mkdir(exist_ok=True)
    for row in rows:dump(HERE/'exchanges'/(row['case']+'.json'),row)
    summary=[{'case':r['case'],'status':r['result']['status'],'request_sha256':adapter.core.digest(r['request'])} for r in rows]
    dump(HERE/'semantic-summary.json',summary)
    inputs=adapter.network.source.verify_dependencies()
    for module in list(sys.modules.values()):
        file=getattr(module,'__file__',None)
        if file:
            p=Path(file).resolve()
            if p.is_relative_to(ROOT) and p.is_file():inputs[str(p.relative_to(ROOT))]=sha(p)
    for p in [HERE/'verify.py',HERE/'examples.py',HERE/'audit.md',HERE/'prepare_verifier.py',ROOT/PLAN,adapter.network.source.PACKAGE/'dependency-lock.json']:
        inputs[str(p.relative_to(ROOT))]=sha(p)
    outputs={str(p.relative_to(ROOT)):sha(p) for p in [*sorted((HERE/'exchanges').glob('*.json')),HERE/'semantic-summary.json',HERE/'focused-tests.log',HERE/'regressions-tests.log']}
    manifest={'started_utc':started,'wall_seconds':time.monotonic()-start,
        'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'command':'CUDA_VISIBLE_DEVICES=-1 python3 -B '+str(HERE.relative_to(ROOT)/'verify.py')+' --record',
        'environment':{'python':platform.python_version(),'executable':sys.executable,'z3':adapter.attachment.history.z3.get_version_string()},
        'cpu_gpu':'CPU only; GPU devices intentionally hidden; no TensorFlow import',
        'data_version':'Pinned retained source dependency lock and complete source requests in exchanges',
        'random_seeds':'N/A: exact rational conformance; no stochastic comparison',
        'plan':PLAN,'result':str(HERE.relative_to(ROOT)/'result.md'),'tests':counts,'exchanges':len(rows),
        'inputs':inputs,'outputs':outputs,
        'interpretation':'Semantic replay checks valid witnesses and conflicts; solver witness selection and wall time may vary.'}
    dump(HERE/'manifest.json',manifest)
    print(json.dumps({'passed':True,'tests':counts,'cases':len(rows),'locked_inputs':len(inputs),'wall_seconds':manifest['wall_seconds']}))
if __name__=='__main__':main()
