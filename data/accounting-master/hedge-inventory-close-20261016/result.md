# Hedge reserve, inventory basis and sale close

16 October 2026. Attempt 01 passes 170 checks with zero failures: two
independently authored terminal cases, 38 adverse requests and two missing/
corrupt input challenges. The endpoint resolves the retained input bytes and
reconstructs the accepted hedge internally before deriving purchase and sale.
It does not accept a caller's substitute reserve.

The claimed target is the cumulative pre-tax subledger for the specified
hedged purchase, complete derivative settlement, direct inventory basis
adjustment and subsequent full sale. The computed quantities equal the
independent expected journal, inventory, gross cash and equity amounts.
IFRS9.6.5.11(d)(i), IAS2.10–11/34 and IAS7.16 supply the inspected historical
accounting/classification basis; recognition, NRV, settlement and valuation
findings are explicit synthetic inputs. No full-company tax result follows.

In the gain case, supplier cash is 12,610, derivative receipt 1,900, reserve
gain 1,810 and cumulative hedge profit 90. Transfer the reserve directly to
reduce inventory cost to 10,800. Before sale cash is 9,290 and pre-tax equity
20,090. Sale receipts 14,500 then produce cumulative profit 3,790 and closing
cash/equity 23,790. Gross operating receipts/payments are 16,400/12,610.

In the loss case, supplier cash is 10,400, derivative payment 500, reserve
loss 400 and hedge loss 100. The reserve loss increases inventory cost to
10,800. Before sale cash is 9,100 and pre-tax equity 19,900. The same sale
gives cumulative profit 3,600 and closing cash/equity 23,600. Gross operating
receipts/payments are 14,500/10,900. Both cases clear inventory, derivative
and reserve after sale without a cash or earnings entry for the basis transfer.

The wrong reserve-to-income treatment gives the same final cumulative profit
after all inventory is sold, but wrong pre-sale inventory and profit. The
independently authored intermediate balances detect it. This is a direct
counterexample to treating final cash/profit agreement as sufficient evidence.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Retain conditional close | Signed basis, interim/final books and gross cash agree | No observed failure | Supplied complete purchase/valuation/settlement facts | Integrate the derivation and extend partial realization separately | Full company, tax/NCI or actual compliance |
| Reject reserve-to-profit shortcut | Pre-sale inventory/profit disagree despite terminal equality | Exact source/target mismatch | None for this specified direct-basis case | Retain intermediate-balance checks | That final agreement validates the route |

| Inference status | Judgment |
|---|---|
| Hard veto evidence | Wrong release fails the source-target/interim balances; no accepted failure |
| Statistical ranking | N/A: exact deterministic examples |
| Descriptive differences | Different terminal dates and values; no performance/economic ranking |
| Default-readiness | No runtime, default or current-law promotion |
| Next evidence | Partial deliveries, retained reserves, company tax/NCI, actual recognition/valuation facts |

Post-run red team: assumed full receipt and cash settlement might be false
for an actual contract. The report refuses missing/changed findings but cannot
establish their real-world truth. Its cash sufficiency check uses the declared
purchase-then-settlement order; funding outside that order needs another
specified event sequence. The report is recomputable and read-only, not a
production idempotency or persisted-book guarantee. No continuation veto fired.
