# Verify saved region proofs before queue completion

26 October2026. W04/W12/W16; MC11/12/24/25/26/28/33/34.

Question: can a saved job be removed from the pending set only when its exact
scope and complete region partition have been checked? Comparator: the accepted
exact-region-certificates-20261026/attempt-01 archive, the independent full-state
sequence oracle, and the original3872 job roster. Re-read the saved archive
without importing or rerunning the accepted writer. Check its hash, each job's
scope/instruction/partition proof and full financial leaf formulas again.

Create a pure finite queue with an immutable expected scope and per-job proof
fingerprints supplied by the verified archive. Pending and certified IDs must
partition the complete expected roster; a completion without the exact saved
proof fingerprint refuses. Pause/resume is JSON interchange under this verified
registry. Validation of the registry has a separate cost from new job budget.
No original concrete-checkpoint schema is silently upgraded, and no claim of
crash durability, authentication, efficient storage or policy equivalence follows.

Primary criterion: exact archive revalidation plus identical final queues for
uninterrupted, zero-budget and mixed-budget continuations, with source/roster/
proof mutation rejection. Vetoes: changed method/source scope, missing child or
job, invalid proof, false completion, stale fingerprint or inconsistent partition.
Counts/runtime are explanatory. Failures trigger local repair unless evidence is
corrupt. Use at most120seconds CPU per attempt and preserve failed attempts.

Assumptions: the finite roster and two-rate model are inherited selected premises;
the caller's expected scope comes from the verified source lock, not the saved
record. JSON is an interchange convenience, not a storage security mechanism.
Full registry revalidation is intentionally a correctness baseline. No runtime
speed/default claim is made. The final frontier can become empty for this scope
while all broader symbolic/domain/policy packages remain open.

Skeptical audit passes: a forged self-consistent queue hash is insufficient;
validation is bound to an externally supplied verified registry. An empty
pending list alone is not a certificate. The prior concrete queue remains
unchanged and its unresolved regions remain historical; this is a new separately
verified queue with new acceptance semantics. No installs, GPU, workers or fees.
Artifacts: exact-region-certificates-20261026/queue-attempt-01/.
