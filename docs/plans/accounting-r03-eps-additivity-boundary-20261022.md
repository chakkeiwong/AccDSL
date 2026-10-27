# R03 — exact additivity boundary for the supplied EPS consequence model

22 October 2026. P17/P19; MC17/24/26/28/29/32–35, G2/G3/G7/G10.
Output: data/accounting-master/r03-eps-additivity-boundary-20261022/.
The manuscript remains the frozen 401-page Version 3.48/not_ready candidate.

## Research intent and skeptical audit

Question: exactly when do complete earnings consequences in the existing
threshold-bonus model have fixed additive increments, as required by the
existing OrderedEPS/1 proof? This is a mathematical applicability question,
not a source interpretation selecting diluted EPS under nonadditivity.

Mechanism: a shared bonus threshold creates a nonlinear expense. Expected
failure: summing the isolated conversion effects overstates combined earnings
when at least two positive interest savings cross an initially unreached
threshold. Candidate: a necessary-and-sufficient additivity condition derived
below. Baseline: direct conditional-world earnings, with the existing additive
selector as a conditional theorem. Comparators are the frozen P80/P90 worlds,
strict fixed-versus-marginal discriminator and final-deletion-instability case.

Audit passes for this scoped analytical unit. It answers a new question left
open by the general-selector work, without trying to pick a legally admissible
path using minimum EPS. Exact additivity of the numerator does not establish
independent legal conversion choices, admissible tax terms, complete inventory,
ordinary-holder attribution or current authority. All those premises remain
separate. A finite grid validates examples and implementation, not the universal
claim: the written proof supplies that claim under the stated domain.

## Declared model and evidence contract

Let the finite series set have I_i >= 0 interest savings and b_i > 0 incremental
shares. Ordinary shares n > 0. Pretax profit P and threshold H are real; bonus
rate 0 <= q <= 1 and supplied complete tax fraction 0 <= t <= 1. Define

    N(S) = (1-t)[P + sum_{i in S} I_i - q max(P + sum_{i in S} I_i - H, 0)].

These are the previously supplied hypothetical terms, not actual recognition
or tax-law assertions. The theorem's domain explicitly excludes negative
interest savings, changing share increments, other dependencies and distinct
expense/tax models. The t=1 endpoint is a mathematical degeneracy, not a
default economic assumption.

N is additive over subsets iff at least one holds: q(1-t)=0; P>=H;
P+sum I_i<=H; or at most one I_i is positive. Prove sufficiency directly.
For necessity in the remaining case, put c=H-P with 0<c<sum I_i. The isolated-
increment numerator minus the complete full-set numerator is

    q(1-t) [sum_i min(I_i,c) - c] > 0.

Derive the identity and strict inequality rather than treating it as a claimed
oracle. Zero-saving series and equality at either kink boundary need explicit
handling. A modular function's isolated increments reconstruct every subset;
failure at the full set is a sufficient counterexample to modularity.

Primary criterion: a complete proof with exact, independently derived rational
checks for each boundary class and all three retained discriminators. A bounded
exhaustive finite domain checks equivalence against direct subset enumeration;
it is an algebra diagnostic, not a search for favorable performance. For
additive examples only, compare the existing fixed-ratio theorem's selection
with exhaustive minimum conditional ratios and both local candidates.
For nonadditive examples, record refusal of the additive premise; no final EPS
selector or interface extension is admitted.

Promotion vetoes: incorrect identity, omitted equality/zero-saving case,
failed counterexample, accidental acceptance outside the domain or accounting
authority claimed from mathematics. Continuation vetoes: protected input or
HEAD/index/unrelated-content changes, invalid inherited source identity or held
runtime/empirical activity. A failed proposed theorem triggers a written repair.
Check counts and timings are explanatory only. No stochastic inference applies.

## Defaults, smallest checks and execution

| Choice | Provenance/status | Risk and early diagnostic |
| --- | --- | --- |
| Threshold bonus and proportional tax | Existing explicit synthetic model | Do not transfer to other rights/tax models; reconstruct bonus/tax accounting identity |
| Nonnegative interest savings | Added explicit theorem-domain restriction | Negative effects break monotone bounds; reject such inputs before evaluation |
| Four additivity conditions | New mathematical hypothesis | Hand-check threshold equality, one positive series, multiple zero series and strict crossing |
| Rational arithmetic | Existing standard-library verification tool | Use direct expense/tax expression and separate gap identity; retain exact fractions |
| Small finite domain | Diagnostic convenience, not representative population | State limits and preserve proof as universal evidence; no model ranking |

Before calculations, protect the completed guidance attempt, Version 3.48 and
predecessor bindings, source/discriminator files, HEAD/index and 36 tracked dirty
paths. Snapshot four controls. Write the proof, hand-authored fixtures and
independent expectations before running the checker. Use CPU-hidden tfgpu
python3 -B and standard library only. No acquisition, installation or upstream
code execution. Retain command, environment, wall time, plan/result and output
hashes in the run manifest. Freeze an additive R08 supplement without changing
53 obligations, six interactions, 46 operations or zero closures. Refresh the
four controls and replay read-only.

Pre-mortem: the result could be misread as a new general diluted-EPS rule.
The proof establishes only a supplied numerator's fixed-increment property;
conditional-world selection outside that property remains unresolved. The
P80 and both strict three-series witnesses must remain visible in the result.
After this finite unit, continue independently ready review/preparation.

## Recovery audit and finite domain, before execution

The resumed proof audit finds the four-condition equivalence valid on its
stated domain. Corrected one transcription error before checking: P80's
isolated-overstatement gap is 8, whereas P90's is 4. No frozen predecessor
has been edited. The completed source-inquiry read-only replay passes.

The diagnostic grid is fixed in advance: P in {-2,0,1,2}, H in {-1,0,2},
q in {0,1/2,1}, t in {0,1/5,1}, and every ordered savings inventory of length
0 through 3 over {0,1,2}. There are 4,320 parameter/inventory combinations.
Set n=7/3 and b_i=(i+1)/2 in that grid. Shares do not enter the additivity
theorem, but these deliberately noninteger positive values exercise exact
denominator arithmetic. Independently hand-authored fixtures cover additional
rational, zero, threshold-equality and negative-profit cases, plus all prior
nonadditive witnesses. Invalid-domain controls must be refused before any
world or selector evaluation. For additive cases, both documentary candidates
must attain the exhaustive subset minimum; ties are allowed, and strict
admission excludes neutral additions. All nonadditive paths retain diagnostic
status and no final accounting selection. The proof, not this grid, supports
the universal equivalence.
