# Reconstruction, numerical methods and conditional forecasts

A forecast is conditional on a reconstructed history, accounting treatment,
behavioral model and future scenario. A probability law is an additional input,
not a consequence of having generated several paths. These methods specify
MC08–MC14, MC18, MC26, MC28–MC30 and MC32–MC34 within the P16 family, uncertainty,
information-view and failure contracts. Finite cases below are mathematical
examples. They establish no empirical predictive ranking or calibrated default.

## Q1. Constructing histories and evaluating queries

Inputs are admitted evidence_view, interpretation choices, template registry,
time/perimeter, unknown domains, initial-state constraints, method versions and
requested horizon/scenarios. Instantiate only declared templates and slots;
share symbol identities across all statements and time. Keep each template's
applicability findings. Discrete choices form a finite explicitly declared tree;
continuous unknowns remain domains with constraints, rather than a grid whose
count implies probability. Lower supported methods after expansion into rational
linear equalities/inequalities plus finite logical choices. Check domain/type,
units and method support before solving. Bilinear quantity×unknown-price,
unknown-rate powers and unrestricted functions are outside that linear capability.

For each branch solve feasibility; retain a verified witness or infeasibility
certificate in the supported fragment. A solver timeout/unknown cannot prove
infeasibility. Enumerate all declared discrete choices only when the coverage
record certifies exhaustion; otherwise save explored, pruned-with-proof and
unexplored regions. One feasible witness does not establish family completeness
outside that template scope. A restated evidence view triggers reconstruction
and selection invalidation under P16; old witnesses remain tied to old sources.

For a linear query q=cᵀx, solve minimum and maximum over the joint constraints
with independently checked primal/dual evidence where provided. Distinguish
attained maximum from supremum: x∈[0,1) gives sup x=1 with no maximizing member.
For q1=x and q2=1−x on[0,1], both marginal maxima are1, but(1,1) is infeasible.
The result API returns the shared feasible path and query relation, not a
fabricated vector of independent extrema. Nonlinear exact capability must name
its supported operations/certificates; a sampled range is only sampled.

## Q2. Discounting and exact numerical boundaries

For positive cash payments C_i at positive times t_i and price P>0, solve
f(r)=Σ C_i/(1+r)^t_i−P on r>−1. Its derivative is
−Σ t_i C_i/(1+r)^(t_i+1)<0, so a sign-changing bracket contains exactly one root.
Select a bracket by explicit bounds/expansion cap, evaluate with outward error
bounds, and bisect until the requested rate/value enclosure is reached. Stop
with unresolved_bracket or numerical_failure if sign or accuracy cannot be
certified. Mixed-sign flows can admit multiple IRRs; the monotonic proof then
fails and this method returns unsupported_root_selection, not the first root
from Newton's method. A root is numerical evidence, not the authority for using EIR.

For rational r and rational time p/q with positive1+r, accumulation is the
positive qth root of(1+r)^p. If a rational candidate g satisfies g^q=(1+r)^p
exactly and g>0, it is exact. Otherwise rational interval bisection with exact
power comparisons provides a certified enclosure; negative p first takes the
reciprocal. For r=0.21 and p/q=1/2, g=1.1 is exact. For r=0.10 and half a year,
the factor is irrational and must not be relabeled exact by decimal rounding.
Posting at quantum0.01 requires the entire monetary enclosure to fall in one
cell of the authorized tie rule; an enclosure straddling a half-cent remains
rounding_unresolved. Refine to a declared cap or preserve that outcome.

Arbitrary continuously compounded rates require a separately error-controlled
exp/log implementation. No external library tolerance becomes the specification.
Solver resource bounds change coverage, not mathematical truth. Replays under a
wall-time cap may explore different cells; compare exact outputs on the same
evaluated cells and preserve both coverage records, as P16 requires.

## Q3. Finite probabilities and continuous inference

A finite LawDefinition contains the joint atoms/regions, exhaustive/disjoint
relations, nonnegative masses summing to one, conditioning information lineage
and substantive justification. For new evidence D with admitted likelihood
L(D|h), posterior mass is p(h)L(D|h)/Σ_g p(g)L(D|g). A zero denominator returns
condition_impossible. The same information atom cannot be submitted again as
fresh evidence; repeating an identical semantic condition is the P16 idempotent
operation. A refinement divides existing mass using an admitted conditional
kernel, not the number of new representatives. Keep unresolved/failure masses.

Example: prior weights1/3 and2/3 with likelihoods3/4 and1 give joint masses1/4
and2/3, evidence probability11/12 and posterior3/11 and8/11. Those numbers are
conditional on assumed weights/likelihoods. If the second branch cannot evaluate
cash, known cash outcomes retain mass3/11 and unresolved retains8/11; reporting
the first branch at probability1 is wrong for the stated target.

For a continuous target, explicitly define coordinates z, base measure, domain,
prior p(z), observation mechanism p(D|z), Jacobians for transformations and
normalizer. Stuart2010 §2.2 equations(2.5)–(2.8) supplies the inspected inverse
problem/Bayes formulation. It does not prove that a mixed accounting model is
identified, well posed or easy to sample. Exact observed accounting constraints
may restrict a lower-dimensional manifold: ordinary Lebesgue density plus an
indicator of a zero-volume equality is not a valid posterior construction.
Parameterize the constrained model with its declared measure or supply an
actual measurement-error model; arbitrary epsilon noise changes the target.

A fully specified continuous baseline uses z~N(m0,V0), y=Hz+epsilon with
epsilon~N(0,R), independent of z, V0 positive definite and R positive definite.
Completing the square yields precision V0⁻¹+HᵀR⁻¹H and information vector
V0⁻¹m0+HᵀR⁻¹y; their solution gives posterior V and m. An implementation should
solve factored linear systems rather than form inverses, and report nonpositive
covariance or rank/model errors. Exact constraints are a separate method.
For scalar m0=0,V0=4,H=1,R=1,y=2, V=4/5 and m=8/5. Cash=100+10z then has
conditional mean116 and variance80. A second independent measurement of2 would
give m=16/9,V=4/9, but reusing the same observation is forbidden. This contrast
is a diagnostic of information double counting, not extra data acquisition.

For bounded non-Gaussian univariate inference, numerical quadrature is permitted
only with a stated tail/domain truncation and integrand error enclosure sufficient
to bound normalizer and requested moments. If a positive lower normalizer bound
is unavailable, return unresolved. For multidimensional or mixed targets,
enumerate finite choices and use a declared integration/sampling method within
each continuous conditional model; evidence/normalizers are needed to combine
branches, not raw draw counts. An optional MCMC backend requires target-specific
parameterization, tuning, independent chains, correctness comparisons on tractable
cases, divergence/convergence/MCSE diagnostics and downstream checks before use.
No validated general sampler, training protocol or tolerances are established here.

The set of histories remains primary when no law is justified. Even infinitely
many reports cannot identify a feature absent from the observation operator.
For observed total debt100 and unobserved floating fraction x∈[0,1], likelihood
constant in x leaves its conditional prior unchanged. A uniform prior is a
chosen assumption, not inferred uncertainty. Giacomini/Kitagawa retained2020
working paper §§2.1–2.3 equations(2.2)–(2.4) motivates posterior classes when a
conditional prior is unrevisable. Our finite interval result uses a direct
project deduction: under all probability measures on[0,1], the expectation of
5+2x lies in[5,7], achieved by endpoint point masses. No transferred SVAR
asymptotic theorem or unique predictive law is claimed.

## Q4. Stress, observation and causal intervention

ExogenousStress replaces a declared future driver path without using it as new
historical evidence. ObservationalCondition changes a joint law through admitted
new information. Intervention requires a StructuralModel with named structural
equations, causal parent relations, exogenous joint law and intervention target;
replace that equation while retaining the others and their disturbance law.
Validate acyclicity or the explicitly supported equilibrium-solution rule before
execution. Pure observational fit does not supply those causal assumptions.
Pearl2009 §3.2 and equations(5)–(9), with the Markovian qualifications in(15)–(17),
support the distinction; correlated exogenous variables are kept joint.

An exact counterexample takes U Bernoulli(1/2), X=U, Y=2X+U. Observing X=1 forces
U=1 and Y=3. Under do(X=1), U retains its original law, so Y=2 or3 with equal
mass and mean2.5. Conditioning on a high investment choice is therefore not the
same as imposing that choice. This authored causal model illustrates the rule;
financial filings alone do not establish its equations or an identified effect.
Policy functions receive the available information view at each decision date,
not future simulated outcomes. Common random numbers can support paired scenario
comparisons but do not by themselves identify causal effects in real data.

## Q5. Forecast evidence required before promotion

The proposed experiment question is whether the full conditional method adds
out-of-time predictive information while preserving statement coherence and
honest unresolved exposure. No experiment is executed in P17. Define issuer
families, dates/horizons, available original bytes and as-of availability before
partitioning. The current corpus's136 unverified publication dates cannot serve
as known historical-information timestamps. Development annotations31 across
four reports are exposed pilot data, not a heldout accuracy population.

Compare the same targets/information against last-observation and seasonal naive,
contractual-runoff/accounting-identity, tuned classical statistical and proposed
structural models; report model variants/ablation separately. Tune within training
windows, keep test issuers or time blocks uncontaminated, and specify denominator
and handling of unavailable predictions. A failed branch stays in coverage and
failure-rate reporting. For probabilistic predictions predeclare proper scores,
calibration/interval coverage and sharpness for the supported quantities, plus
dependence-sensitive joint tests. For unweighted sets report coverage and width
under a stated interpretation; they are not probability intervals.

Primary promotion requires the declared score difference and uncertainty estimate
on matched eligible targets, alongside accounting and time-validity vetoes. Use
issuer/time dependence-aware paired resampling or another justified design; a
few overlapping reports are not independent replications. Descriptive runtime,
point loss, tails and small-seed differences cannot rank viable models. Failed
conservation, look-ahead, missing scope or invalid target vetoes the experiment;
poor candidate prediction triggers repair, not rejection of all alternative-history
modeling. Save split/data/version/model/seed/environment/command/elapsed-time
manifests and failures. Required thresholds must be justified for the intended
decision before running; none is invented here to produce a convenient pass.
