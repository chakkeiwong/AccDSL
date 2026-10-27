# CappedParticipationEPS/1

Read-only conditional calculation under the retained EU2023/1803 original
IAS33.14(b),33–47,A13–A14. This is a specified finite method, not a production
engine or an opinion on an issuer's rights or operative law.

## Inputs and admission

`report` accepts exact canonical rational strings, a single fixed period and
context, positive whole-period ordinary/preferred populations, nonnegative
residual weight and senior period entitlement, and a total preferred cap at
least that entitlement. Supplied findings establish equity classification,
complete current-period entitlement, profit-only residual sharing, fixed rights,
absence of other dividends/attribution, equal continuing/total earnings,
independent gross effects, inventory completeness and constant populations.

Each identified potential series supplies its complete nonnegative gross
after-tax earnings adjustment and positive incremental ordinary shares. It
requires explicit findings for direct/consequential completeness, time weighting
and unconditional exercise. All series cover the whole period. Fractional
incremental shares are permitted because treasury-share results need not be
integers. Base counts are integer populations, not partially weighted shares.

The fixed source bytes are checked on every request. Unknown findings are
`unresolved`; false scope findings are `unsupported`; malformed requests,
contradictory rights, changed sources or context mismatches are `rejected`.
Refusal returns no basic/diluted allocation, selection, trace or mutation.
Successful output is `conditional_complete`, with basic/diluted allocations,
selected series and the recomputed trial at every ordering step. No journal,
dividend payable, cash payment or conversion is posted.

## Allocation and selection

With earnings E, ordinary count n, total participating weight m, senior
entitlement f and residual cap c, participation is
min(c,max(E−f,0)m/(n+m)). Preferred earnings equal f plus participation;
ordinary earnings are the remainder. Preserve the cumulative entitlement even
in loss periods; loss sharing beyond it is excluded by the supplied rights.

For E≥f the ordinary EPS is max((E−f)/(n+m),(E−f−c)/n).
The plan/source-reading derive the strict dilution test a−r*b<0 and optimal
ascending gross a/b prefixes for complete additive gross adjustments a and
incremental shares b. Reallocate class earnings after each assumption, compare
actual ordinary EPS and exclude equality. For E<f no nonnegative a and
positive b deepen the loss per share. This local theorem does not permit
additive ordinary-numerator increments or arbitrary dependent gross effects.

The independent verifier computes per-share claims first and reconstructs
class totals, enumerates every subset of the frozen series, and compares the
minimum with the ordered method. It preserves 18 hand-derived cases, 49 worlds,
input-order equivalence, source challenges and atomic adverse requests.

## Remaining F1 obligation

IAS33.35's consequential profit-sharing expense can depend on the combination
converted. A further method must calculate those consequences jointly. Actual
contractual exercise dependencies also require explicit eligibility/contingent
share rules; minimizing over an invented feasible graph does not establish an
IAS33 procedure. Neither dependence is admitted to this additive gross family.
Existing OrderedEPS/1 and lifecycle methods retain their original contracts.
