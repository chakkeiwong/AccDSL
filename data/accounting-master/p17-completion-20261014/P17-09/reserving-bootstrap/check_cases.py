"""Exact authored uncertainty examples, not a fitted bootstrap implementation."""
from fractions import Fraction as F
from collections import defaultdict
from pathlib import Path
import json,math,time
OUT=Path(__file__).resolve().parent
checks=[]
def check(name,ok,detail=None): checks.append({'name':name,'passed':bool(ok),'detail':detail})
def mean(d): return sum(x*p for x,p in d.items())
def var(d): return sum(p*(x-mean(d))**2 for x,p in d.items())
def tail(d,t): return sum(p for x,p in d.items() if x>t)
def mix(laws):
 d=defaultdict(F)
 for w,law in laws:
  for x,p in law.items():d[x]+=w*p
 return dict(d)
def total_joint(laws):
 d=defaultdict(F)
 for w,law in laws:
  for x,p in law.items():
   for y,q in law.items():d[x+y]+=w*p*q
 return dict(d)
def encode(d): return [{'value':str(x),'probability':str(p)} for x,p in sorted(d.items())]
started=time.perf_counter()
means={F(2):F(1,2),F(8):F(1,2)}
a={F(2):{F(0):F(1,2),F(4):F(1,2)},F(8):{F(4):F(1,2),F(12):F(1,2)}}
b={F(2):{F(1):F(4,5),F(6):F(1,5)},F(8):{F(6):F(4,5),F(16):F(1,5)}}
for name,models in [('A',a),('B',b)]:
 for m,law in models.items():
  check(name+':normalizes:'+str(m),sum(law.values())==1)
  check(name+':mean:'+str(m),mean(law)==m)
  check(name+':variance:'+str(m),var(law)==2*m)
law_a=mix([(p,a[m]) for m,p in means.items()]);law_b=mix([(p,b[m]) for m,p in means.items()])
check('fitted_means_mean',mean(means)==5)
check('fitted_means_variance',var(means)==9)
for name,law in [('A',law_a),('B',law_b)]:
 check(name+':predictive_mean',mean(law)==5)
 check(name+':predictive_variance',var(law)==19)
 check(name+':variance_decomposition',var(law)==sum(p*2*m for m,p in means.items())+var(means))
check('A:tail_over8',tail(law_a,8)==F(1,4))
check('B:tail_over8',tail(law_b,8)==F(1,10))
check('means_alone_wrong_tail',tail(means,8)==0)
joint=total_joint([(p,a[m]) for m,p in means.items()])
independent=total_joint([(F(1),law_a)])
check('joint_total_mean',mean(joint)==10)
check('joint_total_variance',var(joint)==56)
check('independent_marginal_total_variance',var(independent)==38)
check('lost_parameter_covariance',var(joint)-var(independent)==18)
check('same_first_two_moments_different_laws',law_a!=law_b and mean(law_a)==mean(law_b) and var(law_a)==var(law_b))
# Scope-specific source sign counterexample: X has mean abs(m).
m=F(-4);x={F(2):F(1,2),F(6):F(1,2)}
wrong={z-2*m:p for z,p in x.items()};translated={z+2*m:p for z,p in x.items()};reflected={-z:p for z,p in x.items()}
check('source_literal_negative_mean_is12',mean(wrong)==12)
check('translation_mean_is_minus4',mean(translated)==m)
check('reflection_mean_is_minus4',mean(reflected)==m)
check('negative_ODP_variance_impossible',F(2)*m<0)
# Exact sparse original triangle is fitted perfectly under the incremental GLM.
triangle=[[F(100),F(150),F(180)],[F(120),F(180)],[F(140)]]
factors=[sum(r[k+1] for r in triangle if len(r)>k+1)/sum(r[k] for r in triangle if len(r)>k+1) for k in range(2)]
check('original_factors',factors==[F(3,2),F(6,5)])
reserve=sum(r[-1]*(math.prod(factors[len(r)-1:])-1) for r in triangle)
check('original_reserve',reserve==148)
residual_sq=[]
for r in triangle:
 fitted=[None]*len(r);fitted[-1]=r[-1]
 for j in range(len(r)-2,-1,-1):fitted[j]=fitted[j+1]/factors[j]
 obs=[r[0]]+[r[j]-r[j-1] for j in range(1,len(r))]
 fit=[fitted[0]]+[fitted[j]-fitted[j-1] for j in range(1,len(r))]
 residual_sq.extend((z-mu)**2/mu for z,mu in zip(obs,fit))
check('ODP_n_minus_p_is1',6-(2*3-1)==1)
check('ODP_fitted_phi_zero',sum(residual_sq)==0)
# Zero residual dispersion is not admitted as knowledge of a deterministic law.
adverse=[{'id':'sparse-original-triangle','status':'DISPERSION_UNRESOLVED','point_reserve':'148','raw_ODP_phi':'0','reason':'Perfect fit in six cells with one residual degree; no demonstrated deterministic future law or Mack final-factor variance.'},
 {'id':'nonpositive-degrees-of-freedom','status':'DISPERSION_UNRESOLVED'},
 {'id':'missing-process-law','status':'PROCESS_LAW_UNRESOLVED'},
 {'id':'negative-future-mean-under-positive-law','status':'MODEL_SUPPORT_FAILURE'},
 {'id':'nonfinite-future-cell','status':'NUMERICAL_FAILURE'},
 {'id':'missing-cell-mask','status':'STRUCTURAL_MASK_REQUIRED'}]
check('adverse_statuses_not_numeric_fallbacks',all('status' in z for z in adverse))
# Support mismatch between scan law and maintained helper, m=4 phi=2.
check('scaled_Poisson_variance',F(2)**2*(F(4)/2)==8)
check('negative_binomial_variance',F(4)+F(4)**2/(F(4)/(F(2)-1))==8)
check('negative_binomial_can_pay1',F(1)>0 and F(1)%F(2)!=0)
check('underdispersed_NB_size_invalid',F(4)/(F(1,2)-1)<0)
# Next-year CDR is a change in estimated ultimate, not this year's cash.
cdr=F(100)-F(30)-F(80)
check('one_year_CDR_minus10',cdr==-10)
check('cash_only_wrong70',F(100)-F(30)==70 and F(100)-F(30)!=cdr)
# Explicit failed-component mass: never renormalize surviving parameter fits.
check('retained_known_mass',sum([F(1,2)])==F(1,2))
check('retained_unknown_mass',1-F(1,2)==F(1,2))
check('known_mean_contribution',F(1,2)*F(2)==1)
output={'scope':'Authored finite laws; exact checks, no sampling or model fitting','law_A':encode(law_a),'law_B':encode(law_b),'fitted_means':encode(means),'joint_shared_fit_total':encode(joint),'independent_marginals_total':encode(independent),'mean':'5','variance':'19','estimation_variance':'9','expected_process_variance':'10','tail_A':'1/4','tail_B':'1/10','adverse':adverse,'partial_result':{'known_mass':'1/2','unresolved_mass':'1/2','known_mean_contribution':'1','full_mean':None,'status':'PREDICTIVE_RESULT_UNRESOLVED'},'horizon':{'opening':'100','payment':'30','revised_closing':'80','CDR':'-10'}}
(OUT/'exact-cases.json').write_text(json.dumps(output,indent=2)+'\n')
report={'passed':all(c['passed'] for c in checks),'check_count':len(checks),'checks':checks,'wall_seconds':time.perf_counter()-started}
(OUT/'calculation-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'checks':len(checks),'failed':[c['name'] for c in checks if not c['passed']]}))
if not report['passed']:raise SystemExit(1)
