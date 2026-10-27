# E3 observations, target questions and dependence records

This is an additive proposed design for future validation. It supplements the
unchanged Version 3.44 E3 contract. No company outcomes are scored and no
historical forecast, uncertainty procedure or empirical run is admitted.

## Three different questions

The unit is a forecast for one issuer, information origin and fully identified
target, evaluated against one pinned outcome version. A report can supply several
inputs or outcomes, and several forecasts can refer to the same outcome. The
192 reports are therefore neither 192 forecasts nor 192 independent losses.
`target-sheets.json` preserves three alternatives without selecting one.

A finite-panel description asks what happened on named eligible forecast cells.
For a fixed, fully observed paired set A and predeclared nonnegative weights
summing to one, its quantity is D_A = sum a_c d_c, where d_c is the candidate's
loss minus the locked comparator's. This is an exact description if the scores
are evaluated exactly; numerical score approximation retains its own error.
It needs no population confidence interval to describe those observed cells.
It supplies no confidence bound for future issuers or future origins.

Repeated-origin prediction instead fixes the issuer panel and asks about
expected loss under a specified joint law Q for origins, future information,
outcomes and any refitting. Its target could be E_Q[sum_i w_i d_(i,O)]. The
law must say how origins are selected, what regime and horizons are relevant,
and what policy refits or retunes the forecast. A long-run stationary mean is
another assumption, not a synonym for this expectation. Resampling historical
rows does not itself justify stationarity, exchangeability or the required
dependence conditions. Evidence for named issuers does not establish transfer
to new issuers.

Future-issuer prediction asks about E_P[d_(I,O)] under a defined issuer/origin
deployment law P. A frame, inclusion or transport argument, weights, strata and
service-coverage policy must give that expectation substantive meaning. The
nine purposive issuer families do not supply inclusion probabilities or a
representative issuer population. Enlarging their report count cannot repair
that missing argument.

These expectations include the specified fitting policy and information rule.
They do not silently condition on successful forecasts. If only common success
can be scored, report that conditional coverage result and its original eligible
denominator. A full-service effect needs an admitted fallback or a separately
justified missingness/design argument. No missingness assumption is supplied here.

## Proposed observation and comparison records

The following fields are obligations for a later protocol, not populated company
data or a registered runtime schema. Store original evidence separately from
interpretations and derived target values. Unknown fields keep null and a reason.

| Record | Required content and refusal/identity rule |
| --- | --- |
| Protocol and eligibility | Protocol/version, chosen question, frame and inclusion rule, strata, declared origin calendar/horizon rule, full eligible cell IDs and exclusions with reasons independent of candidate success. Freeze these and the weighting rule before test outcomes. |
| Origin | Timestamp with timezone/precision or a bounded time interval; information cutoff; prospective, retrospective or exposed-development status; target interval and elapsed portion. A forecast of a partly elapsed year is a different origin task from a full future-year forecast. |
| Target identity | Issuer/entity and group perimeter versions, actual statement concept/presentation, accounting basis, units/currency, gross/net or other necessary definition, flow start/end with boundary convention or stock measurement date, frequency and outcome-vintage policy. Different intervals or perimeters are different targets. |
| Predictor availability | Every raw source hash/version, locator and version-specific availability evidence, including macro inputs; derived-input dependency hashes and calculation version. Availability must precede the origin's information cutoff. Ingestion time and publication-event metadata remain separate. |
| Training and tuning | Exact training/validation rows and their availability; fit/version and shared-fit ID; fitted scale/feature and hyperparameter provenance; equal stated tuning caps, primary comparator lock and model-selection history. Each fit may use only labels available at its own cutoff. |
| Forecast | Candidate/comparator IDs, same economic assumptions and scenario condition, target/origin/information identities, forecast creation/lock record, law or set status, unresolved mass, finite-moment support, failure/refusal reason, any declared fallback, numerical scoring method/error and random-stream identity when relevant. |
| Realization | Source bytes/locator, first disclosure of the specified target amount and its available-at evidence, release precision, original presentation/basis/perimeter, exact value/precision and derivation if required. Later corrected or restated values are distinct dated sensitivity records linked to the first release. |
| Scale and secondary vector | Same strictly positive as-of known total assets for both models; its own source and available-at evidence; unscaled quantities too. Closing cash/financial debt share an identified date and perimeter; fixed component scales and an admitted joint law are required for the energy score. |
| Paired comparison | Both target/origin/information/score identities, locked comparator, candidate-minus-comparator orientation, original eligible weight, common-coverage status, paired losses where valid, full failure denominator and reasons. Do not replace unknown, refused or nonfinite scores by zero. |
| Design and inference | Chosen population/question, substantive weights and margin, inferential conditions, one-sided bound/level and multiplicity rule, critical-stratum veto roles, dependence and resource/sample justification, exposure/split manifest and separate execution authority. Null here means not admitted. |

An observation ID includes the origin and outcome-vintage policy. Repeated
forecasts of the same target at different origins retain different observation
IDs but one shared target/outcome link. A restated outcome changes that link's
version; it does not overwrite the first release or contaminate an earlier fit.
Deduplicating files by period is insufficient for either operation.

Record the actual forecast creation/lock date separately from its information
origin. A reconstruction created after the outcome became known is retrospective,
even if its input filter correctly implements an earlier cutoff. It cannot be
called an untouched prospective forecast; retain known author/model exposure.

Availability evidence must be at least as precise as the proposed cutoff rule.
For uncertain intervals, require the latest supported availability to be at or
before the earliest admissible inclusive cutoff, or refuse that origin. A declared release day
cannot justify use at 09:00 that day without time evidence. A timestamp for a
different accession, mirror or PDF cannot establish the selected bytes' vintage.
All 192 selected-byte availability values remain null in the frozen inquiry;
this specification does not repair them. Using a later justified origin or a
separately reviewed, explicitly versioned source panel is a possible repair,
not a silent reassignment of those frozen records.

For a year-to-date flow, predict that issuer's stated interval. To derive a
quarter from two cumulative disclosures, retain both values, versions, exact
subtraction and basis/perimeter reconciliation; the derived quarter is first
available only when all required inputs are available. A prior-period amount
in a later comparative is not automatically the first-released outcome.
Stock amounts use their measurement date rather than the flow interval. Do
not pool different frequencies, target lengths or stock/flow concepts merely
because all files carry the same fiscal-year label.

CRPS remains negatively oriented and requires an admitted complete probability
law with finite first moment. Scale all amounts by the same positive as-of asset
amount; missing/nonpositive scale refuses only the scaled comparison and stays
visible. An unweighted admissible set uses scoped inclusion/width/decision checks;
it is not assigned equal probabilities. Unresolved probability mass is not
normalized away. The secondary energy score needs the joint cash/debt law and
fixed component scales, alongside prespecified cash-shortfall and linked-statement
event checks. A vector of separate extrema is not that joint law.

Keep the full E3 baseline ladder, from appropriate naive and contractual runoff
models through tuned classical models, the structural fixed interpretation,
the same model preserving alternatives and a named extension. Match information,
economics, targets and tuning opportunities. Lock the strongest admissible
primary comparator using development evidence, before test outcomes; choosing
the favorable baseline after test results changes the comparison.

## Denominators, overlap and possible dependence

Let E be the frozen eligible set. Keep one row for every member, including
missing outcomes and failed forecasts. A predeclared rule generates common
scorable coverage A; disclose A, E, all reasons and any coverage-specific
weights. D_A describes A only. Neither deleting failures nor zero-filling them
identifies D_E. Any normalization for an A-only description must be labelled
and must not be presented as the original full-service weighted effect.
Candidate and comparator coverage, critical strata, target lengths and exposure
are reported alongside aggregate scores. A failure policy cannot be chosen
from the loss values it would remove.

For each pair of observations preserve the following relations independently:

| Relation | What is recorded | What it does not establish |
| --- | --- | --- |
| Same target/outcome | Identical target identity/version at different origins or in multiple tasks | A new independent outcome merely because there are more forecasts |
| Flow-window intersection | Exact shared calendar-day interval; same-issuer and cross-issuer labels remain separate | A numeric covariance or dependence magnitude |
| Shared source or derived outcome | Common release bytes, revisions or cumulative subtraction inputs | Independence of differently named outcomes |
| Shared issuer/perimeter | Common issuer family, consolidation lineage or economic exposure, even for disjoint periods | Independence after an arbitrary time gap |
| Common calendar/scenario | Overlapping exposure dates, shared macro/sector conditions or economic scenario | Only same-issuer dependence matters |
| Shared fitting/selection | Common training rows, fitted model, hyperparameter selection, data cleaning or forecast randomness | Independent cells simply because target intervals are disjoint |

The graph records known overlap and plausible common mechanisms, not measured
covariance. Missing edges mean not recorded, not independent. A complete list
of observed edges still does not identify an effective sample size, validate
cluster resampling, justify a bandwidth or establish sufficient replication.
Dependency metadata must retain external/common-shock risks too.

A split manifest records every training/validation/test assignment and each
cutoff. Test outcomes must not be used in a fit, normalization, tuning choice or
protocol selection before their release. Overlapping target periods and shared
outcome inputs need an explicit boundary rule and any embargo/gap justified by
the chosen scientific design. “One-year horizon” or grouping files by issuer
does not derive an adequate embargo. Legitimately using a released past outcome
at a later origin can be part of a frozen rolling-refit policy; it must not be
misreported as an untouched one-shot holdout. No blanket embargo length or
split-independence claim is adopted here.

## Exact illustrations and their limits

The six fictional cells use explicit half-open calendar intervals. A1/A4 predict
the same annual target at different origins; A4 is partly elapsed. A1/A2 overlap
for 184 days; A1/A3 for 92. A1/B1 have overlapping calendar exposure across
issuers. A1/C1 have disjoint issuer and calendar targets but share a fitting ID.
These are witnesses for distinct relations, not actual issuer forecasts or a
covariance model. The checker independently compares endpoint intersections
with enumerated calendar-day intersections for all fifteen pairs.

For separate fictional losses (-2,-2,-2) on issuer A and 5 on issuer B, equal
cell weights give (-6+5)/4 = -1/4. Equal issuer weights give (-2+5)/2 = 3/2.
Both are legitimate finite descriptions of different predeclared objectives;
the sign reversal cannot select a deployment objective. It is not a stochastic
ranking and supplies no business margin.

The coverage illustration has four eligible cells but only two valid paired
scores, each difference -1. Its paired mean is -1; the full four-cell effect is
unknown. One candidate has unresolved mass; another target is unknown for both
models. Keeping the denominator at four does not authorize dividing the two
observed differences by four. No fallback or missingness assumption is admitted.

The earlier exact covariance derivation remains applicable only under its stated
synthetic law. Pairing does not remove issuer, calendar or shared fitting
dependence. An E3 promotion still requires a defensible uncertainty bound below
-m, all validity vetoes and a justified material margin. No matched inferential
theorem, sample size or confidence level is selected by these examples.
