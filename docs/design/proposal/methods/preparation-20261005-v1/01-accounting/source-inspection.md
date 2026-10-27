# Inspected authority, derivations and source limits

The four retained PDFs come directly from the Australian Accounting Standards
Board. Their text conversions preserve form feeds for physical PDF-page anchors.
The official portal was queried for 1 January–31 December 2024; its relevant
result pages and each standard's landing page are retained under `sources/`.
Five earlier guessed paths returned HTTP 404 and were not used as evidence.
`source-register.json` records their disposition, all authoritative file hashes,
the URLs and every selected paragraph's exact opening line, text line and page.
Copyright notices are retained. This is internal source preparation, not a
public redistribution or a commercial publication decision.

The primary baseline is a hypothetical Australian for-profit Tier 1 reporter
with a calendar 2024 annual period. AASB 16 and 112's physical-page-5 comparisons
were inspected. They establish the stated IFRS 16/IAS 12 incorporating relation
for that reporting tier. They do not establish actual entity eligibility, another
jurisdiction's endorsement or the full later amendment chain. Covers show start
conditions, not expiry dates; this record does not invent an end date from the
absence of one. The 2025–2029 arithmetic is a conditional continuation under
the pinned rules, not a certification of future applicable law or reporting rules.

| Source | Actual version and application | Inspected support and allowed use |
| --- | --- | --- |
| L16 | AASB 16 compilation 8, 31 December 2023; F2024C00049 registered 16 January 2024; annual periods beginning from 1 January 2024 | Scope/exemptions 3–8; lease identification 9, B9–B30; component and term rules 12–21; lessee recognition/measurement 22–46; presentation and selected disclosures 47–59; Appendix A definitions; C1–C1D effective dates. Supports the stated lease and selected modification with declared facts. Does not complete lessor, impairment, sale/leaseback, transition or full disclosure methods. |
| T112 | AASB 112 compilation 7, 29 September 2023; F2023C00930 registered 24 October 2023; periods beginning from 1 January 2023 and ending from 30 September 2023 | Definitions/tax bases/current recognition 4A–17; selected initial/deductible provisions 22–29; losses 34–37; rates/recovery 46–51A; no discount/reassessment/allocation 53–61A; offset and selected disclosures 71–81; single-transaction transition 98J–98L; Pillar Two 4A/98M; accompanying Example 8 and footnote 2 on pages 50–51. Supports conditional accounting given tax-law/recovery facts; it supplies no real jurisdiction's tax deductions/rates. |
| P116 | AASB 116 compilation 6, 31 December 2022; F2023C00192 registered 13 February 2023; periods beginning from 1 January 2023 | Recognition and initial cost 7/15; class-wide policy 29 and cost model 30; depreciation expense, residual/life review, available-use timing and method 48–62. Supports the specified even-consumption/no-loss assumptions. Does not validate the selected five/ten-year estimates or a real impairment assessment. |
| CF107 | AASB 107 compilation 5, 31 December 2023; F2024C00050 registered 16 January 2024; periods beginning from 1 January 2024 | Interest/tax cash-flow classification 31–36, noncash exclusion 43–44 and financing-liability reconciliation 44A–44D. Supports a consistently selected financing-interest policy for this nonfinancial company and the declared operating tax cash flows; no later AASB 18 regime is silently imported. |

The L16 upstream filename contains `COMPnov22`, while the cover's compilation
date is December 2023. The CF107 filename contains `COMPjun23`, while its cover
also says December 2023. Filenames are retrieval identifiers, not date authority.
The paragraph register records physical-page positions from retained bytes. A
self-review found that a paragraph starting immediately after a form feed could
be assigned the preceding page; the register generator and check now account for
the form feed before the paragraph (notably T112.98L on physical page 29).

| Claim | Exact support | Local deduction and boundary |
| --- | --- | --- |
| Two-year ROU/liability initially 210 | L16.22/24/26/27, physical pages 8–9; Appendix A commencement and IBR, pages 20–21 | Sum of discounted 121 payments; implicit rate unavailable and supported IBR 10% are case assumptions. ROU equals liability only because other cost components are absent. |
| Separate annual depreciation 105 and interest 21/11 | L16.29–33/36–38, pages 9–10; P116.48–62, pages 12–13 | Straight-line is selected because benefits are assumed even; liability accretes its remaining balance. No general best depreciation method or rate estimate is established. |
| Same-asset modification uses revised rate and ROU adjustment | L16.44–46, page 11; modification effective-date definition, Appendix A page 20 | New terms agreed 1 January 2025 create revised PV 220, liability increase 110 and ROU 215. No asset is added and no scope is terminated. Index resets have a different rule in 42–43. |
| Substantive substitution can defeat identified asset; uncertainty has a special presumption | L16.B14/B19, page 24 | L03 positively supplies both substantive conditions. Merely absent information is not equivalent to established substantive rights. |
| PPE timing difference creates DTL 50 in 2024 | T112.7/15–17, pages 7/9–10 | Book 800 minus tax base 600 equals 200; multiply by assumed enacted 25%. Asset-tax basis and jurisdiction deductions must be separately supported for real use. |
| Current tax 75 differs from total tax expense 125 | T112.5/6/12/46/58, pages 7/9/17/21 | Given pretax profit 500, add back book depreciation 200 and deduct tax depreciation 400. Profit input is external to this tax method; rest-of-company journals are not invented. |
| 2025 rate change adds 15 deferred expense without changing 2025 current tax | T112.46–48/51/60, pages 17/21 | Taxable profit remains 400 at 25%; all closing 300 difference reverses at assumed enacted 30%. Effective date and enactment date must be separate facts. |
| No unsupported DTA for losses; no discounting | T112.34–37, pages 15–16; 53/56, page 20 | T03's negative recovery facts block recognition; an unknown fact keeps the claim unresolved. Arithmetic of 100×25% is potential benefit only. |
| Equal initial lease differences need separate recognized gross tax consequences | T112.15/22A/24, pages 9/12; 98J–98L, pages 28–29; accompanying Example 8 and footnote 2, pages 50–51 | Attributed liability deductions, tax bases zero and probable usable profits are required facts. DTA/DTL 52.5 is their consequence; different tax attribution can remove initial differences. Accompanying example illustrates, while normative paragraphs supply the rule. |
| Net presentation requires additional conditions | T112.71/74–75, pages 23–24 | Gross records survive. Same values, entity names or currency are not enough to establish a legally enforceable setoff right. |

This is not an academic method survey. Citation counts, venue ranks and paper
snowballing do not determine the operative standard. Related technical standards
were followed where needed for the immediate depreciation/cash-flow claims.
Full impairment (AASB 136), maturity disclosure (AASB 7), estimates/errors (AASB
108), actual tax law, uncertainty in income-tax treatment and complete effective
chains remain identifiable internal tasks. A preserved source plus an inspected
selected paragraph is stronger evidence than a summary, but does not amount to
a full-domain or full-standard review.
