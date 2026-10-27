# Reconcile statements from a replayed shared-book prefix

24 October 2026. S2-S4; MC11/13/16/24/26/28/33; G4.

## Skeptical audit and evidence contract

Question: can the new return/lease book produce internally reconciled financial
views from its actual event prefix without pretending tax or a fiscal period is
complete? Baselines are the frozen SyntheticReturnLeaseBook/1 execution and
the original native_reports.py accounting identities. The old annual report
requires a tax close that this new profile cannot produce. Bypassing that
prerequisite or labeling recorded zero tax as a calculated tax amount is wrong.

Build a separately named read-only report. Recompute the prefix from opening
and ordered events; do not trust an arbitrary closing state or copied totals.
State whether execution completed or stopped, the completed prefix length,
last completed date and any failed event. Statements describe recorded
postings at that date, not the unexecuted remainder or a complete fiscal year.
Tax assessment, period completion, source admission and annual-close readiness
remain explicitly unresolved. Recorded current/deferred tax may be shown as
account balances but never inferred as the full required tax charge.

Primary pass: all25 accounts have exactly one classification; assets less
liabilities equal equity including recorded profit; opening equity plus
recorded profit and declared owner movements reconciles to closing equity;
gross cash receipts/payments match the event flows and balance movement; the
indirect operating cash bridge removes the noncash lease gain and depreciation
and includes the return/inventory working-capital movements. Require a fresh
zero-income/no-flow opening and unchanged owner-capital accounts in this finite
profile. Do not invent an ownership flow or use a balancing plug.

## Assumptions, diagnostics and work

Account classes extend the original return report with ROU as asset, lease
liability as liability and other_gains as income. Debit-positive signed balances
are the baseline convention. The historical interest election and synthetic
opening are inherited explicit assumptions, not current accounting authority.
Five-event replay yields recorded profit5 and cash361; the early test must
derive these from accounts and events, not constants in reporting code.

1. Pin frozen execution and native report references. Define closed request,
   recorded-only statements, coverage obligations and source limitations.
2. Implement replay-based balance-sheet, income, equity and direct/indirect
   cash views. Unknown tax stays separate from recorded arithmetic.
3. Check mixed and isolated sequences, empty prefix, stopped-funding prefix,
   unsupported inputs, nonzero opening income, retained original controls,
   forged statement/result and full replay.
4. Record complete cases, tests, equations and result; refresh controls and
   integrate into a protected manuscript successor before next coverage review.

A failed accounting identity or hidden unknown vetoes the report candidate;
repair it before recording. Missing full tax is an explicit acceptance boundary,
not a reason to stop this finite reporting design. Stop only on corrupted
protected evidence or an unresolved material semantic decision. Exact CPU
checks, no forecasts/GPU/external service/paid review. Evidence directory:
data/accounting-master/shared-book-statements-20261024/.
