# Use the native obligation structure in the adverse fixture

Attempt02 reached the final obligation-preservation control, then correctly
rejected a malformed test obligation supplied as a string. The native contract
requires id, meaning and affects. The fixture now uses that exact structure.
Attempt02 code/failure is retained. Fresh attempt03 tests preservation of a
valid unresolved obligation without relaxing native validation.
