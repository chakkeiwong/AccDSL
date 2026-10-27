# Claims and asset cohorts behind the same financial report

A company can report the same receivables and plant balances while retaining
different claims and different future depreciation charges. The current native
operation examples make both distinctions explicit. A construction procedure
that starts from financial totals must retain these alternatives until evidence
or a declared modeling assumption distinguishes them.

## Claims survive the year boundary

The three-year example starts with two trade claims and creates twelve more
through purchases and deliveries. Each collection or supplier payment names
the claim it settles. A claim retains its ledger, amount recognised, lifetime
settlements and outstanding amount. If claim c has recognised amount R_c and
settlements A_jc through operation j, its outstanding amount is

    O_c = R_c - sum_j A_jc.

The equality is accompanied by operational conditions: the claim must already
exist, the payment must address the correct ledger, each allocation must be
nonnegative, and it must not exceed the outstanding amount immediately before
that payment. A zero allocation still names and checks a claim. Removing its
endpoint would change the native program's behavior when the endpoint is absent
or belongs to the wrong ledger.

These amounts also have a time scale. The annual executor starts a retained
claim with its opening outstanding balance and counts that year's settlements.
The closing-memory adapter restores the original recognised amount and adds
earlier settlements. The relationship inspector checks both records. Reusing
an annual recognised amount as the lifetime amount would lose part of the
history even when the closing receivable balance remained correct.

In the checked alternative, one unit of a collection moves from one new claim
to another. All journals, closing balances and financial statements remain
unchanged. The two outstanding claim balances change from 102/5 each to 97/5
and 107/5. Aggregate receivables therefore cannot identify the claim allocation
in this supplied family. A later claim-specific collection can distinguish it.

## A policy changes the continuation it must support

The existing settlement policy applies a named collection fraction and exact
installment shares to designated delivery claims. Its saved parent is the
second-year price-revision path, whose invoices are16*12=192 per claim. Under
the supplied9/10 fraction and two equal installments, each collection allocates
192*(9/10)*(1/2)=432/5. The prior fixed allocation was396/5. Four allocations
therefore increase cash by4*(432/5-396/5)=144/5 while decreasing receivables
by the same amount.

Changing this fraction is not enough to define a complete behavioral policy.
With full collection in year two, the retained third-year collection still
addresses the now-settled claims. The native executor refuses the over-settlement
and retains the earlier complete years. To continue that altered scenario, the
modeler must supply a justified contingent collection rule or revise the later
authored actions. The checker must not silently erase the failed payment or
invent that response.

Exact parent identity matters here. The earlier unmodified example has a price
of11 and an invoice of176. The saved policy rejects that different parent.
The first connection attempt selected it incorrectly; the repaired connection
loads and verifies the recorded price-revision path and complete saved result.
This prevents arithmetic from one scenario being attached to another.

## Asset service dates and useful lives determine future expense

The annual depreciation method reads each asset's cost C_i, useful life L_i,
accumulated depreciation D_i and service date s_i. For annual opening date t,
the supplied full-year rule is

    charge_i(t) = 0                                      if s_i > t,
                  min(C_i/L_i, C_i-D_i)                  if s_i <= t;
    D_i(next) = D_i + charge_i(t).

The service test determines whether an asset contributes this year. The
remaining-cost term prevents depreciation beyond cost. An asset's zero charge
therefore need not mean it can be removed: it may enter service later, or its
fully depreciated record may still be needed by a historical query. The current
annual profile explicitly refuses mid-year proration and does not implement
disposals, impairment, revaluation or differences between tax and book basis.

In the original path, annual depreciation is13,15,16 and closing net plant is
98,93,87. One asset added at the end of year one costs10 and enters service at
the start of year two. Replacing its ten-year life with five years leaves every
first-year report line unchanged, then increases the next two annual expenses
by one each. Delaying service instead removes its year-two charge. Cost and
accumulated depreciation alone cannot reproduce all these continuations.

## Responsibilities of the construction procedure

The implemented entrypoint accepts one hash-bound native operation path and
its opening source. The native executor first decides whether the opening
can execute. If required opening values are unknown, the entrypoint preserves
that unresolved result and its obligations, with no population inspection. A
null inspection does not mean the company has no claims or assets. The
lower-level claim and cohort inspectors require an executable opening; a
guarded entrypoint is necessary when that premise has not yet been established.

For an executable opening, the native executor decides which operations run
and which are refused. The inspectors then preserve the declared event
population, executed claim and asset relations, all intermediate memories and
the complete native result. Operation identities include the year because
local operation names repeat. Claim and asset identities persist across years.

For each executed trade operation, the claim inspector retains the creation
or settlement relation, amount, input location and relevant claim guards. For
each executed asset addition or depreciation operation, the cohort inspector
retains the asset identity, method inputs, service/cap reads and resulting
accumulation. Annual populations must agree with native closing memory. An
incomplete path retains its refusal and unexecuted suffix; a successful local
transformation is not substituted for a complete path result.

These are defined parts of the construction interface, not all its required
inputs. The synthetic claim schema contains no counterparty or legal-instrument
identity. The asset schema contains no title or physical location. The new
records mark those facts unknown. A real filing's debt or plant total does not
fill them. Industry-specific operations, source authority, actor receipt and
population completeness require their own supported definitions and evidence.

The guarded entrypoint is
data/accounting-master/company-state-population-admission-20261028/admission.py.
The lower-level implementation references are
data/accounting-master/company-state-relationship-dependencies-20261028/relationships.py
and company-state-asset-cohort-dependencies-20261028/cohorts.py under
data/accounting-master. Their result notes preserve exact comparisons, full
outputs, failed attempts, source hashes and remaining scope. The protected
manuscript has not been changed by this supplementary specification.
