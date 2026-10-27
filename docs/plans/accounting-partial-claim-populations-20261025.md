# Unidentified claim populations over retained partial state

25 October 2026. S2–S4; MC02/04/05/08/11/13/16/24–28/34/35.

Question: how can a financial-statement DSL retain a disclosed receivable
measurement while its individual claim population is unidentified? The latest
real-source comparison establishes that the new lifecycle cannot consume the
retained captions. This is an implementation requirement, not a request to
invent invoices or drop the aggregate evidence.

Skeptical audit before implementation: reuse SourceConstrainedCompanyStateDraft/1
and the existing explicit unknown conventions. Search current collection and
partial-state interfaces before proposing another schema. A Python empty map
currently means an exactly empty population to the lifecycle; it must never
represent unidentified members. A net receivable amount cannot be constrained
to the sum of gross identified claims without a separately supported allowance,
offset, currency, perimeter and measurement mapping. Display-only values do not
become exact through subtraction. A residual computed by balancing would hide
the missing relationship rather than establish it.

The comparator is the retained partial-state result and its two fiscal periods,
plus the lifecycle's known empty opening. Specify a small attached population
view, source measurement references, membership knowledge and query behavior.
Keep it outside executable CompanyBook memory until full state and method
premises are supplied. The view must retain the original observations and
obligations; it should support viewing disclosed measurements while returning
an explicit unresolved result for claim count, exact gross total, collection
schedule or account posting. It must distinguish unknown, explicitly empty and
identified-complete populations without silently selecting a population.

Pass criteria: source-bound behavior on retained annual/interim views, exact
preservation of the partial-state output, separate deterministic unknown/empty
examples, and adverse tests for invented completeness, net-to-gross equality,
lost obligations, false zeros and source substitution. Existing intervals may
only carry through with their separately recorded rounding hypothesis. Claim
truth, complete feasible histories, accounting admission and actual execution
remain unestablished. Counts and successful serialization are explanatory.

Record assumption/default audit and exact command before nontrivial checks.
Use deterministic CPU tests; preserve code, contracts, result and read-only
replay under data/accounting-master/partial-claim-populations-20261025/.
Missing facts reject unsupported queries, not the research direction. Continue
to integrate the checked source-contract and partial-population explanation
into the governing design once the distinction is settled.
