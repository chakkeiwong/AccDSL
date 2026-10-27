# Supervisor review of the worker timing repair

Decision: proceed with one normal bounded P16 continuation. This is supervisor
finding adjudication, not a fresh independent-model controller review. Existing
per-phase plan and result reviews remain required.

The inspected change introduces a read-only clock helper and a protected budget
record before worker inventory capture. Admission still requires the full
configured worker allowance and verification reserve. The budget starts before
inventory/configuration/prompt work. Both startup queries and the launched
process use the same absolute cutoff, so overhead cannot restart the timer.
The current host boot is checked by the helper. All timing decisions use
`time.monotonic`; `measured_at` remains provenance. Controller review packets
include the new helper where timing/lifecycle interfaces are reviewed.

For editable work, the save/check instruction starts at second 600, response
instruction at 780, and enforced cutoff at 840 of a nominal 900-second window.
The save and response instructions depend on worker cooperation. The process
cutoff does not: late observation of even an exit-zero response is timeout, and
ordinary process-group cleanup still precedes file checks. No synthetic success
is inferred from saved files. The new budget record is outside every phase's
declared write scope and stays in the normal before/after inventory.

Evidence: 164 controller tests and 17 proposal tests pass. The seven new
regressions cover civil-clock drift/jumps, invalid/stale clocks, the actual
read-only clock command, attempted budget mutation on success/error, startup
delay at an absolute cutoff, an uncooperative sleeping process, and timely
PARTIAL with a saved subsection despite incomplete whole-contract checks. The
startup-reserve regression now checks the effective early cutoff. The first
full test run found that an isolated controller fixture did not copy the new
module; repairing that fixture made the real internal verification test pass.
The initial failure log is retained. `git diff --check` passes.

All 912 original protected hashes and every accepted phase's evidence, including
P15's 228 files, match. The exact entrypoint still matches its existing narrow
allow rule. No grant or policy was broadened. Old accepted repair plans and the
frozen product-design checkpoint remain unchanged. See `validation.json` and
the baseline/diff/test logs in this directory.

The main uncertainty is behavioral: a model may ignore clock checks, choose too
large a subsection, or take too long to formulate its final response. Earlier
termination could then increase timeouts. The next real P16 attempt must be
examined for clock use, actual saved content, timely response and honest phase
status. Unit tests establish the engineering mechanism, not improved model
throughput or a complete proposal. Full P16 checks currently fail at the missing
contract inventory; this is an expected drafting condition and leaves partial
review pending. It does not prevent a fresh reviewed substantive plan.

No unresolved material code defect was identified in the changed launch,
inventory, deadline, response-validation or continuation paths. The earlier
controller review findings remain covered by the full regression suite and
their preserved review evidence. Final phase acceptance, accounting validity,
forecast validity, proposal readiness and human acceptance are not concluded.
