# RepeatedItemRebalancing/1

Read-only whole-path report. Request fields are exactly wire,operation,opening,
events. Wire is RepeatedItemRebalancing/1; operation is report. Opening contains
context,findings,layer. Context contains entity,book,currency,quantity_unit,
price_unit,risk,relationship,rule,maturity_date,designation_date. All are
nonempty strings; dates are ISO calendar dates, designation precedes maturity.
Price units must equal currency/quantity_unit; risk is one-common-forward-price
and rule is the retained EU2023/1803-original-IFRS9 profile.

Each layer has exactly id,quantity,price,date. Quantity is positive; price
may be signed. Numbers are canonical reduced rational strings. The first
layer's date is original designation. The initial cumulative derivative/item/
reserve/profit are zero, with no opening derivative value in this profile.

Every event has id,operation,date,context,findings. Measurement adds price and
derivative, the cumulative derivative gain from original designation. Item
change is computed from layer origins. Event dates are nondecreasing and
precede maturity; contexts match exactly and IDs are unique. Opening and
measurement require zero_discount_admitted,complete_valuation_effects,
forecast_highly_probable,economic_relationship,credit_risk_not_dominant,
ratio_eligible. All findings are explicit booleans. Missing findings remain
unresolved; false findings require an unsupported result.

An add_item event adds layer and requires objective_unchanged,
changed_relationship,documentation_updated,ratio_eligible. It must immediately
follow a same-date measurement. Its quantity is positive, ID new, and its
designation date/price equal that observation. It adds a zero-origin exposure
without posting or changing cumulative amounts. The method admits finite
event arrays; no mathematical two-addition cap is inferred from the example.

For offsetting cumulative D,H, reserve=sign(D)*min(abs(D),abs(H)); zero amounts
give zero reserve. Same-sign nonzero cumulative values are unsupported here.
Cumulative profit=D−reserve. Post differences to derivative, reserve and gains
with debit-positive signs. Reconcile cumulative books after every observation.

Result fields are wire,status,reason,failed_event,state,trace,journals,mutations.
Status is conditional_complete,unresolved,unsupported or rejected. Positive
state retains context,date,price,D,H,reserve,profit,layers,revision,
last_operation,books. Each trace retains the event ID,operation,state,journal.
Journals contain measurement event ID,date,entries. No actual posting occurs.
On any refusal state is null; trace,journals,mutations are empty. Error location
identifies the zero-based event index, or null for opening/request errors.
Unknown structure, contradictory dates/units/origins and malformed numbers
reject; different risk/source/operations and false findings are unsupported.

Actual finding truth is outside this local report. The runner checks retained
source/input hashes; the calculator does not authenticate a jurisdiction or
valuation. Removal, partial discontinuation, instrument additions/reductions,
settlement, basis transfer, FX/discount/credit models and runtime replay are
separate obligations.
