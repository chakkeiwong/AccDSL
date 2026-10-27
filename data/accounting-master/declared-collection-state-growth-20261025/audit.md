# Typed claim creation: structural audit before implementation

25 October 2026. MC02/05/11/13/15/17/24–28/34/35; S2–S4. The immediate
question is whether one newly created claim can be typed and inserted without
weakening the existing book's exact scalar types or monetary atomicity.

CompanyBookTransition/1 validates that memory_types exactly equals the current
scalar leaf set. Its memory_contract accepts only fixed scalar replacements.
MethodMemoryEffects/1 already validates closed map schemas and atomically stages
insert, append and replacement, including dynamic keys treated as single tokens.
Its existing tests cover collision, malformed paths and late schema failure.
NativeCompanySale/1 imports a fixed record of existing lots and therefore does
not remove the new-identity barrier. These exact inspected contracts establish
the need for a successor; no repository-wide absence is claimed.

The safer first increment is a separately typed, finite map declaration that can
derive an exact leaf map from a current value. It must not alter the frozen book,
change method dispatch, or perform a journal yet. Compare every derived type to
independent expectations and the existing book's declared scalar types. An empty
map represents no items, not hidden zero claims. Explicit field types and a
closed item schema allow future populated states to remain checkable.

Alternative: a separate receivable component with its own balances. That would
need an atomic merge contract with the common monetary book and might duplicate
the obligation already enforced by the book. Investigate it only if the typed
map cannot preserve exact scalar checking without broad engine changes. Do not
turn this provisional choice into a permanent architecture decision.

Evidence contract: explicit record, scalar and finite map type constructors;
exact schema correspondence and leaf derivation; escaped keys; duplicate/unknown
field and context/type failures; bounded population. New declared types must
match a real current value before a later successor can stage it. Promotion
vetoes are schema bypass, conflicting leaf types, missing value coverage or
context mismatch. Counts and successful validation are not evidence of atomic
financial execution. The subsequent credit-sale/collection integration remains
required before this work can address the whole lifecycle.

Defaults: scalar types reuse the existing exact kind/context/dimension checks;
maps use explicit maximum items no greater than the inherited node budget;
fixed records require all fields; arbitrary regexes, coercion, wildcard matching
and remote schemas are excluded. These are bounded engineering choices. The
early check is independent empty/populated/nested map examples, then one actual
declared company memory. No numerical experiment, accounting authority change,
probability or forecasting claim is involved. Frozen predecessors are preserved.
