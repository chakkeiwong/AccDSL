# Chosen term-history boundary — 25 October2026

The typed transition2 engine supports map insertion and scalar replacement;
the carry engine can preserve every current memory leaf. Neither requires
changing frozen engines. A new state profile will contain the book, explicit
memory definition/schema registry, account roles and migration provenance.
Its claim records retain current due/assessment summaries for observation but
add immutable per-claim terms and assessments plus current-term identity.
Validation derives old assessment meaning from the referenced historical term,
not the current due date. Every new assessment records a term identity.

Migration is provisional, explicit and source-bound to a checked old snapshot.
It imports one initial term and the last old assessment under a supplied
no-prior-amendment premise. Earlier assessment/term populations remain unknown;
the imported record must not invent an event ID that was never recorded.
Original balances, flows, identities, scalar memory and old assessment survive.

Date semantics: immediate prospective term event only; effective date equals
event date, no scheduling of future-effective changes. Due cannot precede
effective date. Event date cannot precede current book/collection cursor.
Assessment seals its interval and rejects later amendments on the sealed day.
Same-day amendment before assessment is allowed and explicitly uses new terms.
Receipts change remaining only; previous assessed remaining stays historical.
Carry preserves term/assessment history and advances only the collection clock.

Reuse the typed transition engine for amendment/assessment memory operations;
reuse monetary collection semantics for receipts. Zero journal describes the
constructed state-only operation, not modification accounting. Supplied
approval/premise is required; false means unsupported and unknown unresolved.
No interest, consideration, principal modification or impairment is accepted.

Tests must expose loss of prior assessment basis, backdating, duplicate events,
stale states/terms, schema drift, unknown claims, mismatched customer and replay
tampering. Exact expected20→0 overdue with unchanged prior assessment is primary;
balance and schema checks veto but do not prove accounting truth. Finite map
capacities are convenience limits inherited from the existing typed engine.
Audit passes for this explicit reference, not general real-contract amendments.

First focused execution found that an empty postcondition manifest is outside
the existing requirement grammar. Repaired it using an actual equality check
on the written due date or assessment cursor. A dedicated altered-postcondition
test verifies that this is not a constant-true placeholder. No frozen engine
changed. The earlier failure log is retained; subsequent evidence runs must
use the final postcondition and complete test suite.
