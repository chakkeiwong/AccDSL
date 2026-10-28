# SIM-F021: face, cash and the supplied pricing law

28 October 2026. C04; MC15–18, MC33–34. Attempt02 passes 198 checks across
13 native cases. This is synthetic engineering evidence under an explicitly
supplied pricing law. It does not close T07 or admit any actual market quote.

The exact original inputs are face100, default weight1/10, fixed recovery40
and gross risk-free return21/20. Two-state expected payoff is94. Its discounted
value is1880/21, approximately89.524, leaving115/21 unfunded against a need95.
Promised yield is11/94. Pricing the face as100 instead gives lender break-even
error11. Mixing the principal-based rate with face-based proceeds gives
9000/101 and error−44/101, reproducing the retained26October discriminator.

The existing declared issue method records the supplied proceeds in cash and
carrying debt while recording the promised face separately in contract memory.
Eight exact pricing cases preserve all native balances, all memory, journals,
flows and reports. Controls cover no default, certain default, zero/full
recovery, zero rate and a larger face with either fixed or scaled recovery.
A fixed recovery amount must not silently become a face percentage.

Three inconsistent face/proceeds/quote inputs refuse atomically after the same
three-event prefix. Their complete prior books remain unchanged. A separate
zero-value claim adds promised face without adding cash under this narrow
method's declared contract; that is not an actual offer or accounting opinion.

## What the native check establishes

The native method checks proceeds = face × supplied quote. It does not receive
the probability, recovery or discount law. A self-consistent quote1 and
proceeds100 therefore completes provisionally even though it violates the
original law by11. This is correct relative to the native method's explicit
conditional-input contract; calling it creditor-consistent pricing would be
wrong. The independent oracle detects the difference. T07 must bind actual
pricing assumptions and dates before any stronger interpretation. A content
hash or balanced journal cannot supply that missing economic evidence.

No generic pricing adapter is introduced here: the existing production and
frozen code stay unchanged. The one-period law is supplied for the exact
original failure, with no coupon, fees, tax, options or earlier default cash.
Its probability is a pricing weight. Substituting an empirical physical default
rate would need a separate risk-pricing justification. General invalid-law
admission, settlement/default execution and source-backed offers remain open.

## Audit, failure and verification

The skeptical audit rejected arithmetic-only coverage as evidence of native
recording and rejected quote identity as a pricing criterion. The retained
26October issue factory and current pinned DeclaredCompanyProgram/2 execute
each case with fallback native posting disabled. Entire results and exact
pricing-state tables are retained in attempt02. Source hashes are checked
before and after; no frozen source is overwritten or rerun in place.

Attempt01 stopped because the harness expected a before book in each transition.
Native transitions expose before_sha256; the preceding transition contains the
book. Attempt02 reads that book and explicitly verifies the hash. The failed
script and partial outputs remain. This is a harness repair, not a failed
financing model or failed research direction.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain exact SIM-F021 scoped evidence | State payoffs, lender equation and complete native recording agree | No failed exact or preservation check | Actual probability measure, quote and dates | Preserve separate source/pricing admission obligations | Market valuation or complete T07 |
| Reject face-as-cash and mixed conventions under original law | Errors11 and−44/101 | Independent lender equation rejects | None within the declared law | Keep negative fixtures | General native pricing enforcement |
| Preserve supplied-quote native contract | Identity-consistent quote passes even when economically wrong | Pricing is outside that native method | Caller admission is not established | Bind justified law at a future supported pricing boundary | Bug in the conditional recording method |
| Continue program | No continuation veto remains after harness repair | Original statuses/releases unchanged | Remaining original failures and source admission | Resume ready C04/T03 work | Completed DSL or release |

| Inference status | Assessment |
| --- | --- |
| Hard veto screen | Inconsistent supplied cash/quote values refuse; independent creditor law rejects wrong quotes |
| Statistically supported ranking | None; deterministic exact tests only |
| Descriptive-only differences | Check and case counts |
| Default readiness | No new default or pricing model selected |
| Next evidence needed | Source/measure/date admission and general claim settlement under reviewed survey prerequisites |

Strongest alternative explanation: success could come from supplying the right
quote externally. That is exactly the supported scope, and the wrong-quote
control exposes the limit. A valid quote identity cannot overturn the creditor
calculation; a different admitted probability measure, payoff or discount law
would instead define a different question. The weakest evidence is actual
pricing-law admission, which has not been attempted.

Commands and environment are in attempt02/run-manifest.json; complete results
are in native-cases.json and pricing-states.json. The original201 failure rows
and their inherited statuses remain unchanged.

