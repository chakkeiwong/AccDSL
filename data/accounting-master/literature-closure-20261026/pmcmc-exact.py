"""Exact diagnostic; no stochastic sampler or production default is changed."""
from fractions import Fraction as F
from pathlib import Path
import json,time,hashlib,sys,platform
start=time.monotonic(); p=Path(__file__).resolve().parent
checks=[]
def check(name,condition,detail):
 checks.append(dict(id=name,passed=bool(condition),detail=str(detail)))
 assert condition,(name,detail)
# Equal prior and equal true likelihood. Type0 estimator is .5 or1.5;
# type1 estimator is1. All are positive, with mean1.
states=[(0,F(1,2)),(0,F(3,2)),(1,F(1))]
noise={0:[(F(1,2),F(1,2)),(F(3,2),F(1,2))],1:[(F(1),F(1))]}
for t in [0,1]:check('unbiased_'+str(t),sum(w*q for w,q in noise[t])==1,noise[t])
P=[[F(0) for _ in states] for _ in states]
for i,(theta,w) in enumerate(states):
 for proposed_w,q in noise[1-theta]:
  j=states.index((1-theta,proposed_w));a=min(F(1),proposed_w/w)
  P[i][j]+=q*a;P[i][i]+=q*(1-a)
mu=[F(1,8),F(3,8),F(1,2)]
for i,row in enumerate(P):check('rowsum_'+str(i),sum(row)==1,row)
for i in range(3):
 for j in range(3):check('detailed_balance_'+str(i)+'_'+str(j),mu[i]*P[i][j]==mu[j]*P[j][i],(i,j))
for j in range(3):check('invariance_'+str(j),sum(mu[i]*P[i][j] for i in range(3))==mu[j],mu[j])
check('true_type_marginal',mu[0]+mu[1]==mu[2]==F(1,2),mu)
check('positive_two_step_reachability',all(P[i][j]+sum(P[i][k]*P[k][j] for k in range(3))>0 for i in range(3) for j in range(3)),P)
check('aperiodic_self_loop',P[1][1]>0,P[1][1])
# Wrong alternative: redraw current noise at every iteration as well as candidate.
a01=sum(q0*q1*min(F(1),w1/w0) for w0,q0 in noise[0] for w1,q1 in noise[1])
a10=sum(q0*q1*min(F(1),w0/w1) for w0,q0 in noise[0] for w1,q1 in noise[1])
wrong1=a01/(a01+a10)
check('refresh_rates',a01==F(5,6) and a10==F(3,4),(a01,a10))
check('refresh_stationary_mass',wrong1==F(10,19),wrong1)
check('refresh_bias',wrong1-F(1,2)==F(1,38),wrong1-F(1,2))
check('retain_high_on_rejection',P[1][1]==F(1,3),P[1][1])
result=dict(date='2026-10-26',status='PASS',checks=checks,states=[[t,str(w)] for t,w in states],transition=[[str(x) for x in r] for r in P],extended_stationary=[str(x) for x in mu],target_type1='1/2',refresh_type1=str(wrong1),absolute_bias='1/38',scope='Exact three-state diagnostic. Not a PMCMC implementation, mixing-rate result or empirical comparison.')
(p/'pmcmc-exact-results.json').write_text(json.dumps(result,indent=2)+chr(10))
manifest=dict(command='python3 data/accounting-master/literature-closure-20261026/pmcmc-exact.py',git_commit='Unavailable: unusable .git; no initialization',environment=sys.version,platform=platform.platform(),cpu_gpu='CPU-only rational arithmetic; no GPU detection or imports',seeds='N/A: exact enumeration',wall_seconds=time.monotonic()-start,plan='docs/plans/accounting-literature-closure-20261026.md; plan-review.md particle-MCMC continuation',result='pmcmc-exact-results.json',script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
(p/'pmcmc-exact-manifest.json').write_text(json.dumps(manifest,indent=2)+chr(10))
print(json.dumps(dict(status='PASS',checks=len(checks),target_type1='1/2',wrong_type1=str(wrong1),bias='1/38')))
