# Changing particle representations without changing the inference target

26 October2026. E02; MC12/14/26/29/30, W03/W15. This continues the retained
PMCMC proof reading and adds a scoped SMC2 transfer audit. It does not rerun
the external package or adopt its defaults.

## Sources and inspected scope

Chopin, Jacob and Papaspiliopoulos, *SMC2: an efficient algorithm for sequential
analysis of state-space models*, retained arXiv1101.1528v3,27 January2012,
`../literature-closure-20261026/sources/smc2.pdf`. Inspected Sections3.1–3.3,
3.6–3.7, the related Section4 evaluation setup, and AppendicesA/B. Exact
source-text anchors are equation(7), Proposition1 and AppendixA; equations
(10)–(11) and the exchange ratio on physical page11; Proposition2 and
AppendixB on physical pages26–27. The original source library and retained
text are unchanged. This is a version-specific reading, not a publisher-byte
comparison or a fresh full-paper survey.

The modern author-linked `nchopin/particles` code is pinned at
3388c4bd30ab9acc5a27c970089230f93610b627. Inspected `smc_samplers.py`:
`all_distinct` and `FancyList` around lines317–379; `ThetaParticles` around
400–483; `ArrayMetropolis.step` around606–615; MCMC sequences around659–716;
SMC2 around1052–1181. The prior PMCMC note supplies the original
Andrieu–Doucet–Holenstein and Andrieu–Roberts target-proof reading.
Source hashes are in `smc2-run-manifest.json`.

## The representation is part of the target

Let theta be a persistent company type and let v identify a fixed evidence
vintage. Write its likelihood as L_v(theta). A particle system with N particles
uses auxiliary randomness u with density m_N(u|theta) and a nonnegative
unbiased likelihood estimate Z_N(theta,u). Assuming a finite positive
normalizer C_v, its extended target is

    pi_N(theta,u) = p(theta) m_N(u|theta) Z_N(theta,u) / C_v.

Integrating over u gives p(theta)L_v(theta)/C_v. This is the likelihood-
weighted auxiliary target in source equation(7). AppendixA expands the product
of incremental importance weights, selects a trajectory, and cancels proposal
and resampling factors along its genealogy. Proposition1 then identifies the
posterior marginal. Concatenating particle arrays without their ancestry would
not preserve the same selected trajectory.

Suppose a new representation uses M particles and a fresh u' drawn from
m_M(.|theta). The augmented proposal has density

    pi_N(theta,u) m_M(u'|theta).

Choose the backward density m_N(u|theta). The desired augmented target is
pi_M(theta,u')m_N(u|theta). Dividing it by the proposal cancels p(theta),
C_v and both auxiliary proposal densities, leaving

    w_exchange = Z_M(theta,u') / Z_N(theta,u).

This reproduces the Section3.6.1 exchange weight under the stated support
conditions. The finite diagnostic below uses strictly positive estimates; it
does not resolve zero-estimate or proposal-support cases by division tricks.
One can discard the old auxiliaries after the weighted exchange. Simply
replacing them without this weight produces a different joint distribution.

The distinction can be invisible in the immediate theta marginal. Take prior
probability1/2 for each of two types and true likelihood1 for both. Under
type0 the old estimate is1/2 or3/2, equally likely; the new estimate is1/4 or
7/4, equally likely. Type1 always has estimate1. Both estimators are unbiased.
For new states (0,1/4),(0,7/4),(1,1), the correct extended target is
(1/16,7/16,1/2). An unweighted replacement instead yields(1/4,1/4,1/2).
The type1 marginal is still1/2, so a test of that marginal alone passes.

Now perform a valid PMMH step which proposes switching type, draws the new
estimate and accepts with min(1,Z_proposed/Z_current). Its transition matrix is

    [ 0       0       1     ]
    [ 0       3/7     4/7   ]
    [ 1/8     1/2     3/8   ].

The correct extended target is invariant and satisfies detailed balance.
Starting from the wrongly exchanged distribution, the probability of type1
after one move is1/4+(1/4)(4/7)+(1/2)(3/8)=65/112, rather than1/2. The
difference is9/112. This is an exact one-step counterexample, not a claim that
the valid PMMH kernel has a wrong stationary distribution. It explains why
checking only current type probabilities can miss an invalid representation
change. The ratio-weighted exchange passes full joint-target equality.

## What the inspected code does

The pinned `SMC2.exchange_step` saves the old log posterior, runs
`current_target(t-1,new_Nx)` and returns the new minus old log posterior.
`logG` adds that exchange correction to the next incremental observation
weight. The use of t−1 matters: the exchange occurs before processing the next
datum. Calling the new filter through t and then adding that datum again would
double-count it. The prior cancels in the exchange ratio because theta and the
evidence vintage are unchanged.

`ArrayMetropolis.step` constructs a proposed particle object and copies it
into the current object only where accepted. `ThetaParticles.copyto` also
copies the associated filter objects under that acceptance mask. Rejected
particles therefore retain their old likelihood/filter state. `FancyList`
uses `all_distinct` to deep-copy repeated selections, addressing the risk that
two resampled copies share one mutable filter which advances twice. This is
static code correspondence, not execution of the entire dependency tree.

The modern default is waste-free SMC with a sequence of retained MCMC states.
That extension has additional theory and dependence considerations; the old
2012 SMC2 argument alone does not establish its finite-sample accuracy. The
source's default initial particle count100 and chain length10 remain source
choices. The inspected executable increases the particle count when acceptance
is below its threshold after a move, while its docstring says above. Preserve
that documentation discrepancy without claiming it invalidates the executable
exchange formula.

## Why historical corrections need a separate operation

The source algorithm consumes a fixed sequence of observations. A later
correction replaces part of that sequence and changes L_v, whereas a new
observation ordinarily multiplies the existing likelihood. AccDSL must identify
the evidence vintage in the filter and invalidate its dependent likelihood and
auxiliary state on replacement. The unchanged code does not itself implement
AccDSL source revisions.

For example, with prior(1/2,1/2), an old hard observation has likelihood(1,0),
giving posterior(1,0). A replacement has likelihood(1/4,3/4), so its correct
posterior from the preserved prior is(1/4,3/4). Multiplying the restricted old
posterior by the replacement still gives(1,0). A new/old likelihood ratio is
undefined on the restored second type. Reweighting particles whose support
already excludes that type cannot create it. Reconstruct/replay from a
sufficient preserved checkpoint or use a separately justified bridge with
the required support; do not call replacement evidence another observation.

## Quantitative claims that still need premises

AppendixB assumes uniform bounds on transition and observation-density ratios
(H1a/H1b), followed by posterior regularity conditions H2a–H2d, including a
convergent likelihood maximizer, positive-definite limiting information,
separation away from the maximizer and sufficiently smooth derivatives.
Proposition2's stability/complexity interpretation also idealizes refreshed
particles as exact target draws. The appendix explicitly distinguishes that
idealization from a finite PMCMC move and leaves a quantitative mixing argument
as additional work.

A deterministic permanent type appended to the evolving state need not satisfy
the uniform transition ratio. Hard accounting observations can yield zero
likelihoods, and unidentified alternatives need not have regular posterior
curvature. These are concrete transfer questions for the intended company
model. The paper's selected numerical models and particle settings cannot
supply their answers. The original Cerou/Chopin/Whiteley quantitative
dependencies, modern waste-free theory, complete resampling implementation,
support design, real likelihood identification and downstream company results
remain separate reading/implementation obligations.

## Decision

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Retain exchange ratio and auxiliary state | Local derivation, source equation and exact joint-mass enumeration agree | Unweighted exchange fails the joint target and next-step marginal | General support and full dependency execution | Bind evidence vintage and audit resampling/waste-free extension | SMC2 adopted or generally accurate |
| Replace corrected evidence by replay or justified bridge | Exact support-restoration example passes | Restricted old support cannot recover a deleted type by reweighting alone | Which checkpoint contains sufficient state | Specify and test a versioned inference request | Generic revision engine implemented |
| Keep quantitative transfer open | Required assumptions identified | No verified company mixing, likelihood or curvature premises | Finite-run uncertainty and permanent-type coverage | Target-specific model and independent posterior/decision checks | Performance, scalability or forecast ranking |

`smc2_exchange.py` records28 exact checks and complete distributions in
`smc2-exchange-results.json`. This is deterministic algebra, so no stochastic
ranking or uncertainty interval is inferred. The tested invalid exchange is
rejected; the correctly weighted construction remains viable. The source
reading and diagnostic close a scoped transfer question, not L02 or S1.

Post-run red team: the constructed finite example establishes a possibility,
not the magnitude of bias in an actual issuer application. It does not indict
the pinned code, which includes the exchange correction. A different transition
that explicitly targets the changed distribution could be valid under another
derivation. The weakest remaining evidence is the unexecuted modern inference
stack and the unidentified company observation model. Continue those planned
repairs; no research-direction rejection or continuation veto follows.
