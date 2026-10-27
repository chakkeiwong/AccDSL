# Recovery and skeptical audit — 27 October 2026

Recovered candidate 5.48 and active bank continuation plan from the saved master.
The earlier coupon writers have already succeeded and remain untouched. Existing
dirty changes are unrelated and preserved. No blanket git commit is appropriate.

Audit passes for the bounded read-only question in contract.md. The native source
already retains uncollected_contract, writeoff_contract, and unknown legal
forgiveness. This work makes their dated conservation explicit; it does not repair
a fabricated loss of those fields. Inspected native event ordering, collection
removal, proportional write-off, zero remaining entries, estimate replacement,
and event_after_close refusal before implementation.

Main risks and early checks: (1) confusing nominal amounts with carrying values:
use explicit nominal field names and never alter native reports; (2) balanced
totals concealing date errors: compare each due date at every stage; (3) shared
oracle error: freeze an authored endpoint table and independently accumulate
movements against native snapshots; (4) invented recovery or forgiveness: no new
receipt or journal and explicit unassessed legal status; (5) accidental overwrite:
new directory and exclusive attempt creation. No forecast, legal-policy change,
external contact or dependency installation is part of this unit.
