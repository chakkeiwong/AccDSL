# Joint relations over source measurements

This draft connects existing Apple statement-relation ledgers to the checked
partial-state request. It preserves all 69 annual and 74 interim ledger entries
and their surrounding metadata. Nine balance-sheet relations per source bind
to the current snapshot subset. Each other relation remains visible with its
original record, diagnostic role and reason for deferral. No missing ledger row
or explanatory residual is silently discarded.

The baseline request contains explicit term coefficients, target observation,
source-ledger path, row pointer, digest and the complete partial-state request.
The evaluator checks exact binding against the retained ledgers and snapshot
observations. Each selected relation uses one source group, date, perimeter,
basis, unit and measurement kind. The target's coefficient is minus one in
the residual. Compute from source amounts rather than copying the retained
ledger's computed/residual fields. A literal dash or missing value stays
unresolved; it is never coerced to zero.

Displayed residual zero is an arithmetic observation at displayed precision.
It does not prove an exact underlying equality. A caller may separately propose
the measurement identity represented by a relation; that hypothesis is named,
source-bound and not source-admitted. If all nonzero operands have conditional
rounding intervals, derive the residual interval by exact linear interval
arithmetic. Combine repeated references to the same observation before doing
so: x-x has residual exactly zero, not the difference of independent draws.

For each nonzero coefficient a, multiply both endpoints by a and reverse them
when a is negative, carrying endpoint inclusivity with the endpoint. Sum lower
and upper contributions. An extremal sum is included only when every nonzero
contribution includes that extreme. An empty normalized coefficient list is
the exact interval [0,0]. Zero containment is computed with the correct open
endpoints. Under an authored identity hypothesis, this can reject that local
identity's compatibility with the proposed intervals. Otherwise it is only
an explanatory residual range. Neither result solves the combined system or
constructs legal books, economic memory or an actual company history.

Audit finding from the old ledgers: the annual term-debt diagnostic's preserved
description says it used a source dash convention. The new baseline does not
adopt that convention: this diagnostic is outside the balance-only subset and
stays deferred with its original record. The debt-issuance observation still
retains its reported dash. Similarly, the five interim cross-period identities
have different record shapes and must be accounted for explicitly, not assumed
to have terms and target fields.

Evidence contract: primary pass is complete ledger preservation, exact source
and context binding, independently recomputed displayed arithmetic, correct
signed/dependent interval arithmetic and rejection of false claims. Baselines
are the original source readings and relation ledgers. Integrity or context
errors veto acceptance; unsupported/missing operands motivate the next scope
extension. Counts are explanatory. A local interval test does not establish
joint feasibility, underlying accounting truth, complete reconstruction,
forecast validity or production readiness.

Implementation is a finite typed reference with no new solver, source admission
or changes to predecessor code. The current text frontend still stops at the
partial-state record; relation text is an open language task. Preserve exact
request/result identities and accept results only by full recomputation.
Governing plan: docs/plans/accounting-source-relations-20261024.md.
