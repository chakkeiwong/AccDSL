# Four original debt-family discriminators

28 October 2026. C04; MC08/09/10/18/19/20/28/32.
Plan: docs/plans/company-state-original-debt-failures-20261028.md.
Attempt-03 passes37 checks over13 retained solver queries. No existing
compiler, adapter or financial/solver implementation is changed.

The original targets are SIM-F005, SIM-F007, SIM-F009 and SIM-F014. The
retained borrowing source compiles through core0_frontends_v1; from_p03
constructs its joint continuous fixed/floating family. An explicit equality
adds the original historical interest5 under principal100 and both rates5%.
It does not select a fixed fraction. The observations and source identities
remain synthetic and conditional.

Let F and V denote fixed and floating principal. The native family retains
F+V=100, F=100 alpha, 0<=alpha<=1 and F,V>=0. Historical interest is
(F+V)/20=5 for every member, so it cannot identify alpha. Under the supplied
7% floating reset, interest is I=F/20+7V/100=7-2 alpha. With opening cash95
and immediate payment, C=95-I=88+2 alpha. Thus I is in[5,7], C in[88,90],
and C+I=95 throughout the declared family. This is exact algebra in the
synthetic fixture, not an empirical forecast or general debt model.

| Original row | Exact retained evidence | Remaining scope |
| --- | --- | --- |
| SIM-F005: same debt/interest under fixed and floating contracts | Both endpoints and alpha=1/2 satisfy the same historical observations; the continuous family is retained, not replaced by three witnesses | Financial journal execution and actual source/contract admission are separate |
| SIM-F007: interest7 with cash90 | Both marginal values occur, but their joint combination is infeasible; separate below/above identity violations are infeasible | Other cash flows, taxes and different debt templates require their own relations |
| SIM-F009: resource stop called infeasible | Same feasible family with zero max_cells returns PartialSearch/Unknown, zero completed and one unresolved cell with the full remainder formula | This is an explicit search-budget control, not a wall-clock timeout or all solver failure modes |
| SIM-F014: repeated unchanged interest removes ambiguity | Two additional pre-reset interest5 equalities preserve both endpoints and the interior mixture | No posterior or probability law is supplied, so no probabilistic ranking or update is inferred |

Complete native query results, compiled IR, retained family formulas, witnesses,
exact original rows and source hashes are saved in attempt-03. The independently
authored borrowing fixture supplies the original cash/interest expectations.
Check counts are descriptive coverage only. The original failure statuses and
all201 original records remain unchanged.

Attempt-01 failed before solver execution because the harness used a nonexistent
CompileResult.valid attribute. The correct property is ok. Attempt-02 then
requested Z3 distinct through !=, which the native bounded fragment correctly
refused as UnsupportedFragment/Unknown. The harness wrongly expected infeasible.
Attempt-03 retains that refusal and uses supported strict comparisons to
exclude each side of the equality. Both earlier attempts remain available.
This is harness failure and repair, not evidence against the financial family.

| Decision | Primary criterion status | Veto diagnostic status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain exact four-row evidence | All predeclared financial/joint/coverage predicates pass | No lost feasible witness or false infeasibility in supported queries | Broader templates and actual evidence | Replace related-only pointers for these exact original targets | All201 mechanisms executed or packages closed |
| Preserve partial-search and unsupported meanings | Zero budget and unsupported syntax have distinct retained outcomes | No arbitrary retry or refusal normalization | Other resource and solver failure mechanisms | Keep native result/coverage in future callers | Solver completeness outside its declared fragment |
| Continue failure review | Failed harness repaired; underlying family remains viable | No continuation veto remains |193 prior unreviewed rows now reduce to190 after three newly inspected IDs | Continue remaining exact original cases | Research direction rejection or empirical prediction |

The strongest alternative explanation is that shared native code and simplified
cash assumptions make the checks too narrow. The independent algebra establishes
the exact target under those assumptions; it does not establish a whole-company
history. Repeated identical equalities preserve feasible sets by construction,
but this says nothing about updating with genuinely new rate-reset evidence.
No stochastic ranking, default change, source admission or release promotion.
