# Repeated item additions preserve cumulative hedge measurement

16 October 2026. Accepted attempt02 passes142 exact checks with zero failures:
six independently authored observations, two additions,39 adverse requests and
one comparison with fewer observation dates. Attempt01's136 checks remain
preserved; the subsequent audit added context unit/risk/source-version guards.

The claimed target is a continuing cash-flow hedge with an unchanged
instrument, a single price risk, zero discounting and repeated increases in
the hedged purchase volume. Actual admissibility and valuation completeness
are supplied findings. The calculation retains each layer's designation date
and price, sums its current change and applies IFRS9.6.5.11 to cumulative
instrument/item changes. It posts differences in cumulative reserve/profit.
This equals the stated target by the local derivation in source-reading.md and
the separate origin-based versus incremental-path checks.

At price90, the original100@80 has item loss1000 and derivative gain1200,
producing reserve1000 and cumulative profit200. Add10@90. At price95, item
loss1550 and derivative gain1400 give reserve1400 and profit0. The journal is
debit derivative200, debit gains200, credit reserve400. A reset calculation
instead produces reserve1200/profit200 and is wrong for this cumulative target.

After adding20@95, subsequent cumulative (item change, reserve, profit) values
are (−1810,1810,90), (−1420,1420,80), (530,−200,0), and (400,−400,−100).
The final books are derivative−500, reserve debit400 and gains debit100.
Removing intermediate observations leaves this final state unchanged. Adding
a layer at its current price creates no immediate journal or reset.

The report rejects stale measurements, wrong layer prices/dates, duplicate
identities, overlapping context changes, inconsistent currency/quantity/price
units, changed objectives and unmodeled removal/instrument/settlement methods.
Required findings missing are unresolved; a false eligibility finding is
unsupported. Every refused whole-path result returns no state, trace or journal
and makes no mutation. These statuses do not determine actual eligibility.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Retain add-only item method | Independent cumulative targets, origin/incremental equality and exact journals pass | No accepted failure; context defect repaired | Actual eligibility and valuation inputs | Integrate derivation; connect a completed purchase to inventory basis | Removed/instrument layers or general hedging engine |
| Reject reset minima | Source-rule cumulative reserve differs by200 in discriminating case | Target mismatch is demonstrated | Wider partial-discontinuation allocation needs another derivation | Preserve original finite evidence and explicit residuals | That every original single-reset observation was numerically wrong |

| Inference status | Judgment |
|---|---|
| Hard veto evidence | Reset formula fails this cumulative target; no accepted-run failure |
| Statistical ranking | N/A: exact deterministic accounting demonstration |
| Descriptive evidence | Counts and selected path show coverage, not generality or economic superiority |
| Default-readiness | No actual authority/valuation or runtime/default promotion |
| Next evidence | Purchase basis/release; removed/instrument layers; wider valuations and actual eligibility |

The strongest alternative explanation is an inadmissible supplied designation
or incomplete valuation. Balanced journals and offsetting numbers cannot answer
that question. The method refuses unavailable findings rather than inventing
them. A counterexample inside the declared finite profile would overturn its
calculation; wider layer operations require separate methods. No continuation
veto fired. An online source search returned no usable results; all technical
support here comes from the inspected retained primary source, not that search.
