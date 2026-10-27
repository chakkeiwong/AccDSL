# Apple liquidity: completed bounded source and manuscript unit

9 October 2026. Version 2.13 adds resources available for payment to Chapter 2:
restrictions, securities turnover and valuation, and receivable concentration.
The candidate has 149 pages and preserves all 44 prior displays and all 66
bibliography entries, adding two displays. Full readiness remains **not_ready**;
product implementation and the historical controller remain held.

PDF: `docs/design/proposal/manuscript-liquidity-20261009/accounting-product-proposal.pdf`.
SHA256: `500a17e084d63e4e72700a596a02e12d5dcf9f8c666c7855abeaf7b421a30cb4`.
Plan: `docs/plans/accounting-apple-liquidity-20261009.md`.
Git baseline: `891a80316c3291d701b30723df687e517e11a06e`.
Immediate document baseline: frozen 146-page Version 2.12 and debt manifest
`34741a5f119cfb854b3f6f58f83a50565b2c8b5cb77c6320dfc1463ba3e3acba`.
This E01/C03/C08 unit addresses MC01–05/07–12/14–17/19/28/30/32–35 and
G1/G4/G5/G7/G11/G13/G15/G16 within the declared scope.

## Source population and consequences

Both complete financial-instruments notes are partitioned into fourteen
material units, with thirteen declared policy, statement, liquidity, market-risk
and tax dependencies. The source table population has 392 investment cells
including the repeated September snapshot, or 294 unique dated cells, and 90
statement cells. Eleven query dispositions distinguish supported consequences
from required actual facts. The earlier hedge and escrow interpretations are
bound dependencies. No full company-history or package-semantic closure follows.

All monetary amounts below are USD millions unless stated otherwise. Arithmetic
uses displayed centres; rounding ranges are conditional on nearest displayed
quantum, not issuer-declared conventions or confidence intervals.

| Claimed target | Quantity actually computed or retained | Verdict and unresolved consequence |
| --- | --- | --- |
| Investment resources | Cash plus current/non-current securities = fair value 162,099/156,650/141,368 at September 2023/September 2024/December 2024; adjusted cost plus net unrealised amount gives the same totals | Correct population reconciliations. Adjusted cost is the source label; the second reconciliation is not another resource. Individual lots, currency and settlement remain unknown. |
| General-use resources | Annual displayed subtraction 140,850; nearest-rounding bounds 140,749.5–140,950.5 overlap rounded MD&A 140.8 billion. Quarter subtraction 137,942 with conditional bounds 137,891–137,993; cash plus current securities less escrow centre 50,349 | Source restrictions matter; no genuine conflict is established by annual rounding. Quarter MD&A supplies no numerical unrestricted total. Current securities can be restricted; no exact freely spendable balance or solvency guarantee. |
| Securities cash versus carrying change | Annual net cash released 13,690, stock change −5,427, residual +8,263; quarter 13,335, −15,638 and −2,303 | The identity is correct; identifying the residual as a gain, FX or reclassification journal would be wrong. Cash proceeds differ from book disposals. |
| Valuation and OCI | Total cost/net-unrealised changes −13,152/+7,703 annually and −13,512/−1,770 quarterly reproduce total value changes −5,449/−15,282. Debt OCI net of tax is 6,054/−1,427 | Different population, tax and timing prevent equating endpoint unrealised changes, total resource movement, securities residual and period OCI. |
| Cash-flow cash population | Annual opening exceeds balance cash by 772; changes −794/−22 close at the same 29,943. Quarter endpoints agree with change 356 | Correct comparison; earlier difference remains unallocated. No unsupported location or cause is assigned. |
| Maturity and valuation risk | Separate non-current maturity triples 86/10/4 and 14/9/77 at September, 85/11/4 and 13/10/77 at December. Issuer all-tenor +100bp investment scenario gives declines 2,755/3,089 at annual dates, including associated derivatives | Separate denominators and dated fair-value target retained. No immediate cash schedule, loss probability, locally replicated valuation or new December sensitivity. |
| Trade/customer concentration | Exact-centre whole-customer inclusion-exclusion gives possible unions 33/44/51/62%; eleven-customer examples construct 33 and 62 while keeping exactly two shares at least 10% | Correct conditional percentage examples, not customer identities, divisible membership, monetary losses or probabilities. Gross/net denominator and credit support remain unresolved. |
| Vendor concentration and receipts | Top two 44+23 and 43+24 each total 67% on separate dated vendor populations. Trade balance/indirect-adjustment residuals +114/−174; vendor changes match opposite adjustments | Neither equality nor concentration identifies total collections or stable counterparties. Component sales are excluded from product revenue; gains reduce cost when related final products sell. |

The manuscript follows payment needs with resources, then their conversion
to cash, then future customer receipts. The two new displays are a residual
identity and customer-set inclusion-exclusion. Their assumptions precede them;
their limits and concrete consequences follow immediately. Earlier cash, tax,
debt, revenue and commitment discussions remain intact.

## Decision and evidence roles

| Decision | Primary criterion status | Veto diagnostic status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Complete this bounded liquidity integration | Both full notes, dependencies and query dispositions support the added funding argument | 339 source/arithmetic and 35 candidate/preservation checks pass; clean final build and six body pages read. Extraction and citation defects were repaired | Actual lots, counterparties, settlements, denominator basis and independent/human review | Plan complete annual Note 13/interim Note 10 geographic/segment reading, extending existing selected sums and assertions | Full E01 closure, actual histories, operative compliance, empirical forecast, default policy, independent acceptance or whole-proposal readiness |

Table-alignment and source-fidelity failures were engineering repair triggers
and claim vetoes, not evidence against the research direction. Aggregate-cash
and additive-concentration shortcuts fail for their stated targets; their
failure motivates decomposition and whole-customer alternatives. No continuation
veto remains for this integration. Counts, page length and build success are
explanatory diagnostics, not promotion criteria for the wider proposal.

No stochastic comparison ran; no statistical ranking, probability calibration
or local Monte Carlo claim is made. Engineering checks, numerical identities
and scientific/accounting interpretation remain separate. Candidate shortcuts
are rejected without rejecting the filings or the research direction.

## Verification, repairs and preservation

The first evidence attempt stopped on a wrong dependency filename; the tax unit
uses `tax-bridges.json`. The second passed 334 checks but failed three original
PDF comparisons because the extractor displaced superscript markers. Original
page inspection verified the full headings/footnotes; the repaired comparison
retains token populations and separately checks total-row markers. The final
339 checks pass. Both earlier scripts/results are preserved in attempt directories.

The source review inspected original annual PDF pages
28/29/30/33/34/36/37/39/40/41/42/43/44 and eight derived interim pages. The latter
are explicitly local reflows, with text-order checks and seven-column investment
alignment reconstructed from the original colspan grid. They are not original
filing screenshots. Original source bytes are unchanged.

Two LuaLaTeX builds succeeded in 16.63 and 7.43 seconds with an explicit writable
`/tmp` font cache. The first rendered review was preserved before correcting
the annual comprehensive-income page citation and adding the direct disposal-policy
anchor. Final PDF pages 20–25 were read at normal resolution; pages 1–7 were
inspected for navigation. Twelve inspected images are unchanged after repair;
corrected page 23 was reread. Final LuaLaTeX/bibliography logs are clean. The
surface auditor's nested aligned environment is not a third new display.
[Author review](author-review.md) records the four separate verdicts.

Only the version, one chapter inclusion and the new section differ among the
manuscript sources. All 154 baseline files and 152 preceding-manifest references
are preserved through the four pointer relocations, together with 1,266
historical protected files, 518 upstream references and six controller records.
The four current records are updated before manifest freeze, including both
roadmap current-PDF and latest-result links. Frozen releases are unchanged.
No commit or push was performed; the extensive unrelated dirty work is retained.

The [next-source frontier](next-source-frontier.md) selects annual Note 13 and
interim Note 10 for their remaining geographic, profit-reconciliation and asset
meaning. Existing A21/I11 assertions and income/sales sums are checked dependencies,
not newly discovered gaps. Annual Note 6 is already a complete tax dependency;
broader policies and management/business/risk narratives still require work.
Forty exhibit targets, 136 unverified publication dates, actual company facts,
all five E workstreams and MC01–MC35/G1–G18 acceptance obligations remain.
No network, GPU use, worker, installation, outreach, fee or publication occurred.

Post-run red team: identical aggregate reconciliations can conceal different
instrument and counterparty populations. Matched lot, cash and customer records
could allocate a residual or resolve an overlap; current aggregates cannot.
Missing actual facts and independent assessment are the weakest evidence.
This unit stops at the checked integration specified in its plan; it does not
stop or complete the wider research direction.
