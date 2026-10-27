# Correct the cash-shortage probe using the actual day count

Attempt-01's facility-interest control expected a refusal at annual rate100.
The loan accrues for two days: (427/5)*100*(2/365)=3416/73, below the280 cash
available at the payment. The native complete result is correct; the test
expectation was wrong. All45 comparisons and the failed expectations remain
in attempt-01 with its checker.

Use annual rate1000 solely as a deliberately extreme refusal probe. The exact
two-day interest34160/73 exceeds280, so cash_shortfall is the intended native
classification. No interpretation of feasible market rates is made. Proceed
in attempt-02; no native code or financial method is changed.
