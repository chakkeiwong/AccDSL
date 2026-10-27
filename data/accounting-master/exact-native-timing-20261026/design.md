# Exact native information checking: documentary successor

26 October 2026. MC05/19/20/24/25/33/34, G13/G14/G18.

Skeptical audit passes for a separately named read-only ExactBankInformation/1
checker. It subclasses the frozen BankAssessment Auditor only to override
information(root, view_ref). The retained request/response auditor owns all
other shape, budget, context, state, signature, output and publication checks.
Neither the packet's profile nor any native digest is changed in the baseline.
This is conformance evidence for a possible successor, not migrated native data.

The override retains native dependency closure and exact evidence-ref membership.
It parses decision_at, system_asof, available_at and ingested_at with the pinned
ExactInstantProjection/1 converter. It compares exact coordinates, then compares
measurement_asof against the UTC civil day containing decision_at. The UTC day
is floor(coordinate/86400), in the converter's declared no-leap-second calendar.
No float, datetime precision fallback, inferred offset or date truncation.

Refusal precedence matches the old information method: evidence_not_in_view,
later_information, later_ingestion, future_measurement. Unsupported exact-time
encodings return an explicit exact_time_unsupported refusal; malformed fields
return exact_time_invalid. Both block this check, not the whole research plan.

Baseline comparator: all 271 retained regulatory exchange response checks under
both auditors. Derived cases use a minimal root -> evidence closure and explicit
view. The root is a repinned native AverageAssets record drawn from capital.final;
evidence and view are repinned after each change. The native shape checker checks
all three. This directly tests the information submethod, not a complete derived
regulatory request. Keep that scope in every result.

Primary pass criterion: retained responses agree; manual derived cases retain
membership, ingestion, measurement and exact-time outcomes. Later submicrosecond
evidence must refuse even when the old parser accepts it. Offsets normalizing
across UTC midnight must use the UTC measurement day. Superseded evidence in the
closure remains subject to checks. Missing actual timestamps or source authority
are not repaired by arithmetic. Counts are explanatory, all admission flags false.
