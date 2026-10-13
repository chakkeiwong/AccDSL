# Fair-value transition: derivation and source review

13 October 2026. Implements the audited plan in
`docs/plans/accounting-insurance-transition-balances-20261013.md`.
MC08/10/13/16/19/22/28/30/32–35, G4/G6/G7/G15/G16, E07.
The grouping consequence additionally supplies bounded MC11 evidence.

## Source and inspection

Source: `docs/design/research/standards/aasb17.pdf`, SHA256
`153e720cc1eaf7eea47d50463003391ea0433271694dd83a44c54a0e92deaec3`.
Compilation 4, 31 December 2022, prepared 6 April 2023, amendments through
15 December 2022. Its stated period of application is annual periods beginning
1 January 2023 to before 1 July 2026. This historical edition cannot establish
current operative rules or the ASBE treatment of a particular insurer.

Text pages 1, 5, 11–14, 57–58 and 61–62 were inspected. Page 5 states the
AASB/IFRS relationship and tier qualifications; it is not an unconditional
equivalence assertion. PDF and printed page numbers agree for these pages.
The four retained images were visually inspected: page 12 separates future
coverage/CSM from incurred claims; page 14 identifies the loss component as
part of remaining coverage; page 57 preserves the C4 equity rule and C5's
replacement of C4(a); page 61 states C20 and the separate reinsurance rule.
The previous full Appendix C inspection and AASB108/13 source work are retained
in the 12 October units; they are not claimed as newly executed here.

| Anchor | Inspected requirement | Use and boundary |
| --- | --- | --- |
| 32–37, pp. 11–12 | FCF includes cash-flow estimates, discount/financial-risk effects and nonfinancial risk adjustment | Supplied FCF is already measured; no zero-rate or zero-risk-adjustment assumption |
| 38, p. 12 | CSM represents unearned profit for future services | CSM is a liability component, not immediate transition profit |
| 40(a)–(b), p. 12 | Remaining coverage comprises future-service FCF and CSM; incurred-claims FCF is separate | With no incurred claims, the group's liability is FCF plus CSM |
| 47, p. 14 | Onerous-group liability equals FCF, CSM zero | Supports sign interpretation; its ordinary initial-recognition P&L rule is not substituted for transition equity |
| 49–51, p. 14 | Loss component is part of remaining coverage with separate allocation/reversal functions | Track the component within FCF, never add it again |
| C4(b)–(c), C5, p. 57 | Remove incompatible old balances; recognise net difference in equity; C5 replaces C4(a) | Opening equity absorbs the net transition change under the stated simplifications |
| C20, p. 61 | CSM or loss component is the difference between group fair value and FCF at transition | Derive both signs group by group; fair value excludes the AASB13.47 demand-feature rule |
| C20A, p. 61; C21–C24B, p. 62 | Separate reinsurance, grouping, information, OCI and acquisition provisions | Excluded effects are explicit; eligibility and already-admitted grouping are preconditions |

## Local derivation

Assume two distinct correctly identified issued-contract groups, each with
supported fair-value-transition eligibility. All amounts are authored currency
units at one transition date, with positive values denoting liabilities.
Each group contains remaining coverage only. No incurred claims, reinsurance,
acquisition balances, tax, accumulated OCI or other transition adjustments
exist in this illustration. Assets are unchanged; old liabilities are fully
replaced. These are conditional inputs, not reconstructed issuer facts.

Let F be measured future-service FCF, V be the separately measured group fair
value, C be CSM and K the nonnegative loss component. C20, read with 38/40 and
47/49, gives C=max(V−F,0) and K=max(F−V,0). Therefore C−K=V−F and CK=0.
Because the loss component is within the remaining-coverage liability,
L=F+C=max(F,V). K is not an additional liability. At V=F, C=K=0 and L=F=V.
These equations describe the scoped transition calculation, not a general
subsequent-measurement rule or a general formula including incurred claims.

Group A: F=90, V=110, old liability=105, so C=20, K=0 and L=110.
Group B: F=120, V=100, old liability=115, so C=0, K=20 and L=120.
Both liabilities rise by 5. With assets 500, total liabilities rise from 220
to 230 and opening equity falls from 280 to 270. C4(c), retained when C5
replaces C4(a), supports opening equity rather than current-period earnings.

For A: debit old liability 105 and opening equity 5; credit FCF liability 90
and CSM liability 20. For B: debit old liability 115 and opening equity 5;
credit FCF liability 120. Record B's K=20 within that 120; it creates no
additional journal credit. These are illustrative component entries, not
prescribed account names or an executed insurer's journal.

Aggregating the two *already distinct* groups before applying the sign rule
would use F=210 and V=210, erase both CSM and loss component, and yield L=210.
The correct groupwise L is 230. That pooling understates liability by 20 and
overstates equity by 20. This tests calculation order, not whether the groups
could legitimately have been formed differently under C21–C23.

Rejected targets: L=V gives B=100 instead of 120; L=F+C+K gives B=140;
pooling before the sign rule gives total=210 instead of 230. Source support,
separate component tracking, boundary checks and a balanced opening statement
jointly discriminate these errors; a balanced journal alone would not.

## Skeptical author review and teaching plan

The derivation passes the scoped source audit. Its weakest inputs are the
assumed eligibility, admitted groups and separately measured F/V, all openly
conditional. Source support would fail if incurred claims or other excluded
balances entered without a corresponding derivation. Such a discovery would
veto this use, not the wider insurance method. No new empirical or stochastic
comparison is made, and no ranking or accounting-compliance claim follows.

Target reader: a finance/software reader who has reached the existing
transition section and understands liabilities, debits/credits and equity.
The missing inference is how two separately measured inputs become actual
opening balances. Stage it as A's unearned margin, B's embedded loss component,
the group equations, the opening-equity entries, then the pooling error.
Keep the three quantities F/V/CSM active first; introduce the loss component
only when B needs it. A small two-column comparison supports the sign cases.
The existing real Munich Re disclosure follows, exposing which quantities a
real source actually supplies. Preserve all prior equations, citations and
qualifications. Continue under provisional voice; human reconstruction and
domain acceptance remain pending.
