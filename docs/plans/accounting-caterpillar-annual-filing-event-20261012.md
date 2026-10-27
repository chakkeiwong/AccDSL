# Caterpillar 2024 annual filing event and selected-report boundary

12 October 2026. E01/MC01/04/05/30/33–35; G5/G11/G13/G18. Question:
what does the retained official SEC submission record establish for
Caterpillar's original 2024 Form 10-K event, and what remains unknown about
the selected annual-report PDF? The baseline is the frozen 192-report panel,
the 56 verified/136 unverified selected-date inventory, and the one
unverified Caterpillar annual slot (`caterpillar-2024-annual`). The previous
Apple event unit is complete and is not repeated.

Source: retained `https://data.sec.gov/submissions/CIK0000018230.json`,
captured 2 October 2026 in the corpus access ledger, with source hash
`e6def01c8247684bdcbbfa010ed5c9e621d42177961ada3904629c2f1e455d45`.
Read the original 10-K row for report period 2024-12-31 and preserve CIK,
form, filing date, acceptance timestamp, accession and primary document.
Check the selected annual PDF hash and its embedded Form 10-K cover at PDF
page 11 against Caterpillar Inc., Form 10-K and the same fiscal year. The
selected PDF includes annual-report pages before the Form 10-K; that structure
is a content fact, not evidence that the whole selected PDF was public on the
SEC filing date.

Evidence contract: promote only the filing event when the SEC source identity,
form/period/accession/clocks and selected cover identity all pass. A missing
row, wrong CIK/form/period, amendment confusion, hash mismatch or cover
failure vetoes the event. Do not promote selected-PDF as-of availability from
the filing event, a mirror URL, PDF metadata, page order or a later download.
The result must preserve exact source paths/hashes, the embedded-cover page,
the 56/136 frozen assessment, checks, author review and next frontier. It will
not conclude first public access time, complete-package correspondence or
historical forecast readiness.

Skeptical audit: the obvious baseline error is to treat the annual-report
front matter as part of the filed Form 10-K and therefore date the whole PDF
to 14 February 2025. The selected file is an annualreports mirror; its PDF
hash and printed-page structure must remain separate from the SEC event. The
first cheap diagnostics are source hash, one original SEC 10-K row, selected
hash, page-11 cover identity and absence of a target-year 10-K/A in the
inspected submission arrays. The SEC JSON is a mutable 2026-captured index;
it identifies the event but is not an immutable contemporaneous access proof.
Additional source-context diagnostic: the selected PDF has an annual-report
front section that calls Joseph E. Creed CEO, while the included Form 10-K
signature page is dated 14 February 2025 and calls D. James Umpleby III
CEO. Check both pages and the surrounding form/wrapper boundaries visually.
This is positive evidence that the selected PDF combines differently dated
content layers; it is **not**, without an appointment or publication record,
proof of the wrapper's exact release date or a particular lower bound. The
signed Form 10-K event and the selected PDF's whole-file availability must
remain separate even if all numerical statements agree.
No document fetch, corpus rewrite, runtime, GPU, paid review, outreach,
publication or Git write is in scope.

Output: `data/accounting-master/caterpillar-annual-filing-event-20261012/`.
