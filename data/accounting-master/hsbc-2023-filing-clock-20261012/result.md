# HSBC 2023 Form 20-F filing event and annual-report boundary

12 October 2026. E01/MC01/04/05/30/33–35; G5/G11/G13/G18. Official SEC
submissions identify the original HSBC Holdings plc Form 20-F for the year
ended 31 December 2023. Its filing date is **22 February 2024**, accession
**0001089113-24-000004**, primary document `hsbc-20231231.htm`. The separate
acceptance timestamp is **2024-02-23T01:38:50.000Z**. Preserve both fields
as supplied; their different calendar dates are not a source conflict.
All **22 source, cover and preservation checks pass**.

The inspected recent array contains 1,000 filings dated 7 December 2023
through 6 October 2026. Row 935 is its only original Form 20-F for this
report period. No corresponding Form 20-F/A occurs in those inspected
rows; this is a bounded index finding, not proof that an amendment can
never exist. CIK 1089113 and the legal issuer name were checked explicitly.

The retained official Group archive separately links a **490-page Form
20-F PDF** at source line 8301. That issuer-hosted document's cover says
“As filed with the Securities and Exchange Commission on February 22,
2024,” identifies HSBC Holdings plc, and names the fiscal year ended
December 31, 2023. These agree with the regulator metadata. Its SHA256 is
`ca44e0bf0f4a953e56219f557f8035f34a78952e0291b803cdf65f2bdf93dbc3`.
This is a current issuer-hosted copy; its complete equivalence to the
SEC-filed primary document has not been checked.

The selected annual-report PDF is a **different 450-page file**, SHA256
`2c03736c288399da08b665d72616e45b93c99764ec47891d9c2bc8fa5175c6c5`.
Its inspected cover visibly reads “Annual Report and Accounts 2023.”
Text extraction also exposes “2024,” which is not visible in the inspected
rendering. The raw extraction is retained without silently deleting that
extra year; the cover image supports the visible 2023 identity. This is an
extraction issue, not evidence of an incompatible issuer disclosure.

The archive results-group date of 21 February, SEC filing date of
22 February, UTC acceptance timestamp of 23 February, and annual PDF
filename prefix `240226` describe different evidence. The filename is
not a verified 26 February release date. No inspected source establishes
the selected annual PDF's exact historical byte availability.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain original regulator filing event | Exact issuer, form, period, accession and separate clocks; 22 checks pass | No source identity or event ambiguity | Mutable index and inspection scope | Preserve regulator event and issuer cover separately | Earliest public availability or immutable SEC bytes |
| Withhold selected annual-PDF date | Different file; no version-level correspondence | Historical selected-byte admission remains vetoed | Release/version history of selected annual PDF | Require a genuinely new dated version source | All annual-PDF content was available on filing day |
| Continue another open obligation | Event question answered; no manuscript repair needed | No mission continuation veto | Operative accounting authority and other wider gaps | Pursue a new E07 primary-notice route under its own plan | E01/G13 completion or proposal readiness |

Post-run red team: substantial content could overlap between the annual
report and Form 20-F, but neither common issuer/year nor a cover match
establishes whole-file equivalence. A dated official annual-report release
with version correspondence could change the selected-file verdict. The
weakest evidence remains historical version identity; the checked event
itself is supported. No statistical ranking applies.

The original 174-page Version 2.37, frozen 56 verified/136 unverified date
assessment, and full readiness **not_ready** remain unchanged. Two distinct
official GETs succeeded across this inquiry. No historical shard was needed.
Runtime implementation, the former controller, paid review, outreach and
publication remain held.
