# Exact-byte archive pre-implementation audit

Question, original comparators, criteria and nonclaims follow
accounting-simulator-evidence-archive-20261024.md. This is an optional design
reference under S2-S4, not production S6. Seven frozen inputs are protected.

Additional audit finding: P07 Store commits its initialization before an archive
marker can be added. Creating the final file directly could leave an unrelated
unmarked database after interruption. Prepare a complete marked database in a
same-directory temporary file, close it, then publish with a non-overwriting
hard link. Inspect an existing file read-only before opening P07 Store; reject
unmarked or wrong-version databases without installing triggers or mutating them.
A crash can leave an unreferenced staging file; no automatic sweeping/deletion
of other files is authorized. Observed process recovery is the only durability
claim; filesystem power-loss behavior remains untested.

Material choices: one writer follows P07; SHA256 and immutable node dependencies
are reused for integrity rather than adversarial authenticity; exact bytes are
hex-encoded to avoid Unicode/order/rational normalization; roles are descriptive
and all semantic/admission flags remain false. All maximum record count, bytes
per record and total bytes are caller-supplied positive limits. JSON parsing
checks duplicate keys, finite numeric tokens and UTF-8 without rewriting bytes.
No unreviewed float-to-rational conversion occurs. Nesting/parser failures reject.

Primary evidence: byte equality, exact dependency edges, original native replay
for semantic separation, complete group visibility under interruption. Return
values cannot imply a model was executed. A data/proof mismatch triggers repair;
changed frozen sources stop continuation. No stochastic ranking, production
performance or general schema migration claim is made.
