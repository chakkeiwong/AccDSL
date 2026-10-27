# Connect claim settlement and financing to the complete year

23 October 2026. S3/S4; MC13–18/24/26/28. Continue the authorised master
without promoting the provisional payment schema to production.

## Question and skeptical audit

Can the revised early-supplier-payment schedule reconcile the same opening
company to a complete year's income, balance sheet, cash flow and equity when
the bridging facility has explicit interest and repayment obligations? The
comparator is the retained Northstar stress7/stress9 annual projection at
floating shares 0, 1/2 and 1. The new case must account for financing costs;
simply inserting a draw to repair liquidity would compute the wrong year-end
cash and profit for an interest-bearing loan.

Audit passes for a deterministic documentary comparison with the assumptions
below. It does not select a credit model, establish issuer financing access or
prove a general event generator. All inputs are either retained amounts or
clearly authored scenario terms. Inspect the existing interest/tax/closing
journals and preserve them; derive a distinct successor schedule. Refuse
missing required terms, over-settlement and principal repayment beyond the
drawn amount before applying their proposed journals.

## Exact inputs and assumptions

- Reuse the original cash 74.6, opening receivables 35, payables 30, purchase
  170, sales 300, collections 280 and supplier payment 160. In the authored
  claim allocation, all 160 of supplier payment settles the current purchase,
  leaving current payables 10 and opening payables 30. Collections settle 10
  of opening receivables and 270 of current sales, leaving 25 plus 30. This
  allocation is consistent with the existing forecast's legacy collection and
  collection fraction, but is not recovered invoice evidence.
- Purchase occurs 2 January, delivery 3 January, draw and supplier payment
  4 January 2025, collections 5 January, principal and facility-interest
  payment 6 January, payroll 7 January, and the retained closing events on
  31 December. These are synthetic dates already used by the timing example,
  with a newly explicit draw repayment. No claim about actual issuer dates.
- Draw 85.4 on the existing draft's hypothetical eligible facility; repay
  exactly 85.4 after collection. There is no fee in this defined scenario.
  Interest is simple Actual/365 using calendar dates: principal times annual
  rate times two/365, excluding the draw date and including the repayment
  date. Intraday fractions are deliberately outside this contractual example.
- Use rate 5% as a named scenario hypothesis, borrowed from the existing
  fixed-rate example; also compute 0% and 7% as explicit controls. These are
  not estimated rates, a selected default or a comparison of stochastic arms.
- Follow the retained demonstration's interest-as-operating-cash and immediate
  tax expense/payment conventions. The new interest is deductible in this
  synthetic tax method at the retained 20% rate. No deferred tax, deduction
  cap or jurisdiction-specific compliance claim follows. Reject negative
  profit-before-tax in this profile instead of inventing a loss-tax method.

## Evidence contract

Primary criterion: all six retained rate/share cases remain reproduced before
extension; every funded path stays cash-feasible; identified claim totals
equal their control accounts after each affected event; closing balances,
income, cash flows and equity reconcile with financing costs and tax effects.
Compared with the original, profit, equity, operating cash and ending cash
decline by facility interest times (1 minus tax rate). Debt ends unchanged
because the new draw is repaid; gross financing inflow and repayment remain
separate even though they net to zero.

Vetoes: source mutation, unbalanced journal, negative prefix cash, failure to
close temporary accounts, mismatched claim/control totals, double revenue on
collection, missed loan interest/tax adjustment, or applying part of a refused
claim/principal settlement. Check counts are explanatory only. No forecast
accuracy, statistical ranking, real-company feasibility or product runtime
claim is permitted. A failure repairs this fixture and its stated design;
it is not evidence against simulator research generally.

Run the CPU-only exact checker under
data/accounting-master/funded-year-20261023/verify.py. It reads frozen source
bytes and writes only its own diagnostic records. Preserve the actual command,
environment, source hashes, elapsed time and complete derived event/journal
schedule. Result: data/accounting-master/funded-year-20261023/result.md.

Next: express these dated claims and contract terms through the proposed typed
records and a matched authoring subset, including unresolved input cases.
Full-company syntax and later-sector rules remain distinct open obligations.

## Next executed increment: explicit authoring inputs

The full-year diagnostic now passes. Its synthetic terms still live partly in
the checker, so it is not yet an authoring example. Define a separate closed
FundedYearInputsDraft/1 body for the projection reference, context, floating
share, claim allocations and dates, facility terms, draw/repayment dates,
explicit event order, tax assumption and declared source/assumption text.
Provide the same body as typed JSON and a restricted textual declaration.
The existing NorthstarDebt grammar and product frontend remain unchanged.

Skeptical audit: importing an annual projection is deliberate reuse of an
already specified example, not whole-company text coverage. No opaque host
function may supply a missing rate, date, facility, claim or tax rule. Every
authored field must lower to an explicit IR field; missing declarations must
reject, and unsupported unknown dates must remain an explicit unresolved input
rather than silently use the fixture date. The small parser is a documentary
conformance instrument, not a product compiler or a replacement for S6.

Primary criterion: independently authored text and typed JSON yield identical
closed bodies and match the retained full-year trace's principal, interest,
dates, claim/control totals and event order. Preserve the originating source
digest. Negative controls cover missing declarations, duplicate IDs, wrong
projection/context, invalid dates, ambiguous order and noncanonical rationals.
Malformed syntax is invalid; a supported explicit unknown is unresolved.
No claim about expressive completeness, parser performance or production
runtime follows. Store grammar, both inputs, checks and the exact execution
manifest under data/accounting-master/funded-authoring-20261023/.

## Connect authoring to documentary execution

The matched input checks pass, but their trace comparison does not execute the
authored body. Add a pure documentary executor taking that validated body and
the immutable imported projection. It must derive claim recognition/settlements,
new principal/interest events, tax and closing from those inputs. Do not copy
expected closing balances as computed results. Preserve both the existing
full-year diagnostic and production code.

Skeptical audit: equality between text and JSON is insufficient. Compare each
of the 18 independently retained full-year traces against this new input-driven
calculation, including every journal, final account, income, cash-flow and
equity result. In addition, put payroll before collection to force a known cash
shortfall; verify the refused event changes neither cash, expenses nor claim
state. Unknown dates must return unresolved before execution. Record gross
financing flows, conditional state and explicit noncommit status. A passing
bounded executor is evidence for this reference meaning, not a production
runtime, general-purpose solver, implemented posting API or completed mission.

## Integrate the checked successor meaning

The input-driven comparison passes 113 checks after a manifest-only import
repair. Preserve Version 3.49 and create Version 3.50 under
docs/design/proposal/manuscript-funded-simulator-20261023/. Integrate the claim
allocation, explicit facility decision, complete-year interest/tax consequence,
matched authoring and conditional execution into the language/execution and
portable-reference discussion. Explain the numeric example before its fields.
Retain the difference between a conditional reference path and a production
commit, and between a payable claim's partial settlement and the earlier
full-payment decision subprofile.

Skeptical audit passes for bounded integration: the independent full-year and
input-driven calculations agree, but no new whole-company completeness follows.
Preserve all prior source equations, citations, labels and qualifications;
verify source/PDF hashes, clean-build the successor and inspect changed rendered
pages and transitions. The current schema still imports the annual projection;
do not imply it supplies a full-company grammar. Independent implementability,
domain and human acceptance remain pending. No old controller execution or
release-hash rewrite is required.
