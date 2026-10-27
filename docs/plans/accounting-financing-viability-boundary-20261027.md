# Characterize the unchanged financing viability region

27 October 2026. MC04/05/08/10/11/12/13/18/24/25/26/28/33/34;
W01/03/04/11/12/13/16. Follows the exact policy-failure diagnostic.

Question: on the existing committed-right coupon domain 3<=I1,I2<=6 and receipts
6 or 7, which economic points admit some permitted action sequence, and does
the original refined observation rule realize those paths without future leakage?
The target is deterministic viability, not a forecast, probability or optimum.

Skeptical audit: a finite grid cannot prove a continuous regional boundary. Derive
the boundary algebraically from the independent guards, then use the protected
exact affine partition/proof checker to check every relevant action region.
Keep strict trigger I>11/2, once-only borrowing and repayment timing. Never
replace a failed path with its later algebraic cash. Right absent/mixed is outside
this committed-right statement, not silently covered. Fixed-coupon examples are
checked separately. Receipt between 6 and 7 is a theoretical extension that needs
its own derivation; do not claim the existing finite receipt table validates it.

Candidate characterization for R in {6,7}: if I1<=11/2, pay first and pay second
whenever cash covers, otherwise draw second if triggered. For I1>11/2, draw first
is required; after repayment, pay second is possible iff I1+I2<=R+21/4. At R=6,
the putative infeasible set is I1>11/2 and I1+I2>45/4. At R=7 the domain has no
such point. This is a hypothesis pending exact derivation/checks. The policy uses
the refined first trigger, second coverage/trigger and own-action memory only.

Primary criterion: algebraic proof and exact region coverage, with no possible
point where the proposed classification differs from any-action viability.
Independent expected-state guards are the comparator. False coverage, strict
boundary mistakes, missing actions, bad proof certificates or a policy using
future I2 at the first decision veto the result. Positive/negative boundary and
the existing 1/16 witness are mandatory checks. Grid samples are explanatory
only. A region result must not become an automatic model restriction or repair.

Assumption audit: all numerical constants, domains and rights come from the
protected financing fixture; favorable restriction is not authorised. A derived
threshold can describe required liquidity but must not be adopted as a default.
No probabilities, utility ranking, actual accounting admission or forecasting.
At most three fresh 120-second CPU attempts, GPU hidden, no installs. Store
source locks, proof objects, coverage checks, manifest and result under
data/accounting-master/financing-viability-boundary-20261027/.
Then integrate this result with the point diagnostic; refresh the master and
keep all 18 packages and financing evidence work open.
