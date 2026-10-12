# Revalidate JPMorgan sources and compare the shared 2025 text

13 October 2026. P17; E01/C03; MC01/03/05/28/30/33–35; G13.

The retained official SEC submissions response for CIK 0000019617 covers
2 October 2025 through 2 October 2026. It lists a 2025 Form 10-K filed
13 February 2026 and a Q3 2025 Form 10-Q filed 4 November 2025. The selected
corpus has matching report periods but unverified publication metadata.
Question: what exact filing events are evidenced, and how do their identity
and period compare with the retained issuer PDFs?

Use the captured official response
`data/financial-report-benchmark/landing/jpmorgan/988914cd3a4a690176cd9e5a972fbb585c02d44bc74b33ce9d9fd76b90c4753d.json`
and its `source-access.json` receipt, joined to active coverage and selected
source evidence. Read accession, original/amended form, report date, filing
date and acceptance timestamp separately. Inspect the selected annual wrapper
and embedded 10-K context, and the Q3 10-Q cover. Do not turn wrapper copyright,
chairman-letter date, signatures or filename digits into publication evidence.

Pass criterion: one exact SEC event record for each matched form/period, with
issuer/CIK and cover context checked. Duplicate originals, form/period/entity
mismatch, missing response identity or inconsistent timestamps veto that row.
Acceptance time and filing date retain their source labels and timezone.
Regulator event evidence is not selected-PDF unchanged-byte evidence.
Preserve the 56/136 frozen assessment and the 35 separate issuer declarations.

Skeptical audit: recent metadata includes only these two active-panel periods;
the other 2026 entries are outside the 2018–2025 panel. The official response
lists older shard names, but no uninspected shard is evidence. No new network
access is needed for this unit. The annual wrapper can include material added
after filing; the earliest check is cover/contents inspection. A correctly
matched event can therefore still leave selected-file availability unresolved.
The audit passes for this bounded source question; it does not promise all
32 JPMorgan report dates or a new corpus acceptance count.

Evidence: `data/accounting-master/jpmorgan-filing-events-20261013/`.
Record actual commands, source hashes, inspected pages, results and next source
frontier. Check count is engineering evidence only. No runtime campaign,
forecast validity, professional engagement or manuscript increment is implied.

Pre-run context finding: the annual wrapper is abridged, rather than a complete
embedded 10-K. PDF 75 explicitly excludes Form 10-K pages 1–42 and 328, and
PDF 49 has a chairman's letter dated 6 April 2026. Record the missing-page
obligation and do not equate the selected wrapper with the original February
filing. Inspect those two pages and the Q3 cover/signature (PDF 1/207).
The Q3 PDF has 358 pages, including exhibits after its numbered main filing;
do not truncate its source identity to the financial-statement portion.

The retained issuer earnings feed supplies a distinct, exact primary-document
lead: its 2025/4th-quarter `tenkDoc` item is titled “2025 10-K” and links to
`/content/dam/jpmc/jpmorgan-chase-and-co/investor-relations/documents/quarterly-earnings/2025/4th-quarter/corp-10k-2025.pdf`.
After preserving the event rows, acquire that single official URL with a
bounded 60-second request and record response headers, return code, content
type, bytes and hash. The timeout is a convenience ceiling for one source
request, not scientific evidence. Inspect the cover, contents and signature
to assess whether the omitted pages have been acquired. Identity or non-PDF
failure blocks acquisition acceptance; record the failure and continue other
ready preparation. Acquiring the missing source does not complete semantic
reading of all 43 omitted pages or all exhibits. This extension answers the
newly observed package-coverage defect without changing the research target,
frozen corpus or user-authorized internal scope. Audit passes under that limit.

Acquisition returned a 410-page PDF. Its numbered pages are offset by two PDF
pages; inspect PDF 1, 2, 3 and 330 (cover, index, business opening, signature).
The annual wrapper's printed 43–327 corresponds to PDF 75–359; compare that
285-page text-layer sequence to full-10K PDF 45–329. Exact text agreement is an
explanatory identity diagnostic for the shared section only, not proof of
historical file availability, visual equivalence or full semantic acceptance.
Retain differing pages for inspection instead of coercing equality.

## Baseline correction after inspecting the cumulative records

The initial next-action choice was stale. The 11 October
`jpmorgan-filing-events-20261011` result already identifies all 32 filing
events, and `jpmorgan-complete-filings-20261011` already retained all four
2022–2025 full-10K counterparts. The repeated 2025 download has exactly the
same SHA256. Package ledger, section map and a 40-assertion semantic supplement
also exist. Version 2.50 already explains the omitted-page distinction.
Preserve this redundant request and its timing honestly as revalidation; do not
claim a new source acquisition, new event, newly discovered gap or manuscript
repair. The additional bounded result here is the exact 285-page text-layer
comparison, including the single omission-note difference. Verify prior event
equality and prior full-PDF identity before closure. Add these completed units
to the concise master so they cannot become the next action again.
