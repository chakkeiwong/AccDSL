# Native persistence audit — 25 October 2026

The baseline is direct full AnnualInventoryProgram/1 execution. P07's older
Engine and numeric normalization are wrong for this book; retain its transaction
pattern but no state conversion. Use complete snapshots, exact Unicode/string
JSON, source lock and immutable full request. A new operation executes once via
runtime.transition from the current validated state. Reopening replays committed
prefixes only to verify them; no replay performs external side effects.

A paused run must not claim completed operations. Expose paused_provisional in
the saved result and preserve the original remaining suffix. Final or refused
results must equal the direct runtime exactly. Root-unavailable results are
terminal without operations. A recorded refusal is terminal for the immutable
request; changed assumptions require a new store. Attempt count includes the
refused operation, while trace length counts successes. Test this distinction.

Transaction boundary: complete result, attempt cursor and receipt in one row.
Before-commit exit must leave the prior row; after-commit exit must retain one
new row. SQLite FULL/DELETE settings are inherited engineering choices for
local single-writer tests; passing process-exit tests does not establish power-
loss durability or multiwriter correctness. Hashes establish identity, not
hostile-file authenticity. Recomputed snapshots reject rehashed mutations.
No material unexamined default remains for this finite engineering contract.

Pre-freeze review added the initialization transaction to the crash model. A version0 empty target can be retried only with an explicit request. Two fresh-process exit tests now cover the initial commit as well as operation commits; preserved earlier passing test records are in review-revision-01.
