# Acquisition recoverability — inspected rules and local derivation

13 October 2026. Audited plan:
`docs/plans/accounting-insurance-acquisition-recoverability-20261013.md`.
MC08/10/11/13/16/19/22/28/30/32–35; G4/G6/G7/G15/G16; E07/P17/P18.

The retained historical AASB17 compilation is identified by SHA256
`153e720cc1eaf7eea47d50463003391ea0433271694dd83a44c54a0e92deaec3`.
Its period of applicability is annual periods beginning 1 January 2023 to
before 1 July 2026. Read technical text and inspected six source images:
PDF/printed pages 10, 11, 19, 29, 37 and 38. Page 1's edition finding carries
forward prior inspection. Page 27 was an unneeded extracted candidate, not
the definition page, and is excluded from support and inspection counts.

| Anchor | Requirement read | Local implication |
| --- | --- | --- |
| Appendix A, p. 29 | Acquisition costs must be directly attributable to the portfolio; may relate to issued or expected contracts | Not a permission to capitalise arbitrary selling expense |
| 28A–28B, p. 10 | Systematic rational group allocation; qualifying paid costs before group recognition create assets by related group unless 59(a) election | Cost eligibility, allocation and absence of immediate-expense election are preconditions |
| B35A, pp. 37–38 | Direct group costs allocated to that group and groups containing expected renewals; other portfolio costs allocated to groups | Track renewal origin and future group, rather than an undifferentiated pool |
| 28E, p. 10 | Reporting-date impairment test when facts/circumstances indicate impairment | Author impairment indicators explicitly; no automatic quarterly deduction |
| B35D(a), p. 38; 32(a), p. 11 | Asset cannot exceed expected net inflow for related group under FCF measurement provisions | Use supplied net inflows incorporating required measurement, not premium volume or CSM |
| B35D(b)(i)–(ii), p. 38 | Additional renewal shortfall only to extent not already recognised under (a) | Deduct overlapping first-test loss before posting second-test loss |
| 28F, p. 10 | Reverse previous impairment through P&L to extent conditions improve or disappear | No new cash or write-up beyond previously recognised impairment under these facts |
| B35B–B35C, p. 38; 28C–28D, p. 10 | Revisit allocation assumptions; derecognise asset when related costs enter group measurement, proportionally for later additions | No immutable default allocation; no asset left counted again after incorporation |
| 79, p. 19 | Acquisition assets included in related issued-contract portfolio carrying amounts | Subledger asset identity is not automatically a separate statement line |

## Explicit scope and arithmetic

Follow a 60-unit slice of qualifying *paid* acquisition cash flows allocated
to expected renewals from two distinct origination cohorts: 40 to future G1,
20 to future G2. Other acquisition allocations are outside this slice.
Neither future group is recognised yet, impairment indicators exist, and the
59(a) expense election is not used. Each allocation belongs to its own renewal
cohort/group; there is no allocation overlap or transfer between cohorts.
These are authored facts and a supported-allocation precondition, not an
actual insurer's estimate or a derived optimal allocation method.

The future groups include renewals plus other new contracts. Their respective
measured expected net inflows are 35 and 25, of which the relevant renewal
subsets supply 25 and 10. The other-contract contributions are 10 and 15 in
this additive illustration. These inputs are net measures under 32(a),
including required time/risk adjustments, not gross premiums; the already
paid acquisition costs are not included as another future payment.

G1: group test reduces 40 to 35, loss 5. Renewal shortfall relative to original
40 is 40−25=15; 5 already recognised leaves additional 10. Final asset 25,
total impairment 15. G2: group inflow25 exceeds cost20, so group loss0;
renewals10 imply additional loss10. Final asset10. Combined loss25 leaves
assets35. Adding first loss5 to unadjusted renewal losses15+10 would give
loss30 and asset30, overstating impairment by5.

For this no-prior-impairment, disjoint-cohort case, let A_g be original asset,
N_g the whole-group expected net inflow and U_g the relevant renewal inflow.
Then I_g=max(A_g−N_g,0), J_g=max(A_g−U_g−I_g,0), and remaining asset
B_g=A_g−I_g−J_g. This is a local formula under the positive inputs and
specified matching, not a universal allocation formula for overlapping
renewal populations, prior losses, negative capacities or multiple cohorts.

The impairment entries are debit P&L5 / credit G1 asset5, then debit P&L20 /
credit G1 asset10 and G2 asset10. No cash changes; the acquisition cash was
already paid. For an illustrative slice with initial cash100/equity100 and
no liabilities, allocating/paying60 leaves cash40 and acquisition assets60;
impairment leaves cash40+assets35=equity75.

At a later date, assume no group recognition, cash movement, allocation
change or other movement. B35B's allocation review has been performed and
its inputs are unchanged; measurement assumptions have improved. Full-group
net inflows now45/30, relevant renewals35/15 (other contributions still10/15).
Against original allocations40/20, remaining impairment is5/5, total10.
Reverse G1 loss10 and G2 loss5 under28F, leaving assets35/15=50 and slice
equity90 with cash still40. This reverses15 of the prior25; it does not
recognise renewed contracts or premiums early. If later conditions fully
recover with no other changes, reversal is at most the remaining10 and
assets at most original60. Actual incorporation into group measurement
would derecognise the related asset, with the full group entry needing its
other measurement inputs.

## Skeptical author audit and teaching plan

The scoped derivation passes. The comparison target is recoverability of
identified acquisition assets, not an economic forecast or a reinsurance
measurement. Expected inflows, allocation and trigger facts are deliberately
supplied; their derivation remains required for a real case. Disjoint renewal
origins make the deducted overlap unambiguous. An ambiguous overlap would
require allocation evidence before J could be computed; it is not authority
to use this formula anyway. No stochastic experiment or ranking occurs.

Reader: finance/software reader familiar with group measurement, assets and
P&L. Place the section before adoption/transition so ordinary recoverability
does not inherit a transition-equity treatment. Begin with costs paid before
the future contracts exist, explain the group and renewal distinction, then
show G1 and G2 sequentially. Display the local formula after both meanings
are established. The reversal and cash reconciliation earn the persistence
consequence. Keep accounting-source requirements separate from the chosen
input values and local allocation scope. Human understanding/domain acceptance
remain pending; this is provisional internal preparation.
