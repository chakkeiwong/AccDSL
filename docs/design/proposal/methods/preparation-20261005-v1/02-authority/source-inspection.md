# Source inspection and adversarial review, 5 October 2026

The retained P08 baseline records were read before acquisition. They distinguish
successful official FASB amendment access from missing authoritative ASC access,
and official AASB incorporation from universal IFRS authority. This packet keeps
those distinctions. No access challenge was bypassed, account created, fee paid
or professional contacted. File acquisition and text conversion did not touch
the AccDSL worktree.

`source-register.json` pins each used PDF/text pair, exact provision anchors and
every retained discovery/failure file. Source identity and physical PDF pages are
derived from actual form-feed boundaries; a clean hash/locator is only a
mechanical check. Technical interpretation comes from reading the provisions.
The register's short anchors identify passages; full retained text is available
for local inspection with original copyright notices preserved.

## What was read

- AASB 16: cover, IFRS comparison, recognition exemptions 5–8, control 9 and B9–B31,
  recognition/cost 22–27, subsequent measurement 29–38 and modification 40–46.
  The shared equipment facts meet the specified example assumptions; no actual
  contract or IBR market estimate has been supplied. The 2024 cover date differs
  from the URL'sNov 22 amendment label. For-profit Tier 1 relationship is explicit.
- AASB 112: cover/IAS 12 comparison, definitions/tax-base 7–8, current 12,
  taxable-difference 15–17, initial exception 22/22A, deductible 24 and evidence 28–36,
  rate 46–48, no discounting 53, allocation 58/60/61A, offset 71–76 and 98J–98L.
  The single-transaction amendment is effective for periods beginning 2023.
  The sources supplied by packet 1 are copied and pinned locally, not merely
  linked to mutable acquisition paths.
- ASU 2016-02 Section A: authority disclaimer; lease control 842-10-15-3/4;
  classification 25-2/25-3 and 55-2/55-3; modification 25-8 through 25-12;
  lessee recognition 842-20-25-1 through 25-8, initial 30-1 through 30-5,
  finance 35-1 and operating 35-3. Equal liability trajectories do not imply equal
  ROU or expense. 75%/90% is described as one reasonable approach, not a mandate.
- ASU 2020-05:842-10-65-1/65-4 and related summary. Physical page 14 was rendered
  and visually checked because extracted text combines deleted/inserted dates.
  Correct all-other-entity dates are fiscal years after 15 December 2021 and interim
  periods within fiscal years after 15 December 2022. Public business entity date remains
  after 15 December 2018.2024 is later, but this is not a complete adoption/current-text
  verification.
- ASU 2021-09:842-20-30-3 and 842-10-65-6. Physical page 11 was rendered and checked:
  the risk-free election changed from all leases to class of underlying asset.
  Ignoring that amendment would leave a material stale default even though our
  no-election case's PV stays the same. 2024 current Codification remains missing.
- FAS 109:8–11, 16–18, 20–27 and basis 66–67. This is a 1992 historical document
  obtained from the publisher. It is not admissible as current ASC 740 authority.
  Its plain depreciation/enactment analysis prepares a proposed answer while
  actual current provisions remain on the internal source queue. No obsolete
  statutory rates, special exceptions or presentation were transferred.
- ASU 2019-12:740-270-25-5 and 30-11, 65-8 and BC35–39. Physical page 22 was rendered
  and checked for additions/deletions. The prohibition before enactment remains;
  deleted wording cannot be read as part of the resulting rule. This narrowed
  inspection does not establish every tax recognition/measurement rule.
- ASU 2023-09: effective-date/early-adoption paragraphs and disclosure-amendment
  scope. Public-business-entity annual dates after 15 December 2024 and other-entity
  after 15 December 2025 are recorded. It is a forward amendment lead, not evidence that
  the ASC 740 recognition chain is complete or that those disclosure requirements
  apply to our calendar 2024 no-early-adoption example.
- MoF official 2023 tax application case: all five pages. It assumes rent deducted
  on payment, explicit attribution, sufficient future taxable profit and 25%.
  It quotes Interpretation 16 section 1 disapplying the ASBE 18 initial exception
  for equal paired differences and separately recognises DTA/DTL. Its deliberate
  PV rounding 2600098→2600000 is explicit; no exact-annuity claim is imported.
- ASBE 21 Wikisource reproduction: arts 4–8, 14–33 and lessor-classification
  boundary 35. ASBE 18 reproduction: arts 4–25. These are secondary reproductions,
  never promoted to official-current authority. The initial exemption in old
  ASBE 18 alone is incomplete relative to the inspected official MoF 2023 case.

## Retrieval and remaining authority

Official MoF policy index page 12 identified the exact 2018 lease notice; the
official standards index page 1 identified ASBE 18; official site search found the
specific ASBE 21 standard and 2023 tax application case. The standard/notice and
Interpretation 16 pages returned 502, while the tax application PDF succeeded.
Search results were used as leads, not technical authority. Unrelated Bing
results and challenge pages from other general searches are not source support.
The relevant failure bytes remain in the register; a 200 redirect to MoF 404 is
explicitly a failure, not a successful standard download.

Current ASC, official operative ASBE 18/21/Interpretation 16, a complete amendment
census and real tax law remain open. The proposed answer and checked numerical
consequences already identify why those sources matter. This is useful internal
work, not a packet ready to outsource to a professional.

## Review against packet 1

Read the actual `01-accounting/lease-dossier.md`, `tax-dossier.md` and fixtures.
No material contradiction found in the shared two-payment lease, ten-year
equipment life/FV 1000, tax depreciation/rate assumptions, 2025 total tax 140, or
lease DTA/DTL 52.5 then 27.5/26.25. The matrix's US historical operating branch is a
deliberate comparison, not a competing IFRS calculation. Packet 1's L02 subsequent
same-asset extension is additional evidence; this packet does not claim to have
verified an equivalent cross-standard modification lifecycle. Both packets keep
later years as frozen-rule consequences requiring applicability revalidation.

The counterargument most likely to overturn an adopted rule is a missing
operative amendment, actual contract fact, tax deduction attribution or legal
enactment fact. Each remains explicit. Root's integration review is separate
from author arithmetic, source inspection and this cross-packet consistency read.

## Root-review repair of negative controls

The first diagnostic's four negative controls were insufficient: they compared
wrong calculated quantities with correct quantities without submitting defective
records to a validator. The superseded script and report remain under
`inspection/pre-root-review/`. They are not the final validation evidence.

The revised `check-cases.py` saves a literal baseline record and four mutated
copies in `mutation-fixtures.json`. The baseline passes. Every mutation retains
identical input facts, changes only submitted accounting claims, and is evaluated
by a separate function that derives results from the contractual payment stream
or tax deductions and rate. The final baseline remains unchanged.

| Submitted defect | Independently recomputed rejection |
|---|---|
| Copy the AASB expense and ROU path into the US operating branch | First-year operating expense 126 is rejected against 121; ROU 105 against 110; second-year expense 116 against 121. Cash and liability still agree, demonstrating why those alone are insufficient. |
| Report current tax as total 2024 tax expense | Submitted total 75 is rejected against 125, derived from current tax plus the change in deferred tax. |
| Omit equal commencement DTA and DTL because they net to zero | Submitted gross balances zero are each rejected against 52.5, derived from the fixed zero tax bases, rate and recoverability premise. |
| Discount the deferred liability with the lease rate | Submitted DTL 500/11 is rejected against 50, recomputed from remaining taxable reversals and the tax rate. |

All four mutations are rejected on exactly their intended fields, for a total of
200 successful bounded checks. This is a specification validator for these
declared examples only; no product implementation or current-authority claim is
promoted by its success. Date, standard and quantity spacing in the prose was
also repaired without modifying any retained source.
