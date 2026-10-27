# Semantic annotation of omitted JPMorgan filing ranges

11 October 2026. E01/MC01/03/05/28/30/33–35; G5/G11/G13/G18.

## Research question

For each 2022–2025 JPMorgan package, what substantive filing material sits in
the ranges explicitly omitted from the selected shareholder annual report, and
which dependencies or incorporated references remain unresolved? The unit
starts with Item 1/1A and the ending filing sections because those are within
the omitted ranges and determine whether the structural repair has substantive
coverage. It preserves the selected annual report, complete issuer 10-K
candidate and regulator-event roles as separate records.

## Evidence contract

- **Baseline/comparator:** the frozen selected annual PDF and its exact omission
  notice, paired by fiscal year with the retained issuer-linked complete 10-K
  candidate and SEC filing-event metadata.
- **Primary criterion:** every annotated year has a source quote, complete-PDF
  form-feed page position, section label, substantive claim, dependency list,
  and explicit unresolved-reference status for Item 1/1A and the ending filing
  sections (Item 15/signatures where present).
- **Promotion vetoes:** wrong year or issuer; quote cannot be located in the
  retained text; page position is absent or inconsistent; omission range is
  misread; a role or clock is silently substituted; or a claimed dependency is
  presented as resolved without source evidence.
- **Continuation vetoes:** corrupted local text, missing retained source,
  inability to distinguish form-feed position from printed filing page, or an
  artifact that cannot preserve source quotes and uncertainty. A candidate
  failure or unresolved incorporated reference is evidence for repair, not a
  continuation veto.
- **Explanatory diagnostics:** heading/TOC context, repeated page headers,
  printed page labels, section transitions, cross-reference wording and
  differences between selected and complete text. These explain the map but do
  not establish accounting correctness or historical byte equivalence.
- **Not concluded:** semantic completeness of the entire 10-K, regulator-byte
  equality, earliest public availability, accounting compliance, actual
  company/contract/cohort histories, or readiness of the product.
- **Preserving artifact:** a JSON annotation ledger, bounded quote extracts,
  checks, result note, author review, next frontier, and a closeout manifest
  chained to the section-map completion manifest.

## Default and assumption audit

The complete issuer PDFs and extracted text are inherited from the closed
structural section-map unit. Form-feed positions are a retrieval diagnostic,
not printed filing page numbers. Selected-report omission ranges are taken only
from the frozen package ledger. Regex heading matches nominate windows; a human
readable quote and neighboring context are required before an annotation is
accepted. “Incorporated by reference” is recorded as an unresolved dependency
unless the referenced document is present and checked in this unit.

## Skeptical pre-mortem

The run could appear successful while merely finding table-of-contents strings,
duplicated headers or signatures. To detect that, each row must include a
non-TOC quote and a bounded context window. It could also fail because the
issuer mirror uses different pagination or because an ending exhibit is outside
the selected report's omission notice; those are recorded as source-boundary
findings, not silently normalised. A cheap first diagnostic is to inspect the
first substantive Item 1/1A page and the final filing/signature page for every
year before building the ledger.

## Execution boundary

Use only retained local PDFs/text and package metadata. No network, installation,
OCR/model execution, manuscript rebuild, or historical-byte admission. Keep
outputs bounded and preserve all unrelated dirty work. Run the focused checker,
then close out the unit before starting another frontier.

## Resume audit and repair before execution

The existing layout text interleaves the left and right columns. Taking its
first 700 characters would splice unrelated sentences and can omit the words
needed to support a claim. The unexecuted draft builder also uses the wrong
repository root. Neither the draft nor a regex occurrence count is accepted
semantic evidence. Replace it with exact, complete passage selections from
reading-order extraction of these same retained PDFs; record extraction
commands, source hashes, offsets and page mapping. Inspect rendered pages
where column order or footnote markers affect meaning. Distinguish positive
incorporation, website non-incorporation and documents merely mentioned.

The annotation is a first substantive supplement, not a claim that the entire
Item 1 or Item 1A is read or translated. Preserve the full front ranges locally
and state exactly which passages were read. Prioritize entity relationships,
segment changes, parent-versus-subsidiary liquidity, and the legal status of
referenced material because they affect the proposed company representation.
Identify exact unresolved references rather than one generic dependency row.

The new source preparation uses standard CPU tools only:
`CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python
data/accounting-master/accounting-package-semantic-annotation-20261011/prepare_sources.py`.
It verifies 1982 inherited references, retains reading-order text for front
filing pages (2022 3–44; 2023 3–46; 2024 3–50; 2025 3–44) and each signature
page. The early reading-order diagnostic on 2024 PDF page 3 succeeds. The
revised plan passes the skeptical audit for this limited documentary purpose.

The default reading-order extraction still reorders some paragraph blocks:
2023 PDF page 21 splits a holding-company restriction at the column boundary.
A rendered-page check confirms the correct continuation. For the 36 pages
chosen for annotation, extract each column separately at 72 dpi (letter-size
pages: x=0/306, width=306, y=0, height=750), excluding the printed footer.
Retain both column texts and the left-then-right combination with receipts.
Use full-page signature text. This is a source-reading repair, not an OCR or
runtime benchmark. Printed labels still come from the original page footer and
TOC, not from the crop arithmetic alone.
