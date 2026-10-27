# P19 ASBE source correction in the manuscript

7 October 2026. Direct continuation of the recovered session, addressing MC19,
MC30, MC32 and MC35, with G7/G8 and E07 still open. This finishes the source
repair and the negative readiness work unit; it does not restart the background
campaign or authorize product implementation.

## Reader and bounded change

The readers are accounting researchers and implementers who know carrying
amounts, tax bases and deferred tax but need to distinguish applicable lease and
income-tax rules. They should be able to select the correct adoption schedule,
explain the qualifying temporary-difference test, and reproduce the opening and
comparative adjustments without inferring actual issuer compliance.

The protected baseline is the 123-page P18 proposal at
`docs/design/proposal/manuscript/`. Its PDF SHA256 is
`e60a42dce13f772760d91766f0a0d76cdec2467e29d02042a5a23d8e5639f316`.
Use its existing accepted build evidence; rebuilding that frozen directory would
overwrite protected artifacts. Preserve its source and PDF in an evidence
snapshot before editing the separate candidate at
`docs/design/proposal/manuscript-asbe-20261007/`.

Repair only the ASBE portion of section 9.14, the adjacent source summary,
associated bibliography entries and revision date. Retain existing recognition,
measurement, modification and exemption details, all chapter/specification
inputs, equations, citation keys and stable section identifiers. The old
identifier may retain its historical wording while the visible title changes.
The source/provenance sidecars are the reviewed ASBE supplement and its
`sources-20261007/inspection-v1.json`; preserve those exact reviewed bytes.

## Evidence and skeptical audit

Comparator: the frozen manuscript and the inspected Ministry of Finance texts,
not a source-status summary alone. Pass means the new rendered section removes
stale access claims, states the different 2019/2021 and 2023 schedules and their
conditions, preserves actual-entity limitations, and reproduces the checked
example with usable citations. Compilation and hash checks are engineering
diagnostics; neither certifies source interpretation or human comprehension.

Material defaults come from the already reviewed synthetic P17/P19 lease:
payments 121, rate 10%, two-year depreciation, zero tax bases, tax rate 25% and
sufficient recoverable profit. They are illustrative assumptions, not tax law,
real issuer facts or product defaults. The existing 58-check rational-arithmetic
report is the calculation comparator. No stochastic or performance experiment
is proposed.

The skeptical audit passes with these safeguards. The main risks are conflating
the lease standard's staged entity application with Interpretation 16's tax
date; treating equal carrying amounts as equal temporary differences; importing
the lease election or Interpretation 16 Section III's comparative rule into
Section I; and treating gross recognition as authority for net presentation.
Each must be explicit in the repaired prose. A successful build cannot remove
E07 or the other four substantive readiness blockers. Later amendments, actual
tax law, recoverability, presentation conditions and entity elections remain
unverified. Wrong baseline, source loss, arithmetic mismatch, missing references
or a conflicting writer stop dependent acceptance and trigger repair.

## Reader questions fixed before editing

1. Why can a lease with equal opening carrying amounts still require separate
   deferred-tax balances, and what goes wrong if they are omitted?
2. Which entity groups face the 2019 and 2021 lease dates, and what permits
   earlier application? How does the 2023 tax date differ?
3. Which transaction conditions and recoverability assumption justify the
   deferred-tax calculation, and what does it say about balance-sheet offset?
4. Why does the illustrated opening adjustment increase retained earnings by
   1.25, and what happens during the remaining comparative lease year?
5. Which actual facts and operative sources are still needed before applying
   this treatment to an issuer?

The argument moves from distinct application dates, through lease measurement,
to why the tax rule changes the same lease's gross balances, then to opening
and comparative effects and unresolved issuer facts. This is a bounded repair,
not a rewrite or readability certification of the whole proposal.

## Execution and evidence

Inspect baseline physical pages 68–69 (printed 61–62) and the affected reference
entry; record located deficiencies before editing. Copy only TeX/Bib/spec
inputs to the candidate. Build with the existing LuaLaTeX/latexmk command and a
writable local font cache if needed. Inspect the changed standards pages,
their transition to the next section, the title/contents and added bibliography
entries. Check undefined references, clipping and missing characters, and
compare unchanged chapter inputs and original citation keys against baseline.

Keep the final reviewed P19 readiness JSON and Markdown intact. Record this
integration in a supplement, together with exact source/PDF/build/render hashes,
author comprehension answers, source and calculation checks, and review scope.
An additional bounded tools-disabled Claude review may check the changed prose
against the supplied primary excerpts; it cannot certify human acceptance.

Finally correct P19's stale pending-review result, rerun the unchanged promotion
checker on the final assessment as a new v2 receipt (expected failure at MC01),
verify preserved inputs and saved review receipts, and save a completion record
and run manifest. Update the current requirements supplement, checkpoint and
human-readable next-plan. All evidence lives under
`data/accounting-master/direct-p19-20261007/`; controller history, frozen corpus
requirements/checkpoint and P15–P18 acceptance remain unchanged.
