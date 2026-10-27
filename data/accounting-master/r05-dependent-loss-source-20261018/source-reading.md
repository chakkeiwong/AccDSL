# Dependent forecast losses: checked source and code

18 October 2026. Documentary R05 preparation for E3, not an admitted run.
The comparator is `future-validation-20261015/protocol-ledger.md`, updated by
`protocol-delta-refresh-20261018/protocol-supplement.md` and the selected-panel
`r05-vintage-admission-20261018/admission-note.md`.

## Identity and actual reading

Minchul Shin and Nathan Schor, *ForeComp: An R Package for Comparing Predictive
Accuracy Using Fixed-Smoothing Asymptotics*, arXiv:2603.07458v1, is a matching
45-page primary preprint. The landing page records submission on 8 March 2026;
the PDF cover says 10 March 2026. These are different recorded dates, not an
inferred second version. Only v1 was observed in this bounded check. No
withdrawal/correction notice was observed on that landing page; comprehensive
notice coverage and a later published version are not established.

The source-unit reading covers physical pages 1–23, including sections 2–9,
equations (1)–(17), the applications, simulation design and references; Appendix
A, pages 24–26, was read completely. Appendix B's table captions on pages
27–45 were inspected, with full extracted pages 27/28/29/31/34/38/43 inspected.
This is not a claim to audit every numerical cell on every appendix page.
Rendered pages 3 and 29 were also viewed. Page 3 confirms equations (1)–(3);
page 29 confirms the UCR caption, axes and Table 15's first diagonal h=12,
P=25 entry 0.077. The paper's simulations have not been reproduced.

The original DM1995, HLN1997 and Diebold2015 full texts remain source-blocked.
Their metadata and ForeComp's descriptions do not constitute reading those
papers or inspecting their proofs. A guessed arXiv identifier instead fetched
San and Staples' incompressible-flow paper; that response is rejected identity
evidence and supplies no forecasting support. See the acquisition repair plan.

## What the primary text supports

Section 2, equations (1)–(4), defines one scalar paired loss differential
`d = loss(forecast 1) − loss(forecast 2)`, with positive values unfavorable to
forecast 1. Its hypothesis is two-sided equal expected predictive accuracy,
`E[d]=0`, and its statistic uses the long-run variance of a time sequence.
Stationarity, ergodicity and positive long-run variance are listed there;
the paper supplies no complete new CLT/FCLT proof establishing that this list
alone suffices for the project's panel. The covariance representation helps
state the inference problem; it does not verify its assumptions for these firms.

Sections 3.1–3.2 distinguish rectangular h−1 truncation, the modified statistic
and t critical values, Bartlett normal inference, and fixed-smoothing
alternatives. A finite-sample adjustment is not an exact finite-sample theorem.
Section 8.1 explicitly constructs an example where rolling-estimation loss
dependence extends to R−1, beyond h−1. Forecast horizon alone therefore does
not justify a dependence cutoff for the actual forecasting procedure.

Equations (9)–(10) use Bartlett smoothing with `ceil(1.3 sqrt(P))` and critical
values depending on the actual bandwidth ratio b=M/P. Using the larger
bandwidth with normal critical values is a separate procedure, DM-NW-L.
The displayed practical rule is not literally a sequence with constant b as
P tends to infinity: its b tends to zero. Neither that observation nor a
reference to fixed-b theory establishes target-specific validity for this panel.
The rule is transferred practice, not a project-selected default.

Equations (11)–(13) describe EWC, weighted-periodogram and block-mean methods.
Section 3.2's block procedure treats q nonoverlapping block means as independent
inputs to a t test. Nine issuer labels do not establish such independence;
shared calendar shocks, common estimation and overlapping targets must be
addressed. The cited original theory remains uninspected here.

Sections 4.2–4.5 and Table 2 take a numeric vector of differences. The API's
rectangular-test horizon and the SPF application's nowcast label h=0 require
an explicit mapping; an SPF label is not authority to pass h=0 to an h−1
truncation routine. Section 5 uses listwise deletion; section 6 substitutes
zero for undefined forecast errors in its replication. Those example choices
have different consequences and do not define a missing-outcome policy here.

Section 4.5's Plot_Tradeoff fits a model to demeaned observed losses, simulates
null losses and reports bandwidth sensitivity. It is explanatory sensitivity
under the fitted model. It cannot independently validate that same model,
establish the panel's sampling law, or justify choosing a bandwidth because
it changes the desired rejection decision.

Section 8 and Appendix B report 5,000 replications per design, P in
25/75/125/175/1000, horizons 1/3/12 and rolling-estimation variants. Only the
R=R-tilde diagonal is an equal-loss size design; off-diagonal results must not
all be called size distortions. Table 15's UCR diagonal R=R-tilde=25, P=25,
h=12 reports 0.077 for DM-FB; Table 33's corresponding CR entry is 0.064.
These are source-reported descriptive frequencies, without a local uncertainty
analysis or reproduction. Size-adjusted power's diagonal 0.050 uses empirical
null critical values; it is not evidence of real-world exactness. Eight annual
years, mixed interim horizons and nine issuers are not these simulation designs.

The reference to Müller “2004,” *Journal of Econometrics* 141(2):1331–1352
has an unverified year/volume combination. Preserve the source's reference
as printed; no corrected citation or theorem is inferred from it.

## Inspected package boundary

The retrieved CRAN mirror archive contains `cran-ForeComp-6354aea`, package
1.0.0. DESCRIPTION names both authors, links to `mcmcs/ForeComp`, dates CRAN
publication 20 February 2026, and declares GPL >=3. Its archive and file hashes
pin the inspected bytes. Only short revision 6354aea is supplied; the full
commit and equality to the paper's replication revision are unestablished.
The author development repository was identified but not fetched. No R
installation, package execution, tests or simulation was performed.

Inspected spans, relative to that extracted root:

| File | Lines inspected | Finding and support limit |
|---|---|---|
| DESCRIPTION | complete | Identity, version, provenance, dependencies and declared license; no reuse approval |
| R/forecast_util_functions.R | 1–105 | `loss.diff.p` computes first minus second; four point losses; not distributional CRPS/energy inference |
| R/forecast_eval_functions.R | 35–136, 137–153 documentation, 153–256, 278–321, 406–468 | Rectangular/modified, Bartlett normal/fixed-b, EWC and contiguous near-equal block means; static behavior only |
| R/Plot_Tradeoff.R | 69–137, 201–241, 278–360, plus named-anchor searches | Default preprocessing, fitted simulation and size-adjusted outputs; not every branch audited |

In particular, `na_handling=c("zero","drop","error")` followed by `match.arg`
selects zero by default. The code first computes the loss difference and then
replaces **every nonfinite difference** with zero in that branch. This is
broader than section 6's example-specific forecast-error substitution. A zero
observed difference denotes tied losses; a missing or infinite difference does
not establish a tie. Direct default use would be wrong relative to an E3
claim that preserves missing targets and failure denominators.

`n_sim=1000` is a convenience default. The inspected simulation fits stationary,
nonseasonal, no-mean `auto.arima` to demeaned losses, max.p/max.q=12, AIC,
then uses Gaussian innovations through `arima.sim`. Empirical absolute-statistic
quantiles produce size-adjusted power; fixed-b decisions use two-sided
polynomial critical values. These choices need their own design/assumption
review if ever proposed here. Package availability does not select a procedure,
validate a finite-panel interval, or complete dependency/license clearance.
