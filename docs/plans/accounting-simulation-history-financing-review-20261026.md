# Simulation histories and financing: targeted review

Date: 26 October 2026. User question: preserve alternative journals consistent
with reports, repair debt/equity modelling, and identify relevant literature.
Requirements addressed: MC08–18, MC24–26 and MC28–35. This work is a targeted
design/source review, not an implementation campaign or release promotion.

## Work and skeptical audit

1. Reuse current mission/checkpoint and existing simulator survey; distinguish
   specified history/contract semantics from bounded executable examples.
2. Compare the supplied risky-debt note with Strebulaev–Whited §3.6 and derive
   lender cash conservation using explicit proceeds and promised repayment.
3. Inspect relevant retained technical literature, then record a recommendation,
   source limits and discriminating implementation acceptance cases.
4. Check any illustrative arithmetic, review citations and update the continuity
   records without closing a requirement or changing frozen releases.

Audit: do not infer missing design from an old prototype alone; inspect the
newer declared financing methods/schedules. Do not mistake a balanced journal,
solver residual or a toy numerical check for an identified company history,
accounting compliance or predictive validity. Verify the source's debt
convention rather than assuming the user's note is wrong relative to it.
Do not invent branch weights, equity market prices, recovery rules or general
equilibrium. Stop after the evidence-backed recommendation and scoped gaps;
no long experiment, neural training, external reviewer or engine rewrite.
This plan passes with those boundaries.

## Evidence contract and research intent

Main question: what state and financing semantics are needed to carry all
admissible explanations of reports into distinguishable shock outcomes?
Candidate: joint economic/contract/accounting history families, plus a separate
financing policy and event-to-journal layer. Comparator: current design and
bounded company/declared-financing code, not an invented zero-capability baseline.
Expected failure: report aggregation hides state; debt face and proceeds are
conflated; accounting consistency is mistaken for economic adequacy.

Pass criterion: each recommendation follows from inspected code/source or an
explicit derivation, and every claimed implementation gap has a scoped anchor.
Promotion veto: unresolved timing/units, conflicting source conventions or
unsupported paper claims. Continuation veto: inaccessible material essential
to the particular claim; narrow the claim instead of filling the gap.
Repair trigger: a debt convention discrepancy requires a standalone derivation
before recommending its use. Explanatory diagnostics: simple exact arithmetic
and same-report/different-shock examples. They establish no forecasting ranking.
Not concluded: complete literature coverage, a uniquely reconstructed real
company, default-ready financing software, model convergence or a validated
investment recommendation.

## Assumption audit

| Choice | Provenance / status | Justification | Failure / early check |
|---|---|---|---|
| Existing history-family design | Mission and chapters 5–8; baseline | Preserve intended semantics | Old code understates progress; inspect newer financing modules |
| One-period zero-coupon debt | Supplied note §3.6 source; diagnostic model | Makes proceeds/repayment explicit | Confusion over face/principal; compare both dated cash legs |
| Risk-neutral lender, constant risk-free rate | Explicit diagnostic assumption | Derive elementary break-even identity | Not a general market-pricing rule; state stochastic-discount-factor alternative |
| Positive default recovery example | Constructed arithmetic only | Zero recovery can conceal the convention mismatch | No calibration or empirical claim |
| Unweighted compatible histories | MC12; baseline absent justified measure | Reports need not identify probabilities | Branch multiplicity must not imply likelihood |

## Deliverables

- `docs/design/research/simulation-history-financing-review-20261026.md`: reader
  answer, derivation, evidence anchors, recommended sequence and source limits.
- `data/accounting-master/simulation-history-financing-review-20261026/`:
  diagnostic/source manifest, exact arithmetic and any newly retained extracts.
- Additive entries in requirements and current product checkpoint; no existing
  acceptance wording, phase sequence or frozen hash changes.

Meaning to preserve: identical reports need not identify journals; even identical
journals need not identify contracts; financing behaviour is additional to
accounting; model equity value is not book equity; source transcription fidelity
does not resolve a cash-flow inconsistency. Human judgment of prose is pending.

## Completion

All four bounded review steps are complete. The research note and result record
retain the recommendation, source-convention finding, exact diagnostic and
source limits. Newer financing methods were inspected as planned. A refreshed
checkpoint identified Version 4.41; the inherited 4.40 status was not reused.
No engine implementation, manuscript integration or solver experiment is
claimed by this completion. See the result record for the next justified work.
