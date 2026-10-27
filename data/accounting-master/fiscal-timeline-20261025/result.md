# Deferred evidence and terminal fiscal carry

25 October 2026. MC13, MC15, MC16, MC24, MC28, MC32, MC35.
MixedEventTimeline/3 preserves supplied deferred measurement bytes and native
annual accounting. Thirteen focused tests plus 61 regressions pass (74 total).
Twelve complete exchanges and 343 input files are retained in manifest.json.
The full native manual comparator, commands, environment and duration are saved.

The clock is measurement.at for deferred assessment and next_period.start for
carry. A carry is unique, contiguous and terminal in the current timeline.
Later activity requires a separately state-bound request. This is a bounded
scheduling design, not a claim that a general simulator must stop every year.

## Consequential numerical case

The synthetic sale increases cash from 452 to 467 and reduces inventory from
80 to 70, giving profit 5. Zero supplied current adjustments and rate 1/4 give
current tax 5/4. The explicitly revised recovery capacity and recognized
deduction of 12 give DTA 3 instead of 5; DTL remains 5. The native deferred
journal reduces DTA by 2 and records expense 2, with no cash flow.
After-tax profit is 5 - 5/4 - 2 = 7/4. Carry transfers that amount to retained
earnings (credit-signed balance -47/4 becomes -27/2), retains cash 467 and
tax payable 23/2, archives the full old report and resets period income/flows.

A payment of 1 before deferred assessment makes the original measurement
digest stale. The runner stops with measurement_state_digest and preserves
the payment, cash 466 and remaining assessment/carry. It never rewrites the
digest. A distinct authored request with a fresh measurement ID/digest passes
and carries cash 466 and payable 21/2. A payment after deferred assessment
marks it stale and blocks carry with assessments_incomplete.

The next separately bound period keeps all archives and old tax vintages.
The inherited stock rule reserves 1/2 unit: with one unit left it sells only
1/2 for 15/2, cost 5, cash 949/2 and inventory 65. The first focused run caught
an incorrect full-unit expectation in the test. Inspection established the
explicit reserve; only that expectation was repaired, and generated quantity
is now asserted. No runtime rule was altered to fit the test.

## Native status clarification

The plan used “missing findings” imprecisely. An explicitly unknown deferred
finding returns unresolved; an absent required map entry is structurally invalid;
a known false deferred finding is unsupported. All three preserve the actual
native outcome and valid prefix. The tests establish this exact distinction,
not the looser wording. Carry findings already have a different role: unknown
and false findings remain recorded as unresolved/asserted_false while provisional
carry may proceed. Accounting and source admission remain false. No missing
evidence is converted to approval.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Retain optional fiscal timeline | Full native/manual equality, nonzero deferred/carry arithmetic, explicit next-period continuation pass | Stale original digest refuses; no input mutation, lost archive, hidden clock or automatic renewal observed | Authored bases, recoverability and completeness are hypothetical | Integrate successor, then reassess remaining source and simulator dependencies | Tax-law validity, full fiscal events, complete DSL, company admission or production readiness |

Actual 32-native/64-total execution passes and overflow refuses. Prior version2
financial outcomes are preserved. Results are exact deterministic engineering
checks, with no stochastic ranking. The strongest alternative explanation is
a shared native accounting error: independent tax, cash, inventory and retained
earnings arithmetic checks this case, but cannot establish domain validity.
The weak boundary remains supplied tax evidence and broader combinations.
