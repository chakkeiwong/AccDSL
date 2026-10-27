"""Exact extended-target exchange and corrected-evidence support diagnostic."""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json, os, platform, time

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
START=time.monotonic()
checks=[]
def fmt(q):return str(q.numerator)+'/'+str(q.denominator)
def check(name,condition,detail):
    checks.append({'id':name,'passed':bool(condition),'detail':str(detail)})
    if not condition:raise AssertionError((name,detail))
def vector(values):return [fmt(v) for v in values]
prior={0:F(1,2),1:F(1,2)}
old={0:[(F(1,2),F(1,2)),(F(3,2),F(1,2))],1:[(F(1),F(1))]}
new={0:[(F(1,4),F(1,2)),(F(7,4),F(1,2))],1:[(F(1),F(1))]}
states=[(th,z) for th in new for z,p in new[th]]
desired={(th,z):prior[th]*z*p for th in new for z,p in new[th]}
weighted={s:F() for s in states}; unweighted={s:F() for s in states}; exchanges=[]
for theta in old:
    check('old_unbiased_'+str(theta),sum(z*p for z,p in old[theta])==1,old[theta])
    check('new_unbiased_'+str(theta),sum(z*p for z,p in new[theta])==1,new[theta])
    for a,ma in old[theta]:
        for b,mb in new[theta]:
            proposal_mass=prior[theta]*a*ma*mb
            weight=b/a
            weighted[(theta,b)]+=proposal_mass*weight
            unweighted[(theta,b)]+=proposal_mass
            exchanges.append({'theta':theta,'old_estimate':fmt(a),'new_estimate':fmt(b),
              'proposal_mass':fmt(proposal_mass),'exchange_weight':fmt(weight),'weighted_mass':fmt(proposal_mass*weight)})
for s in states:check('exact_new_joint_'+str(s),weighted[s]==desired[s],(weighted[s],desired[s]))
check('new_target_normalized',sum(weighted.values())==1,weighted)
check('unweighted_joint_wrong',unweighted!=desired,unweighted)
check('unweighted_theta_initially_correct',sum(v for (th,z),v in unweighted.items() if th==1)==F(1,2),'Do not claim immediate theta bias')

# Independent generic PMMH construction from proposal masses and ratios.
transition=[]
for theta,z in states:
    row={s:F() for s in states}
    for proposed,prob in new[1-theta]:
        accepted=prob*min(F(1),proposed/z)
        row[(1-theta,proposed)]+=accepted
        row[(theta,z)]+=prob-accepted
    transition.append([row[s] for s in states])
def step(mass):
    return {s:sum(mass[states[i]]*transition[i][j] for i in range(len(states))) for j,s in enumerate(states)}
after_correct=step(weighted);after_wrong=step(unweighted)
check('pmmh_invariance',after_correct==desired,after_correct)
for i in range(len(states)):
    check('row_normalization_'+str(i),sum(transition[i])==1,transition[i])
    for j in range(len(states)):
        check('detailed_balance_'+str(i)+'_'+str(j),desired[states[i]]*transition[i][j]==desired[states[j]]*transition[j][i],'exact')
check('wrong_exchange_then_move_theta',sum(v for (th,z),v in after_wrong.items() if th==1)==F(65,112),after_wrong)
check('wrong_exchange_bias',F(65,112)-F(1,2)==F(9,112),'one move bias; no stationary-bias claim')

# Replacing an old deterministic observation, not multiplying new evidence.
original={0:F(1,2),1:F(1,2)}
old_likelihood={0:F(1),1:F(0)}
replacement={0:F(1,4),1:F(3,4)}
def normalize(m):
    z=sum(m.values());return {k:v/z for k,v in m.items()}
old_posterior=normalize({k:original[k]*old_likelihood[k] for k in original})
corrected=normalize({k:original[k]*replacement[k] for k in original})
wrong_conjunction=normalize({k:old_posterior[k]*replacement[k] for k in original})
check('corrected_support_restored',corrected=={0:F(1,4),1:F(3,4)},corrected)
check('reweighting_restricted_support_cannot_restore',wrong_conjunction=={0:F(1),1:F(0)},wrong_conjunction)
check('revision_likelihood_ratio_undefined',old_likelihood[1]==0 and replacement[1]>0,'Absolute continuity fails at theta=1')

sources=[
 'data/accounting-master/literature-closure-20261026/sources/smc2.pdf',
 'data/accounting-master/literature-closure-20261026/text/smc2.txt',
 'data/accounting-master/literature-closure-20261026/sources/smc-particles_smc_samplers.py',
 'data/accounting-master/literature-closure-20261026/sources/smc-particles_mcmc.py',
 'data/accounting-master/literature-closure-20261026/pmcmc-dependency.md']
result={'status':'PASS','checks':checks,'states':[(th,fmt(z)) for th,z in states],
 'desired_new_joint':vector([desired[s] for s in states]),
 'weighted_joint':vector([weighted[s] for s in states]),
 'unweighted_joint':vector([unweighted[s] for s in states]),
 'pmmh_transition':[vector(row) for row in transition],
 'after_wrong_exchange_and_one_move':vector([after_wrong[s] for s in states]),
 'exchange_rows':exchanges,'revised_posterior':{str(k):fmt(v) for k,v in corrected.items()},
 'scope':'Exact finite extended-target argument and static source audit; not execution of particles/SMC2 or a mixing/performance claim.'}
(OUT/'smc2-exchange-results.json').write_text(json.dumps(result,indent=2)+'\n')
manifest={'status':'PASS','command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/gap-program-20261026/smc2_exchange.py',
 'plan':'docs/plans/accounting-gap-program-20261026.md','result':'data/accounting-master/gap-program-20261026/smc2-transfer.md',
 'git':'unusable; no commit invented','environment':{'python':platform.python_version(),'platform':platform.platform(),'CUDA_VISIBLE_DEVICES':os.getenv('CUDA_VISIBLE_DEVICES'),'gpu':'intentionally hidden; no GPU imports'},
 'seeds':'N/A exact rational enumeration','data_version':'authored finite auxiliary laws and retained arXiv v3/pinned source',
 'wall_seconds':time.monotonic()-START,'artifacts':['smc2-exchange-results.json'],
 'source_sha256':{s:sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},
 'script_sha256':sha256(Path(__file__).read_bytes()).hexdigest()}
(OUT/'smc2-run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'status':'PASS','checks':len(checks),'wrong_theta_after_one_move':'65/112','bias':'9/112'}))
