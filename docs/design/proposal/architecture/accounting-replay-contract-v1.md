# Accounting replay and event identity — proposed supplement v1

This supplement repairs the replay semantics in accounting-contract-v1.md,
sections 2–4. It supersedes AC04 and AC05 as reproducible retry/staleness
examples, and clarifies invariant 5: event version belongs to the fingerprint,
not the stable lookup key. AC01–AC03 and all predecessor files remain historical
source-scoped evidence. This slice addresses MC13, MC25 and MC34 with MC08
branch preservation and G4/G18 interactions. It specifies behavior, not software.

## Question, evidence and stopping rule

Can the same recorded acquisition be retried after later transactions without
posting twice, while changed requests conflict and genuinely new stale requests
are rejected? Compare identity lookup before freshness with freshness before
identity lookup, using the identical request and committed state. The primary
criterion is the derived response and absence/presence of a further domain
transition in each specified case, including branch isolation. Wrong source
hashes, inconsistent dependencies or non-reconciling arithmetic invalidate the
fixture calculation. Journal balance is an explanatory arithmetic check, not
proof of eligibility. No statistical ranking, runtime durability, accounting
validity or complete IR selection follows. Preserve the result in
accounting-replay-verification-v1.json and stop after this bounded slice.

Skeptical audit: these are matched deterministic cases, not a comparison of
prototype test counts. Failure of the whole P16 checker is expected while four
contracts and the initial profile are unfinished. It does not invalidate a
correctly scoped retry example. Conversely, passing these examples cannot
complete the accounting contract. Remaining input/receipt, eligibility, atomic
failure and architectural-alternative obligations require a subsequent task.

## Identity and record encoding

The stable event key is the tuple (entity_id, book_id, branch_id,
business_event_id). Book identifiers are scoped by entity; branch identifiers
are scoped by book. Branch IDs reference explicit branch records and their
common family. The same event label in a different branch is a distinct posting
identity; it neither inherits a receipt nor grants economic admissibility.
A version change under the same key conflicts. An intentional correction needs
a new business-event ID linked to the superseded event and a separately
specified correction method; a version bump alone never authorizes a second
posting. Correction workflows are outside this slice.

The request fingerprint covers the complete request record: stable key, event
version and payload, expected opening-state digest, context, time/cutoff,
branch record, and authority/method/evidence/assumption record digests. Mutable
transport metadata (arrival time, tracing token) is outside this request. Every
transitive record is immutable and checked against its digest. Thus equal
fingerprints mean equal retained request bytes under this encoding, assuming
SHA256 collision resistance; they do not assert economic equivalence.

For these finite fixtures only, serialize JSON with sorted keys, compact
separators, ensure_ascii=True and allow_nan=False, encoded as ASCII. Objects
have unique string keys; arrays preserve order; numeric amounts are decimal
strings with exactly two fractional digits; versions are nonnegative integers.
Floats, NaN, duplicate keys and non-ASCII text are excluded from this fixture
profile. UTF-8 interoperability, arbitrary dimensions, migrations and a general
language encoding remain open. The digest is SHA256 of the ASCII domain,
a NUL byte and serialized bytes. Domains are accdsl.replay.v1/key,
accdsl.replay.v1/request and accdsl.replay.v1/<record kind>. A receipt references
request, assessment, journal, delta and opening/closing records without a cycle.
The registry stores kind, full content and digest, not symbolic digest labels.

These are proposed convenience choices. SHA256 follows existing immutable
source references; exact two-decimal amounts follow the synthetic A01 example;
branch IDs and monotonically numbered states expose isolation and stale inputs.
Their failure modes are omitted request fields, accidental aliases, precision
loss and mistaken cross-branch reuse. The bounded calculation checks all
request dependencies, changes payload and branch separately, uses Decimal and
checks distinct opening/closing digests. These checks do not promote the
choices to a general persistence or IR default.

## Order, receipts and concurrency obligations

1. Check structure, resolve all pinned records and validate internal context:
   entity/book/branch, currency/unit/basis, event time and source cutoff. An
   exact retry uses its retained historical context, not today's method or
   cutoff. Missing/corrupt dependencies are an invalid request, not a replay.
2. Under that branch/book identity, look up the stable key in committed receipts.
   If found, compare the complete request fingerprint. An equal fingerprint
   returns the original immutable receipt; a different fingerprint returns
   EVENT_ID_CONFLICT before any freshness check. Neither creates a new domain
   transition. Changed payload cannot evade conflict by changing its version.
3. Only for an absent key, compare the expected opening digest with the current
   state of that branch. Mismatch returns STALE_OPENING_STATE without a posting.
4. For a fresh new event, assess eligibility and construct/check the journal
   and independent delta. Only then may one atomic operation insert identity,
   journal, closing state and committed receipt. Recheck absence of the key and
   opening state atomically to prevent a concurrent writer racing these checks.
   Persistence must later specify isolation, crash recovery and audit storage.

The immutable receipt always retains status=committed and commit=true for the
original transaction. A retry response has status=replayed,
additional_commit=false and the same receipt digest; it must never rewrite
that receipt as replayed or return a newer closing state as its original result.
Its response separately identifies the current observed state. A conflict may
identify the existing receipt for diagnosis, without claiming it belongs to the
submitted fingerprint. A stale or conflicting response preserves the submitted
request and known facts; journal and delta are null, additional domain writes
are zero and before/after state and committed-receipt index are identical.
Optional audit logging is separate from domain writes and is not required or
modeled by these fixtures. Replay retrieval is not a fresh eligibility verdict.

Freshness-first on the specified retry sees the original opening state differ
from the now-current state and incorrectly reports STALE_OPENING_STATE. Both
orders reject the genuinely new stale request. Stable-key-only replay without
a fingerprint would incorrectly accept a changed payload. Including payload
or version in the lookup key would instead hide the conflict. These comparisons
justify the proposed order under the stated retry contract; they establish no
speed or storage advantage.

## Concrete inputs and consequences

The fixture registry includes complete branch-scoped opening balances, pinned
context and request dependencies. A01 has price=fair value=100.00 and fee=2.00.
Eligibility is explicitly stipulated under the retained S9 5.1.1 source scope;
this task does not re-establish classification or jurisdiction applicability.
Cash starts at 1000.00, asset and expense at zero, and equity at -1000.00 in
debit-positive notation. The event directly implies cash -102.00, asset +100.00,
expense +2.00, equity zero change. Separately, debit asset 100.00, debit expense
2.00 and credit cash 102.00 aggregate to the same delta. Closing cash is 898.00.
A second separately identified acquisition advances this branch to cash 796.00,
asset 200.00 and expense 4.00; its full request and receipt are retained as setup.

AR01 commits the control. AR02 retries AR01 after the second acquisition and
returns AR01's original receipt without changing either receipt or current
state. AR03 changes the fee to 3.00 under the same key and conflicts, preserving
that submitted fact without posting it. AR04 uses a new event ID with the old
opening digest and is stale. AR05 uses the original event label in another
explicit branch with its own opening state: it commits there while branch A
and both of its receipts remain unchanged. Branch B is a synthetic stipulated
alternative, not a newly inferred economically admissible history.

The calculation independently derives A01 deltas from event amounts and from
journal lines, checks complete receipt references and every source binding,
and derives outcomes before comparing authored expectations. It is an offline
finite document calculation, not a reusable runtime evaluator or product test
suite. Full lifecycle eligibility, general record typing, atomic failure modes,
interfaces, language/IR, persistence and initial-profile selection remain open.
