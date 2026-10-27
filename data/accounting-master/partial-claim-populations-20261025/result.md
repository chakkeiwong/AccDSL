# Unknown claims are not an empty executable population

25 October 2026. Eight focused tests, 23 collection/type regressions and exact
replay pass. Three retained-source views and three constructed population
examples are preserved with 211 locked files. The combined view retains all
54 original balance constraints and every partial-state dependency, attaching
four receivable population views without changing the original state.

The implementation reuses MethodCollections/1. Its partial collection may
contain no observed rows while the total number of actual claims is unknown.
The retained annual and interim trade and vendor-receivable observations have
that status. Their displayed amounts, source references, dates, precision and
unresolved mappings survive. Claim count, gross remainder and due terms remain
explicitly unknown. The adapter accepts no supplied population that could
silently promote these retained disclosures to complete claim schedules.

Separate constructed complete collections demonstrate the distinction. An
explicitly complete empty collection has count zero and gross total zero.
Two uniquely identified rows with remaining amounts 20 and 40 have count two
and total 60, conditional on their supplied completeness. Partial rows cannot
produce that total; an unknown amount preserves a known count but leaves the
total unresolved. Duplicate identities and negative remaining balances refuse.
Known due terms describe contractual dates, not actual or predicted receipts.

An optional source-rounding assumption carries through unchanged. Under the
explicit nearest/ties-away hypothesis, the displayed annual net receivable
33,410 constrains the same consolidated measurement to [33,409.5, 33,410.5).
It does not identify a gross claim total or any member. No balancing residual,
allowance, currency allocation or legal-book mapping is manufactured.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Retain partial population view using existing interfaces | Exact partial-state preservation, unknown/empty discrimination and independently checked counts/sums pass | No checked engineering veto; unresolved membership still vetoes exact population queries | Actual members and measurement relationships remain unidentified | Integrate source reading, correction and partial-population semantics into the governing manuscript | Actual source admission, full history feasibility, complete schedules, settlement behavior or accounting compliance |

The strongest alternative is that a second population model was unnecessary.
The implementation therefore delegates population status and uniqueness to the
existing collection evaluator and preserves the existing partial-state output
verbatim. Its addition is a small source-bound attachment and explicit query
behavior. Known identities and an externally supported completeness statement
would change dependent queries; a displayed aggregate alone does not.

All 53 language obligations, 6 interactions and 46 operations remain. These
checks advance MC02/04/05/08/11/13/16/24–28/34/35 within their stated scope and
close no whole requirement. S1–S5 partial, S6 held, S7 deferred.
