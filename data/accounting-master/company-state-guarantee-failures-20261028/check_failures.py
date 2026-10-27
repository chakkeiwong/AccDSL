"""Inspect original guarantee failures against an unchanged finite native method."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
NATIVE=ROOT/'data/accounting-master/sector-company-composition-20261016'
PLAN='docs/plans/company-state-guarantee-failures-20261028.md'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False)
    start=time.monotonic()
    spec=importlib.util.spec_from_file_location('original_guarantee_probe_native',NATIVE/'reference.py')
    native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
    case=next(x for x in json.loads((NATIVE/'authored-cases.json').read_text())['cases'] if x['id']=='joined-sector-group')
    prior=next(x for x in json.loads((NATIVE/'attempt-01/exchanges.json').read_text()) if x['id']==case['id'])
    base=deepcopy(case['request']);checks=[];cases=[]
    def check(name,actual,expected,role='promotion criterion'):
        checks.append(dict(name=name,passed=actual==expected,actual=actual,expected=expected,role=role))
    def evaluate(name,request,status,reason=None,reader=None):
        before=deepcopy(request);r=native.calculate(request,reader)
        cases.append(dict(id=name,request=deepcopy(request),result=r))
        check(name+'/status',r['status'],status)
        if reason is not None:check(name+'/reason',r['reason'],reason,'explanatory diagnostic')
        check(name+'/request unchanged',request,before,'promotion veto')
        check(name+'/no postings',[r['posts'],r['mutations']],[False,[]],'promotion veto')
        if status!='conditional_complete':
            check(name+'/no report or components',[r['report'],r['components']],[None,None],'promotion veto')
        return r
    r=evaluate('unchanged native baseline',deepcopy(base),'conditional_complete')
    check('entire native baseline reproduces retained output',r,prior['result'],'continuation veto')
    check('baseline request reproduces retained input',base,prior['request'],'continuation veto')
    report=r['report']
    check('unpaid guarantee liability remains',[x['guarantee']['liability'] for x in report['rows']],['7','3'])
    check('unpaid guarantee recognized initially',report['opening']['parent_equity'],'654')
    check('no guarantee settlement origin',[x for x in report['cash_origins'] if 'guarantee' in x['kind']],[])
    check('external liability retained in legal books',[x['legal']['P']['guarantee'] for x in report['rows']],['7','3'])
    for field in base['guarantee']:
        q=deepcopy(base);del q['guarantee'][field]
        evaluate('omitted guarantee/'+field,q,'rejected','guarantee_shape')
    q=deepcopy(base);del q['guarantee'];evaluate('omitted guarantee object',q,'rejected','request_shape')
    q=deepcopy(base);q['guarantee']=None;evaluate('null guarantee object',q,'rejected','guarantee_shape')
    for field,status,reason in [('opening_unamortized','unresolved','missing_amount'),('income_releases','unsupported','guarantee_profile'),('ecl','unsupported','guarantee_profile')]:
        q=deepcopy(base);q['guarantee'][field]=None
        evaluate('null measurement/'+field,q,status,reason)
    for field,value in [('opening_unamortized','0'),('income_releases',['0','0']),('ecl',['0','0']),('ecl',[None,'3']),('income_releases',['2',None])]:
        q=deepcopy(base);q['guarantee'][field]=value
        evaluate('nonprofile measurement/'+field+'/'+json.dumps(value),q,'unsupported','guarantee_profile')
    for field in sorted(k for k in base['findings'] if 'guarantee' in k):
        for value in [None,False]:
            q=deepcopy(base);q['findings'][field]=value
            evaluate('support/'+field+'/'+str(value),q,'unresolved' if value is None else 'unsupported',('missing_' if value is None else 'outside_')+field)
    locked=json.loads((NATIVE/'input-lock.json').read_text())['files']
    for item in locked:
        check('protected input/'+item['path'],sha256((ROOT/item['path']).read_bytes()).hexdigest(),item['sha256'],'continuation veto')
        for mode in ['missing','changed']:
            def reader(p,target=item['path'],mode=mode):
                if p==target:
                    if mode=='missing':raise FileNotFoundError(p)
                    return b'changed'
                return (ROOT/p).read_bytes()
            evaluate(mode+' input/'+item['path'],deepcopy(base),'unresolved' if mode=='missing' else 'rejected','missing_protected_input' if mode=='missing' else 'changed_protected_input',reader)
    original=json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())
    rows=[x['original_row'] for x in original['rows'] if x['original_row']['id'] in ['SIM-F004','SIM-F010']]
    failed=[x for x in checks if not x['passed']]
    verification=dict(status='fail' if failed else 'pass',checks=len(checks),cases=len(cases),failed=[x['name'] for x in failed],
        original_rows=[x['id'] for x in rows],source_challenges=2*len(locked),original_statuses_changed=False,
        limitations=['Missing fields reject; unknown disclosure structure is retained by this audit packet, not a native reconstruction family.',
        'Null ECL and service release are unsupported rather than unresolved in the exact-profile native method.',
        'A disclosed never-paid guarantee is retained, but adding a hidden contract to admissible history families remains untested.'])
    inputs=[Path(__file__),ROOT/PLAN,NATIVE/'reference.py',NATIVE/'authored-cases.json',NATIVE/'input-lock.json',NATIVE/'attempt-01/exchanges.json',ROOT/'data/accounting-master/unified-program-20261028/failure-map.json']
    for m in list(sys.modules.values()):
        p=getattr(m,'__file__',None)
        if p and Path(p).is_file() and Path(p).resolve().is_relative_to(ROOT):inputs.append(Path(p).resolve())
    inputs.extend(ROOT/x['path'] for x in locked)
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],environment=sys.version,cpu_gpu='CPU-only Fraction; no accelerator imports',
        random_seeds='N/A deterministic',data_version='Unchanged retained SectorCompany/1 synthetic case',
        utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plan_file=PLAN,
        result_file=str((HERE/'result.md').relative_to(ROOT)),source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(set(inputs))})
    for name,value in [('verification',verification),('checks',checks),('cases',cases),('original-rows',rows),('run-manifest',manifest)]:
        (out/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps(verification));return bool(failed)

if __name__=='__main__':raise SystemExit(main())
