# MixedContractBilling/1

A read-only exact reference composition of the existing mixed amendment and
CustomerCycle. `reference.py` defines closed request/event fields; examples
and exact outputs are retained in `attempt-01/exchanges.json`. This is no
new runtime service or implicit migration of CorporateComponents/5.

The request has wire, operation=`report`, context, annual_start, as_of,
opening_cash, terms, findings and events. Context binds Australian for-profit
entity, separate book, CU/unit, contract mixed-A and AASB15 compilation8.
Calendar-year starts must lie within the source's annual-start interval
[2023-01-01,2026-07-01); report and events lie in that same calendar year.
All examples use2024. Every event repeats context, has a unique nonempty ID,
economic date and information_date between annual opening and the event.
Chronology is nondecreasing and never exceeds as_of. A cutoff request supplies
only the information/event prefix; later terms are not inferred from later
events. No restatement or bitemporal query engine is claimed.

Amounts are canonical nonnegative rational strings; positive fields and integer
visit counts have stricter checks. Unknown numeric inputs are unresolved;
malformed encodings/IDs/fields are rejected. Unknown required findings are
unresolved and false scope findings unsupported. Missing finding fields are a
shape error. Global findings admit paragraph9 eligibility, over-time
construction, distinct visits, allocations, expected payment-to-transfer
intervals at most one year, election of paragraph63 and absence of tax, FX,
variable consideration, refunds and onerous loss. Every measurement additionally
requires an explicit zero-impairment assessment and continuing contract facts.
Neither admission nor zero impairment is derived by the calculator.

Terms give construction price P, expected construction cost E, equal visit
price v and total visits N. Opening cash is the entire opening capital. There
is no inventory, payable or financing asset in this paid-cost example.

* `advance`: distinct advance_id and positive amount. Records cash and the
  source of available credit; does not earn revenue.
* `perform`: incremental construction_cash_cost, visits and visit_cash_cost.
  Faithful cost progress, transferred visits and immediate expense eligibility
  are admitted. Cumulative construction revenue is P times cumulative cost/E;
  visits add v times their transferred count. Cost cannot exceed E, delivered
  visits cannot exceed N, and cash must fund the payment. The method does not
  infer borrowing or admit deferred cost assets. A cost with no visit is outside
  this immediate visit-expense path.
* `amend`: one approved mixed, nonseparate modification, with admitted allocations
  and continuing faithful progress/timing. new_construction_price,
  new_expected_cost and new_visits_total replace the remaining terms; v is
  unchanged. Construction must be partly complete and remain incomplete under
  the revised cost; some visits must remain. Recompute cumulative construction
  revenue, posting only the difference. Previously earned visits stay fixed.
  Cash/advances are separate events. Repeated modifications retain their
  existing independent methods; this profile does not silently import them.
* `invoice`: a distinct invoice_id, positive gross amount, unconditional-right
  finding and list of credit_id/contract/advance_id/amount records. An advance
  may be split across invoices, but credits cannot exceed its unused amount or
  the invoice gross. Credit IDs cannot repeat and all records belong to the
  same contract. This supports distinct credits from one advance and rejects
  reusing an exhausted advance under a different credit ID.
* `collect`: a distinct settlement_id, known invoice_id and positive amount
  no greater than its remaining net right. Cash collection does not earn revenue.

At each event sum advances A, gross bills G, credits K, later collections C and
earned revenue R. AR=G-K-C; paid-or-due T=G+A-K; CA=max(R-T,0);
CL=max(T-R,0). G and T may not exceed the admitted total contract price.
These are conservative limits for this fixed-price nonrefundable case, not a
general prohibition on other contracts' refundable excess cash.
The full book has cash=opening capital+A+C-paid costs, debit AR/CA/expense,
credit CL/income/capital. Differences in these balances give each event journal.
Receivables remain separate from net contract presentation. Empty journals
are permitted when a prepaid invoice changes identities only.

The report retains all invoice, credit, advance and settlement origins, final
financial balances, OCI0, opening capital, performance/settlement states, and
gross operating cash legs. Direct operating cash A+C-cost equals profit minus
AR/CA increases plus CL increase. A report never posts. Any refusal returns no
partial trace, journal, cash flow or report, and does not mutate its request.
Missing source bytes are unresolved; changed source bytes reject the result.
The source lock and attempt snapshots preserve reproducibility.

Open wider obligations include other modification terms, nonzero impairment,
contract losses, cost assets, taxes, FX and company composition. They remain
named methods or joins in the finite residual queue. This example supplies
their shared billing distinction without closing those separate obligations.
