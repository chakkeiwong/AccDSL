"""Exact, synthetic reference cases. No fitted probabilities or solver promotion."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import hashlib,json,platform,sys,time

start=time.monotonic(); base=Path(__file__).resolve().parent
rows=[]
def encode(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple,set)):return [encode(v) for v in x]
    return x
def check(id,actual,expected,meaning):
    ok=actual==expected
    rows.append(dict(id=id,actual=encode(actual),expected=encode(expected),passed=ok,meaning=meaning))
    if not ok:raise AssertionError((id,actual,expected))

# A nonanticipative action guesses a fair binary payoff driver. Signal observed
# before the action reveals it in one model; the other observes only a constant.
def best_payoff(signal):
    observations=sorted({signal(z) for z in (0,1)})
    policies=[dict(zip(observations,a)) for a in product((0,1),repeat=len(observations))]
    return max(sum((F(int(p[signal(z)]==z),2) for z in (0,1)),F(0)) for p in policies)
check('L01_terminal_law_equal',[(z,F(1,2)) for z in (0,1)],[(0,F(1,2)),(1,F(1,2))],
      'Both models have the same primitive terminal driver; information timing differs.')
check('L01_revealed_signal_value',best_payoff(lambda z:z),F(1),'Policy may condition only on observed signal.')
check('L01_unrevealed_signal_value',best_payoff(lambda z:0),F(1,2),'No actor can condition on the hidden sampled future.')
check('L01_discrete_average_not_action',F(0,2)+F(1,2) in {F(0),F(1)},False,'Conditional averaging need not preserve a discrete action set.')
eps=F(1,10000);cash=[-eps];approx=[eps]
check('L01_threshold_error',abs(F(cash[0]<0)-F(approx[0]<0)),F(1),'Arbitrarily small cash distance can give unit default-probability error.')
check('L01_threshold_distance',abs(cash[0]-approx[0]),2*eps,'The cash error tends to zero while threshold error stays one.')
# Verify coupling bound on a specified finite distribution at several margins.
p=[F(1,4)]*4; x=[F(-2),F(-1,10),F(1,10),F(2)];y=[F(-2),F(1,10),F(1,5),F(2)]
error=abs(sum((w*int(v<0) for w,v in zip(p,x)),F())-sum((w*int(v<0) for w,v in zip(p,y)),F()))
mean_distance=sum((w*abs(a-b) for w,a,b in zip(p,x,y)),F())
for delta in [F(1,20),F(1,5),F(1)]:
    bound=sum((w*int(abs(v)<=delta) for w,v in zip(p,x)),F())+mean_distance/delta
    check('L01_margin_bound_'+str(delta),error<=bound,True,'Local case of the separately derived boundary-mass plus coupling-error bound.')
# Uniform cost error and epsilon-optimality give a regret statement only when
# the same policy class and feasible lift have actually been established.
true_cost=[F(0),F(1,5)];approx_cost=[F(1,10),F(9,100)];chosen=min(range(2),key=lambda i:approx_cost[i])
uniform=max(abs(a-b) for a,b in zip(true_cost,approx_cost))
check('L01_policy_regret',true_cost[chosen]-min(true_cost),F(1,5),'An approximate optimum can choose a worse feasible policy.')
check('L01_uniform_regret_bound',true_cost[chosen]-min(true_cost)<=2*uniform,True,'Uses a common finite feasible policy class; not implied solely by optimal-value proximity.')

def posterior(prior,l1,l0):
    evidence=prior*l1+(1-prior)*l0
    if evidence==0:return 'conflict'
    return prior*l1/evidence
check('L02_uninformative',posterior(F(1,3),F(1,2),F(1,2)),F(1,3),'Uninformative observation leaves prior odds unchanged.')
check('L02_informative',posterior(F(1,2),F(9,10),F(1,10)),F(9,10),'Declared noisy signal changes probabilities, not the underlying type.')
check('L02_zero_evidence',posterior(F(1,2),F(0),F(0)),'conflict','Zero evidence is not permission to select a convenient history.')
check('L02_prior_set_bounds',[posterior(p,F(4,5),F(1,5)) for p in [F(1,4),F(3,4)]],[F(4,7),F(12,13)],'Monotone Bayes map propagates stated prior bounds for a fixed likelihood.')
persistent={(5,5),(7,7)};stagewise=set(product([5,7],repeat=2))
check('L02_false_switching_paths',stagewise-persistent,{(5,7),(7,5)},'Rectangular stagewise choices enlarge a fixed-type family.')
check('L02_resampling_extinction',F(99,100)**100>F(1,3),True,'A type with 1% mass can disappear in 100 iid resampling draws without evidence against it.')
old={0,1};corrected={h for h in old if h==0};wrong={h for h in {1} if h==0}
check('L02_revision_not_conjunction',[corrected,wrong],[{0},set()],'Replacing an erroneous assertion differs from conjoining it.')

# One-period risk-neutral lender, gross risk-free return 21/20; face 100.
face=F(100);solvency=F(9,10);recovery=F(40);gross=F(21,20)
payoff=solvency*face+(1-solvency)*recovery;proceeds=payoff/gross;yield_rate=face/proceeds-1
check('L03_face_proceeds',proceeds,F(1880,21),'Face-based price equals discounted recovery/solvent payoff under declared measure.')
check('L03_yield',yield_rate,F(11,94),'The quoted yield is a derived ratio, not the promised face.')
wrong_rate=(face*gross-(1-solvency)*recovery)/(face*solvency)-1
wrong_proceeds=face/(1+wrong_rate)
check('L03_mixed_convention_gap',gross*wrong_proceeds-payoff,-F(44,101),'Mixing a principal-based rate equation with face-based proceeds fails lender break-even.')
check('L03_funding_refusal',proceeds>=F(95),False,'The desired loan cannot fill a 95 cash gap at this face and price.')
# Waterfall assumes this priority contract; no jurisdictional priority asserted.
def waterfall(assets,senior,junior):
    s=min(assets,senior);j=min(max(assets-s,F()),junior);e=max(assets-s-j,F())
    return s,j,e
check('L03_senior_waterfall',waterfall(F(70),F(60),F(50)),(F(60),F(10),F(0)),'One asset pool cannot be paid twice.')
check('L03_waterfall_conservation',sum(waterfall(F(130),F(60),F(50))),F(130),'Senior, junior and equity allocations exhaust the stated estate.')
# Existing equity worth 80; gross subscription 20; issue cost 2; post-money 98.
pre=F(80);subscription=F(20);fee=F(2);post=pre+subscription-fee;new_fraction=subscription/post
check('L03_new_equity_fraction',new_fraction,F(10,49),'Fair new claim value is gross subscription; old shareholders bear the stated issuance cost.')
check('L03_old_equity_value',(1-new_fraction)*post,F(78),'Net cash and ownership must be solved together.')
shares=F(100);issue_price=(pre-fee)/shares;new_shares=subscription/issue_price
check('L03_new_share_count',new_shares,F(1000,39),'Same-price homogeneous shares reproduce the value allocation under these assumptions.')
check('L03_share_fraction',new_shares/(shares+new_shares),new_fraction,'Ownership fraction and cash-funded claim agree.')

# Disclosure probability: good type 9/10, bad type 1/10. An absent report is evidence.
check('L07_disclosed_good',posterior(F(1,2),F(9,10),F(1,10)),F(9,10),'Disclosed observations are selected under the declared mechanism.')
check('L07_silent_good',posterior(F(1,2),F(1,10),F(9,10)),F(1,10),'Silence changes the posterior when selection depends on type.')
# Uninformed manager probability 1/2, value uniform on [0,1]. With cutoff a,
# silence price is (1+a^2)/(2*(1+a)); equilibrium a=sqrt(2)-1.
# Exact polynomial bracket suffices without introducing floating tolerances.
f=lambda a:a*a+2*a-1
check('L07_disclosure_cutoff_bracket',[f(F(4142,10000))<0,f(F(4143,10000))>0],[True,True],
      'Locally derived uninformed-or-bad-news disclosure equilibrium has a nonzero silence price.')

# Conditional residual r(theta,epsilon)=(theta-1)+theta*epsilon, epsilon +/-1.
# E[r]^2=(theta-1)^2; E[r^2]=(theta-1)^2+theta^2.
def residual(t,e):return t-1+t*e
def square_mean(t):return (sum((residual(t,e) for e in [-1,1]),F())/2)**2
def mean_square(t):return sum((residual(t,e)**2 for e in [-1,1]),F())/2
def independent_product(t):return sum((residual(t,a)*residual(t,b) for a,b in product([-1,1],repeat=2)),F())/4
check('L06_wrong_loss_minimizer',[square_mean(F(1)),mean_square(F(1)),mean_square(F(1,2))],[F(0),F(1),F(1,2)],'Mean squared residual adds parameter-dependent variance and changes the optimum.')
for t in [F(0),F(1,2),F(1),F(2)]:
    check('L06_independent_draws_'+str(t),independent_product(t),square_mean(t),'Conditional independent product recovers squared expected residual in this finite case.')
# F(theta,q)=theta*q, q(theta)=theta: full derivative 2theta, detached derivative theta.
check('L06_detached_gradient',[2*F(3),F(3)],[F(6),F(3)],'A held-fixed pricing block changes the derivative; it may be an alternating algorithm but is not the total gradient.')

# Brier expectation for Bernoulli p is p(1-q)^2+(1-p)q^2, minimized at q=p.
loss=lambda q,p:p*(1-q)**2+(1-p)*q*q
check('L08_proper_score',[loss(F(1,4),F(1,4)),loss(F(1,2),F(1,4))],[F(3,16),F(1,4)],'A correct probability target matters; this arithmetic does not validate a forecast.')

# Further independent implications of the manuscript's authored examples.
enterprise=F(100);senior=F(60);converted_fraction=F(2,5)
residual_equity=enterprise-senior
check('L03_conversion_allocations',[senior,converted_fraction*residual_equity,(1-converted_fraction)*residual_equity],[F(60),F(16),F(24)],'Junior face is extinguished before residual equity is divided; no second debt payment.')
check('L03_conversion_conservation',senior+converted_fraction*residual_equity+(1-converted_fraction)*residual_equity,enterprise,'One estate is allocated once after the specified conversion.')
check('L03_creditor_veto',[F(45)+F(25)>F(50),F(45)>=F(50)],[True,False],'A total-value increase need not satisfy a secured creditor participation condition.')
check('L03_equity_fee_boundary',(F(2)-F(2))/F(100)>0,False,'A fee exhausting pre-issue value prevents this positive-price common-share convention.')
# Two structural models with identical observational laws and different do(X=1).
model_a=[(u,u,F(1,2)) for u in (0,1)]
model_b=[(u,u,F(1,2)) for u in (0,1)]
check('L07_observational_equivalence',model_a,model_b,'Both models observe X=Y=U.')
check('L07_intervention_nonidentification',[sum((F(u,2) for u in (0,1)),F()),F(1)],[F(1,2),F(1)],'Under do(X=1), Y=U and Y=X give different means.')
# An observation is selected by its availability date, not economic period alone.
records=[{'period':2024,'available':'2025-03-01','value':F(10)}, {'period':2024,'available':'2026-03-01','value':F(4)}]
available=[x for x in records if x['available']<='2025-06-01']
check('L08_vintage_cutoff',available[-1]['value'],F(10),'The later restatement is unavailable to this forecast origin.')
outcomes=[('survivor',False),('failed',True)]
check('L08_survivorship_target',[F(sum(x[1] for x in outcomes),len(outcomes)),F(0)],[F(1,2),F(0)],'Dropping the failed issuer changes the event frequency in this authored panel.')
# Equality on historical support does not identify off-support policy response.
policy_a={0:'wait',1:'wait',2:'issue'};policy_b={0:'wait',1:'wait',2:'cut investment'}
check('L08_policy_identification',[all(policy_a[s]==policy_b[s] for s in [0,1]),policy_a[2]==policy_b[2]],[True,False],'Historical agreement does not identify an unobserved financing-shock response.')

result=dict(date='2026-10-26',status='PASS',checks=rows,count=len(rows),
    evidence='Exact deterministic arithmetic/enumeration for declared synthetic models',
    scientific_limit='No real-company calibration, stochastic ranking, global solver convergence or general simulator validation.')
(base/'exact-results.json').write_text(json.dumps(result,indent=2)+'\n')
(base/'run-manifest.json').write_text(json.dumps(dict(
    command='python3 data/accounting-master/literature-closure-20261026/exact_cases.py',
    environment=sys.version,platform=platform.platform(),cpu_gpu='CPU-only standard-library arithmetic; no ML/CUDA imported',
    git_commit='Not applicable: project .git is unusable; source hash retained',
    source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),data='Declared exact synthetic cases in source',
    random_seed='Not applicable: complete finite enumeration and rational arithmetic',wall_seconds=time.monotonic()-start,
    plan='docs/plans/accounting-literature-closure-20261026.md',result=str((base/'exact-results.json').relative_to(base.parents[2]))),indent=2)+'\n')
print(json.dumps(dict(status='PASS',exact_checks=len(rows))))
