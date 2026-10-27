# R05 — changing-family feature procedure diagnostic

23 October 2026. MC04/05/08/10/12/14/18/26/33–35; P17/P19.
Output: `data/accounting-master/r05-changing-family-weights-20261023/`.

## Research question and skeptical audit

Can one predeclared feature-score procedure produce a predictive mixture and a
locked fixed interpretation when the set of admissible histories changes
between forecast origins, without transferring raw component IDs or leaking
later labels? Current proposals do not specify a feature map or fitting model.
This diagnostic tests only the bookkeeping of one candidate on a tiny synthetic
panel. A stable feature map may itself fail to transport across accounting
regimes; the toy cannot decide that issue.

Audit for false evidence: hard-code no company data; make target/outcome timing
explicit; include a new feature absent from eligible training data; prove
duplicate encodings leave canonical output unchanged; do not call score weights
probabilities over true histories; and do not treat synthetic CRPS improvement
as a promotion test. Exact rational checks and a deliberate unavailable case
are more informative here than a stochastic or long run.

## Candidate and evidence contract

Fixture-only candidate: group earlier, released component CRPS by a stable
synthetic feature; take the mean loss by feature; assign positive rational
score `1/(1 + loss)` to each trained feature; normalize over
current canonical histories to obtain forecast-combination coefficients. The
locked fixed comparator chooses the current component with lowest eligible
feature mean loss, with a lexical canonical-ID tie break. The additive constant
1 is a fixture convenience for dimensionless scaled CRPS, not a selected
hyperparameter. A current feature with no
released training loss makes the paired probabilistic comparison unavailable;
the complete family is retained for the set-valued analysis. It is never
dropped or renormalized. This additive diagnostic does not amend the earlier
candidate unless it survives separate methodological review.

This score transform uses means of component CRPS, not minimization of mixture
CRPS. It therefore instantiates a different candidate from a directly optimized
mixture. Component-score fitting cannot be described as optimizing the mixture
objective. Stable feature meanings and their training aggregation remain
unreviewed for real issuers.

Pass criterion: exact enumeration satisfies semantic duplicate invariance,
feature-family changes, strict order
`forecast_lock < outcome_release <= later_fit_cutoff`, no current-outcome use,
deterministic locked selection, simplex validity, and whole-cell refusal for an
unseen feature. Veto on a leaked label, lost history, silently filtered company
or nonfinite/invalid forecast law. Report weight and selector losses only as
fixture outputs. No ranking or model promotion is possible. Compare this
per-member normalization with a candidate repair that first allocates mass
to features, then explicitly divides it among their distinct current members.
Neither sharing rule is implied by semantic deduplication. Cardinality
sensitivity is a repair trigger, not a veto on studying the repair. A third
candidate first quotients identical target-specific forecast laws while
leaving the richer semantic histories intact for other outputs. It must refuse
if one identical forecast law receives contradictory stable features. This
tests whether duplicate OCF laws, rather than merely duplicate encodings, can
distort a forecast mixture.

## Default and assumption audit

| Choice | Provenance and justification | Failure mode | Early diagnostic | Status |
|---|---|---|---|---|
| Feature grouping | Explicit synthetic fixture; makes changing IDs testable | Feature may not carry accounting meaning across origins | Same feature with changed source-supported kernel | Hypothesis only |
| Inverse score, additive constant 1 | Positive rational transform for a hand-checkable diagnostic | Sensitive to scale and constant; tuning can leak | Exact monotonicity plus nested-timing check | Convenience fixture |
| Equal current mass per canonical member within feature | Candidate normalization | Distinct histories collapsed by features may inherit arbitrary within-group sharing | Duplicate and cardinality counterexamples | Unreviewed risk |
| Exact point laws and small panel | Hand-checkable arithmetic | Says nothing about continuous OCF tails | Separate mathematical law test required | Diagnostic baseline |
| All-or-nothing unseen-feature refusal | Prevents silent removal and renormalization | Frequent fallback can make method unusable | Count unsupported current features | Safety convention under test |

## Budget, pre-mortem and next step

CPU-only standard-library rational checks under five minutes; no internet,
GPU, empirical data or environment changes. A run could pass while the feature
map is economically meaningless. It could fail because the fixture lacks
eligible released outcomes rather than because history preservation fails.
Smallest distinguishing checks are feature perturbation, delayed-label refusal
and duplicate/cardinality tests. Artifact: exact result, run manifest and
completion hashes in the output directory. Continue only to design review and
alternative-feature counterexamples; this unit cannot trigger a company run.
