# Derive exact typed monetary effects

24 October 2026. S2–S4; MC13/15/17/23/24/26/27/31.
Pre-run audit: data/accounting-master/monetary-effects-audit-20261024/design.md.

Question: can a closed, reusable expression program derive the selected native
settlement and whole-lot sale journals and gross flows, preserving exact types,
original input dependencies and unknown reasons? Baseline: recomputed
native_returns.transition, not the saved expected journal; additionally use
independent small rational examples and frozen v2 products.

Implement MethodMonetaryEffects/1 separately from frozen requirement profiles.
Reuse v1 canonical scalar/value validation and v2 type/product algebra. Support
ref, const, add, sub, mul and binary min on exact rational quantities. Declare
ordered named calculations with exact result types and transitive input
dependencies; reject forward/cyclic references and identity collisions. A closed
account registry and explicit cash account determine journal aggregation. Gross
flow activity and origin remain declared, ordered and distinct. No callback,
dynamic import, division, implicit rounding, scale conversion or unknown solving.

All declarations/expressions/types and fact records are checked before evaluation.
An unknown monetary result prevents a complete effect proposal; retain independent
known calculations as diagnostics, with original missing reasons. Negative
amounts are allowed algebraically: financial domains and funding belong to the
next event/state layer. A balanced journal and cash agreement are necessary but
cannot authorize a posting. All execution/admission/eligibility flags stay false.

Safety choices: <=1,000,000 canonical bytes per definition/fact map; <=4096
expression nodes, depth <=48, <=256 input/calculation/posting/flow/account entries
per category, and <=4096 bits per rational numerator/denominator. These are finite
implementation bounds, not economically justified defaults. Test their early
failure and preserve unknowns. Exact contexts/scales are required, with no implicit
conversion; static context equality does not establish source date admissibility.

Pass: exact independent arithmetic and recomputed native amount/journal/flow
agreement across normal, NRV-capped, zero, fractional, signed and unknown cases;
malformed/type/context/scale/dependency/cash/unbalanced cases reject; replay pins
source, implementation and fixtures. Preserve all previous package hashes and
run the focused existing unit suite. Counts are bookkeeping. Source drift or
invalid comparator is a continuation veto until repaired; candidate failure is a
repair trigger. No statistical or forecast comparison is run.

Artifacts: data/accounting-master/typed-monetary-effects-20261024/ with design,
cases, checks, source locks, manifest, result and replay. Exact command:
python3 -B data/accounting-master/typed-monetary-effects-20261024/verify.py --record
then --replay. CPU-only deterministic Python; CUDA_VISIBLE_DEVICES=-1.

After verification, refresh the next plan for complete event/state binding,
typed memory effects and atomic full-proposal recomputation. Preserve Version
3.61 until those semantics warrant coherent manuscript integration. No whole MC
row closes; S1–S5 partial, S6 held, S7 deferred.
