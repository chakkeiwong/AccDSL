# Impairment allocation with asset floors and reversal ceilings

14 October 2026. P17-04; historical IAS36 method supplement to X2.
MC02/04/07/11/13–16/19/20/28/30. The protected older examples remain valid
within their assumptions; this method supplies the missing redistribution
and later-depreciation case. It is a documentary specification, not a runtime.

## Source and scope

Use IAS36.2/59–80/104–125 and IAS7.20 in the retained original annex to
EU2023/1803. The retained date corrigendum changes the regulation's date from
13 August to 13 September 2023; it does not alter these paragraphs. The base
publication is 26 September 2023. This is selected historical technical
support, not a complete amendment census or current target-entity admission.
The synthetic T0/T1 case makes no new claim about an actual reporting period.

Supported assets are admitted cost-model PPE and allocated acquired goodwill
in one properly identified unit/group. Scope exclusions in IAS36.2 remain;
do not apply this procedure to inventory, IFRS9 assets or contract assets by
label. Unit identification, goodwill allocation and consistent carrying/value
perimeters follow 66–80. The case assumes no corporate-asset allocation, NCI
or recognized liability that would require other perimeter adjustments.
Paragraph 78 requires a liability included in recoverable value to be reflected
consistently in the comparison; it is not a deduction from just one side.
Revalued-asset profit/OCI routing and tax under 60–64 require their own methods.

## State, values and allocation

Retain unit membership and source judgments, goodwill allocation, each asset's
gross amount, depreciation and impairment allowances, remaining life/residual,
valuation inputs and their status, the no-impairment depreciation path, prior
impairment dates, and later changed-estimate evidence. Keep `missing` separate
from an admitted `not_measurable`/`not_determinable` judgment. A known number
is not supplied by an absence of evidence.

For unit carrying amount B and admitted recoverable amount R, requested loss
is max(B−R,0). Apply it first to goodwill up to its carrying amount (104).
For each other asset with carrying b_i, form source floor f_i as the maximum
of zero, its FVLCD if measurable, and its VIU if determinable (105). If a
required valuation's status is unknown, return `measurement_unresolved`.
An admitted inability to determine individual VIU does not prevent use of a
known individual FVLCD. The reducible amount is max(b_i−f_i,0): a floor above
current cost prevents reduction but does not authorize a write-up.

Allocate the remaining loss pro rata using pre-allocation carrying amounts.
If a proposed share exceeds an asset's reducible amount, assign only that
amount, remove that asset from the active set and redistribute the remainder
among the others. Repeat until the requested allocation is supplied or no
capacity remains. Each strict redistribution removes at least one asset, so
the finite procedure takes at most n saturation passes and one final split.
Use exact fractions in the teaching case; a future quantized profile needs
its own rounding/remainder rule and must not force a balancing plug.

If capacity is exhausted, retain the unallocated amount explicitly. Under108,
only another IFRS can require a liability for a remaining CGU loss. This
allocator returns no liability proposal. A residual also triggers inspection
of measurement consistency, perimeter and separate obligation evidence before
an unconditional posting decision. A numerical capacity-stress fixture is not
proof that its invented valuations describe a coherent accounting situation.

On a qualified reversal, determine the new recoverable amount after a supported
change in estimates (114–116). Passage of time alone is insufficient. Exclude
goodwill (124). Each eligible asset's ceiling is the lower of its recoverable
amount if determinable and its carrying amount had no impairment occurred,
net of intervening depreciation (117/123). Missing assessment is unresolved;
an admitted inability to determine individual recoverable amount leaves the
no-impairment ceiling operative. Apply the same capped allocation to increases,
with positive current carrying amounts as weights (122).

A remaining reversal capacity shortfall is a recognition ceiling, not a liability
or authorization to restore goodwill. Preserve unit value and recognized
carrying amount separately. If an amount remains but every eligible asset has
zero carrying weight, this procedure returns `allocation_basis_unresolved`;
the standard's pro-rata instruction does not itself provide a unique positive
weight vector. Do not invent equal weights. That extension remains open.

## Connected cost-model case

At T0, cash80 lies outside the CGU; within it are A60, B40 and goodwill20.
There are no liabilities; capital/equity is200. Both PPE assets have five
remaining years, even use and zero residual. Individual VIUs are admitted as
not determinable; FVLCD values55/5 establish the floors. The unit has admitted
VIU70 and FVLCD65, so R70 and loss120−70=50. Valuation and scope facts are
authored assumptions, not outputs of the allocation checker.

Goodwill takes20 first. An unconstrained 60:40 split of the remaining30 would
allocate18/12. A can absorb only60−55=5. Its excess13 passes to B, whose final
loss is12+13=25, below its capacity40−5=35. Closing A55/B15/goodwill0 totals70.
Debit impairment loss50; credit goodwill20 and the two asset impairment
allowances5/25. Cash80 plus PPE70 equals equity150. A journal assigning18/12
would balance but leave A42 below its supported floor55.

One full year later at T1, the revised depreciation is55/5=11 and15/5=3.
Debit depreciation14 and credit accumulated depreciation11/3. Carrying amounts
are44/12. Independently, the no-impairment path would have depreciated60/5=12
and40/5=8, leaving48/32. A supported revision to future cash-flow estimates
now establishes unit recoverable amount90; individual recoverable amounts
remain admitted as not determinable. The requested increase is90−56=34, but
only4/20 is permitted by the two ceilings. Reversal24 restores A48/B32,
while goodwill remains zero. Recognized assets total80 although unit value90.

Debit the impairment allowances4/20 and credit reversal gain24. The remaining
allowances are1/5; accumulated depreciation is11/3. Thus original gross100 less
depreciation14 and impairment allowances6 gives PPE80. Erasing the original
allowances30 would produce PPE86, exceeding the depreciated no-impairment
ceiling by6. The remaining allowance balances preserve the different past
depreciation paths; future depreciation of48/4 and32/4 is12/8.

| Pretax statement change/balance | T0 impairment period | T1 following year |
|---|---:|---:|
| Impairment expense | 50 | 0 |
| Depreciation / reversal gain | 0 / 0 | 14 / 24 |
| Profit / OCI | −50 / 0 | 10 / 0 |
| Closing cash / PPE / goodwill | 80 / 70 / 0 | 80 / 80 / 0 |
| Closing liabilities / equity | 0 / 150 | 0 / 160 |
| Operating cash, direct and indirect | 0 | 0 |

The noncash reconciliations are −50+50=0 and10+14−24=0 under historical IAS7.20.
There are no investing, financing or owner movements in these periods. Tax is
uncomputed under the separate IAS12 obligation in36.64; this is a pretax slice.

## Contrary cases and remaining obligations

The exact fixtures check both nonbinding and binding allocations, exhausted
capacity, missing measurements, all-zero reversal weights, the too-large
allowance reversal, an attempted goodwill restoration and passage-of-time-only
reversal. The capacity stress requests50 against capacities5/35, returning
5/35 plus residual10. It deliberately tests a failure disposition; it is not
an admitted CGU measurement and supplies no liability authority.

The strongest competing implementation distributes the original proportional
shares once, clips A and loses the rest. That recognizes only17 of the required
non-goodwill30. Reallocation to B is the distinguishing step. Another restores
all prior allowances or goodwill when the unit's value rises; the depreciated
counterfactual and124 reject it. These facts do not assess a real valuation or
settle the all-zero allocation interpretation. Shared corporate assets, NCI,
restoration and revalued-asset interactions remain named extensions; full company
assembly and general runtime conformance remain open.
