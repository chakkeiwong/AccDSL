# Finite guarantee illustration: declared before computation

Question: can multiplying an underlying-value change by a stated 10% retained
share describe the full change in the amount left after a guaranteed benefit?
The comparator is the current manuscript's conditional share component,
0.1 times the change in underlying value. That component remains correct for
its stated target. A guarantee can add a separate economic exposure.

This is an authored settlement-date component example, not an observed policy
or an insurance-contract classification. Let U be the nonnegative amount in a
held pool allocated to this component, in one currency at one settlement date.
Assume the policyholder receives P = max(90, 0.9 U). Ignore other benefits,
expenses, premiums, taxes and settlement movements in this component comparison.
The illustrative amounts left from the pool are R = U - P. The minimum 90,
share 90% and U scenarios 80, 100, 120 are convenience values chosen to cross
the guarantee boundary. No probabilities, time discounting, risk adjustment,
fair values before settlement, CSM or profit-and-loss entries are supplied.
No eligibility threshold is inferred from either percentage.

By max(a,b) = b + max(a-b,0), P = 0.9 U + max(90-0.9 U,0), hence
R = 0.1 U - max(90-0.9 U,0). The last term is the extra settlement payment
needed to meet the floor; it is not a separately valued guarantee option.
The derived kink is U = 90/0.9 = 100. Below that value, increasing U by one
leaves one more unit after the fixed benefit; above it, only 0.1 remains.

Predeclared expected rows (U, P, R, extra floor payment):
(80, 90, -10, 18), (100, 90, 10, 0), (120, 108, 12, 0).
The U80-to-U100 change in R is 20, comprising share change 2 and release of
the extra floor payment 18. The U100-to-U120 change is 2. A zero-value pool
still owes the floor; a zero floor restores the simple proportional result.
Verify these exact values and the derived identity using stdlib Fraction.

Pass/fail concerns only arithmetic and the declared payoff relation. Failure
requires repairing the derivation or code before use. Passing does not admit
the example to AASB 17, satisfy B101/B107's duration and probability-weighted
conditions, measure fulfilment cash flows or give a CSM movement. The source
comparison must preserve B104's fee definition and B111–B118/paragraph 45's
different accounting destinations, onerous limits and mitigation conditions.
No stochastic comparison, ranking or default promotion is authorised here.
