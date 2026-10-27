# Attach reported opening and movement relations to the same history

25 October2026. MC01,MC05,MC06,MC09,MC10,MC24,MC28. S2-S4.
Baseline: accepted cash-plus-closing-balance histories and the existing
RetainedStatementNetwork/1. Version4.34 remains not_ready; E3 deferred.

Skeptical audit: another closing-only wrapper would repeat the same incomplete
evidence. The existing source network already supplies opening snapshots,
equity bridges, same-date identities and period relations. Reuse it directly
with the typed history attachment; do not implement those source semantics
again. A candidate can satisfy closing statements and fail actual reported
openings. Such rejection motivates a history/mapping repair, not mission failure.

Question: which source constraints invalidate the currently supplied histories,
and can the general same-context network/history interface preserve every
selected equation while keeping unmapped quantities and unknown literals?
Primary criterion: exact source-network/complete-history conjunction, matched
replay and a discriminating opening/equity conflict; source constraints must not
be discarded merely because their quantities lack history mappings. Compare
with unchanged RetainedStatementNetwork/1 and TypedHistoryMeasurementAttachment/1.

Default/assumption audit: all source population, rounding and identity premises
remain explicitly proposed; optional choices stay caller supplied. History
dates, bounds and templates retain their authored provenance. Equal dates,
labels or displayed cash values do not imply equal populations. Inspect the
retained opening cash difference before attaching both to one field. Do not
invent restricted cash, residual assets or balancing accounts to force a fit.

Vetoes: changed source bytes, lost selected relations, implicit context merge,
fabricated source amounts, or interpreting resource exhaustion as empty target.
Repair triggers: candidate conflicts, missing population facts, or unsupported
method shapes. Explanatory only: solver witness choice, timing and counts.
No actual-history, full-source, standards, probability or forecasting claim.

1. Inspect retained network definitions, opening-cash quantities and equity
   movements; document precise candidate/mapping failures.
2. Compose one network parent with separate supplied histories by exact value
   context, preserving all constraints and unmapped observations. Avoid
   cross-context equations unless an explicit supported conversion exists.
3. Test preserved closing-only behavior, additional opening/equity conflicts,
   missing premises/literals, wrong context/scale, altered sources and budgets.
4. Record full exchanges and replay. Use the actual failures to specify the
   next smallest reconstruction or population-mapping repair and continue it.

CPU Python3.11.15/Z3 4.16.0; GPUs hidden. No install/GPU/paid review.
Artifacts: data/accounting-master/retained-network-history-20261025/.
S1-S5 partial,S6 held,S7 deferred. Actual populations remain a substantive gap.
