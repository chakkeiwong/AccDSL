# Approximation cannot redefine the question

28 October 2026. C04; SIM-F052/053/054/055. Attempt01 passes80 exact checks
including15 solver calls. No random experiment or empirical calibration occurs.
The supplied probabilities are assumptions of finite teaching examples.

F052 uses fixed systematic resampling ordinates against common/rare masses
999/1000 and1/1000. One possible outcome keeps100 common copies and no rare
type; another keeps one rare copy. Both have uniform post-resampling weights
and ESS100. Static types remain fixed within their histories, and the original
two-type family stays intact. High ESS therefore does not certify persistent
type diversity or exact feasible support. A missing sample type triggers a
support diagnostic; it does not make every finite sample an invalid Monte
Carlo draw, nor prove the rare type impossible. Rejuvenation is not implemented.

F053 has target tail1/1000, proposal tail1/10 and loss1000. The target expected
loss is1. Correct likelihood ratios are1/100 in the tail and111/100 otherwise;
weighted enumeration reproduces1, while unweighted proposal loss is100. Four
full-support proposals give the same exact target. Missing target support,
negative mass and non-normalized proposals refuse. Complete two-draw enumeration
gives expected ordinary importance estimate1 and expected self-normalized
estimate325/28. They are different finite-sample estimators. This example gives
no variance or general method ranking.

F054 computes the probability of zero events in100 independent draws as
(999/1000)^100, approximately0.904792. Zero events cannot identify zero expected
loss: the supplied target remains1. Exact rational bisection brackets the
one-sided95% zero-event upper endpoint near0.02951305, with width2^-80 and
opposite endpoint inequalities verified. Complete binomial enumeration at
the supplied probability0.001 gives coverage1 for the corresponding upper-bound
procedure; this checks this finite case, not a universal coverage theorem.
The bound assumes a fixed sample size and iid Bernoulli trials under the
declared model. It does not address adaptive stopping or omitted mechanisms.

F055 compares certified intervals with the guard capacity>=100. An interval
wholly above100 is safe and one with upper bound below100 is unsafe. [99,101]
and[98,100] remain unresolved because both funding and failure are feasible.
[100,102] and the exact point100 are safe under the inclusive guard. Two small
point-error examples show opposite false decisions. Fifteen exact solver calls
agree with independent endpoint reasoning and preserve zero-budget Unknown
with the retained formula. The error bound is supplied, not learned or validated
against an actual surrogate.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain F052 support case | Two explicit resampling outcomes preserve underlying family | ESS-only exact-support claim refuted | Real prior and rejuvenation validity | Retain family and audit persistent types | Validated particle filter or exact sampled support |
| Retain F053 weighting case | Finite weighted sums equal declared target | Missing support and wrong measure exposed | Actual target/proposal laws | Preserve weight and support provenance | Method superiority or empirical tail probability |
| Retain F054 rare-event case | Exact no-event probability and confidence endpoint checked | Empty sample does not imply safety | iid/fixed-design and model assumptions | Match uncertainty calculation to sampling design | Posterior probability or universal coverage from one case |
| Retain F055 guard case | Solver witnesses agree with endpoint classification | False threshold decisions and lost Unknown rejected | Provenance of error bounds | Refine unresolved band or retain uncertainty | General surrogate adequacy |

| Inference status | Finding |
| --- | --- |
| Hard veto screen | Wrong support/measure/guard claims are contradicted or refused |
| Statistically supported ranking | None; these are exact finite calculations |
| Descriptive-only differences | Counts and diagnostic ESS describe these cases |
| Default readiness | No sampling, approximation or numerical default changes |
| Next evidence needed | Admitted model laws, target-specific approximation validation and broader query integration |

Post-run red team: exact arithmetic can still answer an unjustified probability
model. The weakest evidence is the supplied economic and error assumptions,
not the arithmetic. These cases preserve the distinction and close no broad
requirement. Continue numerical-objective/derivative failures, source research
and ordered reading from349. No global continuation veto fired.

Final verification passes all1,179 protected hashes, including997 frozen-release
files. The40-task program and original acceptance/failure populations persist.
