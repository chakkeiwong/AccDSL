# Compound tax basis: issue-date result

16 October 2026. Attempt-01 passes 94 exact checks with zero failures,
covering four independently authored positive cases and thirteen adverse
inputs. The authored inputs and historical IAS12 source hash are unchanged.
The first draft's zero-rate and fixed-liability assumptions were corrected
before execution and are preserved in `pre-audit-draft/`.

For proceeds 100, liability 92, residual equity 8 and an explicitly supplied
tax base 100 at rate 1/4, the computed DTL is 2. It is charged to equity,
leaving net equity 6, with no issue-date current tax or tax expense. Thus
cash 100 equals debt 92 plus DTL 2 plus equity 6. With matching base 92,
the initial difference is zero. A supplied zero tax rate produces zero DTL,
and the alternative valid 90/10 split at rate 1/5 produces DTL 2.

The claimed and computed target is the issue-date IAS12.23 treatment for
the combined-proceeds tax-base profile, plus a separately supplied matching
base. The local derivation and source anchors are in `source-reading.md`.
Neither tax-base truth nor a current jurisdiction's rate is inferred. Other
tax-base profiles remain unsupported; missing inputs remain unresolved and
malformed/negative/inconsistent allocations reject. The calculator returns
documentary journal values and makes no book mutation.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Retain issue-date method | Exact source direction, equity origin and financial identities pass | No accepted-run failure | Actual fiscal allocation and rate | Integrate a bounded derivation; specify subsequent tax-base evolution independently | Complete tax lifecycle or real compliance |
| Keep subsequent periods separate | No schedule was supplied or computed | A complete-lifecycle claim would lack required inputs | Deduction timing, tax bases, settlement and origin of reversal | Source-specific next-period plan with authored consequences | Any unchanged company EPS or cash result under different tax bases |

| Inference status | Judgment |
|---|---|
| Hard veto screen | No failures in the exact specified cases |
| Statistical ranking | Not applicable to deterministic identities |
| Descriptive evidence | Counts describe coverage, not general accounting validity |
| Default-readiness | No default, current-law or runtime promotion |
| Next evidence | Tax-base roll-forward, profit/equity origin and company EPS consequences |

The strongest alternative explanation is a supplied tax base that does not
match the actual law. No arithmetic check can establish that premise. The
equity-origin check prevents a balanced but wrong issue-date expense posting.
This unit resolves the named initial-recognition calculation; later earnings
and EPS consequences remain open. The research direction is not rejected,
and no continuation veto fired.
