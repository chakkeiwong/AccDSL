# R03 — Relationship measurement and stopped-reserve attribution

18 October 2026. P15/P17/P19; MC02/05/16/17/24/26/28–30/32–35;
G2/G3/G7/G8/G10/G13. Exact documentary derivation, not a runtime method.
Evidence: data/accounting-master/r03-hedge-attribution-discriminator-20261018/.

## Question and skeptical audit

What does relationship-level cumulative lower-of measurement establish, and
which proposed origin-allocation shortcuts fail for unmatched or opposed
origin gains? Baselines are the unchanged OriginMatchedCessation/1 contract,
the historical EU2023/1803 IFRS9 text and the frozen 3.44 candidate. The
delivered method requires documented exact matches, no shared ineffectiveness
and the same weak gain sign. Do not silently widen it.

Inspected prior work: origin-matched-cessation-20261017 source/contract/result,
partial-hedge-discontinuation-20261016 source/contract, added-instruments plan,
and financing-modifications-net-hedges-20261015 source reading. These use the
retained EU text. No separate unresolved hedge acquisition route was identified
in those records; this is not a repository-wide absence claim. No retrieval
is needed for the proposed algebra; do not retry unrelated failed source URLs.

The tempting plan to admit a general signed allocation from conservation alone
fails audit. Equal totals do not establish accounting admissibility, and
B6.6.14 is a presentation rule rather than a stopped-reserve formula. Revise
the target to a theorem, fixed counterexamples and explicit non-identification
under stated weak bookkeeping constraints. Re-read 6.5.11–12, B6.5.16–23 and
B6.6.13–15 in the retained technical text. This revised plan passes: it can
reject specific mathematical shortcuts without claiming a legal selector.

## Research intent and evidence contract

Mechanism: taking a minimum and aggregating do not generally commute.
Let x_j be signed cumulative instrument gain and y_j the negative of the
matched item's risk change. The relationship calculation is
R=sign(X) min(|X|,|Y|), X=sum x_j, Y=sum y_j, on the diagnostic domain XY>=0.
This orientation/domain is supplied; actual qualification is not inferred.
Compare R with the explicit shortcut L=sum sign(x_j)min(|x_j|,|y_j|), where
each x_j y_j>=0. Neither comparator is an admitted general allocation method.

Primary criterion: derive for nonnegative x,y that
R-L=min(sum max(x_j-y_j,0),sum max(y_j-x_j,0)); identify its exact equality
condition. Check nine hand-authored cases, including a strict unsigned gap,
a signed counterexample and its sign reversal, exact-match controls and net
cancellation. Then exhibit two distinct reserve decompositions with identical
aggregate inputs and different stopped-part releases. They must be described
as bookkeeping-compatible candidates, not proven accounting alternatives.

The unsigned example x=(12,8), y=(6,12) gives R=18,L=14,gap=4,profit=2.
The signed example x=(12,-8), y=(10,-9) gives R=1,L=2,profit=3.
For the unsigned example the weak constraints 0<=r_j<=x_j and sum r_j=18
admit r=(10+t,8-t), 0<=t<=2. Stopping half the first origin gives
F=5+t/2. Immediate cancellation leaves reserve 13-t/2 and total profit
7+t/2, still summing to the same instrument gain20. Derive the interval;
check its two endpoints and midpoint as fixed exact witnesses, not a sweep.
The cap constraint is an analytical hypothesis, not a sourced accounting rule.

Promotion vetoes: incorrect source attribution, arithmetic mismatch, hidden
change of measurement unit, calling a decomposition accounting-admissible,
or loss of protected evidence. A candidate mismatch triggers derivation repair.
Continuation vetoes: corrupt required inputs or work beyond proposal scope.
Explanatory only: case/check counts, the cancellation control, and wall time.
Passing does not admit a selector, establish current law, prove real hedge
eligibility, choose an allocation, change the manuscript or close a whole row.
Artifact: derivation/source-boundary/result, frozen targets, exact calculations,
manifest, immutable control snapshots and additive R08 supplement.

## Material defaults, assumptions and pre-mortem

| Choice | Provenance and status | Justification / failure / early diagnostic |
| --- | --- | --- |
| Historical EU text | Existing primary technical source, historical only | Defines measurement level; paragraph anchors prevent presentation being mistaken for measurement |
| Per-origin lower-of comparator | Explicit candidate shortcut, not a default | Small exact cases can refute it; compare with the relationship total independently |
| Signed orientation and supplied marks | Synthetic hypothesis | No valuation/qualification inference; refuse the nonoffset aggregate domain |
| Weak nonnegative component caps | Analytical hypothesis only | Shows limited constraints underdetermine a split; never call the resulting interval an IFRS bound |
| Half-stop, no later value change, immediate cancellation | Fixed diagnostic convenience | Isolates release sensitivity; retain all historical profit and check full gain conservation |
| Fraction arithmetic, CPU standard library | Author verification tooling | Avoid tolerances; freeze hand targets and derive the min identity before execution |

Pre-mortem: a correct sum could conceal a wrong allocation. Compare the
different downstream releases, not just totals. Exact signed matching can
conserve even when origin signs oppose; this observation removes a proposed
algebraic necessity, not the existing method's scope restriction or source
burden. No general impossibility theorem about future source-supported
allocation rules follows from underdetermination by these limited constraints.

## Execution and continuation

Before calculation protect HEAD/index/empty staging, all 36 tracked dirty
paths, frozen 3.44/R08, the EPS completion and its protected inputs, and the
exact hedge source/contracts. Only the four live controls may change among
existing files; plans/evidence are new. Use standard-library-only
/home/chakwong/miniconda3/envs/tfgpu/bin/python3 with CUDA_VISIBLE_DEVICES=-1.
One-time --prepare, --calculate and --record stages refuse replacement;
default verify.py is read-only. Record actual commands/environment/wall time,
source boundaries, decision/inference tables and the strongest alternative.

After verified results refresh the four controls and add a separately bound
R08 supplement, retaining 53 obligations/six interactions/46 operations and
not_ready. No manuscript edit, installation, runtime/controller, empirical
campaign, commit, outreach, publication or fee. A failed shortcut is not a
continuation veto. Continue a specific new source lead or independently ready
R03–R06 preparation after this finite derivation; do not repeat delivered cases.
