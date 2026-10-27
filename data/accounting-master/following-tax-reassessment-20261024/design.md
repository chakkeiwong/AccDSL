# Following-period cumulative tax replacement

Consume the full successful tax-vintage continuation request. Bind its digest,
new unique assessment id, explicit model selection, cumulative interval, complete
information declarations, adjustment allocations and loss policy. Recompute the
predecessor and recover original carried opening and original loss inventory.
No caller-supplied projected state substitutes for these inputs.

The interval starts at the financial/loss opening, ends no earlier than the first
assessment and no later than the financial endpoint, and covers every completed
event through its last day. Reconcile all pretax accounts and all selected native
return adjustments exactly once. Recompute loss use, expiry and generation from
the original carried inventory; retain previous provisional state as superseded
history. Do not reuse a provisional generated lot id or consume that lot as an
original asset. Historical prior-period loss records remain unchanged.

Let C0 be recorded current expense, C1 new cumulative tax, S current-vintage
settlements and O outstanding carried tax. The increment is C1-C0; current
liability becomes C1-S, aggregate liability O+C1-S. Require C1>=S. If not,
return unsupported with complete predecessor and diagnostic calculation but no
after state. Do not silently net a current credit against old liabilities.
Cash, old vintage, all settlements, components and deferred balances remain exact.

Retain the current vintage id used by earlier allocations. Replace its assessment
amount/provenance/interval and append the full previous vintage and previous loss
state hashes to explicit supersession history. Full predecessor records remain
in the result. Apply recomputes and compares the entire proposal. New deferred
recognition, repeated replacement, subsequent continuation and another carry
remain unsupported dependencies, not claims of annual readiness.
