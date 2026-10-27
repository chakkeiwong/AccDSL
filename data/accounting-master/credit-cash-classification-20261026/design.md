# CreditCashClassification/1

This read-only layer imports one exact retained CreditLinkedBook/1 projection.
It supplies no accounting policy. The caller declares a policy reference,
explicitly marked caller_assumption and bound to the host context. Each native
cash origin is addressed by its index and content digest within that projection.
A declared classification contains named signed components with an activity and
policy reference. Components must sum exactly to that origin and have its sign;
they cannot hide offsetting receipts and payments inside one net amount.
Zero origins remain explicit. Missing or unknown classifications remain visible.

Price, integral cost, integral fee and collections are distinct cash origins.
Effective-interest income and impairment accruals are not classified as cash.
The layer binds each origin to the journal whose exact native prefix introduces
it. Dates, original amounts, journal ids, entity, book and currency survive.
Classification changes never change the journals or balance state.

For each retained observation, aggregate only the origin prefix available at
that journal position, including separate observations on the same day. Report
gross receipts, positive payments and signed net amounts by activity. If any
origin in that prefix lacks classification, the classified statement remains
unresolved and identified partial totals are labelled as such. Net cash still
comes from the native balance projection. Complete classifications reconcile
exactly with that amount; no residual balancing category is permitted.

Rational stage projections gain explicit flow records and are compared with
the unchanged CompanyBookReport/1. Nonrational financial amounts retain their
single-root expressions; no rounded host book is admitted. The original
unclassified acquisition report remains refused in the archived evidence.
Source, accounting, fiscal and complete-note admission stay false. Full
indirect cash reconciliation and actual policy eligibility are separate work.
