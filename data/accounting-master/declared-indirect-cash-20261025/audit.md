# Indirect cash-flow classification audit and repair log

25 October 2026. The evidence contract is recorded before implementation in
docs/plans/accounting-declared-indirect-cash-20261025.md. The comparator is the
unchanged verified declared-program report, with independently specified profit,
adjustment and operating-cash arithmetic. No numerical residual is an input.

The first focused suite ran 12 tests in 304.649 seconds: nine passed and three
errored while constructing new fixtures, before their bridge calculations.
The examples assumed a role named ppe; the existing chart uses plant_cost.
After correcting that role, registry validation exposed missing account_classes
metadata for the newly added method roles. The fixtures now declare those
classes from their explicit book. No frozen engine or pre-existing evidence
changed. The first failed log remains /tmp/accdsl-indirect-tests-01.log.

A targeted rerun now confirms: the noncash asset/debt event has zero profit and
cash; depreciation of 5 has profit -5 and adjustment +5; offsetting gross asset
postings remain visible despite zero net movement. The disposal-gain case is
unsupported by the deliberately narrow account/category contract, with
nonoperating_reconciliation:disposal_gain.1. Its original recorded report still
has profit 2 and investing proceeds 12. This is a missing decomposition in this
candidate, not an invalid transaction or evidence against indirect reporting.
The next repair must classify nonoperating profit components explicitly; it
must not invent a residual adjustment or mislabel the whole asset movement.

The adverse test exchanging working-capital and noncash categories deliberately
still reconciles. Its classification_admission flag remains false. This is a
counterexample to semantic uniqueness: arithmetic can reject some policies,
but it cannot establish their accounting correctness. It is explanatory
evidence, not a promotion criterion for accounting policy.

Full deterministic conformance, source locks and read-only replay remain
required before accepting this finite reference. These tests may exceed five
minutes because they replay complete verified traces; logs stay on disk and
only bounded summaries return to the session. No GPU frameworks are imported.
Use the current project Python environment, without installation or GPU tests.

An older financing-schedules comparison.json contains literal trailing backslash-n
bytes and is not valid JSON. Its immutable bytes are left unchanged and it is
not this increment's comparator. Current results are obtained from the checked
program and exact supplied fixture source; broader old-artifact repair requires
a separately preserved successor record.
