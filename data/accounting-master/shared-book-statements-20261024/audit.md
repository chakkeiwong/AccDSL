# Pre-implementation audit

The plan answers the missing statement connection for the newly checked book.
Original native_reports.py requires completed annual tax; this prerequisite
must not be removed or attributed to the new profile. The new views instead
reconcile recorded amounts and retain unknown tax/annual completion.

The indirect bridge must subtract the lease derecognition gain. In the signed
trial balance, other_gains is a credit-negative income account, so adding its
signed balance to profit removes the positive noncash gain. Depreciation is
added back. Return/inventory working-capital changes retain the original signed
convention, including the credit-negative refund liability. Interest remains
operating under the explicitly inherited historical election.

Require a fresh opening with zero income, no event/flow/tax-adjustment history
and no opening interest already paid. The executor supplies the completed
prefix; an invalid opening supplies no report. A failed later event does not
invalidate the preceding valid state, but must stay visible in report coverage.
Unexecuted dates, owner changes, omitted account categories and balancing
amounts are never invented. Tests and exact identities are the promotion
criterion for this finite reporting reference; they establish no full tax,
source authenticity, statement completeness or production readiness.
