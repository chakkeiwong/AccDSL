# Correct the refusal-wrapper expectation

27 October 2026. Attempt 01 stops at assertion 148 before recording its first
complete case. The verifier wrongly required the method-clock wrapper to omit
its transition field on refusal. The protected method-clock implementation
always carries the transition result, including failed prerequisite diagnostics.
The transition itself has no after state, journal or flow proposal. Preserve
attempt 01 and correct the check to require invalid preconditions and absence of
those successor fields. No runtime code, financial expectation or source changes.
Attempt 02 uses the same cases and bounded CPU contract.
