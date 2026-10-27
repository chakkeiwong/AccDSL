# Apple 2018–2025 original 10-K filing events

12 October 2026. E01/MC01/04/05/30/33–35; G5/G11/G13/G18. Question:
which original Apple Form 10-K filing events for fiscal 2018–2025 can be
identified from the already-retained official SEC submissions record, and
how far do those event dates apply to the selected annual reports? The
baseline is the frozen 192-report panel and 56 verified/136 unverified
selected-report date inventory. Seven Apple annual selected reports have
unverified dates; the 2025 selected HTML has an accepted date. The prior
JPMorgan 2018–2025 filing-event work is complete and must not be repeated.

Source: retained `https://data.sec.gov/submissions/CIK0000320193.json`,
captured in the corpus source-access ledger at SHA256
21eae1adf76b91a72eab511c0a96cd56f2053878b8c22df5bfdbfdbb0adfcc42.
Inspect its parallel recent arrays for original 10-K and any 10-K/A rows,
year/period, filing date, acceptance time, accession and primary document.
Check selected PDF/HTML issuer, form and report period against each official
event, and bind selected file hashes from the frozen date inventory. The
comparison is an identity/context check, not a byte-equality proof. Retain
alternate source dates already present in resolved-sources separately.

Evidence contract: each promoted *event* requires unique SEC CIK, form,
report period, accession, filing date and acceptance timestamp; its selected
report must match issuer, form and period on the cover. An ambiguous or
missing row, amendment confusion, cover mismatch or source/hash failure
vetoes that event. Selected-PDF as-of admission requires independent byte
or complete content/version evidence and is **not** the pass criterion here.
PDF/HTTP timestamps, URL digits, row counts and cover similarity are only
explanatory for availability. This unit will not conclude exact public
access time, selected PDF availability on the filing date, whole-package
coverage or forecast readiness. Preserve exact source paths, hashes, selected
relationships, an event ledger, checks, author review and result.

Skeptical audit: a date-only join from resolved-sources would silently move
alternate-version dates to selected files, the exact failure recognized by
the prior publication plan. Use the selected-date inventory and selected
file hashes as the comparator. The SEC JSON is a 2026-captured mutable
index, not immutable proof that its current contents were visible at an
earlier time. CIK and accession identify filing events; an issuer-hosted
CONVPDF may have different bytes or omissions. The cheapest checks are
source hash, eight unique 10-K periods, amendment scan and first-page
cover identity. If these fail, repair or stop the affected rows before
using dates. No network fetch, PDF re-download, corpus-metadata rewrite,
runtime, GPU, paid review, outreach, publication or Git write is planned.

Output: `data/accounting-master/apple-annual-filing-events-20261012/`.
The retained sources and checked event evidence can advance the E01 clock
ledger without changing Version 2.37 or the frozen 56/136 selected-byte
assessment. After this bounded unit, continue independent ready work.
