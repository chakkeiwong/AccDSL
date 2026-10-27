# Matched term authoring audit — 25 October 2026

The pre-run plan is docs/plans/accounting-receivable-term-authoring-20261025.md.
The comparator is retained evidence from the already checked term-history
reference. Full requests and results are compared, not only ending balances
and not only the new adapter against its own runner. All frozen dependencies
are unchanged. The parser supplies bounded syntax; the typed engine remains
responsible for dates, identities, histories, state transitions and carry.

The initial test run found one mistaken test expectation: the inherited typed
text scalar refuses control characters, including a newline. The quoted and
Unicode round-trip case now uses admissible text; a separate negative test
preserves the newline refusal. This repairs the test rather than broadening
the frozen language or silently normalizing the user's value. Fourteen other
initial tests passed, including both complete retained cases.

The authoring profile imports a previously migrated state with its premise and
unknown historical assessment event; it cannot silently manufacture migration
evidence. The reporting opening and mapping are explicit, hashed imports.
Carry is accepted only at the current state's date, with the frozen term
preservation policy. A grammar-supported report command is explicitly refused
by this narrower profile. No standalone report capability is claimed.

Checked status retains the full successful prefix on a stateful refusal;
syntactically or structurally invalid programs fail compilation. Extra input
types cannot disappear during serialization. Rehashed but semantically invalid
state is rejected after import hash verification. Exact byte locks preserve the
finite implementation and its deterministic evidence. No statistical ranking,
real-source admission or default/accounting policy change follows.
