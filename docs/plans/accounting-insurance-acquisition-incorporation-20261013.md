# Incorporate acquisition assets when the insurance groups are recognised

13 October 2026. P17/E07/P18; MC08/10/11/13/16/19/22/28/30/32–35,
G4/G6/G7/G15/G16. Continue from Version 2.56. Runtime remains held.

Question: once the example's future groups are recognised, how do the remaining
acquisition assets enter the initial CSM and group carrying amounts, and how
does subsequent premium receipt preserve equity without immediate revenue?
The prior section describes derecognition but does not calculate this bridge.

Comparator: Version 2.56's acquisition example and retained AASB17.25–28,
28C–28D, 32, 38–40, 47, B35B–B35C and relevant cash-flow/revenue provisions.
Inspect the exceptions before choosing a journal; do not assume acquisition
assets are an expense again or an additional group asset after incorporation.

Skeptical audit: omitting the derecognised acquisition asset from initial CSM
would overstate CSM; retaining it alongside the complete group balance would
double count. Recognition is not automatically premium receipt, and receipt
is not automatically insurance revenue. A change in estimates between the
impairment and recognition examples could create an unexplained loss; keep
the same group net inflows and explicitly state all additional facts. Check
that the illustrative gross cash flows reconcile to those net measurements.

Evidence contract: derive both group balances and CSM from the source, work
the transfer of acquisition assets and premium receipt, and reconcile the
whole illustrative slice before/after each event. Require exact group and total
conservation, no stale separate acquisition balance, no unexplained current
profit and a zero-acquisition boundary. Incorrect eligibility, source-exception
handling, dates, double counting or inconsistency with previous inputs vetoes
the affected calculation. Positive CSM is future service profit, not acceptance
of the whole insurance method. No runtime execution, actual contract valuation,
current-rule completeness or calibrated insurer forecast follows.

Default audit: retain authored acquisition assets35/15, cash40 and net inflows
45/30. Add explicitly authored premium/current-value claims/risk-adjustment
inputs consistent with those totals, all contracts admitted simultaneously,
supported recognition and group membership, no service yet, no other balances
or movements, and premium receipt immediately after recognition. Do not imply
zero discounting merely because present values are supplied. If any condition
does not support the intended bridge, revise before integration.

Output: `data/accounting-master/insurance-acquisition-incorporation-20261013/`.
Integrate only supported material in a separate Version 2.57 candidate,
preserve prior sources/math/citations, build and inspect, update requirement
evidence and master, commit explicit paths. Human/domain acceptance stays
pending while feasible internal work continues.
