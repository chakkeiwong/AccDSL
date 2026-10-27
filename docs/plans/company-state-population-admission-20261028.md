# Preserve unresolved openings before population inspection

28 October 2026. T01/T03/C04; MC04/08/09/13/18/19/28/33/35.

The current claim and asset inspectors work from complete supplied openings or
an operation-level partial execution. A skeptical entrypoint review finds a
different case: native validation can return unresolved before any event when
an opening claim amount, asset life or global method input is unknown. Reading
those fields as fractions before checking that refusal risks an exception or
fabricated empty population. Audit the boundary before broader reuse.

Question: can a single scoped population entrypoint preserve the exact native
result when no opening is executable, while reproducing both existing
inspections on complete or partially executed paths? Baseline is unchanged
native execution and current claim/cohort outputs. Do not alter their protected
successful run inputs; add a separate admission adapter.

Primary criterion: unknown opening/global fields return the native unresolved
reason and obligations with population inspection explicitly not performed;
invalid/unsupported inputs preserve their native classification. No empty
population is represented as complete. Complete paths and event-level partial
paths reproduce their prior full inspections.

Vetoes: unhandled missing input, wrong classification, invented zero, discarded
obligation, changed source or reinterpretation of an invalid opening. A failing
probe stops the affected case and triggers repair, not abandonment of the
construction program. Counts are explanatory. CPU exact native validation only;
no stochastic run, empirical inference, new default, source admission or
exhaustive whole-company claim.

Material choices: existing native statuses remain authoritative. A valid JSON
object with a wrong parent digest must be refused before execution. Missing
opening claim/asset facts must not be inferred from aggregate accounts. The
entrypoint returns full native context plus unknown population rather than
pretending that zero successfully inspected records means an empty company.

Command: python3 -B data/accounting-master/company-state-population-admission-20261028/check_admission.py --output data/accounting-master/company-state-population-admission-20261028/attempt-01
Preserve full positive/adverse results and manifest under that directory, then
update the common interface note and live program.
