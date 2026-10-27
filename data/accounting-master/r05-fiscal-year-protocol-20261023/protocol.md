# Next full fiscal-year operating cash flow for the nine named companies

The selected question is expected forecast performance at future dates for
Apple, Caterpillar, JPMorgan, Henkel, HSBC, Munich Re, SAIC Motor, Ping An and
Midea. Each company contributes one ninth of the main result after the same
as-of asset scaling is applied to both competing forecasts. The target is the
next complete fiscal year's operating cash flow, with a named information
cutoff before that year begins. `choice.json` preserves both exact answers.

These choices determine the forecast horizon and company weights. They do
not determine the future time process, time weights, fitting window, forecast
service after failure, economically meaningful improvement, confidence level
or required sample. This is an implementable documentary proposal, with no
forecast, inference procedure or financial mapping admitted.

## A fiscal year is an interval, not a label

An annual target row records issuer, fiscal-year label, inclusive start and
end dates, the source supporting those dates, financial perimeter, accounting
basis, currency and unit. Its computational interval is [start, end+one day),
with the original inclusive dates preserved. Calendar dates become instants
only under a justified timezone/boundary convention. Unknown intraday timing
remains an interval, not an invented midnight timestamp. Cash flow is summed
over the actual fiscal interval; it is not a rolling 365-day amount or an
annualised partial year. No duration adjustment of the score is selected.

For cutoff c and an ordered, sufficiently complete admitted fiscal calendar,
choose the earliest full fiscal interval whose start s strictly exceeds c.
The calendar must show no omitted earlier eligible interval. A target start
equal to c fails this strict rule. Use conservative time-bound predicates from
the completed forecast-accountability proposal when either value is uncertain.
An overlap of bounds is unverified, even if a point estimate would pass.
This selection rule is applied before model success or losses are observed.
If the named interval cannot be forecast, preserve its failure; do not move it
to the next year and retain the original analysis identity.

One fiscal-year label must identify one full interval for the chosen company
and financial scope. A changed year-end, short transition period, merger or
changed reporting perimeter triggers a versioned target review. Do not label
a short transition period a full ordinary year or silently delete it. An
unsupported target remains recorded as unsupported under the locked policy.

The nine 2025 annual reports were inspected only for these calendar passages;
exact LF-line quotes and original/text hashes are in `calendar-sources.json`.
Apple's report states a 52- or 53-week year ending on September's last Saturday,
with 52 weeks in 2025 and 2024 and 53 in 2023 (text lines 598–599). Its reported
2025 end is 27 September; subtracting 363 days gives 29 September 2024 as the
start of that 364-day interval. The other eight reports support calendar-year
reporting for 2025. Henkel and Munich Re give explicit January–December ranges;
SAIC, Ping An and Midea state the calendar-year policy; Caterpillar, JPMorgan
and HSBC give full-year cash-flow headers ending 31 December. No source here
establishes a later year's unchanged policy, its exact byte availability at a
past cutoff, or the accounting meaning of its operating-cash-flow measure.

As a conditional planning illustration dated 23 October 2026, extend those
calendar rules unchanged. Apple's FY2027 interval would start 27 September
2026, already elapsed; the next fully future interval would start 26 September
2027 and end 30 September 2028, a 371-day FY2028. For the other eight companies,
the next full interval would be 1 January–31 December 2027. These dates are
derived proposals, not issuer-announced schedules or selected forecast cells.
Waiting until a reporting year is labelled 2027 does not make its start future.
The exact planning calculation is checked without treating this extrapolation
as observed source evidence.

## Information and forecast issuance

Each target needs its own named cutoff, source-time convention and issue
deadline. Preserve protocol lock, input cutoff, model/refit lock, forecast
creation and forecast lock separately. For a prospectively issued full-year
forecast, the proposed additional condition is forecast lock < target start,
as well as the existing strict lock < first-outcome-release condition. A lock
after the start changes the prospective interpretation even when every saved
input has an earlier declared cutoff. Retrospective reconstruction remains a
separate evidence class. A cutoff by itself proves neither actual prior
issuance nor lack of private or previously exposed information.

Every predictor, training label, chosen hyperparameter, scenario assumption
derived from observations, scale and upstream dependency needs evidence of
availability no later than the cutoff. Protocol and tuning decisions informed
by later outcomes also count as exposure. A report's title year, financial
period end, signature date, filing event and local download time have different
meanings. The 192 existing selected-byte admissions remain false. Reusing a
retained annual report does not repair them.

In particular, a forecast of calendar-year 2027 made before 1 January 2027
cannot use a 2026 annual report first released during 2027. A latest available
interim report, or an older annual report, may be the information basis if its
exact version and all dependent data are admitted at the cutoff. Both arms
receive the same permitted information; older information does not become
more current merely because it is the latest available. A late source can
support a separately labelled sensitivity or future origin, not overwrite the
locked forecast's input set.

Define the primary outcome as the first public release of the specified
full-year operating-cash-flow amount, with the target scope and precision
resolved. It may appear in a results announcement before the annual report.
The corpus's rule requiring full reports for source acquisition does not make
the full report the first outcome release. Preserve conflicting, rounded or
partial announcements and reconcile the exact target before admission. Later
restatements retain separately dated sensitivity status. Filing-date evidence
for an annual report cannot prove that no earlier announcement existed.

The proposed scale-selection rule is the most recent reporting-date total
assets among substantively admitted, strictly positive amounts available at
the cutoff for the specified financial scope. Select the as-of version by the
declared revision policy; conflicting values or incomparable scopes remain
unresolved. Both arms use that identical amount A(i,t). Missing, nonpositive,
late or ambiguous scales refuse the scaled comparison while preserving any
separately valid raw score. This rule is a proposal requiring a source/meaning
audit; no actual asset value is selected here. In particular it does not require
unreleased assets at the immediately preceding fiscal-year end.

## Equal companies and the missing time distribution

For issuer i at eligible origin t, define the negatively oriented difference

    d(i,t) = [CRPS(F_candidate(i,t), Y(i,t))
              - CRPS(F_locked_comparator(i,t), Y(i,t))] / A(i,t).

Both probability laws must be complete with finite first moments. Scaling the
loss by A is equivalent to evaluating CRPS for the scaled outcome and forecast
law when A is fixed and positive: in the CRPS integral substitute x=A*z, so
dx=A*dz. This normalization gives a unitless loss; it does not make firms
equally important by itself. Raw scores are still reported. It also does not
make accounting scopes equivalent or justify probabilities on unweighted sets.

Let E_i be issuer i's original eligible origins and b(i,t)>=0 its predeclared
within-issuer weights with sum over E_i equal to one. Then

    D = (1/9) sum_i sum_(t in E_i) b(i,t) d(i,t).

Each issuer's total weight is exactly 1/9, even when planned histories differ
in length. Uniform b=1/|E_i| is one possible finite-sample design, not a selected
time law. If E_i is empty, its required positive contribution is undefined;
remove neither that company nor its one-ninth share. Choosing equal weights
over all observed cells instead gives companies with longer surviving histories
more influence, a different objective.

For a simple nine-company illustration, one company has one cell of loss
difference -8; each of the other eight has two cells, both equal to +1. Equal
companies with uniform within-company weights give D=0. Equal cells give
8/17. Those two numbers answer different questions even with complete data.
If the -8 cell is missing, the original-weight observed contribution is 8/9
with covered weight 8/9. The survivor mean is 1, while the full D is unknown.
It must not be filled with zero, reported as 8/9, or silently replaced by 1.
If a model issued no law, its CRPS is undefined, not merely a missing numeric
observation; a service/fallback definition would be needed first.

For future expected performance write

    Delta = (1/9) sum_i E_(Q_i)[d(i,O_i)].

The Q_i describe issuer-specific future origins, information and refitting
under an explicitly joint data process. The choice of nine firms fixes
membership; it does not identify these laws or stability over future regimes.
Linearity of expectation requires integrability and no independence assumption.
Inference for a finite weighted estimator still involves every cross-term:

    Var(D) = (1/81) sum_(i,t) sum_(j,s)
                   b(i,t)b(j,s) Cov(d(i,t), d(j,s)),

when second moments exist. Same-year labels are not contemporaneous intervals.
Shared macroeconomic shocks, overlapping fiscal intervals, fitted parameters
and serial dependence remain. Missing origins can change Q when conditioning
on success. No independent-company bootstrap, horizon-minus-one truncation,
stationarity or finite variance is established by this derivation.

Several grouping proposals remain feasible: group by fiscal start year, by
fiscal end year, or retain asynchronous issuer sequences under a joint calendar
process. In the conditional illustration above, grouping the next future
intervals pairs Apple's FY2028 with the others' FY2027. Grouping by a common
fiscal label instead delays the calendar-year firms or includes an elapsed
Apple target. The protocol must name its grouping and waiting rule before
losses; no convenient relabelling can settle the dependence model.

## Refit and tuning obligations that can be specified now

The comparison concerns a forecasting policy, including its learning and
failure behaviour. The following fields must be fixed before the affected
outcomes. None is filled by a software package's default.

| Component | Required specification and smallest discriminating check |
| --- | --- |
| Training membership | Exact issuer/origin IDs, interval endpoints, label versions and availability. For each training label require release <= current cutoff; an earlier target start is insufficient. Check a year ending before cutoff whose annual result is released afterward. |
| Window | Fixed number of admitted annual outcomes, fixed elapsed calendar span, expanding history, or another explicit rule. They are different policies. Count usable observations and release lags before assuming any window is feasible. A minimum-history failure remains in the eligible denominator. |
| Features and scaling | Fit transforms, imputation and feature selection only on admitted pre-cutoff training/validation data; include preprocessing in the lock. Outcome-time assets or whole-sample normalization leak future information. |
| Validation | Ordered inner origins simulate the same next-full-year task and availability lags. Preserve issuer identities, fiscal intervals and shared shocks. Random rows or random companies do not reproduce the selected future-time claim. |
| Tuning | Declare candidate families, capacity/architecture choices when learned components apply, objective, hyperparameter ranges, budget ladder, seeds and stopping rule. Equal stated tuning cap applies across the baseline ladder; record actual effort and failed fits. No target-specific protocol means no promotion of inherited settings. |
| Economics and alternatives | Lock the scenario information, economic model and target scope across fixed interpretation and preserved alternatives. State which histories are unresolved and whether an admitted measure exists. A set has no CRPS until an independently justified probability law exists. |
| Comparator | Keep naive, runoff, tuned classical, fixed-interpretation, alternative-history and extension arms distinct. Lock the primary comparator by pre-test evidence and a declared selection rule. No test-outcome selection of the most convenient arm. |
| Cadence | Define what is retrained, retuned or frozen at each origin, what data are carried forward, and when weights/architecture are locked. A fixed estimation window in a paper does not establish this choice here. |
| Failure service | State whether the service refuses, supplies an already declared fallback, or reports a set; retain original failure and fallback use. No numeric penalty or presumed missing-at-random mechanism is selected. |
| Prospective lock | Retain exact predictive bytes, all dependencies, model identity, timestamps and exposure status before target start. A successful replay today does not prove historical issuance. |
| Resource feasibility | Record fitting/validation duration against the proposed cutoff-to-deadline gap before accepting a schedule. No feasibility run is authorised by this document. If an eventual approved training budget cannot support the target-specific protocol, report under-budgeting. |

The retained GW03 April 2003 source describes a fixed finite maximum estimation
window and a conditional-equality test. The completed source inquiry found no
direct justification for AccDSL's meaningful-margin upper bound, expanding
history or this asynchronous nine-company process. Both fixed and expanding
windows remain hypotheses requiring matched inference. That issue is not
resolved by observing that some forecasts could be fitted with either window.

## Remaining dependencies and concrete continuation

| Item | Current disposition | Required next evidence |
| --- | --- | --- |
| E3-R01–R03 | Future named companies, full-year horizon and equal issuer weights selected | No renewed preference question; preserve exact answers. |
| Calendar and cutoff | Historical calendar passages checked; future schedule and instants not admitted | Verify later calendar announcements/continuity and compare common-cutoff versus common-lead-time schedules under actual data release lags. Keep any extrapolated dates conditional. |
| E3-R04 | Future origin law, regime, grouping and time weights unresolved | Specify the temporal deployment question and assess whether historical or prospective observations can support it; examine dependence/stability, without fabricating a law. |
| E3-R05 | Chronology, denominator and refit obligations specified; actual fitting/failure service unselected | Assemble pre-cutoff training/validation feasibility by issuer, then justify window, cadence and service choices. |
| E3-R06 | All 192 selected historical versions unadmitted for as-of use | Establish exact-version availability from retained official bytes and dated archives, or make an explicit successor version with separate provenance. Early outcome announcements also require investigation. |
| E3-R07 | Full baseline ladder and score obligations preserved | Admit target/perimeter, positive scales and complete predictive laws before scoring; comparator choice follows pre-test tuning evidence. |
| E3-R08 | Inference unselected | Match the selected time process, fitting policy, dependence and one-sided margin target to checked theory and adequate data. |
| E3-R09 | Material improvement unselected | Identify the decision and cost of forecast errors; CRPS units alone supply no business-value threshold. |
| E3-R10 | Confidence, multiplicity and sample/resource design unselected | Use the inference conditions, temporal replication and decision risk; nine companies and 192 source files are not independent replication counts. |
| E3-R11 | Empirical/runtime execution held | Requires an admitted protocol, environment and execution scope. |

The next internal investigation is a source-timing feasibility matrix, using
the retained annual and last-interim records and their separate date roles.
It can identify which historical source candidates could precede a full-year
cutoff and which are already too late. Unknown selected-byte availability must
remain unknown even when a reported filing date precedes the cutoff. It can
also compare the prospective calendar proposals without selecting a Q or an
arbitrary lead time. It does not require rerunning source acquisition, fitting
models or receiving another answer to the two resolved questions.
