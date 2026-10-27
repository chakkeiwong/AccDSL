# Connect the rebalanced hedge to purchase cost and subsequent sale

16 October 2026. R03/P17-05.05 and corporate/financing join;
MC02/04/05/11/13/15/16/17/19/24/25/28/30/32/33/34/35; G2/G4/G7/G13/G15/G18.
Documentary pre-tax subledger only; full-company tax/NCI integration remains
separate. No runtime, installation or empirical campaign.

## Question, baseline and skeptical audit

The repeated-item method currently stops with a derivative asset/liability, a
cash-flow reserve and cumulative ineffectiveness. When all designated forecast
purchases occur and become inventory, how do these amounts reach cash, cost
of inventory and later cost of sales? The exact source is IFRS9.6.5.11(d)(i):
remove the reserve directly into the non-financial asset's initial cost, not
an OCI reclassification through profit. IAS2.10–11 specifies purchase cost;
IAS2.34 recognizes inventory carrying amount as expense on the related sale.

Baseline: protected RepeatedItemRebalancing/1 attempt02 and its original
100@80,10@90,20@95 layers. Compare two independently authored terminal dates
from that same admissible path, not two treatments of one unchanged date.
Positive observation m3: price97, total quantity130, supplier cost12610,
derivative1900, reserve1810, ineffectiveness90. Negative final observation m6:
price80, supplier cost10400, derivative−500, reserve−400, ineffectiveness−100.
In either case adjusted inventory cost is supplier cost minus signed reserve,
10800. Signed reserves and derivative settlement must work in both directions.

Use opening cash20000/equity20000 to avoid an artificial funding failure; this
is a convenience synthetic balance, not a financial-policy default. Supplier
purchase, derivative settlement and basis transfer occur at the selected final
measurement date with no intervening valuation movement. All130 units are
received, under one purchase population, and later sold for cash14500. Revenue
recognition is a supplied satisfied fact; this unit does not implement IFRS15.
No fees, FX, credit, costs of conversion, shrinkage, sale returns or other
expenses are assumed. NRV supports10800; missing/different findings refuse.
Income tax is not calculated and reported profit/equity are explicitly pre-tax.

Primary criterion: independent exact journals, purchase/sale statements, gross
cash movements and pre-tax equity bridge agree with the source-signed basis
formula. Positive final profit3790 and cash23790; negative profit3600 and
cash23600. Before sale inventory10800; derivative/reserve zero after close.
Do not promote this subledger to a complete P5/company tax result.

Veto/repair checks: source/resolver mismatch, purchase population/date/price
not equal to the accepted terminal report, missing recognition/NRV/valuation
findings, double basis transfer, wrong cash sign, OCI reclassification through
profit, missing original ineffectiveness or unbalanced books. Classification
and mutation refusal are engineering vetoes; check counts and page counts are
explanatory. Failed local tests trigger retained repair.

Continuation vetoes: inconsistent required source, corrupted immutable input
or a required step beyond authorized documentary work. Lack of an actual
issuer/jurisdiction or paid review blocks that application only.

Pre-mortem: a direct reserve-to-profit release would still balance and could
even produce the same total profit after sale, while overstating inventory
cost and wrong interim earnings. Therefore check the pre-sale balance sheet,
separate OCI movement and recognition origin, not only final cash/profit.
With a reserve loss, adding its signed value instead of subtracting it would
understate inventory cost; the negative case exposes that.

The skeptical audit passes for the stated all-purchased/all-sold pre-tax
subledger. It preserves the source target and compares independently specified
terminal records; excludes partial purchases, cancellation, losses/NRV repairs
and tax instead of inventing their treatment. Those are remaining methods.

## Execution

Inspect retained source anchors; freeze exact expectations, baseline path and
source hashes before implementation under
`data/accounting-master/hedge-inventory-close-20261016/`. Replay the selected
path internally; do not trust a caller-supplied terminal reserve. Use exact
rationals, `CUDA_VISIBLE_DEVICES=-1`, existing Python and up to three focused
repair attempts (a convenience work bound, not a scientific threshold).
Record manifest, refusals, decision/inference tables and strongest alternative
explanation. Integrate passing derivation into a protected successor, inspect
the actual pages and update the master/next phase.
