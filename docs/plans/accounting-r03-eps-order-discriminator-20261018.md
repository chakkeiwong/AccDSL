# R03 — Three-series consequential-EPS ordering discriminator

18 October 2026. P15/P17/P19; MC17/24/26/28–30/32–35;
G2/G3/G7/G8/G10. Documentary derivation and exact reference arithmetic only.
Output: data/accounting-master/r03-eps-order-discriminator-20261018/.

## Question, baseline and skeptical audit

Can fixed standalone ranking with complete cumulative recalculation and repeated
marginal ranking produce different selections in the already declared
threshold-bonus model? The 17 October source inquiry explicitly says its
two-series probes cannot distinguish these policies. That is the baseline,
together with ConsequentialEPSWorlds/1's final-selection refusal and the frozen
3.44 manuscript. The earlier official-source routes are complete for their
scope: retain the failed guessed PDF, historical AASB compilation and IFRS tax
interpretation without retrying them. No new source acquisition is proposed.

The initial temptation to derive a general accounting selector is rejected.
An arithmetic minimizer is not automatically an IAS 33 admissibility rule.
Re-read the retained historical AASB 133.33–35 and 41–44, distinguish its stated
duties from the two candidate algorithms, and keep selection_status not_evaluated
in the admitted two-series method. Three-series diagnostic worlds are an
explicit extension for this derivation, not a change to that method's interface.
No version-3.44 claim is rewritten by a new external note.

The revised plan passes skeptical audit: exact world amounts, strict evaluated
decisions and a small analytic parameter interval can distinguish the policies
without a hidden floating-point tolerance, stochastic score, weak comparator,
tax-law inference or search-driven promotion. A contrasting additive case tests
whether the disagreement is caused by the supplied consequential expense.
No global program/controller/runtime command is needed.

## Research intent and evidence contract

Main question: the policies' mathematical equivalence for this supplied model.
Mechanism: crossing a common bonus threshold changes relative marginal earnings
per incremental share. Expected failure: a frozen ordering can retain an issue
that raises the final ratio relative to removing it, despite every addition
having lowered the then-current ratio.

Candidate policies are fully defined before calculation. Fixed policy sorts
each standalone complete earnings increment divided by its shares once, then
tests every issue against the recalculated current world; rejected issues are
not revisited. Marginal policy recomputes those ratios against the current
accepted world before choosing the next issue, tests it, and removes it from
the remaining queue whether accepted or rejected. Exact equality is excluded
by the strict decrease rule. Stable IDs break ratio ties for reproducibility;
the main example has no ranking ties or tied evaluated acceptance decisions.
These are candidate definitions, not source-attributed rules.

Primary completion criterion: a hand-derived, exact three-series discriminator
with all eight worlds, both traces, all six sequential permutations, independent
fraction comparisons, an analytic interval and an additive control. Failure to
find the nominated difference rejects this example and triggers inspection of
the hand derivation; it does not justify selecting another rule by convenience.
No numerical search, sweep, random seed or empirical outcome is involved.

Promotion vetoes: arithmetic mismatch, an omitted consequential effect, ranking
or threshold ties driving the main result, mutation of the admitted method, or
calling a conditional minimum legally admissible. Continuation vetoes: protected
state corruption or source identity mismatch. Check counts, permutation counts
and wall time are explanatory only. A correct counterexample can reject a
mathematical equivalence claim; it cannot establish a generally valid selector,
current-law treatment, whole-company readiness or independent acceptance.

## Supplied model, defaults and hand calculation

Use P=90, H=100, bonus rate q=1/2, complete tax rate t=1/5 and n=72 ordinary
shares. Series A saves 10 interest/adds 40 shares, B saves 60/adds 34, and C
saves 10/adds 8. For each subset S:

    x(S) = 90 + sum(I_i)
    bonus(S) = (1/2) max(x(S)-100, 0)
    tax(S) = (1/5) [x(S)-bonus(S)]
    N(S) = x(S)-bonus(S)-tax(S)
    D(S) = 72 + sum(b_i), r(S)=N(S)/D(S).

Hand expectations in subset order empty/A/B/C/AB/AC/BC/ABC are earnings
72/80/100/80/104/84/104/108 and denominators 72/112/106/80/146/120/114/154.
Standalone increment ratios A=1/5, B=14/17, C=1 order A/B/C. After A, marginal
ratios B=12/17 and C=1/2 reverse the remaining order. Fixed A/B/C accepts all,
ending at 54/77. Marginal A/C/B excludes B, ending at 7/10. The difference is
1/770. Compare all subsets only as a descriptive mathematical envelope.

Vary only the symbolic ordinary count n: strict disagreement is nominated for
71<n<220/3, including integer counts 72 and 73. Verify those endpoints and the
outside n=74 case as exact boundary diagnostics, not a tuned parameter sweep.
Also set q=0 at the same inputs; then increments are additive, both rankings
are A/C/B and both select A only. Retain the old P80/P90 two-series arithmetic
as explicit baseline checks rather than rerunning frozen recorders.

| Material choice | Provenance / justification | Failure mode / early diagnostic | Status |
| --- | --- | --- | --- |
| Threshold bonus and proportional complete tax | Existing supplied consequential-world model; isolates IAS 33.35's expense interaction | Mistaken for real recognition/tax law; state supplied rights and reconcile each world | Conditional model hypothesis |
| Three synthetic whole-period series, positive shares and savings | Smallest extension able to distinguish the existing two policies after a shared first choice | Quietly extends the admitted exactly-two-series interface; keep all output external | Diagnostic scope only |
| n=72 and the nominated series amounts | Hand construction from the analytic acceptance inequalities | Tie or one-point accident; strict traces, n=73 and boundaries | Counterexample, not default |
| Fixed versus recomputed ranking | Two explicit candidates left unresolved by the prior source inquiry | Algorithm mislabeled as standard; define both and maintain refusal | Unselected candidates |
| Fraction arithmetic, standard-library CPU | Exact finite positive denominators | Floating-point or copied-oracle agreement; hand worlds and cross-products | Author verification tooling |

Pre-mortem: two programs can agree on a wrong formula. Independently derive
the piecewise affine earnings expression and cross-multiply positive ratios;
transcribe expected worlds before execution. The minimum over subsets remains
explanatory even if both programs find it. Historical source wording cannot
alone resolve the contextual ordering interpretation.

## Execution, records and continuation

Before calculation, snapshot the four live controls, all 36 tracked dirty
hashes, HEAD/index/staging, frozen 3.44/R08, completed R05 evidence and exact
prior EPS source/contracts. Only the four live controls may change among
existing files; all derivation/evidence files are new. No manuscript edit,
installation, runtime/controller, empirical work, commit, outreach or fee.

Use /home/chakwong/miniconda3/envs/tfgpu/bin/python3 with standard library only;
intentionally hide GPUs with CUDA_VISIBLE_DEVICES=-1 before imports. The new
verify.py exposes one-time --prepare, --calculate and --record stages; ordinary
replay writes nothing. Preserve actual commands, elapsed time, environment,
sources and output hashes. Write derivation/source-boundary/result notes and
decision/inference-status tables. Add a separately bound R08 supplement and
refresh the four controls after interpreting checked results. Record source
limits, the strongest competing interpretation and the next exact question.

Stop this finite unit after its discriminator and read-only replay. A failure
of candidate equivalence does not invalidate the conditional-world method or
the research direction. Continue another independently ready R03–R06 unit;
do not repeat the earlier source routes or claim a general selection answer.
