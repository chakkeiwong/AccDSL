# Audit declarative invariants for nested claim terms

26 October 2026. MC20/24/25/28/33/34; S2–S4. Existing ReceivableTermHistory/1
already preserves prospective amendments, historical assessment bases, collection
and carry. Existing ReceivableTermText/1 authors commands but delegates state
validation and algorithms to native Python. The current general invariant
source binds top-level maps and scalar row paths; it cannot automatically be
assumed to express each claim's nested terms and assessments.

Question: what exact state relationships and binding operations must be exposed
before term-history validation can be written and independently selected through
the declarative invariant path? Audit the existing validator, frozen evidence,
schemas, collection constraints and guarded expression language. Do not rewrite
the financial operation or infer actual contract facts.

Skeptical audit: old overdue amounts refer to the terms applicable at their
assessment date, not the current due date. Flattening histories without claim
ownership can create false cross-claim matches. Lexically sorting keys is not
chronological order. Current-term membership, predecessor chains, unique
effective dates, greatest applicable term, seen event identity and latest
assessment summary each need explicit handling. A wrapper calling the native
validator would not expose those rules as source.

Evidence contract: preserve the exact frozen states for two charts, map every
native validation obligation to current declarative support or a concrete gap,
and test the smallest proposed row projection on real retained shapes. Compare
row ownership, typed values, order and source pointers exactly. Counts only
describe scope. Complete state/result equality, refusal preservation and empty-
map validation would be required for a later replacement; the audit alone
does not claim those. Missing general primitive support triggers a separate
reviewed implementation plan, not a silent financial special case.

Assumptions: maps are supplied internal collections from synthetic fixtures;
no actual-history completeness. Native behavior is the comparator, not automatic
accounting authority. A sorted projection is only a representation proposal;
its stable tie policy must not hide equal dates that should refuse. Preserve
source/evidence hashes and all current semantic owners. CPU-only bounded local
work; no agents, commits, installations, GPU, fees, outreach, publication or E3.

Save obligation mapping, source lock, shape probes and result under
data/accounting-master/nested-term-invariant-audit-20261026/. Continue a justified
small implementation only after its dependency and evidence audit passes.
