# Aggregate lease balances leave a conditional family

The declared opening has exactly two identified rights, total ROU120, liabilities
A100/B50 and cash200. Let B's ROU be x, so A's is120-x. Nonnegative assets give
0<=x<=120. The source is a synthetic premise; an actual total does not establish
the number or identity of rights, their liability allocation or their rates.

The first original method fully terminates B and discounts A's payment121 at10%.
B's gain is50-x. A's liability110 exceeds its old100 by10, so A's ROU becomes
120-x+10=130-x. The total signed journal is ROU10-x, liability+40,
other_gains x-50. Its sum is zero for every allocation, but the gain is not fixed.

The second method removes ROU10/liability11. The remainder is ROU120-x and
liability99. Payment99 discounted at10% gives liability90; the adjustment-9
leaves ROU111-x. The journal is ROU-19,liability+20,other_gains-1. Original method
support requires that the remaining ROU be nonnegative, hence x<=111. For
111<x<=120 the original method returns unsupported at the second event. These
are still valid declared openings; the unsupported method result does not prove
that the actual economic history is impossible.

For x<=111, payment99 creates interest9/principal90 and cash101. The last event
supplies depreciation81. Original depreciation must not exceed remaining ROU,
so81<=111-x, equivalently x<=30. For30<x<=111 the first three events succeed,
but the final supplied event is rejected. The prefix and its liability settlement
survive. We do not replace81 with a different depreciation to force completion.

For the complete supported four-event sequence,0<=x<=30, final ROU=30-x and
pretax profit=(50-x)+1-9-81=-39-x. Thus the marginal ranges are ROU[0,30] and
profit[-69,-39], but every possible pair satisfies profit-ROU=-69. The pair
ROU30/profit-69 combines incompatible endpoints and is infeasible. A supplied
final-ROU observation10 selects x20 and profit-59. It is a hypothetical additional
observation, not an acquired issuer fact. No probabilities are assigned.

The exact affine solver proves no better endpoint exists, checks attainment,
checks support in both directions and rejects the incompatible marginal pair.
Original native replays at x0/20/30/40/100/111/112/120 agree with the formulas and
refusal positions. A zero-cell budget reports partial search without bounds.
Missing complete membership remains unresolved before native execution.

The full allocation domain is partitioned into complete[0,30], refused-last-event
(30,111] and unsupported-second-event(111,120]. A later family reference must
retain all three cells. Bounds conditional on completion cannot be called bounds
for successful execution of every original allocation. Membership, findings,
dates and original source scope remain premises.
