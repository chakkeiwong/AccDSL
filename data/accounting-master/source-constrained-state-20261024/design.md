# Source-constrained partial company state

SourceConstrainedCompanyStateDraft/1 carries useful measurements before the
company's executable state is known. It reuses the preceding readiness request
and result, their retained context and all unresolved dependencies. It does not
relax either existing execution validator. Its generic structural date rules
allow explicit fiscal intervals; its finite evidence binder remains the retained
Apple annual/interim package. Other issuers require another checked binder.

## Dates and scope

Intervals use [start, end_exclusive), as already specified in the manuscript's
history chapter and company paths. An explicit inclusive source end becomes
end_exclusive by adding one civil day. For the retained sources, the annual
interval is [2023-10-01, 2024-09-29), and the following interim interval is
[2024-09-29, 2024-12-29). This is a contiguous 364-day year followed by a 91-day
quarter. Those counts describe dates; they select no coupon, depreciation or tax
accrual convention. Prior fiscal-closing work already supports a synthetic
short period: this draft adds a directly authored source-state interface, not
the first recognition of non-calendar reporting.

Each authored period binds its original source-period literal and an observation
whose context supplies that period. Snapshot bindings retain their original
measurement date and consolidated context. The snapshot follows the period's
last included day, not its exclusive end. Current annual/interim balance rows
are all included; prior comparisons and other readings remain in the referenced
readiness result. This bounded projection never claims those other readings
have been translated into executable constraints.

## Measurement constraints

The default is display_only: retain the literal and rational displayed amount,
with underlying measurement unresolved. Even a known displayed amount supplies
no unrounded equality, interval endpoints, account decomposition or CompanyState.
The original precision and source-admission fields remain intact.

An optional caller hypothesis can state a positive display quantum q and
nearest rounding with ties away from zero. It is proposed, not source-admitted.
For a displayed value d that is an integer multiple of q, the compatible
underlying value x belongs to [d-q/2,d+q/2) if d>0, (d-q/2,d+q/2] if d<0,
and (-q/2,q/2) if d=0. At either midpoint the rule picks the value of larger
absolute magnitude; this determines which endpoint belongs to the interval.
This is a deduction under that hypothesis, not a claim about the issuer's
rounding rule. A dash has no numeric inverse image in this draft.

Intervals concern the same reported measurement, including its date, perimeter,
unit and measurement basis. They do not map inventory into units or net PPE
into cohorts. Multiple intervals are not assumed independent, and their product
is not a feasible-history set. Feasibility, joint allocations and actual history
remain unknown. Every readiness dependency is retained even when a rounding
hypothesis is supplied.

## Authoring and validation

Typed records and a named, line-oriented text form lower to the same closed
record. Text scalars use shell-style quoting but are parsed as data; no command
execution or code import occurs. Reject extra fields, duplicate declarations,
unknown references, invalid/reversed dates, period gaps/overlaps, changed source
dates or contexts, incomplete snapshot selection and dropped requirements.
All request strings are single-line printable Unicode to preserve round trips.
The result is accepted only by full recomputation from the bound request.

The structural validator is reusable for explicit fiscal dates and validates
period relations without inferring an accounting method. The binder and source
selection are deliberately finite. A successfully validated record is a partial
description with no executable opening, not an admitted company history.

## Audited evidence contract

Baseline: prior readiness's full record projection and source package, existing
half-open periods, and the two still-unmodified execution contracts. Primary
criterion is preservation plus correct source-bound partial-state semantics,
matched authoring and independently checked date/rounding arithmetic. Source
integrity/context errors veto acceptance; missing actual state motivates later
design. Counts are explanatory. No scientific ranking, historical admission,
whole-company feasibility, accounting-method acceptance or production promotion
is inferred. Plan: docs/plans/accounting-source-constrained-state-20261024.md.
