# R05 — predictive history weights and locked selector

23 October 2026. P17/P19; MC04/08/10/12/14/18/26/33–35; G1/G2/G6/G10/G15–G18.
Output: `data/accounting-master/r05-weight-selector-20261023/`.

## Question

How can the preserved-history candidate produce a predictive law, and how can
its fixed-interpretation comparator be selected, without treating solver branch
counts or duplicate encodings as probabilities and without looking at a future
confirmation outcome?

The selected E3 target is expected future operating-cash-flow predictive
accuracy for the same nine named companies. The primary comparison is
candidate minus a locked fixed interpretation under the same information,
economic kernel, target, asset scale, fitting budget and service policy. This
unit develops the procedures; it does not fit a company forecast or choose a
confirmation grid.

## Skeptical audit and evidence contract

A posterior over histories would require an identified observation likelihood
and prior. Neither is admitted by the current source records. Equal weights over
syntactic branches would double-count duplicate encodings, while a selector
chosen after the outcome would be an oracle. The annual panel also leaves few
strict pre-start origins. These are material risks, so the primary proposal uses
forecast-combination coefficients learned only from earlier development origins,
and retains an explicit set-valued path when a law cannot be justified.

Evidence contract for the exact reference is: (1) canonical semantic histories
must conserve mass when an encoding is split or merged; (2) simplex weights must
be finite, nonnegative and sum to one; (3) the mixture CRPS objective must use
only labels released by the later fitting cutoff, while each earlier forecast
uses its own pre-start information; (4) selector ties must be
deterministic and locked before the affected outcome; and (5) missing components,
late labels and invalid laws must refuse the probabilistic score rather than
drop mass or renormalise. The synthetic pass is explanatory evidence only. It
cannot establish forecast quality, a probability measure over true histories,
statistical ranking, or readiness.

## Procedure proposal

1. **Semantic quotient.** Convert each reconstructed history to a canonical
   semantic identifier containing its source-supported assertions, joint
   accounting state and future forecast kernel fingerprint. Equal journals with
   different future kernels remain distinct. Multiple encodings of the same
   identifier are one component; their mass is aggregated before fitting.
2. **Development cells.** For an issuer and forecast origin, construct the
   current admitted family and the component laws using the common economic and
   behavioural model. Build earlier pseudo-origins under their own strict
   cutoffs. Its law, target definition, inputs and scale must be eligible at
   that forecast cutoff. Its outcome is released later and may enter a later
   fit only after release and by that later fitting cutoff. These three dates
   must be recorded separately.
3. **Forecast-combination weights.** Component labels can change as evidence
   accrues, so a raw simplex vector over the current rows is not automatically
   learnable from earlier origins. A candidate solution is a predeclared,
   versioned feature map and score function that gives each semantic component
   an as-of score, normalises scores over the current canonical family, and
   learns its parameters by minimising earlier-origin asset-scaled CRPS of the
   resulting mixtures. All eligible training origins contribute under the
   same equal-company objective; within-company time weights remain to specify.
   These are forecast-combination coefficients, not posterior probabilities
   that histories are true. The feature map, score family, penalty and tuning
   budget are not yet selected. No branch count, syntactic multiplicity or LLM
   confidence supplies a weight.
4. **Fixed selector.** A fixed interpretation also needs a stable procedure
   when the current history family changes. A candidate is a predeclared
   feature-based selector trained on the same earlier-origin data and budget,
   then applied to the current canonical family. A source-priority rule is a
   distinct candidate and has no predictive-selection claim. Lexicographic
   semantic-ID ordering is only a deterministic exact-tie rule after the
   substantive selector has scored the alternatives. No selector may inspect
   the affected outcome.
5. **Stable feature requirement.** Current and earlier cells must expose a
   predeclared feature map whose meanings persist across origins and issuers;
   this is a target-specific transport assumption, not supplied by canonical
   IDs alone. If this map, sufficient eligible history or a complete component
   law is unavailable, the cell is `law_unavailable` and the result remains
   set-valued. Equal weights are not a repair. A pooled feature-weight model
   introduces shared-fitting dependence that must be declared.
6. **Strict matching.** Candidate and fixed arms use the same source versions,
   target mapping, positive asset denominator, economic kernel, training rows,
   inner-origin budget, forecast lock, and fallback policy. A separately tuned
   arm is a broader procedure comparison and cannot be attributed solely to
   mixture integration.
7. **Failure and revision.** Invalid or incomplete laws, late labels, missing
   scales and service failures remain attached to their eligible rows. The
   aggregate is unavailable unless a fallback was locked in advance. No company
   or component is dropped and the remaining weights are not renormalised.

The finite optimisation is convex in the mixture CDF for fixed component laws;
that mathematical fact does not make the fitted coefficients probabilities over
truth. The exact reference below uses persistent synthetic component IDs only;
it does not test the unresolved cross-origin feature map or establish that the
real nine-company panel can estimate it. A separate Bayesian mode remains
possible only after a declared prior, observation likelihood, duplicate policy
and dependence treatment are admitted.

## Defaults, assumptions and promotion boundaries

The semantic quotient and forecast-combination interpretation are design
requirements for this proposal. The number of validation origins, minimum
history, penalty grid, stable-family map, service fallback, future origin grid,
time weights, confidence level and multiplicity procedure remain unselected
scientific choices. They must be frozen in the historical-development result
before prospective confirmation. Candidate weights and selector output are
promotion evidence only through the predeclared paired CRPS uncertainty analysis;
validation loss, a synthetic identity, a passing smoke test or a finite panel
mean cannot rank a future method.

A hard veto is any information leak, invalid law, mass loss, negative/nonfinite
weight, target mismatch, unrecorded fallback, or missing required timing record.
An explanatory diagnostic includes component diversity, optimisation curvature,
number of active components and service rates. A failed candidate weight fit
triggers the set-valued or repair path; it does not reject the broader
history-preservation research direction.

## Execution and artifact

Run only the standard-library rational reference with `CUDA_VISIBLE_DEVICES=-1`;
no ML framework, acquired code, forecast runner, external publication or
historical admission is involved. Preserve the exact fixtures, result, manifest
and four control snapshots. Read-only replay must reproduce the checks.
