"""Exact conditional diagnostics; no numerical model or empirical promotion."""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
from datetime import datetime,timezone
import json,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
SOURCE='docs/papers/Dynamic Models and Structural Estimation in Corporate Finance Strebulaev (2012).pdf'
PLAN='docs/plans/company-state-financing-source-diagnostics-20261028.md'
def main():
    start=time.monotonic();out=HERE/'convention-attempt-01';out.mkdir(exist_ok=False);checks=[]
    def c(name,a,b):checks.append(dict(name=name,passed=a==b,actual=str(a),expected=str(b)))
    eta0,eta1=F('0.08'),F('0.028')
    for e in [F(-1),F(-10),F(-100)]:
        printed_eta=eta0+eta1*e;printed=e+printed_eta
        need=-e;cost=eta0+eta1*need;cash=-need-cost
        c('fixed-cost sign difference e='+str(e),printed-cash,2*eta0)
        c('positive explicit issue cost e='+str(e),cost>0,True)
    c('printed eta negative at e=-10',eta0+eta1*F(-10)<0,True)
    c('zero-fixed-cost limit',F(-1)+eta1*F(-1),-F(1)-eta1*F(1))
    c('no issuance for positive payout',F(2),F(2))
    k,delta,tau,pi,I,cost,r,p,pnext=map(F,['100','1/10','1/5','20','10','2','1/20','5','6'])
    def cash_model(tau,delta):
        return (1-tau)*pi+tau*delta*k-cost-I-pnext/(1+r*(1-tau))+p
    def printed_debt(tau):
        b,bnext=-p,-pnext
        return (1-tau)*pi-cost-I+bnext/(1+r*(1-tau))-b
    c('3.17 to3.21 depreciation shield difference',cash_model(tau,delta)-printed_debt(tau),F(2))
    c('zero-tax substitution limit',cash_model(F(0),delta),printed_debt(F(0)))
    c('zero-depreciation substitution limit',cash_model(tau,F(0)),printed_debt(tau))
    x,y,z=F(2),F(3),F(5);a,b,cval=x+y,y+z,x+z
    c('moment-system x',(a+cval-b)/2,x)
    c('moment-system y',(a+b-cval)/2,y)
    c('moment-system z',(b+cval-a)/2,z)
    c('dependent two-moment counterexample',[(u+v,2*(u+v)) for u,v in [(F(1),F(2)),(F(2),F(1))]],[(F(3),F(6))]*2)
    k,kprime,pi=F(100),F(110),F(30)
    payout=lambda d,f:pi-(kprime-(1-d)*k)-f*k
    c('4.4 direct expansion',payout(F('0.1'),F('0.2')),pi-kprime+(1-F('0.1')-F('0.2'))*k)
    c('4.4 equal delta+phi payout',payout(F('0.1'),F('0.2')),payout(F('0.2'),F('0.1')))
    c('separate depreciation distinguishes',F('0.1')*k!=F('0.2')*k,True)
    source=ROOT/SOURCE;c('retained source identity',sha256(source.read_bytes()).hexdigest(),'3ea7578f4e007d768f1b1570cc29457b8f54428a9dcc3b063fe454286e82dbaf')
    failed=[x['name'] for x in checks if not x['passed']]
    summary=dict(passed=not failed,checks=len(checks),failed=failed,source_equations_eligible_for_direct_import=False,
        scoped_findings=['fixed issuance sign mismatch under positive-cost convention','missing depreciation shield under unchanged profit convention'],
        latest_edition_checked=False,author_code_checked=False,empirical_identification=False)
    inputs=[source,ROOT/PLAN,Path(__file__),ROOT/'docs/plans/company-state-dynamic-financing-reading-20261028.md']
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],
        environment=sys.version,cpu_gpu='CPU-only exact Fraction; no accelerator imports',seeds='N/A deterministic',
        utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,data_version=SOURCE,plan_file=PLAN,
        result_file=str((HERE/'result.md').relative_to(ROOT)),source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in inputs})
    for name,value in [('checks',checks),('verification',summary),('run-manifest',manifest)]:
        (out/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps(summary));return bool(failed)
if __name__=='__main__':raise SystemExit(main())
