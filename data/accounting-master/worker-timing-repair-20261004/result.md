# Timing repair and P16 continuation result

The timing repair is implemented and verified. P16 gained the finite
representation definitions and one paired MA02a example. P16 remains partial;
P17–P19 remain pending and product implementation remains held.

## Executed work and outcome

The saved baseline and pre-edit controls are in `baseline.json` and `before/`.
The reviewed plan is `docs/plans/accounting-worker-timing-repair-20261004.md`;
the code review is `review.md`. The changed controller, clock helper, tests and
plan are recorded in `change.patch`. The initial integration-test fixture failure
was repaired by copying the new dependency into its disposable checkout; its
failure log is retained. Final suites pass 164 controller and 17 proposal tests.
Both live runs reran all 181 successfully. The exact entrypoint allow rule matched;
no rule, standing grant, configured model or provider was changed.

Run `20261004T142931-d2372fef` used the normal command. The plan and independent
plan review completed, but the editable process returned exit 1 after an upstream
disconnect followed by `model_not_found`, at 620.113 seconds. There were no new
files and no timeout. `first-live-run.json` preserves the failure classification
and retry decision. Policy-named local route diagnostic files were absent; the
attempted official documentation pages were inaccessible. No routing conclusion
or model substitution was inferred from that failure.

Under the user's subsequent “continue”, run `20261004T151640-e24fa727` executed:

```text
python3 /home/chakwong/python/AccDSL/scripts/run_accounting_master.py run --max-seconds 4050
```

The initially calculated remaining allowance was 4,121 seconds; 4,050 was used
at launch to account for elapsed preparation. This stayed within the normal
7,200-second continuation boundary established before the first run. Its fresh
plan narrowed work to definitions and one pair, and independent review returned
AGREE without issues. The editable worker saved 10 new files and updated the
three P16 deliverables, with no deletions. It exited 0 and returned valid PARTIAL
after 802.629 process seconds. Startup took about 1.989 seconds; process and
packet absolute deadlines match exactly, with about 35 seconds to spare.

The worker consulted the monotonic clock, saved its initial checkpoint early,
and saved substantive comparison text and fixtures before the finish interval.
The 780-second response instruction was not a guaranteed completion boundary;
the actual final response arrived before the enforced 840-second cutoff. This
is the first observed timely editable PARTIAL after this repair. It establishes
that the mechanism works in this attempt, not that all model timeouts are fixed.
The reduced scope and changed service outcome prevent isolating a causal effect
of the clock repair alone.

## Proposal evidence and limits

The saved comparison is
`docs/design/proposal/architecture/uncertainty-representation-comparison-v1.md`.
Its fixture contains separate family-linked and self-contained numerical
representations with explicit mappings to the same semantic coordinates and
outcomes. The self-contained form embeds its numerical definitions but retains
external evidence and admission dependencies. Exact rational masses are 1/2,
1/3 and 1/6. Both expected receipts preserve synthetic-assumption status and
leave empirical justification unestablished. Neither architecture is selected.

The one-off document diagnostic passed all 205 checks. The supervisor inspected
the comparison and diagnostic and reran it into `representation-recheck.json`;
all 205 pass again. This is bounded consistency verification, not an independent
substantive P16 result review or a runtime conformance result. It checks concrete
input identities, mappings, context equality, probability totals, reference
closure and separate receipt statuses. The full phase checker passes 133/134
checks and still fails only the missing whole-contract inventory. It has not yet
run individual-contract/profile checks. The controller's `completed_partial_tasks`
counter stays zero because it also requires passing full-phase checks; the saved
worker response nevertheless is a real, timely PARTIAL.

The retry ended cleanly with `budget_exhausted`: 2,495.5 seconds remained versus
the unchanged 2,520-second admission requirement for another complete cycle.
No retries were consumed in that invocation, and there were zero timeouts.
The runner lock is free and the last child has no survivors. No additional
invocation was started with insufficient admission time.

Final preservation is in `final-verification.json`: all 912 original protected
hashes, 725 release hashes, eleven accepted-phase evidence sets, 145 checker
inputs, 203 continuation inputs, nine representation inputs and 59 architecture
reference occurrences match. Counts overlap. P15's 228 evidence files remain
unchanged, and the current controller-review receipt still matches its controls.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain timing repair | Deterministic regressions and one timely real PARTIAL pass | No integrity/ownership failure | Whether larger or slower model tasks obey finish instructions | Keep monotonic checks and bounded saved subsections | General timeout elimination or throughput improvement |
| Retain MA02a subsection | 205 consistency checks pass | Full P16 criteria still incomplete | Independent substantive assessment and broader operations | Add overlap and projection comparisons | Architecture selection, accounting/forecast validity, runtime implementation |
| Defer next cycle | Remaining allowance below full admission | Budget continuation stop | Further work requires a fresh bounded invocation | Resume saved next task under the normal command | P16/P17 completion or proposal readiness |

Next work is MA03a overlap (5/6, 1/2, intersection 1/3, union 1) and MA04b
projection with retained elementary identities, then remaining rejection
semantics and uncertainty operations. Six full contracts, initial profile,
integrated acceptance/dependency order, fourteen decisions and the E05 real-source
obligation remain open. Human acceptance remains pending.
