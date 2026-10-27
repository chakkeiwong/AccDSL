"""Missing openings remain unknown; complete and partial traces are preserved."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import argparse,json,subprocess,sys,time
import admission
rel=admission.rel;ROOT=admission.ROOT
PLAN='docs/plans/company-state-population-admission-20261028.md'
INPUT='data/accounting-master/company-operation-path-20261023/example.json'
HERE='data/accounting-master/company-state-population-admission-20261028'

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    out=p.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    path=json.loads((ROOT/INPUT).read_text());source_path=path['initial_year']['source']['path'];source=(ROOT/source_path).read_bytes()
    checks=[];controls={}
    def check(n,a,b):checks.append(dict(name=n,passed=a==b,actual=a,expected=b))
    def inspect(p,s=source):return admission.inspect(p,s,rel.native.digest(p))
    baseline=inspect(path)
    saved_path='data/accounting-master/company-state-asset-cohort-dependencies-20261028/attempt-01/inspection.json'
    saved=json.loads((ROOT/saved_path).read_text())
    check('complete previous inspection exact',baseline['population_inspection'],saved)
    check('complete population remains scoped',baseline['population_complete'],False)
    mutations=[
        ('unknown opening claim',lambda p:p['initial_year']['opening_claims'][0].update(amount='unknown'),'unresolved',None),
        ('unknown opening life',lambda p:p['initial_year']['assets'][0].update(life='unknown'),'unresolved',None),
        ('unknown facility eligibility',lambda p:p['initial_year']['facility'].update(eligible='unknown'),'unresolved',None),
        ('unknown opening inventory cost',lambda p:p['initial_year']['inventory'].update(unit_cost='unknown'),'unresolved',None),
        ('unsupported inventory method',lambda p:p['initial_year']['inventory'].update(method='FIFO'),'unsupported','method'),
        ('unsupported annual coupon',lambda p:p['initial_year']['debt'].update(coupon_years='1/2'),'unsupported','annual_coupon_only'),
        ('invalid opening asset domain',lambda p:p['initial_year']['assets'][0].update(life='0/1'),'invalid','asset_domain'),
        ('invalid opening claim totals',lambda p:p['initial_year']['opening_claims'][0].update(amount='36/1'),'invalid','claim_control'),
    ]
    for name,mutate,status,reason in mutations:
        p=deepcopy(path);mutate(p);saved_input=deepcopy(p);r=inspect(p)
        n=r['native_result'];run=n['years'][0]['run']
        check(name+' no mutation',p,saved_input)
        check(name+' exact native result',n,rel.native.wire(rel.native.execute(p,source)))
        check(name+' not executable',r['status'],'opening_not_executable')
        check(name+' no population fabrication',r['population_inspection'],None)
        check(name+' native classification',r['opening_status'],status)
        check(name+' not complete',r['population_complete'],False)
        check(name+' obligations retained',r['obligations'],run.get('obligations',[]))
        if reason is not None:check(name+' reason',r['reason'],reason)
        if status=='unresolved':check(name+' missing inputs present',bool(r['obligations']),True)
        controls[name]=r
    # Unknown payload after a valid opening keeps the complete executed prefix.
    p=deepcopy(path);next(o for o in p['initial_year']['operations'] if o['kind']=='delivery')['payload']['control_transferred']='unknown'
    r=inspect(p)
    check('operation-level partial inspected',r['status'],'inspected')
    check('operation-level refusal preserved',r['native_result']['years'][0]['run']['status'],'unresolved')
    check('operation-level previous trace reproduced',r['population_inspection'],admission.cohorts.inspect(p,source,rel.native.digest(p)))
    controls['unknown operation payload']=r
    # A later opening failure cannot erase the earlier completed year.
    p=deepcopy(path);p['continuations'][0]['inventory']['unit_cost']='unknown';r=inspect(p)
    check('later opening keeps prefix',r['status'],'inspected')
    check('earlier native year retained',r['native_result']['years'][0],baseline['native_result']['years'][0])
    check('later opening unresolved',r['native_result']['years'][1]['run']['status'],'unresolved')
    check('later unexecuted suffix retained',r['native_result']['unexecuted'],[dict(index=2,period=path['continuations'][1]['period'],status='unresolved',reason='predecessor_incomplete')])
    controls['later opening unresolved']=r
    p=deepcopy(path);p['profile']='wrong';r=inspect(p)
    check('schema refusal',r['status'],'native_refusal')
    check('schema no inspection',r['population_inspection'],None)
    controls['wrong profile']=r
    r=inspect(path,source+b' ')
    check('corrupt source refusal',r['status'],'native_refusal')
    check('corrupt source no inspection',r['population_inspection'],None)
    controls['corrupted source']=r
    try:admission.inspect(path,source,'0'*64);refused=False
    except ValueError:refused=True
    check('external parent rejected',refused,True)
    for name,r in controls.items():
        check(name+' no source admission',r['source_admission'],False)
        check(name+' no actor admission',r['actor_information_admission'],False)
        check(name+' no whole-company claim',r['full_company_constructor'],False)
    files={Path(__file__),Path(admission.__file__),Path(admission.cohorts.__file__),Path(rel.__file__),ROOT/PLAN,ROOT/INPUT,ROOT/source_path,ROOT/saved_path,ROOT/HERE/'opening-probe.json'}
    for m in list(sys.modules.values())+[rel.native,rel.native.reports,rel.native.annual_path]:
        f=getattr(m,'__file__',None)
        if f and Path(f).is_file() and Path(f).resolve().is_relative_to(ROOT):files.add(Path(f).resolve())
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=sys.version,
        cpu_gpu='CPU-only exact native validation; no accelerator imports',random_seeds='N/A deterministic',
        data_version='Native original path and explicit missing/invalid opening controls',utc=datetime.now(timezone.utc).isoformat(),
        wall_seconds=time.monotonic()-start,plan_file=PLAN,result_file=HERE+'/result.md',
        source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(files)})
    failed=[c for c in checks if not c['passed']];v=dict(status='fail' if failed else 'pass',checks=len(checks),failed=failed,controls=len(controls))
    for name,x in [('baseline',baseline),('controls',controls),('checks',checks),('verification',v),('run-manifest',manifest)]:
        (out/(name+'.json')).write_text(json.dumps(x,indent=2)+chr(10))
    for f in [Path(__file__),Path(admission.__file__)]: (out/f.name).write_bytes(f.read_bytes())
    print(json.dumps(v));return bool(failed)
if __name__=='__main__':raise SystemExit(main())
