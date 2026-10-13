# Connect Apple's complete annual statement tables

13 October 2026. P17/E01/P18; MC01–05/07–11/13/15–16/18/28/30/32–35;
G1/G4/G5/G11/G12/G15/G16. Baseline Version 2.59. Runtime remains held.

Question: which consolidated FY2024 statement balances and period movements
can be reconciled together, and which actual transaction links remain unknown
after the completed note investigations? This is the next concrete increment
toward the real package-to-path requirement, not a new completeness definition.

Comparator: the retained Apple FY2024 annual PDF and the existing Apple case,
asset, tax, liquidity, debt and equity results. Source PDF:
`docs/design/cases/apple/annual-2024.pdf`, SHA256
`ec74758cd767465362c641cf2fd5d8fedd477aed2bf7f62117e67610435dcb88`.
Verify the exact digest against the retained source and manifest before capture.
Inspect printed29–33 (PDF32–36): operations, comprehensive income, balance
sheet, equity and cash flows. The FY2023 balance-sheet endpoint is the opening
comparison; historical multiyear columns must not be conflated with FY2024.

Skeptical audit: a catalogue of existing note examples is not a joined
statement case. Conversely, redoing their completed extraction is wasteful.
Capture the complete selected statement rows and reuse the checked note
results by hash. Cash-flow adjustments can differ from changes in balance
sheet accounts; cash repurchases differ from equity reductions; broad D&A
differs from PP&E depreciation. Preserve every unexplained difference.
Never infer cash collections, purchases, OCI attribution, tax settlement or
unrecorded balancing journals solely to fit totals. A complete statement
table is not a complete acquired package or identified transaction history.
This audit passes as a bounded source-and-reconciliation work unit.

Evidence contract: every row of the five selected FY2024 statements receives
an exact source location, literal, scale, period and reported-versus-derived
status. Keep all BS endpoints, all equity-component movements and the period
income/comprehensive/CF rows; preserve source dashes rather than claiming
reported zero. Check subtotals, balance identities, income-to-equity, OCI-to-
equity, cash-to-CF and the complete indirect cash bridge at displayed precision.
Link the existing note residuals to affected rows and retain unresolved
source-to-journal edges. Column/date/sign/scope mismatch or invented residual
cause vetoes the affected relation. A failed equation triggers inspection of
source and model scope, not a plug. Successful arithmetic is engineering
consistency evidence, not a valuation, compliance or forecast test.

Default audit: use the reported consolidated USD millions for fiscal dates
30 September2023 and28 September2024. Do not assume calendar years, exact
unrounded amounts or free use of restricted cash. Do not merge share counts,
per-share amounts and monetary equity. Add no stochastic weights or future
assumptions in this historical unit. Actual transaction allocations, material
notes/external references and historical byte availability remain separate.

Artifacts: `data/accounting-master/apple-statement-network-20261013/`, with
protected baseline, source pages/renders, typed row readings, relationship
ledger, exact calculation checks, unresolved edges and result/manifest.
Integrate consequential explanation as a separate Version2.60, preserving
prior math/citations, build and inspect. Refresh live controls and commit
explicit paths. Subsequent real-case work must address joint historical
alternatives and conditional paths; do not declare that broader task closed.
