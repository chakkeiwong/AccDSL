# Entity cash, transfer limits and payment order

28 October 2026. C04; SIM-F039/040. Attempt03 passes244 exact checks across34
native programs and seven rational-solver calls. The original synthetic
discriminators retain their entity, currency and timing meaning.

With parent cash5, debt payment20, subsidiary cash30 and transfer cap10, the
parent can hold at most15 before payment. The exact constraints cover the full
allowed transfer interval and find no feasible payment. Cap15 is the boundary;
cap14.5 remains insufficient. Leaving the actual cap unknown preserves a
conditional minimum required cap15, not permission to transfer15. Zero solver
budget remains Unknown. Pooled cash35 answers a different question.

The native example supplies an intercompany receivable/payable30 to define a
specific settlement mechanism. Parent collection10 leaves cash15 and blocks
the debt payment without changing the last valid state. The matched subsidiary
leg pays10, leaving cash20 and payable20. Their same-date USD flows sum to zero
across distinct entities. This is a comparison of two separately executed
conditional books; atomic multi-book settlement is not implemented here.
Actual rights, classification and settlement evidence remain prerequisites.

Cumulative usage matters. Under cap10, transfers6 then6 stop at the second
collection. A deliberately weakened per-event limit admits both and still
reconciles. The independent opening-claim-minus-current-claim test detects the
excess2. The supplied cap is kept fixed throughout this fixture; admission of
changed cap vintages or real permissions is outside this unit.

The EUR timing example opens with cash0, receivable20 and debt20. A January3
receipt cannot pay a January2 maturity. A January1 receipt can. For January2
events, payment-first refuses and receipt-first succeeds; order is an explicit
premise, not inferred from equal dates. Moving the January3 receipt ahead of a
January2 payment refuses event_chronology. Net final cash0 conceals the failed
intermediate cash requirement20.

USD-typed or different-entity amounts are rejected before execution with
event_type_mismatch. Artificially supplying opening EUR cash30 makes the
conditional program succeed, but changes the original premise. It cannot be
justified by another entity's USD30 without an explicit transfer and conversion.
No exchange rate, FX service or alternative funding channel is inferred.

Attempt01 failed because the checker referenced a helper in the wrong module.
Attempt02 assumed type refusal produced a current state; native validation
correctly returns top-level invalid before any execution. Both failed sources
and reasons are retained. The checker was repaired; protected engines and
solver defaults were unchanged. The final full run covers both account maps.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain F039 discriminator | Exact local feasibility and native states agree on15 versus20 | Aggregate35 and per-event cap shortcuts rejected | Actual permission, cap vintage and linked settlement | Preserve entity/rights bindings in composition | Group insolvency or atomic multi-book service |
| Retain F040 discriminator | Named dates/order and EUR balances determine payment | Future receipt, wrong currency/entity and changed opening rejected | Actual intraday order, FX and funding access | Bind settlement evidence before admitting histories | Every liquidity channel or settlement system covered |

| Inference status | Finding |
| --- | --- |
| Hard veto screen | Wrong cap, location and chronology fail exact criteria; zero budget remains Unknown |
| Statistically supported ranking | Not applicable: deterministic rational cases |
| Descriptive-only differences |244 checks,34 native programs and seven calls describe this scope |
| Default readiness | No implementation or financial-policy default changes |
| Next evidence needed | Entity claims, transfer authority, cap vintages, FX and linked settlement |

Post-run red team: conditional account operations do not establish that the
intercompany claim or matching cash payment exists. The two independent legs
do not supply cross-book atomicity. These are the weakest limits; they do not
invalidate the original cash-feasibility discriminator. No global continuation
veto fired. Continue loss-vintage, collateral and contractual-clock cases,
alongside primary sources and ordered review. E3 remains deferred.

Final verification matches all1,179 protected hashes, including997 frozen
release files. Current program validation passes21 tests; concurrent research
alignment work expanded that suite during this unit. The refresh verifies30
source hashes, preserves task criteria/statuses/dependencies and records42
reviewed original failures with159 outside this continuation. Main reading
remains336/831. Native regressions were already passed in the preceding unit;
no protected implementation changed here, so they were not redundantly rerun.
