# Explicit time types before exact numeric solving

24 October 2026. Inspected frozen statement_context.context_check/evaluate,
joint_measurement_constraints_v1.validate/assess/check_witness,
method_requirements_v2.typed and reconstruction_v1.construct. The current source
report has ten stock-flow bridges. The existing generic conjunction correctly
requires identical complete types, so it cannot directly express them.

Decision: introduce a distinct TemporalMeasurementConstraints/1 profile whose
measurement type contains the existing quantity value type, an exact instant
or half-open civil-date period, and a named measured quantity. Time remains part
of the measurement type; it is never removed from the supplied declaration.
The value type carries invariant issuer/perimeter/basis and explicit monetary
dimension/scale. A source adapter must retain every original context field and
bind its source dates to this canonical time representation. The two profiles
remain distinct and v1 behavior is unchanged.

Two relation forms are allowed. A same-time equation requires equal economic
value types and equal time declarations for every operand; different measured
quantities may be added only under its proposed identity premise. A stock-flow
bridge names one opening observation, signed period movements, one closing
observation and a declared period. Opening and closing must name the same
measured quantity, use instants on the day before start and day before exclusive
end, and share the economic type with all movements. Every movement must span
exactly that period. Date-only closing snapshots use the retained convention;
intraday timestamps and arbitrary time aggregation are outside this profile.

The named quantity is a declared interpretation, not a conclusion inferred from
equal captions or amounts. Source binding must fix its proposed mapping and
refuse edits. A stock-flow identity premise asserts which period movements
belong in the closing relation. Matching quantity/type fields alone does not
admit a population equivalence or accounting identity.

After those checks, lower to the unchanged exact same-scope numeric conjunction:
one variable per observation, opening coefficient +1, closing -1 and the exact
supplied movement coefficients. The result retains the full typed definition
hash and the generated numeric definition. Lowering does not assert that the
complete measurement types are equal; it only exposes the scalar arithmetic
authorized by the validated relation form. Explicit budgets and optional
interval/identity premises retain their prior meanings.

Evidence contract: exact temporal validation plus independently checked rational
witnesses is the pass criterion. Wrong dates, mixed periods, swapped endpoints,
changed quantity, mismatched issuer/perimeter/basis/dimensions/scale, cycles in
time via repeated endpoint identity, or changed lowering must reject. Absent
premises are unresolved after structural checks. Infeasible conditional equations
reject that system, not research direction; resource exhaustion remains unknown.
The baseline is unchanged v1 plus hand-solvable bridges and the retained displayed
bridge checker. Time rules are explicit scoped design choices, not global defaults.

First test the reusable contract with constructed amounts, then bind the annual
and interim retained cash-flow bridges with exact source identities and optional
rounding/identity/mapping assumptions. Keep those two source observations distinct
even when they describe the same date: their source and reporting bases differ.
The source adapter preserves all 256 observations/143 dispositions and never
creates legal cash or other missing executable state. A result may be retained
as engineering reference evidence without claiming accounting admission.

No scientific ranking or forecast is run. Commands are bounded CPU-only unit and
conformance tests. A source/hash or harness failure vetoes interpretation until
repaired. Independent/domain/human acceptance remains pending; no whole MC closes.
