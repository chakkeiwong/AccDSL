# Projection, dependence and sampled bounds: SIM-F047/048/050/051

28 October2026. C04;MC08/09/10/11/13/14/18/28/33/34.

Question: do exact solver outputs preserve joint constraints when variables,
periods or samples are summarized? Baselines are the four original failure
discriminators, not a new approximation policy. Reuse rational_solver_v1 under
its existing exact fragment and a bounded diagnostic budget; preserve formulas.

Audit: projecting x=z+1,z in[0,2] implies x in[1,3]. Removing z and its constraints
does not compute projection. Persistent paths(0,10)/(10,0) each total10; selecting
the worst component independently invents(10,10) and total20. x-x is exactly0
when the occurrences are shared, while independent interval endpoints allow
[-1,1] for x in[0,1]. A sampled alpha maximum0.9 cannot be the full-domain
endpoint1. Use loss1-alpha to distinguish sampled minimum0.1 from exact0.

Primary pass: solver feasibility/attained bounds agree with independent
algebra and complete finite support; negative mutated models reproduce the
specific wrong answers while remaining explicitly different models. For the
projection, check endpoint/outside values and an exact quantifier-elimination
equivalence in the original affine notation. Do not call a manually authored
interval a generic native elimination algorithm. For dependence, preserve
finite type identity and compare a deliberately rectangular enlargement.
For sampling, do not invent probabilities or convergence evidence. Zero budget
must remain Unknown with its remaining formula, never a bound or default.

Assumptions: original scalar domains and paths are supplied fixtures; unweighted
finite alternatives do not define a distribution. Sample grid0,.1,...,.9 is a
deliberate diagnostic containing the original largest sample. Solver caps are
convenience bounds checked for complete coverage; any incomplete result is a
promotion veto, not evidence against the mathematics. Wrong shared identity,
false projection, unsupported endpoint or lost unknown triggers repair.
Corrupt protected dependencies or invalid harness veto continuation until fixed.
Counts/runtime explain tested scope. No empirical ranking, generic nonlinear
solver claim, default change, forecast or release admission. Preserve all
formulae, outputs, hashes, command/environment and results under
company-state-relational-bounds-20261028; original rows/statuses stay unchanged.
