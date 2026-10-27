# Version 2.33: commitment exposure before funding

12 October 2026. E01/E07/P18; MC01/02/03/08/10/15/16/21/28/30/32–35.
Technical designers should be able to distinguish a contractual commitment,
its allowance population, a measurement liability and a possible future cash
draw. The existing bank chapter explains loan origination and a simple
expected-loss calculation. The new real example belongs after that calculation,
before capital and the synthetic bank path, so the accounting distinction is
introduced before the reader encounters its concrete complications.

Protected baseline: 172-page Version 2.32,
docs/design/proposal/manuscript-bidi-dependencies-20261011/accounting-product-proposal.pdf,
SHA256 8dc196a4043f382111d5bddfaf8ec0c75f9297f807ed7555d5621f6eb0703623.
Read the baseline pages around the insertion. Use a separate candidate under
docs/design/proposal/manuscript-jpmorgan-commitments-20261012/ and evidence
under data/accounting-master/accounting-proposal-v233-integration-20261012/.
Preserve all prior candidate and source-unit bytes.

The source unit jpmorgan-commitments-20261011 is closed with 123 source and
25 closeout checks. It preserves 20 selected table rows, 16 exact spans and
50 documentary reconciliations. Notes 13/28 and the Executive Overview
support the population, liability and forward-transaction clocks. They are
issuer evidence; operative ASC and actual contract verification remain open.
The four quantities have different meanings and do not supply an E05 conflict.

Primary pass: a concise source-grounded insertion with exact inherited-prose,
48-display and 74-bibliography preservation; source hashes remain intact,
references resolve and the affected PDF is readable. A four-row table may
help compare the different quantities. No new mathematical derivation is
needed. Page count and clean builds diagnose layout, not comprehension.
Inspect the complete affected bank slice and its adjacent transition; retain
the source/reader/mathematical/typographic ledgers separately.

Veto: treating a commitment as funded, a future-closing estimate as 2025 owned
loans, a carrying value as an allowance, no allowance as no liquidity demand,
an issuer scenario protocol as a universal default, or source policy as
independent legal/accounting authority. Layout or citation failures trigger
bounded repair. Independent human acceptance remains pending; provisional
drafting continues.

Skeptical audit passes. The unit repairs a specific missing distinction in the
existing bank method and uses inspected source tables with all consequential
footnotes. It does not extend the earlier Indenture discussion, choose a weak
forecast comparator or infer probabilities from amounts. Exact arithmetic is
limited to reported-number relationships. The strongest remaining risks are
reader confusion about the four populations and transaction dates; staged
prose, table labels and continuous page reading address those risks.

Build with LuaLaTeX/latexmk and TEXMFVAR/TEXMFCACHE in /tmp. CPU-only
preservation checks intentionally hide GPU. Record the actual build and
verification commands, timings, final hashes and author-reading limits, then
update the four live controls and proceed to the next substantive queue.
