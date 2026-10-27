# Conditional history to opening: contract audit

25 October 2026. MC02/05/08–13/15/17/19/24–28/34/35, S2–S4.

Inspected typed_history_measurement_attachment_v1.prepare/replay_witness and
typed_affine_history_v1.replay_witness, their existing monetary/stock examples,
CompanyBook/1 validation, report opening checks and typed-memory declarations.
The attachment rechecks all supplied history and measurement constraints for
an explicitly provided witness. Its snapshots contain exact signed accounts and
numeric memory; source admission and operational-precondition checks remain false.
Two valid histories can share closing cash 15 while retaining cumulative sales
5 and 7. Selecting one must retain its witness identity and the parent family.

Material mismatches: history context includes accounting basis while the company
book carries synthetic case/mode; the history snapshot date is an end-of-day
date, whereas the report opening is the first day of a fiscal period; history
memory contains numeric fields and cannot invent customer IDs or payment dates.
These are explicit mapping obligations, not permission for coercion.

Chosen bounded adapter: accept a complete attachment definition, budget and
selected witness; independently replay it; map every source account exactly
once to a uniquely classified target account; map every numeric memory field
exactly once to a nonoverlapping path. Preserve monetary sign, dimensions and
scale. Entity/book must match. The target is explicitly synthetic, with a
declared case ID; retained source context and a stated bridge premise preserve
basis metadata without claiming conversion. Require unit monetary scale.

Select only the final declared snapshot, and set the opening to the next date
under an explicit no-unrecorded-boundary-event premise. This avoids silently
feeding a later-constrained witness into an earlier opening. It still establishes
no investor information cutoff or forecasting admissibility. Income/expense
balances must already be zero; refuse rather than invent closing entries.
The exact source family, selected witness, assumptions, obligations and
exclusions remain in a companion record. Missing premises yield unresolved;
remaining target obligations yield a candidate opening, never execution clearance.

Acceptance: both retained valid monetary witnesses give exact cash/equity 15/-15
but memory 5 versus 7, on two charts. Exact stock units/money map separately.
Invalid witnesses, omitted/duplicated fields, wrong contexts/scales/dates,
nonzero temporary accounts and overlapping paths refuse immutably. Original
attachment and book tests remain the baseline. Report output is a check of the
declared balance mapping, not historical truth. No statistical comparison.

Skeptical/default audit: no balancing plug, unit conversion, invented invoice,
probability, family completeness or source admission. The final-snapshot and
next-day policies are explicit bounded choices. Their early checks are date
and nonzero-temporary-balance refusals. A valid witness that leaves operational
obligations unresolved remains useful for provisional representation; it cannot
authorize execution. Changed frozen sources or failed replay veto this adapter.
No material unresolved human decision blocks this internal increment.
