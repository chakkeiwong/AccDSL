# Restartable full-state annual inventory execution

25 October 2026. S3–S5; MC11/15/23/24/25/26/28/35, G2/G18.

## Research intent and evidence contract
Question: can a local interrupted annual run resume without losing stock/tax
history or applying an operation twice? Mechanism: a single-writer SQLite store
with one immutable program/root record and complete atomic operation snapshots.
Baseline: uninterrupted frozen AnnualInventoryProgram/1 execution. Exact equality
of the complete financial result, trace, retained failures and report is primary.
Reopen validation, source/request identity, event order, stock/tax invariants,
transaction atomicity and refusal retention can veto promotion. Timing/size are
explanatory only. File creation or clean SQL alone cannot establish correctness.
No claim of multiwriter safety, power-loss durability, hostile-file authenticity,
performance improvement, arbitrary-size support or accounting admission follows.

## Skeptical audit
P07 persists a different Engine and numeric canonicalization, so its state or
serializer must not be silently substituted for the 26-account annual book.
Use explicit new schema/profile and lossless canonical JSON for the present
finite evaluator. The runtime is pure and has no external side effects. Reopen
may deterministically replay the committed prefix to validate saved bytes;
this is an integrity check, not a performance-saving checkpoint claim. A digest
alone cannot detect rehashed financial tampering. Preserve the complete ordered
program so changed future operations also invalidate the request identity.
A stop is terminal for that immutable request; repair creates a distinct run.

## Defaults and assumptions
One local writer is the supported scope; SQLite transactions provide the atomic
boundary. Use foreign keys, explicit schema version and no dynamic SQL names.
A caller-supplied path selects a dedicated database; reject an incompatible
existing database without overwriting it. Preserve exact strings/Unicode and
rational representations; do not reuse P07 normalization. Bind source modules,
source-lock digests and request before operations. Budget counts new operation
attempts, including a refused operation, not replay checks. Zero budget may
initialize/validate the root but commits no operation. All assumptions are
engineering choices for this bounded adapter, not mission-wide requirements.

## Staged execution and repair conditions
1. Inspect source invariants, full result assembly and existing P07 transaction
   behavior; finalize a small schema and explicit failure model.
2. Implement init/inspect/advance/reopen with complete snapshot records in one
   transaction per attempted operation. Store refusals and pending suffixes.
3. Check uninterrupted versus chunked execution across inventory sale,
   assessment, measurement, carry and second-period sale; retain all 26 accounts.
4. Test reopen in a fresh process, before/after-commit process exit, idempotent
   retry, zero budgets, stopped requests, changed inputs/dependencies, corrupt
   snapshots including rehashed tampering, and incompatible schema rejection.
5. Record exact commands, environment, manifests, logs, test cases and decisions;
   freeze only after replay and regression checks pass. Preserve failures.
6. Integrate checked behavior and refresh full coverage before the next repair.

Initial smoke: one partial sale, reopen and compare exact saved book. Every
candidate failure triggers a targeted repair unless the input/root, transaction
assumption or scientific target is invalid. No background campaign, external
outreach, GPU or forecasting. CPU-only deterministic controls; random seeds N/A.
