# Grouped row query contract and pre-run audit

26 October 2026. Implements the grouped-query plan for MC20/24/25/28/33/34.
The protected baseline is NestedMapProjection/1; the independent comparator
scans original fixture dictionaries and converts dates and rational values
directly with Python date and Fraction. It receives no candidate rows.

The skeptical audit passes for this bounded question: projection membership
and current-claim ownership cannot stand in for historical term applicability.
Count covers the exact declared parent group. Match returns all matching
indices; greatest returns all tied maxima among eligible indices. Both retain
an explicit ambiguous result instead of selecting the first inserted row.
Candidate indices retain supplied insertion order. Selected values and source
lineage are returned only for one winner. No sorting, floating point, implicit
unit conversion or financial validation occurs.

The query names its context, parent key, escaped parent path and child-map path.
All must agree. A group absent from a complete supplied population is invalid;
a present empty group counts as zero. Selection on an empty group returns none
when allow_empty is true and invalid otherwise. A missing declared input is
invalid. An explicit unknown input is unresolved, even on an empty group.
Partial or unknown populations are unresolved. Greatest without an upper bound
uses explicit null; a missing upper_bound field does not mean unbounded.
Inclusive/exclusive flags are booleans. Bounds and match inputs carry exact
declared types, including rational dimensions, scale and context.

The call binds the query and expected projection inputs, including source
order. Every evaluation recomputes the projection; no caller-provided rows
are accepted. Native term/lifecycle/builder callbacks are disabled in checks.

| Choice | Provenance and status | Failure risk | Early diagnostic |
|---|---|---|---|
| Two-level typed projection | Checked predecessor, reused baseline | Prior row error propagates | Recheck source hashes and compare selected full original rows |
| Date and exact rational ordering | Planned bounded subset | Unit or date conversion mismatch | Wrong type/context/scale and rational-order controls |
| Exact single parent | Native obligation audit | Repeated local IDs cross claims | Distinct Unicode parent with reused child ID |
| 256 predecessor rows/groups | Compatibility bound, not a product default | Silent truncation | Predecessor 256/257 evidence stays locked |
| Unknown and tie distinctions | Explicit design choice | Empty or tie becomes success | Direct status and no-selected-row assertions |

Primary pass criterion is complete query outcome agreement, including rows,
lineage, all candidate/winner indices, counts and reasons. Invalid identities,
mutations, changed frozen bytes, false completeness or wrong outcomes veto
promotion. A comparator or implementation defect triggers repair and a new
run; it does not reject the research direction. Counts/timing are explanatory
only. This is deterministic conformance, with no stochastic ranking.

Pre-mortem: a passing query could still be used as a false proof of a financial
rule. The next phase must specify guarded composition, especially empty or
ambiguous selected-row reads. This phase grants no execution permission, real
company completeness, accounting authority or full term-validator replacement.
Run manifest and complete result pairs preserve evidence. No manuscript pointer
is advanced until a coherent increment is integrated and reviewed.
