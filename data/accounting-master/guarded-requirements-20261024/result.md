# Guarded requirements preserve inactive, unresolved and invalid outcomes

24 October 2026. MethodRequirements/3 adds explicit guard/body dependencies and
required_known inputs through a separate layer over the protected v2 evaluator.
It checks types in every branch, even when inactive, and preserves all unknown
reasons. False guards yield not_applicable; unknown guards remain unresolved;
true guards use the body's declared consequence. An all-inactive selection
returns no_active_requirements and never grants method eligibility.

The increment passes 215 checks with 46 combined unit-test methods, 14 retained
guarded comparisons and 170 protected inputs. Independent tests cover all nine
guard/body truth pairs, known facts required despite inactive equations, malformed
inactive bodies, changed guard identities, missing capabilities and exact input
preservation. Retained unsettled, settled, inconsistent and unknown opening
cases agree with the selected original return-module conditions.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Retain explicit guarded successor | Activation table and scoped retained comparisons agree | No inactive type bypass, lost required fact or authority escalation found | Full collection/state coverage and versioned authoring/binding remain | Connect v2/v3 to explicit text and exact record binding | Complete method, automatic guard correctness, accounting/source authority or production readiness |

A caller can author a different guard only under a different manifest identity;
the evaluator does not prove the guard is sufficient for the financial method.
Residual requirements and all false admission/execution flags remain. The
comparison's nonnegative recovery premise, event/lot chronology, caller findings,
source admission and state effects remain separate. Guard success does not
authorize a transaction or erase a later missing tax requirement.

Evidence is deterministic engineering conformance, not accounting validation or
stochastic ranking. No whole requirement closes or global continuation veto
fires. S1–S5 partial; S6 held; S7 deferred. Version 3.59 remains 429 pages and
not_ready; binding, dimensional and guarded increments await integration.

Reproduce with python3 -B data/accounting-master/guarded-requirements-20261024/verify.py --replay.
Next: docs/plans/accounting-requirement-version-interoperability-20261024.md.
