# Bounded P18 sectors integration review

## Scope and method

I recomputed every numeric case in the four packet files and checked each against `method-cases-v1.json`, then checked the paragraph/section citations against the standards as retained in the packet's own descriptions. I did not re-derive non-numerical prose claims beyond source-boundary consistency.

## Verified (no finding)

- **Bank one-path (15-banking.tex §2):** opening identity 129.2; post-events 21+120−2.4=138.6=117+21.6; runoff 25 → draw 4, cash 0, deposits 92; runoff 40 → 9 unpaid; capital 19.6, RWA 90. All consistent. Origination-via-deposit vs external-transfer separation is correctly kept.
- **Loan roll-forward (bank-methods.tex):** 12-month ECL 0.1×60.5/1.21=5 (lifetime 10); survival-only conditional 1/9 stated and correctly *not* used; authored revision to 0.2 → 11, impairment 6, equity 19; credit-impairment allowance 110−55=55, impairment 44, equity −25; year-two net interest 55×10%=5.5 with gross accretion 11 decomposed 5.5/5.5 → gross 121, allowance 60.5; collection 160.5, write-off to zero; total interest 15.5 − impairment 55 = −39.5 = 100−60.5. Every JSON `rows` entry matches. Initial unconditional law, survival conditioning and changed forecast are kept distinct; gross vs amortised-cost interest basis is correctly switched only at the credit-impairment event (AASB 9.5.4.1(b)). Modification 110→100, loss 10, matches 5.4.3.
- **Funding/capital (methods §4):** 20+8−30 = −2; 18/125 = 14.4%. Matches JSON.
- **PAA + reinsurance (16-insurance.tex):** cash 101; assets 101+12+6=119; liabilities 60+12=72; profit 60−42−12+21=27; equity 47; 72+47=119. Reinsurer kept as separate asset (coverage 12, claims 6, with RA 1 as risk transferred), not netted. Citations 53(b), 69(b), 62–62A, 63–70A, B126 are correct.
- **Chain ladder:** f₁=330/220=1.5, f₂=1.2; ultimates 180/216/252; outstanding 0/36/112, total 148; single final-factor observation correctly flagged as variance-unresolved. Matches JSON.
- **Zero-rate GMM two-year:** FCF −30, CSM 30, LRC 120 = 80+10+30; yearly revenue 60, profit 20; rows [80,60,20],[40,0,40]. Onerous step: FCF +20 → CSM 15 consumed, loss 5, LRC 65 with loss component as tracked portion; decrease 8 → loss reversed 5, CSM 3, FCF 57, LRC 60; LIC-only change 8 correctly bypasses CSM. Matches JSON and 48–52/B96–B97 ordering.
- **Unreversed onerous year two:** allocation 60/13 + 5/13 = 5; revenue 60; profit 60−60+5=5; lifetime 20−5+5=20; cash 20 = equity 20. Matches JSON; consistent with B124 exclusion.
- **Nonzero 10% case:** PV 40+40=80; CSM 30; year 1: accretion 8+3=11 finance, CSM 33 → release 16.5, revenue 65.5, profit 10.5, cash 76 = LRC 65.5 + 10.5; year 2: accretion 4.4+1.65=6.05, revenue 71.55, profit 17.1, cash/equity 27.6; totals 137.05−17.05=120. RA treatment under paragraph 81 is explicitly declared as authored. Matches JSON.
- **Reinsurance collectability:** 100×½×0.9=45. Matches.

## Findings (all minor, nonblocking)

**F1 — `method-cases-v1.json`, missing fixtures for chapter-level examples.** The chapter-15 one-path case (138.6 identity; runoff 25/40; 19.6/90) and the chapter-16 PAA/reinsurance case (profit 27, equity 47, assets 119) have no fixture entries; only the `sections/*-methods.tex` cases are fixtured. Hand verification passes, but the stated purpose ("exact synthetic document calculations") does not cover them. *Repair:* add `bank_path` and `insurance_paa` cases, or state in the JSON `purpose` that chapter narrative examples are outside the fixture set.

**F2 — `sections/insurance-methods.tex`, PAA/reinsurance section, "; .45 and B101--B118".** Leading-dot paragraph reference is a transcription typo (should be "paragraph 45"). *Repair:* "paragraphs 45 and B101--B118".

**F3 — `sections/insurance-methods.tex`, nonzero-discount section, "44, 80--88,B119".** Missing space after comma; cosmetic. *Repair:* "80--88, B119".

**F4 — `sections/bank-methods.tex`, roll-forward section.** The year-two posting "credits interest revenue 5.5 and allowance 5.5" is arithmetically right, but the text should name the allowance credit as discount unwind presented within impairment movement, so the attribution rule stated earlier ("changes in allowance must be attributed…") has a label for it. *Repair:* one clause naming the attribution bucket; no number changes.

**F5 — `method-cases-v1.json` `document` anchors.** Fixtures point at `*-methods-v1.md#B3/#I2/#I2a` while the manuscript integrates `sections/*-methods.tex`. Acceptable as provenance to the frozen markdown, but a reader of the manuscript cannot resolve the anchors. *Repair:* add the `.tex` `\label` names alongside the markdown anchors.

No calculation error or source-boundary misattribution was found. The honestly retained gaps (full IFRS 9/CECL staging, VFA, transition, Basel calibration, actuarial RA) are labelled as such and are not counted against the packet.

## Verdict reason

All bank and insurance schedules reconcile internally and to the accepted fixtures; default-law, survival-conditioning and forecast-revision are correctly separated; gross/net EIR switch occurs at the right event; CSM/RA/LRC/LIC and loss-component mechanics follow the cited paragraphs; reinsurance is never netted. Findings are documentation/fixture-coverage items only, within this packet's integration scope.

VERDICT: AGREE
