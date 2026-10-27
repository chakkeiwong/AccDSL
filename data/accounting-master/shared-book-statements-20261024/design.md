# RecordedSharedBookStatements/1

The closed request contains profile, source_bundle_sha256, opening_sha256,
events_sha256, opening and events. The implementation replays the protected
SyntheticReturnLeaseBook/1 reference. Callers cannot supply closing balances,
an alternative reporting callback or annual-completion flags.

The opening must be a valid fresh period opening, with no recorded income,
event history, flows, tax-adjustment history or already-paid opening interest.
One classification assigns all25 accounts exactly once. Original return
classes gain ROU as an asset, lease liability as a liability and other_gains
as income. Signs retain debit-positive accounting; liability and equity totals
reverse the corresponding credit balances. Recorded profit is the negative
sum of income accounts, including whatever tax postings are actually present.

An accepted request returns recorded_prefix. Its coverage contains requested,
completed and unexecuted event counts, execution status, failed event with
native reason, last completed date and the declared period. A refused later
event leaves statements for the valid completed prefix. Invalid opening or
an unsupported opening basis produces no statement views.

Statements contain recorded assets/liabilities/equity, income, equity movement,
gross receipts/payments/net flows by activity and a full indirect operating
bridge. All complete execution results and gross origins remain available.
No original before/after account or component is dropped. Exact discrepancies
are computed and required to be zero.

For debit-positive balances b, recorded profit is minus the sum of income
accounts. Recorded equity is minus the sum of equity accounts plus profit.
The finite methods have no owner-capital movement; equality of every owner
account is checked before reporting. Cash movement equals operating, investing
and financing net flows. The indirect bridge is recorded profit plus
depreciation, recorded deferred-tax expense and signed other_gains, less
changes in inventory/receivables/payables/recovery/refund accounts and less
already-expensed opening interest paid. Signed other_gains removes the
noncash lease gain; the refund liability retains its credit-negative sign.

The five-event fixture has assets701, liabilities104 and equity597. Opening
equity592 plus recorded profit5 equals597. Operating cash is30-59=-29 and
financing cash is-110, giving total cash movement-139 and closing cash361.
The indirect bridge is5+10-20+16-40=-29, with its other recorded terms zero.
The cash130 funding-failure case reports only two completed events: cash82,
recorded profit16 and operating cash-48. The failed payment remains visible.

These are recorded-only views. Tax assessment, complete period coverage and
annual completion always remain unresolved; annual_close_ready and
complete_financial_statements remain false. A recorded tax balance of zero
does not determine tax owed or the full required charge. The original annual
report still refuses its incomplete-tax input and remains unchanged.

Verification fully recomputes the result and compares canonical bytes,
including execution, source, classification, coverage and all totals. Different
Boolean/integer types, forged profit or a dropped flow cannot pass. Output
classification lists are copied so mutating a result cannot change the registry.
