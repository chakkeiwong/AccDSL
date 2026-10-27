# Exact bank profile: ownership and migration audit

26 October 2026. MC05/19/20/24/25/33/34. The next unit adopts the checked
information-time rule under a separately identified documentary profile.
No original schema, packet, receipt or reference evaluator is changed.

## Ownership inventory and skeptical audit

The retained bank auditor has three operations: regulatory assessment, finite
conditional-loss query and policy description. information checks the full
Evidence closure for membership, availability, ingestion and measurement date.
expected_capital separately compares assessment date with UTC decision date;
expected_loss compares vintage/origin with UTC decision date. expected_policy
reuses loss calculation and information. Those are the only timestamp consumers
in the inspected auditor; accounting event and period fields are civil dates.
All must retain explicit exact-time parsing. No unbounded datetime fallback.

The original schema fixes Profile.profile_id to BankAssessment/1. Changing only
the name in a request would therefore be invalid. The successor uses
BankAssessmentExactTime/1 and a distinct schema identity for Profile and all
definitions whose exact typed references transitively depend on Profile:
OperationSignature, OperationRequest, OperationResult, TransportObservation,
QueryPublicationReceipt, Domain and Region. Other body definitions retain
their exact schema IDs and meaning. SchemaLock retains its shape but has new
content binding the complete successor schema and semantic contract bytes.

The successor auditor validates that explicit schema/contract lock, profile
and supported operation list before evaluating any request. It also checks
profile identity before replay lookup, so an old cached request cannot bypass
the selected successor. Same-profile exact replay still precedes freshness and
head checks. The frozen old auditor retains its original behavior; it is not
retroactively hardened or called a successor.

Migration copies only complete selected publication closures. It replaces
profile, signature, dependent schema and request identities, regenerates exact
submission bytes and authors a new expected response. Old query receipts and
query-index entries remain unchanged. The successor uses a distinct workspace
identity, making this new query publication explicit. Financial record schema
IDs, original sources, views, evidence and accounting heads remain unchanged
when their semantics are unchanged. Changed timestamps require a separate,
explicitly repinned derived input closure.

For ordinary cases the expected output is copied from the frozen complete
publication; only genuinely changed references are substituted. All quantities,
unknowns, diagnostic codes, coverage and obligations remain comparable. The
new publication can coexist with old immutable queries but changes no account,
journal or unrelated owner. This is a bounded profile-specific conversion,
not a general automatic financial migration or actual company history.

## Evidence contract

Compare every retained positive publication, spanning all three operation
families and partial/undefined outcomes. Check successor replay, explicit
cross-profile refusal, schema/contract/decoder binding, exact late-information
and ingestion cases in all families, offset equivalence and full financial
output preservation. Full request packages must revalidate from saved data.
Test bad/missing heads, false publication and identity conflicts as controls.

Pass requires entire response/world correspondence after the declared identity
conversion, not merely matching a ratio. Hard vetoes are mutated predecessors,
unowned timestamp comparison, incomplete schema rebind, changed numerical or
unknown status, old-receipt relabelling or cross-profile replay. Counts are
explanatory. All source/accounting/forecast/product admission flags remain false.
The strongest alternative is a new wrapper that only renames the old profile;
paired later submicrosecond cases must disprove that explanation.

No stochastic inference or regulatory-source update occurs. The old frozen
prudential rules and source caveats remain. The smallest new code is a pinned
auditor subclass plus a finite closure migrator, not a service or dispatcher.
