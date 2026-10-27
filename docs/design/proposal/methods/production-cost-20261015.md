# Cost is conserved, but not all factory spending becomes inventory

15 October 2026. P17-04/11; MC02/05–07/11/13–16/19/20/24–28/30/32–35.
Governing plan: docs/plans/accounting-production-cost-20261014.md.
Dossier: data/accounting-master/p17-completion-20261014/P17-04/production-cost/.

## Pre-run intent and skeptical audit

Question: how do fixed production costs enter unsold inventory when actual
output differs from normal capacity? Baseline: inspected AASB102.10–16 and34/38,
not a margin target or a full-absorption convention. Mechanism: retain cost
origin, yield and capacity; allocate admitted production costs; expense idle
capacity/abnormal outlays; recognize sold goods and preserve remaining units.

Primary criterion: exact source-consistent allocation and stock/expense/cash/
PPE reconciliation, independently recomputed. Balanced wrong treatments must
fail allocation/recognition criteria. Vetoes: unknown capacity, abnormal yield
hidden in unit cost, allocated fixed overhead exceeding incurred amount, wrong
cost origin, or revenue recognized without admitted transfer. Missing actual
tax or firm data limits this pretax authored claim, not continuation. Hashes,
counts and PDF success are integrity/typography only. No stochastic ranking.

Pre-mortem: full-absorption cost at low volume balances but defers idle cost;
using the normal rate unbounded at high output creates cost never incurred;
adding back only expensed factory depreciation can break cash reconciliation
when some depreciation remains in unsold stock. Independently reconcile the
whole production-cost pool, the signed ledger and direct/indirect cash.

Audit passes with the explicit pretax boundary and capacity evidence. The
formula below is a derivation for this single homogeneous pool with constant
fixed costs, not an all-industry or multi-product default. Repairs triggered
by a wrong case do not invalidate all historical inventory methods.

## Facts and defaults

Synthetic Tier1 for-profit manufacturer, calendar2024, ordinary manufactured
goods. Opening cash1000 and net factory PPE600; no debt/payables, inventory,
opening tax balances or owner movements in this slice. Opening pretax net
assets1600. PPE has ten years remaining, zero residual, one component and
uniform time consumption; current depreciation60. Independently admitted
recoverability; no revaluation/restoration/borrowing/lease. Actual tax is not
modelled and no zero-tax real-company assertion is permitted.

The production plan's normal annual capacity is100 good finished units,
averaged over normal periods with planned maintenance already reflected.
This is supplied technical evidence, not inferred from actual output.
Evaluate distinct scenarios Q=60,100,150 and an idle Q=0 boundary. Q150 is
explicitly abnormally high; Q60 is low. No WIP/opening goods/joint products/
normal loss: one complete material kit yields one good unit. Each good unit
uses materials2, direct labor1, variable overhead1, all paid. A separate
documented accident destroys six unused material kits costing12 before labor
or conversion. These inputs are not counted among the Q good kits. Waste has
no recoverable proceeds. The same accident assumption is used in each arm.

Fixed factory overhead180 consists of cash factory management/maintenance120
and the60 noncash depreciation, independent of Q for this bounded scenario.
Separately paid unrelated head-office administration10 and selling services8
are current expense. Selling services relate to the period; the completed
unsold goods need no additional completion or sale expenditure. Each has
supported expected selling price/NRV10. No storage/financing or other costs.

Sell S=40,80,120 for Q60,100,150 respectively, at10 per unit for immediate
cash; Q0 sells zero. Full contract/revenue conditions in source-review.md
are supplied; actual delivery, acceptance and title/control transfer coincide.
A separate S=60 arm holds Q60 and all production cash fixed to test sell-through.
No claim is made that different output scenarios have identical production
spending; only alternative accounting of the same scenario leaves cash fixed.

| Choice and provenance/status | Why; failure; early check |
|---|---|
| N100 and fixed180, authored capacity hypothesis | Separate utilization from unit cost; circular target-margin choice; require independent capacity identity |
| One good kit/unit, no normal loss, authored yield hypothesis | Makes abnormal accident distinct; double-count kits; purchased kits Q+6 versus outputQ/waste6 |
| Direct2+1+1 and equal good units, teaching hypothesis | One weighted-average pool; transferred multiproduct default; reject joint/WIP/unequal-cost inputs |
| Fixed cash120 plus depreciation60, sourced categories and supplied amounts | Show cash/noncash origins; pay depreciation twice; cash excludes60, PPE decreases60 once |
| N-based low allocation and Q-based high cap, local derivation | Follow102.13 in constant-pool case; gross over-allocation; compare exact allocated sum with180 |
| Pretax only, declared scope | Avoid fabricated tax law; equating pretax net assets to distributable equity; output carries tax-uncomputed status |
| NRV10 and transfer facts, supplied admissions | Isolate conversion method; hiding impairment/recognition; refuse missing admissions |

## Procedure and representations

For Q>0, fixed cost per good unit is180/max(100,Q). Allocated fixed cost is
Q times that rate; current unallocated overhead is the remainder of180.
At Q0, no unit-cost division or stock allocation occurs; expense all180.
Admitted unit cost is4 plus allocated fixed cost per unit. Completed inventory
pool=4Q+allocated fixed. Sold-stock expense=S times unit cost; remaining
stock=(Q-S) times unit cost. Abnormal12 and unrelated18 never enter this pool.
The broader inventory expense includes sold-stock cost, unallocated overhead
and abnormal12 under102.38; unrelated18 is separate.

Each cost event has one identity and one destination. The proposed state stores
capacity evidence/version, good-unit and loss populations, cost-pool membership,
fixed cash/noncash origins, allocation, lot quantity/cost and sale-removal IDs.
Revised capacity is a new estimate/evidence event, not an in-place margin plug.
Duplicate resource inclusion and negative stock are invalid. This documentary
method adds no portable OperationRequest encoding and no execution engine.

Journal path: raw good and destroyed-kit materials against cash; waste removes
the12 from raw stock to expense; good materials plus labor/variable overhead
enter finished goods. Fixed cash costs and depreciation first enter a production
clearing account, then allocate that account between finished goods and current
unallocated overhead. The clearing balance must end zero. Sale records cash/
revenue and removes the sold goods. General administration/selling expense is18.

Expected comparisons, to be independently checked: low output unit5.8, stock116,
unallocated72, profit66, closing cash1010/PPE540/pretax net assets1666. Normal
unit5.8, stock116, profit306, cash1250/net assets1906. High unit5.2, stock156,
profit546, cash1450/net assets2146. Idle stock0, profit-210, cash850/net assets1390.
Sell-through low stock0, profit150, cash1210/net assets1750. Pre-check arithmetic
review repaired the planning-only normal/high profit and cash amounts: the
low-output unallocated72 must not also be charged in normal/high scenarios.
Those old provisional values were not executed or integrated into the manuscript.

Adverse low actual-denominator180/60 defers24 idle cost in stock and overstates
profit by24. High uncapped normal rate allocates270 though only180 occurred;
any balancing variance credit exposes an invented allocation. Capitalizing
abnormal12 and unrelated18 into low output defers10 of excluded expense in
the20 unsold units. These are different wrong targets even if books balance.

## Reader and evidence

The reader knows inventory expense and straight-line depreciation. Begin with
the same factory making fewer goods; show why its idle cost cannot become more
valuable stock. Then contrast high output, explain the cap, and join unsold
depreciation to direct/indirect cash. Keep the comparison table compact and
scope/failure facts in prose. Apply the existing scholarly teaching contract;
acceptance remains provisional pending reader evidence.

Persist fixture, independent per-resource ledger, expected statements and
adverse cases. Prepare protected2.93 only after those checks pass; preserve
2.92 and all unrelated index entries. Update results and controls before the
next work unit. After this costing gap, perform a finite residual/convergence
audit to choose the next highest-priority actual omission instead of adding
indefinite similar examples.
