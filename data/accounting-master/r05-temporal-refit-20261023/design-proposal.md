# An annual forecasting policy with release-aware fitting

The proposed policy issues one distribution for each company's next full
fiscal year, before that year begins. It retains the named company panel and
the user's equal company weights. The issue schedule, fitting rule and
failure behaviour are parts of the forecasting method being compared. A
numerically successful fit does not define them after the fact.

## What the eight annual years can supply

Let a company's consecutive ordinary full fiscal intervals have labels y.
Write s_y for the start of year y, so the half-open end of y-1 is s_y. At the
required cutoff c_y<s_y, year y-1 is unfinished. Its actual full-year outcome
is therefore unavailable, even if an early announcement estimates it. Such
an estimate can be a separately identified feature; it is not the eventual
realised OCF training label. A forecast with a later cutoff is a different
task from the selected pre-start full-year forecast.

Consequently, within the retained 2018–2025 labels, a target y has at most
max(0,y-2018-1) usable same-company annual labels: 2018 through y-2. This
optimistic bound assumes every such older label is already released and
correctly mapped. Actual publication delays and mapping failures can only
reduce it. It also assumes unchanged adjacent full-year calendars; transition
periods require the actual interval calculation instead of a label shortcut.

Let r be the minimum number of earlier annual labels needed to fit, and v the
number of earlier inner forecast origins required for tuning. An inner origin
j is possible only if j>=2018+r+1. Its full outcome must also be complete
before the outer cutoff, giving j<=y-2. There are therefore at most

    max(0, y - 2018 - r - 2)

such inner origins. For v=0 the earliest outer label is 2018+r+1; for v>=1
it is 2018+r+v+2. These are necessary timing/count conditions, not sufficient
training protocols or statistical sample-size claims.

| Minimum earlier annual labels r | Inner origins v | Possible outer labels per company | Maximum company-origin cells |
| ---: | ---: | --- | ---: |
| 1 | 0 | 2020–2025 | 54 |
| 3 | 0 | 2022–2025 | 36 |
| 5 | 0 | 2024–2025 | 18 |
| 1 | 2 | 2023–2025 | 27 |
| 3 | 2 | 2025 | 9 |
| 5 | 2 | none | 0 |

The r and v values are deliberately small sensitivity examples, not chosen
windows or adequate budgets for a particular method. Zero inner origins
describes an externally fixed rule; it does not satisfy the tuned-classical
baseline obligation by itself. The 72 annual reports are source inventory,
not 72 independent tests. Interims can improve features if admitted; they do
not create new full-year labels. Pooled training may use additional companies'
older labels under an explicit model and timing rule, but that is a different
policy and creates shared-fitting dependence. The same-issuer bound above
must not be misreported as a universal impossibility theorem for pooled or
externally trained methods.

## Proposed temporal indexing and weights

Use fiscal start year k as a proposed common index while retaining every
actual issuer interval and cutoff. Under unchanged calendars, Apple's
September-start year is labelled k+1, while the other companies' January-start
year is labelled k. This indexing keeps starts within a common civil year;
it does not align exposure intervals or create independent cohort shocks.
An Apple interval beginning in September k overlaps calendar-company
intervals in k and k+1. Serial dependence can extend farther.

This proposal has a practical cost for retrospective inventory. If all
companies only have potential outer label 2025, Apple supplies start year
2024 and the others start year 2025: there is no complete common start-year
cohort. With outer labels 2024 and 2025, only start year 2024 is complete.
The conditional cohort calculation is retained separately. Grouping by end
year would avoid this particular endpoint loss but would index intervals
whose starts occur in different civil years. Neither convention establishes
independence. The proposed start-year grouping is not silently selected as
the final study design.

For a predeclared future grid K of complete named-company start-year cohorts,
a concrete finite design proposal gives b(i,k)=1/|K| for every company and
defines

    Delta_K = (1/(9|K|)) sum_i sum_(k in K) E_Q[d(i,k)].

It is the expected performance of this forecasting policy over that specified
future grid, conditional on a declared starting information set if desired.
Its realised D_K uses the same fixed weights. Linearity makes E[D_K]=Delta_K
for observations drawn from that very joint law with defined integrable
scores. It does not let historical 2018–2025 observations estimate an arbitrary
future law. A transport or stability argument is required for that step.
The grid, its start, length, cutoff instants and conditional information set
remain to specify; no unbounded stationary future claim is inferred.

## Proposed fitting and service record

For every issuer/cohort, retain a protocol record before the affected outcome:

1. Actual full-year interval, target mapping version, cutoff instant and
   forecast-lock deadline strictly before the target start. Use a named
   timezone and publication-bound rule; a day-only source does not become an
   exact midnight. The cutoff lead time is a study parameter, not a package
   default chosen here.
2. Admitted source versions and target/scale meanings. Every training label
   must have a completed interval, eligible availability and valid mapping
   by that fit's cutoff. A later revised comparative value cannot overwrite
   an earlier permissible label. All input transformations follow the same
   evidence boundary.
3. A fitting family, minimum history, window rule, tuning candidates and
   bounded resources justified for that target. Fixed-count rolling,
   elapsed-time rolling, expanding and frozen-fit rules are competing policies.
   The count analysis does not select one or establish capacity adequacy.
4. Ordered inner origins, each reconstructed under its own earlier cutoff.
   Their realised labels may be used for selection only after their own
   availability and before the outer cutoff. Record every failed fit and the
   selection tie rule; do not choose settings on outer losses. Equal caps and
   matched economic/scenario information apply to the full baseline ladder.
5. A fixed primary comparator selection rule. The primary contrast remains
   preserved-alternative histories versus the locked fixed interpretation;
   naive, runoff and tuned-classical results retain their own roles. Different
   accounting mappings or extra information cannot be credited as an effect
   of preserving alternative histories.
6. Forecast bytes, probability-law validation, service status and later
   first-release outcome identity. An output set stays set-valued if no
   justified measure exists. No automatic fallback is selected: missing
   positive-weight laws leave the full score unavailable. A proposed fallback
   must be specified and evaluated as part of the policy before use.

Each inner fit repeats the whole selected preprocessing and tuning policy;
reusing transformations learned on future outer data leaks information. A
model fitted with older labels can use current admitted interim features when
its feature definition permits that pattern and comparable training features
were constructed at their own cutoffs. Training on final full-year features
and deploying on partial-year features needs a distinct justified model.

## Consequence for inference and the next repair

An interval for Delta_K must address common and serial shocks, asynchronous
fiscal overlap, shared tuning and model failures. The small counts do not
justify a company bootstrap, a normal approximation or a default bandwidth.
The inspected April 2003 Giacomini–White source does not settle this: its
finite-window conditional-equality setting is not automatically a one-sided
future-grid performance interval for these nine asynchronous issuers.
Stationarity, dependence rates, moments and future transport remain unchecked.

IFRS18/IAS7 changes from 2027 further weaken an unexamined stable-target
assumption for the IFRS companies. The next source task is a dated technical
check of the cash-flow amendments and application dates, followed by exact
release/scale evidence. Historical relabelling or adding more training rows
cannot by itself repair a changed target. If the admitted sample cannot
support a target-specific tuning and inference protocol, report that design
as under-supported and consider a longer predeclared prospective collection
or a different explicitly justified model. Do not reduce the selected research
question to a favorable descriptive average.
