from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json,hashlib,sys,time,platform
D=Path(__file__).resolve().parent;R=D.parents[3];clock=time.monotonic();rows=[]
def ck(name,actual,expected):rows.append({'name':name,'actual':str(actual),'expected':str(expected),'pass':actual==expected})
def failure_bound(ds):
 p=F(1)
 for d in ds:p*=1-d
 return 1-p
# A common time-zero observation but unrelated initial state laws: no transition
# error can bound a loss that already differs at time zero. Deterministic values.
ck('initial_omission_loss_difference',abs(F(1)-F(0)),F(1))
ck('initial_omission_transition_only_bound',failure_bound([F(0)]),F(0))
ck('initial_omission_invalidates_literal_bound',F(1)>failure_bound([F(0)]),True)
# All observed outputs match, but the requested hidden-state loss is not among
# them. A common bounded loss of the respective hidden states can still differ.
ck('unpreserved_hidden_loss_difference',abs(F(1)-F(0)),F(1))
ck('unpreserved_hidden_loss_fails_zero_bound',F(1)>F(0),True)
# Same initial related state, shared loss, three transitions: old example intact.
ck('original_three_date_bound',12*failure_bound([F(1,20)]*3),F(3423,2000))
# Exact independent first-mismatch enumeration, including date zero.
for i,ds in enumerate([[F(0)],[F(1)],[F(1,10),F(1,20),F(1,5)],[F(0),F(1,20),F(1,20),F(1,20)],[F(1,3),F(0),F(1),F(1,7)]]):
 first=F(0);survival=F(1)
 for d in ds:first+=survival*d;survival*=1-d
 ck('first_mismatch_partition_'+str(i),first+survival,F(1))
 ck('product_bound_attained_'+str(i),first,failure_bound(ds))
 ck('union_bound_'+str(i),first<=sum(ds),True)
# Extremal matched-loss / unmatched-loss allocation saturates eta*(1-p)+B*p.
p=failure_bound([F(1,10),F(1,20),F(1,5)]);B=F(12);eta=F(1,4)
actual=(1-p)*eta+p*B
ck('initial_and_transition_failure',p,F(79,250))
ck('matched_loss_generalized_bound',actual,eta*(1-p)+B*p)
ck('looser_eta_plus_bound',actual<=eta+B*p,True)
# Exhaustive rational survival hazards: allowed actual hazards no larger than
# the supplied maxima. This checks the recurrence at zero surviving mass too.
for n,ds in enumerate(product([F(0),F(1,2),F(1)],repeat=4)):
 bound=failure_bound(ds)
 for factor in [F(0),F(1,2),F(1)]:
  hazards=[d*factor for d in ds];p_exact=failure_bound(hazards)
  ck('survival_'+str(n)+'_'+str(factor),p_exact<=bound,True)
# Threshold atom: vanishing cash error alone does not control crossing.
for n in [10,100,1000]:
 eps=F(1,n);ck('threshold_atom_'+str(n),abs(int(-eps<0)-int(eps<0)),1)
# Common-policy regret at the sharp two-epsilon scale; both approximate
# policies tied, selecting one can incur two epsilon in the original model.
eps=F(3,7);J=[F(0),2*eps];approx=[eps,eps]
ck('common_policy_uniform_error',max(abs(x-y) for x,y in zip(J,approx)),eps)
ck('common_policy_regret',J[1]-min(J),2*eps)
source=R/'docs/design/proposal/manuscript-release-prep-v552r1-20261027/simulation/lit-09-approximation-4.tex'
result={'question':'Necessary initial-state and loss-matching conditions for finite coupling bound','passed':all(x['pass'] for x in rows),'checks':rows,'source':str(source.relative_to(R)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'command':[sys.executable,str(Path(__file__).resolve())],'environment':{'python':sys.version,'platform':platform.platform(),'gpu':'Not used; standard-library exact arithmetic only','seed':'N/A deterministic exhaustive rational fixtures'},'seconds':time.monotonic()-clock,'plan':str((D/'plan.md').relative_to(R)),'limits':'Exact constructed examples and recurrence checks, not a proof for empirically estimated kernels or arbitrary unbounded financial loss.'}
(D/'exact-results.json').write_text(json.dumps(result,indent=2)+chr(10));print(json.dumps({'passed':result['passed'],'checks':len(rows),'source_sha256':result['source_sha256']}))
