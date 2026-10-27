"""Independent cash/equity expected amounts and complete predecessor replay."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from datetime import datetime,timezone
from fractions import Fraction
import json,sys,os,time,platform,subprocess,resource,traceback
import reference as m
H=Path(__file__).resolve().parent;R=H.parents[2];S=H.parent/'acquisition-worksheet-20261027'
SAVED=json.loads((S/'attempt-01/cases.json').read_text())
EXPECTED=json.loads((S/'expectations.json').read_text())
def f(x):q=Fraction(x);return str(q.numerator)+'/'+str(q.denominator)
def bind(b):
    b['payload']['expected_books_sha256']=m.h.digest(b['payload']['books']);b['expected_payload_sha256']=m.h.digest(b['payload']);return b
def fixture(election='proportional',mix='cash',saved=None):
    previous=saved or next(r for r in SAVED if r['id']==election)
    b=deepcopy(previous['request']);b['profile']=m.PROFILE;p=b['payload']
    ca,eq={'cash':('120/1','0/1'),'equity':('0/1','120/1'),'mixed':('50/1','70/1')}[mix]
    p['consideration']=dict(cash=ca,new_parent_equity=eq,kind='cash_and_new_parent_equity',at='2025-07-01T00:00:00Z',currency='USD',unit='currency_unit',premise='Stipulated synthetic component values; no fair-value or debt-conversion claim')
    for stage in ['acquisition','closing']:p['books']['P']['snapshots'][stage]['balances']=dict(cash={'cash':'180/1','equity':'300/1','mixed':'250/1'}[mix],investment='120/1',capital={'cash':'-300/1','equity':'-420/1','mixed':'-370/1'}[mix])
    return bind(b)
def expected(election,mix):
    e=deepcopy(EXPECTED[election])
    # Hand-authored absolute report results; no candidate arithmetic is reused.
    for stage in ['acquisition_balances','closing_balances']:
        e[stage]['cash']=({'cash':'230/1','equity':'350/1','mixed':'300/1'} if stage=='acquisition_balances' else {'cash':'270/1','equity':'390/1','mixed':'340/1'})[mix]
        e[stage]['parent_capital']={'cash':'-300/1','equity':'-420/1','mixed':'-370/1'}[mix]
    e['owners_equity_closing']={
        'proportional':{'cash':'2589/8','equity':'3549/8','mixed':'3149/8'},
        'fair_value':{'cash':'2589/8','equity':'3549/8','mixed':'3149/8'},
        'none':{'cash':'663/2','equity':'903/2','mixed':'803/2'}}[election][mix]
    e['assets_closing']={
        'proportional':{'cash':'1539/4','equity':'2019/4','mixed':'1819/4'},
        'fair_value':{'cash':'396/1','equity':'516/1','mixed':'466/1'},
        'none':{'cash':'356/1','equity':'476/1','mixed':'426/1'}}[election][mix]
    e['equity_closing']={
        'proportional':{'cash':'1441/4','equity':'1921/4','mixed':'1721/4'},
        'fair_value':{'cash':'743/2','equity':'983/2','mixed':'883/2'},
        'none':{'cash':'663/2','equity':'903/2','mixed':'803/2'}}[election][mix]
    e['cash']={'cash':dict(opening='300/1',consideration_paid='120/1',noncash_equity='0/1',acquired='50/1',acquisition_net='-70/1',operating='40/1',closing='270/1'),'equity':dict(opening='300/1',consideration_paid='0/1',noncash_equity='120/1',acquired='50/1',acquisition_net='50/1',operating='40/1',closing='390/1'),'mixed':dict(opening='300/1',consideration_paid='50/1',noncash_equity='70/1',acquired='50/1',acquisition_net='0/1',operating='40/1',closing='340/1')}[mix]
    e['parent_equity']=dict(opening='300/1',new_equity={'cash':'0/1','equity':'120/1','mixed':'70/1'}[mix],owners_profit=e['owners_profit'],closing=e['owners_equity_closing'])
    return e
def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' and os.environ.get('PYTHONDONTWRITEBYTECODE')=='1'
    resource.setrlimit(resource.RLIMIT_CPU,(100,100));out=H/sys.argv[1];out.mkdir(exist_ok=False)
    started=datetime.now(timezone.utc).isoformat();clock=time.monotonic();checks=[];cases=[];controls=[]
    files={H/f for f in ['prepare.py','reference.py','verify.py','contract.md','predecessor-lock.json']}
    files.add(R/'docs/plans/accounting-acquisition-consideration-20261027.md')
    files.update(R/p for p in json.loads((H/'predecessor-lock.json').read_text()))
    files.update(R/p for p in json.loads((S/'attempt-01/source-lock.json').read_text()))
    lock={str(p.relative_to(R)):sha256(p.read_bytes()).hexdigest() for p in files}
    for p in files:
        dst=out/'inputs'/p.relative_to(R);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(p.read_bytes())
    def ck(name,a,b=True):
        checks.append(dict(name=name,passed=a==b))
        if a!=b:raise AssertionError(name+': '+repr(a)[:200]+' != '+repr(b)[:200])
    def run(name,b,election,mix):
        before=deepcopy(b);r=m.report(b);ck(name+'/status',r['status'],'conditional_worksheet');ck(name+'/immutable',b,before)
        ck(name+'/all_report_fields',r['report'],expected(election,mix))
        ck(name+'/original_legal_books',r['original_books'],b['payload']['books']);ck(name+'/consideration',r['consideration'],b['payload']['consideration'])
        ck(name+'/scope_and_unknowns',r['symbolic_result'],m.sym.derive(b['payload']['symbolic_request']))
        ck(name+'/flags',[r[k] for k in m.FLAGS],[False]*len(m.FLAGS))
        prior=next(x for x in SAVED if x['id']==election)['result']
        ck(name+'/same_conditional_measurements',r['conditional_measurements'],prior['conditional_measurements'])
        for stage,key in [('acquisition','acquisition_worksheet'),('closing','closing_worksheet')]:
            ck(name+'/'+stage+'/all_adjustment_origins',r[key]['journals'],prior[key]['journals'])
            # Unchanged total consideration leaves all consolidation adjustments unchanged.
            adjusted=deepcopy(prior[key]['adjusted']);adjusted['P.cash']={'cash':'180/1','equity':'300/1','mixed':'250/1'}[mix];adjusted['P.capital']={'cash':'-300/1','equity':'-420/1','mixed':'-370/1'}[mix]
            raw=deepcopy(prior[key]['raw']);raw['P.cash']=adjusted['P.cash'];raw['P.capital']=adjusted['P.capital']
            ck(name+'/'+stage+'/all_adjusted_accounts',r[key]['adjusted'],adjusted);ck(name+'/'+stage+'/all_raw_accounts',r[key]['raw'],raw)
        cases.append(dict(id=name,request=b,result=r));return r
    def reject(name,b,reason,rehash=True):
        if rehash:bind(b)
        before=deepcopy(b);r=m.report(b);ck(name+'/status',r['status'],'invalid');ck(name+'/reason',r['reason'],reason)
        ck(name+'/immutable',b,before);ck(name+'/flags',[r[k] for k in m.FLAGS],[False]*len(m.FLAGS));ck(name+'/no_report','report' not in r)
        controls.append(dict(id=name,request=b,result=r))
    try:
        for election in ['proportional','fair_value','none']:
            for mix in ['cash','equity','mixed']:run(election+'/'+mix,fixture(election,mix),election,mix)
        for prior in SAVED:
            b=fixture(saved=prior);r=m.report(b);ck('replay/'+prior['id']+'/status',r['status'],'conditional_worksheet')
            report=deepcopy(r['report']);report.pop('parent_equity');report['cash'].pop('noncash_equity')
            ck('replay/'+prior['id']+'/complete_report',report,prior['result']['report'])
            for key in ['original_books','acquisition_worksheet','closing_worksheet','conditional_measurements','symbolic_result','acquired_items','basis_premises']:
                ck('replay/'+prior['id']+'/'+key,r[key],prior['result'][key])
            cases.append(dict(id='baseline/'+prior['id'],request=b,result=r))
        b=fixture();b['payload']['consideration']['cash']='119/1';reject('stale_envelope',b,'payload_binding',False)
        for key in ['cash','new_parent_equity']:
            b=fixture();b['payload']['consideration'][key]='-1/1';reject('negative/'+key,b,'negative_consideration')
        b=fixture('proportional','mixed');b['payload']['consideration']['new_parent_equity']='60/1';reject('inconsistent_total',b,'investment_binding')
        b=fixture('proportional','equity');b['payload']['books']['P']['snapshots']['acquisition']['balances'].update(cash='180/1',capital='-300/1');reject('noncash_invented_payment',b,'parent_purchase_journal')
        b=fixture('proportional','equity');b['payload']['books']['P']['snapshots']['acquisition']['balances'].update(cash='420/1',capital='-540/1');reject('noncash_invented_receipt',b,'parent_purchase_journal')
        b=fixture();b['payload']['consideration']['kind']='debt_conversion';reject('debt_conversion_not_equity_issue',b,'consideration_kind')
        b=fixture();b['payload']['consideration']['at']='2025-07-01T00:00:00.1Z';reject('subday_consideration',b,'consideration_date')
        b=fixture();b['payload']['consideration']['currency']='HKD';reject('wrong_currency',b,'consideration_unit')
        b=fixture();b['payload']['consideration']['unit']='thousands';reject('wrong_unit',b,'consideration_unit')
        b=fixture();b['payload']['consideration']['premise']='';reject('missing_value_premise',b,'text_required')
        b=fixture();b['payload']['consideration']['fair_value_established']=True;reject('open_schema',b,'consideration_fields')
        b=fixture('proportional','equity');b['payload']['operating_cash']='160/1';reject('equity_in_operating_cash',b,'postcontrol_cash_revenue')
        for p,d in lock.items():ck('protected/'+p,sha256((R/p).read_bytes()).hexdigest(),d)
        result=dict(status='PASS',cases=len(cases),refusal_controls=len(controls),assertions=len(checks),protected_files=len(lock),source_admission=False,accounting_admission=False,posting_authorized=False,report_authorized=False)
    except Exception:result=dict(status='FAIL',cases=len(cases),refusal_controls=len(controls),assertions=len(checks),error=traceback.format_exc())
    for name,obj in [('verification.json',result),('cases.json',cases),('controls.json',controls),('checks.json',checks),('source-lock.json',lock)]:
        (out/name).write_text(json.dumps(obj,indent=2)+'\n')
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 '+str(Path(__file__).relative_to(R))+' '+sys.argv[1],environment=platform.python_version(),cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic synthetic',started_utc=started,wall_seconds=time.monotonic()-clock,data_version='source-lock.json',plan='docs/plans/accounting-acquisition-consideration-20261027.md',result=str((H/'result.md').relative_to(R)),output=str(out.relative_to(R)))
    (out/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(result))
    if result['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
