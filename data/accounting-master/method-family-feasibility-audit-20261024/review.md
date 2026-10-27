# Method-family feasibility and remaining phase gaps

24 October 2026. Version3.66 is 451 pages, not_ready. Source inspection covers
the selected settlement/sale definitions, exact known-value monetary evaluator,
typed return transition, affine history, attachment and strict authoring. It does
not re-audit all domain methods or establish authority for a financial treatment.

The settlement definition computes refund n*p, handling n*h, carrying amount
min(n*(c-d),nrv), and a difference of prior recovery/refund balances. If every
operand is unknown, the products are genuinely nonlinear. With explicitly fixed
unit refund, cost, deterioration and handling amounts, these products become
affine and the minimum becomes piecewise affine. The sale expression is affine
in proceeds and carrying cost. The existing known-value evaluator already checks
types and exact arithmetic; that is the comparator for a family extension.

The bounded probes pass 21 checks. The current solver rejects unknown-by-unknown
products and arithmetic If expressions as unsupported. Encoding one minimum as a
Boolean disjunction creates four comparison predicates and 81 sign cells; a
one-cell budget leaves 80 unvisited. This is a structural result for that formula,
not a performance ranking. Explicit disjoint arms (left <= right; right < left)
each remain a linear conjunction. Exact cases below, at and above the tie replay
correctly, and the arms are exhaustive and disjoint by an exact logical check.

The next substantive layer is a restricted piecewise-affine family compiler for
existing typed method expressions. It must preserve both arms, complete inputs,
domains, requested measurements and unresolved obligations. A point witness must
not stand in for the family. Reject products of two unresolved symbolic operands
without substituting a convenient price. Explicitly fixed domains may become exact
constants, with their defining domains retained. Resource stops preserve unvisited
branches. No new nonlinear solver or default policy is selected.

Typed measurement attachment also remains open, but another attachment adapter
would not address the existing method's minimum or unknown-input arithmetic. The
method-family compiler supplies a distinct prerequisite for richer reconstruction.
Its later connection to typed histories, candidate generation and source admission
will require separate checked composition; the next plan does not claim that work.

| Phase | Current scope | Remaining work |
|---|---|---|
| S1 research | Retained survey and exact selected-method inspection | Gentry derivation/version, Francis/Rowell text, matched ACTUS and new method-specific primary evidence when consequential |
| S2 architecture | Typed unknown histories and preserved full-family conjunction | Method-family conditions, source admission, candidate generation and cross-layer composition |
| S3 DSL | Five-profile strict authoring and typed affine state constraints | Piecewise method expressions next; unknown products, general contracts, typed measurement attachment and wider sectors remain |
| S4 conformance | Typed-state counterexamples and 94 targeted authoring/regression methods | Exact piecewise family versus known evaluator; whole real-company history and independent implementation remain |
| S5 manuscript | Version3.66 and bounded final rendered review | Integrate subsequent substantive results; whole-document/independent/domain/human acceptance |
| S6 production | Reference code only | Held |
| S7 prediction | Earlier study choices preserved | Deferred |

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Compile an exact restricted piecewise method family | Operator audit and exact discriminating probes establish the missing interface and viable linear representation | No input corruption or target mismatch; unsupported nonlinear product is expected | Branch growth, global resource accounting and future native/state composition | Implement separately audited bounded compiler with exact witness/evaluator replay | General nonlinear solver, complete native method or accounting eligibility |
