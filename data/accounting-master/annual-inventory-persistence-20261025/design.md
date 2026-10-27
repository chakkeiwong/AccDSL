# AnnualInventoryStore/1

One dedicated local SQLite database stores one immutable complete runtime request,
its exact canonical SHA256, the evaluator/source-lock identities and one initial
root result. An append-only checkpoints table stores each attempted operation's
full result, attempt index, result hash and predecessor hash. Sequence zero is
the evaluated root with no annual operations. No account projection is allowed.

advance(max_operations, expected_cursor=None) executes at most the explicit number
of new attempts. Zero checks state but advances nothing. expected_cursor makes a
retry of an already committed chunk observational: if current cursor is ahead,
return its checked current result without applying another operation. A future
cursor is invalid. Calls without expected_cursor request another chunk. A failed
operation increments attempt count but leaves the successful trace unchanged;
the stored refusal and full pending suffix are terminal. Completed or terminal
stores are idempotent under further advances.

While operations remain unattempted the result status is paused_provisional.
All other result fields, including report, root, full request identity and pending
operations, use the annual runtime's meanings. On final completion or refusal,
the complete result equals uninterrupted runtime.run(request). No incomplete
fiscal year is relabeled accounting-admitted.

Reopen validates the schema, source identity, complete request, row order, every
hash and predecessor, then independently recomputes each committed prefix through
the frozen runtime. It does not execute uncommitted future operations. This
cost grows with prefix count and is deliberately not a scaling claim. New steps
use runtime.transition with the loaded full book. SQLite commits the complete
snapshot atomically. Injected exit checks cover process termination immediately
before and after commit; they do not simulate hardware power loss.

Expected source/request mismatches, rehashed tampering, incompatible databases,
noncanonical JSON, wrong cursor/budget and schema drift reject explicitly. Existing
incompatible databases are inspected before PRAGMA changes or schema writes.
UTF-8 text and exact rational strings are preserved. Only a single local writer
is supported; external authentication, migration, arbitrary corruption recovery,
family-level scheduling and multiwriter contention remain separate work.

An interruption before initial commit may leave an empty, schema-version-zero SQLite file. An explicit complete request may initialize that empty target; reopening without the request rejects because none was durably recorded. Incompatible nonempty databases remain unchanged. Initial-after-commit exit retains the root record.
