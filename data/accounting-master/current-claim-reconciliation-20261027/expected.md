# Independent arithmetic and reuse conditions

27 October 2026. These expected values are derived before the new verification
and do not import the production methods or rerun an archival writer.

C01: with principal 100, fixed rate 1/20 and shocked floating rate 7/100,
interest is 5 + 2 alpha. Starting cash 95 and no other cash movement gives
90 - 2 alpha. Both endpoint histories fit historical interest 5, but their
future pairs are (5,90) and (7,88). For alpha in [1/5,2/5], interest endpoints
are 27/5 and 29/5, cash endpoints 448/5 and 446/5. Every pair sums to 95.
This is a counterexample to unique reconstruction, not a claim that every
filing leaves every contract characteristic unidentified.

C25: opening cash 16 and inventory 104 balance debt 100 and capital 20.
Fixed coupon 5 and operations 6 leave cash 5. Face price 88/105 requires
315/88 new face to raise 3; final face is 9115/88 and carrying amount 103.
Final cash/inventory are 8/104; interest/payroll expenses are 5/6; capital
remains 20. Reported equity is 20 - 11 = 9, giving assets 112 = 103 + 9.
Floating coupon 7 leaves cash 3 after operations. Gross equity proceeds 6
and fee 1 bring cash to 8 and book capital to 25; expenses are 7 and 6, so
reported equity is 12 and liabilities remain 100. Price 19/100 gives 600/19
new shares, ownership fraction 6/25 and unchanged 100 incumbent shares.
These are authored initial-measurement conventions, not standards admission.
Compare all final balances and every dated cash movement in each of the four
retained complete executions, not just final cash or a stored pass flag.

C23: in the retained two-type/two-state model, each initial pair has mass 1/4.
Type 0 has stay probability 3/4; type 1 has stay probability 1/2. An observed
state has likelihood 4/5, the other 1/5; a missing observation has likelihood 1.
For observations (1, missing, 0), direct path enumeration gives unnormalized
masses (68,23,80,20)/800, hence posterior (68,23,80,20)/191. Conditioning the
original prior on type 0 gives (68,23,0,0)/91 after those observations. Removing
that restriction and replaying restores type 1; another likelihood update of
the zeroed posterior cannot do so. The four-prior/27-sequence exhaustive
comparison remains retained evidence, not a newly executed filter benchmark.

C22: source Example 1 has creditor outside value max(16,28/2)=16 and final
credible payment max(8,26/2)=13. Current resources are w+2, so continuation
needs w+2+13 >=16, equivalent to w>=1. At w=1, payments (1,2,13) leave cash
(0,0,13) and give the creditor 16. At w=1/2 the available 31/2 is insufficient.
Operating value 28 exceeds liquidation value 16 in both cases. The stipulated
offer game and deterministic one-creditor setting are essential.

C21: the reviewed proof uses P(E_t) >= (1-delta_t) P(E_{t-1}) including the
zero-survival case. With initial failure at most delta_0, total failure is at
most Delta = 1-(1-delta_0) product(1-delta_t). Bounded losses in [0,B] differing
by at most rho on E_T give E|L-Ltilde| <=rho(1-p)+Bp <=rho+(B-rho)Delta for
0<=rho<=B. No policy averaging or independence of the hazards is needed.
Existing exact counterexamples and 272 checks are retained; their old source
hash identifies the diagnosed baseline, not the later repaired manuscript.
The protected integration records connect that repair to the current text.
