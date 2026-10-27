# F2 — instrument-only reduction with heterogeneous component values

16 October2026. MC02/04/05/11/13/16/17/19/24–28/30/32–35;
G2/G4/G7/G12/G13/G17/G18. Documentary methods only. Evidence:
`data/accounting-master/instrument-reduction-20261016/`.
Baseline: Version3.30, AddedInstrumentLayers/1, RepeatedItemRebalancing/1 and
PartialHedgeDiscontinuation/1. Preserve those finite contracts unchanged.

## Skeptical plan audit and target

The prior partial-discontinuation calculator removes matched homogeneous item
and derivative portions. It is the wrong baseline for an instrument-only
ratio reduction: IFRS9.B6.5.18 leaves the hedged item unchanged. A nominal
percentage of the aggregate derivative value also fails when component values
per unit differ. Rebalancing is a continuation, with ineffectiveness measured
immediately beforehand (B6.5.8), not a fresh designation or an elective reset.

Use separately identified eligible external derivatives, each designated in
full at zero initial cost/value, jointly hedging one unchanged purchase. A
reduction selects a proportion of one entire instrument, not an aggregate
valuation percentage or selected time component. The removed portion remains
owned; its subsequent value changes go to profit underB6.5.16/18. Historical
gains generated while it was designated remain part of the continuing hedge's
cumulative history. There is no stopped purchase population or fabricated
stopped-item reserve in this profile.

Define for component j its whole-instrument value V_j, its designated fraction
w_j, cumulative designated gain G_j and subsequent undesignated gain U_j.
Between observations, add w_j*delta(V_j) to G_j and (1−w_j)*delta(V_j) to U_j.
At a reduction after a same-date complete measurement, change w_j prospectively
and freeze that portion's stop value; G_j,U_j,hedged-item origin,reserve and
profit do not jump. With zero initial cost/value and no intermediate settlement,
sum(V_j)=G+U. For offsetting G,H, reserve R=sign(G)*min(abs(G),abs(H)); cumulative
profit=(G−R)+U. The original item H=q*(initial_price−current_price) is unchanged
by a derivative reduction. The reserve stays associated with that entire item.

This is a local cumulative-history deduction from6.5.11/B6.5.8/16/18, not an
explicit numerical example quoted from the standard. A competing calculation
that deletes the removed component's prior gain causes a historical reset; a
matched split changes the hedged item; neither matches this stated target.
The audit requires the zero-change reduction and historical-gain conservation
tests before any later report. If source or derivation invalidates that target,
stop this dependent method and continue the aligned-option subunit ofF2.

## Evidence contract and hand-derived targets

Two distinct derivatives A,B have nominal quantities60,40, zero initial value
and zero cost. One highly probable100-unit purchase has original price10.
At the pre-reduction observation price11, A=60 and B=80, so G140,H−100,R100,
profit40. Reduce A by30 nominal units: its stopped value is30, not42 (the
aggregate30% shortcut). Remaining designated nominal is30+40=70; the item
quantity remains100. No financial amount changes at the reduction.

At price12, A=120 and B=100. Designated history is140+(1/2)(120−60)+(100−80)=190;
undesignated gain is30. Total derivative carrying value220 equals190+30.
H−200 givesR190 and cumulative profit30. Purchase100units for1200; settle A120
and B100 separately. Opening cash/capital2000 becomes cash1020 and inventory
1010 after the reserve basis transfer190. Final equity2030=capital2000+profit30.

Comparator: remove30 of B's40 units instead. Stopped value60; remaining nominal
still70, but final G205,U15,R200,profit20,inventory1000,cash1020,equity2020.
Identical aggregate nominal ratios therefore do not identify the result.
Also freeze unchanged marks at reduction, no reduction, proportional reductions
of both components, a lower item-price gain, a signed reversal, and derivative
asset/liability presentation. Negative reserve requires explicit recoverability.
Every final cash amount preserves supplier payment and each derivative settlement.

Primary pass criteria: independently authored reports, per-component histories,
unchanged item and no rebalancing jump, lower-of reserve, complete gross cash,
basis and equity reconciliation, and atomic adverse refusal. Veto missing marks,
unidentified reductions, false qualification/documentation, changed sources,
historical resets, elective outcome management, missing settlement and funding.
Counts and build success are explanatory only. No actual hedge designation,
valuation model, operative-law, tax, cash-flow activity classification or company
composition is established. Independent/domain/human acceptance remains pending.

## Default audit, environment and continuation

| Choice/provenance | Justification | Failure mode / early check | Status |
|---|---|---|---|
| Distinct60/40 nominal instruments, synthetic marks | Exposes unequal per-unit values | Aggregate scalar allocation; equal-remaining-nominal counterexample | Example hypothesis |
| Zero initial cost/value | Isolates reduction from already-delivered acquisition accounting | Confusing carrying value with gain; explicit origin finding | Finite scope |
| Designated-tenure accumulation, source/local deduction | Preserves prior measurement and stops only future contribution | Prior gain erased or instantaneous reserve manufactured; zero-change test | Reviewed local derivation |
| One unchanged purchase and common price risk | Identifies reserve attachment | Matched item shrink incorrectly reused; reject changed quantity/origin | Explicit finite scope |
| All qualifying facts and full marks supplied | No silent inferred effectiveness/valuation | Convenient true defaults; unknown/false findings refuse | Conditional input |
| Exact fractions, existing CPU Python | No numerical solver needed | Encoding/sign error; rational/journal/conservation checks | Engineering choice |

Freeze this plan, source reading and hand-derived targets before implementing.
Run `CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/instrument-reduction-20261016/verify.py`.
Preserve numbered attempts and manifests. Integrate asVersion3.31 after the
existing instrument-addition discussion, protecting130 Version3.30 sources.
Inspect actual pages, preserve the full obligation ledger and refresh controls.
Then audit actual-versus-aligned option time value underB6.5.32–33; that named
F2 obligation is not covered by this non-option method. Continue B1 afterward.
No global continuation veto has fired.
