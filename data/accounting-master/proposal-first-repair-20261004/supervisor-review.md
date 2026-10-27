# Supervisor review — proposal-first controller repair

4 October 2026, Hong Kong. Scope: scheduler, persisted state, worker modes,
review recovery, registered checks, accepted evidence and proposal readiness.
Independent sequential controller reviews are recorded in run
`20261003T190824-e9275ee2`; their results were still pending when this note was
written. This note is not an independent review receipt.

The pre-edit audit rejected reusing P14 as the proposal gate because P14 depends
on implementation, and rejected changing historical phase contracts because
that would invalidate their original acceptances. The separate workflow map and
new proposal stages remove that dependency cycle. Migration verified all 15
old contracts and phase records unchanged and all ten acceptances reusable.

Code inspection and executed regressions found and repaired these issues:

| Finding | Repair and evidence |
| --- | --- |
| A held product phase could otherwise be called directly despite scheduler filtering. | `phase_block` is enforced in selection, `execute_phase` and `worker`; both bypass paths are tested. |
| A worker-written readiness flag or old acceptance might be mistaken for proposal approval. | Readiness is recomputed from current phase contracts, prerequisites, structural checks, exact inputs and independent review/process files. Product execution remains disabled even in the positive readiness test. |
| A reviewer returned PLAN and retry reused its output destination. | Role-specific schemas, strict role validation and one bounded fresh-directory review retry preserve the rejected response. |
| Failed read-only calls could truncate evidence before the supervisor handled the failure. | Worker-finally inventories enforce read-only and phase write scopes, including exception paths; an integrity failure cannot be retried as a provider error. |
| Empty captures or top-level pass with a failed subcheck could appear successful. | The registered checker owns a fresh stdout capture, hashes it, checks nonzero tests/subchecks/errors and validates declared artifacts. |
| Compacting a new phase packet dropped the previous outcome and next actions. | Restore the last outcome, phase states and proposal-phase next actions; the existing cross-phase continuation tests pass. |
| A completed reviewer process or a referenced rendered page could be omitted from readiness evidence. | Gate requires the review process in accepted hashes and all current structural-check inputs bound by the final accepted phase; negative tests exercise both omissions. |

Validation before execution: 127 controller tests and 14 proposal evidence tests
passed. The master's own startup reran the combined 141 tests successfully.
Tests use synthetic documents to check missing coverage, changed sources,
invented quotes, omitted failure behavior, stale prerequisites, build/render
bindings and unresolved proposal decisions. Those fixtures do not validate prose,
accounting, sources in the real proposal, or human acceptance.

Inspection limits: workers are trusted cooperative processes; scope checks
detect changes after a call and preserve prior bytes, rather than providing
malicious-process containment. Semantic adequacy still needs substantive review.
No product source was edited by this controller repair; existing prototypes and
their domain limitations remain evidence for the proposal.
