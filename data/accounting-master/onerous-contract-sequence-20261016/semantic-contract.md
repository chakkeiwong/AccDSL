# OnerousContractSequence/1

Read-only documentary measurement of one remaining point-in-time service and
its existing eligible contract-cost asset. Amounts are canonical nonnegative
rational strings; results may be signed. Examples are in
`attempt-01/exchanges.json`. Input/source identities are in `input-lock.json`.

The request contains exactly wire, operation, context, opening_date,
opening_cash, original_unamortized_cost, findings and events. Wire is
`OnerousContractSequence/1`, operation `report`. Context is the exact entity,
book, currency, unit, rule and contract mapping. Unit is currency units; the
rule is the historical `EU2023/1803-original-IFRS15-IAS37` profile. Every event
repeats the context. Opening equity equals supplied cash plus supplied
original unamortized cost; no hidden opening liability is admitted.

Global findings admit original cost eligibility, one remaining point-in-time
service, no prior service/amortization, no advances/receivables/tax/FX/
reimbursement, immaterial time value and an enforceable contract. This is not
a declaration that every contract's losses qualify for a provision. The
specific unavoidable obligation is calculated after the asset tests.

`assess` contains consideration, incremental_cash, allocated_direct_cash,
exit_compensation, information_date and findings. All events have unique
nonempty IDs, canonical dates, nondecreasing time and the same annual period.
Information lies between opening and assessment. Consideration is fixed across
reviews; changing price or credit proceeds needs a different method. Assessment
findings admit completed other-standard impairment, no further CGU loss,
complete disjoint direct costs, no future noncash costs, reliable best
estimates, collectible fixed consideration, available enforceable exit and
no other exit benefit/cost. No scalar amount can establish these findings.

Let B be consideration, D the two future cash cost components, A0 original
unamortized cost and A current carrying. Set Anew=min(A0,max(B−D,0)). Post
asset loss A−Anew, then set P=min(max(D+Anew−B,0),K), where K is exit
compensation. Post only the change from the prior provision. The no-service
scope makes A0 the reversal ceiling; it is not a general later amortization
ceiling. Other-asset/CGU outcomes are admitted separately, not calculated.

`fulfil` and `cancel` contain receipt, incremental_cash, allocated_direct_cash,
exit_compensation and unrelated_admin_cash. Findings admit confirmed same-
contract cash, complete performance or termination, no remaining obligations,
no alternative use of remaining contract cost and unrelated administration.
No second settlement or assessment after settlement is accepted.

Fulfillment requires receipt and each direct cost to match the latest assessed
amounts, with zero cancellation payment. A surprise needs an explicit preceding
review. It records revenue/receipt B; removes remaining asset A and pays D;
uses P against those contract expenditures, leaving expense D+A−P. Cancellation
requires zero performance receipt/cost and payment equal to the last K; it
expenses any remaining asset, pays K and uses P against that obligation.
Administration is paid/expensed separately and never uses P. Cash funding
before the same-date receipt must cover the cost and administration in the
conservative supported ordering; insufficient cash is unsupported rather than
an invented borrowing. The method does not select management's action.

Success returns the final pretax balances, trace, debit-positive journals and
separate gross cash origins, all with no mutation or posting. Every stage
checks book balance, net assets/equity and cash origins; independent verification
also compares frozen financial stages and final receipts/costs. Required missing
findings are unresolved, false findings unsupported, and invalid data rejected.
Any refusal returns no report/trace/journal/cash effect. Sources are verified
on every call; the run manifest binds the executed calculator/verifier.

The61 adverse requests cover meaningful missing/false findings, source/context/
time mismatch, wrong order, changed forecasts, funding and duplicate settlement.
This is not universal malformed-input coverage or a running service. Partial
service, variable/credit consideration, discounted obligations, other assets'
impairment and noncash allocations, tax, FX and general company joins remain
explicit separate methods. Human/domain acceptance remains pending.
