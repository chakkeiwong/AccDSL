# Feasible decisions and the information they use

28 October2026. C04; LIT-F006/007/008/009. Attempt01 passes288 exact
checks,18 complete result groups,16 refusal controls and162 common-policy cost
comparisons. These are deterministic teaching examples, not empirical estimates.

LIT-F006: an indivisible100 issue against obligation50 has actions0 and1.
They leave unpaid50/cash0 or unpaid0/cash50, respectively. The illustrative
cost is issue count plus twice the default indicator, giving costs2 and1.
A relaxed half-issue appears to cost1/2 but is infeasible in the stated problem.
The validator refuses it. Explicit lifts to0 or1 remain feasible and preserve
their actual consequences; a lift that chooses differently on the same observed
cash according to hidden type refuses. This does not choose an economically
justified lift or prove a general approximation theorem.

LIT-F007: cash−epsilon replaced by+epsilon has point error2epsilon and default
probability error1. Three exact epsilon values retain the discrepancy. For a
supplied joint coupling of X and Y, strict default X<c, and delta>0, disagreement
requires either |X−c|<=delta or |X−Y|>=delta. The union bound followed by Markov's
inequality therefore gives probability error at most
P(|X−c|<=delta)+E|X−Y|/delta. The checker verifies the pointwise implication
on75 exact combinations and compares three complete finite couplings to the
bound. Their actual probability error is1/4 and mean cash error3/40. Equality
at the threshold is treated as nondefault. Without masses the result is an
uncertain boundary set, with no probability attached. The coupling, dates,
currency and error premises remain supplied assumptions; no approximation
algorithm has been shown to produce them.

LIT-F008: exact costs(0,100) and approximate costs(100,0) have identical minima,
yet the approximate optimizer incurs exact regret100. A zero uniform-error
claim refuses. On a genuinely common feasible policy class, a uniform cost
bound epsilon and eta-optimal approximate choice give regret<=2epsilon+eta:
the selected exact cost is at most its approximate cost plus epsilon, at most
the approximate optimum plus eta+epsilon, and at most the exact optimum plus
eta+2epsilon. The named finite example has regret1/5 and bound11/50; all162
two-policy comparisons on the declared grid satisfy the inequality. Different
policy identities, missing selected policies and false eta bounds refuse.
Shared labels still require the caller to establish actual feasibility and
information compatibility; these examples do not authenticate that premise.

LIT-F009: two supplied paths have first/second values(−.01,.99) and(.01,−.99).
Each distinct first observation identifies its only sampled continuation.
Enumerating stop at time0 or all stop/continue choices at time1 gives empirical
optimal cost−1/2. Pooling both first observations into one near-zero bucket
permits only common actions and gives0. This deliberately hides the small
first-value difference; its exact success uses the example's symmetry and is
not a general quantization guarantee. Under the four-path comparator with
independent equal-mass increments±1 at each first value, every feasible policy
has cost0, including the empirically selected rule. Choosing by the unobserved
future increment refuses. All input paths, observations, policies and losses
are saved so the changed information set is visible.

The source audit reads Pflug/Pichler Theorem6.1 and proof on physical10–11:
convex decision feasibility and conditional averaging are material to its
argument. It also reads adapted-estimation Example7.1 on physical20, whose
Gaussian-walk optimal-stopping construction differs from the local finite
example. We preserve that distinction. The local checks reproduce neither its
Gaussian law nor its asymptotic theorem. Earlier finite-compression and exact
case artifacts are pinned for context and were not rerun. No new source-status,
correction-search, whole-paper or survey-completion claim is made.

| Decision | Primary criterion status | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain four scoped discriminators | Full finite actions, couplings, policy costs and stopping paths agree with exact comparators | All expected refusals observed; no failed check | Real feasible policies, approximation coupling and information process | Continue ordered review361 and remaining original failures/source research | General approximation, actual policy transfer, forecast or release readiness |

The claimed target is feasibility and information-valid approximation within
the authored finite problems. The computed objects are complete original
action results, finite joint-law probabilities and full policy cost tables;
their equality or bounds hold under the stated premises. Check counts and
runtime are engineering diagnostics. No stochastic candidate ranking or new
default is supported. The strongest misleading alternative is changing a
policy class or hiding observations to obtain a better result; explicit input
records and refusal controls expose it. A source-backed example violating
these premises would require a new comparison, not extension by relabeling.

Command: python3 -B data/accounting-master/company-state-policy-boundaries-20261028/check.py attempt-01.
The attempt contains checks, complete results, original rows, source hashes,
snapshots and CPU-only manifest. Original acceptance statuses persist.
Selected5.55-R1/provisional5.56-D1 remain not_ready; E3 deferred.
