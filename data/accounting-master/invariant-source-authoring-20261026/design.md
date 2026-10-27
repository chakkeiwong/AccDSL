# Bounded invariant source: audit and grammar decision

26 October 2026. MC02/08/15/20/24/25/33/34. The engineering question is whether
explicit source can reconstruct the existing complete typed invariant and
preserve program behaviour, while letting an author alter an actual rule.
The comparator is the retained BookStateInvariant/1 object and its unchanged
collection, totals, guarded requirement and program evaluators.

## Skeptical and assumption audit

The current common source exposes method algorithms but selects the whole
state invariant by hash. BookStateInvariant/1 binds exact typed book fields to
MethodCollections/1 and MethodCollectionTotals/1. Its finite operators already
cover uniqueness, order, references, per-row guarded predicates and exact sums.
A new evaluator would create an unnecessary comparator mismatch. Copying the
whole invariant JSON into a source token would leave the authoring gap intact.
The chosen frontend exposes each declaration and lowers to these existing
objects; it uses the original expression parser for every predicate.

The original source/resource limits are inherited engineering limits, not
evidence of usability or scale. Enforce the same byte, declaration, depth and
node bounds and test an oversized source early. Source spans bind exact UTF-8
bytes, including CRLF and non-ASCII strings; whitespace may alter source identity
without altering typed identity. Mutable state pointers remain explicit and are
checked by the unchanged binder against the supplied typed book, including empty
maps. Internal completeness remains distinct from actual-company completeness.

An explicit rule edit may legitimately weaken a selected invariant; this
language does not certify accounting policy. The meaningful variant changes a
retained false outcome to unsupported and must preserve the failed prefix and
the original reason. Unknown fields or incomplete collections stay unresolved.
Accepting a false predicate merely because parsing succeeds is a veto.

## Grammar and ownership

BookStateInvariantText/1 uses one declaration per line. The header identifies
the native invariant, totals and snapshot profiles and their method/version
names. A context declaration is followed by explicit global declarations and
state bindings. A collection names its memory-map pointer or seen-event source;
each field declares type, role, provenance and key/field/value binding.

Unique, ordered and references declarations preserve list order. An each block
declares the collection, a rules block and row/global bindings. A rules block
declares MethodRequirements/3, inputs, guarded predicates, required-known names,
capabilities and residual prerequisites. Predicate syntax is parsed by the
existing guarded-expression Reader; its final typed manifest is validated by
the retained compiler. No caller values, selected-result hashes or runtime
callbacks enter the block. The final aggregate rules block and total bindings
name the exact sums or global inputs. Snapshot, totals and invariant residuals
remain distinct lists. Every dictionary declaration rejects duplicate keys.

AuthoredCompanyText/2 replaces the old select_invariant line with a delimited
inline invariant source block. The adapter lowers it, constructs the exact
typed resource internally and then invokes the unchanged v1 compiler. That is
an implementation reuse boundary, not an author-supplied opaque algorithm.
All old source lines retain mappings to original byte spans; embedded rule
errors point inside their source block. The returned compiled program and
native execution result must equal the old typed program and result exactly.

## Evidence contract and stop rules

Pass requires both chart invariants exactly equal, all 22 full command results
equal, all 16 counterexamples refused with complete failed-prefix equality,
meaningful direct rule edits, partial/unknown preservation and precise errors
for malformed, duplicate, unbound and ill-typed declarations. Full source can
be reconstructed with only the remaining data resources; the complete invariant
resource is absent from supplied imports. Source counts are explanatory only.

Predecessor mutation, different financial outcomes, lost unknowns, source-limit
bypass or false invariant success veto acceptance and trigger repair. No
scientific ranking, real-source, accounting or production acceptance follows.
The strongest alternative explanation is cosmetic source around imported rules;
exact removal of the invariant resource and a consequential predicate edit
must rule it out. Proceed with this bounded frontend and saved comparisons.
