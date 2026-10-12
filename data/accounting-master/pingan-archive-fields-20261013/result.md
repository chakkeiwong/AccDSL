# Ping An archive links and distinct clocks

13 October 2026. P17; E01/C03; MC01/03/05/28/30/33–35; G13.

Fifteen of the sixteen selected Ping An reports match an attachment URL in the
retained official archive exactly, after prefixing protocol-relative links
with `https:`. Each match agrees with the selected article ID, title, report
year and class. The sixteenth, the 2019 interim ASBE report, uses an IR Asia
mirror. Its URL does not match the archive's same-period attachment; that
article's dates cannot be assigned to the selected mirror. All 123 scoped
source checks pass.

For all fifteen matches, the existing `archive_created_at` field preserves
`createDate`, while the different `creDate` field had not been carried into
that metadata. This supplement preserves both, along with `updateDate` and
the empty `timingOn`/`timingOff` fields. No matched article contains a
`publishDate` field. At response level, `createDate`, `updateDate` and
`publishDate` are present but null. Missing fields, nulls and empty strings
remain distinct; `readTimes` is a counter, not a timestamp.

For the 2025 annual report, article 27925664 says `createDate` =
2026-03-30 14:47:00, `creDate` = 14:47:45 and `updateDate` = 14:47:53.
For the 2023 interim report, article 24413790 says 2023-09-04 14:13:00,
2023-09-04 14:14:50 and 2023-09-06 17:55:49 respectively. Choosing an earlier
field as public availability would therefore change a query with a cutoff
between 4 and 6 September, without any inspected support for that choice.
All strings lack a timezone. The backend field semantics and the moment of
public availability remain unknown.

The retained 2019 basis review distinguishes an excluded IFRS/IAS 34 file
from the accepted ASBE mirror. Its exact source quotations and both hashes
are preserved here as prior evidence, not presented as new page reading.
The archive's same-period title alone cannot establish accounting-basis or
byte equivalence. Two separate issuer-hosted ASBE candidate links already
exist in the retained discovery; their content is the next bounded inquiry.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain fifteen exact attachment bindings and one distinct-source disposition | All sixteen active reports accounted for | Hash, article, URL, year/class and metadata checks pass; mirror substitution withheld | Backend date meaning and historical public availability | Inspect the two retained 2019 issuer-source leads | Fifteen new publication dates or historical-byte admissions |
| Preserve date fields as distinct source assertions | Raw names, values and missing/null states retained | No inferred timezone or publication field | Whether any documented field has public-release meaning | Require explicit issuer field semantics or independent availability evidence before admission | That creation or update happened at the time readers could access the report |

This is engineering and source-provenance evidence. No accounting treatment,
runtime compatibility or statistical comparison was evaluated. The strongest
alternative explanation is that a backend create/update operation coincided
with release; the captured response neither proves nor disproves it. Exact
official field documentation or an independently retained release event could
change the chronological disposition. The weakest evidence for a stronger
claim is the absence of source-defined semantics and timezone.

No publication declaration was added. Version 2.50, the frozen 56 filing
dates / 136 unverified dates, the 35 supplemental declarations and full
`not_ready` status remain. E01/E05/E07/E08/E14 stay open.
