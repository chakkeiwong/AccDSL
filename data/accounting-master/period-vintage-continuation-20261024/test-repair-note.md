# Focused test repairs — 25 October 2026

The first suite ran 41 methods in 114.35 seconds and found two fixture/assertion
errors. The historical reassessment field is supersession_history. Also, the
portable-input validator rejects floating-point input before execution, so a
float is a malformed request, not a financial-operation rejection with a prefix.
The fixture now states that boundary explicitly and tests a zero denominator
as an operation-local invalid exact rational. Neither finding changes financial
semantics. Rerun the corrected focused and predecessor suites before recording.

The independent smoke controls passed: split payment plus depreciation gives
cash 709/2, payable 23/4, profit -2 and operating cash -3. A hypothetical
assessed payable of 2007/4 exceeds cash 715/2 and produces funding_failure
without state mutation. A retained-lot sale produces cash 482, profit 10 and
operating cash 30. These deterministic controls support only this reference
adapter; they do not establish annual, tax-law or whole-company readiness.
