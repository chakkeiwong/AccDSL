# Particle inference: original proof dependency and a rejection-state failure

26 October 2026. MC12–14, MC23–26 and MC29–35. This is an additive research
note after the Version5.11 build; it does not silently modify that frozen PDF.
The original-access and scoped exact-target proof gap is repaired. General
inference, mixing guarantees, model identification and SMC2 acceptance stay open.

## Primary sources inspected

Andrieu, Doucet and Holenstein (2010), Particle Markov Chain Monte Carlo Methods,
JRSSB72(3),269–342, DOI10.1111/j.1467-9868.2009.00736.x. Retained from Doucet's
Oxford author site. The local published article includes discussion. Inspected:
Sections2.4.1–2.4.3, the non-linear example/evaluation in3.1, assumptions and
extended targets in4.1–4.5, AppendixA and proofsB.1–B.4. The full discussion,
Lévy evaluation and all secondary dependencies were not systematically read.

Andrieu and Roberts (2009), The Pseudo-Marginal Approach for Efficient Monte
Carlo Computations, Annals of Statistics37(2),697–725, DOI10.1214/07-AOS574.
Retained arXiv0903.5480v1, journal-formatted reprint. Inspected: Section1/Table1,
Section2(A1) and equations(2.1)–(2.4), Section3 Theorem1 and its full proof,
Section7.1 exact-marginal example. No full performance-theorem reading or
line-by-line comparison with publisher bytes is claimed. Metadata and source
hashes are in source-support.json and citation-venue.json.

## Why the estimator belongs to the state

Let theta denote a persistent type, p(theta) its prior, and L(theta) the
likelihood of a fixed evidence vintage. Auxiliary randomness u has law m_theta.
Assume a finite nonnegative estimate Lhat(theta,u) with expectation L(theta),
a finite positive normalizing constant Z, and the required proposal support.
The joint target density is

    pi_tilde(theta,u) = p(theta) Lhat(theta,u) m_theta(u) / Z.

Integrating u gives the desired posterior p(theta)L(theta)/Z. Propose theta'
from q(theta'|theta), and u' from m_theta'. Detailed balance yields acceptance

    min(1, p(theta') Lhat(theta',u') q(theta|theta')
           / [p(theta) Lhat(theta,u) q(theta'|theta)]).

The rejected state includes its old u and likelihood estimate. Replacing the
denominator with a fresh estimate changes the transition law. This is the
MCWM/GIMH distinction in Andrieu–Roberts Section1/Table1 and the unchanged
likelihood in Andrieu–Doucet–Holenstein equations(13),(35). Their equations
(31),(36) supply the extended particle target; AppendixB.1 telescopes the
importance ratio to the estimated normalizer divided by the true normalizer.
AppendixB.3 refers convergence to Andrieu–Roberts Theorem1. That theorem assumes
(A1), an irreducible/aperiodic ideal chain, and positive rejection probability
rho(theta,Z); its proof transfers accessible sets by induction. These are
conditions to check, not facts established for AccDSL's unknown company model.

Invariance, convergence and useful finite-run accuracy are different results.
The PMCMC paper's bounded-weight/forgetting assumptions support quantitative
claims only where they hold. A permanent type does not automatically satisfy
forgetting after being appended to the evolving state. A biased estimated
likelihood, an unbiased log-likelihood, a missing proposal-support region, or
a stale likelihood after a disclosure correction cannot inherit the argument.
A source correction changes the target evidence vintage and requires explicit
invalidation/recomputation, not silent reuse of an auxiliary state.

## Exact discriminating case

Both types have prior1/2 and true likelihood1. For type0 the likelihood
estimate is1/2 or3/2 with equal probabilities; for type1 it is always1.
Every estimate is positive and unbiased. Propose switching type every step.
The augmented states are (0,1/2),(0,3/2),(1,1), and the retained-estimate kernel is

    P = [[0, 0, 1], [0, 1/3, 2/3], [1/4, 1/2, 1/4]].

Its stationary probabilities (1/8,3/8,1/2) obey detailed balance, have the
correct type marginal1/2, and give positive two-step reachability with a
self-loop. Refreshing both estimates gives switch rates5/6 and3/4. The unique
stationary probability of type1 becomes (5/6)/(5/6+3/4)=10/19, a bias of1/38.
Thus unbiased likelihood estimates alone do not validate the refreshing chain.
The exact rational reference has24 passing assertions; no stochastic run,
finite-run mixing claim or performance ranking is involved.

Particle Gibbs needs a conditional particle system that preserves a reference
trajectory and the appropriate genealogy, not an ordinary particle-filter
replacement. PMCMC AppendixA conditions resampling; for multinomial offspring,
its procedure samples N-1 offspring then adds the protected child. Theorem5
states invariant-target preservation for N>=1 but its convergence statement
requires N>=2 and the additional assumptions. These should not be conflated.

## Original code comparison

The already pinned nchopin/particles source, particles/mcmc.py, has SHA256
5e1fa6e9679eb9f76dea8b1d33af9ad6e8db99ba84d68ed1839d5a5a67771fc2.
GenericRWHM.step at lines285–297 computes a proposed posterior, compares it
with the stored chain.lpost[n-1], and on rejection copies the previous chain
entry. PMMH.compute_post at lines445 onward obtains the proposal's estimated
log likelihood from its particle filter. This retained-current pattern agrees
with the exact-target requirement. It is a static check of the pinned
maintainer implementation, not reproduction of the2010 paper's experiments.
Adaptive proposal defaults, support, particle-number adaptation, resampling,
revision replay and the whole SMC2 path need their own validity checks.

The original PMCMC numerical example reports mode trapping despite apparently
fast ACF decay for a local update (Section3.1,pp282–283). This motivates a
reference-posterior check; it does not set AccDSL's particle count or establish
a method ranking here. The2009 toy example uses known marginals and comparable
computational efforts; those problem-specific settings are not transferred.

## Decision and next evidence

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Close original-access and scoped target-proof dependency | Primary algorithms, extended target and linked proof inspected | Missing support or changed target would veto transfer | Company likelihood and adapted implementation | Preserve explicit evidence vintage and auxiliary state | SMC2 accepted |
| Reject refreshing-current variant for stated target | Exact stationary marginal differs by1/38 | Wrong target established in this finite case | Other variants with explicit corrections | Retain estimator or derive a valid alternative kernel | Every noisy MH method is wrong |
| Keep scalable inference open | No company/runtime criterion evaluated | No support, mixing or target-vintage evidence yet | Computational adequacy and identification | Reference comparisons under a reviewed protocol | Forecast validity |

| Inference status | Assessment |
|---|---|
| Hard veto screen | Refreshing-current candidate computes the wrong invariant marginal in the stated example |
| Statistically supported ranking | None; exact algebra only |
| Descriptive-only differences | Source and check counts |
| Default readiness | No inference default promoted |
| Next evidence | Identified target, support and resampling audit, immutable-vintage replay, and downstream uncertainty analysis |

The strongest alternative explanation is that this diagnostic is finite and
constructed. It does not weaken the exact counterexample, but it prevents a
claim about the size of bias in a company application. The direction remains
viable: the retained-estimate construction passes the exact target check.
The remaining work is implementation/identification and general inference,
not another request for access to these two original papers.
