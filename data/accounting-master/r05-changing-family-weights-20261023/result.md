# Changing history families: the weighting convention matters

The diagnostic supplies a concrete counterexample to automatic per-history
normalization. It also checks two narrower repairs. No procedure is adopted
for E3 and no company forecast is evaluated.

Two synthetic features have equal earlier mean component CRPS of one. Their
inverse-loss scores are both one half. With one current history under each
feature, normalization gives weights (1/2, 1/2) on point forecasts (0, 2).
Adding another distinct full history whose OCF forecast is also zero changes
ordinary per-member weights to (1/3, 1/3, 1/3). The total mass at zero is now
2/3. At outcome two, CRPS changes from 1/2 to 8/9 despite an unchanged set of
distinct OCF forecast laws. This is exact arithmetic, not empirical evidence.

Allocating mass to features first holds their total masses at (1/2, 1/2) and
shares the first feature's mass between its two histories. It preserves the
original OCF law in this example. But splitting that feature category into two
equally scored categories again gives combined mass 2/3. A stable feature map
must therefore explain its partition and within-category allocation. Semantic
deduplication alone cannot supply a measure on distinct admissible histories.

A third candidate groups exactly identical OCF forecast laws for scoring while
retaining the distinct full histories for other quantities. It gives the
original (1/2, 1/2) OCF law in this fixture. If one OCF law receives inconsistent
features, the reference refuses the cell rather than choosing a feature or
averaging scores silently. This grouping is target-specific: two histories
with identical OCF laws may have different liabilities, liquidity, or joint
statement laws. They must not be merged in the company-history representation.
Equality of real continuous laws also requires a defensible comparison method;
point equality here is only a fixture.

The inverse transform fits mean component losses. It does **not** minimize
mixture CRPS. A direct mixture-objective procedure remains to specify and must
not inherit this diagnostic's fitting claim. The constant one, synthetic
features, equal within-feature sharing, and point-law support are unpromoted
choices. Arbitrary canonical-ID order resolves the fixture tie but cannot
justify a real accounting interpretation.

## Decision table

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Reject automatic per-history normalization as count-neutral | Added same-OCF-law history leaves OCF law unchanged | Fails: mass changes from 1/2 to 2/3 | Whether a substantively justified measure should change instead | Require an explicit predictive measure | History preservation is unhelpful |
| Keep feature-mass allocation as a candidate | Invariant within a declared feature group | Passes this case; feature partition still changes mass | Economic validity of grouping/sharing | Specify target-specific features and allocation | Unique or correct weights |
| Keep target-law grouping as a candidate | Identical target laws share one predictive representation | Passes point-law case; conflicting features refused | Equality and transport of general forecast laws | Develop direct mixture scoring on stable law features | Full histories may be collapsed |
| Accept timing/unseen-feature checks | No unreleased labels or silent removal | Four invalid cases refused | Actual eligible historical data remain absent | Preserve explicit unavailable-cell handling | A viable real fitting sample |

## Inference status

| Evidence class | Status |
|---|---|
| Hard veto screen | Count-neutrality claim fails for ordinary normalization; invalid timing/features/IDs are refused |
| Statistically supported ranking | None |
| Descriptive-only differences | No random estimates; exact fixture CRPS differences do not rank company procedures |
| Default readiness | No model, selector, allocation, feature map or inference default adopted |
| Next evidence needed | Direct mixture objective, target-law feature meaning, as-of source feasibility and a prospective design |

Attempt 01 (10 checks, three refusals) is preserved in the attempt-01 files.
The extension adds target-law grouping and the conflicting-feature refusal;
the current replay passes 12 checks and four refusals. CPU devices alone were
used; no acquired code or network access. The manifest measures only the short
reference/record command, not drafting time.

Strongest alternative: extra distinct histories may legitimately carry more
mass under an explicit reference measure. The diagnostic rejects automatic
count-neutrality, not every count-sensitive measure. Conversely, a target-law
quotient can suppress meaningful joint-output differences if applied outside
the chosen OCF target. The next repair must preserve the full joint histories
and state exactly what forecast distribution is being scored.

Safe replay: `env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B data/accounting-master/r05-changing-family-weights-20261023/verify.py`.
