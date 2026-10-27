# Two dates with persistent hidden contract terms

26 October2026. W03/W04/W05/W16; MC05/11/12/26/28/33/34, G16, L01/L02.
Ready continuation after the checked one-date continuous-guards reference.
This plan is not an implemented or accepted result.

Question: which persistent contractual and accrued-claim distinctions must
survive a first-date observation so that a compressed representation produces
the same second-date journal states and feasible observation-measurable
policies as full enumeration? Keep the one-date example as an exact baseline;
add one actual continuation, not independent copies of the first decision.

Before coding, specify the full cash/claim carry, whether a facility is one-use,
repayment/maturity, rate paths and joint constraints, and exact observations
available at each date. Supply a synthetic closed family rather than invented
probabilities. Keep unknown contract type persistent. Do not assume observing
one coupon reveals a facility right. New rates and clauses cannot be redrawn
independently by the compressed representation.

Comparator: exhaustive finite modes × exact two-rate regions, with independent
complete journals, cash prefixes, unpaid claims and policy histories. Establish
region coverage and coefficient equality analytically. Nonanticipativity must
hold at both dates; a separate information-erasing and information-revealing
control should change the policy set. Include equal closing balances with
different unpaid memory, reused versus exhausted facilities, an unresolved
budget prefix, and scope invalidation after a contract/source revision.

Promotion criterion: equality of every full retained transition and feasible
policy on the declared family. Vetoes: missing regions, lost claims, infeasible
cash prefixes, invented future information or a comparator sharing the defect.
Counts/runtime are explanatory. General efficiency, actual source admission,
probabilities and arbitrary-horizon equivalence are not conclusions.

Skeptical review: copying the one-date model twice would answer the wrong
question because it replenishes cash and facility capacity. The continuation
must inherit actual ending state and declared timing. The above missing
premises must be authored and reviewed locally before the execution command;
this is an ordinary implementation choice within existing user authorization.
Use exact rational CPU arithmetic, no installs/GPU/background process, at most
three120-second diagnostic attempts in a fresh two-date-memory output directory.
A discovered ordinary candidate failure triggers repair, not direction rejection.
Source facts and eventual accounting authority remain separate from this fixture.

## Execution premises and skeptical review, before implementation

Execute a bounded continuation now. For each of four persistent fixed/floating
and available/unavailable modes, r1 and r2 range independently over[0.02,0.08].
This rectangle is a supplied feasible family, with no probability or claim
about actual rate dynamics. Coupon floors/caps and fixed coupon5 are unchanged.
The facility permits one draw of1 over the entire horizon and costs0.25 at
that draw. A draw on date1 is repaid in full on date2 after a supplied operating
cash receipt R and before the second coupon. There is no facility interest or
redraw after repayment. Original principal100 is outstanding beyond this horizon.
The receipt is income (cash/equity increase R); no tax is included.

Use two explicit receipt hypotheses R=6 and R=7. This is a contractual/timing
sensitivity, not calibration. Every event inherits the preceding complete
ledger: accrual, first order, dated receipt, facility repayment, second accrual,
second order. If the first order refuses, return the incomplete prefix with its
payable and do not fabricate date2 states. Equal-date settlement ordering is
part of the model. No counterparty finality or reporting-standard treatment is
claimed. All alternative instructions are compared against the same opening.

At date1 coarse/refined signals are as in the one-date reference. At date2
supply the actor's previous signal/order plus predicates for whether interest
exceeds5.5 and whether available cash covers it; these predicates are observed
before the second order. Facility rights remain hidden; the actor remembers its
own draw. Atomic pay/draw choices and robust feasibility remain the objective.
A refusal still supplies correct unpaid-claim state, not a feasible policy.

The amount C2 before second coupon is11.5-I1 after a first pay when R=6, and
11.25-I1 after a first draw. Thus draw then pay requires I1+I2<=11.25. For
R=7 the latter condition becomes I1+I2<=12.25, automatically true because both
coupons are at most6. This analytic comparator is authored independently of
sequential journal execution. In the committed family a refined first signal
selects pay/draw as before. R=6 has a concrete infeasible point I1=I2=6;
R=7 admits pay at date2 throughout. Coarse first information still fails even
when R=7, and unavailable high-rate facilities fail already on date1.

Use exact affine forms in(r1,r2) and rational half-space feasibility, including
strict boundaries. Enumerate the11×11 oracle rate atoms per persistent mode,
then split actual action and observation half-spaces. A bounded closure polytope
has finitely many vertices. For nonempty closure, the average of all vertices
satisfies every strict constraint precisely when each strict face leaves some
vertex off that face; otherwise the strict region is empty. This provides a
feasible witness and detects excluded boundaries. Optimize affine expressions
by closure vertices; test attainment on the optimizing face with the same
strict-feasibility rule. Check this small solver independently on rectangles,
diagonal cuts, lines, singletons, empty strict faces and rational boundaries.

Compare every complete path expression and every feasible domain against
independent closed-form cash/debt/payable/equity/journal formulas, and compare
admissible policies over the declared observation history. The first test is
solver validity; if it fails, repair before interpreting financial results.
Sampling is explanatory only. Retain raw rate/mode/cell identity and unresolved
regions. Check independent-resampling and facility-replenishment controls,
clairvoyance, omitted repayment, lost payable and altered signal histories.

Audit passes with this narrower contract: R=6 is expected to reject the
candidate policy, which motivates R=7 as a discriminating resource comparison;
it does not reject the simulator. Both are exact declared-premise cases, not
statistical ranking or promotion of a default. A return to independent fresh
cash/facilities at date2 would compute the wrong target. Larger-dimensional or
arbitrary-horizon methods, common production execution and real source admission
remain open. Save code, formulas, inputs, exact controls, result and manifest in
data/accounting-master/two-date-continuous-memory-20261026/. No existing successful
reference is rerun; import only its pure definitions if needed.

## Reviewed repair extension after three rejected attempts

Three runs stopped on inconsistent account identifiers in accrual, draw and
repayment journals, before producing an accepted economic result. The earlier
repair note incorrectly said all journal strings had been inspected: the third
failure shows that inspection was incomplete. Preserve it as a recorded failed
review, not a justification to relax full-journal comparison.

Root repair: use the balance dictionary's account identifiers in every journal,
with distinct event labels. Independently update the candidate and oracle to
that explicit schema. Before any fourth full run, inspect every journal debit
and credit against the balance account set on fixed/floating, first/second-draw,
and refusal paths, and compare those small complete journals. A failed local
schema check vetoes the full run. Authorize one additional120-second CPU run
under the unchanged economic/evidence contract, in attempt-04. This is a bounded
implementation repair under the user's continuation, not a widened scientific
sweep. Further failures require diagnosis and preserved incomplete status;
no evidence result may be promoted just because its numerical balances match.

Skeptical review: ordinary spelling patches missed a common schema issue. The
new account-membership diagnostic addresses the cause and would have caught
all three defects before full enumeration. No probability, cash/default model,
or oracle feasibility condition changes. Thus the additional bounded run can
answer the original question; rejecting the research direction is unwarranted.
