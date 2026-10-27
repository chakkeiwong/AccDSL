from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,os,platform,subprocess,sys,time
import reference as candidate
import fixtures as f
H=Path(__file__).resolve().parent;R=H.parents[2];A=H/('attempt-'+sys.argv[1]);A.mkdir(exist_ok=False)
clock=time.monotonic();started=datetime.now(timezone.utc).isoformat()
def sha(p):return sha256(p.read_bytes()).hexdigest()
def save(n,x):(A/n).write_text(json.dumps(x,indent=2)+chr(10))
checks=[];cases=[];controls=[]
def ck(n,v):checks.append(dict(name=n,passed=bool(v)));assert v,n
B=H.parent/'debtor-conversion-worksheet-20261027/attempt-01'
lock=json.loads((B/'source-lock.json').read_text())
for p,h in lock.items():ck('baseline:'+p,sha(R/p)==h)
for p in [H/'reference.py',H/'fixtures.py',H/'verify.py',H/'contract.md',R/'docs/plans/accounting-creditor-conversion-worksheet-20261027.md',B/'verification.json',B/'cases.json',B/'source-lock.json',H.parent/'acquisition-prior-interest-20261027/source-inspection-02/aasb128-nov2024-jan2025.pdf']:
    lock[str(p.relative_to(R))]=sha(p)
save('source-lock.json',lock)
for n in ['reference.py','fixtures.py','verify.py','contract.md']:(A/n).write_bytes((H/n).read_bytes())
try:
    ck('cpu_hidden',os.environ.get('CUDA_VISIBLE_DEVICES')=='-1')
    ck('debtor_pass',json.loads((B/'verification.json').read_text())['status']=='PASS')
    for row in f.cases()+f.unresolved():
        out=candidate.report(row['request']);ck('complete:'+row['id'],out==row['expected']);cases.append(dict(**row,actual=out))
    outputs={r['id']:r['actual'] for r in cases}
    debtor={r['id']:r['actual'] for r in json.loads((B/'cases.json').read_text())}
    for current,other in [('allowance_then_exchange','gain'),('zero','zero'),('gain','loss')]:
        cr=outputs[current]['report'];dr=debtor[other]['report']
        ck('paired_profit:'+current,candidate.num(cr['income']['profit'])==-candidate.num(dr['income']['profit']))
        ck('paired_non_cash:'+current,cr['cash_flow']['net_change']==dr['cash_flow']['net_change']=='0/1')
        ck('paired_equity_value:'+current,cr['noncash_exchange']['shares_received']==dr['noncash_exchange']['equity_recognised'])
    a=outputs['allowance_then_exchange'];b=outputs['zero_allowance_loss']
    ck('same_total_not_same_components',a['report']['income']['profit']==b['report']['income']['profit'] and a['report']['income']['impairment_result']!=b['report']['income']['impairment_result'] and a['legal_journals']!=b['legal_journals'])
    def refuse(name,mutate,rebind=True,reason=None):
        r=f.request();mutate(r)
        if rebind:f.bind(r)
        o=candidate.report(r);ck('refusal:'+name,o['status']=='invalid')
        if reason:ck('reason:'+name,o['reason']==reason)
        ck('permissions:'+name,all(o.get(k) is False for k in candidate.FLAGS));controls.append(dict(id=name,request=r,actual=o))
    refuse('profile',lambda r:r.update(profile='other'),False,'profile')
    refuse('payload',lambda r:r.update(expected_payload_sha256='bad'),False,'payload_binding')
    refuse('scope_hash',lambda r:r['payload'].update(scope_result_sha256='bad'),True,'scope_result_binding')
    refuse('currency',lambda r:r['payload']['schedule'].update(currency='HKD'),True,'units')
    refuse('unit',lambda r:r['payload']['schedule'].update(unit='millions'),True,'units')
    refuse('actor',lambda r:r['payload']['source'].update(actor='other'),True,'source_context')
    refuse('subject',lambda r:r['payload']['source'].update(subject='S'),True,'source_context')
    refuse('assessment_order',lambda r:r['payload']['schedule'].update(assessment_at='2026-10-27T01:30:00Z'),True,'schedule_dates')
    refuse('close_order',lambda r:r['payload']['schedule'].update(close_at='2026-10-28T02:00:00Z'),True,'schedule_dates')
    refuse('allowance_above_gross',lambda r:r['payload']['schedule']['measurement'].update(assessed_allowance='101/1'),True,'allowance_exceeds_gross')
    refuse('negative_share_value',lambda r:r['payload']['schedule']['measurement'].update(share_fair_value='-1/1'),True,'nonnegative_share_fair_value')
    refuse('float_value',lambda r:r['payload']['schedule']['measurement'].update(share_fair_value=70.0),True,'exact_number')
    refuse('wrong_opening',lambda r:r['payload']['schedule']['opening'].update(capital='-100/1'),True,'selected_opening')
    refuse('missing_allowance',lambda r:r['payload']['schedule']['measurement'].pop('assessed_allowance'),True,'measurement_fields')
    refuse('issuer_fallback',lambda r:r['payload']['schedule']['measurement'].update(liability_fair_value='60/1'),True,'measurement_fields')
    refuse('missing_influence',lambda r:r['payload']['schedule']['premises'].pop('significant_influence'),True,'premises_fields')
    refuse('wrong_classification',lambda r:r['payload']['schedule']['premises'].update(loan_classification='fvtpl'),True,'premise_loan_classification')
    refuse('extra_cash',lambda r:r['payload']['schedule'].update(cash_paid='70/1'),True,'schedule_fields')
    def stale(r):
        r['payload']['schedule']['measurement']['assessed_allowance']='0/1';r['expected_payload_sha256']=f.digest(r['payload'])
    refuse('stale_schedule',stale,False,'schedule_source_binding')
    def stale_source(r):
        r['payload']['source']['text']='Changed';r['expected_payload_sha256']=f.digest(r['payload'])
    refuse('stale_source',stale_source,False,'evidence_binding')
    for p,h in lock.items():ck('protected:'+p,sha(R/p)==h)
    save('cases.json',cases);save('controls.json',controls);save('checks.json',checks)
    result=dict(status='PASS',cases=len(cases),measured_cases=5,unresolved_cases=len(cases)-5,refusal_controls=len(controls),assertions=len(checks),protected_files=len(lock),**candidate.FLAGS)
    save('verification.json',result);print(json.dumps(result))
except Exception as exc:
    save('failure.json',dict(error=str(exc),checks=checks,cases=cases,controls=controls));raise
finally:
    save('run-manifest.json',dict(command=sys.argv,git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),environment=platform.python_version(),
      cpu_gpu='CPU; GPU intentionally hidden',CUDA_VISIBLE_DEVICES=os.environ.get('CUDA_VISIBLE_DEVICES'),started_utc=started,wall_seconds=time.monotonic()-clock,
      seeds='N/A deterministic exact fractions',data_version='source-lock.json',plan='docs/plans/accounting-creditor-conversion-worksheet-20261027.md',
      result=str((H/'result.md').relative_to(R)),artifacts=str(A.relative_to(R))))
