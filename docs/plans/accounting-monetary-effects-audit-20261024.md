# Audit typed monetary effects before general transition execution

24 October 2026. S2–S4; MC05/13/15/17/23/24/26/27/31;
G2/G3/G10/G13/G15/G17. Preserve complete native state structure and all prior
requirement evidence. Do not overwrite frozen native transition/apply code.

Question: what exact reusable effect semantics are needed to derive the retained
settlement and whole-lot sale journals from before-state and event inputs, while
keeping failure atomic and verifying the proposed after-state by recomputation?
Baseline: native_returns.py transition/propose/apply and native_reports.py
report/carry, plus the pinned retained financial comparator. Inspect existing
Core 0 posting/effect IR and portable operation definitions before inventing a
second executor. Separate language gaps from already supported native effects.

Skeptical audit: accepting an authored journal or supplied after-state is not
derivation. A balanced journal can still use wrong recognition/measurement.
Generic callbacks or caller-supplied imports cannot supply missing semantics.
Unknown tax evidence need not block an earlier non-tax event. Failure must keep
the exact prior book and identity state; proposal hash equality is insufficient
without trusted recomputation. Preserve economic funding failure separately.
Typed multiplication requires explicit dates/contexts/dimensions, and min for
recovery measurement needs an explicit supported operator or existing equivalent.

First inventory exact native input reads, requirements, calculations, posted
accounts, cash classifications, memory changes and after-state checks for each
selected event. Link them to existing reusable representations and to concrete
test evidence. Identify unsupported domains, chronology, source binding and
schema obligations separately. Record a complete effect contract before choosing
the smallest implementation increment. The audit itself does not promote a DSL.

Primary artifact: a source-anchored operation/effect coverage map and a skeptical
comparison with existing IR, including exact algorithm/typing/replay gaps and an
audited next implementation plan. Counts are bookkeeping. Missing input/effect
coverage, unexplained defaults or caller callbacks veto implementation until
repaired. Candidate failures trigger specific repairs rather than ending the
simulator program. No whole-method or forecasting claim follows.

Artifacts: data/accounting-master/monetary-effects-audit-20261024/.
CPU-only source and deterministic checks; preserve exact input hashes, plan,
command/environment, result and next step. S1–S5 partial, S6 held, S7 deferred;
Version 3.61 remains not_ready. No external publication or paid review.
