# Private loan terms, causal questions and joint scenarios

28 October 2026. C04; SIM-F013/017/020;
MC04/05/09/10/13/14/18/25/28/33/34. Attempt01 passes 170 exact checks, with
seven complete saved results and 22 refusal controls. Inputs, observable
policy paths, source snapshots and hashes are retained in attempt-01. Its
manifest records the command, Git commit, Python environment and elapsed time.
These are deterministic CPU-only examples, not an empirical comparison.

The manager receives supplied signed loan terms before making a reserve
decision. The analyst sees the same debt100 and cash10 but has not yet
accessed the terms. With coupons5/7, the manager can reserve5/7 and pay the
coupon without unused reserve. Before disclosure, the analyst's observable
history requires one common action. Reserve5 leaves floating-coupon arrears2;
reserve7 leaves fixed-coupon unused reserve2. Payment uses the earmarked
reserve under an explicit teaching assumption. No probability or preferred
policy is inferred from these alternatives.

Publication alone does not grant access. The analyst can use the terms only
at the supplied access timestamp; a fixed-offset equivalent instant agrees,
while a fraction of a second earlier does not. Private delivery does not need
a publication timestamp. Unknown access, unknown terms and conflicting
assertions do not generate a policy message. Source-byte changes, wrong loan
identity, inconsistent chronology and unsupported routes refuse. Repeated
identical assertions are idempotent. The complete manager policy cannot run
against the earlier analyst history because its observation keys are absent.

The loan-source projection is a separate, narrow fixture helper. The retained
ExactSourceTimeViews/1 engine supports other specific financial-family and
observation-scheme slots; it was inspected but not relabeled as a general loan
adapter. The new helper reuses exact timestamp conversion and the existing
finite observable-policy/path engine. Source text, assertion meaning, actor
receipt, public debt and loan population are supplied premises. Hash equality
does not authenticate them, and the result makes no actual-knowledge claim.

For F017, the supplied equations R=1+U, D=100-40U and Y=D-10R give cash40
when conditioning on R=2. Replacing only the rate equation preserves the
equal-mass U law, giving cash80/40 and mean60. The alternative equations
R=1+U, D=140-40R have the same observed joint law but give intervention cash40.
Thus the observed law does not identify which intervention answer is correct.
An imposed stress with the first model's explicit demand law matches its
intervention arithmetic by construction; the match does not establish causality.

For F020, the supplied joint scenarios (FX1,demand100) and (FX2,demand40)
give cash50/30 after cost50. Cartesian recombination invents cash-10 and150.
The joint-support query rejects those pairs relative to the declared family.
Unweighted scenarios provide bounds but no mean or probability. With explicit
equal masses the joint mean is40; multiplying the marginal laws instead gives
mean55 and negative-cash probability1/4. These are different declared models,
not estimates of company behavior. Unknown demand remains unresolved.

| Decision | Primary criterion | Veto diagnostic | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain F013 observable-policy evidence | Complete loan paths use only each actor's supplied observations | Unknown/conflicting/invalid inputs and hidden-policy reuse refuse | Actual source meaning, access and general loan integration | Connect reviewed source assertions to broader company state | Actual management knowledge or source admission |
| Retain F017 target distinction | Conditioning and equation replacement reproduce independent exact arithmetic | Same observed law supports different interventional outcomes | Which causal model, if any, is justified for a company | Continue source-based causal assumptions and uncertainty analysis | Empirical causal identification or forecasting |
| Retain F020 joint-support evidence | Paired scenarios preserve their cash range and declared measure | Unsupported pairs and incomplete masses refuse | Real economic dependence remains supplied | Bind supported joint scenarios and retain unresolved dependence | Empirical scenario probabilities or general stress validity |
| Continue program | All local checks pass | No global continuation veto | Remaining source, method and manuscript obligations | Review the next original gaps and source dependencies | Release readiness |

Post-run red-team: these helpers can compute a supplied assertion or structural
model correctly while that assertion or model is wrong about a company. The
source interpretation and economic assumptions remain the weakest evidence.
The computations equal their stated finite targets; actual actor information,
causal structure and joint-law calibration remain unverified. Original
acceptance statuses, protected helpers and frozen releases stay unchanged.
