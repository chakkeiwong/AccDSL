"""Exact missing-value distinctions and native result/source precedence."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time
import inspect_inputs as inspector

ROOT=inspector.ROOT;HERE=Path(__file__).resolve().parent
PLAN='docs/plans/company-state-guarantee-input-repair-20261028.md'

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    out=p.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    previous=json.loads((HERE/'attempt-01/cases.json').read_text())
    by={x['id']:x for x in previous};base=by['unchanged native baseline']['request']
    results=[];checks=[]
    def check(name,actual,expected):
        checks.append(dict(name=name,passed=actual==expected,actual=actual,expected=expected))
    def evaluate(name,q,obligations,status,native_result=None,reader=None):
        before=deepcopy(q);d=inspector.digest(q);r=inspector.inspect(q,d,reader)
        results.append(dict(id=name,result=r))
        check(name+'/classification',r['inspection_status'],status)
        check(name+'/exact unknown pointers',[(x['pointer'],x['state']) for x in r['obligations']],obligations)
        check(name+'/input unchanged',q,before);check(name+'/input retained',r['input'],before)
        check(name+'/input identity',r['request_sha256'],d)
        check(name+'/no admission',[r[x] for x in ['posts','source_admission','actor_information_admission','population_complete','history_family_constructed']],[False]*5)
        check(name+'/no mutations',r['mutations'],[])
        check(name+'/repeatable',inspector.inspect(q,d,reader),r)
        if native_result is not None:check(name+'/whole native result',r['native_result'],native_result)
        return r
    evaluate('baseline',deepcopy(base),[],'supplied_guarantee_inputs',by['unchanged native baseline']['result'])
    expected={}
    for field in ['id','beneficiary','opening_unamortized','income_releases','ecl']:
        expected['omitted guarantee/'+field]=[('/guarantee/'+field,'omitted')]
    expected.update({'omitted guarantee object':[('/guarantee','omitted')],
        'null guarantee object':[('/guarantee','explicit_null')],
        'null measurement/opening_unamortized':[('/guarantee/opening_unamortized','explicit_null')],
        'null measurement/income_releases':[('/guarantee/income_releases','explicit_null')],
        'null measurement/ecl':[('/guarantee/ecl','explicit_null')],
        'nonprofile measurement/ecl/[null, "3"]':[('/guarantee/ecl/0','explicit_null')],
        'nonprofile measurement/income_releases/["2", null]':[('/guarantee/income_releases/1','explicit_null')]})
    for name,item in by.items():
        if name=='unchanged native baseline' or name.startswith(('missing input/','changed input/')):continue
        obligations=expected.get(name,[])
        if name.startswith('support/') and name.endswith('/None'):
            obligations=[('/findings/'+name.split('/')[1],'explicit_null')]
        evaluate(name,deepcopy(item['request']),obligations,'incomplete_guarantee_inputs' if obligations else 'native_refusal',item['result'])
    q=deepcopy(base);q['guarantee']['ecl']=['7']
    evaluate('missing second interval',q,[('/guarantee/ecl/1','omitted')],'incomplete_guarantee_inputs')
    q=deepcopy(base);del q['findings']['guarantee_ifrs9_scope']
    evaluate('omitted scope finding',q,[('/findings/guarantee_ifrs9_scope','omitted')],'incomplete_guarantee_inputs')
    for value in [[],42,'guarantee']:
        q=deepcopy(base);q['guarantee']=value
        evaluate('malformed guarantee '+str(value),q,[],'native_refusal')
    q=deepcopy(base);q['guarantee']['extra']='0'
    evaluate('unknown extra field',q,[],'native_refusal')
    q=deepcopy(base);q['wire']='SectorCompany/2';del q['guarantee']
    evaluate('wrong wire plus omission',q,[],'not_inspected')
    target=json.loads((inspector.NATIVE/'input-lock.json').read_text())['files'][0]['path']
    for mode in ['missing','changed']:
        def reader(path,mode=mode):
            if path==target:
                if mode=='missing':raise FileNotFoundError(path)
                return b'changed'
            return (ROOT/path).read_bytes()
        q=deepcopy(base);q['guarantee']['ecl']=None
        r=evaluate('source refusal precedes missing ECL/'+mode,q,[],'not_inspected',reader=reader)
        check(mode+'/source refusal reason',r['reason'],'native_source_refusal')
        check(mode+'/native source status',r['native_result']['status'],'unresolved' if mode=='missing' else 'rejected')
    for label,field in [('wrong request digest',None),('changed implementation pin','NATIVE_SHA256'),('changed source-lock pin','LOCK_SHA256')]:
        original=getattr(inspector,field) if field else None
        try:
            if field:setattr(inspector,field,'0'*64)
            try:inspector.inspect(base,'0'*64 if field is None else inspector.digest(base))
            except ValueError as exc:reason=str(exc)
            else:reason='NO REFUSAL'
            expected_reason={'wrong request digest':'request identity mismatch','changed implementation pin':'native implementation identity mismatch','changed source-lock pin':'native source-lock identity mismatch'}[label]
            check(label,reason,expected_reason)
        finally:
            if field:setattr(inspector,field,original)
    failed=[x for x in checks if not x['passed']]
    verification=dict(status='fail' if failed else 'pass',checks=len(checks),cases=len(results),failed=[x['name'] for x in failed],
        native_implementation_changed=False,history_family_constructed=False)
    inputs=[Path(__file__),Path(inspector.__file__),ROOT/PLAN,HERE/'attempt-01/cases.json',inspector.NATIVE/'reference.py',inspector.NATIVE/'input-lock.json']
    for m in list(sys.modules.values()):
        path=getattr(m,'__file__',None)
        if path and Path(path).is_file() and Path(path).resolve().is_relative_to(ROOT):inputs.append(Path(path).resolve())
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],
        environment=sys.version,cpu_gpu='CPU-only Fraction; no accelerator imports',random_seeds='N/A deterministic',
        data_version='Unchanged SectorCompany/1 plus explicit source/shape/null controls',utc=datetime.now(timezone.utc).isoformat(),
        wall_seconds=time.monotonic()-start,plan_file=PLAN,result_file=str((HERE/'result.md').relative_to(ROOT)),
        source_hashes={str(x.relative_to(ROOT)):sha256(x.read_bytes()).hexdigest() for x in sorted(set(inputs))})
    for name,value in [('verification',verification),('checks',checks),('results',results),('run-manifest',manifest)]:
        (out/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps(verification));return bool(failed)

if __name__=='__main__':raise SystemExit(main())
