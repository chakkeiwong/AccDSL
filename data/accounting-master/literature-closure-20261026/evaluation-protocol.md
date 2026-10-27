# Estimation and solver evidence protocol

26 October 2026; MC23–26, MC29–35; W6/W8. This specifies the next evidence,
not a training run. E3 remains deferred under current program controls.

## Research intent

Question: does a specified policy/observation model explain issuer decisions
and improve the decision-relevant forecast under information actually
available at forecast time, while preserving financing and accounting
feasibility? Candidate: a joint hidden-contract/state and policy model with
explicit disclosure mechanism. Expected failure: observational equivalence,
selection bias, price-policy inconsistency, infeasible issued quantities or
low neural residual on the wrong objective.

Baseline ladder: (1) persistence and dated accounting cash projection; (2) a
tuned classical finite/state-space or structural policy model; (3) the plain
proposed method; (4) the enhanced method with the additional learning or
compression component. All use identical vintages and feasible actions.
A classical model that is deliberately denied information available to the
new method is not a fair comparator.

## Identification map

| Quantity | Potential evidence | Restriction still needed | Discriminating next evidence |
|---|---|---|---|
| Fixed/floating fraction, maturity and covenants | Notes and actual agreements | Missing terms cannot be inferred from a single balance | Additional contract/interest-reset observations; preserve unidentified set |
| Recovery and creditor ranking | Security and entity records, realized workouts | Liquidation costs, collateral and legal enforcement | Dated estate and creditor allocation; conservation checks |
| Issuance costs and market access | Gross proceeds, fees, failed/refused issues | Selection into successful offerings | Include attempts/refusals, not just executed issues |
| Investment/payout response | Dated actions and opportunity variables | Preferences, governance and opportunity shocks are confounded | Off-support shock cases or defensible identifying restrictions |
| Disclosure mechanism | Publication and silence, reporting rules | Missingness often depends on latent state | Sensitivity across plausible selection/likelihood mechanisms |
| Ownership and conversion | Register, prospectus, options, dated terms | Market value differs from book equity | Share-count reconciliation and contingent allocation |

## Pass/fail roles fixed before execution

- Primary criterion: a predeclared paired out-of-sample score or decision loss
  for a named target and horizon, with uncertainty sufficient for the intended
  ranking. Actual units and economically relevant margin must be set after the
  target/data are specified; no convenient universal threshold is invented.
- Promotion veto: invalid information cutoffs, lost rare types, failed cash or
  ownership conservation, wrong pricing measure/objective, unacceptable
  feasibility errors, or uncertainty too wide to support the proposed ranking.
- Continuation veto: corrupted data, invalid comparison harness, missing
  mandatory target observations or broken numerical reference. Candidate
  failure alone triggers the planned repair, not abandonment.
- Repair triggers: low residual with bad downstream policy -> inspect objective
  and gradients; boundary failures -> retain discrete regimes/refine near
  thresholds; type extinction -> explicit conditional strata/rejuvenation;
  selection sensitivity -> weaken inference or improve observation model.
- Explanatory only: loss curves, runtime, number of particles, source count,
  training-point accuracy and fit on observed support.

## Data and evaluation design

Freeze filing bytes, event availability, restatements and forecast origins.
No future restatement enters a past origin. Keep delisted/defaulted issuers
and publication delays. Separate fitting, tuning, calibration and final
evaluation periods; common macro shocks require time-aware dependence.
Predeclare paired issuer/time-block intervals or another justified dependence
model. Do not rank continuous metrics from a few seeds without uncertainty.
Tail losses require enough independent events; otherwise report descriptive
results and the attainable precision. Unweighted sets are assessed as sets,
not converted to probabilities by counting witnesses.

## Neural target protocol

Derive full coupled Bellman/pricing/constraint residuals in dated units. Check
conditional expectation versus mean-square, all price/state derivative paths
and boundary feasibility on exact cases. Use classical solutions as references
where available. Specify capacity and optimizer search, budget ladder, seed
policy, heldout states concentrated near economically consequential boundaries,
and downstream cash/default/ownership tests before training. Transfer of the
Krusell–Smith notebook defaults is only a baseline hypothesis. Pure repeated
TensorFlow kernels require explicit stable signatures; pfor remains prohibited
without the separately required approval. XLA requires its own compatibility,
memory, numerical and downstream checks before adoption.

## Required artifact and non-conclusions

A future run manifest records exact source hashes, command, environment,
data versions, seeds, wall time, hardware and plan/results. Record engineering
correctness, numerical validity and scientific interpretation separately.
A passed score cannot establish accounting compliance, causal identification,
a complete family of histories, or correct behavior outside evaluated support.
This protocol supplies no empirical ranking or approved numerical default.
