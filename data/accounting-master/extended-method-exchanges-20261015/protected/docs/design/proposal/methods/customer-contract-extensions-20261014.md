# Customer advances and product returns

Proposed method supplement, 14 October 2026. MC02/04/07/13–16/19/20/28/30.
This extends the restricted R01–R03 revenue method without changing its valid
results. It uses the existing AccountingEventBasis, authorization, proposal,
EconomicDelta and atomic commit boundary. It does not implement an engine.

## Authority, ownership and applicability

Support is the retained AASB15 compilation no. 8, compilation date 31 December
2022, amendments through 15 December 2022, prepared 6 April 2023 and registered
as F2023C00402 on 3 May 2023. Its stated annual-period interval is
2023-01-01 <= start < 2026-07-01. The compilation table identifies the 2014
standard and included amendments through AASB2022-8; it does not establish a
complete current amendment census. The case assumes an Australian for-profit
entity in calendar 2024/2025, within AASB15.5–10 and the contract criteria of
paragraph 9. No current ASC/ASBE applicability or treatment difference follows.

Paragraphs 31–38 supply performance/control conditions, 47–59 and B23 the
transaction-price estimation and reversal constraint, 105–109 the separation
of contract balances and unconditional rights, and B20–B27 the return method.
Economic facts, cost, price, entitlement estimates and expected recovery costs
remain separately admitted measurements. An expected return count is a chosen
conditional input, not a calibrated probability supplied by the standard.

The corporate contract owns the state below, per contract/entity/book/currency.
The evidence/time layer supplies immutable source and measurement views; the
event scheduler supplies actual performance, billing and settlement dates.
An unknown required fact produces unresolved with no posting; a known false
required condition produces ineligible. A different transaction, such as a
defective-product warranty, produces outside_scope for the returns method.
No property of a balanced journal overrides these findings.

## A. An advance applied once to a later bill

Scope: one fixed-price performance obligation; no refunds, cancellations,
financing, credit loss, sales taxes, modifications or cross-contract offsets.
Advances in this method precede any performance or unconditional billing;
multiple such advances may occur up to the fixed price. Later receipts settle
an admitted receivable. More general mid-contract advances need a separately
specified extension, not an accidental use of these preconditions.

Retain cumulative earned revenue R, gross billed consideration G, cash advances
A, advances applied to those gross bills K and subsequent receivable cash
collections C. G includes the already paid portion shown as a credit on the
bill; it is not the new unconditional receivable. The remaining credit is
U=A−K. Every allocation binds an advance_id and invoice_id; an amount cannot
be reused. The method preserves their residual balances, not just totals.

Let T=G+A−K. Then

    AR=G−K−C; CA=max(R−T,0); CL=max(T−R,0); received_cash=A+C.

Admissible states require 0<=K<=min(A,G), 0<=C<=G−K and 0<=R,T<=price,
with CA and CL netted only within this same contract under paragraph 105.
The derived control is received_cash+AR+CA−CL=R: since
CA−CL=R−T, the left side is A+C+G−K−C+R−(G+A−K)=R.
This is a consequence of the explicitly restricted facts, not a universal
revenue formula or an offset rule for different customers.

1. `advance_received`: amount a>0, payment identity/date, contract and cash
   evidence; require R=G=C=K=0 and A+a<=price. Debit cash a, credit CL a;
   A increases by a. No revenue or receivable is created.
2. `performance_recognised`: increment r>0, obligation/control or over-time
   progress evidence, admitted price and estimate version. Require R+r<=price.
   Debit existing CL by min(r,CL), debit CA for the remainder, credit revenue r;
   R increases by r. Collection or billing cannot supply missing performance.
3. `gross_bill_issued`: gross g>0, itemized advance credits k, invoice identity,
   due date and unconditional-right evidence for n=g−k. Require
   0<=k<=min(g,U), unused credits and T+n<=price. Debit AR n, credit CA by
   min(n,CA) and CL for the remainder. G increases g and K increases k.
   The applied advance has already affected CL/CA through T; it is not released
   again merely because the invoice displays it. Zero monetary lines are omitted.
4. `receivable_settled`: cash c>0 with settlement identity and right allocation,
   c<=AR. Debit cash c, credit AR c; C increases c. An overpayment is outside
   this operation and requires its own admitted event.

For price100, first receive30: cash30/CL30. Then earn60: debit CL30 and CA30,
credit revenue60. A gross invoice80 applies the30 advance and creates a new
unconditional right50: debit AR50, credit CA30 and CL20. Collect20: cash50,
AR30, CA0, CL20 and revenue60. Net assets60 equal revenue60 for this revenue
slice. Billing before performance gives the same endpoint: invoice creates
AR50 and adds CL50 to the existing30; performance then releases60 of CL80.
Intermediate balances differ and the actual event order remains preserved.

Completing performance to100 releases CL20 and creates CA20. The final bill20
creates AR20 and releases CA20. Collect the remaining50: total cash100 and
all AR/CA/CL zero. No estimate of income tax or cost of service is supplied by
this revenue-only slice. Its pretax revenue contribution must be joined to
those separate methods before constructing complete company statements.

Wrong but balanced alternatives include crediting revenue on the initial30
payment and creating AR80 after accepting the30 prepayment. The first violates
performance conditions; the second creates an extra30 right. Applying the same
credit to the final bill is rejected before state mutation. A gross invoice
that is entirely covered by a valid advance has n=0: account balances and
profit/cash remain unchanged, but G and K and the credit allocations change.

For that state-only case, the proposed authored package uses a tagged
JournalProposal payload with `effect_kind=state_only`, `lines=[]`, and an
EconomicDelta with the nonzero allocation changes and zero account deltas.
Authorization recomputes n=0 and every credit balance. The schema rejects an
empty line set for any nonzero monetary delta. The same four-Ref commit,
expected head, business identity/replay and atomic journal/state/receipt rules
apply. This is a proposed package schema under the existing schema lock; the
native acquisition schema with nonempty lines is unchanged and cannot be used
to submit this case. An unsupported package returns UNSUPPORTED_PROFILE_OPERATION
without committing. P17-10 still owes the complete positive/replay/conflict
exchange for this new profile before interface acceptance.

## B. A delivered product can still carry a refund obligation

Scope: transferred, homogeneous non-defective goods with a contractual cash
refund right; immediate cash sale; one price and former unit carrying cost;
no exchanges, additional promises, financing, tax or credit risk. B26 excludes
same-type/quality/condition/price exchanges; B27 sends defective-product
replacement to warranty guidance. Control/performance and contract criteria
must pass before this method is eligible. Under B22 the stand-ready promise
to accept returns is not an additional performance obligation.

Retain cohort and item identities, units transferred N, unit price p, prior
carrying cost c, gross cash consideration Np, cumulative actual refunded units
j, estimated remaining returns q, estimate view/date and constraint findings,
refund liability L, recovery asset H, recovered inventory, recovery-cost and
deterioration inputs, and the legal return-window end. The refund expectation
and reversal-constraint assessment use only information admitted at that date;
later actual returns cannot be silently substituted into the original view.

For initial q expected returned units, the admitted transaction price in this
simple example is (N−q)p, L=qp. With no expected recovery costs or deterioration,
H=qc. More generally, apply B25's former carrying amount less expected recovery
costs and potential value decreases. A missing recovery estimate does not
default to zero. The example is limited to nonnegative supported recoverable
amounts; any separate obligation beyond that requires its own treatment.

At transfer debit cash Np, credit revenue (N−q)p and refund liability qp.
Remove inventory Nc by debiting COGS Nc−H and the recovery asset H. Present H
separately from L. At each reporting date recompute L and H for remaining
returns: an increase in L reduces revenue; an increase in H reduces COGS.
Decreases reverse those entries. B23–B25 require updates; a revision is not
automatically a correction of the original source view.

On actual accepted return, bind its units and refund to the cohort; update the
estimate first if necessary. Debit refund liability and credit cash for the
admitted refund. Debit recovered inventory at the admitted recoverable carrying
amount and credit the recovery asset. Track return processing costs and value
changes under their own specified measurement rather than making recovered
inventory equal cash refunded. At expiry, no remaining refund/recovery right
is removed until the contractual/legal facts and unresolved claims support it.

Take a synthetic cohort of100 units, price10 and cost6. Opening inventory600
is financed by opening equity600; there are no other pretax balances. Transfer
and cash receipt occur in2024. The initially admitted estimate is10 returns,
with the paragraph53 method and paragraph56 constraint stipulated satisfied.
Recognize revenue900, refund liability100, COGS540 and recovery asset60; cash
is1000. Profit360 gives equity960, and assets1060 equal liability100+equity960.
At the 2024 close, new admitted evidence changes expected returns to12. Debit
revenue20/credit refund liability20; debit recovery asset12/credit COGS12.
Closing revenue880, COGS528, profit352; cash1000, recovery asset72, refund
liability120 and equity952. The gross asset/liability balances remain visible.

In2025 the return period ends with eight actual accepted units, refunded80,
and no remaining right or unresolved claim under the stipulated legal facts.
Immediately before final settlement, revise the total refund/recovery estimate
to8: debit refund liability40/credit revenue40 and debit COGS24/credit recovery
asset24. Debit refund liability80/credit cash80 and inventory48/credit recovery
asset48. The year2025 profit contribution is16; closing cash920+inventory48
equals equity968, with no remaining refund/recovery balance. Lifetime revenue
920 less COGS552 gives368, matching the change from opening equity600.

The direct operating cash flows are1000 and−80. Indirectly,2024 profit352 plus
inventory decrease600 minus recovery-asset increase72 plus refund-liability
increase120 gives1000. In2025, profit16 minus inventory increase48 plus recovery
asset decrease72 minus refund-liability decrease120 gives−80. There is no
investing/financing flow in this slice, no OCI and no owner movement after the
opening balance. These are pretax contributions, not complete after-tax company
statements or an assertion that tax is zero.

If expected recovery costs are1 per unit and deterioration0.5 for the12-unit
estimate, H=12(6−1−0.5)=54, not72. COGS is546 and pretax profit334; the refund
liability remains120 because that expectation has not changed. This sensitivity
does not pay those costs early or invent their later actual values. Recognizing
gross revenue1000/COGS600 without L/H balances arithmetically but is wrong for
the stipulated refund/recovery facts. Netting H72 against L120 hides the gross
asset and liability required by B25. A missing estimate or control finding
blocks posting; a warranty exchange is outside this method.

The weakest evidence for any actual-company application is the contract,
entitlement/reversal assessment and recovery measurement, not the arithmetic.
The method remains conditional until those facts are admitted. Missing tax,
warranty, modification and other operation methods stay in the P17-04 matrix.
