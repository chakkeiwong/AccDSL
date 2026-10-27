# Pre-implementation schedule audit — 25 October2026

MC13/14/15/18/23–26/28/32/34/35. Read prior simulator-timing and settlement-decision
results: dated cash feasibility and explicit same-instant dependency mattered.
Those earlier UTC/settlement conventions are not interchangeable with the current
annual book's day-level inventory decisions. Use explicit priority only for this
authored same-day case; no general priority or business calendar is inherited.

Question: remove caller precomputation of future book hashes while preserving
the exact decision/accounting consequences. Comparator: unchanged checked
StateDecisionEvent/1 sequence. Primary: exact materialized requests, transitions,
complete state and all financial fields; independent stock/cash arithmetic.
Veto: stale root, malformed future template, duplicate or ambiguous order,
calendar bounds, changed dependency and missing refusal prefix. Counts/runtime
are explanatory. A candidate failure triggers repair; it does not reject the
company simulator direction. No stochastic ranking or empirical forecast claim.

Assumptions: closed authored scenario and fixed selected lot come from the
decision reference; no external intervening events is unverified. Integer-day
calendar is a convenience subset; leap/exclusive-end tests expose date mistakes.
64 decisions/32 schedules are finite-reference limits with boundary tests, not
scalability evidence. Stable IDs describe authored decisions, not source facts.
Audit passes for this bounded extension; general calendars and decisions stay
open. Preserve pinned decision implementation and all frozen predecessors.

The first15 focused methods passed in18.747 seconds. Before recording, added
stock-depletion, invalid-interval, aggregate-occurrence and request-byte checks.
Inherited caller bounds are2,000,000 bytes/100,000 nodes/depth64, explicitly
documented rather than silently promoted as general performance defaults.
