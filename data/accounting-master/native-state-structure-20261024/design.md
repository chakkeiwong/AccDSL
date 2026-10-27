# Exact structure for the retained native legal-book state

24 October 2026. NativeReturnStateStructure/1 validates raw bytes for the
NativeReturnBookReference/1 runtime shape. It is a separate structural result,
not an automatic source admission or selected-state predicate pass. Its exact
schema digest and raw SHA256 are caller-pinned; unavailable or mismatched bytes
are not silently repaired. The strict preserved decoder rejects duplicate keys,
floating/nonfinite JSON numbers, malformed UTF-8 and non-ASCII object keys.

The complete outer fields are taken from native_returns.py initialize/invariant.
Nested component and tax shapes reuse the retained return authoring schema;
lots add concrete disposition memory. Balances use the exact native account
registry. Flow records match transition; prior-year records match carry. The
schema is closed at every fixed object. The lot dictionary has explicit key
syntax and a closed lot shape. Full typed records, including otherwise unused
fields, are validated before any selected projection.

Known runtime balances, refund/recovery, lot amounts, interest amounts, flow and
adjustment coefficients are canonical exact rational strings. Negative coefficients
are structurally legal; nonnegative/funding/accounting meaning belongs to the
separate domain evaluator. Runtime settled/disposed memory is concrete Boolean.
The tagged-unknown disposition experiment is deliberately outside this concrete
native profile and remains a separate selected-language extension.

Legacy unknown strings are retained only where native initialization can carry
them without computing them: component sold/expected units, per-unit refund/cost,
handling/deterioration estimates; tax rate/bases and the five tax findings.
Opening DTA/DTL must be known, as initialize computes them. These rules preserve
pending tax evidence without pretending that tax can execute. A text label equal
to unknown remains ordinary text where the inherited schema permits it.

All dates are canonical valid ISO dates; this layer does not impose a new ordering
between retained prior-year dates and the current period. Lifetime seen IDs,
disposed lots and prior-year adjustments survive carry. Hash strings and retained
record pointers follow the existing authoring contract. Unicode values are not
normalized. Source/role/calendar meaning remains a caller/method obligation.

Bounds reuse 1,000,000 raw bytes, 4,096 nodes, depth 48 and scalar length 4,096.
They are defensive implementation limits, not financial restrictions. The schema
and bounded exact-scalar walk are both tested. Structural errors include the
field path; raw decode failures identify the byte-decoder boundary. Results retain
raw/schema/decoded hashes and the decoded record, with all admission/eligibility/
execution flags false. The original bytes remain caller-owned.

Evidence: every saved after-state and carry opening, a reconstructed initialized
opening from inspected authoring/source facts, pending-tax/unused-component
unknowns, and systematic extra/missing/type mutations for every fixed-object
schema location. Compare selected semantic failures separately: structurally
valid negative cash is still funding_failure under the state assessment.
No new method, actual-company state or complete accounting standard is claimed.
