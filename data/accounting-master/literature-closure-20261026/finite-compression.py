"""Exact finite reference; conditional TV bound, not learned-model validation."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json,platform,time
p=Path(__file__).resolve().parent;start=time.monotonic();checks=[]
def ck(name,ok,detail):
    checks.append(dict(id=name,passed=bool(ok),detail=detail))
    if not ok:raise AssertionError((name,detail))
# Hidden theta persists throughout. Controller observes cash c, not theta.
# One unnecessary tag k is removed; it changes neither law nor action set.
# Discrete borrowing a in {0,1}; cost and default flag are part of each outcome.
# All values/probabilities are synthetic, declared, rational.
T=3;delta=F(1,20);B=F(12)
def kernel(theta,c,a,tag,approx=False):
    bad=F(1+theta,4)+(delta if approx else 0)
    out={}
    for expense,prob in [(1,1-bad),(3,bad)]:
        cash=c+a-expense;default=cash<0;next_c=max(0,cash)
        loss=F(a)+3*int(default)
        key=(theta,next_c,next_c,int(default),loss) # state, observation and output jointly
        out[key]=out.get(key,F(0))+prob
    return out
def tv(a,b):return sum(abs(a.get(k,F(0))-b.get(k,F(0))) for k in set(a)|set(b))/2
# A policy is a rule at each date based on cash==0 versus cash>0.
# Fixed history-memory subset is deliberately declared; no full-policy claim.
policies=list(product([0,1],repeat=2*T))
def paths(theta,policy,approx=False,tag=0):
    frontier={(2,(),F(0)):F(1)}
    for t in range(T):
        nxt={}
        for (cash,hist,total),weight in frontier.items():
            a=policy[2*t+int(cash>0)]
            for (_,c,o,d,loss),pr in kernel(theta,cash,a,tag,approx).items():
                key=(c,hist+((a,o,d,loss),),total+loss)
                nxt[key]=nxt.get(key,F(0))+weight*pr
        frontier=nxt
    return {hist+(('total',total),):weight for (_,hist,total),weight in frontier.items()}
def mean(law):return sum(path[-1][1]*w for path,w in law.items())
# Exact sharing must pass for every relevant local state/action, not reports only.
for theta,c,a in product([0,1],range(3),[0,1]):
    k=kernel(theta,c,a,0);ka=kernel(theta,c,a,0,True)
    ck(f'tag_merge_{theta}_{c}_{a}',k==kernel(theta,c,a,1),'joint law exactly equal')
    ck(f'tv_bound_{theta}_{c}_{a}',tv(k,ka)<=delta,str(tv(k,ka)))
ck('persistent_type_merge_rejected',kernel(0,2,0,0)!=kernel(1,2,0,0),'same observed cash, different joint kernel')
# Coupling union bound: probability of any mismatch <=1-(1-delta)^T.
bound=B*(1-(1-delta)**T);summaries=[]
for theta in [0,1]:
    full=[];approx=[];maxerr=F(0);maxpath=F(0)
    for j,policy in enumerate(policies):
        law=paths(theta,policy);alaw=paths(theta,policy,True)
        ck(f'full_law_tag_{theta}_{j}',law==paths(theta,policy,tag=1),'complete action/observation/default/loss path')
        ck(f'probability_{theta}_{j}',sum(law.values())==1 and sum(alaw.values())==1,'both normalized')
        v=mean(law);w=mean(alaw);err=abs(v-w)
        ck(f'bounded_loss_{theta}_{j}',all(0<=path[-1][1]<=B for path in law),'total loss in [0,12]')
        ck(f'value_error_{theta}_{j}',err<=bound,str(err))
        ck(f'path_tv_{theta}_{j}',tv(law,alaw)<=1-(1-delta)**T,str(tv(law,alaw)))
        maxerr=max(maxerr,err);maxpath=max(maxpath,tv(law,alaw));full.append(v);approx.append(w)
    selected=min(range(len(policies)),key=lambda j:approx[j]);regret=full[selected]-min(full)
    ck('common_class_regret_'+str(theta),regret<=2*bound,str(regret))
    summaries.append(dict(theta=theta,policies=len(policies),max_cost_error=str(maxerr),max_path_tv=str(maxpath),uniform_cost_bound=str(bound),selected_policy=list(policies[selected]),regret=str(regret)))
# No prior is inferred. Robust choice minimizes worst loss across persistent types.
full=[[mean(paths(th,pi)) for th in [0,1]] for pi in policies]
small=[[mean(paths(th,pi,True)) for th in [0,1]] for pi in policies]
robust=lambda xs:max(xs)
chosen=min(range(len(policies)),key=lambda j:robust(small[j]))
regret=robust(full[chosen])-min(map(robust,full))
ck('unweighted_persistent_robust_regret',regret<=2*bound,str(regret))
# Type is never independently redrawn at subsequent dates. No inference of weights.
out=dict(status='PASS',checks=checks,summary=summaries,robust_regret=str(regret),assumptions=dict(horizon=T,hidden_type='fixed0 or1; no mixture inferred',initial_cash=2,actions=[0,1],shock_expenses=[1,3],full_bad_probability='(1+theta)/4',approximation_shift=str(delta),policy_class='64 deterministic rules: action indexed by date and zero/positive observed cash',loss='action +3*default each date',bound=str(bound)),manifest=dict(command='python3 data/accounting-master/literature-closure-20261026/finite-compression.py',python=platform.python_version(),git='unusable; no commit invented',cpu='exact rational enumeration; no GPU imports',seed='N/A exact',wall_seconds=time.monotonic()-start,plan='docs/plans/accounting-literature-closure-20261026.md'),scope='Finite method-transfer oracle; no production-runtime execution, universal compression rate or empirical forecast claim')
(p/'finite-compression-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(status='PASS',checks=len(checks),summary=summaries)))
