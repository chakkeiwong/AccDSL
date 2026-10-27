# Follow-up controller repair

The independent review of run `20261005T083051-60af77f3` identified six further
accidental-failure paths. The campaign stopped before any P16 attempt. This
repair addresses MC25/MC27/MC33/MC34 and preserves proposal-first scope.

| Finding | Repair | Executed evidence |
| --- | --- | --- |
| Prepared worker inputs excluded from ordinary inventory | Pin prepared packet, recovery, schema, prompt, budget and completed configuration records through every launch exit | Review/edit mutation, truncation and deletion cases, on successful return and interruption |
| Unregistered configuration subprocesses | Use registered bounded process groups, separate JSON stdout/stderr, original worker cutoff | Actual fake CLI success; SIGINT/SIGTERM after registration leave no survivors; startup reserve test |
| Historical success published as current readiness | Reload and check current protection/readiness under runner lock before publishing; preserve the historical invocation | Serialized invalidation is retained as historical success and current supervisor-repair status |
| Runtime event/process files exempted without checking expected changes | Track exact supervisor writes, check before and after updates, reject changed/deleted bytes | Review/edit overwrite, truncation, deletion and creation cases |
| Injected checks bypass live artifact checks | Require explicit test-only injection in an isolated root; reject it in the live root and at dispatch | Live construction/check/run rejection cases |
| Built-in validation used returned data rather than primary deliverable | Load primary JSON, require equality, validate loaded data and bind primary bytes before acceptance | Malformed and different-valid primary JSON both produce FAIL for P00/P01 |

Commands:

```text
python3 -m unittest discover -s tests -p test_accounting_master.py
python3 -m unittest discover -s tests -p test_accounting_proposal_current.py
```

Final results: **198 controller tests passed in 45.799 seconds; 20 proposal tests
passed in 2.059 seconds**. Logs are retained beside this note. The first controller
run had one outdated synthetic stop fixture, repaired to use the actual CLI's
`requested_at` format; the original failed log is preserved.

Skeptical post-review: a valid newly created stop request is permitted external
operator input and prevents accepting a worker response. File hashes cannot
attribute it to a hostile same-user actor; that threat model is not claimed.
Checked event/process updates concern accidental changes in this trusted
sequential workspace. Current readiness can differ from a historical success;
the former controls continuation, while the latter stays in the invocation
record. No product code, P16 content or accepted evidence was changed.

| Decision | Primary criterion | Veto checks | Main uncertainty | Next action | Limit |
| --- | --- | --- | --- | --- | --- |
| Obtain fresh startup review | Current controller/proposal suites pass and every new finding has a focused regression | Accepted/corpus/external source hashes match; saved P16 review valid | Independent review of these follow-up changes is pending | Record supervised recovery, rerun exact campaign command | No P16 acceptance or accounting/forecast validity |

Both most recent controller-only invocations stopped before any phase attempt.
The consecutive-no-progress threshold is therefore being acknowledged through
an explicit supervisor-repair boundary, preserving its prior count and all run
history. This allows review of changed, tested code rather than an unchanged
automatic retry. The original 48-hour deadline and editable retry limit are
unchanged. See `resume-record.json` for exact hashes, budget and transition.
