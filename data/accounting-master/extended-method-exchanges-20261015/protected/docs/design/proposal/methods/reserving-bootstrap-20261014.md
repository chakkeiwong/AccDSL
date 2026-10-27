# Conditional reserve laws: estimation, process and horizon

14 October2026. Scoped P17-09/E08 and actuarial E07 supplement. Source inspection
and exact cases: `data/accounting-master/p17-completion-20261014/P17-09/reserving-bootstrap/`.
This specifies an optional candidate procedure; it does not adopt a numerical
default, calibrate an insurer or define its IFRS17 risk adjustment.

## Target and model identity

Inputs identify the observed cumulative paid-claims triangle, currency and
scale, origin/development/calendar periods, information cutoff, structural
missing mask, adjustments and exclusions, tail, and links to insurance groups.
Mack's cumulative conditional-moment model and the incremental ODP GLM are
different model records, even when fitted reserves coincide. Store the exact
source edition, observation model, residual rule, parameter count, fitted
dispersion, process law, dependence, horizon and failure policy.

The directly inspected source is England2001 ARP138 §§2–3 and AppendixA,
not an assumed exact copy of the2002 journal addendum. For observed incremental
X and strictly positive fitted m, r=(X−m)/sqrt(m), phi=sum(r²)/(N−p), and
adjusted r*=sqrt(N/(N−p))*r. For a complete n-by-n triangle's origin-plus-
development model, N=n(n+1)/2 and p=2n−1; missing cells change rank and cannot
use these counts blindly. Reject unidentified rank or N≤p. Residual pooling
is an assumption requiring diagnostics by origin, development and calendar
time. Dispersion0 on the tiny perfectly fitted example is an unresolved
estimation problem, not evidence of deterministic future payments.

## Explicit optional procedure

1. Fit volume-weighted development factors to the declared cumulative data.
   From each latest observed diagonal, work backwards by dividing by fitted
   factors and difference to obtain fitted increments. Require finite positive
   fitted increments for this positive-increment profile.
2. Compute residuals, phi and adjustment once. Retain unadjusted/adjusted
   identities and the actual resampling pool; do not silently center, trim,
   exclude structural zeros or duplicate a degrees-of-freedom correction.
3. For each specified bootstrap index, draw residuals with replacement using
   its named RNG substream, invert X*=m+r*sqrt(m), accumulate, refit factors,
   project cumulative future claims and difference into conditional means.
   A fit is shared across all cells in that draw. Denominator0, invalid support,
   nonfinite arithmetic or impossible rank yields a specific failed draw.
4. Use a separately named process RNG substream to draw conditional future
   increments under the supplied law. For m>0, phi>0, source alternatives are
   scaled-Poisson phi*Poisson(m/phi), or Gamma(shape=m/phi,scale=phi). Both
   have mean m and variance phi*m but different support/tails. Conditional
   cell independence is a stated assumption; shared parameter draws retain
   dependence after mixture. No hidden global independent-marginal redraw.
5. Sum aligned cells to origin/calendar/total payments; preserve all identities
   for discounting, treaty application and group mapping. Map to measurements
   only under separately admitted discount/RA/accounting facts.
6. Return completed draws and failures with attempted counts and coverage.
   Structural absent cells are not numerical failures. If any required draw
   fails, the full empirical predictive result stays unresolved; valid draws
   are conditional diagnostics. Do not impute0, redraw until successful, or
   normalize over successes unless a different conditional target is explicit.

The empirical resampling distribution is a method-generated approximation,
not an identified true posterior. A finite fixture may carry exact authored
probabilities; attempted bootstrap failure frequency is not proof of unknown
population probability. Simulation count, seed policy and convergence/quantile
uncertainty requirements belong to a target-specific validation plan; the
source's1000 replications and package default999 are not accepted defaults.

## Checked counterexamples

The authored conditional mean M is2 or8 with equal mass. ModelA draws0/4
equally given2 and4/12 equally given8. ModelB draws1/6 with probabilities4/5,1/5
given2 and6/16 with the same probabilities given8. Both satisfy E[Y|M]=M
and Var(Y|M)=2M. Both therefore have mean5 and variance10+9=19, whereas
the fitted means alone have variance9. Yet P(Y>8) is1/4 underA and1/10 underB.
The examples establish precisely why two moments neither identify a law nor
justify a particular tail. They are not calibrated claims data or a bootstrap.

For two conditionally independent cells sharing the same M, aggregate mean10
and variance20+36=56. Redrawing the two marginal laws independently instead
gives38, losing covariance9 per pair. If M=8 remains unresolved, retain mass1/2
and known mean contribution1; the full mean is withheld.

The original triangle still gives reserve148. Under the incremental GLM all
six observed increments fit exactly, so N−p=1 and phi=0. That observation
does not repair Mack's unobserved final-factor variance or supply a defensible
predictive tail. Return `DISPERSION_UNRESOLVED` for this illustrative input.

## Literal source error and package-specific alternatives

England2001 p5's negative-mean suggestion subtracts2m from a draw with
mean|m|. For m<0 its resulting mean is−3m; m=−4 gives12. It is wrong
relative to its stated mean target in the retained version. Translation by+2m
or reflection can produce mean m, but they impose different support and use
variance phi|m|, changing the positive ODP model. This profile returns
`MODEL_SUPPORT_FAILURE` and requires a separately reviewed signed-claims model.

Pinned ChainLadder0.2.17 source at commit5cd0dd441c3bb9e1ee6d7572d5bc1475f29be728
is implementation evidence, not the author paper. Its `od.pois` uses a
negative-binomial helper with size=m/(phi−1), not scaled Poisson. Both have
matching first two moments for phi>1; only one is confined to multiples of
phi. The helper is outside its parameter support at0<phi<1. The source also
uses signed gamma draws, resets the same seed in both stages and replaces
all missing process values with0. No unwrapped package output is accepted as
the specified law. No local R execution or installed-package compatibility is
claimed; the existing package remains a candidate for a later adapter audit.

## Horizon and validation obligations

The inspected2019 accepted manuscript §§3/3.2, equations5–7 requires closing
reserves conditional on the newly emerged payments for a one-year claims
development result: CDR=opening reserve−payments−revised closing reserve.
Opening100,payments30,revised closing80 gives−10;100−30=70 is not this result.
Lifetime future payments and one-year changes in estimated ultimate cost need
different query IDs and information sets. The paper's model-specific Appendix1
Mack-ratio bootstrap must not be replaced by an incremental ODP procedure
under the same name. Its analytic-comparison examples do not establish
empirical coverage, default readiness or a regulated risk measure here.

A future validation plan must define data vintages and group mapping, fit/tail
and calendar diagnostics, comparator tuning, heldout development diagonals,
proper scores/coverage with dependent-origin uncertainty, seed/budget ladder,
failure accounting, tail Monte Carlo error and downstream measurement checks.
Naive/contractual runoff, tuned classical reserving and proposed/enhanced
methods remain separate baselines. The source-specific consistency follow-up
and target-specific empirical protocol remain required before promotion.
