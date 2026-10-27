# Reconcile conditional current tax without silently posting or refunding

24 October2026. S2–S4;MC05/11/13/16/24/26/28/35;G2/G4;P17-04.10/11.

## Skeptical audit and research intent

The information assessor can accept inconsistent numeric declarations and
arbitrary treatment text. That limited result is correct for its declared
target but cannot justify tax calculation. The original return-only tax close
omits the mixed lease gain, immediately pays tax and reverses all deferred
balances. Reuse is vetoed; retain the two original exact native controls.

Question: can a separate finite conditional calculation preserve complete mixed
income and return-adjustment origins, require consistent lease-right tax bases,
and expose gross current-tax arithmetic without inventing refund, settlement,
deferred-tax recognition or completed annual accounting?

The model is an explicit arithmetic assumption: a single declared nonnegative
rate multiplied by nonnegative declared taxable profit, before credits and
other regimes. This is a replaceable hypothetical profile, not a legal default.
Multiple rates, credits, graduated rules, minimum tax and loss treatment require
other rules. Inspect existing taxlots methods as a comparator for specificity,
not as authority to infer the missing regime. No actual source or law is added.

## Evidence and implementation contract

Inputs bind an unchanged successful information request, its exact digest and
a separately declared calculation model. Require an affirmative assumption
that the uniform-rate/no-credit arithmetic is selected. The complete pretax
income is recomputed from all seven income accounts, including other_gains.

Each signed current-tax adjustment declared by account must be allocated to
identified items. Every completed native return tax-adjustment event within
the interval appears exactly once, at its original signed amount and event
identity. Caller-supplied additional items have explicit origin and assumption
provenance. Per-account item sums equal the supplied account adjustments;
there is no hidden residual or balancing adjustment. Native adjustment amounts
are never added again outside those allocations.

Opening and closing aggregate ROU/liability tax bases must equal the respective
sums across all retained rights. This subset requires consistency even for
zero carrying amounts; it does not infer zero tax basis from termination.
An inconsistency vetoes this calculation, not the underlying recorded report.

Compute signed taxable profit as complete pretax income plus reconciled signed
adjustments. If negative, retain the exact loss and return loss_route_required;
do not compute a negative payable or cash refund, and do not recognize a loss
asset. If nonnegative under the explicit selected model, compute gross current
tax at the declared rate. Tax cash settlement, accrued payable, deferred tax,
posting, legal admission and annual-close readiness always remain unresolved.

Primary pass: independently calculated exact arithmetic, complete native report
preservation, complete adjustment identities and aggregate/right basis equality.
Vetoes: missing/duplicate/extra native adjustment origins, changed amounts,
allocation mismatch, inconsistent bases, false/unknown model premise, identity
tampering or lost stopped-prefix state. Passing type checks alone is insufficient.
Expected negative-profit results trigger a later explicit loss-method design,
not termination of the simulator direction.

Test the unchanged mixed example as a negative-profit case under an expressly
hypothetical reconciliation; test positive and zero controls by changing only
explicit hypothetical additional adjustments. Preserve every original request.
All fixture assumptions are labelled, not admitted facts. Save complete cases,
tests, exact commands, source hashes, decision and uncertainty in
data/accounting-master/shared-tax-reconciliation-20261024/; refresh controls.
S1–S5 partial,S6 held,S7 deferred. No whole requirement closes.
