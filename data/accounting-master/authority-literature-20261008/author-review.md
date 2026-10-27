# Version 2.4 bounded author review

8 October 2026. Candidate:
`docs/design/proposal/manuscript-authority-20261008/accounting-product-proposal.pdf`.
128 pages; SHA256 `0391d75656859855838ea356387fd846c6979a346c549df1e6fbfcf46970d632`.
Baseline is the protected 127-page Version 2.3. This is the authoring agent's
bounded review, not independent accounting, ordinary-reader or human acceptance.

The actual final rendered pages were viewed individually at normal resolution:
1, 5–6, 60–61, 81–85 and 123–128. The images and their PDF binding are in
`render-manifest.json`. The bank sequence was read in order from the preceding
funding/allowance example through the altered source explanation and the
subsequent funding-policy section. Bibliography inspection covers its complete
final six pages. No complete-document read is claimed.

## Findings and dispositions

* Page 60 now names the dated ASBE 22 support and leads to Chapter 11 while
  preserving the unknown entity-specific amendment/application chain. Page 61
  remains a distinct inventory comparison; the credit-loss addition does not
  claim to settle that inventory authority gap.
* Page 81 retains the earlier liquidity illustration and conditional ECL
  display. The text still distinguishes its inputs from the later loan.
  Its old display, probability dependence and cash-flow horizon qualification
  remain unchanged.
* Page 82 adds Article 47/48 support immediately after the verbal horizon
  distinction, then explains the risk test, probability-weighted measurement
  and source-date limits. It fits without clipping. The pre-existing interface
  explanation continues on page 83; it remains implementation-reference prose.
* Page 83 establishes the bullet-loan facts and qualitative default before the
  first allowance calculation. The original calculations are retained. The
  new one-year boundary explains why the same amount can arise in two stages.
  The next paragraphs distinguish expected recovery from a maximum recovery and
  make the assumed write-off information sequence explicit. These repair
  consequential assumptions, not just style. They do not establish real credit
  judgments. The paragraph continues naturally onto page 84 at the write-off
  posting; no text or table is clipped.
* Page 84 retains all five balance-sheet rows, negative equity, the total-loss
  reconciliation and the asset-modification example. The new Article 42/56
  sentence preserves the distinction from the liability ten-percent test.
  Page 85 retains capital/funding and forecast-validation limits. Its short
  final-page text is acceptable at this chapter boundary; no content was
  compressed or deleted merely to reduce pagination.
* The title and contents identify Version 2.4 and retain the bank section
  sequence. Bibliography pages 123–128 retain the earlier entries and add the
  official ASBE 22 source, exact inspected articles, page date and unresolved
  issuance/amendment limits. URLs and notes fit their columns. The final
  LuaLaTeX log has no warnings or overfull/underfull boxes.

## Content preservation and reader questions

The candidate changes only the title version, the Chapter 9 authority paragraph,
the bank-method section and one appended bibliography entry. All other source
files, the bank table, existing displayed equations and older bibliography
entries are preserved. The old deterministic recovery sentence is replaced
deliberately: an expectation of 60.5 with prospects of fuller recovery is
consistent with the stated delayed write-off branch; a finding of definite
non-recovery earlier would require an earlier write-off. No accounting-source
claim is silently weakened to preserve the old schedule.

Author answers to the bounded reader questions:

1. Opening ECL is 5 because first-year defaults cause later discounted losses;
   no cash need fall due within the first year.
2. With exactly twelve months left, the revised forecast gives both general
   horizons the same ECL of 11. The separate SICR judgment remains required.
3. Subsequent credit-impaired interest is 10% of net amortised cost 55, hence
   5.5; gross accrual and allowance unwind reconcile separately.
4. The assumed no-recovery finding arises at settlement. Article 43 would
   require earlier write-off if that finding arose earlier.
5. The text identifies the 2017 source and its stated 2018 date while leaving
   the issuance schedule, later changes and company adoption evidence open.

These are author checks against the repaired slice. A fresh reader has not
answered the questions, and human comprehension remains pending.

| Ledger | Verdict |
| --- | --- |
| Reader comprehension | The intended distinctions are explicit in the bank sequence; no independent-reader or whole-document readability acceptance |
| Mathematical integrity | Fifty exact quote/PV/journal checks pass; all original example amounts and displays remain; credit judgments are assumed |
| Source fidelity | Dated Chinese provisions, local deductions, unavailable notice and blocked Caiani source remain distinct; no current applicability claim |
| Typography and rendering | Sixteen final pages inspected, including changed/adjacent pages and the full bibliography; final build has no warnings or box errors |

The corrected build environment was material: the first XeLaTeX attempt used a
different engine and introduced warnings in unchanged material. It is preserved
under `build-xetex/`. The sandboxed LuaLaTeX attempt failed only because its font
cache was unwritable; the trusted retry used the existing engine/cache and
succeeded. No package was installed. No independent reviewer or subagent ran.
