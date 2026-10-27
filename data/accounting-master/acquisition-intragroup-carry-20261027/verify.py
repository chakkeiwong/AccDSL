"""Exact complete two-year carry comparisons with immutable failure records."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as F
import json,os,sys,time,platform,subprocess,resource,traceback
import reference as m
import fixtures as f
H=Path(__file__).resolve().parent;R=H.parents[2]
def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' and os.environ.get('PYTHONDONTWRITEBYTECODE')=='1'
    resource.setrlimit(resource.RLIMIT_CPU,(110,110));out=H/sys.argv[1];out.mkdir(exist_ok=False)
    clock=time.monotonic();started=datetime.now(timezone.utc).isoformat();checks=[];cases=[];controls=[]
    files={R/p for p in json.loads((H/'predecessor-lock.json').read_text())}
    files.update(H/p for p in ['prepare.py','reference.py','fixtures.py','verify.py','contract.md','predecessor-lock.json']);files.add(R/'docs/plans/accounting-intragroup-carry-20261027.md')
    lock={str(p.relative_to(R)):sha256(p.read_bytes()).hexdigest() for p in files}
    for p in files:q=out/'inputs'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
    def ck(n,a,b=True):
        checks.append(dict(name=n,passed=a==b))
        if a!=b:raise AssertionError(n+': '+repr(a)[:220]+' != '+repr(b)[:220])
    def run(earlier,settled,fraction,tax='known'):
        name='/'.join([earlier,'settled' if settled else 'credit',fraction,tax]);b=f.fixture(earlier,settled,fraction,tax);before=deepcopy(b);r=m.report(b)
        ck(name+'/status',r['status'],'tax_method_required' if tax=='unresolved' else 'conditional_carry_worksheet')
        ck(name+'/immutable',b,before);ck(name+'/flags',[r[k] for k in m.FLAGS],[False]*len(m.FLAGS))
        if tax=='unresolved':
            ck(name+'/no_report','report' not in r);ck(name+'/prior_retained',r['prior_result'],f.prior(earlier,settled)['result']);ck(name+'/request_retained',r['request'],b)
        else:
            for key,value in f.expected(earlier,settled,fraction).items():ck(name+'/'+key,r[key],value)
            ck(name+'/request_identity',r['request_sha256'],f.digest(b));ck(name+'/prior_identity',r['prior_result_sha256'],b['payload']['prior_result_sha256'])
            # Full journal replay from the closed legal opening.
            replay={k:F(v) for k,v in r['opening_legal'].items()}
            for entry in r['legal_journals']:
                ck(name+'/legal_balance/'+entry['id'],sum(F(v) for v in entry['entries'].values()),F(0))
                for k,v in entry['entries'].items():replay[k]+=F(v)
            ck(name+'/legal_replay',{k:f.frac(v) for k,v in replay.items()},r['closing_legal'])
            for entry in r['group_journals']:
                ck(name+'/group_balance/'+entry['id'],sum(F(v) for v in entry['entries'].values()),F(0))
                for k,v in entry['entries'].items():replay[k]=replay.get(k,F(0))+F(v)
            ck(name+'/group_replay',{k:f.frac(v) for k,v in replay.items()},r['closing_adjusted'])
            ck(name+'/no_reacquisition',not any(x['id']=='acquisition' for x in r['group_journals']))
            if (earlier,settled,fraction)==('0/1',False,'1/1'):
                for key,val in dict(profit='-2/1',owners_profit='3/8',nci_profit='-19/8',cash='310/1',assets='1627/4',liabilities='57/2',equity='1513/4').items():ck(name+'/absolute/'+key,r['report'][key],val)
        cases.append(dict(id=name,request=b,result=r))
    def reject(name,b,reason,rehash=True):
        if rehash:f.bind(b)
        before=deepcopy(b);r=m.report(b);ck(name+'/status',r['status'],'invalid');ck(name+'/reason',r['reason'],reason);ck(name+'/immutable',b,before);ck(name+'/no_report','report' not in r);ck(name+'/flags',[r[k] for k in m.FLAGS],[False]*len(m.FLAGS));controls.append(dict(id=name,request=b,result=r))
    try:
        run('0/1',False,'0/1')
        for earlier in ['0/1','1/2']:
            for settled in [False,True]:
                for fraction in ['0/1','1/2','1/1']:
                    if (earlier,settled,fraction)!=('0/1',False,'0/1'):run(earlier,settled,fraction)
        run('0/1',False,'1/1','unresolved');run('1/2',True,'1/2','unresolved')
        b=f.fixture();b['payload']['sale']['receipts']='39/1';reject('stale_envelope',b,'payload_binding',False)
        for key,reason in [('prior_result_sha256','prior_binding'),('source_lock_sha256','source_lock_binding')]:b=f.fixture();b['payload'][key]='0'*64;reject(key,b,reason)
        b=f.fixture();b['payload']['ownership']='50_percent';reject('changed_ownership',b,'ownership_continuity')
        b=f.fixture();b['payload']['period']['start']='2025-01-01T00:00:00Z';reject('replayed_year',b,'period')
        for key,value in [('legal_depreciation','0/1'),('additional_depreciation','0/1'),('tax_release','0/1'),('premise','automatic_annualisation')]:
            b=f.fixture();b['payload']['equipment'][key]=value;reject('equipment/'+key,b,'equipment_schedule_required')
        for key,value,reason in [('id','acquisition','sale_identity_date'),('at','2025-06-01T00:00:00Z','sale_identity_date'),('currency','HKD','sale_units'),('unit','thousands','sale_units'),('fraction_of_remaining','3/2','selected_sale_fraction'),('fraction_of_remaining','-1/2','selected_sale_fraction'),('receipts','41/1','sale_amounts'),('legal_cost','20/1','sale_amounts'),('recognition','cash_only','revenue_premise')]:
            b=f.fixture();b['payload']['sale'][key]=value;reject('sale/'+key+'/'+value,b,reason)
        b=f.fixture();b['payload']['tax_continuation']='assume_zero';reject('implicit_zero_tax',b,'tax_continuation')
        b=f.fixture();b['payload']['opening_legal']['P.retained_post']='0/1';reject('unclosed_parent_profit',b,'complete_opening_carry')
        b=f.fixture();b['payload']['opening_group']['group.nci']='-115/4';reject('opening_nci_reset',b,'complete_opening_carry')
        b=f.fixture();b['payload']['opening_group']['group.inventory_deferred_tax_asset']='0/1';reject('forgotten_dta',b,'complete_opening_carry')
        b=f.fixture();b['payload']['opening_group']['S.equipment']='90/1';reject('replayed_acquired_basis',b,'complete_opening_carry')
        b=f.fixture();b['payload']['opening_group']['P.investment']='120/1';reject('reacquisition',b,'complete_opening_carry')
        b=f.fixture();b['payload']['opening_group']['P.retained_post']='-1/1';b['payload']['opening_group']['S.retained_post']='-181/8';reject('balanced_wrong_attribution',b,'complete_opening_carry')
        b=f.fixture();b['payload']['opening_sha256']='0'*64;b['expected_payload_sha256']=f.digest(b['payload']);reject('opening_hash',b,'opening_binding',False)
        b=f.fixture();b['payload']['sale']['extra']=True;reject('open_sale_schema',b,'sale_fields')
        for p,d in lock.items():ck('protected/'+p,sha256((R/p).read_bytes()).hexdigest(),d)
        result=dict(status='PASS',cases=len(cases),refusal_controls=len(controls),assertions=len(checks),protected_files=len(lock),source_admission=False,accounting_admission=False,posting_authorized=False,report_authorized=False)
    except Exception:result=dict(status='FAIL',cases=len(cases),refusal_controls=len(controls),assertions=len(checks),error=traceback.format_exc())
    for name,value in [('verification.json',result),('cases.json',cases),('controls.json',controls),('checks.json',checks),('source-lock.json',lock)]:
        (out/name).write_text(json.dumps(value,indent=2)+'\n')
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 '+str(Path(__file__).relative_to(R))+' '+sys.argv[1],environment=platform.python_version(),cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',started_utc=started,wall_seconds=time.monotonic()-clock,data_version='source-lock.json',plan='docs/plans/accounting-intragroup-carry-20261027.md',result=str((H/'result.md').relative_to(R)),output=str(out.relative_to(R)))
    (out/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(result))
    if result['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
