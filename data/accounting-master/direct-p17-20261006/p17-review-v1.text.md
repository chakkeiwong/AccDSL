# Independent integrated P17 review

Scope of what I checked: every numerical schedule in the eleven method documents and method-cases-v1.json was independently recomputed (revenue/billing orders, FIFO/average/NRV, PPE, lease 210/110/0 and modification 220, lease–tax joint statements 811.5/813.25 and both OCF paths, EIR root and fee, 10% test, modification gain, repurchase, treasury/compound equity, acquisition/NCI/step-up/disposal gains 18/23, intragroup 40/DTA 10, FX 10/5 and translation OCI 11 = 100×0.1+20×0.05, bank five-row roll-forward and 15.5−55=−39.5, insurance base, onerous reversal/restoration, onerous carry-through 60/13+5/13, nonzero-rate 65.5/71.55/17.05, chain-ladder 148, pension 116/88/28/13/5, impairment, awards, provision, valuation, finite Bayes 3/11, Gaussian 8/5–16/9, causal 3 vs 2.5, rounding enclosures, √1.1 enclosure). All agree with the stated values. Interface routing was checked against interfaces-contract I2 rows and the cross-contract amendment; ASBE21 claims were checked against the retained Chinese text (articles 6, 14–18, 20–23, 25–29, 30–33, 60–67, 68; publication 2019-10-28); AASB 17 onerous ordering was checked against paragraphs 44/48–51 and B120–B124; AASB 9 credit-impaired interest against 5.4.1(b). No contradiction between methods, no lost economic state, no invented probability, and no wrong-timing defect found. The six author repairs are substantively adequate. Remaining findings are traceability/editorial.

## Findings

**F1 (low) — Index interface strings garbled after routing repair.** `corporate` and `bonds_equity` interface fields read "…events follow accounting.assess@1 evaluates the native request; …" (two clauses concatenated). Consequence: manuscript integration would copy a syntactically broken routing statement for exactly the item repaired. Repair: "…events are routed as follows: accounting.assess@1 evaluates…" (groups/banks/insurance variants are well-formed).

**F2 (low–medium) — Source-register locators narrower than cited paragraphs.** (a) financing-methods F1–F2 cite AASB9 4.1.2/4.1.2A, 5.1.1, 5.1.

1A/B5.1.2A and 3.3.1–3.3.3; the A9 register locator lists only 5.4.1–5.4.4, 5.5.1–5.5.20, B3.3.1–B3.3.6, B5.4.6, B5.5.26–B5.5.55. (b) corporate-extensions X1 cites IAS19.83; EU2023 locator lists 67–74/113/120–127 only. (c) X4 says IFRS13 ".61–90 guide"; locator covers 24/42–43/69–73 and 67–80. (d) AASB116.7/15, 29–30, 48–62 (C1) and the Green2007/Doshi2024/Halaj/Behn mentions have no entry in method-source-register-v1; they rest on prior P08/preparation packets per the brief, which I cannot inspect. Consequence: the register cannot be used as the sole provenance check for these mechanism claims. Repair: extend the locators (or cite "per preparation-20261005 source-register / P08 A01–A07" inline) and narrow IFRS13 to 67–80 (69/80 are the only paragraphs actually used). Not a readiness blocker; these are mechanism citations, not authority admissions.

**F3 (low) — Debt modification wording ambiguous.** F2: "Replace with 133.1 due one year later" — the arithmetic (PV 121 at 10%, new EIR 133.1/118−1) only holds if 133.1 falls due on the original maturity date (one year after the modification). If read as "one year after the original due date", PV = 110 and the 10% test fails. Repair: "due at the original maturity date, one year after the modification".

**F4 (low) — Northstar opening facts in cases but not in the specification text.** method-cases `joint_forecast` uses opening_equity 90.6, opening_cash 74.6, capex 20, dividend 8 and implicitly a 7% floating rate (interest 5(1−x)+7x) and in-year tax settlement (no tax payable on the balance sheet). C3 states none of these, yet "A 9% floating rate gives all-floating interest 9" cannot be derived from "5+2x" without the 7% base. Consequence: a reader of C3 alone cannot reproduce the 9% row or the cash/equity reconciliation. Repair: one sentence in C3 stating the opening cash/equity, capex, dividend, 7% base floating rate and same-year tax payment, with the protected fixture as source.

**F5 (low) — Index bank assumption misstates weights.** `banks.assumptions` says "weights 0.9/0.1 then 0.8/0.2"; B3's initial law is three-scenario 0.1/0.1/0.8 (lifetime 10, twelve-month 5). Repair: "initial masses 0.1/0.1/0.8, revised 0.8/0.2".

**F6 (low) — Event naming drift.** C1 table uses `consume_or_sell`; index uses `consume`. Repair: align.

## Context insufficient
Protected Northstar fixture, prior P08/preparation source registers, the 192-report panel, the "136 unverified publication dates", Apple fiscal-week assertions and the Halaj/Behn/Green/Doshi ledgers were not supplied; I accept the brief's statement that six quote hashes and 1,244 protected files were verified and make no independent claim about them.

## Named full-readiness blockers (not P17 defects)
Current ASC (403), ASBE18/Interpretation16/lease notice (502), real package closure, source-backed conflict, adapter runtime, empirical forecasts and human acceptance remain correctly labelled blocked/open (E01/E05/E07/E08/E11–E14). The specifications do not overstate them.

The stated methods and finite examples are internally coherent, correctly scoped, arithmetically exact, consistent with the P16 contracts and the inspected source excerpts, and suitable as a source-limited proposal specification for manuscript integration once the minor repairs above are applied.

VERDICT: AGREE
