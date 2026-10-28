"""Original finance cases and complete retained native evidence, without reruns."""
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip,json,platform,subprocess,sys,time,traceback
import rights as f
H=Path(__file__).resolve().parent;ROOT=H.parents[2];OUT=H/sys.argv[1]
OUT.mkdir(exist_ok=False);start=time.monotonic();checks=[];results=[];controls=[];reused=[];sources=set()
def dump(name,x):(OUT/name).write_text(json.dumps(x,indent=2)+chr(10))
def ck(name,a,b):
    large=isinstance(a,(dict,list)) or isinstance(b,(dict,list))
    checks.append(dict(name=name,passed=a==b,actual=None if large else a,expected=None if large else b,actual_sha256=f.digest(a) if large else None,expected_sha256=f.digest(b) if large else None))
def keep(name,inputs,result):results.append(dict(name=name,inputs=deepcopy(inputs),result=deepcopy(result)));return result
def refuse(name,fn,reason):
    try:fn();actual='accepted'
    except ValueError as exc:actual=str(exc)
    controls.append(dict(name=name,reason=actual));ck(name,actual,reason)
def read(relative):
    p=ROOT/'data/accounting-master'/relative;sources.add(p)
    return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())
def reuse(directory,names):
    folder=ROOT/'data/accounting-master'/directory;rows=read(directory+'/checks.json');lookup={r['name']:r for r in rows}
    for name in names:
        r=lookup[name]
        if 'actual' in r:ck('retained/'+name,r['actual'],r['expected'])
        else:ck('retained hashes/'+name,r['actual_sha256'],r['expected_sha256'])
        ck('retained pass/'+name,r['passed'],True)
    files=sorted(p for p in folder.iterdir() if p.is_file());sources.update(files)
    manifest=read(directory+'/run-manifest.json')
    for path,expected in manifest.get('source_hashes',{}).items():
        p=ROOT/path;sources.add(p);ck('source/'+path,sha256(p.read_bytes()).hexdigest(),expected)
    reused.append(dict(directory=directory,selected_checks=names,files={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in files}))

def main():
    face=Q(100);recovery=Q(40);default=Q(1,10);gross=Q(21,20)
    payoff=(1-default)*face+default*recovery;proceeds=payoff/gross;yield_rate=face/proceeds-1
    keep('original creditor law',dict(face='100',recovery='40',default_weight='1/10',gross='21/20'),dict(expected_payoff=str(payoff),proceeds=str(proceeds),promised_yield=str(yield_rate)))
    ck('proceeds',str(proceeds),'1880/21');ck('promised yield',str(yield_rate),'11/94')
    mixed=Q(9000,101);ck('mixed lender gap',str(gross*mixed-payoff),'-44/101')
    for name,need,mode,status in [('original refusal','95','require_full','refused_insufficient_offer'),('explicit smaller replan','89','require_full','conditional_full_payment'),('partial distress','95','partial_payment','conditional_partial_payment')]:
        r=keep(name,dict(proceeds=str(proceeds),need=need,mode=mode),f.funding(str(proceeds),need,mode))
        ck(name+'/status',r['status'],status);ck(name+'/cash conserved',Q(r['paid'])+Q(r['closing_cash'])==proceeds,True)
        ck(name+'/obligation conserved',Q(r['paid'])+Q(r['unpaid'])==Q(need),True)
        if name=='original refusal':ck(name+'/gap',r['funding_gap'],'115/21');ck(name+'/no payment on refusal',r['paid'],'0')
        if name=='partial distress':ck(name+'/arrears',r['unpaid'],'115/21')
    ck('unknown offer unresolved',f.funding(None,'95','require_full')['status'],'unresolved_offer')
    refuse('implicit distress policy',lambda:f.funding(str(proceeds),'95','default'),'explicit_payment_policy_required')
    refuse('negative need',lambda:f.funding('10','-1','require_full'),'negative_need')
    refuse('negative proceeds',lambda:f.funding('-1','10','require_full'),'negative_proceeds')
    for estate,expected in [('70',{'senior':'60','junior':'10','equity':'0'}),('130',{'senior':'60','junior':'50','equity':'20'})]:
        r=keep('strict waterfall'+estate,dict(estate=estate,claims={'senior':'60','junior':'50'},priority=['senior','junior']),f.waterfall(estate,{'senior':'60','junior':'50'},['senior','junior']))
        ck('original waterfall'+estate,{**r['payments'],'equity':r['equity_residual']},expected)
        ck('one estate'+estate,str(sum(map(Q,r['payments'].values()))+Q(r['equity_residual'])),estate)
    alternatives=[f.waterfall('70',{'senior':'60','junior':'50'},p) for p in [['senior','junior'],['junior','senior']]]
    keep('unknown priority retains alternatives',dict(estate='70',priority=None),dict(status='unweighted_priority_alternatives',alternatives=alternatives,probabilities=None))
    ck('different priority recoveries',[r['payments'] for r in alternatives],[{'senior':'60','junior':'10'},{'junior':'50','senior':'20'}])
    ck('independent recovery overdraw',min(70,60)+min(70,50)-70,40)
    refuse('missing claimant in priority',lambda:f.waterfall('70',{'senior':'60','junior':'50'},['senior']),'priority_claim_population')
    refuse('duplicate priority',lambda:f.waterfall('70',{'senior':'60','junior':'50'},['senior','junior','junior']),'priority_claim_population')
    refuse('negative estate',lambda:f.waterfall('-1',{'senior':'60'},['senior']),'negative_claim_or_estate')
    state=f.opening();before=deepcopy(state);event=dict(id='conversion.1',fraction='2/5',approved=True)
    converted=keep('full junior conversion',dict(state=state,event=event),f.convert(state,event))
    ck('conversion input unchanged',state,before);ck('estate unchanged',converted['current']['estate'],'100')
    ck('junior extinguished',[converted['current']['junior_claim'],converted['current']['junior_active']],['0',False])
    ck('ownership partition',[converted['current']['converted_fraction'],converted['current']['old_equity_fraction']],['2/5','3/5'])
    settled=keep('original60-16-24 distribution',converted['current'],f.settle_converted(converted['current']))
    ck('original allocations',[settled[k] for k in ['senior','converted_equity','old_equity']],['60','16','24'])
    ck('no junior debt again',settled['junior_debt'],'0');ck('whole estate distributed',sum(Q(settled[k]) for k in ['senior','junior_debt','converted_equity','old_equity'])==100,True)
    forged=deepcopy(converted['current']);forged.update(junior_active=True,junior_claim='50')
    refuse('stale debt plus shares',lambda:f.settle_converted(forged),'converted_claim_still_active')
    # Paying converted holder the entire residual40 as debt also conserves cash,
    # but violates extinguishment and the declared2/5 ownership distribution.
    keep('balanced wrong remaining debt',dict(estate='100'),dict(senior='60',junior_debt='40',converted_equity='0',old_equity='0',total='100',valid=False))
    ck('conservation alone misses rights',60+40==100 and 40!=16,True)
    refuse('same conversion repeated',lambda:f.convert(converted['current'],event),'duplicate_conversion')
    e={**event,'id':'conversion.2'};refuse('second different ID',lambda:f.convert(converted['current'],e),'junior_already_extinguished')
    for approval,status in [(False,'unsupported'),(None,'unresolved')]:
        e={**event,'approved':approval};r=keep('approval'+str(approval),dict(state=state,event=e),f.convert(state,e));ck('approval state immutable'+str(approval),r['current'],state);ck('approval result'+str(approval),r['status'],status)
    refuse('bad ownership',lambda:f.convert(state,{**event,'fraction':'3/2'}),'ownership_fraction')
    bad=deepcopy(converted['current']);bad['old_equity_fraction']='1';refuse('ownership over-allocation',lambda:f.settle_converted(bad),'ownership_partition')
    reuse('company-state-face-proceeds-failure-20261028/attempt-02',['original/state expansion','original/lender break even','original/native replay','original/all balances','original/all memory','SIM-F021 yield','SIM-F021 need95 shortfall','mixed-convention proceeds','mixed-convention lender gap'])
    reuse('company-state-book-contract-failure-20261028/attempt-01',['unknown_face/exact joint family','original promised110 minus carrying100','wrong face substitution value','alpha/face110/complete unchanged book','alpha/face110/face memory','alpha/face110/carrying debt','beta/face110/complete unchanged book'])
    reuse('company-state-pricing-policy-failures-20261028/attempt-01',['policy-dependent exact values','funding shortfall remains','original law at false root'])
    reuse('company-state-claims-conversion-20261028/attempt-04',['alpha/all balances','alpha/all memory','alpha/no cash movement','alpha/convert/replay','beta/all balances','beta/all memory','beta/convert/replay','independent claim payments overdraw pool'])
    native=read('company-state-claims-conversion-20261028/attempt-04/native-results.json.gz')
    for owner in ['alpha','beta']:
        r=next(x['result'] for x in native if x['id']==owner+'/convert');ck(owner+'/native face actually cleared',r['current']['memory']['terms']['face'],'0/1');ck(owner+'/native shares actually retained',r['current']['memory']['terms']['new_shares'],'16/1')
    original=read('unified-program-20261028/failure-map.json');ids=['LIT-F016','LIT-F017','LIT-F018','LIT-F019','LIT-F020'];rows=[r['original_row'] for r in original['rows'] if r['original_row']['id'] in ids]
    ck('original rows',len(rows),5);dump('original-rows.json',rows)
    return dict(passed=all(c['passed'] for c in checks),checks=len(checks),result_groups=len(results),refusal_controls=len(controls),reused_units=len(reused),failed=[c['name'] for c in checks if not c['passed']],original_rows=ids)
try:
    summary=main();dump('verification.json',summary)
except Exception:
    dump('failure.json',dict(error=traceback.format_exc(),checks_passed=sum(c['passed'] for c in checks)));raise
finally:
    dump('checks.json',checks);dump('results.json',results);dump('controls.json',controls);dump('reused-evidence.json',reused)
    for name in ['check.py','rights.py']:(OUT/name).write_bytes((H/name).read_bytes());sources.add(H/name)
    sources.add(ROOT/'docs/plans/company-state-finance-reconciliation-20261028.md')
    dump('source-hashes.json',{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(sources)})
    dump('manifest.json',dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=platform.python_version(),cpu_gpu='CPU only; exact standard-library fractions; no accelerator imports',random_seeds='N/A deterministic examples',data_version='Original finance cases and complete retained native evidence',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plan='docs/plans/company-state-finance-reconciliation-20261028.md',result=str(H.relative_to(ROOT)/'result.md'),artifacts=str(OUT.relative_to(ROOT))))
print(json.dumps(summary));raise SystemExit(not summary['passed'])
