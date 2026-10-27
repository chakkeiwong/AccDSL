# R03-A — Financing changes and hedge accounting

15 October 2026. Version 2.96, 284 pages, provisional and not_ready.
PDF: docs/design/proposal/manuscript-financing-changes-20261015/accounting-product-proposal.pdf
SHA256: 10af497755650076da3ee4516cea72359528ba09aedef3a1082f97e800dc00a4.
Plan: docs/plans/accounting-financing-changes-20261015.md.
Method: docs/design/proposal/methods/financing-changes-20261015.md.
MC06/07/11/13–20/24–28/30/32–35; G1/G3/G6/G7/G9/G13–18.

## Result and financial meaning

Nine conditional cases retain 26 events and 14 adverse alternatives. All 302
independent checks pass. Repurchase allocates consideration between liability
and equity; the source-rounded 1,700 payment gives a 119 liability loss and
619 equity debit, rather than a 738 loss. A separate exact discounted-cash-flow
calculation preserves the distinction between exact and source-rounded values.
Immediate share-only inducement uses the amendment-date share quote: ten
additional shares at 40 produce a 400 loss. Neither delayed acceptance nor
cash alternatives inherit that simplified result.

The inventory hedge carries cumulative effective amounts of 10 then 14,
with cumulative ineffectiveness of 2 then 1. Purchasing inventory for 114
and transferring the reserve of 14 gives inventory cost 100; that transfer
is not an OCI reclassification. With sale proceeds of 130, the same journal
history gives profit and operating cash of 31 and final cash/equity of 231.
Separate interest and cancellation cases show when the reserve reaches
earnings, when it remains, and how an unrecoverable loss is released.

The fair-value hedge adjusts debt from 100 to 110 against a derivative gain
of 8. Subsequent contractual payment of 121 requires an effective rate of
10% and interest expense of 11. Cash retains its contractual split of
21 interest and 100 principal; it does not follow the effective expense.
Benchmark reform requires a direct reform cause and economic equivalence:
one equal coupon does not establish equivalent future terms.

The claimed target is the historical, conditional accounting method and its
deterministic financial consequences. The checked calculations compute that
target for the specified cases. Supplied derivative values, eligibility
findings and actual contract/legal facts are inputs, not independently
established valuation or compliance conclusions.

## Source and document checks

The retained AASB132 and AASB9 compilations apply to the declared calendar
2024/25 examples; AASB107 supports their specified historical cash-flow
classification. Exact source hashes, applicability and inspected passages
are in source-support.json. Printed repurchase/inducement tables on AASB132
physical pages 47–48 were visually inspected. A mistaken TOC render is not
credited as technical-page inspection. Online discovery supplied no usable
additional evidence.

All 103 preservation/build checks pass. The protected predecessor PDF and
83 source-file originals remain unchanged. The successor changes only its
version and the financing-chapter insertion, adding one section. Displays
increase 98→101, labels 169→174 and citation occurrences 496→513, with none
removed; the bibliography is unchanged. The build reports no diagnostics.
Seven final rendered physical pages were inspected: 1,163–168. This is an
author review of affected pages, not whole-candidate or human acceptance.
The 100-entry unrelated index remains byte-for-byte unchanged.

## Decision

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Retain the scoped repair | Exact methods, journals and positive/adverse cases supplied | No failed numerical or preservation check | Actual terms, market valuations and current authority | Continue R03-B and later finite clusters | Full R03, multi-GAAP compliance or runtime conformance |
| Keep broader financing residuals open | Specific source/valuation limits located | Missing broader methods veto their admission | Delayed/contingent inducement, excluded option components, rebalancing/group hedges, legal capital | Resolve against the promised profile and dated primary authority | Supplied fair value closes valuation |
| Retain provisional manuscript | Affected-page and preservation checks pass | Whole review and independent/human acceptance pending | Narrative consistency across accumulated supplements | R07/R08 review of the final candidate | Page count or check count establishes readiness |

Post-run red team: balanced journals can still embody the wrong measurement
date, reserve transfer or cash classification. The adverse cases specifically
test these errors. The weakest evidence is the assumed market measurement and
eligibility, not the exact arithmetic; changing those facts would change or
invalidate the conditional result. No stochastic comparison or ranking was
performed. This result advances one finite repair, without rejecting or closing
the wider research/design direction.
