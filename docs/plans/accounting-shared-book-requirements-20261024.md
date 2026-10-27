# Express shared-book totals and allocation invariants

24 October 2026. S2–S4; MC05/13/15/17/23/24/26/27/31;
G2/G3/G10/G13/G15/G17. Preserve the recorded collection and identity layers.

Question: can exact totals over explicitly complete typed collections express
the selected native shared-book equations without inventing missing balances?
Baseline: native_returns.py invariant, especially signed book balance, inventory
allocation, refund-liability sign, recovery-asset allocation and lot tax basis.
The exact comparison uses known retained states and isolated mutations; financial
feasibility and source truth are separate from these necessary equalities.

Skeptical audit: balanced journals are necessary but not sufficient. A partial
account list must not sum to a claimed whole book. Account classification and
coverage require separate checks. Negative liabilities follow the native signed
book convention; do not add balancing plugs, absolute values or rounding. An
empty complete collection has total zero; a partial or unknown collection is
unresolved even if observed coefficients cancel. Unknown fields never become zero.
Exact field types, context and scale must match the declared sum; there is no FX
conversion or implicit group-to-legal allocation.

Inspect existing aggregation and scalar machinery first. Reuse Fraction and
the protected v3 evaluator for equations. Add a versioned collection-total
assessment that explicitly binds global or sum values to the original typed
input declarations and preserves indexed contributors and unknown reasons.
Keep full account-registry coverage, local amount domains, row state and monetary
effects as separately stated conditions. No inference from selected sums to full
native invariant equivalence.

Primary acceptance: independently hand-computed signed sums and selected native
invariant comparisons, including empty complete, partial, unknown, mixed signs,
unit/context mismatch, known allocation errors and invalid rows. Preserve exact
source and prior-result hashes. Counts/timing are explanatory only. A known
accounting mismatch vetoes the candidate; a missing effect method triggers the
next typed-transition/atomic-posting repair, not global abandonment.

Default audit: exact rationals and conservative unknown propagation inherit the
checked requirement semantics. Bounded collection sizes and expansion limits
remain engineering policies; inspect whether repeated sums need a separate work
budget. Supplied completeness remains a caller declaration, not a proven actual
company ledger. Monetary reconciliation provides no statistical ranking or
forecast evidence. Record comparator coverage and explicit non-equivalences.

Artifacts: data/accounting-master/shared-book-requirements-20261024/.
CPU-only deterministic checks; capture plan, command, commit/environment,
input/output hashes, decisions and next phase. Version 3.60 remains not_ready;
S1–S5 partial, S6 held, S7 deferred. No whole MC requirement closes.
