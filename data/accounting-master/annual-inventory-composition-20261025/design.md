# Optional inventory activity in the complete annual book

AnnualInventoryProgram/1 retains the root-once operation-list structure of
AnnualProgram/1 and adds optional kind partial_inventory_sale. Its event uses
RecoveredLotSale/1 and all six explicit findings. Other operation kinds delegate
to the protected annual transition. This is a selected extension,not a silent
change to the old grammar or schema.

The financial state retains its original SyntheticReturnLeaseTaxBook/1 profile
and all26 accounts. Annual invariants validate the complete state before and
after every operation. The proportional formulas and declaration rules are the
checked partial-lot method's rules;their numerical application is written against
the registered full financial state. No tax payable,history or account is
projected away,renamed or offset into equity. No evaluator is monkeypatched.

A partial sale changes only the selected lot,cash,revenue,inventory,cost of
sales,date,event identities and gross cash flows. It preserves all liability
vintages,settlements,current/deferred assessments,losses,opening balances and
archives. After a current assessment the status becomes activity_after_assessment;
a prior deferred measurement becomes stale. The new id joins unassessed native
activity. The sale date must be outside the assessed interval,at or after the
current financial date,and inside the period. Assessment calculations and
fresh-measurement rules then operate unchanged on the new financial state.

The root is a new explicit request over the already checked retained-lot
scenario,with its planned whole-lot sale omitted. Recomputed opening units2,
carrying20,cash452,payable41/4 and profit0 remain exact. Selling one unit for15
therefore gives cash467,inventory70,remaining cost10 and profit5;tax payable
remains41/4. Assessment and deferred measurement are supplied explicitly.
The residual unit can cross a provisional boundary and be sold next period.

Every result retains the original root result,full trace,current period book,
report and unprocessed operations. Economic refusal preserves its successful
prefix. Complete apply recomputes all results. Ordinary programs compare to old
annual results on every financial field and trace;new profile/request/implementation
identities deliberately differ and are not claimed byte-identical.

Source syntax and family dispatch are not provided by this interface. The
existing authoring and family implementations must continue rejecting the new
operation until separately extended with exact lowering and result comparisons.
No annual accounting admission,actual history or production readiness follows.
