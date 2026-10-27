# Ordered identity availability without accounting postings

24 October 2026. The finite collection comparison preserves four counterexamples
that require event-by-event identity memory. The native return validator starts
with opening lot IDs, creates a recovered lot once at settlement and permits a
whole-lot sale only when the lot exists and has not been sold. Its settlement
counter also permits only one complete settlement. A reusable local identity
trace can express these conditions without claiming a financial-state transition.

MethodIdentityLifecycle/1 embeds an explicitly authored MethodCollections/1
snapshot definition and selects its event collection and action-tag field.
It declares named pools with matching text key types, a live initial collection
and a retired initial collection. Retired identities remain remembered and
cannot be created again. Each distinct action tag maps to a nonempty ordered
list of create, require or consume operations. Every operation names a pool and
an explicitly typed row/global key binding. Unknown actions and duplicate action
definitions are invalid; supplied strings never load code.

All definition types, mappings, row values and known action tags are validated
before tracing, including events after an unresolved input. Snapshot assessment
runs independently and its full findings remain visible. A snapshot invalid or
unsupported result blocks the trace. Snapshot unresolved findings need not erase
an otherwise known identity trace, but they prevent overall success. This
preserves the distinction between identity feasibility and other prerequisites.

A complete identity trace requires complete initial live/retired pools and a
complete event sequence. Unknown initial keys or incomplete initial membership
stop before the first event. A partial event list likewise stops before any
observed event because omitted predecessors may change identity availability.
For complete sequences, an unknown action tag or operation key stops at that
event; the committed prior trace remains visible. Later events are not inferred.
Independent snapshot diagnostics still inspect all observed rows.

For a known action, execute its operations on a private copy of the pool state.
Create requires an identity absent from both live and retired memory. Require
needs a live identity without changing it. Consume needs a live identity and
moves it to retired memory. Commit that event's identity state only if every
operation succeeds. Failed or unresolved events publish their operation position
and the preceding committed state, with no partially changed pool. This is local
identity atomicity, not journal posting, monetary atomicity or durable commit.

The retained declaration uses a component pool consumed by settlement, a lot
pool created by settlement and consumed by sale, and the inspected snapshot
checks. Thus a second settlement or sale requires an already consumed resource;
same-date events retain their original order. Initial retired collections are
explicit empty declarations in the retained authoring example, not proof of
the actual company's lifetime history. Native shared-book state may carry more.

Limits reuse the collection byte/row/constraint bounds and add at most 32 pools,
32 action tags and 32 operations per action. They are defensive engineering
choices tested at the boundary, not accounting restrictions. Pool key equality
requires exact text/context equality; global/row declarations retain their
declared roles. Input hashes, definition hash and complete identity trace are
recorded. Every result leaves source/accounting admission, method eligibility
and executed false; the identity trace is labeled a diagnostic simulation.

Primary evidence: the four frozen counterexamples must now reject for the
corresponding identity reason; all 15 retained cases must agree with native
structural validation on their declared scope. Independent tests cover atomic
failure, unknown stop, reuse of retired identities, action coverage, exact order
and malformed inactive/future rows. Money, book invariants, source truth,
full native authoring schema and accounting compliance remain separate.
