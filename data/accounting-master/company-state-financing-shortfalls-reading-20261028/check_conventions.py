"""Exact source-convention checks; no behavioral simulation."""
from fractions import Fraction as F
from pathlib import Path
from hashlib import sha256
import json,sys,time,subprocess,platform
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
start=time.monotonic();out=HERE/'convention-attempt-01';out.mkdir(exist_ok=False);checks=[]
def c(n,a,b):checks.append(dict(name=n,passed=a==b,actual=str(a),expected=str(b)))
alpha,beta=F(2),F(5);w=lambda s:F(s<=0);y=lambda s:beta+alpha*w(s)
c('right-minus-left treatment indicator',w(F(1,100))-w(F(-1,100)),F(-1))
c('printed outcome difference',y(F(1,100))-y(F(-1,100)),-alpha)
c('treated-minus-control difference',y(F(-1,100))-y(F(1,100)),alpha)
c('zero-effect masks orientation',F(0)*(-1),F(0))
for p,r in [(F(8),F(-1,10)),(F(12),F(0))]:
 b,tau,G,lam=F(10),F(1),F(-2),F(1,10);D=(b-p*(1+r)+tau)*int(p*(1+r)<b);e=G-D;phi=lam*e*int(e<0)
 c('Bellman omission p='+str(p),(G+phi)-(e+phi),D)
 if p==8:
  c('shortfall plus penalty',D,F(19,5));c('prose versus post-return contribution',(b-p*(1+r))-(b-p),F(4,5))
 else:c('no-shortfall difference',D,F(0))
theta,eta=F(7,10),F(7,40);a=eta-theta
c('labor exponent',a,F(-21,40));c('labor marginal product at unit inputs',a,F(-21,40))
c('positive-marginal-product assumption fails',a>0,False)
c('labor own second derivative',a*(a-1),F(1281,1600))
c('negative-Hessian diagonal assumption fails',a*(a-1)<0,False)
p=HERE/'sources/shortfalls-author-20080520.pdf';c('source identity',sha256(p.read_bytes()).hexdigest(),'8ea063d62cb5bfc04f726e368e247077d25bc7b27fa60dd6a9f1f972e14d2d6a')
failed=[x['name'] for x in checks if not x['passed']]
summary=dict(passed=not failed,checks=len(checks),failed=failed,literal_model_eligible_for_import=False,author_code_checked=False,published_equivalence_checked=False)
plans=[ROOT/'docs/plans/company-state-financing-shortfalls-reading-20261028.md',ROOT/'docs/plans/company-state-shortfalls-conventions-20261028.md']
manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=platform.python_version(),cpu_gpu='CPU-only exact Fraction; no GPU imports',seeds='N/A deterministic',wall_seconds=time.monotonic()-start,data_version=str(p.relative_to(ROOT)),plan_file=str(plans[1].relative_to(ROOT)),result_file=str((HERE/'result.md').relative_to(ROOT)),source_hashes={str(x.relative_to(ROOT)):sha256(x.read_bytes()).hexdigest() for x in [p,Path(__file__),*plans]})
for n,d in [('checks',checks),('verification',summary),('run-manifest',manifest)]: (out/(n+'.json')).write_text(json.dumps(d,indent=2)+chr(10))
print(json.dumps(summary));raise SystemExit(bool(failed))

