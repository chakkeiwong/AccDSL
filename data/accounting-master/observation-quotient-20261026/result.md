# Finite observation-preserving aggregation checked

26 October 2026. MC08/09/10/11/12/14/18/24/25/33/34; S2/S4.
The helper checks a proposed partition of a fully supplied finite model against
equal permitted actions, current outputs and the complete joint law or relation
of successor block, observation and immediate requested output. Its local
finite-horizon derivation is in design.md. No model probabilities are estimated.

Twelve accepted cases reproduce complete observable paths under independently
coded enumeration, including all four signal-contingent second-action choices,
duplicate successor states, mapped initial information and a first action using
that information, an unweighted relation,
multiple scenarios and a zero-horizon model. Eight rejected cases identify
unequal actions, outputs or joint kernels. Two deliberate representative merges
are additionally shown to change complete path laws despite matching all three
separate marginals. All 20 saved model/partition results and the 12 complete
path comparisons recompute. There are 38 boundary controls and 166 assertions;
four protected baseline files remain unchanged.

In the supplied lending example, a green observation leads to lending, while a
red observation leads to waiting. With signal accuracy 9/10, the exact paths
ending in cash movements +2, -4 and 0 have masses 9/20, 1/20 and 1/2. Duplicate
initial states preserve that law. Changing the association of signal and future
payoff while keeping both marginals fixed changes the policy's full path law.
This is a hypothetical arithmetic example, not measured credit performance.

For the unweighted loan types, the only retained two-payment paths are (-5,-5)
and (-7,-7). Recombining their one-period marginal sets invents (-5,-7) and
(-7,-5). The checker rejects that merge; it assigns no weights to these paths.

| Decision | Primary criterion status | Veto diagnostic status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Retain finite helper as design evidence | Full path equality for accepted cases; exact adverse witnesses and independent false-merge comparisons | No lost dependence, inferred weight, stale reuse or exactness after budget exhaustion in checked cases | Finite fixtures cannot prove implementation correctness for every input | Integrate the explicit sufficient condition and its checked finite scope | General state minimization or production implementation |
| Retain rejected partitions as counterexamples | Different actions, current output or joint kernel is exhibited | Rejection includes unreachable declared states by design | The condition is sufficient, not necessary for a particular initial policy | Refine the partition or retain hidden memory | Rejection of all possible aggregation methods |
| Preserve unknown status on resource stops | Comparison and path budgets retain unfinished obligations/frontiers | No quotient returned for an incomplete condition check | Validation and frontier construction are not streaming memory guarantees | Recheck with an adequate explicit budget | Scalable whole-company compression |

| Inference status | Result |
|---|---|
| Hard veto screen | 8 supplied merges fail the sufficient condition; malformed inputs, stale bindings and policy misuse are refused. These are finite engineering verdicts. |
| Statistically supported ranking | None; no stochastic experiment or sampled comparison occurred. |
| Descriptive-only differences | Case/path counts and wall time describe this run only. |
| Default-readiness | No algorithm, compression policy or numerical default is promoted. |
| Next evidence needed | Broader model-authoring and integration cases, independently implemented checker, and real-company state/information justification before runtime use. |

Red-team: a correct checker can preserve the law of an economically incorrect
supplied model. The strongest remaining alternative explanation is missing
persistent state or a mistaken observation law. No finite kernel audit here
identifies either from disclosures. A second risk was mutable aliasing: an
accepted quotient initially shared a current-output dictionary with its input.
The author audit found and repaired that before final evidence; a mutation
control now proves the returned dictionary does not alter the supplied state.
The first saved run had 148 assertions; the final run adds explicit negative
path comparisons and binding/alias controls. This was an engineering repair,
not evidence against the aggregation argument.

The claimed target is exact preservation of the specified finite observable
path law/relation. The helper computes a sufficient local condition; the
independent oracle computes complete paths for the selected policies. These
agree for accepted fixtures. No empirical calibration, accounting compliance,
whole-company adequacy, forecast accuracy or independent acceptance follows.
All admission flags remain false. S1–S5 remain partial, S6 held and E3 deferred.
No whole requirement closes.
