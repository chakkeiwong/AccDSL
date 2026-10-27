# Continuous coupon-domain viability contract

27 October 2026. Implements accounting-financing-viability-boundary-20261027.md.
Skeptical audit passes with a simplification discovered algebraically before the
run: when I1<=11/2 and R>=6, second cash after pay1 is at least 6, which covers
every I2<=6. Thus the proposed fallback second draw is unnecessary on the viable
region. The explicit rule is draw first iff I1>11/2; pay second. This is a
conditional witness on the derived viable region, not a changed default/domain.

Domain: committed right, 3<=I1,I2<=6, R exactly 6 or 7, original once-only draw,
fee 1/4 and repayment. Coupon variables are used directly; the protected coupon
map covers this range. Check each coupon coordinate endpoint with the retained
rate function; rate-region counts are not used as area or probability.

Partition domain with the two exact predicates I1<=11/2 and
I1+I2<=R+21/4. Three exhaustive disjoint regions: pay-first, viable draw-first,
and infeasible draw-first. Certify all inherited guards of pay/pay in the first
region and draw/pay in the second, by proving each violating intersection empty.
In the third region prove the accepted intersection empty for each of four
action sequences. All emptiness objects use the protected rational elimination
producer and independent multiplier checker. Preserve strictness and all rows.
State matching against saved symbolic paths is required before interpretation.

Primary pass: exact proofs and complete partition/action coverage. Controls
damage multipliers, boundary strictness, branch/action coverage and the claimed
observation rule. Authored point tests cover first-trigger equality, sum equality,
both sides, the prior witness and receipt 7. They explain boundaries; exact
certificates establish the whole region. Show R7 infeasible region empty. The
information witness uses only the first refined trigger and constant second pay;
future I2 never enters first action. No automatic removal of infeasible points.

At most three fresh 120-second CPU attempts, GPU hidden. Record proof objects,
complete guards, expected boundary, source hashes, manifest and result. No
forecast, actual company claim, optimality, probability or model default change.
