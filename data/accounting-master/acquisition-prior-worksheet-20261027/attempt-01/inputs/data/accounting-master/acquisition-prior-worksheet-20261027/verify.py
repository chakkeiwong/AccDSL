from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from fractions import Fraction as F
from datetime import datetime,timezone
import os,sys,json,time,platform,subprocess,resource,traceback
import reference as m
import fixtures as f
H=Path(__file__).resolve().parent;R=H.parents[2]
def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' and os.environ.get('PYTHONDONTWRITEBYTECODE')=='1';resource.setrlimit(resource.RLIMIT_CPU,(110,110));out=H/sys.argv[1];out.mkdir(exist_ok=False);clock=time.monotonic();started=datetime.now(timezone.utc).isoformat();checks=[];cases=[];controls=[]
    files={R/p for p in json.loads((H/'predecessor-lock.json').read_text())};files.update(H/p for p in ['reference.py','fixtures.py','verify.py','prepare.py','contract.md','predecessor-lock.json']);files.add(R/'docs/plans/accounting-prior-interest-worksheet-20261027.md');lock={str(p.relative_to(R)):sha256(p.read_bytes()).hexdigest() for p in files}
    for p in files:q=out/'inputs'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
    def ck(n,a,b=True):
        checks.append(dict(name=n,passed=a==b))
        if a!=b:raise AssertionError(n+': '+repr(a)[:220]+' != '+repr(b)[:220])
    def run(c):
        n='carrying/'+str(c);b=f.fixture(c);before=deepcopy(b);r=m.report(b);ck(n+'/status',r['status'],'conditional_prior_worksheet');ck(n+'/immutable',b,before);ck(n+'/flags',[r[k] for k in m.FLAGS],[False]*len(m.FLAGS))
        for k,v in f.expected(c).items():ck(n+'/'+k,r[k],v)
        ck(n+'/scope_retained',r['scope_result'],f.SCOPE['result']);ck(n+'/schedule_retained',r['schedule'],b['payload']['schedule']);ck(n+'/source_retained',r['source'],b['payload']['source'])
        ids=[x['id'] for x in r['legal_journals']];ck(n+'/update_before_purchase',ids.index('prior-equity-update')<ids.index('new-share-purchase'))
        for e in ['P','S']:
            state={k:F(0) for k in r['original_books'][e]['snapshots']['closing']['balances']}
            for ev in r['legal_journals']:
                if ev['entity']!=e:continue
                ck(n+'/balanced/'+ev['id'],sum(F(x) for x in ev['entries'].values()),F(0))
                for k,v in ev['entries'].items():state[k]+=F(v)
                ck(n+'/cash_nonnegative/'+ev['id'],state['cash']>=0)
            ck(n+'/closing/'+e,f.ser(state),r['original_books'][e]['snapshots']['closing']['balances'])
        z=r['closing_worksheet']['balances'];profit=-sum(F(z.get(k,0)) for k in ['prior_remeasurement_gain','revenue','depreciation','operating_expense','tax_expense']);ck(n+'/account_profit',profit,F(r['report']['profit']))
        ck(n+'/account_assets',sum(F(z.get(k,0)) for k in ['cash','equipment','goodwill']),F(r['report']['assets_closing']))
        ck(n+'/nci_unchanged',r['report']['nci_profit'],'63/8');ck(n+'/goodwill_unchanged',r['report']['goodwill'],'135/4')
        ck(n+'/cash_roll',F(r['report']['cash']['opening'])+sum(F(x['amount']) for x in r['cash_origins']),F(r['report']['cash']['closing']))
        ck(n+'/noncash_update',all('cash' not in x['entries'] for x in r['legal_journals'] if x['id']=='prior-equity-update'))
        cases.append(dict(id=n,request=b,result=r))
    def unresolved(n,b,deps):
        f.bind(b);before=deepcopy(b);r=m.report(b);ck(n+'/status',r['status'],'method_required');ck(n+'/deps',r['dependencies'],deps);ck(n+'/retained',r['request'],b);ck(n+'/immutable',b,before);ck(n+'/no_report','report' not in r);cases.append(dict(id=n,request=b,result=r))
    def reject(n,b,reason,rehash=True):
        if rehash:f.bind(b)
        before=deepcopy(b);r=m.report(b);ck(n+'/status',r['status'],'invalid');ck(n+'/reason',r['reason'],reason);ck(n+'/immutable',b,before);ck(n+'/no_report','report' not in r);ck(n+'/flags',[r[k] for k in m.FLAGS],[False]*len(m.FLAGS));controls.append(dict(id=n,request=b,result=r))
    try:
        for c in [35,40,45]:run(c)
        for key,dep in [('tax','prior_gain_tax_method'),('separate_books','separate_books_method')]:b=f.fixture();b['payload']['schedule'][key]='unresolved';unresolved(key,b,[dep])
        b=f.fixture();b['payload']['schedule']['combined_measurement']={'status':'unresolved'};unresolved('measurement',b,['combined_investment_measurement'])
        for timevalue,dep in [(None,'measurement_source_availability_unknown'),('2027-01-01T00:00:00Z','measurement_source_after_cutoff')]:
            b=f.fixture();b['payload']['source']['available_at']=timevalue;b['payload']['schedule']['evidence_sha256']=f.digest(b['payload']['source']);unresolved(dep,b,[dep])
        b=f.fixture();b['payload']['schedule']['new_cash']='120/1';reject('stale_payload',b,'payload_binding',False)
        for key,reason in [('source_lock_sha256','source_lock_binding'),('base_result_sha256','base_result_binding'),('scope_result_sha256','scope_result_binding')]:b=f.fixture();b['payload'][key]='0'*64;reject(key,b,reason)
        for key,value,reason in [('prior_carrying','34/1','selected_amounts'),('new_cash','120/1','selected_amounts'),('prior_fair_value','35/1','selected_amounts'),('prior_fraction','1/4','ownership_schedule'),('new_fraction','3/4','ownership_schedule'),('at','2025-07-02T00:00:00Z','schedule_dates'),('currency','HKD','schedule_units'),('tax','assume_zero','tax_disposition'),('separate_books','cost','separate_book_method'),('evidence_sha256','0'*64,'schedule_source_binding')]:
            b=f.fixture();b['payload']['schedule'][key]=value;reject(key,b,reason)
        b=f.fixture();b['payload']['schedule']['combined_measurement']['closing']='125/1';reject('changed_measurement',b,'combined_measurement_values')
        b=f.fixture();b['payload']['source']['actor']='analyst';b['payload']['schedule']['evidence_sha256']=f.digest(b['payload']['source']);reject('wrong_actor',b,'source_context')
        b=f.fixture();s=b['payload']['books']['P']['snapshots']['closing']['balances'];s['investment']='115/1';s['prior_remeasurement_gain']='0/1';reject('balanced_missing_remeasurement',b,'complete_legal_books')
        b=f.fixture();s=b['payload']['books']['P']['snapshots']['closing']['balances'];s['cash']='180/1';s['capital']='-295/1';reject('invented_cash',b,'complete_legal_books')
        b=f.fixture();b['payload']['scope_request']['payload']['relationship']['significant_influence']='yes';reject('wrong_relationship',b,'selected_scope_request')
        b=f.fixture();b['payload']['base_request']['payload']['consideration']['cash']='80/1';reject('mutated_comparator',b,'selected_base_request')
        b=f.fixture();b['payload']['books_sha256']='0'*64;b['expected_payload_sha256']=f.digest(b['payload']);reject('book_binding',b,'books_binding',False)
        for p,d in lock.items():ck('protected/'+p,sha256((R/p).read_bytes()).hexdigest(),d)
        result=dict(status='PASS',cases=len(cases),refusal_controls=len(controls),assertions=len(checks),protected_files=len(lock),source_admission=False,accounting_admission=False,posting_authorized=False,report_authorized=False)
    except Exception:result=dict(status='FAIL',cases=len(cases),refusal_controls=len(controls),assertions=len(checks),error=traceback.format_exc())
    for n,v in [('verification.json',result),('cases.json',cases),('controls.json',controls),('checks.json',checks),('source-lock.json',lock)]: (out/n).write_text(json.dumps(v,indent=2)+'\n')
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 '+str(Path(__file__).relative_to(R))+' '+sys.argv[1],environment=platform.python_version(),cpu_gpu='CPU;GPU intentionally hidden',random_seeds='N/A deterministic',started_utc=started,wall_seconds=time.monotonic()-clock,data_version='source-lock.json',plan='docs/plans/accounting-prior-interest-worksheet-20261027.md',result=str((H/'result.md').relative_to(R)),output=str(out.relative_to(R)))
    (out/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(result))
    if result['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
