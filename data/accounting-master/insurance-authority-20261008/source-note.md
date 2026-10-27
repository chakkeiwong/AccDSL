# ASBE 25: short coverage and later claims

8 October 2026. E07/C05 internal source and calculation preparation. The
official text was retrieved successfully through the HTTP link published by
the Ministry's retained index, after HTTPS returned 502. This is an inspected
dated source, not a verified complete current amendment chain.

## Sources and inspection

`sources/asbe25-http.body` is the Ministry of Finance page titled
“企业会计准则第25号——保险合同（财会〔2020〕20号）”, published 24 February 2022.
The document number identifies the 2020 standard; the page date does not
identify when an individual insurer first applied it. SHA256:
`b2777070fc522840594a5388baa0d8d34a51edd11e379c1ea2b0d82de7c9a006`.
`source-extract.json` preserves article and paragraph boundaries alongside the
raw HTML. Chinese whitespace introduced by inline HTML spans is removed;
English interpretations below are local translations, not official English.
The extractor requires headings 1–120 in order. An initial diagnostic missed
the character 零 after article 100; the corrected extractor handles it and
does not split internal article references into new articles.

Inspected the complete extracted provisions for Articles 2–3, 11–31, 50–57,
86, 97, 106–109, 119–120. Articles 106–109 identify transition obligations;
no transition calculation or full reading of Articles 110–118 is claimed.
All 120 headings were extracted, which is not evidence of inspecting all
120 articles. Claims are limited to the located anchors in the supplement.

Comparator: retained `docs/design/research/standards/aasb17.pdf` and `.txt`,
compilation 4, dated 31 December 2022, prepared 6 April 2023 and registered
26 April 2023 as F2023C00382. Its cover applies to annual periods beginning
on or after 1 January 2023 but before 1 July 2026. Inspected recognition
paragraphs 25–27, measurement 32–37, PAA 53–59 and allocation B126–B127.
The comparison concerns these dated provisions, not universal IFRS/ASBE
equivalence or a later AASB compilation.

| Question | ASBE 25 anchor and interpretation | Retained AASB 17 comparator |
| --- | --- | --- |
| Recognition | Article 16: earliest of coverage start, first premium due (or receipt if no due date), or becoming onerous | 25–26 |
| Measurement inputs | Articles 21/23/25/26: expected probability-weighted current cash flows, appropriate financial adjustment and a separately estimated non-financial risk adjustment | 32–37 |
| PAA eligibility | Article 50: reasonable expectation of no material difference in remaining-coverage measurement, subject to variability restriction, or every contract's coverage no more than one year | 53–54 |
| Initial and later remaining coverage | Article 53: received premium with applicable acquisition/other adjustments, then the specified roll-forward including service revenue | 55 |
| Remaining-coverage financing | Article 54: financing adjustment, with an exception when every service portion is within a year of the related premium due date | 56 |
| Onerous remaining coverage | Article 55: excess remaining-coverage fulfilment cash flows produce a loss and liability increase | 57–58 |
| Incurred claims | Article 56: fulfilment cash flows; the option to omit time-value/financial-risk adjustment is conditional on payment/receipt within a year after incurrence | 59(b) |
| Revenue | Article 57: passage of time unless risk release is not predominantly time-based, then expected timing of service expenses; the common uniform-risk case is used here | B126–B127; wording is not asserted identical |
| Disclosure | Articles 86(3)/97: distinguish present value and non-financial risk adjustment for PAA incurred claims; disclose eligibility and financing choices | No additional AASB disclosure comparison claimed |

Three intervals therefore answer three different questions. One-year coverage
does not remove discounting from a two-year outstanding claim. This follows
from applying the separately inspected conditions; it is not a general
statement that all short insurance products qualify for every simplification.

## Conditional accounting consequence

All amounts are illustrative currency units for an isolated group ledger.
Each issued policy has exactly one year of coverage, begins with the same
premium due/receipt date and has no earlier onerous trigger. Assume valid
insurance scope/grouping, premium 120, risk released uniformly over the year,
no acquisition costs, investment component, reinsurance, tax, other expenses
or other movements. Apply the permitted remaining-coverage financing exception.
No facts indicate onerous remaining coverage at inception or at the reporting
date. These are authored assumptions; they do not establish real eligibility.

After half a year, release revenue 60 and retain remaining coverage 60. At that
reporting instant a claim is first incurred; its expected payment is 60.5 exactly
two years later. The amount is an expected value, not a certain settlement.
Use an assumed appropriate flat annual effective discount rate of 10% and an
independently authored current non-financial risk adjustment of 5, stated in
present-value units and not discounted a second time. Neither input is inferred
from an actual insurer or calibrated here. There is no passage of time between
claim incurrence and this measurement, hence no intervening finance accrual.

Claim cash-flow PV is 60.5 / 1.1² = 50; incurred-claim liability is 50 + 5 = 55.
Recognise debit insurance service expense 55 / credit incurred claims 55 under
Article 31. Together with debit cash 120 / credit remaining coverage 120 and
debit remaining coverage 60 / credit insurance revenue 60, the group balances
are cash 120, remaining coverage 60, incurred claims 55 and cumulative result 5.
Assets less liabilities equal that result. This is a mid-coverage consequence,
not a complete insurer forecast or an assumed outcome through settlement.

For the same two-year payment and risk adjustment, omitting discounting gives
65.5, overstates the required liability by 10.5 and understates this result by
10.5. That shortcut is **wrong relative to the stated target** under the
inspected dated rules and assumptions. Omitting the risk adjustment instead
gives 50 and understates the liability by 5. At zero interest the discounting
difference disappears, but the risk adjustment remains. A genuinely shorter
settlement may qualify for the Article 56 option; a different timing assumption
is a different case, not a defence of the two-year shortcut.

## Applicability and source gaps

Article 120 states 1 January 2023. That sentence alone does not resolve all
entity groups' application schedules. The official search identified the
original release explanation and a later implementation notice, but the
following routes returned 502 within the eight-distinct-URL budget:

- 2020 release explanation:
  `http://kjs.mof.gov.cn/gongzuodongtai/202012/t20201223_3636696.htm`.
- 2025 implementation notice:
  `http://kjs.mof.gov.cn/zhengcefabu/202506/t20250612_3965538.htm` and its HTTPS
  version.
- Document-number issuance search on the Ministry service.

Keep the issuance schedule, later amendments/implementation conditions and
actual entity adoption unverified. Do not infer a 2026 or 2027 schedule from
memory, search snippets or a publication date. The successful search preserves
a different official lead, the 2025 explanatory Q&A
`http://kjs.mof.gov.cn/zhengcejiedu/202506/t20250612_3965540.htm`, for a later
bounded unit. The listed 2026 implementation Q&A and presentation changes also
need source-specific inspection before any current-authority claim. These
leads are not technical support for the present calculation.

The full E07 queue still includes operative ASC, ASBE 22 applicability,
prudential rules, actual company/contract facts, broader financing, variable-fee
options/guarantees, transition, acquisition/reinsurance and actuarial evidence.
An access failure blocks the unsupported applicability claim; it does not
invalidate the inspected calculation or stop unrelated internal preparation.

## Manuscript diagnosis before editing

Read baseline PDF pages 86–91 at normal resolution. Page 90/printed 83,
section 12.6 correctly says that a short payment lag is not the eligibility
test, but leaves the three timing conditions and their numerical consequence
implicit. It supplies no direct ASBE 25 comparison or source-date boundary.
The opening of that section can therefore be read as one broad PAA exemption.
Add the three conditions and the group example there, before the separate
reinsurance discussion. Preserve the earlier complete gross/reinsurance and
general-measurement cases, all their calculations and all source qualifications.

The new transition starts from the existing LRC/LIC distinction, asks which
amount the simplification changes, and uses the expected two-year claim to
make discounting necessary. No new stochastic estimator or complex notation
is introduced. The prepared reader should leave able to reproduce 55 and
identify the separate evidence needed for real rates, risk adjustment and
entity applicability. Human comprehension remains pending.
