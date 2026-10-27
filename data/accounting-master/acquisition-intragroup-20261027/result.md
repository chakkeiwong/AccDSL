# Downstream inventory transfer — 27 October 2026

ConditionalDownstreamInventory/1 passes **22 full cases, 33 refusal controls and
648 assertions**, preserving 95 source/comparator/code files. The numerical
cases cover three consideration mixes, three NCI elections, credit and cash
settlement, plus explicitly unrecognised and unresolved tax branches.
Evidence: attempt-01/verification.json, cases.json, controls.json, source-lock.json
and run-manifest.json. The successful writers and attempt are frozen.

The complete legal/acquisition/closing account maps, adjustment journals and
origins, financial reports, parent/NCI totals and paired cash records match
independently authored expectations. Inventory remains 20 after the full 30 sale
and 10 unrealised margin elimination. Settlement adds paired +30/-30 cash records
and eliminates both gross flows. Group cash and the subsidiary-derived NCI profit
remain unchanged in this downstream example. Legal books are retained unchanged.

For the proportional-NCI cash purchase with recognised stipulated tax, closing
assets are 1629/4, liabilities 27 and equity 1521/4. Parent equity is 2749/8 and
NCI 293/8. With the DTA explicitly unrecognised, assets and equity each decrease
by 5/2; the external current-tax payable remains. Unknown tax returns
tax_method_required with retained pretax worksheets and no final report.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain conditional downstream companion | Complete deterministic comparisons pass | All 33 specified invalid requests refuse; source/comparator hashes intact | Tax facts and attribution are supplied; event journals and external resale remain incomplete | Add explicit legal event journals and independently compare external resale before broadening direction | Actual compliance, complete consolidation, general tax allocation or implementation readiness |

Engineering ledger: exact report/worksheet comparisons pass, without mutating
predecessor files or requests. Numerical ledger: rational deterministic totals
and full account comparisons pass; no stochastic ranking is made. Interpretation
ledger: the result is a conditional method example, not source or accounting
admission. No whole requirement closes. Source review and limits are recorded in
tax-source-review.md; inspected standards do not supply tax laws or rates.

Post-run red team: matching closing books does not yet prove a complete dated
legal-event trace, and an unsold-inventory example cannot establish reversal on
external resale. These are implementation-scope gaps, not a failure of the tested
candidate or a continuation veto. The next discriminating companion should
retain sale/settlement/tax journals and show the external profit, inventory and
cash consequences. An independently computed discrepancy would reject that
candidate; it would not retroactively erase this bounded evidence.

All 53 obligations, six interactions, 46 operations and 18 packages remain open.
S1–S5 partial, S6 held, E3 deferred. Version 5.30 remains governing; this companion
awaits integration. No agents, installations, GPU, commits, fees, outreach or
publication were used.
