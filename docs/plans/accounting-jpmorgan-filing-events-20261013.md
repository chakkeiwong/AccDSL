# Bind two retained JPMorgan filing events to their report contexts

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
