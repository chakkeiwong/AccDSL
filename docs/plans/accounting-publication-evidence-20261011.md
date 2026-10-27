# Historical filing-event and selected-byte availability evidence

11 October 2026. E01/MC01/04/05/30/33–35; G5/G11/G13/G18. Question: which
actual filing events can be identified for the corpus without claiming that
later downloaded or reformatted report bytes existed at the same time?
Baseline: frozen 192-slot coverage, selected acquisition records (56 verified
filing dates, 136 unverified), resolved-source metadata and Version 2.26.

Skeptical audit found a material baseline trap: the resolved-source ledger has
66 dated report slots, but ten dates identify alternate source versions. A
date-only join would wrongly promote those dates into selected-byte availability.
Keep two separate fields: official filing-event date/identity, and selected
report's historical byte/coverage correspondence. Supplement only; do not
rewrite frozen corpus metadata or historical acceptance counts.

Primary criterion: official retained/new metadata with exact CIK, form,
report period, accession, primary document and filing/acceptance clocks, plus
explicit relationship to each selected report. Duplicate original/amended
filings must remain visible; do not select by nearest date alone. A missing
identity or clock distinction vetoes date promotion. Missing byte equivalence
vetoes as-of admission of selected bytes, not filing-event identification.
Corrupted sources or prior manifests are continuation vetoes for that claim.
HTTP/PDF dates, URL digits and counts are explanatory only. No whole-report
historical completeness, exact intraday access time or forecasting readiness.

Concrete new route: the retained official JPMorgan SEC submissions index
`988914cd3a4a690176cd9e5a972fbb585c02d44bc74b33ce9d9fd76b90c4753d.json`
lists thirteen historical index files overlapping 2018–March 2021. No matching
filename appears in prior index plans, acquisition results or source-access
record. Inspect those metadata files for 2018–2020 10-K and first-three-quarter
10-Q events. These are different data.sec.gov routes from failed SEC Archives
document downloads. No archive retry is authorised by this premise.

Budget: thirteen metadata requests, <=2 MiB and 45 seconds each. The size cap
is a convenience allowance for roughly 2,000-row SEC indices, not a quality
criterion. Fetch one first; continue only after schema, identity context and
date range prove useful. No documents, installations, extraction, GPU or model
work. Use the existing CPU Python and trusted public-source permissions where
required. Retain all responses, request timings and any failures. A failed
unchanged URL is not retried. Save results at
`data/accounting-master/publication-evidence-20261011/`.

Verify all 1638 inherited references and preserve four live controls. Inventory
the actual selected metadata from the last retained-version record, not fields
absent from coverage.json. Inspect report identity in already retained text;
declare uncertain links rather than invent equality. Document source/byte clocks,
run focused checks, update the live supplement and continue feasible work.

Probe repair before further acquisition: the first historical index returned
valid 10-Q metadata but its live range (4 March–27 June 2019) differs from the
retained parent range (4 December 2018–27 March 2019). SEC shard filenames are
mutable; the retained index cannot delimit live coverage. Refresh the official
parent, preserve both versions, and select live ranges before continuing.
Increase the convenience budget to sixteen metadata URLs to cover the probe,
new parent and up to fourteen current historical files. This is the same
question and public-source cost class; no runtime work or scope promotion.
The changed range is a harness repair trigger, not a rejection of filing-event
metadata. Validate actual response ranges and preserve ambiguity explicitly.

The refreshed parent returned 4,642,815 bytes although curl received a 2 MiB
max-filesize option. This local curl/response combination did not enforce a
streaming body limit. Preserve the response and failed cap assumption; no
redownload is needed. Give the known parent a measured 5 MiB allowance and
enforce a 2 MiB streamed-body cap for each remaining historical shard. The live
parent selects 13 shards (one already acquired), so 15 total URLs suffice.
Parent range endpoints are navigation metadata rather than immutable contents:
the acquired 049 includes 27 June while the refreshed parent lists 26 June.
Match exact filing records and assess target coverage directly.
