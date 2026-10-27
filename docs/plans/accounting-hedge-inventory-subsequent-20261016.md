# Carry the hedged inventory basis through partial sales and NRV changes

16 October 2026. R03 corporate/financing join, MC02/04/05/11/13/15/16/17/19/
24/25/28/30/32/33/34/35 and G2/G4/G7/G13/G15/G18. Documentary reference
calculations and manuscript only; no runtime or empirical execution.

## Question, baseline and skeptical audit

How does the directly adjusted purchase cost enter earnings when only some
goods are sold, and how does a later net realisable value (NRV) recovery avoid
reinstating a write-down on goods already sold? The baseline is the protected
Version 3.20 all-purchased/all-sold subledger, with supplier cost C, derivative
D, reserve R, initial inventory C-R=10800 and hedge earnings D-R. Both positive
and negative reserve terminal cases are retained. Final cash/profit agreement
alone is insufficient; the primary targets are intermediate cost, quantity,
allowance, profit and equity, plus their cumulative reconciliation.

The audit rejects allocating the hedge reserve among partial forecast purchases
by an assumed percentage. This phase instead starts after ALL 130 units have
been acquired and ALL reserve has entered inventory. IAS2.25/27 supplies weighted
average cost for ordinarily interchangeable inventory. A single homogeneous
batch, with identical nature/use and uniform per-unit economics, has cost
10800/130=1080/13 per unit. Designation-layer origins are not separate physical
inventory lots. Additional purchases, heterogeneous items, specific-identification
cases and a partial designation/purchase require other methods.

IAS2.28–34 requires current carrying cost on sale, period write-downs and
reversals capped at original cost for goods still held. Keep gross adjusted
cost and its allowance separately. For remaining units q and common supported
NRV v, target carrying value is q*min(1080/13,v); a sale removes its share of
both gross cost and current allowance. The first valuation cannot silently be
reused at every later reporting date: each NRV event supplies a dated valuation
finding and, for recovery, the required changed-circumstances finding.

The skeptical audit passes for this homogeneous single-batch method. A missing
valuation or false recognition finding blocks that case, not other internal
methods. No claim of current jurisdictional compliance or actual valuation is
made. Preserve the historical source version and all earlier evidence.

## Intent and evidence contract

Mechanism: retain quantity, gross adjusted cost and allowance through sale and
NRV events after reconstructing purchase/settlement/basis internally. Expected
failure: expense the whole batch on the first sale; ignore the basis adjustment;
keep a sold unit's allowance available for later reversal; or recreate OCI
after the reserve was transferred into inventory.

Primary criterion: exact independently authored stage balances and journal
origins for both hedge signs; original all-sold outputs remain equal at the
limiting case. Hard vetoes are corrupt/missing source bytes, accepting substituted
terminal state, invalid context or dates, overselling, unsupported cost formula,
missing NRV/recovery findings and disagreement with any intermediate target.
Invalid request handling must be atomic. Failed local checks trigger a retained
repair. Check counts, page counts and runtime are explanatory only. No stochastic
ranking or new default policy is proposed.

Continuation vetoes are inconsistent required authority, corrupted protected
inputs or work beyond the documentary authorization. No absence of independent
or human acceptance ends feasible internal preparation. Passing establishes
only the declared deterministic method, not a production inventory engine,
complete company statements, tax/NCI, IFRS15 recognition, partial purchases,
forecast cancellation, general NRV estimation or forecast quality.

## Independent targets and assumption audit

Both source-bound terminal cases acquire 130 units and begin with cash/equity
20000. The gain case has pre-sale cash9290/profit90; the loss case9100/−100.
Sell52 for5800: cost4320, remaining inventory6480. Reduce NRV to70 on the
remaining78 units: carrying5460, allowance1020. Sell26 for2900: expense1820,
remaining52 units gross4320, allowance680, carrying3640. Recover NRV to90:
reverse680, carrying4320. Sell52 for5800: closing cash/profit23790/3790 or
23600/3600. Total expense10800 comprises cost of sales10460 and net write-down340.
The tempting reversal of1020 after the second sale is wrong by340.

Also freeze no-sale, partial-sale-only, original all-sold, recovery to80 then90,
and repeated unchanged valuation targets. Exact fractional inputs avoid rounding
policy assumptions. Weighted average is a supported case policy, not a preferred
universal default. Uniform per-unit NRV is an explicit synthetic finding; mixed
contracts, differing selling costs or other heterogeneous units invalidate it.
Opening cash20000, sale proceeds14500 in total, no tax/fees/FX/returns/shrinkage,
and purchase-before-settlement funding order are inherited case assumptions.
Check these at admission; missing funding must not be concealed by later receipts.
The initial NRV supports adjusted purchase cost; later declines are separately
dated. Revenue recognition is supplied, not inferred from receiving cash.

Pre-mortem: a final correct profit can hide premature cost recognition and an
excess recovery can hide inside a balanced journal. Compare every intermediate
inventory/allowance/earnings balance; mutate the recovery and sale order. Verify
that a whole sale and an equivalent partition produce identical final balances
when no valuation or reporting boundary intervenes.

## Execution and reader contract

Retain exact source anchors and independent expected results, then lock their
bytes before writing the calculator under
`data/accounting-master/hedge-inventory-subsequent-20261016/`. Existing Python,
Fraction and CPU-only `CUDA_VISIBLE_DEVICES=-1`; no installation. Preserve every
attempt, actual command/environment/commit/duration and result. Up to three
focused repairs is a work-management bound, not a correctness threshold.

The reader knows the completed purchase example. Begin with goods still on the
shelf, derive per-unit cost, then distinguish an unsold unit's write-down from
one already included in cost of sales. Introduce the allowance only when that
distinction is needed. Protect Version3.20 sources, integrate next to the
purchase example, build and inspect affected pages. Keep voice provisional
pending human feedback. Update all53 obligations, six interactions and the
three live controls without changing frozen release evidence.
