from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
from copy import deepcopy
import json,os,platform,subprocess,sys,time
import reference as candidate
import fixtures as f
H=Path(__file__).resolve().parent;R=H.parents[2];A=H/('attempt-'+sys.argv[1]);A.mkdir(exist_ok=False)
started=datetime.now(timezone.utc).isoformat();clock=time.monotonic()
def sha(p):return sha256(p.read_bytes()).hexdigest()
def save(n,x):(A/n).write_text(json.dumps(x,indent=2)+chr(10))
checks=[];cases=[];controls=[]
def ck(n,v):checks.append(dict(name=n,passed=bool(v)));assert v,n
base=H.parent/'acquisition-debt-relationship-20261027/attempt-01'
lock=json.loads((base/'source-lock.json').read_text())
for p,h in lock.items():ck('baseline:'+p,sha(R/p)==h)
for p in [H/'contract.md',H/'reference.py',H/'fixtures.py',H/'verify.py',R/'docs/plans/accounting-debtor-conversion-worksheet-20261027.md',base/'verification.json',base/'cases.json',base/'source-lock.json']:
    lock[str(p.relative_to(R))]=sha(p)
save('source-lock.json',lock)
for n in ['contract.md','reference.py','fixtures.py','verify.py']:(A/n).write_bytes((H/n).read_bytes())
try:
    ck('baseline_pass',json.loads((base/'verification.json').read_text())['status']=='PASS')
    ck('cpu_hidden',os.environ.get('CUDA_VISIBLE_DEVICES')=='-1')
    for row in f.cases():
        out=candidate.report(row['request']);ck('complete_measured:'+row['id'],out==row['expected'])
        cases.append(dict(**row,actual=out))
    for name,r,deps in f.unresolved():
        p=r['payload'];q=p['scope_request'];role=q['payload']['perspective'];changes={k:v for k,v in q['payload']['assertions'].items() if v!=f.old.DEFAULT[k]}
        _,sc=f.scope_pair(role,changes or None)
        expected=dict(profile=f.PROFILE,source_admission=False,accounting_admission=False,posting_authorized=False,report_authorized=False,
          request_sha256=f.digest(r),scope_result=sc,schedule=deepcopy(p['schedule']),source=deepcopy(p['source']),
          scope_assessment='supplied_assertions_only',status='method_required',dependencies=sorted(deps),request=deepcopy(r),report=None)
        out=candidate.report(r);ck('complete_unresolved:'+name,out==expected)
        cases.append(dict(id=name,request=r,expected=expected,actual=out))
    def refuse(name,mutate,rebind=True,reason=None):
        r=f.request();mutate(r)
        if rebind:f.bind(r)
        out=candidate.report(r);ck('refusal:'+name,out['status']=='invalid')
        if reason:ck('reason:'+name,out['reason']==reason)
        ck('no_permission:'+name,all(out.get(k) is False for k in candidate.FLAGS))
        controls.append(dict(id=name,request=r,actual=out))
    refuse('profile',lambda r:r.update(profile='other'),False,'profile')
    refuse('payload_hash',lambda r:r.update(expected_payload_sha256='bad'),False,'payload_binding')
    refuse('scope_hash',lambda r:r['payload'].update(scope_result_sha256='bad'),True,'scope_result_binding')
    refuse('unit',lambda r:r['payload']['schedule'].update(unit='millions'),True,'units')
    refuse('currency',lambda r:r['payload']['schedule'].update(currency='HKD'),True,'units')
    refuse('source_subject',lambda r:r['payload']['source'].update(subject='P'),True,'source_context')
    refuse('source_actor',lambda r:r['payload']['source'].update(actor='other'),True,'source_context')
    refuse('opening_after_event',lambda r:r['payload']['schedule'].update(opening_at='2026-10-27T01:30:00Z'),True,'schedule_dates')
    refuse('closing_after_cutoff',lambda r:r['payload']['schedule'].update(close_at='2026-10-28T02:00:00Z'),True,'schedule_dates')
    refuse('float_value',lambda r:r['payload']['schedule']['measurement'].update(equity_fair_value=70.0),True,'exact_number')
    refuse('negative_value',lambda r:r['payload']['schedule']['measurement'].update(equity_fair_value='-1/1'),True,'nonnegative_equity_fair_value')
    refuse('zero_denominator',lambda r:r['payload']['schedule']['measurement'].update(equity_fair_value='1/0'),True,'exact_number')
    refuse('wrong_opening',lambda r:r['payload']['schedule']['opening'].update(cash='31/1'),True,'selected_opening')
    refuse('extra_cash',lambda r:r['payload']['schedule'].update(cash_paid='70/1'),True,'schedule_fields')
    refuse('missing_tax',lambda r:r['payload']['schedule']['premises'].pop('tax'),True,'premises_fields')
    refuse('invented_tax_method',lambda r:r['payload']['schedule']['premises'].update(tax='assume_zero'),True,'premise_tax')
    refuse('bad_reliability',lambda r:r['payload']['schedule']['measurement'].update(equity_fv_reliable=True),True,'measurement_reliability')
    def stale_schedule(r):
        r['payload']['schedule']['measurement']['equity_fair_value']='120/1';r['expected_payload_sha256']=f.digest(r['payload'])
    refuse('stale_schedule',stale_schedule,False,'schedule_source_binding')
    def stale_source(r):
        r['payload']['source']['rationale']='Changed';r['expected_payload_sha256']=f.digest(r['payload'])
    refuse('stale_source',stale_source,False,'evidence_binding')
    for p,h in lock.items():ck('protected:'+p,sha(R/p)==h)
    save('cases.json',cases);save('controls.json',controls);save('checks.json',checks)
    result=dict(status='PASS',cases=len(cases),measured_cases=4,unresolved_cases=len(cases)-4,refusal_controls=len(controls),assertions=len(checks),protected_files=len(lock),**candidate.FLAGS)
    save('verification.json',result);print(json.dumps(result))
except Exception as exc:
    save('failure.json',dict(error=str(exc),checks=checks,cases=cases,controls=controls));raise
finally:
    save('run-manifest.json',dict(command=sys.argv,git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),
      environment=platform.python_version(),cpu_gpu='CPU; GPU intentionally hidden',CUDA_VISIBLE_DEVICES=os.environ.get('CUDA_VISIBLE_DEVICES'),
      started_utc=started,wall_seconds=time.monotonic()-clock,seeds='N/A deterministic exact fractions',data_version='source-lock.json',
      plan='docs/plans/accounting-debtor-conversion-worksheet-20261027.md',result=str((H/'result.md').relative_to(R)),artifacts=str(A.relative_to(R))))
