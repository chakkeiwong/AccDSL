# JPMorgan commitment exposure and expected funding

11 October 2026. E01/E07; MC01/02/03/08/10/15/16/21/28/30/33–35,
G4/G5/G7/G11/G15. The question is how a reported bank commitment becomes an
exposure, an allowance input and a possible funding demand without equating
those quantities. The existing banking chapter has a drawn-loan example and
a generic credit-loss formula, but no inspected real commitment population.
Prior result-file searches find no completed JPMorgan commitment source unit.

## Evidence and interpretation contract

Source: the retained complete issuer-hosted 2025 Form 10-K, SHA256
e16cdad03ca84732dbe21b2595c112e975d5a3f27bce9f394828160275bfe79c.
Inspect the lending-related body of Note 28 starting at PDF page 297
(printed 295), and Note 13 starting at PDF page 260 (printed 258), including
the comparative 2024 amounts and every footnote used in a reconciliation.
Read enough adjacent text to define each population; do not silently merge
guarantees, derivatives, unconditionally cancellable card lines, loans and
other commitments. This is issuer policy/reporting evidence, not independent
operative US GAAP or prudential authority.

Primary pass: an exact source ledger with dated amounts/units, full qualifying
spans, demonstrable component sums or bridges, and explicit unresolved draw,
loss and liquidity inputs. Compare only populations stated in the same source
or explicitly reconciled by its footnotes. The candidate for improvement is
the design's treatment of commitments, not the issuer or a forecasting model.

Veto source admission for a wrong hash, unreadable table, ambiguous column
alignment, missing material footnote or unsupported population mapping. Repair
extraction/alignment before using a number. Missing modelling inputs veto a
numerical forecast, not continued source preparation. Pure counts, extraction
success and balanced arithmetic explain preparation progress but do not prove
accounting validity, completeness, legal enforceability or forecast skill.
No stochastic ranking applies. Preserve this result in
data/accounting-master/jpmorgan-commitments-20261011/; preserve Version 2.32
until a separately checked integration is complete.

## Assumptions and skeptical audit

| Choice | Provenance and status | Why use it | Failure mode and early diagnostic |
| --- | --- | --- | --- |
| 2025 filing and its 2024 comparatives | Retained latest annual candidate; convenience scope, not universal default | Same report supplies policies and dated populations | Later changes or regrouping; retain source date and compare explicit headings/footnotes |
| PDF extraction | Existing local PyMuPDF and pdftotext; engineering convenience | Locate exact passages without OCR/install | Columns mix; read rendered pages and use layout extraction |
| Integer millions | Source table units, to be confirmed | Exact documentary sums | Published rounding differs from underlying amounts; preserve source precision, do not infer exact exposures |
| Future draws and losses remain unknown | No fitted model/borrower-level facts | Prevent unsupported conversion of limits into cash flows | Assumed full draw or default implied by absence of inputs; retain conditional obligations separately |

Skeptical audit passes for this bounded source unit. The baseline is the
actual existing bank design; the source is already verified and locally
available. No weak forecast comparator, transferred PD/LGD default, retry
loop or runtime experiment is involved. Before any calculation, verify that
the exact disclosed categories form the claimed total. A successful command
could still mislead through table-column or perimeter confusion; visual
inspection and preserved footnotes are the early checks.

## Execution and next decision

Use CPU-only extraction/check scripts with CUDA_VISIBLE_DEVICES=-1; no ML
framework import, installation, GPU, network or controller run is needed.
Read the note bodies and affected rendered tables, retain a small source
ledger, and run exact arithmetic checks only for disclosed relationships.
Record actual commands, source/candidate hashes, decisions and missing inputs.
If the source supports a materially useful explanation, integrate it into a
new manuscript candidate with exact preservation checks and page reading.
Full readiness and independent/human/domain acceptance remain unchanged.
