# P17-09/P18 — Reserving uncertainty supplement

14 October2026. Version2.85,254 pages; **not_ready**. Candidate:
`docs/design/proposal/manuscript-reserving-bootstrap-20261014/accounting-product-proposal.pdf`.
SHA256 `fa2d2a38f0c9ea2d420f7b346ff8f5496d0d9680b6aa8d89322ef05db82a5638`.

## Substantive result

The inspected2001 institutional England addendum specifies a two-stage
incremental reserving procedure: residual resampling/refitting for estimation
variation, then conditional draws for future process variation. The earlier
point estimate148 remains unchanged and insufficient to identify a predictive
law. The new section follows that triangle at §12.8, teaching the distinction
with exact authored finite laws and specifying positive support, residual
adjustment, shared-fit dependence and preserved failures.

Both authored laws have mean5 and variance19, but P(payment>8)=1/4 or1/10.
The fitted-mean law alone has variance9. Two cells sharing the same fit have
total variance56; independent marginal simulation instead gives38. These are
exact counterexamples, not stochastic estimates or calibrated insurance laws.
The sparse original triangle has zero incremental-model residual dispersion
with one residual degree of freedom; this is not evidence of zero future risk.

The retained2001 p5 negative-mean prescription is wrong relative to its stated
mean target: if E[X]=|m| and m<0, E[X−2m]=−3m. At m=−4 it is12, not−4.
The prescription is excluded; the positive-mean method remains a candidate.
Exact wording in the2002 journal version remains unverified.

The pinned maintained ChainLadder source uses a negative-binomial helper for
`od.pois`, unlike the scan's scaled-Poisson draw. It also requires adapter
attention to signed support, missing-value masks and repeated seed resets.
These are static code observations; no R runtime or defect-rate claim follows.
The inspected2019 accepted manuscript supports a separate one-year CDR
target: opening100−payments30−revised closing80=−10, requiring re-estimation
under the year's information. It is not the lifetime payment distribution.

## Evidence and limits

-46 exact checks pass; no random sampling, ML framework or GPU initialization.
-85 manuscript preservation/build checks pass:70 predecessor sources intact;
 displays86→87,labels154→155,citations445→454; bibliography append-only.
-73 project build inputs reside inside the new candidate. Build has no
 recorded diagnostics. Physical pages1,182–185,247–248 inspected, including
 the supplemental bibliography check. Whole-candidate/human review remains pending.
-All six literature ledgers updated; all historical rows preserved. Source
 and forward/version/omission records distinguish publication and retained
 working versions. Four previously blocked originals remain untouched.
-100 unrelated staged entries exactly match the protected index snapshot.

## Decision table

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Integrate bounded procedure and counterexamples | Passed within stated scope | Literal sign prescription excluded; no unit-wide veto | Residual/process assumptions and empirical adequacy | Inspect consistency follow-up; finish target-specific protocol | A fitted or unique predictive law |
| Keep package as candidate evidence | Static behavior checked | Unwrapped mask/law/support semantics not accepted | Runtime behavior and dependency integration | Later precise adapter review without installation | Production compatibility or defect rates |
| Retain overall negative readiness | Required design/integration obligations remain | P17/P18/P19 incomplete | Whole-company interactions and acceptance | Continue audited ready work | Completion from build/counts |

## Inference status

| Category | Result |
|---|---|
| Hard veto screen | Exact sign counterexample rejects one retained-version prescription; invalid support/nonfinite draws veto a complete result |
| Statistically supported ranking | None; no stochastic comparison conducted |
| Descriptive-only differences | Published1000-draw and2019 analytic-comparison tables; no local ranking |
| Default-readiness | No method, law, replication budget or RA default promoted |
| Next evidence | Consistency assumptions/proofs, real-target diagnostic protocol, downstream measurement validation |

## Post-run red team and continuation

Strongest alternative explanation for the source sign issue is a working-version
typo corrected in the journal; this is why the conclusion is scoped to the
retained scan. Strongest challenge to the optional procedure is that matching
conditional moments or analytical prediction errors need not establish a
correct full predictive distribution. A new2024 forward lead directly
addresses Mack-bootstrap consistency; its retained2023 author preprint will
receive the next independent technical audit. It is not used as theorem
support in2.85.

Weakest current evidence is real-target empirical suitability, which this
documentary unit does not test. No continuation veto fired. A rejected
negative-mean prescription does not reject reserving research; it triggers
explicit support checks. Continue P17-09 consistency, then current interface/
interaction work. P17/E07/E08 and P18 whole-candidate review remain open.
