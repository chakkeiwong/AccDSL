# PerformingEIRSchedule/1 and POCIDatedSchedule/1

Read-only documentary exchanges; conditional synthetic inputs. Full examples
are authored-cases.json and attempt-01/exchanges.json. Source, plan and authored
targets are bound by input-lock.json; calculator bytes are captured per attempt.
These new profiles do not change frozen POCIAnnualTerminal/1.

Top-level keys are exactly wire, operation, context, opening_cash, acquisition,
numerical and events. Operation is report. Context exactly names entity, book,
currency, unit, rule, contract and calendar. All strings are nonempty; unit is
currency units, rule EU2023/1803-original-IFRS9, calendar
ACT/365F-annual-compound. Events repeat the same context. Amounts and rates are
canonical reduced rational strings (no decimal or binary float inputs); dates
are canonical ISO dates. Unknown supplied numbers/findings are unresolved.

Numerical has scale12–24 decimal-grid digits, max_width in(0,1/1000] currency
units and initial_pv_tolerance exactly0. Every reported monetary interval stores
lower, upper, width and whether its endpoints coincide. Each fractional factor
is enclosed by integer-power inequalities; every monetary width must fit the
caller-supplied maximum. There is no default hidden tolerance. At most64 dated
cash amounts,128 events and7305 days are admitted; rational encodings are at
most80 characters with absolute value≤10^12. These limits bound the calculator,
not the economic domain. The financial rate lies in(−1,10].

Acquisition exactly supplies date, price, cost, fee_received, rate, contract,
expected and findings. Initial carrying is price+cost−fee_received>0 and cannot
exceed opening cash. Contract and expected are maps from future dates to
nonnegative rational receipts. Initial expected receipts cannot exceed contract
amounts at a date. Performing expected receipts equal its contractual estimate.
The original rate must discount the complete initial expected schedule exactly
to initial carrying. Fractional accrual dates are supported; an irrational root
not established by the exact initial identity is outside financial admission.

Common supplied findings admit amortised cost, integral-cash classification,
complete cash/terms, information view, no modification/FX/tax, and no initial
write-off requirement. POCI separately requires classification at origin and
price equal to fair value. Performing separately requires performing origin
and an independent zero-credit-loss assessment. Neither is inferred numerically.
Integral costs and fees are separate cash origins, even though the opening
journal records their combined asset amount. Opening cash is initial equity.

Each event exactly has id, operation, date, information_date, context and
findings plus its operation fields. IDs are unique, cannot equal acquisition
or end in _accrual. Dates cannot go backward. Information must be available
between acquisition and the event; no expected positive receipt can be skipped.
Findings admit the information view, complete intervening cash, unchanged terms,
no earlier required write-off during accrual, and no required write-off left
unhandled after the event. Unknown/false findings refuse atomically.

Before the event, accrue G and signed L by F=(1+r)^(actual days/365), recognizing
interest (G−L)(F−1). Accrual never resets the original rate. Operations:

- advance: report the accrued state; no positive receipt may remain due that day.
- credit_revision (POCI only): fields expected and writeoff. Set N to original-
  rate PV, recognize its change as impairment and set L=G−N, without flooring L.
  Writeoff exactly has fraction, portion_id, no_reasonable_recovery and
  portion_expected_cash. Fraction0 has the explicit null finding/id and zero
  cash pattern. A positive fraction≤1 identifies an unrecoverable proportional
  whole-claim portion with zero expected cash; the supplied proportional gross
  allocation is W=fraction×G. Remove W from G and L together, retain removed
  contractual cash, and verify every remaining expectation against surviving
  contract. A fraction1 first measures N to0 and then fully derecognizes.
- estimate_revision (performing only): field expected. Under the supplied
  unchanged-terms finding, replace the estimated contractual receipt schedule
  for an existing prepayment option; no maturity extension. Adjust G to its
  original-rate PV with a separate B5.4.6 catch-up origin and profit. This is
  not a modification, credit revision or evidence of a real prepayment right.
- collect: fields amount and close. Confirmed cash must equal that day's complete
  expectation and not exceed remaining contract. Remove the dated expectation,
  reduce gross and increase cash. Retain any uncollected contractual balance.
  At the last receipt close must be true; remove residual G/L together after
  confirming net0. No event follows financial derecognition. Unexpected cash
  first requires an admitted revision/assessment; no silent loss/gain is added.

Independent financial identities: direct PV of remaining complete expectations
equals N; G equals initial carrying compounded to the date plus each dated
gross origin compounded from its own date. Origins include negative cash and
write-offs, non-credit catch-ups and terminal allowance clearing. Cash+N equals
opening capital plus interest, impairment and catch-up profit. Interval overlap
checks support the analytic identities but do not prove general conformance.
Journal entries are bounded values linked by the same mathematical identities;
independent endpoint rounding is not an exact journal posting policy.

Success returns conditional_complete, stages, closing, original cash and gross
origins, factor bounds, removed/uncollected contracts and proposed journals;
posts=false and mutations=[]. Refusal returns no closing/stages/journals/cash
or mutation. Unknown inputs/source are unresolved; unsupported scope/finding or
numeric budget is unsupported; contradictions and changed bytes are rejected.
General malformed-input completeness is not asserted.

The separate solve_rate utility brackets positive future-receipt EIRs with
certified endpoint PV signs and a requested rate width. Signed cash-flow root
ambiguity is refused. Its bracket may support later rate-interval methods; it
is not a rounded rate accepted by these financial profiles. Floating rates,
general modifications, staging, forecast estimation, arbitrary write-off
allocation, post-write-off recoveries, FX/tax, portfolios and general root-
uncertainty propagation remain separate obligations.
