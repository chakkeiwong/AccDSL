# Share authorization, cash settlement and investor value remain distinct

28 October 2026. C04/T08; original SIM-F030/033/034. Attempt02 passes249 checks
across37 native cases. The separate fixture adds typed authorization, accepted
offer and receipt requirements to existing immutable method data; native code
and prior fixtures remain unchanged. Two account mappings agree with independent
balances, full share memory, financing cash, equity movements and zero profit.

For the approved fifteen-share raise,14 and15 shares settle successfully;16
refuses before any posting. False approval, rejected offer, failed settlement,
zero/short receipt and a mismatched offer price refuse atomically. Unknown
approval, offer, settlement or receipt remains unresolved. Duplicate execution
does not issue shares or receive cash twice. These statuses describe supplied
premises and native execution, not actual legal authority or bank verification.

The generic baseline can issue16 without the added authorization rule. Removing
receipt rules while leaving their inputs declared is correctly rejected by the
native schema as unused_input_declaration. Attempt01's checker incorrectly
assumed that mutation would execute and raised KeyError before saving its full
checks. Its code and failure record are preserved. Attempt02 includes that
schema safeguard and a valid negative control with vacuous receipt equalities.
That control produces balanced cash160 from opening10 even though the supplied
settlement is false and receipt0. Independent receipt expectations identify the
wrong result. Native balance and replay alone cannot admit an equity transaction.

## Ownership and value

The illustrative valuation assumes100 old shares, economic assets1000,15 new
shares, no debt, fees, tax or project change, and cash added at the stated issue
price. Existing investors own100/115 =20/23 after either issue. At price10,
post-issue value1150 leaves their value1000 unchanged. At price8, post-issue
value1120 gives them22400/23, a loss600/23. New investors receive value3360/23
for cash120, a corresponding gain600/23. The value transfer sums to zero under
these explicit assumptions. Percentage dilution alone therefore does not
determine a loss of investor value.

The native opening book equity is10, or0.1 per old share, while supplied economic
assets imply10 per old share. Accounting accepts an explicitly supplied0.1 offer
under the fixture's transaction conditions, but that does not justify choosing
the offer from book value. Under the same economic assumptions, that shortcut
reduces old investors' value by2970/23. Neither the native accounts nor this
illustration estimates a market price; the economic value is an independent
premise. These exact calculations are conditional examples, not forecasts.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain SIM-F033 discriminator | Cap, offer and receipt checks match independent states and atomic refusals | Unknowns unresolved; false/inconsistent inputs refuse | Real authorization and independently observed receipts | Bind actual evidence separately; extend specific operation contracts | General equity/legal admission |
| Retain SIM-F030 discriminator | Exact same ownership with different value effects | Value and transfer conservation pass | Economic asset value and issue assumptions | Supply justified valuation and offer evidence for a real case | Dilution percentage predicts value loss |
| Retain SIM-F034 discriminator | Book and economic values remain separate inputs | Book-price shortcut fails the value-preservation criterion | Actual economic value and market offer | Inspect valuation/offer premises rather than infer them from carrying values | Book equity determines a fair price |

| Inference status | Finding |
| --- | --- |
| Hard veto screen | Invalid authorization/receipt and schema states refuse; unknown evidence stays unresolved |
| Statistically supported ranking | Not applicable: deterministic exact examples |
| Descriptive-only differences |249 checks and37 cases describe selected coverage |
| Default readiness | No implementation default, market model or actual admission changed |
| Next evidence needed | Real rights, approvals, accepted terms, receipt provenance, valuation and complete share population |

Post-run red team: supplied true booleans and receipt amounts can be wrong in
the world. This fixture checks conditional execution and cannot establish their
truth. A reviewed evidence-binding layer remains necessary. The independent
value equations are valid only under their stated asset and financing assumptions;
fees, debt, preferential rights or project responses require different equations.
No broad equity package or release closes. No continuation veto fired.

Final verification matches all1,179 protected hashes including997 frozen-release
files. Nine program regression tests pass. The native financing/method-clock/
company-program code also remains unchanged from the56-test pass in the preceding
reference unit. Navigation verifies29 source hashes and preserves all task
statuses, criteria and dependencies. Original review coverage is now32/201;
169 rows remain outside this continuation. Main reading remains336/831.
