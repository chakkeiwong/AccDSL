# Local review and persistence profile v1 (P07)

This implementation addresses MC04, MC25, MC27 and MC34 within G17/G18.
It supports one local SQLite writer and the deterministic P05 company engine.
It implements local review decisions; an accepted extraction is not an accepted
accounting interpretation or evidence of professional accounting validity.

## Evidence contract and skeptical audit

Question: do interruption and replay preserve actual P05 execution, and do
corrections retain historical results while invalidating transitive dependents?
The comparator is uninterrupted P05 execution on identical economic inputs,
checked with the independent P05 journal/statement verifier. Exact state,
ordered journals, asset cohorts, receipts and lineage must match persistent
uninterrupted and interrupted executions. Conflicting retry acceptance, mixed
commits, missing lineage, stale-result reuse, changed historical results or
missing obligations veto acceptance. Timing and test counts only describe the
checks. Source truth, accounting validity, forecast skill and human acceptance
are not established. Results are preserved in P07 recovery.json and result.md.

The reviewed plan survives the skeptical audit: P05's in-memory snapshots alone
are inadequate; its dynamic payment resolution and duplicate handling require a
persisted cursor and resolved payloads. P06's direct-only invalidation requires
persistent transitive traversal. Tests use actual APIs and the independent
verifier, rather than copied expected numbers. Interrupted subprocesses remain
attached and bounded. There are no scientific method rankings in this phase.

## Defaults and failure probes

| Choice/provenance | Reason/status | Failure mode and earliest check |
| --- | --- | --- |
| SQLite, stdlib, one writer (approved plan) | Bounded engineering choice | Transaction fault injection and reopening; no distributed durability claim |
| DELETE journal, FULL synchronous, foreign keys | Reviewed integration choice | Integrity/foreign-key checks and terminated writer |
| P05 rational arithmetic and synthetic fixture | Existing comparator, not a new economic default | Independent posting/statement checks and perturbed inputs |
| Explicit dependency ordering | Conservative profile; no proved commutation | Reject ambiguous same-date schedules, cycles and missing references |
| Immutable full run locks including code hashes | Reproducibility requirement | Changed lock/code/source byte checks on resume |
| No production stochastic execution | Explicitly unsupported | Unsupported return; reference tuple checks prove identity only |

## Interfaces and acceptance map

`Store.create_run` locks spec, schedule, view, initial state, scenario, horizon,
outputs, numeric/calendar, environment, packages and stream scheme. Events keep
P05 aliases and a separate domain/version hashed economic identity. Parameter
changes leave the economic event identity unchanged and conflict on retry.
`apply_event` reconstructs the actual engine, resolves dynamic payments from the
committed state, and commits receipt, state, journal, measurements and dependency
edges in one transaction. `resume_run` verifies hashes and replay; `execute_period`
uses the persisted cursor. Failures return typed statuses and no partial state.
`freeze_result` retains the full result under its original evidence view;
atomic file export is a derivative of SQLite truth.

Canonicalization uses NFC UTF-8 JSON, ASCII sorted keys, reduced rational
records, declared set ordering and domain/version SHA-256. Floats, duplicate
keys and normalization collisions are errors. Numeric strings in imported P05
payloads remain schema strings; numbers passed as numeric values use rational
records. No algebraic normalization of imported formulas is claimed.

`add_source` retains verified bytes, hash and path; `propose` retains raw literal,
locator, context, value and extraction/interpretation layer. `review` is
append-only and requires reviewer/time, rationale, applicability and
reconciliation evidence. Only Proposed may become Accepted,
AcceptedAlternative or Rejected. Accepted and AcceptedAlternative may become
Superseded with a distinct compatible accepted replacement. Self-supersession
is rejected before mutation, preserving the accepted reading and current view.
Choice groups expose
alternatives; incompatible accepted readings remain explicit conflicts.
Review idempotency uses request identity and prior view; stale requests conflict.
New views inherit prior invalidations. Descendants are marked stale only in the
new view. Historical results keep their old views. P06 handles availability
selection with unknown timestamps retained as unresolved, never invented.
Use of a dependency traverses all its ancestors and checks each reading's review
state in the requested view. This also rejects descendants first created after
supersession. State, journal and measurement nodes depend on the run and preceding
events, so corrections reach persisted outputs as well as reports. Source-byte
verification follows the referenced dependency graph; unrelated sources cannot
disable an otherwise valid run.

Schema 1 is a legacy event-store representation with text JSON nodes. Schema 2
adds canonical node bytes and their digests transactionally while retaining the
original payload, old identity, new identity and mapping. Historical run and
P05 event identities are preserved. Conversion must decode to equal values;
semantic-changing conversions fail and need new model/run identities.
Legacy immutable triggers are temporarily removed and restored within that same
transaction. Foreign-key integrity and exact execution replay, including all
output dependency edges, must pass before migration commits. Initial schema and
head creation are likewise one transaction; interruption leaves an empty store
that can be opened again.

The repair probes found two implementation errors: Fraction values previously
became schema strings on storage, and new descendants of superseded readings
could escape the recorded invalidation set. Fraction payloads now use tagged
rational records with exact decoding; ancestor review-state checks close the
second error. Explicit event phases distinguish identities, with the declared
`P05-period-step` phase for P05 events, whose original aliases remain unchanged.
New regression tests cover these errors, interrupted initialization, migration
with immutable triggers, invalid lineage and unrelated-source isolation.

| Criterion | Executable obligations |
| --- | --- |
| Interrupted replay equals uninterrupted | Each event boundary; each transactional write; killed process before/after commit; P05 independent verifier |
| Duplicates, partial writes, migration | Stable identities, changed payload/locks, failed export, rollback and repeated migration |
| Correction and preservation | Reading→mapping→calculation→run→report closure; unrelated and historic results unchanged; 720→120 extraction vs 120→110 disclosure |
| Branch/event/stream identity | Permuted branches/dependencies; reference tuple domain separation; production randomness explicitly Unsupported |

Unimplemented: distributed writers, a review UI, general accounting, arbitrary
storage/hardware crash guarantees, assessed Monte Carlo generators and transforms.
