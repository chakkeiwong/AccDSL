# HSBC older annual-results group links

12 October 2026. E01/MC01/04/05/30/33–35; G5/G11/G13/G18. Question:
which selected 2018–2023 annual reports are linked within dated results
groups in the second retained official HSBC archive capture, and does its
2023 group/file-name discrepancy change the publication conclusion?
Candidate mechanism: the `page=1&take=100` capture contains older rows
missing from the first capture. Expected failure mode: transferring each
parent group date to the report file or using URL digits as release proof.

Baseline/comparator: the frozen eight-year HSBC annual rows in
`data/financial-report-benchmark/coverage.json`, the first-capture HSBC
result, and the 56/136 selected-date inventory. The second source is the
retained official `page=1&take=100` archive, SHA256
`c4207a0649d2233fd39bce12b803715ec9e70f30fa4b0246e7bbfb7bb9715bb9`.
Use its original source-access record and exact local bytes. No new network
request is required. The two captures are distinct retrospective snapshots;
their duplicated 2024/2025 rows are controls, not new events.

Research/evidence contract: record a **group-to-selected-link** for a year
only if the parent row has a unique annual-results title/date, the child
has a unique exact English annual-report title/year, its input matches a
real hyperlink, and the official absolute URL matches the selected URL.
Source-hash, row ambiguity, year mismatch, duplicate candidate or selected
hash failure veto the link. Parent date, child `data-date`, PDF content date
and URL digits explain chronology but do not establish the report's first
release or exact selected-byte availability. A report-specific dated
announcement and version proof would be separate evidence. Output: a
bounded source ledger, checks, source review and result under
`data/accounting-master/hsbc-older-results-groups-20261012/`.

Skeptical audit: the first capture's absence of 2018–2023 is a pagination
limit, not proof that no older report exists. The second capture may contain
11 annual group headings, including duplicate recent groups and an extra
Chinese-only 2018 row. Compare only the six missing selected annual years;
do not count duplicate groups twice or treat a Chinese-only row as an English
selected source. In 2023, a 21 February group contains a URL starting
`240226`; this visibly challenges file-date promotion but does not prove a
26 February release. Verify the row's children before interpreting it.
The plan has the right comparator, exact stop condition, bounded CPU-only
environment and an artifact that answers only the declared source question.
Even a successful run cannot close G13 or change the frozen 56/136 count.
If all six bind, close the unit and pivot to a different obligation or a
genuinely report-specific dated version source; do not keep re-querying the
same archive. No manuscript revision, runtime, GPU, paid review, outreach,
publication or Git write is planned.
