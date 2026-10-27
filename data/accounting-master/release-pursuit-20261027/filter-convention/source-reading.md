# Particle-weight convention and retained source

The inspected source is Doucet and Johansen, *A Tutorial on Particle Filtering
and Smoothing: Fifteen years later*, version 1.1, December 2008 with March 2012
typographical corrections. Its exact local path and SHA256 are in
source-identity.json. The original paper collection is unchanged. This reading
does not establish that no later correction or edition exists; no current
publisher-wide correction search or official-code audit was completed here.
The proposal below is supported by the displayed density-ratio derivation and
the exact finite examples, with the tutorial supplying the explicit algorithmic
conventions. No convergence theorem or software implementation is promoted.

Section 2.1, physical page 4 (printed page 2), assumes a Markov latent process,
conditionally independent observations and known model parameters. Equations
(1)–(2) define transition and likelihood densities relative to dominating
measures. Sections 2.1–2.2, pages 5–7, give the product prior, likelihood and
posterior recursion. These premises prevent treating reports from an arbitrary
company as an admitted state-space likelihood without further modeling.

Section 3.2, physical pages 11–12 (printed 9–10), requires target support to be
covered by the proposal. Equations (21)–(25) define the unnormalized density
ratio and normalized weighted empirical measure. The later self-normalized
estimator is a finite-sample ratio estimator; ordinary and self-normalized
importance estimators must remain distinct. This unit does not import its
asymptotic-bias or central-limit formulas as newly checked theorems.

Section 3.3, physical pages 12–14 (printed 10–12), factors the sequential
proposal in equation (28), derives the weight recursion in (29), and defines
the incremental ratio in (30). Its SIS algorithm multiplies the existing
weight by that ratio. The AccDSL equation is this recursion specialized to
the Markov proposal and filtering target. The original sentence called the
whole updated weight an incremental weight and omitted the no-resampling
convention. That sentence is under-specified; the displayed equation is
correct under SIS. Using it with a retained pre-resampling parent weight
after ordinary resampling is wrong relative to the declared filtering target.

Section 3.4, physical page 15 (printed 13), draws ancestors from the weighted
empirical measure and assigns equal weight 1/N to each child. Section 3.5,
physical pages 16–18 (printed 14–16), explicitly uses only the incremental
ratio after that reset. Its adaptive algorithm retains the old weight when
resampling is skipped and resets it when resampling occurs. The three
algorithm pages were also viewed at normal resolution in source-13.png,
source-16.png and source-17.png; the tildes distinguishing pre/post-resampling
particles and weights are material.

The proposed ancestor ratio W_j/r_j follows directly from the augmented
target W_j f_j(x) g(x) divided by proposal r_j q_j(x). It is a local derivation
relative to the supplied finite empirical measure. It does not identify that
measure with the exact posterior of the original continuous model. Ordinary
multinomial resampling sets r_j=W_j; an altered ancestor proposal needs the
ratio. The exact two-type example yields posterior (1/2,1/2), double weighting
yields (3/4,1/4), and omitted correction under uniform ancestor proposals gives
(1/4,3/4). Eighty-one finite two-state cases additionally check non-identity
transitions and different state proposals. These are exact identities, not
empirical rankings or claims about any one stochastic realization.

Sections 3.5–3.7, physical pages 18–21, explain genealogy loss and distinguish
path-distribution degeneration from fixed-dimensional filtering behavior under
mixing conditions. The explicit CLT proof is referred to Del Moral and other
sources; those proofs are not newly checked here. No uniform-in-time accuracy
claim for static company contracts is imported. Section 4.6, physical pages
33–36 (printed 31–34), factors a joint target into a marginal and tractable
conditional, then develops conditionally linear Gaussian and partially observed
linear Gaussian cases. Its Kalman sufficient statistics retain the dependence
needed for conditional likelihoods. This supports the existing conditional
integration discussion; it does not license discarding company history memory.
The beginning of section 5 was also inspected: its fixed-lag approximation
targets a truncated-information smoothing distribution and retains bias even
as the particle count grows. No fixed-lag default is proposed here.

The strongest risk in the repair is suggesting that exact weight algebra gives
an exact finite-sample posterior. The new paragraph says explicitly that the
four-child allocation is an illustration and that a random allocation need not
match the posterior exactly. Ancestor diversity, static-parameter loss, source
likelihood admission and model misspecification remain separate concerns.
