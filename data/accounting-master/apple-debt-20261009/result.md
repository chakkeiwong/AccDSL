# Apple debt: completed bounded source and manuscript unit

9 October 2026. Version 2.12 integrates checked annual debt movements,
commercial-paper refinancing and dated risk disclosures into Chapter 10.
The candidate has 146 pages and preserves all 42 earlier displays and all 66
bibliography entries, adding two displays. Full proposal readiness remains
**not_ready**. Product implementation and the historical controller remain held.

PDF: `docs/design/proposal/manuscript-debt-20261009/accounting-product-proposal.pdf`.
SHA256: `c36abf7cfc0a7003ce4406d737374150eeff57da876af123b957be09034e7f9b`.
Plan: `docs/plans/accounting-apple-debt-20261009.md`.
Baseline Git: `891a80316c3291d701b30723df687e517e11a06e` (Version 2.11 commit).
MC01–05/07–12/14–17/19/28/30/32–35 and G1/G4/G5/G7/G11/G13/G15/G16 are
addressed within the E01/C03/C08 scope.

## Source population and findings

Annual Note 9 and interim Note 6 are read completely and partitioned into nine
material units. Thirteen declared source dependencies cover the complete
derivative passages, debt statement context, calendars, gross derivative
presentation, liquidity and market-risk discussions. The earlier checked euro
coupon/settlement example remains a separate dependency. Ten queries preserve
their supported answers and unresolved facts. All 79 numeric table cells,
including comparative years and both commercial-paper maturity classes, are
checked against the retained originals. This does not establish full package,
instrument, rule or whole-company history coverage.

All monetary amounts below are USD millions unless stated otherwise. Arithmetic
uses displayed centres and retains source precision; no unrounded issuer book
is inferred.

| Target | Quantity actually checked | Verdict and remaining limit |
| --- | --- | --- |
| Annual term-debt movement | Principal −9,231, net unamortised component +35, hedge basis +755, carrying amount −8,441 | Components add exactly at displayed centres. Reported net term cash flow is −9,958, leaving 727 at principal level and 1,517 at carrying level. Neither residual identifies FX, a cash payment or a journal. |
| Quarter term-debt movement | 94,804 = 96,662 − 1,009 − 849 | Reproduces the existing checked result, not new evidence of a cause. Interim rounded 94.8 billion is compatible with the statement total. |
| Maturity and current debt | Six principal buckets sum to 97,341; fiscal-2025 principal is 10,930 versus current carrying 10,912 | The 18 difference does not allocate discounts or hedges. Fiscal buckets, the calendar issuance range and MD&A twelve-month cash requirements remain distinct. |
| Future interest | MD&A 38.5 billion total, 2.6 billion within twelve months | Retained as stated future cash requirements; not period expense, effective rate or present value. |
| Commercial-paper cash and balances | Annual 5,985 + 3,960 + 22 = 9,967; quarter 9,967 − 7,944 − 28 = 1,995 | Residuals remain unallocated. All three annual short/long-maturity cash bridges reconcile; net amounts do not identify gross issues/redemptions. |
| Hypothetical 60-day principal round trip | At-par 1,000 issue and repayment, zero net principal, simple 5% ACT/360 interest 25/3 | Three journals balance and leave incremental cash/equity −25/3, liability zero. Only principal endpoint/net-flow ambiguity is demonstrated; interest and other statement targets can reject the addition. No actual Apple transaction or full compatible history is claimed. |
| Interest-rate exposure | Issuer +100-basis-point/all-tenors scenario including associated derivatives: annual expense +139/+194 at the two annual dates | Correct source target. Notional × 1% gives 145.75/193.75. The 2024 mismatch exceeds conditional display rounding; the 2023 match does not validate the shortcut. Swap/reset explanation remains unknown. |
| Currency risk | Issuer 95%, one-day foreign-currency derivative VaR 538/669 | Underlying exposures are excluded; not net company VaR, a hard maximum, or a locally replicated model. Interim no-material-change referral does not issue updated numerical sensitivities. |

The new prose uses the annual component bridge to explain the cash distinction,
then the scoped borrowing example to explain gross activity, and finally the
reported scenario to explain exposure after hedging. Earlier quarterly and
coupon examples remain unchanged. Hedge carrying amounts, derivative notional,
gross derivative fair values and cash classifications retain their separate
targets. The word “generally” is preserved in the issuer's operating-cash-flow
description; it does not become an unconditional rule.

## Decision

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Complete the bounded debt integration | Two full notes and dependencies support useful, source-faithful consequences and an explicitly conditional example | 162 source/arithmetic and 33 candidate/preservation checks pass; final build clean; five body pages read | Actual instrument movements, holdings, calendars, currency/hedge links and operative accounting facts remain unknown | Plan and audit complete annual/interim Note 4 cash/securities/liquidity reading; retain completed hedge/escrow work as dependencies | Full E01 closure, all admissible histories, default accounting policy, compliance, product implementation, current issuer risk or whole-proposal readiness |

No stochastic comparison ran. The issuer's Monte Carlo description is retained
as a source assertion; it supplies no local statistical ranking, uncertainty
estimate or model validation. A failed shortcut rejects that shortcut, not the
filing or the research direction. The source/extraction discrepancy and the
candidate-check parser error were engineering issues and were repaired before
dependent acceptance.

## Verification and repair history

The first source run passed 160 checks and failed one original-text comparison.
PyMuPDF placed securities-table references (1)/(3) at the end of the hedge
passage on PDF page 40. Visual inspection locates them in the preceding table;
the checker now removes only that displaced sequence for comparison. Note 9's
two-tier header is checked as an exact token permutation, with full matching
text outside it. Original PDF/HTML/text bytes remain unchanged.

The final source run passes 162 checks. An intermediate successful report is
also preserved: the final preparation corrects the derived balance-sheet unit
heading to include par value and keeps evidence output hashes limited to files
that its own script creates, avoiding a dependency on the later renderer.
Three source preparations and three derived-render runs are recorded. The
first candidate-check attempt treated the year header as a data row and stopped
before producing a report; its script/failure record is retained. The repaired
checker passes all 33 checks without a manuscript change.

One local LuaLaTeX build succeeded in 15.70 seconds using an explicitly writable
`/tmp` font cache. Final LuaLaTeX and bibliography logs have no warnings. No
dependency installation or trusted retry was needed. Annual original PDF pages
28/30/34/36/37/40/41/46/47 and four labelled derived interim pages were inspected.
Final manuscript PDF pages 82–86 were read at normal resolution; pages 1–7 were
inspected for navigation. The surface auditor's nested `aligned` flag does not
represent a third display. [Author review](author-review.md) records equation,
reader, source and rendering judgments separately. Independent/human acceptance
remains pending.

All 174 baseline files and 177 preceding-manifest references are retained,
using the four `pointers-before/` relocations. The 1,266 historical protected
files, 518 upstream references and six controller records also pass preservation
checks. Forty exhibit targets, 136 unverified publication dates, actual company
facts and all five wider E workstreams remain. No original acceptance requirement
is relaxed. No network, GPU use, worker, fee, outreach or publication occurred.

The next smallest source question is how disclosed cash and marketable
securities constrain available liquidity, once restrictions, valuation,
classification and movements are kept separate. Remaining Note 4 cash/securities
and receivable passages have not been completed by the debt subsection alone.
Audit their full annual/interim population and policy/statement/MD&A dependencies
before any new calculation. This unit completes at the checked integration.

Post-run red team: the strongest alternative explanation of a residual is an
undisclosed combination of movements and measurement differences. Matched
instrument-level records could identify it; algebra on aggregates cannot.
The weakest evidence remains missing actual facts and independent/human review.
A clean build and exact balances do not overcome either limitation.
