# SequentialReturnStateFamily/1

A complete fixed opening and conditional settlement family are retained before
adding one whole-lot sale of its newly created lot. The closed definition has
profile, first_family, sale_event, proceeds_domain, premise, observations and
obligations. The first event must be settlement. Sale identity/date/method/lot,
performance and fraction remain fixed. Unknown performance or fraction remains
unresolved, false performance or fraction other than one is unsupported. Sale
proceeds can be a fixed known value or a domain for an explicitly unknown value;
its source must match the original sale skeleton digest and pointer.

No intermediate witness is selected. Every complete first branch and constraint
survives. The sale cost is the first branch's symbolic carrying amount. The
unchanged sale definition supplies posting/flow expressions; its supported
ref/const/add/sub syntax is compiled against that shared cost and sale proceeds.
The native created-lot continuity premise explicitly records the two dates,
same lot identity and source calculation, preserving the event-dated contexts.
It does not delete a type context key to force an equality.

Prefix balances equal original opening plus the first journal, then plus sale
journal. First-event funding remains; terminal cash is separately nonnegative.
Proceeds are nonnegative. Optional observations contain id, prefix (1 or2),
account, complete type and existing domain record. Exact date/context/dimension/
scale must match the prefix account. All observation/domain/continuity premises
remain in the result; missing ones leave formulation incomplete and unresolved.
No source interpretation or actual state is inferred.

Each feasible assignment replays the complete repaired first family and then
both original native sale transitions. The original monetary sale evaluator,
compiled journal, every compiled prefix balance, each observation and all
constraints are checked with exact arithmetic. Full intermediate/final state,
flows and journal remain available. An alternative valid assignment is accepted
after the same checks, including JSON serialization round-trip.

The first compiler shares a variable dictionary among its branches; the new
successor must copy that dictionary before adding the sale variable to each arm.
The initial test failure exposed this and it was repaired without changing
the frozen parent. A second pre-recording review repaired result completeness
metadata so every new sequence/observation premise is included. Tests cover both.

The inherited global branch/cell/time policy remains; a known witness under
partial coverage does not prove all branches visited. If the first branch is
infeasible and a later arm is unvisited, result is unknown, not empty. Every arm
must be checked infeasible for emptiness. Exact replay is bounded but not hard
wall-clock preemption. No probabilities from branch counts; no financing plug.

The restricted two-event topology is explicit. Arbitrary event sequences,
symbolic collection structure, actual source-state recovery, wider methods and
independent/production acceptance remain open.
