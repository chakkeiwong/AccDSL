# Sequential probes before choosing an implementation

Use the recorded uncertain_settlement_two_states request and both valid branches
from conditional-return-state-family-20261024-r2/cases.json. Apply the same retained
whole-lot sale event, with date fixed to the settlement date, using both original
transitions. Compare intermediate cash, inventory, profit and lot carrying value;
then compare complete terminal states, journals and flows. Do not assume profit
differences persist after sale: original postings may cancel them cumulatively.

A proposed observation inventory=65 after settlement should retain the low-NRV
history and exclude the first high-carrying witness. Both complete trajectories
must remain available before that observation is applied. This distinguishes
full-family propagation from selecting one intermediate state.

The exact comparator is original native execution on each complete assignment.
Hard vetoes: invalid original state, mismatched journal/flow, lost identity/time
condition or changed frozen source. Descriptive only: example output differences.
No general completeness, probability, forecasting or real-company admission
follows. Record exact requests, outcomes, source hashes and decision.

Use the JSON-stable repaired successor, whose saved-result replay is required
before this audit. The first recorded candidate remains frozen with its failed
replay; its tuple/list serialization error is not reused as accepted evidence.

Pre-recording repair: the first probe incorrectly treated newly returned lot
carrying=5 as total inventory. The complete opening already has inventory=60.
Use total inventory=65, preserving the full native opening. The alternative is
80. Both later terminal balances and cumulative profit coincide; this is an
observed result, not an assumed terminal difference. The failure invalidated
the probe comparison baseline only and triggers this repair.
