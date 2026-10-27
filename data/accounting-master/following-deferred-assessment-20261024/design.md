# Fresh following-period deferred assessment

Consume the complete successful following-period current-tax reassessment and
recompute it. Bind the request digest and a new unique assessment id. Retain the
full predecessor,actual financial opening,tax vintages,payment history,loss ledger
and unresolved carry findings. The selected model is a hypothetical single-pool
gross deferred assessment with all movements through profit or loss.

A fresh measurement record names at,the exact state_sha256,and known jurisdiction
and regime matching the original carried loss inventory. Its account_bases map
contains every current nondeferred asset/liability basis account; lease_bases
contains each current lease right's asset/liability basis key. Values are known
nonnegative rational declarations with provenance. Item bases must sum to the
account declarations and equal the corresponding lease/retained-lot declarations.
The measurement date equals the current assessed book date. No old basis or
recovery capacity is automatically reused. The complete current item population
includes ordinary accounts,inventory subdivisions,lease rights and remaining loss
lots,including retained zero quantities. No removed or new unrecognized item is
silently substituted.

For carrying C and tax base B,the signed taxable difference is C-B for assets,
B-C for liabilities,and minus remaining loss for loss lots. Explicit recognized
deduction u satisfies0<=u<=deductible. A single fresh capacity K bounds the sum
of u across all items. Desired DTA=sum(rate*u);desired DTL=sum(rate*taxable).
Recorded DTA/DTL allocations must sum exactly to current book balances and have
explicit support. Journal desired-minus-recorded assets/liabilities with deferred
expense deltaDTL-deltaDTA. Do not net,create capacity from DTL,renew old findings,
invent a tax base or recognize a loss automatically.

Cash,current tax expense,aggregate and per-vintage payable,all settlements,
components and loss quantities remain exact. Only DTA,DTL,deferred expense and the
new seen id change. Reconcile four statements from the actual carried opening.
Full apply compares the entire result including measurement,history and findings.
OCI/equity/combination/offset/credit routes,subsequent continuation and repeated
carry remain separate dependencies. This is conditional bookkeeping,not admission.
