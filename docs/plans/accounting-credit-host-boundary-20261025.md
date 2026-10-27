# Audit exact credit amounts at the company-book boundary

25 October 2026. S2-S5; MC08/10-13/16-18/24-28/32-35.
Baseline: accepted CreditLinkedSchedule/1 and unchanged CompanyBook/1,
CompanyBookTransition/1-2, MethodMonetaryEffects/1 and CompanyBookReports/1.

Question: which exact retained credit amounts can the existing host represent,
and what additional semantics are required for the remaining amounts? The
measurement layer alone cannot authorize account mapping, fiscal interpretation,
cash classification or posting. Forecast evaluation remains deferred.

Skeptical audit passes for a read-only boundary diagnostic. Test actual host
validation, not a string search alone. Native CU is not a three-letter host
currency code; any illustrative CU-to-XCU mapping must be explicit, one-to-one
and context-bound. Allowance has a credit balance represented by minus L; it
is a contra asset, not a liability or an independent cash amount. Profit is
minus signed interest, impairment and catchup postings. Write-off changes
gross and allowance without creating cash. Original event dates must survive.

Primary criterion: inventory every monetary field and journal entry for all
nine exact schedules, certify rational projection where available, show actual
host rejection of non-rational expression wires, and specify the missing
boundaries with their tests. Preserve complete native result and root identity.
No rounding, arbitrary endpoint, balance plug or general inverse is permitted.
Acceptance of rational values is type evidence only, not an admitted book.

Defaults/assumptions: the retained book's exact rational type and limits are the
comparator, not defaults to overwrite. A single-root optional reference can
test selected credit journals plus unrelated rational balances; it would not
handle general multi-rate/multi-contract companies. Rates, expected schedules
and historical rule premises stay supplied assumptions. A cumulative interval
covering all native dates does not establish annual completeness.

1. Recompute and bind nine exact schedules; count monetary projections and
   non-rational fields, preserving first counterexamples.
2. Call existing monetary/book validators with projected rationals and linked
   expressions, keeping candidate books separate from native evidence.
3. Compare a rational-only adapter, an optional exact single-root book, and
   quantization. Specify context, account classes, root equality, explicit
   refusal of ordering, fiscal periods, complements and reporting dependencies.
4. Write the next implementation plan with a bounded evidence contract; update
   master controls after the diagnostic and continue feasible work.

Vetoes: changed locked inputs, expression mistaken for a rational, lost native
identities, false inequality/order decisions, implicit rounding or inferred
accounting authority. These trigger repair before dependent acceptance.
Successful type checks and case counts are explanatory, not compliance.
Artifact: data/accounting-master/credit-host-boundary-20261025/.
All53 obligations/6 interactions/46 operations remain; S1-S5 partial, S6 held,
S7/E3 deferred. No installation, workers, commit, GPU, fees or outreach.
