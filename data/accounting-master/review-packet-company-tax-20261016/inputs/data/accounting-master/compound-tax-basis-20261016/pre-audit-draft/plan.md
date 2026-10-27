# Initial tax base for a compound convertible

16 October 2026. MC02/04/17/19/24/25/30/32/34/35; P17-05.03;
G7/G13/G15. This is a documentary method unit under retained IAS 12.23,
61A and 58; no runtime, installation, empirical campaign or current-law
admission is part of this work.

## Question and repaired baseline

When an issuer allocates convertible proceeds between liability and equity,
what happens at initial recognition if tax law assigns the liability a tax
base equal to the combined proceeds? Compare this exact source-described case
with the separately supplied matching-base case in the Version 3.16 company
join. The target is the tax journal at issue date; later tax-base evolution,
coupon deduction, settlement, P&L reversal and company/EPS consequences are
outside this bounded unit.

The candidate arithmetic is proceeds100, liability92, equity residual8,
tax base100, rate25%. The source says this yields a taxable temporary
difference on the separately recognized equity component; calculate DTL2 and
charge it directly to equity, leaving net equity6. Cash100 then reconciles to
liability92 + DTL2 + equity6. Under the alternative supplied tax base92,
there is no issue-date difference in this narrow calculation and equity remains8.
Do not silently splice the DTL case into CompanyEPSJoin/1: when and how it
reverses affects earnings and requires a separate tax-period reconciliation.

## Evidence contract and plan audit

Primary criterion: exact source-rule classification and journal balance for
both explicitly supplied base cases, independently enumerated before the
reference calculation. A missing tax-base/rate/allocation finding is unresolved;
a contradicting unsupported tax schedule is unsupported; malformed rationals,
negative allocations, excessive component total or nonpositive rate are rejected.
Vetoes: direction contradicts IAS 12.23, the tax effect is booked to current
expense rather than equity at issue, DTL amount is wrong, books fail to balance,
or an issue-date result is presented as a complete subsequent tax schedule.
Schema/build/check counts explain integrity only. No current jurisdiction,
future reversal, accounting compliance or downstream EPS consequence follows.

Assumptions: the tax base100 and tax rate25% are explicit illustrative
jurisdictional premises, not defaults; the total proceeds100 and liability92
come from the inspected historical example; equity8 is the residual; the rate
applies to the8 temporary difference. Failure mode is to infer law from rate or
mistake separate-component accounting for a net liability. The earliest check
is the source paragraph and exact journal identity. This is a deterministic
reference calculation; no random seed or statistical ranking applies.

Pre-mortem: numerical agreement could conceal a reversed difference direction
or an incomplete tax rule. Independently state the IAS12.23 direction before
writing expected values and bound the artifact to the exact historical text.
A calculation that balances can still be wrong if DTL is booked to earnings;
the explicit equity-origin check separates that explanation. The next justified
step is source-supported subsequent-period reversal only after tax deductions,
tax bases and settlement facts are independently specified.

Skeptical audit passes for this narrow issue-date method. It repairs a real
source gap discovered during the company join, states an exact comparator,
provides stop/refusal conditions, and does not promote a tax rate to a legal
default. It cannot close broader tax-origin, jurisdiction or financing rows.

## Execution and result artifact

Author two base cases, expected result and adverse inputs before coding.
Verify the protected IAS12 source hash, then run exact rational CPU-only
checks with `CUDA_VISIBLE_DEVICES=-1`. Retain every attempt and a run manifest
under `data/accounting-master/compound-tax-basis-20261016/`. Update the result
with the actual command, environment, source anchors, wall time, hard vetoes,
next method and explicit nonconclusions. Preserve Version3.16 and its company
join checks; any manuscript integration must create a protected successor.
