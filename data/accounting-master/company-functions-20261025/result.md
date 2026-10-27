# Reusable pure-function result

Typed CompanyFunctions/1 declarations now lower through the protected
CompanyExpressionsDraft/1 evaluator. Twenty-three focused test methods cover
names, types, units, entity context, nested/repeated calls, unknowns, lazy
branches, unused arguments, recursion and resource boundaries. Forty-six
comparison checks cover six collection-policy cases and complete three-year
financial results. The verification manifest records the actual run counts.

The ordinary case exactly reproduces the saved policy, generated path and full
accounting result. The stress case decreases cash by 192/5 and increases
receivables by 192/5, leaving profit unchanged. An unused unknown discount in
the stress branch produces the same financial results. Unknown selected inputs
block materialization; a negative collection fraction is refused by the
existing policy generator. No input is mutated or promoted to historical,
behavioral or forecast evidence.

Definitions are pure, monomorphic and lexically scoped. All definitions and
branches receive static checks. Calls preserve declared argument dependencies
separately from effective result dependencies, and generated nodes retain their
definition/call origins. Scope and expansion budgets are explicit convenience
limits. No host code, recursion, simultaneous solver, event generation, automatic
financing or external model is introduced.

The original 20 tests passed; three later boundary tests exposed a fixture
counting mistake, documented and repaired before final verification. All
protected predecessors remain unchanged. See review.md for decisions and
limits, checks.json for named evidence and manifest.json for provenance.

Matched textual syntax, parser spans, portable module dispatch, endogenous
decisions and broader company methods remain open. Next: integrate the checked
source/function additions into protected Version 4.00. Current manuscript stays
Version 3.99 until that integration passes. S1–S5 partial; S6 held; S7 deferred.
No whole requirement closes, no commit is made, and forecasting remains deferred.
