# Local supervisor review and execution decision

4 October 2026, Hong Kong. Scope: the diff in refresh.patch against the preserved
before/ files. This is a local supervisor review of a prompt/plan refresh, not
a new independent review of the complete controller.

The confirmed defect was asymmetric plan preparation: initial execution removed
held historical detail, but both repair paths restored the whole plan. The new
refresh_worker_plan method calls the existing authoritative refresh, retains
workflow, gate, phase states and outcome, and includes issues, residuals and
next actions for active proposal phases. It links the full generated plan.
Initial execution, timeout/partial continuation and failed-check/result-review
repair all use this method. The controller-review scope includes the helper.

The new regression traverses both repair paths in one execution: a timeout after
writing partial work, then a completed write whose check fails, followed by a
successful repair. All three planning calls retain the active instructions,
exclude held detail and receive increasing generations. The complete plan still
retains the historical residual. This checks actual retry behavior rather than
only reproducing the helper's dictionary construction.

The prompt adds incremental substantive writes and an explicit instruction to
use the existing checks/response reserve. This can reduce lost handoffs; tests
do not establish that future model workers will always obey it or finish within
their limit. The previous timeout also involved a large task; focused task
selection and saved partial rows remain necessary. No timing limit was relaxed.

Reviewed interfaces: full state persistence, original phase criteria, workflow
policy, worker sandbox/approval arguments, process cleanup and hash validation
are unchanged. A partial or timed-out result still cannot grant acceptance.
The update to P15 progress replaces stale absent-file assertions with inspected
current files and the remaining work; it does not create coverage or acceptance.

Validation: 145 controller tests and 17 proposal tests passed. The existing
startup rerun remains required. All 868 release/accepted evidence hashes match,
and all fifteen historical phase records are unchanged. Every required direct
master command passed both dedicated and effective policy checks; the dedicated
rule did not allow the three unrelated commands. No global rule, tool install,
worker grant, credential or model setting changed.

Decision: resume the existing proposal campaign with the direct refresh and run
commands in docs/plans/accounting-master-refresh-20261004.md. Preserve the two
earlier independent reviews and their adjudication as historical review evidence.
Bind this local review and its checked diff to the current controller receipt,
with its actual provenance. P15 is incomplete, P16–P19 are pending, and product
implementation remains disabled.
