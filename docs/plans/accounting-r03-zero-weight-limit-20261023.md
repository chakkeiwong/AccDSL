# R03 — limits of positive-weight CGU reversal allocation

23 October 2026. P17/P19; MC02/04/17/19/24/26/28/29/30/33–35;
G2/G3/G7/G10. Output: `data/accounting-master/r03-zero-weight-limit-20261023/`.

## Research intent and evidence contract

Question: does the existing capped proportional reversal procedure have a
unique continuous extension when every eligible non-goodwill carrying amount
tends to zero? The completed publisher follow-up explicitly leaves this
limiting argument unchecked. Its actual example has positive eligible amounts;
no new technical authority or current applicability can be inferred from it.

Candidate mechanism: introduce small positive carrying weights, apply the
existing positive-weight rule and take their limit. Expected failure: different
relative weights approaching the same zero vector produce different restored
carrying values. Exact comparator: the positive-weight capped redistribution
procedure in `impairment-floors-20261014.md`, with fixed restoration ceilings
and a specified final carrying total. An arbitrary equal-weight regularizer
is a hypothesis, not the comparator or an adopted policy.

Primary criterion: a written proof of the positive-weight characterization
and its entire limiting allocation set, with exact rational witnesses checked
against an independently written iterative capped allocator. The finite checks
validate transcription and algorithm correspondence only. The proof, not the
number of examples or tiny chosen epsilon, supports the mathematical claim.

Promotion veto: an incorrect proof, hidden changing caps, wrong reversal total,
failed exact witness, skipped domain condition, or accounting authority inferred
from algebra. Repair trigger: an implementation or fixture disagreement; inspect
the source expression and proof before repairing. Continuation veto: corrupted
protected evidence, invalid inherited source identity or a held action needed
for the proposed run. Explanatory diagnostics: fixture counts, elapsed time,
number of cap redistributions and size of the chosen perturbation. A failed
regularizer rejects that candidate, not the source target or research direction.

Even a successful proof does not determine the IAS 36 allocation at zero,
establish actual-issuer admissibility, justify changing reported carrying
amounts, or select a numerical policy. Preserve source and interpretation
boundaries, a decision table, exact examples, author review, manifest and
additive R08 supplement. No manuscript repair is presumed.

## Domain and proposed result

Exclude goodwill and assets with zero restoration ceiling from the perturbed
positive set. For m remaining assets let C_i>0 be fixed admissible ceilings and
let T be a supplied final total with 0<T<=sum C_i. At each positive perturbation
0<b_i<C_i and sum b_i<T. Requested reversal is T-sum b_i; capacity is C_i-b_i.
These quantities must change together. Holding the requested reversal fixed
while changing initial carrying amounts would answer a different question.

The capped algorithm keeps the original b_i as weights on each unsaturated
set. Its final balances should have the form min(C_i, lambda b_i), for a common
lambda>=1 with sum final balances=T. Prove this correspondence before using it.

Conjecture: the full set of attainable limiting balances as b tends to zero
through positive vectors is A={x:0<=x_i<=C_i, sum x_i=T}. For 0<T<sum C_i,
construct paths to every member using an interior feasible vector and a shrinking
mixture. Limits must stay in A because it is closed. If m>=2, A has multiple
members, so no unique continuous extension exists. When T=sum C_i or m=1,
the mathematical target is unique. At T=0, the boundary feasible set is {0},
but there is no positive-reversal approach with sum b_i<T; label that separate
case explicitly. T>sum C_i is outside this exact-total theorem and belongs to
the existing capacity-shortfall disposition.

## Skeptical plan audit and defaults

Audit passes for this local mathematical question. The earlier two-asset cap
interval proof already shows constraint underdetermination; it does not show
whether approaching from ordinary positive-weight cases selects a unique
point. This unit answers that distinct question. It may reinforce the existing
unsupported-method status, but cannot repair missing accounting authority.

| Choice | Provenance/status | Justification | Failure mode | Early diagnostic |
| --- | --- | --- | --- | --- |
| Original carrying weights held within each allocation | Existing positive-weight method; baseline | Matches the retained procedure | Recomputing weights after each split changes the comparator | Check the active-set invariant and a multi-cap witness |
| Fixed ceilings and final total | Explicit mathematical hypotheses | Isolates the zero-weight limit | Treating changing caps or fixed reversal amount as equivalent | Verify capacities C-b and reversal T-sum b in every fixture |
| All eligible perturbed weights positive | Interior approach; hypothesis | Defines the limit being tested | Assuming zero weights were admissible runtime inputs | Refuse nonpositive weights before allocation |
| Exact fractions | Existing standard-library tool; reviewed diagnostic choice | Exposes equality/cap boundaries without floating tolerance | Calling tiny epsilon numerical evidence for a limit | Require a symbolic construction and exact finite checks |
| Finite fixtures, no sweep | Convenience for transcription checks | Smallest discriminating artifacts | Counts promoted to general proof or performance | Hand-authored expected vectors and independent scalar characterization |

Pre-mortem: a seemingly stable result along equal-weight perturbations could
conceal path dependence. Compare two different normalized weight directions
at the same scales, then approach a feasible boundary allocation. Also test
binding caps, several capped assets, an exact cap equality, one asset, total
capacity, zero boundary target and outside-domain inputs. Do not infer a unique
rule merely because constraints happen to leave one vector in a special case.

## Execution order

1. Preserve the completed native audit, all inherited protected bytes,
   HEAD/index, 36 tracked dirty paths and four current-control snapshots once.
2. Write the complete derivation and hand-authored fixture expectations before
   calculations. Bind the existing method and two CGU source notes. Reuse their
   source scope; no new literature survey or source downloads are planned.
3. Run only authored CPU-hidden standard-library Fraction checks in the
   existing tfgpu interpreter. Preserve exact command, duration and outputs.
4. Inspect disagreements and perform adversarial author review. Freeze only
   after read-only preflight, then record once and replay read-only. Refresh
   the four controls and retain every obligation and unselected admission.
5. Continue the next independent ready internal task; a nonunique limit blocks
   this proposed fallback, not the wider program.

Runtime/controller, installation, empirical campaigns, acquired-code execution,
commits, outreach, publication and fees remain held. Version 3.48/401/not_ready,
53 obligations, six interactions, 46 operations and zero whole-row closures
remain. At plan creation E3 and six scientific choices were unselected;
192 vintages remain unadmitted. During completion the user selected the
repeated-origins direction for the named companies. That separate successor
record changes no premise or result of this mathematical unit.
