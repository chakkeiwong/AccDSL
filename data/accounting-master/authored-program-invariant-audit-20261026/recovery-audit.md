# Counterexample harness correction

The first probe used a post-sale book as a report opening. The native report
correctly refused opening_at_period_start, so that run did not answer the
invariant question. Keep the genuine period opening and instead author the
single changed claim field in the sale's memory effect, followed by a report.
Compare the resulting complete state with the intended changed state and the
original lifecycle control verdict. This distinguishes a valid report boundary
from a missing economic-state invariant. Bound assertion output to status/reason
instead of printing nested books or full trace records.

The empty-customer mutation is already refused by the typed memory schema's
nonempty-string rule. Record it as covered, not as a missing invariant. Do not
relax the schema or force every candidate probe to demonstrate a gap.
