# Filing-event evidence for JPMorgan 2018–2020

All twelve expected original 10-K/10-Q filings are identified in official SEC
historical submission metadata. Their issuer, form and report period agree with
the retained PDF cover text. **75 source/identity checks pass**, including
preservation of 1638 prior references. Each row retains accession number, primary
document, filing date, acceptance timestamp, metadata response hash, selected
PDF hash and the exact scope of its correspondence.

| Report period | Form | SEC filing date |
| --- | --- | --- |
| 2018-03-31 | 10-Q | 2018-05-02 |
| 2018-06-30 | 10-Q | 2018-08-01 |
| 2018-09-30 | 10-Q | 2018-10-31 |
| 2018-12-31 | 10-K | 2019-02-26 |
| 2019-03-31 | 10-Q | 2019-05-02 |
| 2019-06-30 | 10-Q | 2019-08-06 |
| 2019-09-30 | 10-Q | 2019-11-04 |
| 2019-12-31 | 10-K | 2020-02-25 |
| 2020-03-31 | 10-Q | 2020-05-07 |
| 2020-06-30 | 10-Q | 2020-08-03 |
| 2020-09-30 | 10-Q | 2020-11-02 |
| 2020-12-31 | 10-K | 2021-02-23 |

`filing-events.json` is the detailed supplement. `selected-date-inventory.json`
reconstructs the frozen active corpus assessment: 56 selected reports carry
verified filing-date metadata and 136 do not. The resolved-source ledger has
66 dated slots, but ten involve alternate source versions. Those ten remain
in `dated-alternate-sources.json`, with no automatic date transfer. The twelve
new event rows have no selected-byte as-of admission. The original 56/136
assessment has not been rewritten or retrospectively declared wrong.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain twelve official filing events | Unique original forms/periods/accessions; retained-cover identity checked | Source/identity checks pass | Selected PDF versus filed primary-document content; later amendments | Compare exact versions only when required; continue other filing-event evidence | Selected PDF existed unchanged on filing date |
| Preserve two availability ledgers | Active version metadata and alternate dates inspected | Date-only byte admission remains vetoed | First public access and complete package vintage | Keep filed-event clocks separate from selected bytes | Historical forecast readiness |
| Repair source navigation and size bound | Mutable index range and ineffective initial curl size flag identified | Repairs pass for remaining sources | Future mutable index contents | Refresh parent when needed; stream-cap responses and use actual accessions | Index URL is immutable identity |
| Preserve V2.26 | No generic manuscript gap requiring revision found | PDF hash unchanged | Independent/human/domain acceptance | Continue E01 publication evidence and wider queues | Whole proposal ready |

Fourteen public metadata URLs succeeded: thirteen historical shards and their
refreshed parent. The first probe showed that shard 049's date range had shifted
since the retained parent index. The refreshed parent itself returned 4,642,815
bytes despite the supplied 2 MiB curl option; this cap assumption failed and is
not presented as a successful bound. Its retained bytes fit the subsequently
documented 5 MiB parent allowance. The remaining twelve requests ran with an
enforced 2 MiB streaming cap and all stayed below it. All request bodies,
headers, actual commands and timings remain in this unit.

The API's `filingDate` and `acceptanceDateTime` are retained exactly as returned,
not collapsed to one date. For example, the 2019 Q2 row reports filing date
6 August and acceptance `2019-08-06T02:19:56.000Z`. The interpretation of a
historical public-access cutoff is not established merely by those fields.
No later amendment was found in the retrieved target-period rows, but this
date window cannot exclude amendments outside it.

The strongest alternative explanation for an apparent PDF/date match is a
later reformatted or revised copy with the same cover. Only a content/version
comparison could settle that relationship. The current result establishes
filing events, not exact historical bytes. The initial failures concerned
source navigation and acquisition controls, not the value of the metadata.
Both were repaired; no whole-program continuation veto fired. No stochastic
comparison or ranking applies.

Version 2.26 remains 168 pages, SHA256
`d7c60268490921ec7edbc964ece351ebcdbd478ce422fa20b59de844e3ab48d7`.
Readiness is `not_ready`. No manuscript rebuild, model/package installation,
GPU, new PDF extraction, paid review, outreach or publication occurred.
