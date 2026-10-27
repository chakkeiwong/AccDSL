# From equal payment totals to valid continuation

Readers: accounting modellers and language implementers. Entry: the preceding
section shows one/split payments leaving 1/16 unpaid and different flow histories.
Open questions: does this survive arbitrary cash-only schedules, and can the
equal financial balances be used as one future state? Teach the invariant first,
then show the chronology and replay counterexamples before restricted equality.

The recurrence follows by substitution, with S_i defined before its display.
The strictly positive U−C gap explains both partial-only admissibility and the
residual claim at exhaustion. Separate finite method checks from the algebraic
proof and from runtime resource/identity/date conditions. The program-opening
constraint creates a real implementer question: retain both original opening
and current checkpoint rather than reset the date or erase flows.

Cold-reader questions: Why can payment not remove the funding gap? What does
the algebra prove versus the twenty runtime cases? Which concrete instruction
distinguishes equal balances? When is numeric continuation equal? Why does a
midperiod checkpoint need its original opening for cumulative reports?

Protected baseline: manuscript-coupon-continuation-v546-20261027. Target:
manuscript-coupon-scope-v547-20261027. Append one section, preserving all earlier
argument and equations. Author-read both covers and every added page. Keep
independent reader, domain and whole-document acceptance pending.
