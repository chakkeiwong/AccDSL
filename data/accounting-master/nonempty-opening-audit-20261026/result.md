# A carried book needs claim validation, not an empty-map exception

26 October 2026. MC01/09/17/24/25/28/33/34; S2/S3/S4. Four exact
carried openings from the retained successful programs have one or three live
claims, receivables of 20 or 39, unchanged identities, and no current-period
flows. Their full state invariants and opening reports pass. Ten complete
continuation commands reproduce the original suffix requests, transitions,
reports, current/opening states, failures and unexecuted suffixes. Trace indices
are rebased to the new command list; no financial payload is changed.

The old opening template rejects these valid carried states at empty_claims.
Removing only that diagnostic stage next fails claim_total, whose predicate
requires receivables to be zero. Removing both lets the remaining structural,
role/cost/policy and report conditions pass. These diagnostic templates are not
promoted. Five corrupt states also pass those remaining checks: a wrong claim
total, negative remaining amount, missing sale identity, future issue date and
inconsistent overdue amount. The full invariant rejects all five.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Unsupported conclusion |
|---|---|---|---|---|---|
| Design a separately selected complete-claims opening contract | Four exact carried states and ten complete continuations pass; two empty-specific checks isolated | Five corrupt states prove that structural checks alone are insufficient | Completeness is known only for supplied synthetic internal state; no actual-source history proof | Reuse remaining opening checks plus the exact full selected invariant and bind that admission to execution | General opening acceptance, arbitrary invariant safety, issuer completeness or accounting compliance |

Evidence: 76 assertions, ten protected files; native lifecycle and operating
builder disabled. No saved code or opening contract changed. The result
identifies a scope limit in the empty-opening target, not a failure of the
retained carry or simulation. A candidate that omits the full invariant is
wrong for the stated complete-claims target. Implement its separate successor
under a reviewed plan and preserve all empty-opening evidence.
