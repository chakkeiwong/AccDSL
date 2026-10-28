"""Exact numerical-target counterexamples, no solver/default promotion."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import platform,subprocess,sys,time
import z3
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
PLAN='docs/plans/company-state-numerical-targets-20261028.md'
BASE=ROOT/'data/accounting-master/company-state-pricing-policy-failures-20261028/attempt-01'
def dump(p,d):p.write_text(json.dumps(d,indent=2,default=str)+'\n')
def residual(t,e):return t-1+t*e
def price(a,p):return a*p
def policy(a):return 2-a
def poly(u):return (u-1)*(u-3)
def slope(u):return 2*u-4

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True,type=Path)
    out=ap.parse_args().output.resolve();out.mkdir(exist_ok=False);start=time.monotonic()
    checks=[];calculations={};smt=[]
    def ck(n,a,e):checks.append(dict(name=n,passed=a==e,actual=a,expected=e))
    def prove(n,formula,expected='unsat'):
        s=z3.Solver();s.set(timeout=10000);s.add(formula);r=s.check()
        ck(n,str(r),expected);smt.append(dict(name=n,formula=formula.sexpr(),result=str(r),model=str(s.model()) if r==z3.sat else None))
    eps=[Q(-1),Q(1)]
    ck('epsilon mean',sum(eps)/2,Q(0));ck('epsilon variance',sum(e*e for e in eps)/2,Q(1))
    expectations=[]
    for t in [Q(-1),Q(0),Q(1,4),Q(1,2),Q(1),Q(2)]:
        mean=sum(residual(t,e) for e in eps)/2
        single=sum(residual(t,e)**2 for e in eps)/2
        independent=sum(residual(t,e1)*residual(t,e2) for e1,e2 in product(eps,repeat=2))/4
        same=sum(residual(t,e)*residual(t,e) for e in eps)/2
        ck('mean/'+str(t),mean,t-1);ck('single/'+str(t),single,(t-1)**2+t*t)
        ck('independent/'+str(t),independent,(t-1)**2);ck('same draw/'+str(t),same,single)
        expectations.append(dict(theta=t,mean=mean,squared_mean=mean**2,single_squared=single,independent_product=independent,same_draw_product=same))
    theta=z3.Real('theta')
    prove('desired unique minimizer',z3.Or((theta-1)**2<0,z3.And((theta-1)**2==0,theta!=1)))
    prove('single-draw square completion',2*theta**2-2*theta+1 != 2*(theta-z3.RealVal('1/2'))**2+z3.RealVal('1/2'))
    prove('single-draw unique minimizer',z3.And(2*theta**2-2*theta+1<=z3.RealVal('1/2'),theta!=z3.RealVal('1/2')))
    ck('single-draw minimum leaves expected residual',sum(residual(Q(1,2),e) for e in eps)/2,Q(-1,2))
    ck('single minimum is wrong target',sum(residual(Q(1,2),e) for e in eps)**2/4,Q(1,4))
    ck('negative independent product possible',residual(Q(3,4),-1)*residual(Q(3,4),1)<0,True)
    calculations['residuals']=expectations
    # F057: exact constrained comparison and multiplier.
    a=z3.Real('a');lam=z3.Real('lambda')
    prove('nonnegative constrained difference',z3.And(a>=0,(a+1)**2<1))
    prove('strict uniqueness at boundary',z3.And(a>0,(a+1)**2<=1))
    prove('KKT unique supplied convex solution',z3.And(a>=0,lam>=0,2*(a+1)-lam==0,a*lam==0,z3.Or(a!=0,lam!=2)))
    ck('boundary derivative nonzero',2*(Q(0)+1),Q(2))
    ck('boundary multiplier stationarity',2*(Q(0)+1)-Q(2),Q(0))
    ck('boundary complementarity',Q(0)*Q(2),Q(0))
    ck('interior stationary action infeasible',Q(-1)>=0,False)
    for point in [Q(0),Q(1,10),Q(1),Q(100)]:
        ck('boundary algebra/'+str(point),(point+1)**2-1,point*(point+2))
    # F058: exact differences, frozen and complete dependency.
    derivatives=[]
    for point in [Q(1,2),Q(1),Q(3,2)]:
        full=2-2*point;partial=2-point;chain=partial-point
        ck('full chain/'+str(point),chain,full)
        for h in [Q(1,10),Q(1,100),Q(1,1000)]:
            numerical=(price(point+h,policy(point+h))-price(point-h,policy(point-h)))/(2*h)
            detached=(price(point+h,policy(point))-price(point-h,policy(point)))/(2*h)
            ck('total difference/'+str(point)+'/'+str(h),numerical,full)
            ck('partial difference/'+str(point)+'/'+str(h),detached,partial)
            derivatives.append(dict(action=point,step=h,full_derivative=full,partial_derivative=partial,central_total=numerical,central_frozen=detached))
    ck('derivative at full optimum',2-2*Q(1),Q(0));ck('detached derivative at full optimum',2-Q(1),Q(1))
    ck('full optimum price',price(Q(1),policy(Q(1))),Q(1));ck('partial-zero boundary price',price(Q(2),policy(Q(2))),Q(0))
    prove('full price maximum at one',z3.And(a>=0,a<=2,a*(2-a)>1))
    prove('policy equation derivative path',2-a-a != 2-2*a)
    calculations['derivatives']=derivatives
    # F059: validate and reuse the exact retained false-tail evidence.
    manifest=json.loads((BASE/'run-manifest.json').read_text())
    reverified=[]
    for name,h in manifest['source_hashes'].items():
        actual=sha256((ROOT/name).read_bytes()).hexdigest();ck('retained source/'+name,actual,h);reverified.append(name)
    old=json.loads((BASE/'verification.json').read_text());ck('retained pricing attempt passed',old['status'],'pass')
    results=json.loads((BASE/'solver-results.json').read_text())
    selected=[x for x in results if x['id'] in ['wrong positive tail','global flat capacity','need110/region0','need110/region1','need110/region2']]
    ck('retained selected cases',len(selected),5)
    for r in selected:
        if r['id'].startswith('need110'):
            ck(r['id']+'/no original root',r['result']['feasibility'],'Infeasible')
        else:
            expected='10140' if r['id']=='wrong positive tail' else '100'
            ck(r['id']+'/exact bounds',[r['result']['bounds'][k]['value'] for k in ['lower','upper']],[expected,expected])
    face=Q(10140);true=(min(face,60)+min(face,140))/2;false=100+(face-140)/1000
    ck('false tail predicted funding',false,Q(110));ck('original payoff at false root',true,Q(100));ck('remaining shortfall',110-true,Q(10))
    calculations['retained_funding']=dict(source_result=str((BASE.parent/'result.md').relative_to(ROOT)),verified_source_count=len(reverified),selected_results=selected,false_face=face,predicted_proceeds=false,original_proceeds=true,shortfall=110-true,scope='Existing conditional evidence reused, not an independent benchmark')
    # F060: branch completeness uses algebra; Newton output stays local.
    u=z3.Real('u')
    prove('all roots in exact two-branch set',z3.And((u-1)*(u-3)==0,u!=1,u!=3))
    prove('root one feasible',u==1,'sat');prove('root three feasible',u==3,'sat')
    ck('first exact root residual',poly(Q(1)),Q(0));ck('second exact root residual',poly(Q(3)),Q(0))
    branches=[]
    for initial,target in [(Q(0),Q(1)),(Q(4),Q(3))]:
        value=initial;steps=[]
        for k in range(8):
            den=slope(value)
            ck('nonzero Newton denominator/'+str(initial)+'/'+str(k),den!=0,True)
            steps.append(dict(iteration=k,value=value,residual=poly(value),derivative=den))
            value=value-poly(value)/den
        ck('local Newton distance/'+str(initial),abs(value-target)<Q(1,10**10),True)
        ck('local Newton residual/'+str(initial),abs(poly(value))<Q(1,10**10),True)
        branches.append(dict(initial=initial,iterations=8,final=value,final_residual=poly(value),checked_near_root=target,scope='Local diagnostic only; exact algebra separately identifies roots',steps=steps))
    ck('different initializations different roots',branches[0]['checked_near_root']!=branches[1]['checked_near_root'],True)
    ck('midpoint zero derivative',slope(Q(2)),Q(0));ck('midpoint still nonzero residual',poly(Q(2)),Q(-1))
    calculations['roots']=dict(polynomial='(u-1)*(u-3)',exact_roots=[1,3],local_attempts=branches,midpoint_attempt=dict(initial=2,status='unresolved_zero_derivative',residual=-1),economic_selection=None)
    fm=ROOT/'data/accounting-master/unified-program-20261028/failure-map.json'
    originals=[r['original_row'] for r in json.loads(fm.read_text())['rows'] if r['original_row']['id'] in ['SIM-F056','SIM-F057','SIM-F058','SIM-F059','SIM-F060']]
    ck('exact original cases',[r['discriminating_case'] for r in originals],['r=theta-1+theta epsilon','Minimize(a+1)^2 subject to a>=0','Price depends on action through policy','Positive learned slope beyond true capacity100','Different basins or equilibrium branches'])
    failed=[x for x in checks if not x['passed']]
    v=dict(status='fail' if failed else 'pass',checks=len(checks),direct_smt_cases=len(smt),retained_solver_cases=len(selected),failed=[x['name'] for x in failed],original_rows=[r['id'] for r in originals],neural_training=False,equilibrium_admission=False,default_change=False)
    for name,value in [('verification',v),('checks',checks),('calculations',calculations),('direct-smt',smt),('original-rows',originals)]:dump(out/(name+'.json'),value)
    sources={Path(__file__),ROOT/PLAN,fm,BASE/'run-manifest.json',BASE/'verification.json',BASE/'solver-results.json',BASE.parent/'result.md'}
    sources.update(ROOT/'docs/design/proposal/manuscript-release-prep-v552r2-20261027/simulation'/n for n in ['11-numerics.tex','26-finite-finance.tex'])
    dump(out/'run-manifest.json',dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=dict(python=platform.python_version(),z3=z3.get_version_string()),cpu_gpu='CPU-only exact rational and direct polynomial SMT; no GPU imports',random_seeds='N/A deterministic',data_version='Original F056-F060; explicit local affine policy and two-root polynomial',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plan_file=PLAN,result_file=str((H/'result.md').relative_to(ROOT)),source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(sources)}))
    (out/'check.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(v));return bool(failed)
if __name__=='__main__':raise SystemExit(main())
