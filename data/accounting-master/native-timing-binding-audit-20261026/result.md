# Date requirements cannot substitute for exact information timestamps

26 October 2026. MethodRequirements/1–3 reject an instant type; civil dates
cannot distinguish evidence arriving one second after a same-day cutoff.
TemporalMeasurementConstraints/1 uses date-level balance times, not timestamp
ordering. These are genuine interface limits rather than defects in civil dates.

The retained native parser correctly orders the full-second case and recognizes
equivalent explicit offsets. However, its date-time schema accepts
2026-04-01T00:00:00.0000002Z and 2026-04-01T00:00:00.0000001Z, while its datetime
parser maps both to the same value. It therefore computes the wrong ordering
for an exact-instant claim: two-tenths of a microsecond is later than one-tenth.
The supplied BankAssessment packet has five unique timestamps, all whole seconds;
this finding does not invalidate those retained full-second comparisons.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Refuse date truncation and unrestricted datetime reuse | Same-day and submicrosecond counterexamples expose lost ordering | General exact-instant claim fails; retained full-second evidence unaffected | Broader timestamp grammar/precision policy | Specify an exact rational projection into the existing evaluator | Source availability truth, accounting admission, whole native profile validity |

Repair trigger: preserve the old parser/profile and add a named exact conversion
with a restricted, explicit grammar, original-byte lineage, offset handling and
unknown propagation. Reuse the existing binder and rational comparisons, not a
second predicate evaluator. Unsupported leap seconds, unknown offsets and
date-only evidence require explicit refusal or unresolved treatment, not a
convenient timestamp. The flaw rejects the unrestricted parser claim, not the
simulator research direction. No global continuation veto fired.

The probe, inspected source hashes and exact comparisons are retained in
checks.json. This is a deterministic diagnostic, not a stochastic comparison.
