"""Exact approximation counterexamples; no sampled method ranking."""
import argparse
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from math import comb
from pathlib import Path
import json
import platform
import subprocess
import sys
import time

H=Path(__file__).resolve().parent;ROOT=H.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import z3
from rational_solver_v1 import Problem, Budget, q, solve
BUDGET=Budget(10,10000,100,100,10000,1000,1000000)
PLAN='docs/plans/company-state-approximation-boundaries-20261028.md'
SOURCE='docs/design/proposal/manuscript-release-prep-v552r2-20261027/simulation/09-approximation.tex'

def dump(p,d):p.write_text(json.dumps(d,indent=2,default=lambda v:str(v) if isinstance(v,Q) else str(v))+'\n')

def importance(target,proposal,loss):
    if set(target)!=set(proposal) or set(target)!=set(loss):raise ValueError('support_keys')
    if any(x<0 for x in target.values()) or any(x<0 for x in proposal.values()):raise ValueError('negative_mass')
    if sum(target.values())!=1 or sum(proposal.values())!=1:raise ValueError('mass_not_one')
    if any(target[x]>0 and proposal[x]==0 for x in target):raise ValueError('uncovered_target_support')
    return {x:target[x]/proposal[x] for x in target if proposal[x]>0}

def upper_zero(n,alpha,iterations=80):
    if n<=0 or not 0<alpha<1:raise ValueError('invalid_zero_event_design')
    lo,hi=Q(0),Q(1)
    for _ in range(iterations):
        mid=(lo+hi)/2
        if (1-mid)**n>alpha:lo=mid
        else:hi=mid
    return lo,hi

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True,type=Path)
    out=ap.parse_args().output.resolve();out.mkdir(exist_ok=False);start=time.monotonic()
    checks=[];calculations={};solver=[];formulas=[]
    def ck(name,actual,expected):checks.append(dict(name=name,passed=actual==expected,actual=actual,expected=expected))
    def refuses(name,fn,expected):
        try:fn()
        except ValueError as e:ck(name,str(e),expected)
        else:ck(name,'accepted',expected)
    # F052: two fixed systematic offsets are explicit cases, never random draws.
    family={'common':Q(999,1000),'rare':Q(1,1000)};before=deepcopy(family)
    scenarios=[]
    for label,offset,rare_count in [('lost',Q(1,200),0),('retained',Q(19,2000),1)]:
        ordinates=[offset+Q(i,100) for i in range(100)]
        types=['common' if u<family['common'] else 'rare' for u in ordinates]
        weights=[Q(1,100)]*100
        ess=1/sum(w*w for w in weights)
        absent=sorted(set(family)-set(types))
        ck(label+'/valid ordinates',all(0<=x<1 for x in ordinates),True)
        ck(label+'/rare count',types.count('rare'),rare_count)
        ck(label+'/weight ESS',ess,Q(100))
        ck(label+'/underlying family preserved',family,before)
        ck(label+'/missing support audit',absent,['rare'] if label=='lost' else [])
        histories=[(x,x,x) for x in types]
        ck(label+'/static type never redrawn',all(len(set(h))==1 for h in histories),True)
        scenarios.append(dict(label=label,offset=offset,ordinates=ordinates,types=types,weights=weights,ESS=ess,unique_types=len(set(types)),absent_types=absent,retained_family=family,interpretation='Deterministic possible resampling case; no posterior or exact-support claim'))
    ck('high ESS cannot certify full family',scenarios[0]['ESS']==100 and bool(scenarios[0]['absent_types']),True)
    ck('wrong replacement deletes feasible rare type',set(scenarios[0]['types'])==set(family),False)
    calculations['resampling']=scenarios
    # F053: change of measure, all two-outcome sums exactly enumerated.
    target={'calm':Q(999,1000),'tail':Q(1,1000)};loss={'calm':Q(0),'tail':Q(1000)}
    exact=sum(target[x]*loss[x] for x in target)
    ck('target expected loss',exact,Q(1))
    proposals=[]
    for tail in [Q(1,1000),Q(1,10),Q(1,2),Q(999,1000)]:
        proposal={'calm':1-tail,'tail':tail};weights=importance(target,proposal,loss)
        ck('normalization/'+str(tail),sum(proposal[x]*weights[x] for x in proposal),Q(1))
        weighted=sum(proposal[x]*weights[x]*loss[x] for x in proposal)
        ck('exact weighted expectation/'+str(tail),weighted,exact)
        proposals.append(dict(proposal=proposal,weights=weights,weighted_expectation=weighted,unweighted_expectation=sum(proposal[x]*loss[x] for x in proposal)))
    proposal={'calm':Q(9,10),'tail':Q(1,10)};weights=importance(target,proposal,loss)
    ck('oversampled tail weight',weights['tail'],Q(1,100))
    ck('oversampled calm weight',weights['calm'],Q(111,100))
    ck('unweighted oversampling loss',proposals[1]['unweighted_expectation'],Q(100))
    pairs=[];ordinary_mean=Q(0);normalized_mean=Q(0)
    for sample in product(target,repeat=2):
        probability=proposal[sample[0]]*proposal[sample[1]]
        ordinary=sum(weights[x]*loss[x] for x in sample)/2
        normalized=sum(weights[x]*loss[x] for x in sample)/sum(weights[x] for x in sample)
        ordinary_mean+=probability*ordinary;normalized_mean+=probability*normalized
        pairs.append(dict(sample=sample,probability=probability,ordinary=ordinary,self_normalized=normalized))
    ck('two-draw ordinary expectation',ordinary_mean,exact)
    ck('two-draw normalization changes expectation',normalized_mean==exact,False)
    ck('two-draw enumeration mass',sum(x['probability'] for x in pairs),Q(1))
    refuses('proposal misses rare support',lambda:importance(target,{'calm':Q(1),'tail':Q(0)},loss),'uncovered_target_support')
    refuses('proposal not normalized',lambda:importance(target,{'calm':Q(1),'tail':Q(1,10)},loss),'mass_not_one')
    refuses('proposal negative mass',lambda:importance(target,{'calm':Q(11,10),'tail':Q(-1,10)},loss),'negative_mass')
    calculations['importance']=dict(target=target,loss=loss,proposals=proposals,two_draws=pairs,ordinary_expectation=ordinary_mean,self_normalized_expectation=normalized_mean)
    # F054: exact binomial calculation; no generated sample or iid inference.
    n=100;p=Q(1,1000);alpha=Q(1,20);none=(1-p)**n
    ck('no-event probability near .905',Q(904,1000)<none<Q(906,1000),True)
    ck('no-event loss estimate is not expected loss',Q(0)==exact,False)
    lo,hi=upper_zero(n,alpha)
    ck('zero-event upper lower sign',(1-lo)**n>alpha,True)
    ck('zero-event upper upper sign',(1-hi)**n<=alpha,True)
    ck('root bracket width',hi-lo,Q(1,2**80))
    ck('zero-event upper about .0295',Q(295,10000)<lo<hi<Q(296,10000),True)
    ck('true example p below upper',p<lo,True)
    ck('one-event-trial closed-form boundary',upper_zero(1,alpha)[0]<1-alpha<=upper_zero(1,alpha)[1],True)
    refuses('zero trials invalid design',lambda:upper_zero(0,alpha),'invalid_zero_event_design')
    refuses('zero alpha invalid design',lambda:upper_zero(n,Q(0)),'invalid_zero_event_design')
    pmf=[Q(comb(n,k))*p**k*(1-p)**(n-k) for k in range(n+1)]
    ck('complete binomial mass',sum(pmf),Q(1))
    ck('binomial expected event count',sum(k*mass for k,mass in enumerate(pmf)),n*p)
    # U(k)<p iff F_p(k)<alpha for k<n by monotonicity of the binomial CDF.
    # At this small supplied p even U(0)>p; no general coverage proof is claimed.
    cdf=Q(0);noncoverage=Q(0);noncovering=[]
    for k,mass in enumerate(pmf):
        cdf+=mass
        if k<n and cdf<alpha:noncoverage+=mass;noncovering.append(k)
    ck('supplied-p exact coverage',1-noncoverage,Q(1))
    ck('supplied-p coverage at least nominal',noncoverage<=alpha,True)
    calculations['rare_event']=dict(n=n,p=p,severity=1000,expected_loss=exact,no_events_probability=none,no_events_decimal=float(none),alpha=alpha,zero_event_upper_bracket=[lo,hi],upper_decimal=float((lo+hi)/2),bracket_iterations=80,pmf=pmf,noncovering_counts=noncovering,coverage=1-noncoverage,sampling_assumptions='Fixed n; iid Bernoulli under supplied probability. No observed sample, dependence, adaptive stopping or model-error coverage.')
    # F055: interval guard decision, including attained threshold equality.
    intervals=[('above',Q(101),Q(103),'safe'),('below',Q(97),Q(99),'unsafe'),('straddle',Q(99),Q(101),'unresolved'),('lower touches',Q(100),Q(102),'safe'),('upper touches',Q(98),Q(100),'unresolved'),('exact threshold',Q(100),Q(100),'safe'),('exact below',Q(999,10),Q(999,10),'unsafe')]
    capacity=z3.Real('capacity')
    classifications=[]
    for name,lower,upper,expected in intervals:
        problem=Problem(name,'Supplied certified error interval, required funding100')
        problem.variables=dict(capacity=capacity);problem.add('lower',capacity>=q(lower));problem.add('upper',capacity<=q(upper));problem.outputs=dict(capacity=capacity)
        result={}
        for label,condition in [('can_fund',capacity>=100),('can_fail',capacity<100)]:
            r=solve(problem,BUDGET,extra=[condition]);solver.append(dict(id=name+'/'+label,result=r));result[label]=r['feasibility']
            formulas.append(dict(id=name+'/'+label,constraints=[dict(label=k,expression=v.sexpr()) for k,v in problem.constraints],extra=condition.sexpr()))
            ck(name+'/'+label+'/decided',r['feasibility'] in ['Feasible','Infeasible'],True)
        status='safe' if result['can_fail']=='Infeasible' else ('unsafe' if result['can_fund']=='Infeasible' else 'unresolved')
        ck(name+'/classification',status,expected)
        direct='safe' if lower>=100 else ('unsafe' if upper<100 else 'unresolved')
        ck(name+'/independent endpoint classification',status,direct)
        classifications.append(dict(name=name,lower=lower,upper=upper,status=status,results=result))
    ck('small point error false positive',Q(1002,10)>=100 and Q(999,10)<100 and abs(Q(1002,10)-Q(999,10))<=1,True)
    ck('small point error false negative',Q(998,10)<100 and Q(1001,10)>=100 and abs(Q(998,10)-Q(1001,10))<=1,True)
    unknown=solve(problem,replace(BUDGET,max_cells=0),extra=[capacity>=100])
    solver.append(dict(id='zero budget guard',result=unknown))
    ck('zero budget unknown',unknown['feasibility'],'Unknown')
    ck('zero budget retains formula',bool(unknown['coverage']['unvisited']['retained_formula']),True)
    ck('zero budget not complete',unknown['coverage'].get('complete'),False)
    calculations['thresholds']=classifications
    fm=ROOT/'data/accounting-master/unified-program-20261028/failure-map.json'
    originals=[r['original_row'] for r in json.loads(fm.read_text())['rows'] if r['original_row']['id'] in ['SIM-F052','SIM-F053','SIM-F054','SIM-F055']]
    ck('exact original cases',[r['discriminating_case'] for r in originals],['Rare static contract type is removed without evidence','Target tail .001 sampled at .1','Loss1000 with probability.001 and100 draws','Capacity estimate straddles required funding'])
    failed=[c for c in checks if not c['passed']]
    verification=dict(status='fail' if failed else 'pass',checks=len(checks),solver_cases=len(solver),failed=[x['name'] for x in failed],original_rows=[r['id'] for r in originals],random_simulation=False,empirical_probability_admission=False,default_change=False)
    for name,value in [('verification',verification),('checks',checks),('calculations',calculations),('solver-results',solver),('formulae',formulas),('original-rows',originals)]:dump(out/(name+'.json'),value)
    sources={ROOT/PLAN,ROOT/SOURCE,fm,Path(__file__)}
    sources.update(Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().is_relative_to(ROOT))
    dump(out/'run-manifest.json',dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=dict(python=platform.python_version(),z3=z3.get_version_string()),cpu_gpu='CPU-only exact rational arithmetic and SMT; no GPU imports',random_seeds='N/A no random experiment',data_version='Supplied original F052/053/054/055 examples',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plan_file=PLAN,result_file=str((H/'result.md').relative_to(ROOT)),source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(sources)}))
    (out/'check.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(verification));return bool(failed)

if __name__=='__main__':raise SystemExit(main())
