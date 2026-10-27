# Exact information timing: inspected gap and diagnostic contract

26 October 2026. MC05/19/20/24/25/33/34 and G13/G14/G18.

MethodRequirements/1–3 accept boolean, text, date and rational scalars. Only
date and rational permit ordered comparison; date parsing requires a canonical
civil date. TemporalMeasurementConstraints/1 calls a date-level balance time
an instant, but it also parses a civil date and is not an information timestamp.

The native BankAssessment auditor normalizes datetime.fromisoformat to UTC.
The retained schema uses date-time validation. Context chronology likewise
requires an explicit offset, while CompanyInformationDraft/1 uses a UTC string
regex with an arbitrary fractional part before datetime parsing. The receivable
source helper restricts timestamps to whole UTC seconds. These are different
supported scopes and cannot be interchanged by their names.

Audit passes for the following cheap diagnostic: exercise the actual native
parser and existing requirement dispatch on retained timestamps; compare a
same-day later instant, equivalent offsets, and two fractional instants beyond
microseconds. The oracle uses integer day/second counts and an explicit rational
fraction, not floating timestamps. Inspect native schema acceptance separately.
No financial method executes and no original evaluator changes.

Primary criterion: classify whether existing representation loses the ordering
needed by the native information condition. Counts are explanatory. A same-day
date collision is an interface gap, not evidence that native full-second checks
are wrong. A submicrosecond collision, if accepted by the schema/parser, limits
that parser's claim. Existing full-second retained results remain separate.

Assumptions: the diagnostic uses Gregorian dates and explicitly supplied fixed
offsets. It does not model leap seconds, timezone databases, historical civil
time regimes, or infer an instant from a date-only disclosure. Those require
separate contracts. No source availability or admission is authenticated here.

Reuse decision after diagnosis: preserve all old versions. Prefer an explicit
exact timestamp-to-rational derivation feeding the existing dimensional
requirement/binder machinery over a second predicate interpreter. Any repair
needs a versioned grammar, retained original strings and source identities,
precision refusal, unknown propagation and independent ordering examples first.
