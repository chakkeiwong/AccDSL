from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from datetime import datetime,timezone
import os,sys,json,time,platform,subprocess,resource,traceback,fitz
import reference as m
import fixtures as f
H=Path(__file__).resolve().parent;R=H.parents[2]
def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' and os.environ.get('PYTHONDONTWRITEBYTECODE')=='1'
    resource.setrlimit(resource.RLIMIT_CPU,(110,110));out=H/sys.argv[1];out.mkdir(exist_ok=False);clock=time.monotonic();started=datetime.now(timezone.utc).isoformat();checks=[];cases=[];controls=[]
    files={R/p for p in json.loads((H/'predecessor-lock.json').read_text())};files.update(H/p for p in ['reference.py','fixtures.py','verify.py','prepare.py','contract.md','predecessor-lock.json']);files.add(R/'docs/plans/accounting-prior-interest-acquisition-20261027.md')
    lock={str(p.relative_to(R)):sha256(p.read_bytes()).hexdigest() for p in files}
    for p in files:q=out/'inputs'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
    def ck(n,a,b=True):
        checks.append(dict(name=n,passed=a==b))
        if a!=b:raise AssertionError(n+': '+repr(a)[:240]+' != '+repr(b)[:240])
    def common(n,b,r):
        ck(n+'/flags',[r[k] for k in m.FLAGS],[False]*len(m.FLAGS));ck(n+'/no_report','report' not in r);ck(n+'/no_postings','legal_journals' not in r)
    def run(id,cls,tr):
        n=id+'/'+cls+'/'+tr;b=f.fixture(id,cls,tr);before=deepcopy(b);r=m.derive(b);ex,deps=f.expected(id,cls,tr)
        ck(n+'/status',r['status'],'conditional_prior_expressions');ck(n+'/immutable',b,before);common(n,b,r)
        ck(n+'/expressions',r['expressions'],ex);ck(n+'/dependencies',r['dependencies'],deps);ck(n+'/base',r['base_result'],f.prior(id)['result'])
        ck(n+'/prior',r['prior'],b['payload']['prior']);ck(n+'/descriptors',r['descriptors'],{k:b['payload'][k] for k in ['carrying','cumulative_oci']});ck(n+'/source',r['source'],b['payload']['source']);ck(n+'/request_identity',r['request_sha256'],f.digest(b))
        ck(n+'/no_duplicate_prior_fv',r['expressions']['acquisition_excess']['coefficients']['P'],'1/1')
        cases.append(dict(id=n,request=b,result=r))
    def unresolved(n,b,expected):
        f.bind(b);before=deepcopy(b);r=m.derive(b);ck(n+'/status',r['status'],'unresolved');ck(n+'/dependencies',r['dependencies'],sorted(set(expected)));ck(n+'/expressions',r['expressions'],{});ck(n+'/immutable',b,before);common(n,b,r)
        ck(n+'/prior_retained',r['prior'],b['payload']['prior']);cases.append(dict(id=n,request=b,result=r))
    def reject(n,b,reason,rehash=True):
        if rehash:f.bind(b)
        before=deepcopy(b);r=m.derive(b);ck(n+'/status',r['status'],'invalid');ck(n+'/reason',r['reason'],reason);ck(n+'/immutable',b,before);common(n,b,r);controls.append(dict(id=n,request=b,result=r))
    try:
        for path,page,text in [('conversion-control-scope-20261026/source-attempt-02/aasb3-2026.pdf',13,'profit or loss or other comprehensive income'),('conversion-control-scope-20261026/source-attempt-02/aasb3-2026.pdf',30,'pre-existing relationship'),('conversion-control-scope-20261026/source-attempt-02/aasb127-2022.pdf',6,'using the equity method'),('contingent-conversion-authority-20261026/source-attempt-02/aasb9-2026.pdf',89,'shall not be subsequently transferred to profit or loss')]:
            ck('source/'+path+'/'+str(page),text in ' '.join(fitz.open(H.parent/path)[page-1].get_text().split()))
        for id in ['proportional/equity','fair_value/equity','none/equity']:
            for cls,tr in [('fvtpl','none'),('equity_fvoci','retain_reserve'),('equity_fvoci','transfer_within_equity')]:run(id,cls,tr)
        for id in ['prior/debt','prior/unresolved']:
            old=f.prior(id);kind=old['request']['payload']['prior_interest']['kind'];unresolved(id,f.fixture(id),['prior_interest_and_separate_transaction_analysis:'+kind]+['base:'+x for x in old['result']['dependencies']])
        for cls in ['equity_method','unresolved']:
            b=f.fixture();b['payload']['prior']['classification']=cls;unresolved(cls,b,['prior_classification_method:'+cls])
        for field,dep in [('hedging','hedging_method'),('separate_transactions','separate_transaction_analysis')]:
            b=f.fixture();b['payload']['prior'][field]='requires_method';unresolved(field,b,[dep])
        for field in ['equity_eligible','irrevocable_election']:
            b=f.fixture(classification='equity_fvoci',treatment='retain_reserve');b['payload']['prior'][field]=None;unresolved(field,b,['fvoci_eligibility_or_election'])
        for value,dep in [(None,'source_availability_unknown'),('2027-01-01T00:00:00Z','source_after_cutoff')]:
            b=f.fixture();b['payload']['source']['available_at']=value;f.resupport(b);unresolved(dep,b,[dep])
        b=f.fixture();b['payload']['prior']['fraction']='1/4';reject('stale_payload',b,'payload_binding',False)
        for field,reason in [('base_result_sha256','base_result_binding'),('source_lock_sha256','source_lock_binding')]:b=f.fixture();b['payload'][field]='0'*64;reject(field,b,reason)
        for field,value,reason in [('kind','debt','prior_kind_binding'),('fraction','3/4','prior_fraction'),('fraction','0/1','prior_fraction'),('classification','debt_fvoci','classification'),('separate_books','cost','separate_books_not_derived'),('equity_eligible','yes','boolean_or_unknown'),('evidence_sha256','0'*64,'prior_source_binding')]:
            b=f.fixture();b['payload']['prior'][field]=value;reject('prior/'+field+'/'+str(value),b,reason)
        b=f.fixture();b['payload']['cumulative_oci']['zero_stipulated']=False;reject('fvtpl_prior_oci',b,'fvtpl_oci_must_be_zero')
        b=f.fixture(classification='equity_fvoci',treatment='retain_reserve');b['payload']['prior']['oci_treatment']='recycle_to_profit';reject('equity_fvoci_recycling',b,'equity_fvoci_no_recycling')
        for field,value,reason in [('symbol','P','duplicate_symbol'),('kind','prior_equity_fair_value','descriptor_kind:carrying'),('currency','HKD','descriptor_units:carrying'),('at','2025-07-02T00:00:00Z','descriptor_date:carrying'),('evidence_sha256','0'*64,'descriptor_source:carrying')]:
            b=f.fixture();b['payload']['carrying'][field]=value;reject('carrying/'+field,b,reason)
        b=f.fixture();b['payload']['source']['actor']='analyst';f.resupport(b);reject('wrong_actor',b,'source_context')
        b=f.fixture();b['payload']['prior']['extra']=True;reject('open_schema',b,'prior_fields')
        for p,d in lock.items():ck('protected/'+p,sha256((R/p).read_bytes()).hexdigest(),d)
        result=dict(status='PASS',cases=len(cases),refusal_controls=len(controls),assertions=len(checks),protected_files=len(lock),source_admission=False,accounting_admission=False,posting_authorized=False,report_authorized=False)
    except Exception:result=dict(status='FAIL',cases=len(cases),refusal_controls=len(controls),assertions=len(checks),error=traceback.format_exc())
    for n,v in [('verification.json',result),('cases.json',cases),('controls.json',controls),('checks.json',checks),('source-lock.json',lock)]: (out/n).write_text(json.dumps(v,indent=2)+'\n')
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 '+str(Path(__file__).relative_to(R))+' '+sys.argv[1],environment=platform.python_version(),cpu_gpu='CPU;GPU intentionally hidden',random_seeds='N/A deterministic',started_utc=started,wall_seconds=time.monotonic()-clock,data_version='source-lock.json',plan='docs/plans/accounting-prior-interest-acquisition-20261027.md',result=str((H/'result.md').relative_to(R)),output=str(out.relative_to(R)))
    (out/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(result))
    if result['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
