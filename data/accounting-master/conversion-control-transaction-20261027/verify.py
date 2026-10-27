from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
from itertools import permutations
from copy import deepcopy
import json,os,platform,subprocess,sys,time
import reference as candidate
import fixtures as f
H=Path(__file__).resolve().parent;R=H.parents[2];A=H/('attempt-'+sys.argv[1]);A.mkdir(exist_ok=False)
clock=time.monotonic();started=datetime.now(timezone.utc).isoformat()
def sha(p):return sha256(p.read_bytes()).hexdigest()
def save(n,x):(A/n).write_text(json.dumps(x,indent=2)+chr(10))
checks=[];cases=[];controls=[]
def ck(n,v):checks.append(dict(name=n,passed=bool(v)));assert v,n
B=H.parent/'creditor-conversion-worksheet-20261027/attempt-01';lock=json.loads((B/'source-lock.json').read_text())
for p,h in lock.items():ck('baseline:'+p,sha(R/p)==h)
for p in [H/'reference.py',H/'fixtures.py',H/'verify.py',H/'contract.md',H/'source-review.md',R/'docs/plans/accounting-conversion-control-transaction-20261027.md',B/'verification.json',B/'cases.json',B/'source-lock.json']+list((H/'source-attempt-01').iterdir()):lock[str(p.relative_to(R))]=sha(p)
save('source-lock.json',lock)
for n in ['reference.py','fixtures.py','verify.py','contract.md','source-review.md']:(A/n).write_bytes((H/n).read_bytes())
try:
    ck('cpu_hidden',os.environ.get('CUDA_VISIBLE_DEVICES')=='-1');ck('creditor_pass',json.loads((B/'verification.json').read_text())['status']=='PASS')
    for row in f.cases():
        out=candidate.derive(row['request']);ck('complete:'+row['id'],out==row['expected']);cases.append(dict(**row,actual=out))
    original=f.request()
    for i,order in enumerate(permutations(range(4))):
        r=deepcopy(original);d=r['payload']['declaration'];d['components']=[d['components'][j] for j in order];d['inventory']=list(reversed(d['inventory']));f.bind(r)
        ex=f.expected(r,f.TOTALS,'108/1');out=candidate.derive(r);ck('permutation:'+str(i),ex==out);cases.append(dict(id='permutation_'+str(i),request=r,expected=ex,actual=out))
    def refuse(name,mutation,rebind=True,reason=None):
        r=f.request();mutation(r)
        if rebind:f.bind(r)
        out=candidate.derive(r);ck('refusal:'+name,out['status']=='invalid')
        if reason:ck('reason:'+name,out['reason']==reason)
        ck('permissions:'+name,all(out.get(k) is False for k in candidate.FLAGS));controls.append(dict(id=name,request=r,actual=out))
    refuse('profile',lambda r:r.update(profile='other'),False,'profile')
    refuse('payload_hash',lambda r:r.update(expected_payload_sha256='bad'),False,'payload_binding')
    refuse('duplicate_inventory',lambda r:r['payload']['declaration']['inventory'].append('old_debt'),True,'duplicate_inventory')
    refuse('missing_component',lambda r:r['payload']['declaration']['components'].pop(),True,'component_count')
    refuse('duplicate_component',lambda r:r['payload']['declaration']['components'].__setitem__(0,deepcopy(r['payload']['declaration']['components'][1])),True,'complete_unique_components')
    refuse('undeclared_component',lambda r:r['payload']['declaration']['components'][0].update(id='unknown'),True,'undeclared_component')
    refuse('debt_as_consideration',lambda r:r['payload']['declaration']['components'][1].update(role='acquisition_consideration'),True,'kind_role_mismatch')
    refuse('debt_as_prior_equity',lambda r:r['payload']['declaration']['components'][1].update(role='prior_equity'),True,'component_role')
    refuse('prior_equity_kind',lambda r:r['payload']['declaration']['components'][1].update(kind='prior_equity'),True,'component_kind')
    refuse('fee_as_consideration',lambda r:r['payload']['declaration']['components'][2].update(role='acquisition_consideration'),True,'kind_role_mismatch')
    refuse('negative_amount',lambda r:r['payload']['declaration']['components'][0].update(amount='-1/1'),True,'canonical_nonnegative_amount')
    refuse('float_amount',lambda r:r['payload']['declaration']['components'][0].update(amount=80.0),True,'canonical_nonnegative_amount')
    refuse('noncanonical',lambda r:r['payload']['declaration']['components'][0].update(amount='160/2'),True,'canonical_nonnegative_amount')
    refuse('unit',lambda r:r['payload']['declaration'].update(unit='millions'),True,'unit')
    refuse('source_actor',lambda r:r['payload']['source'].update(actor='other'),True,'source_context')
    refuse('source_date',lambda r:r['payload']['source'].update(at='2026-10-26T01:00:00Z'),True,'source_date')
    refuse('future_event',lambda r:r['payload']['declaration']['context'].update(cutoff='2026-10-26T01:00:00Z'),True,'date_order')
    refuse('automatic_coverage',lambda r:r['payload']['declaration'].update(inventory_coverage='verified'),True,'assertion_inventory_coverage')
    refuse('extra_goodwill',lambda r:r['payload'].update(goodwill='100/1'),True,'payload_fields')
    def stale(r):
        r['payload']['declaration']['components'][1]['amount']='30/1';r['expected_payload_sha256']=f.digest(r['payload'])
    refuse('stale_declaration',stale,False,'declaration_source_binding')
    def huge(r):
        d=r['payload']['declaration'];d['inventory']=['item_'+str(i) for i in range(17)]
    refuse('resource_bound',huge,True,'inventory_bound')
    for p,h in lock.items():ck('protected:'+p,sha(R/p)==h)
    save('cases.json',cases);save('controls.json',controls);save('checks.json',checks)
    result=dict(status='PASS',cases=len(cases),base_cases=9,permutations=24,refusal_controls=len(controls),assertions=len(checks),protected_files=len(lock),**candidate.FLAGS)
    save('verification.json',result);print(json.dumps(result))
except Exception as exc:
    save('failure.json',dict(error=str(exc),checks=checks,cases=cases,controls=controls));raise
finally:
    save('run-manifest.json',dict(command=sys.argv,git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),environment=platform.python_version(),cpu_gpu='CPU; GPU intentionally hidden',
      CUDA_VISIBLE_DEVICES=os.environ.get('CUDA_VISIBLE_DEVICES'),started_utc=started,wall_seconds=time.monotonic()-clock,seeds='N/A deterministic exact partition',data_version='source-lock.json',
      plan='docs/plans/accounting-conversion-control-transaction-20261027.md',result=str((H/'result.md').relative_to(R)),artifacts=str(A.relative_to(R))))
