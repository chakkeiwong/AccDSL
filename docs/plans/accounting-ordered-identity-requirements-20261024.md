# Preserve identity creation and consumption in supplied event order

24 October 2026. S2–S4; MC05/13/15/17/23/24/26/27/31;
G2/G3/G10/G13/G15/G17. Protect MethodCollections/1 and all recorded predecessors.

Question: can a reusable identity lifecycle declaration detect sale before lot
creation, repeated consumption and duplicate complete settlement while retaining
supplied event order? Four checked snapshot counterexamples motivate this repair:
equal-date sale before creation, missing sale lot, whole-lot double sale and two
complete settlements. They reject whole-method promotion of the snapshot fragment;
they do not invalidate the simulator direction or the snapshot checks.

Exact comparator: the known_lots/sold/settlements loop in retained return_schema.py
validate; native_returns.py supplies the separate monetary/state boundary. Inspect
and reuse existing bounded event/state machinery where semantics match. Author
generic create/consume/reference and single-use resource declarations explicitly;
do not hardcode return-event names or infer a balance-sheet effect.

Skeptical audit: sorting equal dates can repair an invalid schedule by changing
its meaning. Set membership cannot prove earlier availability. Unknown events
or partial schedules may contain missing creation/consumption, so continuing a
concrete state after them can make a false conclusion. Define a conservative
unknown transition before implementation. A known repeated immutable identity
may still be a contradiction under an explicitly declared no-reuse rule; any
stronger all-history conclusion needs proof. Full record/type validation must
precede simulation, even for unreachable branches. No journal or book is posted.

Initial default: only a complete sequence with known event action and key can
support a complete identity trace. Unknown transition inputs produce unresolved
and an explicitly stopped identity trace; subsequent structural validity and
independent snapshot checks still run. Reject missing/ambiguous action mappings;
every observed event gets a declared disposition. Declare initial identity sets,
no-reuse and single-consumption behavior; preserve disposed identities as memory.
These are local identity semantics, not accounting facts or probabilistic histories.

Primary criterion: repair all four preserved counterexamples and independently
authored create/reference/consume schedules, with exact trace and original order.
Known duplicates, missing known resources, repeated consumption, ambiguous action
definitions and source/type changes veto candidate acceptance. Unknown incomplete
traces block success, not unrelated internal work. Runtime/counts are explanatory.
No complete method, actual company feasibility, accounting compliance or forecast
claim follows. Next repair is typed monetary state invariants and atomic effects.

Artifacts: data/accounting-master/ordered-identity-requirements-20261024/.
Record plan, reviewed assumptions, exact code/comparator hashes, commands,
CPU-only environment, outcomes and remaining limits. S1–S5 partial; S6 held;
S7 deferred. No global continuation veto is supported.
