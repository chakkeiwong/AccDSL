# Persistence, correction and recovery, proposed version 1

A completed accounting transition is one committed fact about a particular
book and branch. A lost network response must not post it again; a correction
must not rewrite what an earlier information view contained. This contract
addresses MC04–MC06, MC18, MC25, MC27 and MC33–MC35, especially G17/G18. It
specifies observable storage behavior. The examples are transaction traces,
not an implemented database or a durability experiment.

## P1. Ownership and retained objects

One transactional store owns immutable portable records, dependency edges,
review snapshots, branch heads, committed journals/state deltas, operation
receipts and continuation checkpoints. Original source bytes live in immutable
content-addressed storage. A metadata transaction may reference a blob only
after its exact bytes are durably available and verified. A crash between blob
creation and metadata commit can leave an unreferenced blob; it cannot leave an
accepted source reference to absent bytes. Existing originals are retained.
Exports, caches, Parquet tables and rendered reports are derivatives of a named
store snapshot, not additional writable truth. An export failure does not undo
a committed transaction or justify posting again.

Each branch has a stable `branch_key`, an immutable branch definition Ref and a
mutable head `(state_ref, generation)`. Its required `book_mode` is exactly
`synthetic` or `real` and is immutable for that branch. Posting profiles declare
the modes they support; authorization checks mode and evidence scope. Changing
mode requires a new branch and fresh admission, not an in-place relabeling.
The branch definition names its family,
evidence/model/scenario versions and projection namespace. A separately
commissioned hypothetical run uses a new projection namespace/branch key;
reopening the same run uses its original key. A branch revision, renamed run or
retry cannot evade an event conflict inside that namespace. Aggregating branches
requires the declared family/view semantics and never counts projections as
multiple realized transactions.

The initial local implementation is proposed to have one logical transaction
writer. Multiple clients may submit requests, but the store serializes commits.
Other implementations must provide the same atomic comparisons and isolation;
“single writer” is not permission to omit stale-state checks. SQLite is an
implementation candidate based on P07's bounded probe. Distributed consensus,
specific filesystem durability and physical media failure guarantees require
their own implementation and evidence; no document calculation establishes them.

## P2. Event commit and replay

The stable accounting lookup key remains the tuple `(entity_id, book_id,
branch_key, business_event_id)` from accounting-replay-contract-v1. Event version,
payload and expected opening state belong to the complete request fingerprint,
not the lookup key. The generic Core 0 run/event key is historical exploratory
evidence and does not override this rule. Legacy fixture digests are retained
through the import mapping in L1, never silently compared with portable digests.

For one requested event the store performs:

1. Validate the request's decoding, field shapes, exact reference closure,
   internal bindings and admissible historical context. Corrupt or inconsistent
   input fails before any receipt lookup. Validate independent fields in the
   declared stage order; do not derive fresh accounting assumptions here.
2. Read the committed receipt index under the stable key. An equal fingerprint
   returns the original immutable receipt with `additional_commit=false`.
   A different fingerprint yields `EVENT_ID_CONFLICT`, including when its event
   version differs. Replaying a valid historical request is not reassessment
   against today's source or method version.
3. For an absent key, compare both expected opening state and expected head
   generation. A mismatch returns `STALE_OPENING_STATE`. Assess treatment and
   construct the candidate journal, economic delta and closing state outside
   mutation. Arithmetic/balance alone cannot authorize a treatment.
4. In one transaction, recheck absent key and the same head comparison, validate
   the candidate dependencies, then insert the journal, delta, closing state,
   dependency edges and immutable committed receipt, and advance the head.
   Commit all or none. A competing identical commit returns the original
   receipt; a different fingerprint conflicts; a competing different event
   advancing the head makes this request stale. No speculative candidate is
   published as committed while the comparison is unresolved.

The observation returned with replay may identify today's branch head, but the
receipt's original opening/closing states, assessment and journal never change.
The four accounting domains in the existing fixtures—state, journal registry,
delta registry and committed receipt index—remain identical on rejection/replay.
Candidate scratch data and diagnostics are not members of those domains.
Rejected requests may append a separately typed audit record after validation;
it cannot appear in the committed event index or count as an economic transition.
If an operation promises an audit receipt and its audit write fails, report that
failure explicitly while retaining the established unchanged-domain outcome.

## P3. Crash ambiguity, resume and exports

A response has `commit_observation` equal to `committed`, `not_committed` or
`unknown`. A crash before the atomic commit leaves the old head and no new
receipt. A crash after commit but before acknowledgement leaves the complete
new head and receipt. The client's timeout alone cannot distinguish those cases;
return `unknown` with the original key/fingerprint and query/retry that identity.
Do not retry under a fresh event ID. Once storage recovers, receipt lookup
resolves the ambiguity. Missing/corrupt committed dependencies are an integrity
failure, not a reason to reconstruct an apparently similar receipt.

A search checkpoint atomically records the semantic manifest, partition identity,
completed/explored cells, preserved unresolved formulas/regions, frontier order,
budget used and resulting objects. A cell is not complete before its evidence
and frontier transition commit together. Resume requires the original semantic
manifest and partition/traversal identity. An increased explicitly supplied
budget is a new scheduling request linked to the old checkpoint, not a new
financial model. Changed source, context, method, scenario, family or ordering
requires a new applicable manifest and a stated reuse relation; it cannot reuse
an old suffix by position. Cancellation preserves the last committed frontier.

Immutable export manifests name every record/blob, format/decoder, digest,
root query/view and required reference closure. Stage an export in a temporary
location, verify its closure, then publish its manifest atomically. An incomplete
export is explicitly incomplete and cannot be loaded as a closed bundle. Import
verifies all referenced bytes before committing metadata; an unavailable
optional attachment remains a located coverage obligation. Missing required
closure rejects dependent use, even if the manifest itself hashes correctly.

## P4. Review, correction and invalidation

Source and review requests have their own idempotency namespace
`(operation_kind, workspace_key, request_id)` and fingerprints. A repeated exact
request returns its immutable receipt; changed payload conflicts. A new review
uses an expected prior view and generation. It records reviewer, rationale,
accepted layer, referenced evidence and operation (propose, accept,
accept-alternative, reject or supersede). Legal state transitions follow the
evidence contract. Self-supersession and mismatched replacement scope reject
before mutation. Only review admission records can advance a reading's layer.

A new immutable view records its parent, changed decisions and dependency
selection revisions. It never mutates the old view. Invalidation follows the
reverse dependency graph transitively, including dependencies on candidate-set
membership, not only on the previously chosen members. Therefore adding a newly
eligible filing can stale a selection that formerly had one member. Newly
created descendants must check all ancestors against their requested view;
they cannot escape invalidation by being created after the invalidation scan.
Unrelated dependency closures remain usable. `explain` always uses the output's
frozen view; a current-view query explicitly reports stale dependencies.

A correction to an economic event is a new business event linked to its
predecessor and a specified correction method (reversal/replacement or a dated
adjustment, as applicable). It does not overwrite the original receipt and a
version bump alone does not post it. Corrected historical disclosure creates a
new evidence/model projection; it does not retroactively change what an investor
or the system knew. P17 supplies the accounting treatment of each correction;
missing treatment authority remains unresolved rather than a generic reversal.

## P5. Migration and reproducibility

Migration input is `(old_schema, new_schema, migration_method_ref, source_snapshot,
expected_head, declared_semantic_relation)`. Output retains original bytes/IDs,
new bytes/IDs, a complete mapping and the comparison evidence. A
representation-only migration must preserve decoded typed quantities, contexts,
uncertainty categories, references, admission states, event identities and exact
reference-query outcomes. Invertibility over the retained source domain or an
explicit lossless retained original is required. Changed model meaning, rounding,
calendar, probability or operation order is a new model/version, not a successful
representation-only migration. Failed mapping or comparison leaves all prior
heads and objects usable; migration never silently fills missing metadata.

Replay locks the model, view, package/calculator versions, scenario, requested
outputs, numeric/calendar policies, algorithm/capability manifest and relevant
environment. Exact rational operations on the same evaluated domain require
exact equality. Receipt replay returns the original recorded partition and
values. Re-executing a partial search with a wall-time limit need not visit the
same cells on another machine: compare answers on matched cells, retain both
frontiers and make no claim that partial coverage is identical. Reproducible
prefix comparisons use a pinned traversal and operation-count budget;
elapsed-time limits are resource stops, not semantic equality criteria.
Resume uses P3's exact saved frontier. Approximate
operations require predeclared method-specific error comparisons and retain both
values; a generic float tolerance cannot establish financial equivalence.
Random-stream identity names seed, coupling group, economic owner, date,
shock-kind and draw index, with pinned generator and transforms. Branch traversal
position is absent. The retained SHA-based reference primitive remains only an
identity illustration; no production generator or calibration is selected here.

PX01–PX08 in the shared examples specify lost acknowledgement, exact replay,
changed payload, two writers at one head, correction invalidation, branch
isolation, incomplete export and migration outcomes. Their finite traces make
the expected behavior reviewable. The future implementation must additionally
pass crash/reopen/fault-injection tests on the selected storage/environment.

## P6. Alternatives and tradeoffs

Mutable documents with periodic checkpoints cannot establish the atomic
receipt/state relation above without an additional transaction protocol.
An event log with deterministic projections is viable if its commit marker,
projection visibility and replay checkpoints obey the same contract. The
proposed transactional metadata store plus immutable blobs separates large
source bytes from small atomic changes and fits existing local probes. Its
single-writer throughput and crash guarantees are unmeasured. Analytics engines
and storage libraries remain replaceable behind these observable semantics.
