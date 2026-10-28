"""Units, carried maturity and honest evaluation of exact supplied examples."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import gzip,json
from pathlib import Path
import platform,subprocess,sys,time
import fixture as f
from partial import summarize
ROOT,H=f.ROOT,Path(__file__).resolve().parent
PLAN='docs/plans/company-state-units-horizon-evaluation-20261028.md'
def dump(p,d):p.write_text(json.dumps(d,indent=2,default=str)+chr(10))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    out=ap.parse_args().output.resolve();out.mkdir(exist_ok=False);start=time.monotonic()
    checks=[];native=[];calculations={}
    def ck(n,a,e):
        row=dict(name=n,passed=a==e,actual=a,expected=e)
        if len(json.dumps(row,default=str))>1400:row=dict(name=n,passed=a==e,actual_sha256=sha256(json.dumps(a,sort_keys=True,default=str).encode()).hexdigest(),expected_sha256=sha256(json.dumps(e,sort_keys=True,default=str).encode()).hexdigest())
        checks.append(row)
    def run(n,b):
        before=f.program.digest(b);r=f.program.run(b)
        ck(n+'/input unchanged',f.program.digest(b),before);ck(n+'/replay',f.program.verify(b,r),True)
        native.append(dict(id=n,input=b,result=r));return r
    # F061: monetary unit versus dimensional residual, exact minimizer.
    units=[]
    for scale in [Q(1),Q(1,10**6),Q(10**6)]:
        raw=1/(1+scale**2);normalized=Q(1,2)
        ck('raw derivative zero/'+str(scale),2*scale**2*raw+2*(raw-1),Q(0))
        for t in [Q(0),Q(1,4),Q(1,2),Q(1)]:
            loss=scale**2*t*t+(t-1)**2
            minimum=scale**2/(1+scale**2)
            ck('raw square completion/'+str(scale)+'/'+str(t),loss-minimum,(1+scale**2)*(t-raw)**2)
            normalized_loss=(scale*t/scale)**2+(t-1)**2
            ck('normalized unit invariance/'+str(scale)+'/'+str(t),normalized_loss,t*t+(t-1)**2)
        units.append(dict(monetary_scale=scale,raw_minimizer=raw,normalized_minimizer=normalized))
    ck('raw dollar/million decision changes',units[0]['raw_minimizer']==units[1]['raw_minimizer'],False)
    ck('million raw near one',units[1]['raw_minimizer']>Q(999,1000),True)
    ck('consistent normalized decisions',[u['normalized_minimizer'] for u in units],[Q(1,2)]*3)
    calculations['units']=units
    # F062: use actual carried opening; full state and reports, two account maps.
    old=f.ex.native.Engine.apply;f.ex.native.Engine.apply=lambda *a,**k:(_ for _ in ()).throw(AssertionError('legacy fallback forbidden'))
    try:
        for owner,cash in product(['alpha','beta'],[Q(3),Q(1)]):
            name=owner+'/cash'+str(cash);b,m=f.first(owner,cash);r=run(name+'/stub2027',b)
            ck(name+'/first complete',r['status'],'complete_provisional')
            if r['status']!='complete_provisional':continue
            borrowed=deepcopy(b['opening']['balances']);borrowed.update({m['cash']:f.fmt(cash+20),m['debt']:'-20/1'})
            accrued=deepcopy(borrowed);accrued.update({m['interest']:'2/31',m['interest_payable']:'-2/31'})
            carried=deepcopy(accrued);carried.update({m['interest']:'0/1',m['retained']:'2/31'})
            ck(name+'/borrow full balances',r['trace'][0]['result']['transition']['after']['balances'],borrowed)
            ck(name+'/accrued full balances',r['trace'][1]['result']['transition']['after']['balances'],accrued)
            nxt=r['trace'][3]['result']['next_opening'];ck(name+'/carried full balances',nxt['balances'],carried)
            ck(name+'/carried debt memory',nxt['memory']['finance'],dict(cursor='2028-01-01',debt='-20/1'))
            ck(name+'/one day stub',b['opening']['period'],dict(start='2027-12-31',end_exclusive='2028-01-01'))
            ck(name+'/short horizon cash',r['trace'][2]['result']['cash_flows']['closing_cash'],f.fmt(cash+20))
            ck(name+'/short horizon liabilities',r['trace'][2]['result']['balance_sheet']['total_liabilities'],f.fmt(20+Q(2,31)))
            ck(name+'/borrowing not profit',r['trace'][2]['result']['income']['profit'],'-2/31')
            ck(name+'/all carried balances balanced',sum(Q(x) for x in carried.values()),Q(0))
            c=f.second(b,r,m);ck(name+'/exact accepted opening',c['opening'],nxt)
            z=run(name+'/maturity2028',c)
            accrual2=deepcopy(carried);accrual2.update({m['interest']:'60/31',m['interest_payable']:'-2/1'})
            paid_interest=deepcopy(accrual2);paid_interest.update({m['cash']:f.fmt(cash+18),m['interest_payable']:'0/1'})
            ck(name+'/second accrual all balances',z['trace'][0]['result']['transition']['after']['balances'],accrual2)
            ck(name+'/interest settled all balances',z['trace'][1]['result']['transition']['after']['balances'],paid_interest)
            ck(name+'/total interest exactly2',Q(r['trace'][2]['result']['income']['expenses'])+Q(60,31),Q(2))
            if cash==3:
                ck(name+'/repayment completes',z['status'],'complete_provisional')
                final=deepcopy(paid_interest);final.update({m['cash']:'1/1',m['debt']:'0/1'})
                ck(name+'/final all balances',z['current']['balances'],final)
                ck(name+'/final debt memory',z['current']['memory']['finance'],dict(cursor='2028-01-31',debt='0/1'))
                report=z['trace'][3]['result']
                ck(name+'/2028 cash movement',report['cash_flows']['net_movement'],'-22/1')
                ck(name+'/financing payment',report['cash_flows']['activities']['financing']['net'],'-20/1')
                ck(name+'/operating interest payment',report['cash_flows']['activities']['operating']['net'],'-2/1')
                ck(name+'/reconciliations',report['reconciliations'],dict(balance_sheet='0/1',cash='0/1',equity='0/1'))
                ck(name+'/admission flags',[report[x] for x in ['source_admission','accounting_admission','fiscal_complete','notes_complete']],[False]*4)
                ck(name+'/report ends at maturity',report['as_of'],'2028-01-31')
            else:
                ck(name+'/shortfall stops',z['status'],'stopped_provisional')
                ck(name+'/shortfall invalid',z['stop']['status'],'invalid')
                ck(name+'/no fabricated payment',z['current']['balances'],paid_interest)
                ck(name+'/debt stays outstanding',z['current']['memory']['finance']['debt'],'-20/1')
                ck(name+'/cash shortfall positive',20-Q(z['current']['balances'][m['cash']]),Q(1))
            request=deepcopy(r['trace'][3]['request']);tamper=deepcopy(r['trace'][3]['result'])
            tamper['next_opening']['balances'][m['debt']]='0/1';tamper['next_opening']['balances'][m['retained']]=f.fmt(Q(2,31)-20)
            tamper['next_opening']['memory']['finance']['debt']='0/1'
            ck(name+'/erased debt still balances',sum(Q(x) for x in tamper['next_opening']['balances'].values()),Q(0))
            refused=f.program.carry.apply(request,tamper)
            ck(name+'/erased debt refused',refused['status'],'invalid');ck(name+'/carry recomputes',refused.get('reason'),'proposal_recomputation_mismatch')
            native.append(dict(id=name+'/tampered carry',request=request,proposal=tamper,result=refused))
    finally:f.ex.native.Engine.apply=old
    # F063: correspond to already retained constrained historical fit, no score.
    previous=ROOT/'data/accounting-master/company-state-original-debt-failures-20261028/attempt-03'
    manifest=json.loads((previous/'run-manifest.json').read_text())
    for p,h in manifest['source_hashes'].items():ck('historical source/'+p,sha256((ROOT/p).read_bytes()).hexdigest(),h)
    witnesses=json.loads((previous/'witnesses.json').read_text());result=json.loads((previous/'verification.json').read_text())
    ck('retained historical unit passes',result['status'],'pass')
    ck('imposed historical fit',[x['historical_interest'] for x in witnesses],['5']*3)
    ck('future outcomes distinguish',[x['stress_interest'] for x in witnesses],['5','7','6'])
    ck('no empirical forecast from constrained fit',result['empirical_forecast'],False)
    ck('no inferred probability from fit',[x['probability'] for x in witnesses],[None]*3)
    calculations['historical_fit']=dict(witnesses=witnesses,interpretation='Reconstruction checks imposed observations; not future empirical validation',source_hashes_verified=len(manifest['source_hashes']))
    # F064: exact continuous law, endpoint approximation and quadrature.
    threshold=Q(447,5);alpha_boundary=(90-threshold)/2
    ck('breach alpha threshold',alpha_boundary,Q(3,10));ck('uniform breach',1-alpha_boundary,Q(7,10))
    ck('uniform mean',Q(88+90,2),Q(89));ck('endpoint mean',Q(88+90,2),Q(89))
    endpoint_breach=sum(Q(1,2) for x in [88,90] if x<threshold);ck('endpoint breach differs',endpoint_breach,Q(1,2))
    mids=[Q(2*i+1,8) for i in range(4)]
    ck('midpoint mean',sum(90-2*x for x in mids)/4,Q(89));ck('midpoint breach',sum(Q(1,4) for x in mids if 90-2*x<threshold),Q(3,4))
    boundary=[Q(1,10),Q(3,10),Q(1,2),Q(7,10),Q(9,10)]
    ck('grid strict boundary',sum(Q(1,5) for x in boundary if 90-2*x<threshold),Q(3,5))
    ck('grid inclusive boundary',sum(Q(1,5) for x in boundary if 90-2*x<=threshold),Q(4,5))
    calculations['tail']=dict(cash='90-2alpha',alpha_law='Supplied Uniform[0,1]',mean='89',threshold=str(threshold),breach_operator='<',exact_breach='7/10',endpoint_breach=str(endpoint_breach),midpoint_alpha=list(map(str,mids)),midpoint_breach='3/4',empirical_admission=False)
    # F065: keep unsupported mass, not zero cash or a default outcome.
    rows=[dict(id='ordinary',mass='3/5',status='complete',cash='100'),dict(id='breach',mass='1/10',status='complete',cash='20'),dict(id='distress',mass='3/10',status='unresolved',cash=None)]
    partial=summarize(rows,50,['0','100'])
    ck('known mass',partial['known_mass'],'7/10');ck('unresolved mass',partial['unresolved_mass'],'3/10')
    ck('known weighted contribution',partial['known_weighted_contribution'],'62');ck('conditional mean',partial['conditional_on_success_mean'],'620/7')
    ck('no unconditional mean',partial['unconditional_mean'],None);ck('breach bounds',partial['breach_probability_bounds'],['1/10','2/5'])
    ck('mean bounds from supplied cash range',partial['mean_bounds'],['62','92'])
    ck('no bounds without assumption',summarize(rows,50)['mean_bounds'],None)
    completions=[]
    for cash in [0,49,50,100]:
        completed=deepcopy(rows);completed[-1].update(status='complete',cash=str(cash));r=summarize(completed,50)
        exact_mean=Q(62)+Q(3,10)*cash;prob=Q(1,10)+(Q(3,10) if cash<50 else 0)
        ck('completion mean/'+str(cash),Q(r['unconditional_mean']),exact_mean)
        ck('completion breach/'+str(cash),list(map(Q,r['breach_probability_bounds'])),[prob]*2)
        ck('completion within mean bounds/'+str(cash),Q(62)<=exact_mean<=Q(92),True)
        completions.append(dict(cash=cash,result=r))
    dropped=deepcopy(rows[:2])
    for row in dropped:row['mass']=str(Q(row['mass'])/Q(7,10))
    wrong=summarize(dropped,50)
    ck('renormalized success gives conditional mean',wrong['unconditional_mean'],partial['conditional_on_success_mean'])
    ck('renormalization hides mass',wrong['unresolved_mass'],'0')
    ck('renormalized breach',wrong['breach_probability_bounds'],['1/7','1/7'])
    try:summarize(rows[:2],50)
    except ValueError as e:ck('unadjusted omitted mass refused',str(e),'mass_not_one')
    else:ck('unadjusted omitted mass refused','accepted','mass_not_one')
    for name,bad,expected in [('unknown assigned zero',[*deepcopy(rows[:2]),dict(rows[-1],cash='0')],'unknown_has_value'),('duplicate',[*deepcopy(rows),deepcopy(rows[0])],'duplicate_branch')]:
        try:summarize(bad,50)
        except ValueError as e:ck(name,str(e),expected)
        else:ck(name,'accepted',expected)
    calculations['partial']=dict(original_rows=rows,partial=partial,possible_completions=completions,wrong_renormalized_rows=dropped,conditional_only=wrong)
    fm=ROOT/'data/accounting-master/unified-program-20261028/failure-map.json';originals=[r['original_row'] for r in json.loads(fm.read_text())['rows'] if r['original_row']['id'] in ['SIM-F061','SIM-F062','SIM-F063','SIM-F064','SIM-F065']]
    ck('original discriminators',[r['discriminating_case'] for r in originals],['Dollars transformed consistently to millions','Borrow20 at year-end and repay22 next month','Evaluate on statements already imposed as constraints','Two-point approximation matches mean89 but breach.5 not.7','Solver failures occur mainly under distress'])
    failed=[x for x in checks if not x['passed']];v=dict(status='fail' if failed else 'pass',checks=len(checks),native_programs=sum('input' in x for x in native),carry_tamper_controls=sum('proposal' in x for x in native),failed=[x['name'] for x in failed],original_rows=[x['id'] for x in originals],empirical_forecast=False,source_admission=False)
    for name,obj in [('verification',v),('checks',checks),('calculations',calculations),('original-rows',originals)]:dump(out/(name+'.json'),obj)
    with gzip.open(out/'native-results.json.gz','wt') as z:json.dump(native,z)
    sources={Path(__file__),ROOT/PLAN,H/'fixture.py',H/'partial.py',H/'setup-diagnostics.md',fm,previous/'verification.json',previous/'run-manifest.json',previous/'witnesses.json'}
    sources.update(ROOT/'docs/design/proposal/manuscript-release-prep-v552r2-20261027/simulation'/n for n in ['11-numerics.tex','12-validation.tex','18-computation-cases.tex','23-memory-case.tex','24-evaluation.tex'])
    sources.update(Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().is_relative_to(ROOT))
    dump(out/'run-manifest.json',dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=dict(python=platform.python_version()),cpu_gpu='CPU-only exact native execution and rational arithmetic; no GPU imports',random_seeds='N/A deterministic',data_version='Original F061-F065; explicit stub period/rate/schedule and finite/continuous probability examples',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plan_file=PLAN,result_file=str((H/'result.md').relative_to(ROOT)),source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(sources)}))
    for n in ['check.py','fixture.py','partial.py']:(out/n).write_bytes((H/n).read_bytes())
    print(json.dumps(v));return bool(failed)
if __name__=='__main__':raise SystemExit(main())
