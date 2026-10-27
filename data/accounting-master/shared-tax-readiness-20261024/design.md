# Tax-information readiness for a recorded mixed interval

24 October 2026. S2–S4; MC05/11/13/16/24/26/28/35; G2/G4.

## Audit after inspecting reusable components

The real-company readiness catalog correctly separates jurisdictional bases,
timing, recognition and settlements from financial captions, but is a documentary
catalog rather than an evaluator. MethodRequirements/3 supplies exact typed
known/unknown values, explicit guards and separately retained findings. Reuse
that evaluator; do not modify its frozen versions or the native tax method.

This successor assesses whether an explicit finite set of declarations has
been supplied for a replayed interval. Success is named information_supplied,
not tax_ready. It never computes taxes or establishes that the declarations
are legally correct, economically complete or adequate for a future calculator.
The calculation_ready, source_admission, accounting_admission, annual_close_ready
and executed flags always remain false. An assumption cannot become a fact by
passing a type check.

## Input and population

The closed request contains profile, report_request, report_request_sha256,
interval and information. The interval contains start, end_exclusive and
activity_through. This first assessor requires its start to equal the native
opening date. Its exclusive end lies within the original execution window;
every requested event lies inside the interval. activity_through is the last
included calendar day, exactly one day before end_exclusive. This is a caller's
coverage assertion date, not a changed state date or evidence of source timing.
The report is replayed unchanged; no caller-supplied closing state is accepted.

Every original pretax account, including zero balances, requires a described tax
treatment and signed current-tax reconciliation adjustment. Every balance-sheet
asset/liability except deferred-tax balances requires opening and closing tax
bases. Each lease right found in the opening or any completed intermediate state
requires opening/closing asset and liability tax bases, deduction timing and
modification-gain treatment. Thus a right removed before closing remains in the
population. All such values are declarations, not inferred amounts.

Global declarations cover jurisdiction/regime, interval basis, rate, loss route,
deferred recognition/recovery, cash-settlement policy and affirmative findings
on interval coverage, reconciliation coverage, temporary-difference population,
opening basis support and recognition support. Unknown or absent declarations
remain unresolved; false prerequisite findings are unsupported. Extra keys and
wrong types are invalid. A stopped native event sequence is a separate unresolved
requirement even if every information field is supplied.

Known information has exactly status, value and provenance. Provenance has kind
(assumption or source_reference) and reference. Unknown information has exactly
status and reason. Supplied source references are retained strings, not fetched,
authenticated or admitted. Omitted information is represented as missing_input
by the prerequisite evaluator. Exact request/report/definition/result digests
bind all data. Complete input and native result remain in the output.

Rational declarations use the evaluator's explicit dimensions and scale: money
has the book currency dimension at unit scale; the rate is dimensionless. The
finite information contract requires a nonnegative rate and imposes no arbitrary
100% cap. This is a structural design choice, not a jurisdictional tax rule.

## Acceptance and limits

Compare missing, false, unknown and well-typed hypothetical declarations against
explicit expected classifications. Check all required account and right identities,
including removed right B, rather than counting fields alone. Forge each identity,
drop/extend coverage, vary endpoints and preserve all inputs. Existing tax controls
remain frozen and are not replaced by positive readiness fixtures. No tax amount,
annual flag or legal default is supplied. Passing this assessor only justifies
the next calculation design under separately reviewed assumptions.
