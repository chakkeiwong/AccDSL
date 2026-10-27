# Cash-only partial schedules preserve the shortfall

27 October 2026. Attempt-01 passes: 20 full runtime cases, four inspected method
definitions, 517 assertions, eight controls and 204 protected files. Python
3.11.15; 11.306 seconds; CPU with GPU intentionally hidden. Exact command and
commit are recorded in attempt-01/run-manifest.json. No predecessor was rerun.

For the selected carried history let S_i be cumulative payment after i events.
At i=0, cash C0=85/16, positive claim U0=86/16 and paid P0=0. The actual method
posts −q to cash, +q to signed payable, and writes old paid2+q. Therefore the
induction step gives C_i=C0−S_i, U_i=U0−S_i, P_i=S_i. The checked coefficient
identities yield U_i−C_i=1/16 and U_i+P_i=U0. Because U_i>C_i, a positive amount
q<=C_i is automatically strictly below U_i. A finite positive schedule is
economically affordable exactly when its total is <=C0, subject separately to
the stated dates and event identities. At cash exhaustion 1/16 remains owed.

This is an exact algebraic statement for this selected recurrence. Four actual
method definitions were inspected for postings, cumulative calculation, bindings,
guards, memory writes and classification. Runtime checks add nonuniform,
same-day, unequal-rational, tiny-then-rest and near-exhaustion schedules on the
four chart/action origins. They compare full states, journals, flows and reports
against the independent oracle. A residual of 1/2^64 remains exact in the
near-exhaustion case; it is not rounded into cash exhaustion.

A 65-command schedule summing to the available cash is economically affordable
but statically refused with command_limit. Period-end/pre-opening events are
refused without changing the book. Rational bit limits and four method
corruptions are detected. These checks separate mathematical possibility from
bounded runtime support. Limits are in attempt-01/runtime-limits.json; they are
not a sufficient guarantee that every smaller request will execute.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain invariant and bounded conformance result | Exact recurrence coefficients, actual method correspondence and 20 full comparisons pass | Eight controls rejected; upstream hashes preserved | General runtime proof and source applicability remain open | Test continuation distinctions between equal balances with different dates/IDs/flows before choosing a compressed state | No arbitrary-size runtime guarantee, fresh funding, default finding or whole-package closure |

Post-run red team: unchanged totals could hide wrong dates or original decision
memory; full comparisons retain those fields. Correct finite examples could
still miss implementation behavior elsewhere; the algebraic result is stated
separately and runtime coverage remains finite. No continuation veto fired.
The current manuscript remains 5.46 until a separate integration is verified.
