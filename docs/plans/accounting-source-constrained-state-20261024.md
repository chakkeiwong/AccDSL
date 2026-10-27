# Fiscal periods and partial source-constrained company state

S2/S3/S4; MC02/04/05/06/10/11/16/24/28; G2/G5/G12/G13/G15.
Predecessor: real-company-input-readiness-20261024. This is deterministic
language/interface design, not a forecasting experiment or production release.

Question: can a program represent a dated partial company state constrained by
reported amounts while declining to manufacture the latent state required for
execution? Keep the problem separate from the finite calendar-year engines.
Baseline: readiness's exact source/context/precision and unavailable dependencies;
existing Context/EvidenceView distinctions and source-family results remain
authoritative. Inspect those prior definitions before choosing additional fields.

Skeptical audit: a 52-week fiscal year is not a calendar year; date arithmetic
does not choose a day-count or depreciation method. A consolidated snapshot
does not become a legal trial balance. A displayed amount is known evidence,
but exact latent balance and a rounding interval are not determined unless
the rounding convention is separately supported or explicitly assumed. A
cohort or claim decomposition cannot be inferred from a net caption. Do not
call a nonempty list of constraints a feasible whole-company state. The new
interface must preserve those distinctions even when every schema check passes.

Implement a closed typed/text draft for explicit half-open fiscal intervals,
dated source observation bindings, reported-amount constraints and unresolved
state requirements. A generic structural validator should handle non-calendar
periods; a retained-source binder checks Apple identities and original dates.
No observed aggregate becomes an exact underlying balance. The no-assumption
path carries display-only constraints. An explicitly declared rounding
hypothesis may add a labelled interval on that same reported measurement,
without allocating it to legal accounts or discharging unrelated unknowns.
Assumption-free and conditional states must have distinct identities.

Use matched typed/text construction, exact output identity and independent date
and rational arithmetic checks. Test overlapping/gapped period chains, reversed
or invalid dates, changed source instants/perimeters/units, unsupported exact
bindings, lost obligations and altered rounding premises. Preserve useful
displayed values when component state is unknown. The result must retain actual
history feasibility as unknown and expose no executable CompanyState.

Primary criterion: a coherent, source-bound partial-state representation with
correct finite semantics and transparent missing dependencies. Source corruption,
context mismatch or silent inference veto acceptance. Missing real facts trigger
further scoped design, not a global stop. Counts/builds are explanatory only.
No accounting-method acceptance, production readiness, exhaustive family or
forecast skill follows from passing these checks.

Defaults: half-open date intervals are an explicit engineering convention that
reuses existing company paths; inclusive source dates require a checked next-day
conversion. Display-only is the baseline because the retained sources state
displayed precision, not a checked rounding rule. Any rounding route is an
optional hypothesis, never a default promotion. Exact fractions avoid numeric
rounding in the diagnostic; they do not make source amounts exact.

Artifacts: data/accounting-master/source-constrained-state-20261024/.
Plan before implementation; CPU-only check/record/replay; preserve predecessor
files and failures. Once checked, integrate explicit company composition,
readiness and this coherent source-state interface in a protected successor to
Version 3.56. Then refresh whole-language gaps and resume independent ready
work. S1–S5 partial; S6 held; S7 deferred. No paid review or external publication.
