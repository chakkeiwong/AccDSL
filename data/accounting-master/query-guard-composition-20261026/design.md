# Query-to-guard binding semantics

The 18-case guard audit confirms that MethodRequirements/3 makes false-guard
requirements inactive; it does not evaluate their unknown bodies as true.
The distinct no_active_requirements result survives. A required_known input
still demands a known value even under an inactive guard. These checked
semantics are retained without changing the expression evaluator.

QueryGuardedInvariant/1 binds a finite map of reviewed grouped queries to an
explicit v3 manifest. The independent reviewed-selection digest covers the
entire declaration, including queries, ambiguity consequences and bindings.
Changing it requires an explicitly revised selection. Each call also binds
the book's serialized order, memory definition, schemas and per-query
population declarations. Queries are always recomputed from these inputs.

Count binds an exact dimensionless rational. A unique selected row supplies
has_row=true and selected_field values with exact source lineage. Allowed
none supplies has_row=false and unknown selected fields. Ambiguous or
unresolved queries supply unknown values; they can never imply false absence.
Ambiguity follows the explicit invalid/unresolved policy. Invalid queries
fail structurally before predicates; any unresolved query keeps the whole
result unresolved even if the v3 guard is inactive. An inactive rule over
allowed none remains a legitimate separate result; required_known or
allow_empty=false can demand the row when that is the declared requirement.

The pre-run audit finds no unresolved baseline mismatch for this finite
adapter. Primary evidence compares independent original-state query bindings
and full unchanged-v3 assessments. Query evidence and frozen hashes guard
the shared primitives; no scientific or financial validity follows from the
comparison. The 32-query limit is a compatibility bound with explicit
overflow refusal, not a promoted product restriction. Repeated projection
work is intentional for this bounded design probe, with no performance claim.
Dynamic parent/child template instantiation remains a separate dependency.
