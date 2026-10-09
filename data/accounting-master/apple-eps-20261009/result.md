# Apple earnings per share and ownership: bounded result

9 October 2026. E01/C03/C08 complete within the declared scope. Version 2.11
is a separate **144-page candidate** at
`docs/design/proposal/manuscript-eps-20261009/accounting-product-proposal.pdf`.
PDF SHA256: `63c48da717cf41e0ee0c2efc7a9a2cff9addc5101e8e36ff02c6d38003766ecb`.
Full proposal readiness remains **not_ready**; implementation and the historical
controller remain held. The requested prior checkpoint commit is
`47afa90f1024aa9a5875b990c5d668048ef7f557`; the earlier closed tax unit correctly
retains its older run-time commit.

## What the evidence establishes

Six full notes were read: annual 3/10/11 and interim 3/7/8. Their sixteen material
units, fifteen explicit dependencies, 89 note-table numeric cells and ten queries
are retained in `source-claim-supplement.json`. Dependencies include both
purchase-interval tables and programme footnotes, equity/cash/balance/operating
statements, calendar and capital-return passages, and annual Note 1's explicit
straight-line compensation policy. Supporting statements are only formalised
for the declared rows; this is not full filing semantics.

All **167 source/arithmetic checks and 32 candidate/preservation checks pass**.
Five basic/diluted share bridges and ten EPS ratios reproduce the reported
figures under explicit scales and conditional rounding. In fiscal 2024,
93,736 million dollars × 1,000 / 15,343,783 thousand shares gives 6.109054
dollars per share, compatible with reported 6.11. Replacing that denominator
with closing shares gives about 6.201 and is wrong relative to the stated basic
EPS target. The calculation checks displayed quantities, not the issuer's
undisclosed exact numerator or full diluted-EPS methodology.

The annual quantity bridge closes at 15,116,786 thousand shares. The next
quarter's Item 2 table narrows repurchases from the note's rounded 100 million
to 99,790 thousand. Opening/closing shares then imply 23,735 thousand net other
increases at displayed centres. Their components and dates remain unidentified;
this is not a claim that all are RSUs or that rounded centres are exact facts.

Two conditional fiscal-2024 histories fit opening/closing shares, annual issuance
and repurchases, the annual basic weighted average, the comparative first-quarter
basic weighted average, and all three fourth-quarter purchase quantities.
They differ by 66,097,000 shares after 100 elapsed days. Formula and independent
daily sums agree exactly. The first-quarter average is 15,509,763,000 shares;
the annual average is 15,343,783,000. This proves non-uniqueness in the stated
integer-share, 364-day, displayed-centre model. It does not reconstruct Apple's
actual dates, trading prices, journals or all admissible histories.

RSU quantity bridges close at 163,326 thousand annually and 186,756 thousand
in the following quarter. Gross vesting, net common-share issuance and
incremental diluted shares remain different targets. All three annual RSU
bridges and the quarter are checked. Grant-date prices, vesting-date values,
expense, equity compensation and unrecognised cost keep their own measures.
The FY2023 antidilution exclusion and generally four-year vesting statements
are not promoted to rules for every period or award.

| Displayed amounts, USD millions | Fiscal 2024 | Fiscal 2025 Q1 |
| --- | ---: | ---: |
| Repurchase equity reduction | 95,846 | 23,476 |
| Cash-flow repurchases | 94,949 | 23,606 |
| Difference: equity reduction less cash | 897 | −130 |
| Employee-withholding equity reduction | 5,605 | 2,993 |
| Cash-flow employee-tax payments | 5,441 | 2,921 |
| Difference: equity reduction less cash | 164 | 72 |
| Equity compensation less compensation expense | 346 | 97 |

All monetary equity components and total equity reconcile for the five reported
periods. The differences above are not assigned to excise tax, fees, unsettled
trades or another invented cause. The straight-line expense policy does not
make aggregate unrecognised cost divided by a weighted period an identified
future expense schedule. Actual cohorts and recognition periods remain needed.

## Decision and limits

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Integrate the bounded EPS argument | Source context, ratios, movements and two quantity histories checked | Final source/numerical/preservation checks pass | Actual event identities, award terms and prices | Preserve result; move to full bounded debt-note reading | Whole-package completeness, operative ASC implementation or acceptance |
| Reject closing-share EPS shortcut | Its ratio differs from reported weighted-denominator EPS | Wrong target supported directly | Exact unrounded issuer amounts | Keep separate dated and weighted measures | A filing error |
| Reject initial annual-only schedules | They omit reported fourth-quarter purchases | Disclosure compatibility veto; repaired | Additional facts may reject later witnesses | Retain refined alternatives and source dependencies | Rejection of the whole research direction |
| Retain two refined quantity witnesses | Both satisfy declared quantity constraints | No mathematical veto in stated model | Prices, award/settlement terms and further filings | Obtain facts before treating them as full histories | Exhaustion, actual chronology or probability ranking |
| Keep cash/equity/expense differences unallocated | Targets are explicitly distinct | Unsupported causal allocation barred | Settlement and classification detail | Preserve exact question and missing facts | Cause from a residual alone |

This deterministic documentary unit has no stochastic ranking, seed comparison
or default-policy promotion. Source checks and a clean PDF build cannot certify
accounting compliance, an implemented engine or empirical forecasting validity.

## Integration, repairs and preservation

The manuscript adds two subsections inside Chapter 10's equity discussion and
one timing equation. All 41 earlier displays, all 66 bibliography entries and
the prior source text survive. Final pages 82–87 were read at full size; pages
1–7 were inspected for navigation on a contact sheet. Original annual pages
22, 32, 34–37, 39, 47–48 and five labelled derived interim pages were inspected.
`author-review.md` records the four separate comprehension, mathematics, source
and rendering judgments; independent reader and human acceptance remain pending.
The surface audit found no missing references, repeated words or placeholders;
the section anchor is intentionally retained for future cross-reference use.

Repairs were substantive as well as presentational. Initial screened witnesses
failed fourth-quarter quantity constraints; the revised examples also include
the first-quarter comparative. One source check first failed because two PDF
extractors permute a multi-column RSU header. The repair permits only that exact
header token permutation; all surrounding text and numeric rows are checked.
Original-page inspection restored the initially missed Note 1 policy dependency.
The initial derived purchase table clipped labels, and its first reflow shifted
columns; the final view preserves every nonempty cell in the correct column.

Four build attempts are recorded: sandbox font-cache failure; trusted failure
from an omitted grammar listing in the candidate copy; successful build after
restoring that unchanged listing; and a final successful build after the policy
clarification. Final LaTeX and bibliography logs are clean. Failed/superseded
artifacts are preserved; no earlier closed-unit generator was rerun.

125 immediate baseline files and 128 preceding-manifest references are checked,
along with 1,266 protected historical files, 518 upstream references and six
controller records. Four pre-V2.11 live pointers are retained in
`pointers-before/`. P19's historical pointer resolutions remain unchanged.
No network acquisition, installation, GPU work, outreach, fee or publication.

The strongest alternative explanation to any apparent reconstruction success
is that aggregate matches conceal incompatible actual dates or monetary terms.
New source constraints could reject a witness and trigger refinement. The
result rejects specific shortcuts, not the research direction. The weakest
evidence remains actual event/cohort identity, explicitly left unresolved.

## Next bounded question

Plan and audit the complete retained annual Note 9 and interim Note 6 debt
reading, with commercial-paper, term-debt, maturity, carrying-value, cash-flow,
currency and hedge dependencies. Earlier selected debt arithmetic remains
checked; do not repeat it as if it were new or treat it as complete note coverage.
The new question is which principal, carrying-value, maturity and settlement
constraints those complete notes supply, and which actual instrument/FX/hedge
facts remain missing. Maintain all five E workstreams, forty exhibit targets,
136 unverified publication dates and every MC01–MC35/G1–G18 obligation.
