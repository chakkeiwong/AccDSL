# Ordered full-intent gate semantics

26 October 2026. The plan and its six flat-conjunction counterexamples establish
why the gate is sequential. The supplied template names context, operation,
complete input types and an ordered list of stages. Each stage contains one
existing MethodRequirements/3 manifest, an exact map from its input declarations
to typed sources and a caller-visible failure reason. No whole-method inference
or native callback is allowed.

The generic outer interface validates template/call identity, current typed book,
event shape/id/date, nondecreasing event date within the period, exact full event
input population and each type/value/provenance. It then returns unresolved with
the exact unknown input names if any are unknown. This is before stage execution.
Approval is the first supplied predicate for each retained contract. Remaining
stages retain the native order: sealed cursor, sale due/absence or collection
existence/customer; assessment cursor, interval/adjacency, period end.

Source kinds are closed: event_input; event_metadata(id/date); book_date;
period_end; memory_leaf with a fixed pointer; map_contains with a fixed declared
map pointer and named text event input; map_field using the same key and a
declared scalar field; and calendar_adjacent with named date sources. The map
must be a typed map, its row field a scalar with exact matching type. Membership
is computed from actual memory, never supplied as a caller finding. Lookup is
evaluated only in its ordered stage after existence has passed.

Calendar adjacency compares validated date ordinals: right-left=1. Both dates
are explicit; the primitive neither adds an assumed business day nor skips
holidays. Minimum and maximum dates cannot overflow because no date is created.
This matches the retained next-calendar-day relation, not a fiscal calendar.

Every stage and binding is validated before execution, including later stages
that would be skipped. Exact declaration/binding coverage and source type checks
must not depend on successful row lookup. Predicate compilation is delegated to
the existing guarded evaluator. At execution, process one stage at a time; stop
at its first non-satisfied result with the stage id and declared reason. A
no-active-requirements result is not success for this gate. Unknown from a typed
source remains unresolved. No later invalid premise outranks an earlier unknown
or unsupported result.

The template and call bind exact context, book, event and template digests.
Schema-registry and memory-definition digests are bound as well. Since the
native unknown-input list follows event-input insertion order while canonical
JSON hashes omit map order, the call also binds a separate input-order digest.
Selected-row sources name a preceding presence stage; compilation proves that
stage uses an unconditional membership predicate for precisely that map/key.
No mutation or posting occurs. The gate reports eligible only for this selected
finite contract; source/accounting admission and product readiness remain false.
The constructors subsequently emit requests and existing transition predicates
still control monetary execution. Full lifecycle state invariants remain separate
and unchanged. The exact evidence contract and repair triggers are in the plan.
