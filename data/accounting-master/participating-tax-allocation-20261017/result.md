# Participating-tax reference result

17 October 2026. The documentary ParticipatingTaxEPS/1 method passes **624
deterministic checks**, zero failures, in `attempt-01/checks.json`: 13 authored
cases, 27 exact payout/rights/rate combinations, 42 adverse requests and 10
protected-input challenges. `attempt-01/manifest.json` records the executed
command, commit, environment, elapsed time and output/source identities.

The published ordinary earnings numerators 120, 200 and 40 are reproduced.
The source's base balances move 0 → 330 → 550 → 0, and the final residual-tax
adjustment is −150. Recognition of actual benefits in profit versus equity
changes reported profit but leaves admitted EPS allocation unchanged. The
zero-dividend first period allocates ordinary earnings of 120 even though the
ordinary base share of reported profit is only 30. No actual dividend or tax
asset is posted by this calculation.

The checked mathematical target is ordinary earnings under fixed proportional
base rights, ordinary-only tax-benefit rights, the source's contemporaneous
benefit payout pattern and supported supplied tax facts. The reference computes
the three source steps; an independent verifier computes current entitlements
directly as (b+ta)P. They are equal under the written derivation. Nonnegative
current base profit, supplied denominator and complete rights remain required.
Signed residual reversals do not imply an admitted loss-tax recognition method.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Admit the finite documentary basic-EPS allocation | Published numerators, signed reversal, class conservation, direct entitlement and timing invariance pass | No numerical/source mismatch; incomplete, contradictory, unsupported and future-information requests refuse atomically | Real rights, current tax applicability, benefit recognition and retained/other benefit-sharing profiles | Integrate the method and exact source limits into Version 3.39 | No production posting, tax-law determination, nonadditive dilution selection or current issuer admission |

The strongest alternative explanation for a passing check is that the two
calculations merely encode the same unsupported assumption. Here the three
source numerators and negative reversal provide independent primary examples;
the direct derivation checks the particular extension to other rational
parameters. The weakest evidence remains application outside the supplied
rights/tax facts. An example with retained tax benefits, changing rights or
shared tax benefits would require another allocation analysis; this method
explicitly refuses those findings rather than claiming coverage.

This is exact deterministic evidence; stochastic ranking is inapplicable.
Manuscript integration/rendering and candidate assessment are recorded separately.
