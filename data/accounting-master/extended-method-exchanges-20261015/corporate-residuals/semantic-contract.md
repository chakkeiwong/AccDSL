# CorporateResiduals/1 — finite documentary semantics

16 October 2026. Scope: MC02/04–07/11/13–20/24–28/30/32–35 and P17-04 residuals.
This separate namespace inherits no request admission from a predecessor.
Its examples are authored exchanges, not a running accounting service.
Historical EU sources, conditional findings and exact rational values apply
only to the stated examples. Actual facts, valuation, operative authority and
whole-company completion are not inferred. `tax_status` is component-scoped.

Signed journal amounts are debit-positive. Profit is minus the sum of signed
income accounts. Gross cash categories retain receipts and payments separately.
Each posting changes one tagged component plus its company-book balances.
The component cannot explain unrelated opening equity, cash or other components.
P5 must join components in one actual company rather than sum isolated reports.

## Recognition and calculation rules

**rcost.settle.** The return window is finally closed. Supplied facts give
returned units r, unit refund p, former cost c, actual deterioration d, and
selling-administration handling cash k per returned unit. Inventory is the
smaller of r(c−d) and supplied aggregate NRV. Opening refund L and recovery A
are fully released. Cash refund P=rp and handling K=rk remain separate inputs.
Debit refund L and inventory V; credit recovery A and cash P+K; credit revenue
L−P; debit cost of sales A−V and selling-cost expense K. The equation balances without expensing expected
handling costs a second time. An expired unused refund changes revenue; an
unused recovery changes cost of sales. Different actual and expected quantities
are allowed within original sold units. A still-open window, missing NRV,
missing settlement, or unclassified handling cannot use this finalisation rule.
Capitalisable recovery work requires another method; it is not expensed here.

**cgu.reverse.** Changed recoverable amount creates requested reversal up to
recoverable less current CGU carrying, including non-reversible goodwill.
Eligible asset capacities are min(no-impairment carrying, supplied individual
recoverable cap) less carrying, floored at zero. Allocate using original current
carrying weights, iteratively redistributing amounts blocked by caps among
remaining positive-weight assets. An all-zero eligible weight sum with a
positive proposed reversal is unresolved `zero_weight_allocation_unspecified`.
Neither equal weights nor capacities become an invented source rule. No reversal
of goodwill is admitted. **individual.reverse** is the separate cost-model
individual-asset route: min(recoverable, no-impairment carrying) less carrying,
floored at zero. Revaluation routing remains outside this finite method.

**lease.reduce.** Each surrendered right has traced attributable ROU and
liability amounts. Whole-right termination must remove both in full. Other
rights retain their own identities; an overall area/unit fraction is not an
allocation. Derecognition gain = removed liability minus removed ROU. Revised
remaining liability per right is sum(payment[t]/(1+revised_rate)^t), t=1..n,
for supplied equally spaced annual end payments. Adjust remaining ROU by the
change from liability after derecognition to revised liability. A negative
remaining ROU or non-annual/unknown allocation requires another method.
**lease.pay** covers a one-year annual payment from a just-measured opening
liability with no intervening accrual or modification: interest = rate×liability;
principal = amount−interest. Payment must not exceed liability+interest.
**lease.depreciate** uses a supplied, explicitly justified systematic allocation,
not an automatic fraction of cash payments. Principal cash is financing and
interest operating under the historical election. Values and period evidence
remain synthetic premises; no independent interest-rate valuation is claimed.

**cost.incur.** A single identified acquisition or fulfilment lot first checks
other-standard priority. Capitalise only incremental acquisition costs or
directly related costs creating resources for future performance, with supplied
recoverability; otherwise expense known ineligible/waste/past-service costs.
No one-year acquisition-cost expedient is selected. Cash equals invoiced cost
in these cases. **cost.amortize** allocates current and hypothetical unimpaired
carrying separately using delivered service units / remaining service units.
The equal-unit benefit pattern is an explicit supplied finding. **cost.impair**
uses max(0, credit-adjusted remaining consideration − remaining direct costs)
after other-standard impairment. **cost.reverse** needs changed circumstances
and is limited to hypothetical amortised carrying. A subsequent CGU review
remains a distinct required assessment; this component test cannot close it.

**distinct.modify/perform.** Prospective modification applies only when the
remaining and added goods are distinct but the separate-contract SSP condition
fails. Add agreed consideration and units to the remaining schedule, retaining
previous revenue. Delivery earns remaining consideration×units/remaining units.
Successive modifications repeat that calculation on the current state.
**integrated.modify/perform.** A single integrated obligation has total price T,
justified cumulative progress f and revenue R. Modification/cumulative progress
change earns T_new f_new−R. Revised progress is a supplied measurement, not the
old fraction silently carried into a changed scope. In both routes the debit
is unbilled contract asset; invoice/collection/general mixed obligations use
their own methods and later company joins.

**acqdta.recognize.** Supplied additional deductible difference x at admitted
rate r creates benefit xr after recoverability. For an acquiree's benefit from
new acquisition-date information while the measurement period is open (and
within its end and the one-year maximum), reduce related goodwill by
min(goodwill,xr) and credit any excess to tax profit. This is a retrospective
acquisition adjustment, carried explicitly in the component's adjustment ledger.
All other benefits follow their independently identified underlying origin;
the acquirer's own benefit stays outside acquisition accounting (IAS12.67) and
follows its traced profit, OCI or equity origin (IAS12.61A–63). Elapsed time alone is not
measurement-period eligibility. Missing acquisition facts or origin is unresolved.
This finite method treats positive additional recognition, not every IAS8
error/correction or complete retrospective comparative-statement rebuild.

**taxlots.remeasure.** Each temporary-difference lot retains its entity,
authority, origin and recovery evidence. Positive signed differences are
deductible; negative are taxable. New signed deferred amount equals difference
times its admitted recovery-period rate, times a supported recognition fraction
for deductible lots (taxable lots use one). Preserve gross DTA/DTL accounts;
credit changes to profit, OCI or direct equity by traced origin. No blended
convenience rate or cross-lot recoverability is inferred. **taxlots.present**
allows net presentation only for a single authority and taxable entity with an
affirmed enforceable current-tax setoff right. Cross-entity simultaneous-settlement
routes remain unimplemented. Net presentation changes report values only;
gross account and lot amounts remain available. Unknown setoff rights cannot
support a requested offset. This is a supplied difference schedule, not a full
tax-base/recovery forecast or a complete company tax return.

## Exchange, refusal, replay and reporting

Each admitted method requires exact source/context/view, an eligible Admission,
authorisation, independently checked proposed journal and economic delta,
atomic commit receipt and report. All source and code inputs are snapshotted.
An authority, fact or method refusal leaves the entire world unchanged and
identifies the exact missing item. No fallback zero tax or synthetic balancing
plug is admitted. Every monetary transition has a balanced wrong-journal case;
every method has a semantic refusal. Positive CGU allocation and the all-zero
unresolved path are separate evidence.

Identity is entity/book/branch/business event. Exact retry returns the original
receipt before freshness or re-derivation, even after a newer head/view. A
different request at the same identity is rejected. Lost acknowledgement keeps
commit unknown and retries the exact bytes in both possible worlds. Atomic
publication includes head, journal, delta, receipt, identity index and referenced
records, and preserves unrelated owners. Reports check exact receipt chains,
periods, income/OCI/equity and gross cash bridges, tax presentation and source
view. Each annual and full-path report is component-scoped; after-tax coverage
and human acceptance remain pending.
