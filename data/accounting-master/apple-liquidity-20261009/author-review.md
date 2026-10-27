# Author review of the bounded liquidity addition

9 October 2026. Candidate: 149-page Version 2.13,
`docs/design/proposal/manuscript-liquidity-20261009/accounting-product-proposal.pdf`.
SHA256: `500a17e084d63e4e72700a596a02e12d5dcf9f8c666c7855abeaf7b421a30cb4`.
This is author preparation. Independent-reader and human acceptance are pending.

## Continuous reading and transition checks

PDF pages 20–25 (printed 13–18) were read in order at normal resolution.
Pages 1–7 were inspected on a contact sheet for title, contents and navigation.
The latter inspection is not a continuous read of the manuscript. The final
source-anchor repair changed only PDF page 23 among these thirteen images.
That page was reread in full after rebuilding; all other inspected page images
are byte-identical to their preserved first-build images.

Page 20 develops payment timing from lease and purchase obligations. Page 21
finishes the conditional delivery/settlement example, supplier constraints and
management's contingent-loss assessment. The new section then asks what can
fund those obligations. It introduces sources, dates, units and the December
quarter boundary before the resource table, which starts page 22. The heading
and introductory paragraph remain together; the page turn does not split a
table or equation from its explanation.

Page 22 provides two reconciliations of the same resource total and then asks
which funds can be used. The escrow subtractions preserve displayed precision;
the conditional rounding overlap explains why the annual MD&A amount is
compatible rather than manufacturing a conflict. The December current-securities
restriction makes the maturity/general-use distinction concrete. The final
paragraph keeps the two maturity populations separate and retains management's
operating-cash and debt-market assumptions. The table fits within the text block;
negative signs, dates and commas are legible.

Page 23 starts from the observed difference between securities decline and cash
released. M0/M1, C and R are defined before the display, including signs, units
and period. Both annual and quarterly instances are explained; the following
paragraph leaves R unallocated. Total investment valuation, marketable-debt
OCI and cash-flow cash are then distinguished by their populations. The final
paragraph separates a fair-value rate scenario from cash payments. The citation
review corrected annual comprehensive income to printed page 30 and added a
direct Note 1 anchor for specific identification. The corrected page has no
clipped text, detached qualifier or problematic break.

Page 24 moves from possible future receipts to collection amounts and customer
membership. It explains the indirect-cash-adjustment limitation before adding
concentration. A and B are whole-customer sets, s is their receivable share,
and displayed percentages are explicitly treated as exact illustrative centres
before inclusion-exclusion appears. The eleven-customer example constructs
both endpoint memberships, with exactly two customers at least 10 percent.
The denominator, collateral and loss-probability qualifications remain adjacent.
Vendor receivables then introduce their own component-sale origin and denominator.
The ending returns to the historical record; page 25's existing source-assertion
chapter can use that distinction without new notation or a retrospective rewrite.

## Reader questions answered from the rendered slice

| Question | Supported answer |
| --- | --- |
| Why does the resource total not identify general-use funds? | The reported total includes escrow; current marketable securities can also be restricted. Removing disclosed escrow does not identify liquidation prices or payment dates. |
| Does 140,850 million contradict reported 140.8 billion? | No conflict follows. Under nearest-display rounding, possible subtraction and MD&A ranges overlap; the convention itself is conditional. |
| Why does security-stock decline differ from cash released? | Maturity and sale cash less purchases measures net cash. The carrying movement additionally needs book disposals and measurement/classification movements; +8,263/−2,303 remain unallocated. |
| Can OCI explain the residual by subtraction? | No. Endpoint total unrealised balances include a different population; the period marketable-debt OCI is net of tax and includes reclassification. |
| What do maturity and sensitivity disclosures add? | Dated contractual bands with two separate denominators, and an issuer fair-value response to a specified rate shock including derivatives. They provide neither immediate cash nor a probability of loss. |
| How can 18%, 11% and 33% coexist without adding to 62%? | The two large customers may be inside the carrier group. Exact-centre whole-customer membership gives possible unions 33/44/51/62%; both extreme cases have explicit constructions. |
| What still determines receipts and funding? | Lots, cash-sale/book-disposal links, currencies, restrictions, settlement dates, customer identities/membership, denominator basis, allowances, collateral and actual collection events. |

## Equation and source review

The stock/cash equation is a definition of a residual on displayed USD-million
centres. It is correct as an identity and wrong if used to claim that the
residual is an identified gain, FX movement or journal. Negative C would mean
net cash investment; positive R offsets part of a cash-release-induced stock
decline. Source cash rows and the two dated balance populations determine the
shown residuals, but not their causal allocation.

The concentration equation is finite-set inclusion-exclusion for sums of
receivable shares. It is exact for a common denominator and the assumed
displayed centres. Customer membership is binary. If both major customers are
carriers the overlap is 29%; if neither is, it is zero; one-customer membership
gives overlap 18% or 11%. The equation is not a probability model and the
examples fit marginal percentages only, not a complete Apple history.

Both displays are used immediately and need no equation numbers. The surface
audit's three-environment count includes the nested aligned block, leaving two
new display objects. Its unreferenced section label is a navigation anchor;
no missing reference, duplicate label, repeated-word or placeholder finding
was reported. These diagnostics do not certify comprehension.

The source evidence review is in `pre-integration-review.md`: two complete notes,
fourteen material units, thirteen declared dependencies and eleven queries.
It includes original annual pages and a clearly identified derived interim
view with original grid alignment and complete excerpt text. The new table
preserves the source label adjusted cost. No source has been modified.

## Four separate verdicts

| Ledger | Verdict and limit |
| --- | --- |
| Reader comprehension | The bounded addition makes restriction, security cash/valuation and customer overlap explainable in the funding question. The answers above are author judgments; independent/human reading remains pending. |
| Mathematical integrity | The stated sums, residual identities, conditional rounding overlap and discrete membership examples are correct within their assumptions. No full history, causal residual allocation, operative accounting compliance or forecast is established. |
| Source fidelity | Complete bounded notes and dependencies preserve dates, units, precision, maturity populations, OCI tax scope and risk qualifiers. Source/citation repairs are preserved; unknown actual lots, counterparties and settlements remain unknown. |
| Typography and rendering | Six body pages read continuously and seven navigation pages inspected. Table, equations, citations, signs and page transitions are legible; final LuaLaTeX/bibliography logs are clean. This is not a full 149-page reread. |

The strongest alternative explanation for an apparent reconciliation is a
change in population or undisclosed transactions. The text preserves those
possibilities rather than naming a cause from a residual. Instrument/customer
records could allocate particular movements or resolve overlap; current
aggregates cannot. Missing actual facts and independent assessment are the
weakest evidence, not arithmetic precision. No continuation veto remains for
this bounded integration; wider readiness remains `not_ready`.
