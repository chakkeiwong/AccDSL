# A guaranteed benefit changes the insurer's exposure

12 October 2026. E07/C05, P17; MC16/19/22/28/30/32–35, G7/G8/G16.
The retained AASB 17 source supports a material extension of the manuscript's
conditional 10% share example. The entity's share of underlying fair value is
one component of the variable fee; B104 also subtracts fulfilment cash flows
that do not vary based on underlying returns. Guarantee-related financial
changes and the share component have specified CSM treatment, with onerous
and risk-mitigation exceptions. A simple percentage cannot supply the whole
accounting movement.

All **30 source/preservation checks and 15 exact-arithmetic checks pass**.
Nineteen source anchors are retained. Nineteen selected PDF pages were read;
six source renders (1, 13, 14, 50, 51, 52) were inspected. They confirm the
edition, paragraph structure, cross-page continuations of 45/B107/B116 and
the different B115(a)/(b) instrument lists. The result is scoped to compilation
no. 4: annual periods beginning from 1 January 2023 and before 1 July 2026.
It is not a full standard review or a current-rule/compliance conclusion.

The authored settlement component promises the larger of 90 and 90% of an
allocated held pool U. The amount left after payment is
U − max(90, 0.9U) = 0.1U − max(90 − 0.9U, 0).
For U = 80, 100, 120, the policyholder receives 90, 90, 108, leaving
−10, 10, 12. The first 20 increase in U leaves 20 more, comprising the
ordinary 2 share change plus an 18 reduction in the extra floor payment.
The next 20 increase leaves only 2 more. Zero-pool and zero-floor controls
also agree with the predeclared derivation.

The claimed and computed target here is the settlement component's residual,
and they are exactly equal under its declared payoff terms. The previous
20-times-10% computation is also correct for its expressly conditional share
component. Equating either with the complete CSM change would be wrong:
the diagnostic supplies no probabilities, pre-settlement valuation, discounting,
RA, service allocation, group loss component or complete contract. In
particular, B107/B108 assess variability over the contract's duration on a
probability-weighted present-value basis; these three unweighted scenarios
cannot establish direct-participation eligibility. The percentages are
illustrative contract assumptions, not statutory thresholds.

The source additionally distinguishes an identified reference pool from assets
actually held, locks eligibility to inception except for the specified
modification path, retains cash-flow interaction between groups, and keeps
reinsurance classification separate from its possible use in risk mitigation.
The complete condition/dependency map is in source-reading.md; exact excerpts
and normalized offsets are in source-anchors.json. No new evidence fills
actual insurer, contract, calibration or later-amendment gaps.

| Decision | Primary criterion status | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Integrate the guarantee mechanism and source distinctions | Selected provisions/dependencies read; exact payoff derivation and controls agree | No source-identity or arithmetic veto | Whether readers distinguish the simple component from measurement | Separate Version 2.47 with preservation and rendered review | Full VFA implementation or accounting compliance |
| Retain the current component calculation | 20 × 10% = 2 is correct for that component | Stronger whole-exposure/CSM interpretation is vetoed | Actual terms and other FCF changes | Explain the additional floor term and conditions | Rejection of the existing scoped illustration |
| Keep actual eligibility and valuation unresolved | No actual contract or admissible expectations supplied | Three-scenario eligibility/valuation inference is vetoed | Enforceability, inception expectations, probabilities, market/RA/service/loss/mitigation inputs | Continue supported specification and actual-source preparation | An admitted insurance contract, fair value or CSM journal |

There is no stochastic experiment, observed ranking or default change. The
finite checks are deterministic engineering/arithmetic evidence. Source
interpretation remains an author assessment pending independent domain review.
Post-run red team: U minus the benefit can be mistaken for insurance profit or
the standard's full fee. The planned prose must call it a settlement component,
explain the held-pool assumption, and separate investment assets from insurance
measurement. Full scope/insurance-risk and transition rules remain unreviewed
here; the limited source selection must remain explicit.

Version 2.46 remains current pending integration. The Apple indenture and forty
exhibits remain unresolved; frozen dates and E01/E05/E07/E08/E14 are unchanged.
Full readiness is **not_ready**. Next:
docs/plans/accounting-insurance-vfa-integration-20261012.md.
