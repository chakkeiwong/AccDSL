# Additive typed-map transition audit

25 October 2026; S2–S4, MC02/11/13/15/17/24–28/34/35.

The 13 foundation tests pass, including both actual collection openings and
insertion with the frozen memory stager. A material boundary is explicit:
the old schema subset cannot encode map capacity. Therefore a successful
schema-only stage is insufficient; the successor must derive and validate
the full declared types before and after staging, before returning an after-state.

Chosen bounded design: CompanyBookTransition/2 carries CompanyMemoryTypes/1
alongside the existing CompanyBook/1 state. The declaration's generated schema
and current leaves must exactly match the book. Existing book validation,
monetary derivation, requirement assessment and staging remain frozen imports.
Common request validation uses a copy with no memory operations; this copy is
never executed. Every original operation then receives the successor's own
static type check. The original method hash remains the request identity.

Allowed writes are scalar replacement and insertion of a complete typed map
value. Dynamic keys must come from text-typed input fields and are single path
tokens. Record replacement, append, deletion and silent type changes are
unsupported. Read templates transfer exact context, dimensions and scale;
literal constants are explicitly checked against their destination type.
Postconditions may bind existing leaves; binding a newly introduced identity
is a later authoring extension, not silently weakened validation.

All monetary effects and staged memory remain provisional until post-state
validation and postconditions pass. Failed staging, duplicate identity, capacity,
type or postcondition checks return no after-state and cannot mutate inputs.
Replay recomputes the entire proposal. This preserves in-memory atomicity;
durable storage, arbitrary lifecycle semantics and source/accounting admission
are outside this increment.

Acceptance: compare fixed replacements with the unchanged v1 engine on both
charts, exact new claim and journal values, escaped IDs, repeated creation,
type/dimension mismatches, capacity, unknown inputs and tampered proposals.
Test counts and balanced journals alone cannot establish receivable lifecycle
correctness. That requires the subsequent sale/collection/assessment/carry cases.
No benchmark, stochastic comparison or financial default changes are proposed.

Skeptical audit passes for this limited increment: the comparator is exact v1
behavior, no fictitious initial claims are introduced, capacity is checked
outside the schema, and the projection is validation-only. A bypass or changed
frozen source vetoes promotion and triggers repair. It does not cancel the
planned lifecycle integration.
