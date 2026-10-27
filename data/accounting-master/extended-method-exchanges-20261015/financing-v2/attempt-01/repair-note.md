# Attempt 01: reporting-calendar fixture repair

The independently checked packet has 19,815 checks, with two failures. Both
boundary fixtures change an event date across a year boundary without changing
its declared reporting period. The resulting `reporting_period_mismatch`
correctly precedes the intended anniversary/designation checks. This is a
fixture defect, not evidence of a different accounting conclusion. The builder
will update the boundary event's annual reporting period with its date. Keep
the original packet, validation and input snapshot unchanged; build attempt 02.
Also correct the contract's equity-report bridge to name the new repurchase
and reissue counters already checked by the verifier. No continuation veto
fired; independent finances, protected inputs and staged index passed.
