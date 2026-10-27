# Why the comparison covers the continuous domain

This is a local derivation for the supplied fixture, not an imported theorem.
The baseline coupon and guards are specified in the reviewed plan and in
Version5.19, simulation chapter17. Broader compression/literature conclusions
retain the separate source boundaries in literature-closure-20261026.

For floating debt, interest is3 for r<=0.03,100r for0.03<r<0.06 and6 for
r>=0.06. Fixed interest is5. The rate domain is[0.02,0.08]. The coarse signal
splits at0.04; the liquidity/optional trigger splits at0.055. Pay is feasible
when5.5-I>=0. Draw requires an available facility,I>5.5, and6.25-I>=0.
Since I<=6, the last inequality holds throughout an eligible draw region.
The candidate must find roots only inside the applicable affine piece.

The independent oracle partitions at the six points0.02,0.03,0.04,0.055,0.06,
0.08 and the five open intervals between them. These eleven cells are disjoint
and cover the closed domain. On each cell every guard is constant and every
financial amount is affine. Fixed-mode partitions can be coarser; comparison
uses a common refinement. Each oracle cell is verified to belong to exactly
one candidate cell, in its entirety. On open cells all affine coefficients
match; on singletons their evaluated constants match. Thus equality holds at
every real rate in the domain, not only at the midpoint used to identify a
piece. This argument assumes the enumerated formulas/roots exhaust the model.

Accrual records interest expense/payable I. Refusal retains cash5.5,
other assets94.5, old debt100, payableI and equity-I; both sides of the balance
sheet equal100. Successful pay leaves cash5.5-I, payable0 and equity-I.
Successful draw adds debt1 and a cash fee0.25, then pays interest: cash6.25-I,
other assets94.5, debt101 and equity-I-0.25. Assets100.75-I equal liabilities
plus equity100.75-I. Each corresponding journal and cash flow is compared.
There is no rounding policy or claim of standards-based classification.

For a signal value o, let H(o) be every retained history with that observation
and A(h) the actions feasible at h. A deterministic observation-measurable
robust policy exists exactly when every nonempty H(o) has nonempty intersection
of A(h) over h in H(o). Necessity: one signal selects one action, which must be
feasible in every member. Sufficiency: choose one action from each nonempty
intersection; the finite signal set makes this a total policy. This statement
is confined to the two atomic actions and supplied information. It gives the
same feasible-policy set as enumerating all assignments and testing every cell.

The high coarse signal contains floating rates below and above0.055. Below,
pay is feasible and draw forbidden; above, pay fails and draw is feasible only
if the facility is available. For the committed-only family the intersection
is empty under coarse information, but the trigger signal separates it into
{pay} and {draw}. If the unavailable-facility mode is retained above the trigger,
its action set is empty; revealing that fact cannot supply funds.

For affine f(r)=ar+b on a nonempty open interval(l,u), its infimum and supremum
are the smaller and larger endpoint limits. Neither is attained if a!=0;
both are attained if a=0. Singleton values are attained. Draw cash6.25-100r
on(0.055,0.06) therefore ranges over(0.25,0.75). At r=0.06, the cap makes cash
0.25 feasible, showing why an open interval and its endpoint cannot be treated
as an undifferentiated interval bound.

If a separately justified uniform approximation bound is |I-Ihat|<=epsilon,
a strict trigger I>K is definitely true when Ihat-epsilon>K, definitely false
when Ihat+epsilon<=K, and otherwise unresolved. The two conclusions follow by
ordering the entire permitted interval. Pay uses the reverse weak inequality.
An observation comparison r<=s uses the same reasoning with its own rate-error
bound. A financial guard margin does not establish an observation margin.
These tests can certify a uniform action on a region only when all its action
and observation premises hold. They do not prove approximation equivalence,
policy regret, an error bound itself, or a probability of breach.

Scope fingerprints retain rate domain, mode set, floor/cap, trigger, signal,
observation map, horizon, query, action class, clause version and precision.
Changed scope is rejected before lookup. Actual source versions, arbitrary
history memory and multi-date filtrations remain beyond this small reference.
Budgets limit transition evaluation, not state support: unevaluated regions
remain listed and interest retains the valid outer bound[3,6]. This bound is
not a policy-feasibility certificate. Eager partition construction can still
be combinatorially expensive in larger models.
