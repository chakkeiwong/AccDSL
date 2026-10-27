# Exact committed-right financing viability boundary

27 October 2026. Attempt 01 passes: two continuous receipt domains, eight
action-region exclusions, 366 guard implications, eight boundary examples,
315 assertions and ten corruption controls. All 146 protected files are unchanged.
Runtime 0.278 seconds. Exact affine certificates establish the continuous result;
point checks are explanatory controls, not its proof.

For committed borrowing rights, coupons 3<=I1,I2<=6 and the original once-only
facility, the infeasible set is exactly

    I1 > 11/2  and  I1 + I2 > R + 21/4.

At receipt 6 this becomes I1>11/2 and I1+I2>45/4. At receipt 7 it is empty on the
specified coupon square. Strict boundaries are retained: equality at the first
trigger permits pay1; equality at the sum boundary permits draw1/pay2 with zero
final cash. No model domain, right, payment rule or source assumption is changed.

Derivation: when I1<=11/2, pay1 is possible. Receipt R>=6 then leaves at least 6
for coupon I2<=6, so pay2 always succeeds. When I1>11/2, pay1 fails; draw1 is
permitted and its fee leaves the first settlement nonnegative. Repayment after
receipt leaves R+21/4-I1 for the second coupon. The facility has already been
used, so draw2 is unavailable; pay2 succeeds exactly at the stated sum boundary.
The exact checker proves every guard of the indicated viable path throughout
each region, and excludes every action path in the infeasible region.

The original refined first trigger therefore suffices to implement a common
rule on the derived viable region: draw1 iff the trigger is true; pay2. This
uses no future coupon at the first date. The rule does not make the excluded
region feasible, and that region is not silently removed from the model. Fixed
coupons 5/5 are a separately checked viable example; absent/mixed rights and
general receipts are outside this committed-right conclusion.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Accept exact scoped boundary | Exhaustive region partition, all viable-path guards and all infeasible action exclusions certified | Ten bad boundaries, coverage/proof objects and information claims rejected | Representation of missed obligations after infeasibility; broader rights/models | Integrate diagnosis/boundary, then connect rejected payment to persistent obligation/report semantics | Actual distress, automatic domain restriction, optimality, default change or forecasting |

| Inference status | Finding |
| --- | --- |
| Hard veto screen | Missing action/guard/region, false proof and future-information claim rejected. |
| Statistically supported ranking | Inapplicable: exact affine result. |
| Descriptive-only differences | Counts and runtime. |
| Default-readiness | Conditional characterization only; original domain remains intact. |
| Next evidence needed | Preserve financially infeasible branches as explicit economic outcomes. |

Strongest alternative explanation was a hidden guard beyond the simple cash
inequality. Every inherited guard was included, including strict trigger,
once-only memory, repayment and cash nonnegativity. Corrupt proof or omitted
guard would overturn the result. Manifest records command, Git, Python, CPU,
source locks and outputs; GPU intentionally hidden. Version 5.44 still governs.
All 18 packages stay open; S1–S5 partial, S6 held, E3 deferred.
