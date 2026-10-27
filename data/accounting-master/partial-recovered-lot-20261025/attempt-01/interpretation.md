# Incorrect expected profit repaired

The first focused run passed11 of12 tests. The statement control returned21,
while the test asserted61 without a supporting derivation. The implementation
and statement identities were correct relative to the inspected fixture.

The original lease reduction credits other_gains20. Return settlement credits
cost of sales4 and debits handling expense8; it creates no revenue adjustment
because the actual refund40 equals the opening refund liability40. Thus profit
before this sale is20+4-8=16. Proceeds15 less released inventory10 adds5, giving21.
Assets827 minus liabilities214 equals equity613,which is opening equity592 plus
profit21. Operating cash is-48+15=-33 and the indirect bridge gives the same amount.

The unsupported expected61 was wrong. This is a test-fixture expectation defect,
not evidence against proportional allocation. Preserve the original test and log;
change only that expectation and rerun the focused suite. No implementation
change or weakening of acceptance criteria is justified.
