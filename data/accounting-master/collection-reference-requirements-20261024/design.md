# Finite collection prerequisites before ordered state effects

24 October 2026. The inspected retained return validator has distinct snapshot
checks (duplicate identities, component references, opening acquisition dates,
nondecreasing event dates and half-open period membership) and an ordered
known-lot/sold-lot loop. The latter changes the identity state after each event.
Native invariant/propose/apply additionally govern balances, disposed stock,
lifetime event IDs and recomputed proposals. These are not interchangeable.
The composed company profile repeats identity/capability membership checks;
the inspected portable authoring adapter supplies typed references and byte
selection, not a general collection prerequisite evaluator. This is a scoped
reuse audit, not proof of repository-wide absence.

MethodCollections/1 is a separate selected-prerequisite definition, not an
automatic MethodRequirements version upgrade. It declares global inputs,
collections with complete field types/roles/source descriptions, and a closed
list of unique, references, ordered or each constraints. Each uses a preserved
MethodRequirements/3 definition with explicit row/global input mapping and
exact type and role agreement. No callbacks or arbitrary supplied code run.
Reference comparison requires exact type/context equality; ordered comparisons
are limited to dates and rational values with matching type within a field.

Values have separate globals and collections. A collection is explicitly
complete with rows, or partial with rows and a nonempty reason. Partial rows
are observed members in their supplied relative order; additional members may
exist between them. An absent collection means partial with no observed rows
and the reason missing_collection. Missing row/global fields are unknown;
unexpected collections, fields or malformed tagged values are invalid. IDs
are not inferred, deduplicated or sorted. Unknown scalar values retain reasons.

For uniqueness, a known duplicate is false even if other fields or membership
are unknown. Otherwise incomplete coverage or unknown keys leaves the condition
unknown. A complete empty list is vacuously unique. For ordered dates/amounts,
a reversal in the known subsequence is false even across unknown values. With
no reversal, unknown values or incomplete coverage keep the result unknown.
This rule uses the explicit relative-order meaning of partial rows.

For references, each known source key must resolve to exactly one target key.
Two known matches are false; zero matches is false only when the target is
complete and all its keys known. One known match remains unresolved if unknown
target keys or incomplete membership could add another match. Unknown source
keys remain unresolved. A complete empty source list is vacuously satisfied.
Target key uniqueness beyond referenced keys requires a separate unique rule.

Each evaluates every observed row through the preserved guarded evaluator,
including structural checking of inactive branches. A known invalid/unsupported
row remains visible even if another row or collection membership is unresolved.
The empty complete collection satisfies the universal condition, while an empty
partial collection is unresolved. Required-known rules remain in the row template.
Per-row original results and indexed row/global bindings remain in the output;
no inferred raw-source binding or accounting admission is claimed.

Summary precedence is invalid, unsupported, unresolved, then selected collection
requirements satisfied. All findings are retained. Every result leaves executed,
method_eligible, source_admission and accounting_admission false. Original
definition and values hashes accompany results. Raw record binding and versioned
text for this separate profile are future work, not silently inherited success.

Engineering limits: inherited 1,000,000-byte canonical input bounds; at most
256 observed rows across collections, 128 constraints, and 65,536 counted
expanded row-template nodes. These are explicit defensive implementation choices,
not economic limits. Boundary tests must show refusal, and future scale changes
need their own evidence. Exact types/scalars and guards reuse frozen v1/v2/v3.

The comparator uses full native structural validation only on a valid retained
record and mutations isolated to selected snapshot conditions. Ordered creation,
single complete settlement, sale-before-existence, whole-lot double sale, monetary
state effects, source-pointer semantics and full record shape remain residual
conditions. A selected pass does not claim native validator equivalence.

Primary acceptance is independent expectations and exact selected comparator
outcomes, with unchanged upstream hashes. Counts and source inventories are
explanatory. Candidate failures trigger repair; no current finding supports a
global continuation veto. No stochastic or forecasting comparison is performed.
