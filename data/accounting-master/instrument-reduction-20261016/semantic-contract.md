# InstrumentReduction/1

Read-only conditional whole-path report under the inspected historical
IFRS9.6.2.4–5,6.5.11,B6.5.8/16/18/21. Actual marks, eligibility and required
rebalancing findings are supplied. No runtime posting or current-law opinion.

The request has exactly wire,operation,context,opening_cash,findings,item,
instruments,events. Wire is InstrumentReduction/1; operation is report. Context
is the fixed2025 synthetic legal book and historical rule profile. The item
has id,positive quantity and positive origin price. Exactly two distinct
instruments have id and positive original nominal quantity. Both have admitted
zero initial cost/value, full original designation and remain owned until
settlement. No option or excluded valuation component is admitted.

Canonical rational strings carry all quantities and values. Marks and
settlements may be signed; prices/counts/reductions have their stated positive
domains. Unknown fields reject. All findings are explicit booleans: unknown is
unresolved, false scope finding unsupported, malformed encoding rejected.

Events have unique IDs, matching contexts, canonical nondecreasing dates within
designation/maturity, and complete operation-specific findings:

* `measure`: price and one whole-instrument mark for every ID. Update each
  component's G by its designated fraction times the mark change, and U by the
  complementary fraction times that change. Item H uses unchanged original
  quantity/price. For offsetting cumulative G,H use signed lower-of reserve;
  profit=(G−R)+U. Keep gross derivative assets and liabilities visible.
* `reduce_instruments`: positive named quantities, each no larger than the
  currently designated quantity, immediately after a same-date measurement.
  Record date, nominal quantity/fraction, whole mark and stopped portion value;
  reduce only the fraction applied to future changes. No journal or reserve/
  profit/item jump. Full discontinuation requires another method. Findings
  admit structural ratio change, unchanged objective, remaining qualification,
  updated documentation and retained ownership.
* `purchase_and_settle`: immediately after the maturity-date measurement.
  Purchase quantity equals the complete unchanged item; price equals the
  latest observation and supplier cash equals their product. Every derivative
  settlement equals its full latest signed value. Supplier funding is checked
  before settlement, then each derivative cash movement separately. Transfer
  the attached reserve into inventory basis. No event may follow closing.

Each component retains its stopped origins, G,U,current value and settled cash.
Before settlement V=G+U; afterward V+settled_cash=G+U. Its equivalent history
formula is G=w*V+sum(stopped_fraction*stop_mark), using the settlement mark in
place of V after closing. The reserve is associated with the unchanged item;
the report does not allocate it to heterogeneous removed purchase populations.

Success returns chronological stages, balanced proposed journals, three gross
cash origins, final state and a closing cost/reserve/inventory bridge.
`posts=false`, `mutations=[]`. It requires a completed closing; no incomplete
path is presented as a full report. Any failure returns no state, closing,
stages, journals or flows. Source-byte changes reject and missing bytes remain
unresolved. No unknown series, mark or settlement is skipped.

The delivered cases verify two choices of30-unit removal, unchanged marks,
no removal, proportional component reductions, a smaller item change, a signed
reversal and simultaneous derivative assets/liabilities. The method does not
value derivatives, infer qualification, determine tax/cash-flow activity,
allocate an unidentified heterogeneous stopped-item reserve, or calculate
actual/aligned option components. The latter is the next named F2 subunit.
