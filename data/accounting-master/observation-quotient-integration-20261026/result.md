# Finite state aggregation integrated into Version 5.5

26 October 2026. MC08/09/10/11/12/14/18/24/25/30/33/34; S2/S4/S5.
Version 5.5 is a 719-page governing design candidate, not_ready. The matching
standalone simulation volume is 171 pages, including 155 body pages and the same
26 chapters. Section 8.9 explains finite observation-preserving aggregation.

Main PDF: docs/design/proposal/manuscript-observation-quotient-20261026/accounting-product-proposal.pdf
SHA256: 7ace3886763d77dc068340a38fc7e8f1167617b2206516d7fcfe1101b8e842ce.
Standalone PDF: docs/design/proposal/manuscript-observation-quotient-20261026/simulation-foundations.pdf
SHA256: 1a39bd1e7e1e3c7e36d914cf324660d135808bb5fe4c21982bdc324791b4ef43.

All 215 predecessor source files are protected. Only the two cover versions
and one compression scope sentence plus an input insertion change; the new
section is separate. All inherited mathematics, citations and examples remain,
and 25 other simulation chapters are byte-identical. Both PDFs built on their
first attempt. Two auxiliary-label parser failures in verification were repaired
without changing either PDF; verification-repair.md records them. References,
page bounds and source preservation pass. No new warning appears. The main
document retains five underfull warnings; standalone has none.

The finite engineering result is ../observation-quotient-20261026/result.md:
12 accepted complete-path comparisons, 8 rejected partitions, 2 explicit false
merge path comparisons, 38 boundary controls and 166 assertions. The result
preserves exact supplied probabilities or unweighted possibilities, initial
information and persistent type. Counts do not establish general correctness
or whole-company state sufficiency.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Advance main and standalone candidates | Finite checking behavior accurately explained with exact declared source delta | No removed mathematics/source, new warning or unsupported empirical claim | Independent and whole-document acceptance pending | Refresh ten controls and four stable links | Finished simulator or financial DSL |
| Continue language design | Full event intent currently delegates specialization to a named native Python owner | No unsupported general portability claim | Exact split between portable method body and event-dependent construction | Audit native specialization, existing authored mechanisms and minimum declarative requirements | New accounting rule or generic callback registry |

Strongest alternative explanation: the exact finite tests preserve a supplied
model that omits an economically persistent variable. That limitation remains
explicit. A changed probability, lost initial information or unrecorded source
delta would overturn this integration. No whole requirement closes. All 53
obligations, six interactions and 46 operations remain; S1–S5 partial, S6 held,
E3 deferred.
