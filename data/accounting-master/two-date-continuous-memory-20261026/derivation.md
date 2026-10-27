# Exact two-date regions and inherited cash

This is a local derivation under the execution plan's synthetic premises.
It supplies no new imported literature result or accounting-standard claim.

Let I1 and I2 be coupons, each equal to5 in the persistent fixed mode, or each
computed from its date's rate using100 min(0.06,max(0.03,r)) in the persistent
floating mode. The same mode and facility right persist. A floating mode can
have different rates across dates, but cannot turn into fixed debt without an
explicit amendment. No probability measure is supplied.

After a first ordinary payment cash is5.5-I1. After a first draw and fee it is
6.25-I1 and facility debt is1. Before coupon2 the company receives operating
cash R, then repays the first draw. Thus cash before coupon2 is
5.5+R-I1 after pay, and5.25+R-I1 after draw. Paying coupon2 requires their
respective differences from I2 to be nonnegative. In the second case the
facility remains used even after repayment: repayments extinguish debt, not
the contractual one-use restriction. No assumed redraw can fill the gap.

For R=6 after first draw, pay2 is feasible iff I1+I2<=11.25. At I1=I2=6 the
company has5.25 cash and6 payable. A new draw of1 with fee0.25 would exactly
fill the0.75 gap, which explains why losing the used-facility flag reverses the
answer. For R=7 the bound is12.25, while I1+I2<=12; pay2 is therefore feasible
throughout the first-draw region. After first pay, I1<=5.5, so even R=6 gives
cash before pay2 at least6. The example's failure is localized to a previous
draw combined with a sufficiently high total coupon.

A first draw requires the observed trigger I1>5.5 and an available facility.
Coarse information r1>0.04 joins histories requiring opposite first orders.
The refined trigger signal separates them. Conditional on committed facilities
and R=7, the first decision is fixed by the signal; at the second date ordinary
payment always works. An unused facility may also be drawn if I2>5.5, even
though payment is affordable. There are two such reachable observation classes
in this fixture, each allowing pay or draw, hence four feasible policies. No
objective ranks them. Off-path actions are omitted from this policy count.

Each date's coupon and initial signal change at a finite set of rational
thresholds. The eleven point/open rate atoms give121 rectangles or lower-
dimensional products per persistent mode. Later cash-coverage conditions add
diagonal rational half-spaces such as I1+I2<=11.25. On each resulting region,
all balance/journal amounts are affine in(r1,r2). Regions are bounded because
they retain the original rate box. Finite modes and receipt alternatives give
968 initial cells; action and information splits produce2,828 retained outcome
states, including incomplete refusal prefixes.

For bounded nonempty polytope P defined by weak versions of the inequalities,
its vertices generate P. The average of every distinct vertex lies strictly
inside every required strict half-space unless the whole polytope lies on that
half-space's boundary. Indeed each weak inequality is nonpositive at every
vertex. Its average is negative exactly when at least one vertex has negative
slack. Consequently a common average satisfies all strict inequalities iff
all can be satisfied within P. The finite vertex enumeration also covers
bounded lines and singleton intersections by intersecting their active boundary
lines. This argument assumes a bounded, closed two-dimensional half-space
closure; it does not cover unbounded polyhedra or general nonlinear regions.

An affine extremum over P occurs at a vertex. For a strict region, the same
vertex extremum is an infimum/supremum of the closure. Attainment is checked by
intersecting the optimizing affine equality with the original strict region
and retesting feasibility. Empty strict faces are therefore not mistaken for
attained extrema. The diagnostics explicitly test open rectangles, diagonal
cuts, lines, points and impossible strict faces.

Acceptance-domain comparison uses independent closed-form financial
inequalities. Every candidate accepted region must be a subset; subtracting
their union from the expected domain must leave nothing. For each pair of
orders, accepted and refused regions must be disjoint and cover the initial
cell. Amounts agree by affine coefficients, with singleton axes substituted.
Thus these are complete-region statements, not interpolation from sampled
rates. Both comparisons use the same geometry implementation, a remaining
method risk stated in the result.

Interest accrual persists even when an order fails. The returned state contains
all posted cash, income, fee, repayment and interest effects to that point,
alongside outstanding interest payable. A first-date refusal terminates this
selected trace; it is not a modeled default/restructuring process. Alternative
orders can still be explored from the original state. Continuing after default,
source-bound contract revisions and query-budget/resumption semantics require
further specifications and checks.
