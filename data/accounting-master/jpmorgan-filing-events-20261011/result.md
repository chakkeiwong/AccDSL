# JPMorgan 2021–2025 filing-event supplement

Twenty additional original filing events are identified from official SEC
metadata. With the preceding twelve events, the supplements now identify
**all 32 JPMorgan annual/first-three-quarter filing events for 2018–2025**.
All **154 documentary checks pass**; 1730 prior references verify. Forty new
historical metadata requests succeeded within enforced 2 MiB streaming caps;
the current parent and two historical shards were reused.

Sixteen selected reports have matching issuer/form/period cover evidence. Four
annual reports instead contain explicit omissions from their corresponding
Form 10-K:

| Selected report | Excluded original Form 10-K pages |
| --- | --- |
| 2022 annual | 1–42, 304 |
| 2023 annual | 1–44, 322 |
| 2024 annual | 1–48, 334 |
| 2025 annual | 1–42, 328 |

The exclusion notices and selected source hashes are retained in
`partial-annual-counterparts.json`. These PDFs are useful annual reports, but
they are **wrong as evidence of complete Form 10-K coverage**. This is a new
specific E01/MC01/MC05 gap within the existing G11/G13 obligations. It does not
erase their retained statements/notes or retroactively rewrite frozen source
acceptance. It requires complete filing counterparts and separate availability
records. All twenty selected-byte as-of admissions remain withheld.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain twenty event records | Unique original form/period/accession; official CIK metadata | Identity checks pass; no conflicting duplicate accession | Later updates and selected-byte correspondence | Preserve exact event clocks and source hashes | Whole-PDF publication time |
| Reject complete-filing interpretation for four annual reports | Their explicit Form 10-K exclusion notices | Whole-filing coverage veto fires for those selected files | Content/version relation to exact filed documents | Acquire complete 10-K counterparts from newly inspected issuer feed links | Entire corpus unusable |
| Continue the source repair | Exact `tenkDoc` URLs found for 2022–2025 in retained official issuer feed | No prior attempt at these URLs found in acquisition ledger | Live file access and identity | Bounded acquisition, cover/structure verification, preservation | Repair complete before documents checked |
| Keep V2.26 | No generic manuscript claim says these PDFs are complete filings | PDF unchanged | Independent/human/domain acceptance | Update supporting evidence and live roadmap | Readiness |

`filing-events.json` retains each source response/row, accession, filing and
acceptance clocks, selected PDF/text hashes, relation and admission status.
No duplicate accession or target-period amendment was returned in this inspected
source set; that observation is bounded by the retained responses, not a claim
that later revisions cannot exist. The frozen 56 verified/136 unverified
selected-report date assessment remains intact.

The strongest alternative explanation is a complete Form 10-K elsewhere in the
issuer package, which the retained issuer feed now confirms as an acquisition
lead. That does not make the selected partial annual PDFs complete. The observed
failure is a document-selection/coverage mismatch, not a rejection of the
research direction. The next phase repairs precisely this mismatch; stopping
for generic human review would leave feasible internal work unfinished.

No statistical comparison applies. The 168-page Version 2.26 PDF remains
SHA256 `d7c60268490921ec7edbc964ece351ebcdbd478ce422fa20b59de844e3ab48d7`.
Readiness stays `not_ready`. No installation, OCR/model execution, GPU,
new document extraction, outreach, fees or publication occurred.
