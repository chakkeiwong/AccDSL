"""Exact diagnostic cases; no stochastic performance or simulator acceptance."""
from fractions import Fraction as F
from pathlib import Path
import json, hashlib, platform, time
start=time.monotonic();p=Path(__file__).resolve().parent;rows=[]
def ck(name,ok,actual,expected):
    rows.append(dict(id=name,passed=bool(ok),actual=str(actual),expected=str(expected)))
    if not ok:raise AssertionError(rows[-1])
# TC-VAE v1 Theorem3.1: closed convex H={clip(identity,0,1)}.
# T=1, mu=delta1, nu=delta0, Q(x,h)=h, uniform x-Lipschitz L=0.
mu_value=F(1);nu_value=F(0);rhs=F(0)
ck('convex_singleton_policy_value_gap',mu_value-nu_value==1,mu_value-nu_value,1)
ck('stated_bound_fails_without_transfer_closure',mu_value-nu_value>rhs,(mu_value-nu_value,rhs),'1 > 0')
ck('transferred_action_outside_policy_class',F(0)!=F(1),0,'H(1)=1')
# Hart–Moore1991 Example1. Nonnegative current payments; zero discount.
for w in [F(0),F(1,2),F(1),F(2)]:
    current_capacity=w+2;last_credible=F(13);outside=F(16)
    feasible=current_capacity+last_credible>=outside
    ck('hart_feasibility_w_'+str(w),feasible==(w>=1),feasible,w>=1)
    if feasible:
        initial=F(1);first=F(2);last=F(13)
        ck('hart_cash_w_'+str(w),w-initial>=0 and w-initial+2-first>=0 and w-initial+2-first+26-last>=0,(w-initial,w-initial+2-first,w-initial+2-first+26-last),'all nonnegative')
        ck('hart_creditor_w_'+str(w),initial+first+last==outside,initial+first+last,outside)
ck('hart_positive_surplus_insufficient',F(28)>F(16) and F(2)+F(13)<F(16),(28,16,15),'continuation surplus but infeasible promises')
# Square-wave kernels: on each alternating half-cell P(U=1|y)=1 or0.
# Kronecker kernel on {0,1}: squared MMD to fair mixture=1/2 everywhere.
for n in [1,2,4,16,64]:
    mass=F(0);first_moment=F(0)
    for k in range(n):
        a=F(2*k,2*n);b=F(2*k+1,2*n)
        mass+=b-a;first_moment+=(b*b-a*a)/2
    ck('kernel_marginal_'+str(n),mass==F(1,2),mass,F(1,2))
    ck('kernel_weak_linear_moment_'+str(n),first_moment-F(1,4)==-F(1,8*n),first_moment-F(1,4),-F(1,8*n))
    ck('kernel_strong_squared_'+str(n),F(1,2)>0,F(1,2),'constant nonzero')
# Off-support policy: behavior always A, both models match; B loss differs.
P={'A':F(1),'B':F(100)};Q={'A':F(1),'B':F(0)}
ck('behavior_policy_agrees',P['A']==Q['A'],(P['A'],Q['A']),'same')
chosen=min(Q,key=Q.get)
ck('learned_policy_fails_off_support',chosen=='B' and P[chosen]-min(P.values())==99,P[chosen]-min(P.values()),99)
out=dict(status='PASS',checks=rows,scope='Exact finite counterexamples and source-example arithmetic; no empirical or general simulator validation.',manifest=dict(command='python3 data/accounting-master/literature-closure-20261026/recent-method-cases.py',python=platform.python_version(),git='unusable repository marker; no commit invented',cpu='exact rational CPU arithmetic; no ML/GPU imports',seed='N/A exact',data='declared synthetic/source example',plan='docs/plans/accounting-literature-closure-20261026.md',wall_seconds=time.monotonic()-start))
(p/'recent-method-results.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(status=out['status'],checks=len(rows))))
