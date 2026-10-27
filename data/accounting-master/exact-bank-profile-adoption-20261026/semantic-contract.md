# BankAssessmentExactTime/1 documentary contract

26 October 2026. This explicit successor retains the original BankAssessment/1
financial definitions, frozen source period, supplied scenario bounds, partial
outputs, publication effects and scientific limitations. The predecessor
contract is bound in source-lock.json. No current regulatory advice or source
admission is supplied. It supports the same three named operations in
specification_example mode and has no accounting effect.

All information timestamps use the pinned exact rational-instant converter.
Availability is no later than decision_at; ingestion is no later than
system_asof. Both comparisons include all evidence in the semantic input
closure, including superseded records. Membership is exact reference membership.
Measurement, assessment and vintage/origin civil dates compare against the UTC
day of the exact decision instant. The converter uses its declared Gregorian
no-leap-second calendar, mandatory known UTC offset and at most eighteen
fractional second digits. Excess precision or negative-zero unknown offset is
explicitly unsupported, never silently truncated or treated as UTC.

Profile and all transitively dependent typed-envelope schemas are versioned
separately. Unchanged financial input/output shapes retain original schema IDs.
SchemaLock binds exact complete schema bytes and these contract bytes; the
profile identifies that lock and the supported read-only operations. The
successor checker is pinned to the predecessor native validator and exact-time
implementation. It validates the chosen profile and lock before request replay.

An old request is not reinterpreted under this contract. Conversion creates a
new OperationRequest, signature and exact submission bytes under a distinct
workspace_key. It publishes a new query and receipt. Old profile records,
publications, query indexes and receipts remain unchanged. A selected original
financial closure may be shared only when its exact meaning and bytes remain
unchanged. Replacing an evidence time changes that closure's identities and is
recorded separately from profile-only conversion.

Within the successor profile, exact request replay returns the original
successor output/receipt/status/coverage before freshness or head checks.
Changed bytes under an existing identity refuse. New requests still require
native operation/signature, view, environment, budget and accounting-head
agreement. A rejection has no query result, receipt or coverage and changes no
world state. Successful or partial query publication changes only immutable
records and the query index, never accounting heads, journals or balances.

This contract specifies finite closed examples. It does not implement a server,
authorize a financial posting, prove concurrent or hardware-loss durability,
authenticate real source publication times, optimize a banking policy, calibrate
a forecast or establish general whole-company financial-statement completeness.
