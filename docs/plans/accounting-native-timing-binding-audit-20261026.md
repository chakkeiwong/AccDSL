# Audit exact information timing in native method bindings

26 October 2026. S2/S3/S4; MC05/19/20/24/25/33/34, G13/G14/G18.

Question: can the existing common requirement types faithfully express the
native information-cutoff conditions, including times within one day, without
weakening source-view admission? The preceding date-only binding deliberately
leaves native availability and ingestion obligations unresolved.

Skeptical audit: inspect existing instant/date/text/numeric types and all already
available temporal helpers before adding a new evaluator. Calendar dates are
not timestamps. String order is not a safe substitute for instant order with
different offsets or precision. A caller finding cannot establish source truth.
The baseline is the native BankAssessment information check and preserved
requirement versions. No new source authority, default cutoff or time conversion
may be inferred. Counts are explanatory only.

1. Inspect exact supported types, temporal helpers and retained timing cases.
2. Record a field-level gap/reuse decision and smallest counterexample.
3. If a repair is justified, write its explicit type/encoding/version plan
   before implementing a bounded reference. Otherwise specify the unresolved
   capability and continue independent ready work.
4. Refresh requirements and the remaining work queue with actual evidence.

Primary criterion: exact representation and ordering agree with native UTC
instants, including offset-equivalent values, same-day differences and unknowns.
Unsupported precision/calendars must refuse. A diagnostic can establish only
timing semantics, not actual evidence availability, membership or source admission.

Artifacts: data/accounting-master/native-timing-binding-audit-20261026/.
No installs, agents, commits, GPU, fees, outreach, publication or forecasting.
