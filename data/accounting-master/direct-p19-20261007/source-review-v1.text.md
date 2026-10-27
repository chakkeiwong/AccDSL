# P19 review: ASBE lease-tax source supplement

Scope of this review: the supplied `asbe-tax-source-repair-v1.md` checked against the retained Chinese text of ASBE 18 (all 25 articles), the Interpretation 16 PDF text (5 pages), the 财会〔2018〕35号 notice page, the supplied ASBE 21 articles 60–68, `inspection-v1.json` and `check_source_repair.py`. No tools or external material used.

## A. Source-rule claims verified against the supplied text

| Supplement claim | Source location | Finding |
|---|---|---|
| ASBE 18 title and publication 2006-03-09; template date and URL directory are not dates of the standard | asbe18.txt: title line; `发布日期: 2006年03月09日`; template line `2017年11月21日 星期二`; URL `200806/` | Verified. Correctly separated. |
| Arts 4–9 define tax bases and taxable/deductible temporary differences | 第四条–第九条 | Verified. |
| Arts 11(2) and 13 hold the original initial-recognition exemptions; Art 13 limits DTA to probable taxable profit | 第十一条（二）, 第十三条 `以很可能取得…应纳税所得额为限` | Verified. |
| Arts 16–20: measurement, rates, consistent recovery/settlement basis, no discounting, review | 第十六条–第二十条 | Verified. Art 19 quote located. |
| Arts 21–23: P&L vs equity allocation; separate noncurrent presentation | 第二十一条–第二十三条 | Verified. Note: the retained ASBE 18 text contains **no offset criteria at all** (nothing analogous to IAS 12.74). The supplement's refusal to settle offset from Art 23 alone is therefore correct; `分别…列示` is a classification instruction, not an offset rule. |
| Interp. 16 I(a): not a business combination, no initial effect on accounting profit or taxable income/loss, equal taxable and deductible TDs; examples lessee lease liability/ROU and decommissioning; excluded from Arts 11(2) and 13 exemption; recognize DTL and DTA 分别 | PDF text lines 14–22, page 1 | Verified. "Under the applicable income-tax provisions" matches `应当根据《企业会计准则第18号——所得税》等有关规定`, which is the hook that keeps Art 13 recoverability in force. |
| I(b): transactions between earliest comparative opening and 施行日 adjusted; existing qualifying balances at that opening → cumulative effect to opening retained earnings and other items; disclosure; early application from issuance year with disclosure | page 2, lines ~30–41 | Verified. |
| IV: Section I effective 2023-01-01; II and III from publication | page 5, lines 111–114 | Verified. II and III transition clauses reference 2022-01-01 and (III only) `对可比期间信息不予调整` — correctly kept out of the lease-tax treatment. |
| Notice 财会〔2018〕35号, signed 2018-12-07, published 2018-12-14, URL 13 Dec | lease-notice-recovery.txt: document number, `2018年12月7日`, `发布日期: 2018年12月14日` | Verified. |
| Para I: dual-listed and overseas-listed IFRS/ASBE preparers from 2019-01-01; other ASBE enterprises from 2021-01-01 | Para 一 | Verified; translation accurate. |
| Para II: early adoption only for enterprises whose parent or subsidiary is overseas-listed and prepares overseas statements under IFRS/ASBE; not before simultaneous

application of ASBE 22 (2017-03-31) and ASBE 14 (2017-07-05) | Para 二 | Verified. |
| Para III discontinues 2006 ASBE 21 and its application guide | Para 三 | Verified. |
| Art 61: retrospective (ASBE 28) or cumulative-effect to opening retained earnings without comparative adjustment, with detailed conditions | 第六十一条（一）（二） | Verified; `不调整可比期间信息` located. |
| Art 68 general 2019 date does not fix every entity's mandatory date | 第六十八条 + notice Para 一 | Verified; the notice's staged schedule governs. |

## B. Arithmetic (recomputed by hand)

- PV: 121/1.1 = 110; 121/1.21 = 100; total 210. ✔
- Liability: 210 → 231 − 121 = 110 → 121 − 121 = 0. Interest 21, 11. ✔
- ROU: 210, 105, 0. ✔
- DTA (liability × 25%): 52.5, 27.5, 0. DTL (ROU × 25%): 52.5, 26.25, 0. ✔
- Year 1: DTA −25 (expense), DTL −26.25 (benefit) → net benefit 1.25. Year 2: net expense 1.25. Lifetime 0. ✔
- Consistency check not stated in the supplement but confirming its assumptions: year-1 book expense 126 vs tax deduction 121 → current tax 1.25 above 25% of accounting profit; deferred benefit 1.25 offsets it; total tax = 25% × accounting profit. The "deductions allocated to the liability / zero tax bases" assumption is internally coherent.
- Transition: 500 + 105 + 27.5 = 632.5; 110 + 26.25 = 136.25; 495 + 1.25 = 496.25; 136.25 + 496.25 = 632.5. ✔ Journal DTA 27.5 = DTL 26.25 + RE 1.25. ✔
- `check_source_repair.py`: ROOT = parents[3] resolves to repo root; expected values are literals, PV computed from cash flows; sign convention `(ΔDTL − ΔDTA)` as expense is consistent with the prose. Hash and quote-containment checks match the JSON.

## C. Located findings (none blocking)

1. **Interpretation 16 metadata not verifiable from what I was given.** `财会〔2022〕31号`, signed 2022-11-30, published 2022-12-13 rest on `interpretation16.txt` (HTML page), which was not supplied; the PDF text carries no number or date. The URL directory says `t20221212`, the attachment filename `P020221213`. The supplement handles the analogous URL/print discrepancy for the 2018 notice but is silent on this one. Non-blocking; record as "verified from HTML page only" in the next revision.

2. **PDF extraction order glitch, lines 18–19.** `，不适用《企业会计准则第 18 号` precedes `称适用本解释的单项交易）`. The anchor quotes at lines 14 and 16 are unaffected; the substantive reading is correct. Worth a footnote so a later reader does not think a clause is missing.

3. **I(b) comparative restatement is implied but not stated.** Section I(b) lacks the `对可比期间信息不予调整` language that Section III contains; its first sentence adjusts transactions in the window from earliest comparative opening to 施行日. In the illustration this means the comparative year's deferred net expense of 1.25 would also be restated, not only the opening equity. The supplement says "comparative periods must be supplied by the entity"; it does not misstate, but the next revision should say explicitly that Section I(b) implies adjusted comparatives.

4. **"Verified early adoption" under-specifies eligibility.** Early adoption of ASBE 21 is available only to Paragraph II enterprises (parent/subsidiary overseas-listed, IFRS/ASBE overseas statements) and only after ASBE 22/14. A second-group entity with no such affiliate could not early adopt at all. Minor precision.

5. **Anchor line numbers are not checked.** The script checks `quote in file`, not the `line` field. Harmless for verdict; note so line numbers are not treated as verified.

6. **ASBE 21 attachment articles 1–8, 14–18, 20–33 not supplied** to this reviewer; only 60–68. The supplement's lessee scope/measurement claims from those articles are accepted as declared inspection, not independently verified here.

## D. Boundary confirmations

- 2019/2021 (lease adoption) and 2023 (Interpretation 16 Section I) are kept distinct throughout; no conflation found.
- Illustrative parameters (210/121/10%/25%, zero tax bases, recoverability, 500/495 opening balances) are clearly labelled assumptions; no actual tax-law, entity, adoption, amendment or offset fact is asserted.
- The competing "old exemption, zero deferred balances" reading is correctly rejected for a qualifying post-2023 case by I(a)'s express exclusion.
- The supplement states the correction is for the *next* manuscript revision. This AGREE does not imply the frozen P18 PDF contains it, nor E07 closure, nor current-2026 ASBE compliance, nor any later-amendment census.

VERDICT: AGREE
