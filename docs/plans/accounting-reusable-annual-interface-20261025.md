# Audit a reusable multi-vintage annual interface

25 October 2026. S2–S5; MC05/11/13/16/24/26/28/35; G2/G4.

Question: what common state and operation contract can repeat across financial
periods without year-specific caller chains, lost settlements, renewed loss or
recognition capacity, or guessed fiscal completeness? Comparator: the checked
second boundary and period-aware continuation, retaining exact predecessor
history. The immediate deliverable is an implementation-governing contract and
discriminating reference cases, not a production controller or tax-law model.

Audit first: inspect the current and deferred assessment populations, first
assessment/reassessment assumptions, two-vintage constraints, reporting classes,
loss clocks and boundary checks. Distinguish reusable financial kernels from
hardcoded caller nesting. Record what can be reused unchanged and what needs a
new interface. Do not edit frozen predecessors.

Define a period book with immutable opening, complete financial state, stable
liability identities, archived period histories, current assessments, loss
state, recognition evidence, findings and explicit dependencies. Distinguish
assessment creation from replacement; older vintages cannot be overwritten.
Allocated payment uses only period-local settlements and actual shared cash.
New current assessment appends one stable identity; its replacement recomputes
cumulative obligation from the correct opening and retains payments. Deferred
measurement binds the freshly assessed state. Closing requires aligned clocks
and carries balances without renewing admission or capacity.

Specify input/output schemas, invalid/unresolved/unsupported/funding states,
prefix and pure-apply semantics, full-history access and finite replay limits.
Identify incomplete meaning explicitly; do not introduce generic dispatch that
accepts unsupported records merely because their totals balance.

Evidence contract: independent rational recurrences over at least three
liabilities and multiple periods, zero/fully settled histories, reassessment
after payment, loss expiry/usage, deferred-capacity renewal refusal, actual
cash shortage, repeated event identity and out-of-period events. Exact state,
journal, cash and report identities are primary. Changed sources, wrong
comparators, dropped history or unreviewed default behavior veto evidence.
Counts and runtime are explanatory. No forecast or standards-compliance claim.

First write the dependency audit and contract under
data/accounting-master/reusable-annual-interface-20261025/. Then choose the
smallest reference adapter that tests the unresolved interface, with focused
tests before widening to the next operation. Record results, refresh the active
checkpoint and continue independent ready work. S6 held; S7 deferred.
