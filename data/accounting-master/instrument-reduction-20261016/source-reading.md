# Instrument reduction: source and cumulative-history deduction

Inspected EU2023/1803 original IFRS9.6.2.1–6.2.6 (35715–35813),
6.5.11–12 (36078–36170), B6.5.5–21 (41957–42217), and B6.5.22–28
(42218–42388). Retained primary text/PDF under p08-v3-preparation; no current
issuer law or valuation finding is inferred.

6.2.4(c) permits a proportion of an entire instrument;6.2.5 permits jointly
designating combinations. Instrument-specific nominal fractions therefore need
not equal a fraction of aggregate carrying value. B6.5.8 requires measurement
before rebalancing and treats rebalancing as continuation. B6.5.16/18 leaves
the reduced portion owned but outside the hedge, with later changes in profit;
the hedged item and measurement of continuing volume remain unaffected.
B6.5.21 requires updated documentation. B6.5.12/15/23 exclude elective removal
to suppress observed ineffectiveness or pretending a changed objective is
ordinary rebalancing.

For whole-instrument mark V_j and designated fraction w_j, a measured change
delta(V_j) splits into w_j*delta(V_j) while designated and the complement after
removal. Accumulating these changes gives G_j and U_j. A reduction changes
only the fraction for future changes, leaving prior G_j/U_j unchanged. Since
the original values/costs are zero and all instruments remain owned, V_j=G_j+U_j.
Equivalently, G_j=w_j*V_j+sum(stopped_fraction*V_at_stop); this is an independent
closed-form check on the chronological accumulation.

The original continuing purchase retains its own cumulative H and its reserve.
Apply6.5.11's lower-of test to designated gain history G and item H; total
earnings=(G−R)+U. Removing a derivative portion does not remove purchase units
or invent a stopped-item reserve. There is no reclassification on the quantity
change itself. At purchase6.5.11(d)(i) transfers the attached reserve into the
nonfinancial asset's basis, separately from full gross derivative settlement.

This extension is a local deduction of the stated continuation and prospective
measurement rules, not a quoted general allocation theorem. It does not
allocate an unidentified reserve across heterogeneous discontinued purchases.
The no-change measurement, chronological/closed-form agreement and full cash/
basis bridge are necessary checks. They do not authenticate actual eligibility,
valuation, documentation, recoverability or independent domain acceptance.

Options are excluded. B6.5.32–33 was separately inspected as the next F2 lead:
aligned time value uses a hypothetical option matching item terms, with distinct
rules depending on whether initial actual time value exceeds or falls below
the aligned value. This source is not reduced to proportional nominal scaling.
