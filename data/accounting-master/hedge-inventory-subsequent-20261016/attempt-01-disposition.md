# First attempt: ineffective adverse test repaired

The first attempt recorded593 checks and two failures, both from the same
wrong-context request. Its mutation set currency toUSD, which was already the
original currency. Acceptance of that unchanged request was correct; the test
did not create the intended inconsistency. The repair changes only the test
currency toEUR. The original attempt, calculator, independent stage targets and
source lock are retained unchanged. This is a test-harness failure, not evidence
against the inventory method; rerun the focused suite after correcting the
challenge. No scientific or accounting promotion follows from a check count.
