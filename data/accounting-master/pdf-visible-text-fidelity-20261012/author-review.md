# Cover visibility and manuscript review

Author inspection, 12 October 2026. This is not independent or human acceptance.
The source is the selected 450-page HSBC annual PDF, SHA256
`2c03736c288399da08b665d72616e45b93c99764ec47891d9c2bc8fa5175c6c5`.
Its physical cover visibly reads HSBC Holdings plc, Annual Report and Accounts
2023. I inspected `rendered/hsbc-annual-cover.png` at its normal reading size.
PyMuPDF preserves both Accounts 2024 and Accounts 2023. Poppler places a separate
2024 token below the 2023 line; it does not return the same complete phrase.
The candidate wording was corrected to state the shared extra-year finding.

The selected trace contains three spans, including two spans at sequence 8.
The earlier Accounts 2024 glyph bounds are fully inside the later opaque
rectangle at sequence 49. Accounts 2023 is then painted at sequence 50.
These selected records explain the inspected title. They neither identify
author intent nor implement a generally valid PDF visibility classifier.

The existing annotation schema validates unchanged. Its literal retains the
complete PyMuPDF cover output. The visible-year reading stays proposed; the
internally checked annotation rejects the 2024 visible-year interpretation
with a reason. No independent adjudication or actual accepted 2024 reading is
invented. Six query examples state design expectations; no product adapter or
query engine was run.

## Four separate review ledgers

| Ledger | Finding | Evidence and limits |
| --- | --- | --- |
| Reader comprehension | The added case explains why two extractors can agree about characters yet fail to determine the visible report year. It states what stays searchable and what a later correction changes. | Baseline PDF 143–145 inspected before editing; final PDF 143–146 read in order. Author judgment only; human comprehension remains pending. |
| Mathematical integrity | No displayed mathematics, derivation or previous financial example changed. | All 48 displays and all 48 baseline author-source files are preserved except the three declared source edits. No general rendering theorem or parser accuracy claim is made. |
| Source fidelity | The visible title, raw text and local drawing-order explanation have distinct evidence. Report identity does not supply historical availability. | Exact PDF and page, both raw extractions, retained extraction, selected trace/drawing records and same-byte render. All 75 earlier bibliography entries remain; one exact cover source is added. |
| Typography and rendering | The new correction paragraph now starts together at the top of PDF 144. No clipped text, broken citation or serious build warning was found in the inspected slice. | Final PDF 1, 143–147 and 171 inspected at normal resolution; final renders bind SHA256 `f77a019fcfb7af70faadc4a5f98aee31cf969713e0d1e898b7ac6a7a65749815`. The rest of the manuscript is preserved by source comparison, not claimed reread. |

The root surface auditor does not expand included files. It was therefore run
on the adapter section separately, before and after the repair; reference and
display preservation checks cover all author sources. Both bounded audits
reported no repeated-word, placeholder, punctuation-spacing, duplicate-label,
missing-reference or long-sentence candidates. Those diagnostics do not certify
the prose. The final TeX and bibliography logs are clean.

## Reader questions, answered from the final slice

Both years survive extraction because characters painted earlier remain in the
PDF even when later drawing covers them. The inspected render and drawing order
support 2023 as the visible cover year. Rejecting the 2024 interpretation leaves
the PDF and raw occurrence intact. If it had previously been accepted, a new
reading and explicit Supersede decision would require dependent results to be
revalidated while keeping the old frozen view. The visible year still supplies
no historical availability timestamp. These answers appear in the manuscript,
without requiring the operational sidecar to supply missing reasoning.

The transition begins with the preceding XBRL example's lesson that faithful
preservation needs original occurrences. The PDF case adds one burden: text
presence and visible presentation can differ. It explains the drawing sequence
before introducing the existing literal/readings fields, then returns to the
Arelle/Docling interface discussion. No new mathematical prerequisites arise.

Strongest alternative explanation: parser-specific extraction order could
explain differences in token order, but cannot explain away the inspected
opaque overpainting. A different selected PDF or renderer producing a different
visible title would require a new version-specific inquiry. The weakest part
of the evidence is its one-page, author-reviewed scope; no wider accuracy,
independent review, historical publication or accounting-conformance finding
follows. E05 is not closed by covered text.
