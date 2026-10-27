"""Complete-output exact comparisons and malformed-request controls."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as F
import json,os,sys,time,platform,subprocess,resource,traceback,fitz
import reference as m
import fixtures as f
H=Path(__file__).resolve().parent;R=H.parents[2]
def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' and os.environ.get('PYTHONDONTWRITEBYTECODE')=='1'
    resource.setrlimit(resource.RLIMIT_CPU,(110,110));out=H/sys.argv[1];out.mkdir(exist_ok=False)
    started=datetime.now(timezone.utc).isoformat();clock=time.monotonic();checks=[];cases=[];controls=[]
    files={R/p for p in json.loads((H/'predecessor-lock.json').read_text())}
    files.update(H/p for p in ['reference.py','fixtures.py','verify.py','prepare.py','contract.md','predecessor-lock.json'])
    files.add(R/'docs/plans/accounting-intragroup-realisation-20261027.md')
    lock={str(p.relative_to(R)):sha256(p.read_bytes()).hexdigest() for p in files}
    for p in files:
        q=out/'inputs'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
    def ck(name,actual,expected=True):
        checks.append(dict(name=name,passed=actual==expected))
        if actual!=expected:raise AssertionError(name+': '+repr(actual)[:220]+' != '+repr(expected)[:220])
    def run(election,mix,settled,tax,sold):
        name='/'.join([election,mix,'settled' if settled else 'credit',tax,sold]);b=f.fixture(election,mix,settled,tax,sold);before=deepcopy(b)
        r=m.report(b);ck(name+'/status',r['status'],'tax_method_required' if tax=='unresolved' else 'conditional_realisation_worksheet')
        ck(name+'/immutable',b,before);ck(name+'/flags',[r[k] for k in m.FLAGS],[False]*len(m.FLAGS))
        for key,value in f.expected(election,mix,settled,tax,sold).items():ck(name+'/'+key,r[key],value)
        ck(name+'/request_identity',r['request_sha256'],f.digest(b))
        ck(name+'/predecessor_identity',r['predecessor_result_sha256'],b['payload']['predecessor_result_sha256'])
        ck(name+'/unique_journals',len({x['id'] for x in r['legal_journals']}),len(r['legal_journals']))
        # Independent complete trace accumulation and chronological cash checks.
        for entity in ['P','S']:
            state={key:F(0) for key in r['original_books'][entity]['snapshots']['closing']['balances']}
            for entry in r['legal_journals']:
                if entry['entity']!=entity:continue
                ck(name+'/balanced/'+entry['id'],sum(F(x) for x in entry['entries'].values()),F(0))
                for key,value in entry['entries'].items():state[key]+=F(value)
                ck(name+'/nonnegative_cash/'+entry['id'],state['cash']>=0)
            ck(name+'/replayed_closing/'+entity,{k:f.frac(v) for k,v in state.items()},r['original_books'][entity]['snapshots']['closing']['balances'])
        if tax=='unresolved':ck(name+'/no_report','report' not in r)
        if (election,mix,settled,tax,sold)==('proportional','cash',False,'recognised','1/2'):
            expected=dict(profit='39/1',owners_profit='483/16',nci_profit='141/16',assets_closing='416/1',liabilities_closing='113/4',equity_closing='1551/4',owners_equity_closing='5603/16',nci_closing='601/16')
            for key,value in expected.items():ck(name+'/absolute/'+key,r['report'][key],value)
        cases.append(dict(id=name,request=b,result=r));return r
    def reject(name,b,reason,rehash=True):
        if rehash:f.bind(b)
        before=deepcopy(b);r=m.report(b);ck(name+'/status',r['status'],'invalid');ck(name+'/reason',r['reason'],reason)
        ck(name+'/immutable',b,before);ck(name+'/no_report','report' not in r);ck(name+'/flags',[r[k] for k in m.FLAGS],[False]*len(m.FLAGS))
        controls.append(dict(id=name,request=b,result=r))
    try:
        for path,page,anchor in [('aasb102-compiled-dec2021.pdf',9,'When inventories are sold'),('aasb15-compiled-dec2022.pdf',12,'customer obtains control'),('aasb15-compiled-dec2022.pdf',13,'physical possession may not coincide'),('aasb15-compiled-dec2022.pdf',14,'amounts collected on behalf of third parties')]:
            text=' '.join(fitz.open(H/'source-inspection-01'/path)[page-1].get_text().split());ck('source/'+path+'/'+str(page),anchor in text)
        run('proportional','cash',False,'recognised','1/2')
        for election in ['proportional','fair_value','none']:
            for mix in ['cash','equity','mixed']:
                for settled in [False,True]:
                    for sold in ['0/1','1/2','1/1']:
                        if (election,mix,settled,sold)!=('proportional','cash',False,'1/2'):run(election,mix,settled,'recognised',sold)
        for tax in ['unrecognised','unresolved']:
            for settled in [False,True]:
                for sold in ['0/1','1/2','1/1']:run('proportional','cash',settled,tax,sold)
        b=f.fixture();b['payload']['external_sale']['receipts']='21/1';reject('stale_envelope',b,'payload_binding',False)
        for key,reason in [('predecessor_result_sha256','predecessor_binding'),('source_lock_sha256','source_lock_binding')]:
            b=f.fixture();b['payload'][key]='0'*64;reject(key,b,reason)
        for field,value,reason in [('customer','P','external_parties'),('seller','P','external_parties'),('id','inventory-P-S-1','external_parties'),('at','2025-09-01T00:00:00Z','external_date'),('at','2026-01-01T00:00:00Z','external_date'),('at','2025-12-31T12:00:00Z','selected_external_calendar'),('currency','HKD','external_units'),('unit','thousands','external_units'),('fraction','-1/2','selected_resale_fraction'),('fraction','3/2','selected_resale_fraction'),('fraction','1/3','selected_resale_fraction'),('receipts','19/1','external_amounts'),('cost','10/1','external_amounts'),('recognition','cash_received','revenue_premise')]:
            b=f.fixture();b['payload']['external_sale'][field]=value;reject('external/'+field+'/'+value,b,reason)
        b=f.fixture();b['payload']['event_calendar']['precontrol_close']='2025-08-01T00:00:00Z';reject('precontrol_history',b,'selected_event_calendar')
        b=f.fixture();b['payload']['history_premise']='inferred from balances';reject('invented_history',b,'history_premise')
        b=f.fixture();s=b['payload']['books']['S']['snapshots']['closing']['balances'];s['cash']='111/1';s['merchandise_revenue']='-21/1';reject('balanced_wrong_sale',b,'complete_legal_books')
        b=f.fixture();b['payload']['books']['S']['snapshots']['closing']['balances']['inventory']='30/1';reject('missing_inventory_cost',b,'complete_legal_books')
        b=f.fixture();b['payload']['books']['S']['snapshots']['closing']['balances']['current_tax_payable']='0/1';reject('missing_external_tax',b,'complete_legal_books')
        b=f.fixture();b['payload']['external_sale']['extra']=True;reject('open_schema',b,'external_sale_fields')
        b=f.fixture();b['payload']['books_sha256']='0'*64;b['expected_payload_sha256']=f.digest(b['payload']);reject('books_identity',b,'books_binding',False)
        for p,d in lock.items():ck('protected/'+p,sha256((R/p).read_bytes()).hexdigest(),d)
        result=dict(status='PASS',cases=len(cases),refusal_controls=len(controls),assertions=len(checks),protected_files=len(lock),source_admission=False,accounting_admission=False,posting_authorized=False,report_authorized=False)
    except Exception:result=dict(status='FAIL',cases=len(cases),refusal_controls=len(controls),assertions=len(checks),error=traceback.format_exc())
    for name,value in [('verification.json',result),('cases.json',cases),('controls.json',controls),('checks.json',checks),('source-lock.json',lock)]:
        (out/name).write_text(json.dumps(value,indent=2)+'\n')
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 '+str(Path(__file__).relative_to(R))+' '+sys.argv[1],environment=platform.python_version(),cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',started_utc=started,wall_seconds=time.monotonic()-clock,data_version='source-lock.json',plan='docs/plans/accounting-intragroup-realisation-20261027.md',result=str((H/'result.md').relative_to(R)),output=str(out.relative_to(R)))
    (out/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(result))
    if result['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
