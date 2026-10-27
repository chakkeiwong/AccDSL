# Complete supplied claims at an opening boundary

The audited plan is docs/plans/accounting-complete-claims-opening-20261026.md.
The target is a complete synthetic internal book at a new reporting period,
including claims issued earlier. It is not a disclosure reconstruction.

CompleteClaimsOpening/1 contains the selected empty template, its digest,
the selected state invariant and digest, excluded stages [empty_claims,
claim_total], and residual scope. A separate call binds the complete input,
serialization order, contract and completeness declaration. Completeness has
profile SuppliedClaimPopulation/1, status complete, claim-map pointer /claims,
book digest and explicit provenance. Other statuses remain unresolved and do
not become complete because the map contains rows. This declaration expresses
the supplied internal scope; it never certifies actual-source completeness.

Trusted selection is an explicit argument, bound into the call and program
selection. It pins the original empty-template and full invariant identities.
The adapter verifies the original empty_claims stage is equals at
[opening,memory,claims] with the empty dictionary, and that claim_total is the
audited zero-receivable predicate. The exact selected template digest also
protects every other stage. The adapter derives the structural template by
excluding only those two stages, then reuses admission.assess. The subsequent
guards.assess checks the full invariant on the unchanged opening.

Structural/report validation precedes the invariant in this new profile; this
is explicit new failure order. A successful result contains both full results,
original/derived template identities and the exact invariant/completeness
selection. The full report remains required; a mid-period snapshot does not
become an opening merely by passing the claim invariant.

The new bound wrapper admits this same input, checks shared facts, profiles,
roles, unit-cost pointer, policy, complete rules, invariant and projected
commands using the existing binding contract's checks, then runs the unchanged
composer. To avoid reproducing those checks, reuse the original binding with
the derived structural template and a corresponding explicit internal
selection only after the full invariant admission passes. Retain that
delegated result verbatim. Do not monkeypatch semantic owners or accept a
caller-provided success flag. Failures before delegation execute no command.

All numeric/state conditions remain original evaluators. The trusted selection
is a finite reviewed configuration, not proof that arbitrary edited predicates
implement financial policy. Source authoring and broader opening histories
remain follow-on work; no old frozen source is modified.
