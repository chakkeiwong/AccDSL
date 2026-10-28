# Relational bounds and what sampling leaves unknown

28 October2026. C04;SIM-F047/048/050/051. Attempt01 passes87 exact checks over25
rational-solver calls plus a direct affine quantifier-elimination equivalence.
These are deterministic supplied examples, not empirical probability models.

For x=z+1 and0<=z<=2, the retained solver certifies attained x bounds1 and3.
Endpoints and interior2 are feasible;0 and4 are not. Direct Z3 elimination of
z is logically equivalent to1<=x<=3, checked by an unsatisfiable exclusive-or
counterexample. Removing z and its constraints instead admits0 and4. The
correct interval is a result for this affine example; no generic native
projection service is claimed.

The persistent type admits precisely(0,10) and(10,0), both totaling10. Removing
the shared type admits(0,0) and(10,10) as well, and total ranges0–20. Summing
stagewise maxima gives20 only in that enlarged model. It is wrong relative to
the declared persistent family. The change is not a conservative estimate of
the same exact support; it is an explicit enlargement that must be labelled.

For shared x in[0,1], x-x has exact range[0,0]. Treating the second occurrence
as independent y in[0,1] creates[-1,1]. Restoring x=y restores zero. The wider
range can be an outer enclosure if labelled as such, but cannot be reported
as the exact range of the original linked expression.

With loss1-alpha and alpha in[0,1], the exact attained loss range is[0,1]. The
deliberate grid0,.1,...,.9 has minimum loss.1. The unsampled alpha1 is feasible
and gives0. The remaining region(.9,1] has minimum0 and supremum.1, with the
upper bound unattained. Neither the sample minimum nor a truncated search
establishes the exact worst case. A zero-budget call retains Unknown, incomplete
coverage and its remaining formula.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain F047 projection case | Exact bounds, members and affine elimination agree | Dropped constraints admit false values | Broader projection fragments | Preserve implied constraints and unsupported scope | Generic native elimination |
| Retain F048 persistence case | Exact support has two paths,total10 | Rectangular shortcut invents20 | Real type persistence/evolution | Keep shared state unless a change is supplied | Dynamic ambiguity universally rectangular |
| Retain F050 linked-expression case | Shared x-x is0 | Independent-copy range is different | Larger nonlinear expressions | Preserve relational identity and label enclosures | Every interval enclosure exact |
| Retain F051 endpoint case | Full-domain endpoint and remaining interval checked | Sample minimum fails exact claim; budget remains Unknown | Actual sampling law and wider domains | Retain unsampled scope and certified bounds | Statistical convergence or empirical ranking |

| Inference status | Finding |
| --- | --- |
| Hard veto screen | False projection, invented path and false exact sample/range claims are rejected |
| Statistically supported ranking | Not applicable: deterministic fixtures |
| Descriptive-only differences |87 checks and25 calls describe tested scope |
| Default readiness | No solver policy or numerical default changes |
| Next evidence needed | Real source constraints, wider fragments and integration with scoped query services |

Post-run red team: these small exact problems validate their explicit relations,
not the adequacy of an issuer model. A wrong source mapping can supply a perfectly
solvable wrong relation. No global continuation veto fired; quiet rights,
information-state equivalence, cache scope and broader cases remain ready.

Final verification: final-verification.json records all1,179 protected hashes
unchanged, including997 frozen-release files. The program retains40 tasks,114
acceptance rows and156 clauses. The21 program-validator unit tests pass.
These checks preserve prior evidence; they do not close the broader program.
