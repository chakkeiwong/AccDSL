**Findings**

E11 is concretely scoped. Q1–Q2 name the supported fragment (rational linear equalities/inequalities plus finite logical choices after expansion), the excluded operations (bilinear quantity×price, unknown-rate powers, unrestricted functions), and distinct incomplete outcomes: solver timeout/unknown (not infeasibility), partial coverage records, `unresolved_bracket`, `numerical_failure`, `unsupported_root_selection`, `rounding_unresolved`. The IRR monotonicity argument, sup-vs-max and joint-vs-marginal extrema points, and the rational-power exact/enclosure rule are correct as stated. Continuously compounded rates are explicitly declared to need a separate error-controlled exp/log, not quietly assumed.

E13 is concretely scoped. Q3 gives a finite LawDefinition with a checked worked posterior (1/4, 2/3, 11/12 → 3/11, 8/11), mass-retention for unresolved branches, the Gaussian baseline with correct arithmetic (V=4/5, m=8/5; cash mean 116, variance 80; repeated-observation diagnostic 16/9, 4/9), the invalid density-plus-indicator warning, and the bounded set-valued result [5,7]. Q4's causal counterexample (observe → Y=3; do → mean 2.5) is correct. Q5 is a predeclared protocol with no executed claim.

I find no material numerical or probability method hidden as "later runtime." Each deferred capability (exp/log, ex

act-constraint Gaussian conditioning, non-Gaussian quadrature, MCMC) carries an explicit unsupported/unresolved status or precondition list rather than an implied default.

**Needed repairs (minor, non-blocking)**

1. Q1 says primal/dual evidence is checked "where provided." A min/max returned without an independently checked certificate should carry a distinct status (e.g. `uncertified_extremum`) so uncertified LP results are not conflated with exact ones.
2. Q2 "exact constraints are a separate method" and "separately error-controlled exp/log" should map to named initial-profile unsupported codes, matching the other outcome labels, so the profile's refusal surface is enumerable rather than prose.
3. Q3 MCMC preconditions are listed but no acceptance test is fixed; E13's "optional Gaussian conditioning" wording should state that MCMC is excluded from the initial profile entirely, not merely optional.
4. Monetary quantization applies per enclosure; the method should say whether aggregate postings (sum of several enclosures) are quantized before or after summation, since straddle status can differ.

**Bounded agreement**

Within the scoped question, E11 and E13 supply concrete method answers and the negative assessment does not conceal a material omission. Broader obligations (exact rational LP implementation evidence, calibration data, Q5 dependence-aware resampling design) remain open and are correctly deferred, not resolved.

VERDICT: AGREE
