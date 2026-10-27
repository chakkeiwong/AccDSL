# R05 — exact-URL historical archive inquiry

23 October 2026. P17/P19; MC04/05/19/25/26/33–35.
Output: `data/accounting-master/r05-archive-leads-20261023/`.

Question: does a distinct public archive route supply a dated capture of the
exact retained Apple or JPMorgan 2025 interim source? The baseline is the
unchanged 192 historical-vintage admissions, all false. The selected URLs and
original hashes come from the completed interim-assets inquiry. No completed
acquisition or extraction is rerun.

Skeptical audit: a report date, current issuer download, archive index row or
redirect alone cannot prove which bytes were available at a historical cutoff.
A replay needs its capture identity, original URL, status, date and byte
comparison. Even a matching capture gives an archive-observation bound under
the archive's clock/provenance assumptions; it does not prove first release or
the latest version at every earlier date. CDX length fields and replay response lengths have separately retained meanings; a digest match is checked independently from PDF completeness. A blocked endpoint is access evidence,
not evidence that no archive exists. These distinctions repair the main risks
before requests are made. No admission will be changed by this inquiry.

Research intent and evidence contract: seek a concrete version lead, not an
empirical forecast result. Query exact URLs in Internet Archive CDX, with a
bounded diagnostic search interval 2025-01-01 through 2026-10-22. That interval
is a search convenience, not a selected forecast cutoff. Request at most 50
rows per query and retain index bodies and headers. If a route is blocked,
one distinct Internet Archive availability-API query may test accessibility.
Follow an exact capture only when one is returned. Maximum five distinct HTTP
requests, each bounded by 35 seconds and 12 MB; no automatic retries. A sandbox
network failure may be retried with the required trusted tool permissions and
is recorded separately. Stop this route after its budget or no usable lead;
continue independent fitting/inference design.

Pass criterion for a version lead: a usable response identifies an exact
original URL and capture timestamp. A stronger byte-match finding requires a
retrieved body matching the frozen original SHA-256, with transport decoding
explicit. Invalid or mismatched bytes veto admission and trigger investigation;
empty/denied responses explain access only. No publication-time, historical
eligibility, forecast accuracy or whole-row completion claim follows.

Defaults and assumptions: two issuers are a small access diagnostic chosen for
different hosts/formats, not a representative archive sample; 50 rows/12 MB/
35 seconds/five requests bound resources and can truncate evidence; archive
metadata is third-party evidence with an explicit trust assumption. Do not
treat CDX digest as a verified original SHA-256. No confidence level or model
parameter is selected.

Execution: preserve ordinary source/request hashes, a concise result and run
manifest, and snapshots of the four current controls. Use curl for retrieval,
standard-library Python for parsing/hashing, and no acquired-code execution or
ML imports. CPU checks use CUDA_VISIBLE_DEVICES=-1. Update current controls
only after the result is concrete. The frozen manuscript, prior artifacts,
Git HEAD/index and unrelated edits remain preserved.
