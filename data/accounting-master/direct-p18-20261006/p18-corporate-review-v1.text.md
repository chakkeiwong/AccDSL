# P18 corporate integration review

Scope: transcription of corporate, lease/tax, financing, group/FX and standards numerical methods into the manuscript, checked against `method-cases-v1.json` and the P16/P17 boundary text. Retained open gaps (current ASC, real-company semantics, insurance VFA/transition, actual regulatory/actuarial data, human acceptance) are not counted as failures.

## Arithmetic spot-checks (all reconcile)

- **Lease/tax (corporate-methods §2 vs JSON `lease_tax`)**: PV 110+100=210; interest 21/11; liability 110/0; ROU 105/0; DTA/DTL 52.5→27.5/26.25→0; taxable 179, current tax 44.75; pretax 174/184; tax 43.5/46; profit 130.5/138; cash 679/813.25; equity 630.5/768.5; both balance-sheet identities (811.5, 813.25) and both indirect OCF reconciliations (300, 255.25) hold. Modification 144/1.2+144/1.44=220, +110, ROU 215. Matches JSON exactly (including the −1.25/+1.25 deferred rows).
- **Standards lease contrast (§S2–S4 vs JSON `lease_basis`)**: IFRS 126/116; US single expense 121 with interest 21/11 and ROU reduction 100/110, ROU 110/0. Consistent across standards-methods, corporate-methods and ASBE section (ROU 210/105/0).
- **Debt (financing-methods F1–F2 vs JSON `debt`)**: EIR 10%; 110/121; PV(133.1)=121, Δ=11=10% inclusive; loss 8 against FV 118; 115.5/1.1=105, gain 5, interest 10.5; repurchase gain 2; unpaid 41; half-year factor 1.1 vs wrong 10.5. All match.
- **Shares/compound (F3 vs JSON `shares`)**: 200/−30/+20, treasury cost 15, other equity 5, outstanding 95; compound 90/10, accretion 10, no conversion cash. Chapter 14 coupon bond: 11050/121≈91.3223, 1050/11≈95.4545, then 100. Correct and explicitly distinguished from the zero-coupon F3 case.
- **Groups (G2 vs JSON `group`)**: NCI 20, goodwill 16; NCI 24, parent 16; transfer 12, equity debit 3, NCI 12; gains 18 and 23. Chapter 14 zero-goodwill case: group 110, loan elimination, disposal gain 4, residual 104. All reconcile.
- **Intragroup/FX (G3–G4 vs JSON)**: elimination 40, outside profit 60, DTA 10; 120/130/10/125/5; translated 156/120/25, OCI 11 = 100×0.1+20×0.05, split 8.8/2.2. Correct.
- **Extensions (X1–X4 vs JSON)**: DBO 116, assets 88, net 28, expense 13, OCI 5; unit PV 1000/11, 200 settlement; impairment 30=20+10, reversal cap 20; awards 150/90 and 200/200/400; valuation 70, 100, 4. Correct.
- **Operating (C1, C3)**: revenue AR/CA/CL states (20/10/0; 50/0/20; prebill 80/0/80); inventory 26/24, 30/20, margins 22/18, write-down 8, reversal 6, cap 24; PPE 30 then 20; Northstar linear family, 288.2=148.2+140, 9% all-floating 62.4/92/145/285. Chapter 8 inventory (64/56, 80/40, 72/48; 6 then 4) correct.

No old/new contradictions were found between chapters 8/14 and the inserted sections; source-status statements (AASB compilation dates, EU 2023/1803 historical scope, ASBE 21 official page, ASU non-authoritative covers, ASC 403) are consistent in every location.

## Findings (all minor, nonblocking)

1. **`sections/standards-methods.tex`, "US GAAP proposed methods", ASC 740 paragraph.** The text states book 800/tax 600 → DTL 50 (a 200 difference), then "the saved matrix shows 75 versus 90 on a 300 closing difference under the declared 2025 facts", while "75" also appears as current tax on taxable 300. A reader cannot reconstruct which year carries the 300 difference or whether 75 is current tax or a 25% DTL. Repair: state the 2025 closing difference explicitly (e.g. "closing difference 300 in 2025 gives DTL 75 at 25% versus 90 at 30%") and separate it from the current-tax 75.

2. **`chapters/14-financing-groups.tex`, chapter preamble.** "the coupon-bearing convertible below and the later zero-coupon modification are different instruments" — the zero-coupon compound in `financing-methods.tex` §F3 is a separate issuance example, not a modification. Repair: reword to "the later zero-coupon compound example in the financing methods".

3. **`methods/method-cases-v1.json`, `lease_tax.expected.deferred_expense`.** Sign convention (negative = net deferred benefit) is not declared anywhere in the JSON; the prose only says "net benefit 1.25". Repair: add a one-line convention note in `purpose` or a `conventions` field so the array is reconstructible without the manuscript.

4. **`sections/corporate-methods.tex`, "Lease and tax integration", cash-flow paragraph.** "Select financing classification for lease interest under the retained AASB 107 regime" is an election (AASB 107 permits operating or financing presentation of interest paid), and the OCF 300/255.25 and the "−121 financing" figures hold only under it. The JSON `lease_tax` case does not record that election. Repair: add the classification election to the JSON inputs (or label it in the prose as a declared election) so a different election visibly changes OCF rather than silently failing reconciliation.

5. **`sections/corporate-methods.tex`, "Operating events", AASB 15 paragraph.** "the retained compilation applies to the stated for-profit FY 2024 example" sits alongside `standards-methods.tex` dating the AASB 15 compilation 31 December 2022 "with the source covers' application window". Not contradictory, but the applicability bridge is left implicit. Repair: add "(compiled 31 Dec 2022, application window covering FY 2024 per cover)" or a cross-reference to the standards section.

6. **`sections/groups-fx-methods.tex`, "Perimeter and consolidation state".** The 80%/96 goodwill case is introduced as "a new example; it does not change the preceding zero-goodwill case" — correct, but Chapter 14's zero-goodwill case states "no tax or goodwill arises" without noting it is a different acquiree (net assets 50, price 40). Repair: one clause in Chapter 14 ("a different acquiree from the goodwill case that follows") to prevent a reader from attempting to reconcile 40/50 with 96/100.

## Verdict reason

Every copied numeric path reconciles with the accepted JSON fixture and internally across chapters; no transcription error, contrary assumption or standards overclaim was found. Source limits and the honestly retained gaps are stated consistently and are not upgraded to authority. The six findings concern reconstructability wording and one undeclared election/sign convention, none of which changes a value or a verdict in the packet.

VERDICT: AGREE
