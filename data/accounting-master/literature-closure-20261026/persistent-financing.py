"""Finite reference methods for persistent inference and price-policy consistency."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json,platform,time
p=Path(__file__).resolve().parent;start=time.monotonic();checks=[]
def ck(name,condition,detail):
    checks.append(dict(id=name,passed=bool(condition),detail=str(detail)))
    if not condition:raise AssertionError((name,detail))
def norm(m):
    z=sum(m.values(),F())
    if z==0:return {'status':'evidence_conflict','mass':m}
    return {'status':'ok','mass':{k:v/z for k,v in m.items()},'normalizer':z}
def transition(th,x,y):return (F(3,4) if th==0 else F(1,2)) if x==y else (F(1,4) if th==0 else F(1,2))
def likelihood(obs,state):return F(1) if obs is None else (F(4,5) if obs==state else F(1,5))
def filtering(prior,obs,admit=(0,1)):
    initial=norm({(th,x):w*int(th in admit) for (th,x),w in prior.items()})
    if initial['status']!='ok':return initial
    m=initial['mass']
    for y in obs:
        pred={(th,z):sum(m.get((th,x),F())*transition(th,x,z) for x in [0,1]) for th,z in product([0,1],repeat=2)}
        step=norm({(th,z):w*likelihood(y,z) for (th,z),w in pred.items()})
        if step['status']!='ok':return step
        m=step['mass']
    return dict(status='ok',mass=m)
def enumerate_paths(prior,obs,admit=(0,1)):
    m={(th,x):F(0) for th,x in product([0,1],repeat=2)}
    for th in [0,1]:
        for xs in product([0,1],repeat=len(obs)+1):
            w=prior[(th,xs[0])]*int(th in admit)
            for t,y in enumerate(obs):w*=transition(th,xs[t],xs[t+1])*likelihood(y,xs[t+1])
            m[(th,xs[-1])]+=w
    return norm(m)
priors=[{(th,x):(q if th==0 else 1-q)/2 for th,x in product([0,1],repeat=2)} for q in [F(1,1000),F(1,4),F(1,2),F(3,4)]]
for i,prior in enumerate(priors):
    for obs in product([None,0,1],repeat=3):
        a=filtering(prior,obs);b=enumerate_paths(prior,obs)
        ck('filter_vs_paths_'+str(i)+'_'+str(obs),a['mass']==b['mass'],obs)
        ck('posterior_normalized_'+str(i)+'_'+str(obs),sum(a['mass'].values())==1,'unit mass')
        ck('rare_type_retained_'+str(i)+'_'+str(obs),all(v>0 for v in a['mass'].values()),'positive support retained without resampling')
    a=filtering(prior,[None]*3)['mass']
    ck('uninformative_type_odds_'+str(i),sum(a[(0,x)] for x in [0,1])==sum(prior[(0,x)] for x in [0,1]),a)
prior=priors[2];obs=(1,None,0)
old=filtering(prior,obs,admit=(0,))['mass'];revised=filtering(prior,obs)['mass']
ck('revision_reopens_type',sum(old[(1,x)] for x in [0,1])==0 and sum(revised[(1,x)] for x in [0,1])>0,(old,revised))
ck('revision_replays_original_prior',revised==enumerate_paths(prior,obs)['mass'],'recompute all still-active evidence from preserved prior')
ck('impossible_hard_evidence_is_conflict',filtering(prior,obs,admit=())['status']=='evidence_conflict','no fallback weights')
# Unweighted support propagation retains joint (theta,state) pairs and never invents odds.
possible=set(product([0,1],repeat=2))
for y in obs:possible={(th,z) for th,x in possible for z in [0,1] if transition(th,x,z)>0 and likelihood(y,z)>0}
ck('unweighted_support_preserved',possible==set(product([0,1],repeat=2)),sorted(possible))
# Explicit prior-set interval, with a single binary likelihood .8 versus .2.
post=lambda q:4*q/(1+3*q)
ck('prior_interval_lower',post(F(1,4))==F(4,7),post(F(1,4)))
ck('prior_interval_upper',post(F(3,4))==F(12,13),post(F(3,4)))
# Funding: existing senior face40, new junior face80, project investment60.
# Cash proceeds P, shortfall60-P subscribed by old shareholders if feasible.
# Safe estate100; risk estate20/220, equal weights. Total estate is distributed once.
rf=F(21,20);senior=F(40);junior=F(80);cost=F(60)
policies={'safe':[(F(1),F(100))],'risk':[(F(1,2),F(20)),(F(1,2),F(220))]}
def allocation(estate):
    s=min(estate,senior);j=min(max(estate-s,0),junior);e=max(estate-s-j,0)
    return s,j,e
values={}
for policy,states in policies.items():
    v=[F(0)]*3
    for i,(pr,estate) in enumerate(states):
        a=allocation(estate)
        ck('estate_conservation_'+policy+'_'+str(i),sum(a)==estate and min(a)>=0,a)
        ck('priority_'+policy+'_'+str(i),a[1]==0 or a[0]==senior,a)
        for k in range(3):v[k]+=pr*a[k]/rf
    values[policy]=v
consistent=[];candidate=[]
for intended,v in values.items():
    proceeds=v[1]
    # At a posted price proceeds is fixed; management compares all available policies.
    owner_values={k:vv[2]-(cost-proceeds) for k,vv in values.items()}
    best=max(owner_values.values());responses=[k for k,u in owner_values.items() if u==best]
    lender_gap={k:values[k][1]-proceeds for k in responses}
    if intended in responses:consistent.append(intended)
    candidate.append(dict(intended=intended,proceeds=str(proceeds),best_responses=responses,owner_values={k:str(v) for k,v in owner_values.items()},lender_gap={k:str(v) for k,v in lender_gap.items()}))
ck('safe_quote_undermined',candidate[0]['best_responses']==['risk'],candidate[0])
ck('safe_quote_lender_gap',values['risk'][1]-values['safe'][1]==-F(400,21),values['risk'][1]-values['safe'][1])
ck('only_pure_consistent_policy',consistent==['risk'],consistent)
ck('risk_consistent_price',values['risk'][1]==F(800,21),values['risk'][1])
wealth=F(20);required=cost-values['risk'][1]
ck('equilibrium_quote_funding_refusal',required>wealth,(required,wealth))
ck('commitment_changes_cash_feasibility',cost-values['safe'][1]<=wealth,(cost-values['safe'][1],wealth))
ck('safe_commitment_owner_participation_fails',values['safe'][2]-(cost-values['safe'][1])<0,'cash affordability alone is not voluntary participation')
# Separate restructuring participation: continuation estate70, outside50/20.
# Offer45/25 conserves value but senior refuses;50/20 meets both.
outside=(F(50),F(20));bad=(F(45),F(25));good=(F(50),F(20))
ck('aggregate_surplus_not_participation',sum(bad)==70 and bad[0]<outside[0],bad)
ck('participation_feasible_allocation',sum(good)==70 and all(a>=b for a,b in zip(good,outside)),good)
# If mandatory fee1 reduces estate to69, both outside options cannot be met.
ck('restructuring_fee_can_destroy_feasibility',F(69)<sum(outside),(69,sum(outside)))
# No unique bargaining solution is inferred from feasibility.
result=dict(status='PASS',checks=checks,financing=candidate,financing_required_owner_cash=str(required),scope='Finite exact reference algorithms; no empirical priors, legal insolvency rules or general equilibrium existence claim',manifest=dict(command='python3 data/accounting-master/literature-closure-20261026/persistent-financing.py',python=platform.python_version(),git='unusable; no commit invented',cpu='standard-library exact rational arithmetic; no GPU imports',seed='N/A exact enumeration',data='authored finite models',wall_seconds=time.monotonic()-start,plan='docs/plans/accounting-literature-closure-20261026.md'))
(p/'persistent-financing-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status='PASS',checks=len(checks),financing=candidate,required=str(required))))
