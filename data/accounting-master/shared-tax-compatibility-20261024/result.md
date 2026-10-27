# Original tax close is incompatible with the mixed book

24 October 2026. S2–S4; MC05/11/13/16/24/26/28/35; G2/G4;
P17-04.10 and P17-04.11. All 92 diagnostic checks pass and preserve 69 source
files. Both original 2025 tax controls reproduce their complete saved proposals
and states. Those results remain valid within their original finite scope.

Direct native tax reuse on the unchanged mixed state is rejected with invalid:
closed state fields. The input remains byte-equivalent. That refusal is correct:
the shared state contains three additional accounts and lease memory. Projecting
or relabelling it would not preserve the stated mixed-book target.

The old pretax function computes minus the sum over its original six pretax
income accounts. Applied diagnostically to the mixed balances, it returns -15.
The mixed report includes other_gains=-20 in addition, so its pretax profit is
-15-(-20)=5. Thus the old function is wrong relative to the complete mixed-book
pretax target, with an omitted gain of 20. This says nothing adverse about its
original return-only calculation. Both quantities and their account lists are
saved in diagnosis.json.

The original return adjustment is -24. Mechanical multiplication at the old
fixture rate gives (-15-24)/4=-39/4 or (5-24)/4=-19/4. These are diagnostic
expressions, not assessed taxes: the lease deduction timing, remaining ROU tax
basis, modification-gain treatment and loss route are unspecified. Neither
expression licenses a cash refund. The native method explicitly refuses its
negative-current-tax route. Retaining the original rate does not supply tax law.

There is also a temporal incompatibility. Native tax close on 31 December sets
tax_closed_until to 1 January, an exclusive endpoint. The current shared-book
invariant requires tax_closed_until no later than state date; changing just that
field yields tax_close_date. The shared declared period itself runs from
1 January 2024 to 1 January 2026 (731 days). That synthetic execution window
does not establish a single annual tax or reporting interval.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Reject direct original-tax reuse on the mixed book | Full state, income and close-time compatibility fails | Closed-state refusal, omitted gain, unresolved tax facts/loss route and exclusive-close conflict | Applicable lease tax treatment and fiscal coverage are not supplied | Specify and check explicit tax fact requirements and close-time meanings in a separate successor | No assessed mixed tax, annual close, tax-law compliance or rejection of the simulator direction |

The failure invalidates direct reuse, not the research direction or original
reference. The next repair must preserve every account and component, require
explicit tax facts and retain unresolved outcomes. It must not infer a tax base
from a carrying amount, turn a loss into a refund, or mark a two-year execution
window as a completed annual period. The strongest alternative explanation—an
unnoticed native regression—is constrained by exact original-control replay.
Actual jurisdictional and company evidence remains the weakest part because
none is present in this synthetic example. No global continuation veto fires.
