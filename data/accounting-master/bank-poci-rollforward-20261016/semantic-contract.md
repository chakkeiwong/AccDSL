# POCIAnnualTerminal/1

This read-only documentary exchange supports one fixed terminal claim with
integer annual-anniversary periods. Complete examples are in
`attempt-02/exchanges.json`; protected source/fixture identities are in
`input-lock-v2.json`. The original lock and attempt-01 remain preserved;
`admission-repair.md` explains the tighter write-off admission.
Canonical reduced rational strings encode all amounts/rates.
Missing values are unresolved; they are not zero.

Top-level fields are exactly `wire`, `operation`, `context`, `opening_cash`,
`acquisition`, `events`. Wire is `POCIAnnualTerminal/1`, operation `report`.
Context has entity, book, currency, unit, rule, contract and calendar. Nonempty
strings are required; unit is `currency units`, calendar `annual-anniversary`,
rule `EU2023/1803-original-POCI`. Every event repeats that exact context.

Acquisition has date, price, contractual_receipt, expected_receipt,
credit_adjusted_rate, term_years and findings. Dates are canonical ISO days,
term_years a positive integer excluding booleans. Annual anniversary dates must
exist. Price/contract are positive; initial expectation is positive and does not
exceed the contract. Rate r is greater than−1; zero and negative rates are
supported. Price must exactly equal expected_receipt/(1+r)^term_years.
No approximation or implicit root rounding is admitted.

Acquisition findings independently admit POCI on initial recognition,
amortised-cost classification, price equal to fair value, no integral
fees/costs, complete expected cash, contract terms and no modification/FX/tax/
other cash. High risk, discount and numerical consistency cannot supply these
findings. Purchase debits the asset and credits cash; initial subsequent-change
loss allowance is zero. Opening cash is also initial equity capital.

Acquisition, each advance and each credit revision additionally require
`no_full_or_partial_writeoff_required`. This is a separate supplied finding
about the carried state, including the interval covered by an advance; it is
never inferred from a positive expected receipt. False findings require a
different, earlier write-off transition and are unsupported here; unknown
findings are unresolved. Terminal collection uses its separate final recovery
assessment. No routine can establish the truth of these synthetic findings.

Each event has id, operation, date, context and findings. IDs are unique,
nonempty and cannot be `acquisition` or end in `_measure` (reserved for the
terminal measurement trace). Supported operations:

- `advance` has no extra fields. Date is exactly the next anniversary, at
  most maturity. Findings admit the information view, unchanged credit
  assessment and no interim cash/modification. Accrete before-allowance carrying
  G by rG; accrue signed allowance L by rL; recognize interest r(G−L).
- `revise_credit` adds expected_receipt, credit_improved and information_date.
  Date is the current anniversary; information is available between acquisition
  and that date. Findings admit the credit cash forecast and unchanged terms.
  New net carrying is PV(expected receipt) at original r; recognize its change
  as impairment and set L=G−N. The Boolean credit-improved finding is retained
  in the request; it does not change the POCI origin or rate. Unknown state
  refuses. A zero forecast before maturity needs an earlier write-off method
  and is unsupported here. No positive allowance floor is applied.
- `collect_close` adds cash and information_date, and is allowed only at
  maturity. Cash is confirmed and lies between zero and the contractual claim.
  Findings admit no reasonable further recovery and complete contractual
  population. First remeasure net asset to that known receipt, recording the
  final impairment change as trace `id_measure`. Then collect cash and clear
  gross asset and signed allowance atomically. Preserve contract minus cash as
  uncollected contractual amount; legal release remains `not_assessed`.

For active periods, G=P(1+r)^t, N=Et/(1+r)^(T−t), and
L=[(C−Et)−(C−E0)]/(1+r)^(T−t). The implementation checks these identities,
but verification also compares to independently authored stage/journal targets.
The scalar expectation is a supplied forecast, with no inferred probability law.
No event can reset the rate, change the contract or post a caller-supplied
allowance. No event is accepted after collection/financial derecognition.

Success has `conditional_complete`, the context/origins, original credit-adjusted
rate, initial credit shortfall PV and zero initial loss allowance, final
financial state, contract shortfall and explicit legal/calibration/tax limits.
Stages retain gross/allowance/net carrying, cumulative interest and impairment,
cash/profit/equity and POCI origin. Journals and cash origins are proposals
only; posts is false and mutations empty. The source/fixture lock is checked
on each call. The run manifest binds calculator bytes.

Refusal returns no report, trace, journal, cash flow or mutation. Unknown
findings/amounts and missing source bytes are unresolved. False admission,
different methods/calendar/rule, nonpositive discount base, early collection
or early zero-recovery continuation and insufficient funding are unsupported.
Contradictory structure, contexts, dates, amounts or changed bytes reject.
The 71 adverse examples are preserved with reasons; universal malformed-input
coverage and independent implementation conformance are not claimed.

Intermediate payments, fractional periods/day-counts, multi-date forecasts,
modifications, non-credit estimate changes, fees, FX, tax, portfolios and later
recoveries after write-off remain separate. This historical source profile
does not establish present-law or actual-company applicability.
