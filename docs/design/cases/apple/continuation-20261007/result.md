# Apple filing continuation: source access, interpretation and consequences

The continuation locates 26 of the 70 known exhibit targets, proposes 32
source-bound material assertions across all 23 annual/interim notes, and works
a conditional financing query from retained disclosures. It also corrects an
actual error in the earlier case: Apple's reported cash balance cannot be
labelled as excluding restricted cash. The proposal remains not ready; this is
bounded progress on E01, with supporting E05 and E14 repairs.

## What the source inspection changes

The retained annual PDF contains twelve substantive exhibit bodies missing from
the retained HTML container. Earlier retained reports contain ten other cited
award-plan/form targets. The newly retained 2017 annual PDF supplies two more;
the 2021 indenture and annual power of attorney were already located. These
make 26 located targets. Forty other exhibit rows remain unresolved. The four
remaining rows concern annual/interim XBRL sets and cover-page duplication:
the annual issuer extension archive is now retained, while its ten external
schema imports and transitive dependencies remain open. These statuses account
for all 70 rows without calling the package closed.

The 2017 source is a public AnnualReports mirror, identified by issuer, filing
period and exhibit content. Its current bytes do not establish historical byte
availability. The annual XBRL archive follows the URL in the previously retained
issuer feed. It contains six named XML/schema members. Successful acquisition
does not establish complete taxonomy closure, licence/distribution permission,
correct tagging, Arelle compatibility or accounting validity.

The exact 2013/2018 indentures and 2023 officer-certificate routes were attempted.
Trusted issuer-feed requests returned an HTTP 403 JavaScript challenge; SEC
archive requests returned HTTP 403; the retained EDGAR mirror link first failed
at the HTTP/2 transport layer and the bounded HTTP/1.1 attempts timed out.
Those receipts are retained. A sandbox DNS failure is separately recorded and
was rerun in the trusted context. No challenge, authentication or paywall was
bypassed. Unattempted exhibit targets remain unexpanded, rather than being
called inaccessible because a different URL failed.

The selected assertions retain modality, scope, units, dates, affected model
areas and missing facts. They cover perimeter, calendar and comparatives,
revenue timing and unbilled services, EPS units, cash restrictions, hedges,
PP&E, tax components, leases, debt, discretionary repurchases, qualified RSU
vesting, purchase obligations, contingencies, qualitative supplier exposure and
segment aggregation. Thirty-two is the size of this selected review set, not
the denominator of all material assertions. All 23 notes still have unresolved
semantics and zero translations have human admission.

## Three consequences for a real financing query

At 28 September 2024, the $29,943m cash-and-equivalents balance includes $2.6bn
restricted escrow for the State Aid tax obligation (annual Note 4, printed
p.37; Note 7, p.39). P02's `cash_excluding_restricted` measurement is **wrong
relative to that source**. The supplement provides corrected observation
overrides and an invalidation disposition for unrestricted-liquidity and funding
queries. The 2023 exclusion label is unsupported by the bare caption; this
repair does not infer a 2023 restriction amount from the 2024 footnote.
The displayed subtraction $29,943m − $2,600m = $27,343m is an indicative
remainder, not an exact available-cash determination. It also cannot account
for restrictions or funding conditions not established in the selected facts.

Quarter-end carrying debt is $10,848m + $83,956m = $94,804m, down $1,858m from
$96,662m. The cash flow statement reports $1,009m repayments. The residual
$849m decrease is the amount needed after that cash repayment to reconcile
displayed carrying values. **Its cause is not identified.** It is not established
as an exchange loss, interest expense or a particular posting. The separate
cash bridge checks: $29,935m operating + $9,792m investing − $39,371m financing
= $356m increase; $29,943m + $356m = $30,299m. Correct cash arithmetic does not
identify the missing debt movements.

Exhibit 4.1 reports EUR1,250m of 0.875% Notes and EUR1,000m of 0.000% Notes
outstanding on **18 October 2024**. Scheduled maturities are 24 May and
15 November 2025. Apple's fiscal 2025 ends on 27 September 2025; the November
maturity belongs to **fiscal 2026**. With disclosed faces unchanged and no early
redemption, default or additional-payment branch, the first series has
EUR10.9375m annual coupon and EUR1,260.9375m final scheduled principal/coupon;
the second has EUR1,000m principal and zero stated coupon. These are conditional
scheduled cash amounts, not forecasts of realised payments. Both dates are
Saturdays. Exact settlement needs the governing series/payment provisions and
calendar, and the exhibit expressly qualifies its summary by the 2013/2018
indentures. The retained 2021 indenture is no substitute.

The query exposes dependencies for cash, closing debt, accrued interest, profit,
retained earnings, other comprehensive income and cash flow classification.
Holdings dates, FX, discount/premium amortisation, hedge designations, tax and
classification determine different parts of those statements. The proposed
answer is therefore partially identified: retain the conditional euro schedule
and the unanswered dependencies rather than inventing a dollar forecast or
probabilities over histories. The manuscript keeps its earlier marginal stress
and its explicit exposure/no-tax assumptions separate from these source facts.

## Evidence repair and validation

Three spans in the old E05 candidate record did not support the labels assigned
to them: the purported fixed-debt passage quoted leases, the swap passage a
footer, and the assets passage comprehensive income. The separate
`e05-anchor-repair-v1.json` supplies exact corrected spans. Reinspection preserves
the prior conclusions about compatible exposures, different measurements,
precision and matching assets. Neither these locator errors nor the cash
metadata error constitutes a genuine conflicting disclosure. E05 remains open.

`case-supplement-v1.json` binds the sources, 70 reference dispositions, seven
further package obligations, additional recursive frontier, 32 assertions,
23 note dispositions, corrections and query. `check_case_supplement.py` checks
exact original/extraction hashes and quotes, independent quarterly inline facts,
displayed arithmetic, dates and preserved historical evidence. Its 969 checks
pass. This number measures mechanical assertions, not semantic accuracy.

The new Version 2.2 manuscript is in
`docs/design/proposal/manuscript-case-20261007/`; prior P18 and Version 2.1 files
are preserved. The source restriction, euro terms and call-right pages were
visually inspected. The new argument explains restrictions, reconciliation,
fiscal timing and statement consequences before the prior assumed stress.
Build/render and preservation details are in the continuation evidence folder.

| Decision | Primary criterion status | Veto status | Main uncertainty | Next justified action | What is not concluded |
| --- | --- | --- | --- | --- | --- |
| Accept this bounded supplement as author-checked preparation | Source references, selected meanings and conditional query are reconstructible | No remaining detected source/arithmetic error in the scoped checks; earlier metadata and locator errors have explicit corrections | Unreviewed material assertions and contract/holding facts | Expand actual unresolved targets and contract consequences; continue independent E05/E07/E08/E14 tasks | E01 closure or independent/human acceptance |
| Retain whole-proposal not_ready | Original package/domain/literature/reuse acceptance remains incomplete | Forty exhibit targets and recursive dependencies remain open; wider method blockers persist | Extent of omitted instruments and complete company semantics | Reassess full MC/G obligations after substantive evidence, without restarting the controller | Product implementation, compliance or forecast validity |

Post-run red team: the strongest alternative explanation for the apparent
source-access progress is improved container indexing rather than new economic
knowledge. The counts therefore remain separate from the new cash and calendar
interpretations. The weakest part of the financing evidence is the missing
governing instruments and actual later holdings. A contrary governing provision,
different applicable date, or a source-supported later transaction would require
revising the conditional schedule. None would invalidate the need to preserve
context and unknowns. This is a repairable incomplete candidate, not evidence
against the research direction. No stochastic ranking was conducted.
