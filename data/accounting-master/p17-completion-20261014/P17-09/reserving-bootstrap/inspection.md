# Reserving bootstrap — technical inspection in progress

14 October 2026. Author inspection, no independent or human acceptance.
Plan: `docs/plans/accounting-reserving-bootstrap-20261014.md`.

## Primary retained version

England, Peter, November 2001, Actuarial Research Paper138, *Addendum to
Analytic and Bootstrap Estimates of Prediction Errors in Claims Reserving*.
Institutional record2275 and its linked `138-ARC.pdf` identify the author and
version. The PDF has24 physical pages: repository cover, title, historical
notice, then numbered paper pages1–17 and institutional trailing material.
It is a scan; ordinary text extraction captures only the repository cover.
Physical pages2–20 were rendered and inspected directly. Technical anchors:
paper pages2–7 §§1–5, equations2.1–2.6 and3.1, AppendixA pages8–12,
references page13, Tables1–3 pages14–16 and Figure1 page17.

Crossref identifies the separate December2002 journal addendum,
DOI10.1016/S0167-6687(02)00161-0. Exact equivalence is **not checked**. The
1999 journal article is not retained: its metadata text-mining link returned
HTTP400. The 2002 survey publisher PDF link returned HTML. These routes provide
no technical support. Distinguish the independently inspected 2001 method
from the earlier paper as described by its author. Do not cite the uninspected
1999 paper for a directly verified formula or assert a journal-wide error.

## Checked method and source boundary

The incremental GLM uses E[Xij]=mij, Var[Xij]=phi*mij and
log(mij)=c+alpha_i+beta_j, with alpha_1=beta_1=0 (2.1–2.3). This is a
particular model with positivity qualifications; identical chain-ladder point
estimates do not equate it with Mack's conditional cumulative model.
Unscaled Pearson residual is (X−m)/sqrt(m); phi is sum(r²)/(n−p), with n
observations and p fitted parameters (2.4–2.5). Equation2.6 describes the
earlier prediction-error combination: analytic process variance plus a
degrees-of-freedom-adjusted bootstrap estimation variance.

Paper page4 specifies: backward-fit cumulative observations from the latest
diagonal; difference to fitted increments; compute residuals and phi; adjust
residuals by sqrt(n/(n−p)); resample with replacement; invert to pseudo
increments; accumulate and refit factors; project and difference future means;
draw future payments conditional on those means and the fixed estimated phi;
sum by origin and total. AppendixA illustrates each transformation, including
gamma process draws using phi52601. It does not merely resample observed
payments or report the dispersion of fitted future means as predictive risk.

Section3's scaled-Poisson draw is phi*Poisson(m/phi); gamma is explicitly a
pragmatic alternative with matching mean/variance but different shape. A
fully specified process distribution is additional to the two moments. The
residual adjustment belongs before resampling; applying another n/(n−p)
factor to resulting estimation variance would double this correction.

### Local sign finding — source statement reconstructed first

Paper page5 proposes drawing X with mean abs(m) when the predicted mean m is
negative, then subtracting2*m. Taken literally, E[X−2m]=abs(m)−2m=−3m for
m<0, not m. For m=−4 the resulting mean is12, not−4. This prescription is
**wrong relative to its stated mean-preservation target in the retained scan**.
It does not invalidate the positive-mean two-stage procedure. Exact journal
wording and any correction of this passage remain unverified. A translation
X+2m or reflection−X can match mean m, but they have different support and
replace impossible negative variance phi*m with phi*abs(m). Neither becomes
an AccDSL default without a justified signed-claims model.

### Evaluation and comparison

The paper uses the Taylor/Ashe triangle and1000 simulations. Tables1–2 compare
point estimates and percentage prediction errors with analytic and earlier
bootstrap results; Table3/Figure1 summarize the simulated distribution. These
are descriptive source results, not an out-of-sample coverage study, statistical
superiority result, or evidence that an insurer's RA has been identified.
Section5 expressly allows different predictive laws with the same moments
and notes negative outcomes/practical difficulties. No local replication run.

## Maintained package inspection

Retained `mages/ChainLadder` commit
`5cd0dd441c3bb9e1ee6d7572d5bc1475f29be728`; DESCRIPTION0.2.17,
dated2023-01-09, GPL(>=2). This is the commit returned for the inspected
file's most recent change, **not a claim to be the latest package release**.
Inspected `R/BootstrapReserve.R`, `man/BootChainLadder.Rd`, DESCRIPTION.
The package credits Markus Gesmann/Nigel de Silva and follows the 2002
survey. It is maintained implementation evidence, not original-author code
or a replication of the retained2001 version.

`BootChainLadder` separates fitted-mean `ParamDist.ByOrigin` from simulated
payment `IBNR` results. It uses absolute fitted means in residuals and signed
gamma/process draws. Its `od.pois` helper uses a negative binomial when
dispersion differs from1, with size=m/(phi−1), rather than the scan's scaled
Poisson. For phi>1 the first two moments match but laws differ; for0<phi<1
this helper's size is negative. Thus `od.pois` is not a complete law identifier.

Additional adapter hazards visible in source: both simulation stages reset the
same seed when supplied; all NA process entries are converted to0; residual
summation uses `na.rm=TRUE`; the early rectangular-triangle check contradicts
the more general help text. These are static observations. No R execution,
empirical dependence effect, runtime failure frequency or production defect
claim has been established. A future adapter needs a structural missing-cell
mask separate from failed values, explicit RNG streams and supported shape.

## Forward source acquired, narrower audit pending

England/Verrall/Wuethrich2019 accepted manuscript, institutional record21270,
DOI10.1016/j.insmatheco.2018.12.002, is retained. §§2.2,3/3.2 distinguish a
Mack-ratio bootstrap from the incremental ODP model, and next-year payments
from the change in ultimate estimates after re-reserving. Equation5 defines
CDR=opening reserve−next-year payments−closing reserve. Relevant evaluation
and appendix inspection is still required before admitting further claims.
The introduction's then-expected IFRS17 effective date is historical and is
not current accounting authority.

## Follow-up inspection completion

The limited horizon claim is now checked through §4 Tables1–4 and Appendix1
complete procedure pp31–33. Physicalpage7 (paperpage6) was rendered to check
equations5–6 after text extraction dropped indices. Equation5 is opening
estimated reserve minus next-year increment minus revised closing estimate.
No higher-order/asymptotic bootstrap validity claim is admitted. Sections5–6
and Appendices2–3 are outside the imported claim and not claimed fully read.

The dated forward scan returned a consequential2024 consistency paper; its
retained arXiv2303.05913v1 is dated10March2023. This will receive its own
full technical audit before theorem or correction claims are imported.
