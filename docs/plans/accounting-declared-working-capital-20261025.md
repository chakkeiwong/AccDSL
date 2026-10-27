# Trace-derived working-capital schedules

MC02/06/11/13–18/23–28/32/34/35. Question: can verified declared-program events
produce exact receivable,inventory,supplier-payable and payroll-payable roll-forwards
without classifying arbitrary postings by labels or inventing missing disclosures?
Comparator: independent six-method event arithmetic,full before/after balances and
raw verified transition journals. Use an explicit selected method-definition set
and account role map; mismatched method hashes or unexplained account changes must
refuse the supported schedule rather than silently label them other.

Write exact schedule and period/report selection semantics before coding. Verify
the complete program result first;select a successful report trace row and its
actual period opening. Classify only supported named methods by exact definition
identity,not method-key strings. Retain event IDs,dates,requests,result hashes,
opening/activity/closing signed amounts,units,price premise and source provenance.
Report positive asset/liability balances under the declared sign convention.
Inventory cost additions/releases reconcile;receivables separate credit sales and
collections;payables separate purchases/payments;payroll separates accrual/payment.
Reject changed role maps,ambiguous unknown methods affecting scoped accounts,
missing movement rows,wrong period opening and reused carry histories.

Primary pass: every schedule reconciles independently and to selected statements;
full-period/two-chart/text cases plus stopped-prefix selected prior report;explicit
refusal of unsupported movement. Cash bridge is explanatory reconciliation only;
no indirect cash-flow policy or accounting admission follows. Notes retain missing
maturity,ageing,impairment,terms,related-party,tax and disclosure-population facts.
Never set notes_complete or fiscal_complete true. Unknown facts remain visible.

Record tests/manifest and integrate,refresh full coverage,then advance the next
corporate/financing clock or dynamic-state dependency identified by the audit.
Candidate failure triggers repair;invalid comparator/source premise blocks only
that claim. No forecasting or professional outreach.
