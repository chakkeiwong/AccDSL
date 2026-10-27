# Bounded review handoff repair

The run stopped at 2026-10-04 21:55 UTC after saving the uncertainty contract,
chaining repair and author assessment. It used four editable attempts and had
zero timeouts. P16 was not complete: four proposed contracts existed, with five
contracts, the initial profile and fourteen decisions still unfinished.

The controller incorrectly gated a bounded result review on the phase-wide
checker passing. That checker correctly rejected the incomplete nine-contract
architecture. Plans then requested independent review, but the loop assigned
another repair worker. The final worker reported the dispatch mismatch and the
campaign stopped with no eligible phase. The problem was control flow, not an
external source dependency or an uncertainty-method rejection.

The repair dispatches `bounded_partial_work` reviews despite phase incompleteness,
preserves checked pending reviews for read-only resume, records their terminal
verdict and next actions, and permits a resumed review to advance to planning
without manufacturing an edit. A bounded review retains its scope even if a
later checker passes. Full-phase acceptance still requires all declared criteria
and an independent full result review. The explicitly configured reviewed_scope
policy for other work is unchanged.

Five focused regressions cover the actual failure, review resume without an
editable worker, stale evidence, rejection routing and prevention of accidental
full acceptance. An older test expected the now-repaired skipped-review behavior;
its assertion now requires the bounded review and preserves the next substantive
task. All 180 controller tests and 17 proposal tests pass. Exact commands,
environment, input hashes and test logs are retained in `recovery.json`.

The saved, approved uncertainty-review plan is queued using the current proposal
checks and exact file hashes. Old attempts, responses and continuations remain
intact. The original campaign deadline is unchanged. Startup must review the
changed controller before dispatching the independent uncertainty review. No
acceptance is inferred from the repair worker's earlier author assessment.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | What is not concluded |
| --- | --- | --- | --- | --- | --- |
| Repair review routing | Incomplete-phase partial results reach the independent review role; unavailable reviews resume without editable work | Focused and existing tests pass; startup controller review remains required | Model/service behavior and semantic reviewer findings | Run the same approved campaign entrypoint | P16 acceptance or uncertainty correctness |
| Reuse the saved uncertainty work | Current checks and evidence hashes retain its approved review scope | Preservation checks pass; structural phase incompleteness remains | Actual independent review outcome | Review, then repair findings or specify accounting | Full proposal readiness, product implementation or forecast validity |

Post-edit skeptical review: the critical alternative was a scope leak on resume
when fresh checks passed. The explicit bounded-resume branch and regression
prevent that promotion. The remaining weakness is that deterministic fault
injection cannot establish model-review quality; actual source and semantic
inspection must still occur. A stale input or integrity mismatch invalidates
resume, and a substantive REVISE determines the next repair. Controller changes
invalidate its former review; the standard startup review is not skipped.
