# Author bounded state invariants from explicit source

26 October 2026. MC02/08/15/20/24/25/33/34; S2/S3/S4. Work directory:
data/accounting-master/invariant-source-authoring-20261026/.

Question: can a company-program author express the current typed state
invariant, including row rules and totals, without importing the complete
algorithm as an opaque hashed resource? Baseline is BookStateInvariant/1 and
AuthoredCompanyText/1, their two retained company programs and full results.
No general accounting-policy language or new invariant evaluator is implied.

Before implementation, inspect the selected invariant, collection/totals
definitions, guarded-expression grammar, common-program compiler and source
limits. Record a skeptical audit and exact grammar/ownership decision. Reject
a design that only pastes a complete invariant JSON blob under a new heading,
silently changes rule order or treats successful parsing as accounting evidence.
Reuse the existing guarded-expression parser and typed evaluators wherever
their exact contracts fit. Keep source provenance and semantic identity distinct.

The bounded source must expose global/collection declarations, state pointers,
uniqueness/references/ordered constraints where supported, row predicates,
total bindings and aggregate predicates. All types, contexts, provenance,
unknown behaviour and residual prerequisites remain explicit. Lower to the
unchanged typed invariant; no Python callbacks or alternate arithmetic engine.
Compose it into a separately named common-program text successor, preserving
the original parser and examples. A user-authored rule variant must change
behaviour under the same saved state, not merely change a content hash.

Primary criteria: exact typed invariant equality for both charts; all 22
complete command outcomes equal; all 16 original inconsistent states still
refuse; a meaningful directly edited predicate changes the intended outcome;
malformed/duplicate/unbound/ill-typed source refuses with exact UTF-8 locations.
Retain partial/unknown reasons and source/resource limits. Check failed prefixes
and full resulting states, not just summary status or a selected balance.

Vetoes: changed predecessor bytes, lost unknowns/context, silently omitted rule,
false invariant success, changed native financial result, unbounded source or
runtime-code injection. Counts are coverage diagnostics only. A failing case
triggers local repair under this scope; it does not reject language authoring.
No stochastic ranking, real-company completeness or accounting approval follows.

Record source locks, exact commands/environment, complete comparisons and
reconstructible source examples. Integrate coherent results only after the
bounded criteria pass; refresh the next dependency before proceeding.
No installs, agents, commits, GPU, outreach, fees, publication or forecasting.
