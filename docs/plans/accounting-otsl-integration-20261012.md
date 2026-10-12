# Explain token syntax and rectangular-cell validation

12 October 2026. E08/C06, E14/C07, P18; MC23/25/29–35, G8/G9/G10/G18.
Protected baseline: 182-page Version 2.45, SHA256
0604999145379f9a2f1bffba8af039a066f15a20bfe3dd40a0e90a0d2baf4887,
docs/design/proposal/manuscript-tableformer-20261012/accounting-product-proposal.pdf.
Make a separate Version 2.46 only after closing the checked OTSL source inquiry.

Accounting researchers and implementers must understand three different
questions: whether a token sequence satisfies local syntax, whether its merged
cells form a nonoverlapping rectangular partition, and whether it reproduces
the source table correctly. The existing Version 2.45 already separates table
structure, text and financial meaning; it does not explain the geometry needed
between token syntax and conversion. Repair only the local table-conversion
discussion in Section 13.13 and add one version-specific paper reference.

Read the baseline PDF 149–151 first. Preserve a source copy outside the new
candidate. Explain the paper's five token meanings in ordinary prose, then use
the finite two-by-two sequence C L / U C with explicit row endings to show
why equal row lengths and neighbor rules allow an L-shaped merged cell. State
the exact extra requirement: each reconstructed cell occupies a complete
rectangle, cells do not overlap, and every declared slot belongs to a cell.
The source paper's validity/prediction distinction remains explicit. Do not
present an entire replacement grammar or an implemented validator.

Add one concise source-grounded sentence that the retained consumer uses
partial corrections and a first-line counter that remains zero, so its source
does not establish complete syntax enforcement. Keep branch details, AST
checks, benchmark/default and published-version limits in the evidence note.
Do not claim a model actually produced an affected table, change runtime code,
or rank OTSL against HTML. Original arXiv v1 locators must be explicit;
published full-text equivalence is unverified.

Evidence contract: comparator is exact Version 2.45; pass requires a supported
material addition, all old prose/48 displays/92 references preserved, clean
LuaLaTeX/BibTeX build, resolved citations/references, bound source evidence and
readable final pages/transitions/bibliography. Lost content or a misstated rule,
unread condition, bad merge interpretation or false code scope vetoes the
candidate. Counts/build are engineering diagnostics, not readability acceptance.
An author's finite proof demonstrates the specific counterexample only; it
cannot certify parser correctness, completeness or general theorem validity.

Default and skeptical audits: the source is the identified author copy,
arXiv:2305.03393v1; old HTML method and later 4.0.2 are distinct comparators.
Ordinary rectangular rowspan/colspan is the stated exchange target, not a
universal assertion about all table forms. The counterexample checks each rule
and merge meaning and includes valid/invalid controls. Runtime occurrence,
frequency, local performance and independent acceptance stay unevaluated.
The plan passes with those exact boundaries. A failed universal sufficiency
claim triggers this specification repair; it does not reject the method.

Artifacts: data/accounting-master/otsl-integration-20261012 and separate
docs/design/proposal/manuscript-otsl-20261012. Record actual build/check/render
commands, preservation and comprehension/source evidence, result and manifest.
Refresh four live controls, scoped commit, then rotate to another concrete
workstream after reviewing current dependencies. Preserve frozen source units,
all wider E01/E05/E07/E08/E14 obligations and not_ready. No implementation,
installation, GPU/model run, fees, outreach or publication.
