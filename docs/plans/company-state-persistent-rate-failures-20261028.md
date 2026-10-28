# Persistent loan type and dated rate shocks: SIM-F011/018

28 October2026. Ready C04 continuation, MC08/09/10/11/14/18/26/28/33.
Original criteria and failure statuses remain unchanged; T07 is still planned.

## Skeptical plan audit

The original SIM-F011 example is a100 loan fixed at5% or floating at7% for
each of two years. Its admissible paths are(5,5) and(7,7). The earlier same-date
fixed/floating mixture and finite policy examples do not establish this exact
two-year claim. Use an explicit persistent binary variable in the existing
rational solver, and execute each retained loan through two years and an actual
native annual carry. Compare full states and both annual reports.

The native retained financing builder does not implement floating reset rules.
Do not describe it as such. A separate bounded exact schedule diagnostic will
handle SIM-F018: fixed coupon versus reference rate plus fixed spread; a shock
enters the reference path once and only at the applicable reset. The resulting
schedule is engineering evidence, not a native floating-contract admission.
The two-year native example has supplied constant coupon amounts, not a general
schedule engine. Keeping those limits explicit repairs the main possible
baseline error; the bounded plan passes audit.

## Research intent and evidence contract

Question: do persistent-type constraints preserve joint paths across dates,
and does a dated200bp reference-rate shock affect only eligible reset exposure?
Candidate: unchanged rational solver plus declared native carry; separate
explicit synthetic schedule. Comparators: enumerate the original two types;
independent exact date-interval arithmetic and source half-year limiting case.
Expected failures: mixed(5,7)/(7,5) paths, carry dropping type/coupon, fixed
coupon shocked, spread shocked too, shock doubled, or effect preceding reset.

Primary pass: exact path set and cross-year books/reports match; mixed paths
are infeasible under persistent scope, feasible only under deliberately redrawn
scope; schedule amounts match independent rational formulas at each date.
Vetoes: incorrect state/report, lost unresolved budget, wrong date/rate target,
corrupted source or protected mutation. Harness errors trigger repair of that
check. A deliberately incorrect candidate is a promotion veto, not a reason
to stop unrelated ready work. Counts and timing are descriptive only.
Nonconclusions: no inferred prior, probability, actual loan terms, pricing,
accounting/source admission, general ACTUS/calendar compliance or T07 closure.

## Assumption/default audit

| Choice | Provenance and reason | Failure / early check | Status |
| --- | --- | --- | --- |
| Principal100; coupon5/7; two years | Original03-learning.tex example | Replacing target with contemporaneous mix; enumerate four pairs | Baseline |
| No amendment/refinancing | Original persistent-type premise | Silent change; type equality and preserved native memory | Scope hypothesis |
| Cash20, inventory100, debt100, equity20 | Common authored opening, enough cash for either path | Funding confound; all balances and prefixes checked | Convenience fixture |
| Binary type; no weights | Original unweighted family | Invented posterior; retain null probabilities | Reviewed scope |
| Explicit solver budget | Same bounded exact backend as prior failure work | Resource exhaustion called infeasible; zero-budget control | Convenience cap, not coverage evidence |
| Fixed5%, reference3% plus spread2% | Equal initial coupons isolate rate target | Double shock to spread; independent formula controls | Authored diagnostic |
|2027 actual days/365; resets Jan1/Jul1 | Exact dated example; no leap-year ambiguity | Annual average masquerading as half-year; count181/184 days | Declared convention |
| Shock effective at reset included | Explicit boundary convention | Off-by-one; before/on/after-reset cases | Hypothesis |
| Native coupon and carry preserve supplied amounts | Retained typed runtime | Calling it a reset implementation; separate result sections | Engineering baseline |

## Execution

Write only under company-state-persistent-rate-failures-20261028 and this plan.
Fresh attempt directories retain inputs, formulas, complete native/solver
results, source locks, original rows and run manifests. Use python3 -B on CPU,
no accelerator imports, installations, stochastic training or external sources.
Run exact diagnostics, relevant existing tests, program validation and fresh
protected-file checks. Record decision/inference tables; refresh C04 and the
next ready phase. Preserve the original manuscript and frozen code.
