# P17-04/P18 continuation: impairment floors and reversal ceilings

14 October 2026. MC02/04/07/11/13–16/19/20/28/30/32–35; E07/G4/G12/G15/G16.
Baseline Version 2.78, 237 pages, SHA256
`7fb6e19ce905f52071239f2c2000ff389db86f2c8f1172b9d7bce723526bae77`.

## Question, evidence and skeptical audit

Complete the residual in X2/Section 9's impairment method: how does allocation
change when an individual asset floor binds, and how does later depreciation
limit reversal? Existing goodwill-first and standalone 80/60/90 examples are
delivered and must be preserved. Compare the new procedure with IAS36.104–108,
114–125 in the retained original EU2023/1803, not with journal balance or a
count of cases. The original PDF's regulation date is corrected by its retained
corrigendum from 13 August to 13 September 2023. This is selected historical
technical support; complete later amendment and target-entity admission are
not established. Use relative measurement dates T0/T1, not an invented current
EU compliance interval. IAS7.20 in the same historical source supports the
noncash operating reconciliation.

Skeptical audit: a low CGU recoverable amount paired with higher individual
disposal values could reflect incoherent valuation inputs. An exhausted-capacity
fixture therefore tests the allocation diagnostic only and is not an admitted
accounting example. Do not manufacture a liability for its residual: 108
requires a separate IFRS basis. Distinguish an input absent from the file from
a supported finding that an individual value is not measurable/determinable.
The latter can affect the standard's conditional floor/ceiling; the former
cannot silently become zero or infinity. A zero proportional-weight sum is
also unresolved, not authority to choose equal weights. This revised scope
passes the audit and preserves those open interpretation/input obligations.

Primary criterion: a reproducible capped proportional allocation, full
goodwill/asset and no-impairment depreciation histories, and complete pretax
journal/statement bridges, with contrary balanced outcomes rejected. Wrong
source/scope, violation of an admitted floor/ceiling, goodwill reversal, an
invented liability or an unreconciled result vetoes the affected method and
triggers repair. Exact fractions, invariants, hashes and compilation provide
calculation/integrity evidence, not valuation validity or runtime conformance.
No stochastic ranking, experiment, numerical-framework or GPU run is involved.

## Facts and default audit

The synthetic company starts T0 with cash 80, two cost-model PPE assets carrying
60/40, allocated acquired goodwill 20, no liabilities and equity 200. Cash is
outside the tested CGU. The CGU boundary and allocation level are assumed
properly admitted under 66–80, with no shared corporate assets, noncontrolling
interest or recognized liability requiring a perimeter adjustment. Both PPE
assets have five years of remaining even use, zero residual and no prior
impairment. Individual VIU is supported as not determinable; admitted individual
fair values less disposal costs are 55/5. The unit's supported recoverable
amount is 70 (assumed VIU70, FVLCD65). These values are measurement inputs, not
results of a new cash-flow/market valuation model.

Loss50 first removes goodwill20. Allocate the remaining30 over weights60/40,
subject to capacities5/35: A takes5 and B25. At T1, one year later, revised
depreciation is11/3, carrying44/12. The hypothetical no-impairment path is48/32.
A supported change in estimated future cash flows raises unit recoverable
amount to90; mere discount unwinding would not qualify under116. Individual
recoverable amounts are supported as not determinable. Thus reversal ceilings
are48/32, allowing4/20. Recognize reversal24, leave goodwill0, and preserve
the unexplained-by-recognition difference between unit90 and carrying80 as
a ceiling restriction, not a missing asset or cash receipt.

| Choice | Provenance/status and reason | Failure mode / early diagnostic |
|---|---|---|
| Cost-model PPE, goodwill, same admitted unit | Synthetic narrow scope; IAS36.2/60/66–80/104 | Invented perimeter or cross-regime OCI; validate membership/scope before arithmetic |
| Exact positive original carrying weights | IAS36.104/122; finite documentary method | Floor-clamped amount silently lost; compare to independently enumerated feasible allocations |
| Historical sources and relative dates | Retained original/corrigendum; current admission unestablished | Later authority silently assumed; source note and case mode are explicit |
| Even use, zero residual, stable useful lives | Authored convenience; isolates impairment memory | Restore old nominal cost after a year; compute both depreciation paths |
| Fair values/VIU and changed-estimate evidence supplied | Authored measurement assumptions; not estimated by checker | Missing values or time passage treated as evidence; adverse admission cases |
| Pretax, no cash movement/other business | Bounded slice; tax remains open under IAS36.64 | Claim a full company/compliant statement; keep tax and complete assembly separate |

## Bounded execution

1. Preserve source pages for scope, unit/measurement consistency, allocation,
   reversal and cash reconciliation plus the corrigendum. Record exact hashes
   and limits. Write method/state/error procedures, including residual and
   zero-basis behavior, before code.
2. Use system Python/Fraction for exact allocation and explicit journals.
   Independently enumerate the two-asset rational/whole-unit fixture solutions
   and verify the proportional-with-caps solution rather than trusting journal
   balance. Check loss50, later depreciation14, reversal24, closing PPE80,
   cash80 and equity160. Preserve complete positive and diagnostic cases.
3. Integrate beside the existing impairment paragraph in a protected successor
   Version2.79. Retain prior mathematics/citations and inspect the affected
   rendering after a clean approved document build. This does not implement
   the runtime accounting package.
4. Record a decision table, alternative explanation, remaining interpretation/
   authority limits, commands/timing and result manifest. Refresh the corporate
   residual matrix and live controls, then audit the next ready unit.

Evidence root:
`data/accounting-master/p17-completion-20261014/P17-04/impairment-floors/`.
Method: `docs/design/proposal/methods/impairment-floors-20261014.md`.
Pre-mortem: an arithmetically successful allocator could accept mutually
inconsistent valuations, restore goodwill or hide missing input behind a
numeric floor. Keep measurement admission separate from arithmetic. Rejection
of one such candidate does not stop independent method work. No continuation
veto is currently present; missing human feedback blocks final acceptance only.
