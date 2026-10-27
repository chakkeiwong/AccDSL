# Connect claim relationships to the existing settlement policy

28 October 2026. T01/T04/C04; MC08/09/13/18/19/28/33/35.

## Audit, question and evidence contract

The existing SettlementPolicyDraft/1 transformer already binds named delivery
operations, claims, collection operations and exact shares. Do not build another
policy engine. Inspect whether the new relationship trace preserves those
bindings and whether a locally valid transformed year remains feasible under
the full existing three-year continuation.

Baseline: unchanged example path and unchanged 9/10 policy. Conditional
controls: 4/5 and 1/1 collection fractions, chosen as exact arithmetic probes,
not calibrated behavior, recommended policies or probability assumptions. The
1/1 control is expected to leave later authored collections targeting already
settled claims. A downstream over-settlement is evidence of retained memory
and incompatible authored continuation, not evidence against policy modeling.

Primary criterion: every policy allocation trace binds to its exact
year-qualified claim relation and independently calculated invoice*fraction*share.
All non-target path fields and all earlier-year histories remain identical.
The original fraction reproduces the baseline; changed fractions preserve
full native results and any later refusal. Native actor-information and forecast
admission stay unresolved/false.

Promotion veto: mismatch, fabricated identity, erased refusal, changed non-target
field or admission upgrade. Continuation veto: corrupted source/input or native
binding failure; preserve the failed attempt and repair. Counts and timing are
explanatory. No stochastic ranking or numerical-policy default change.

Assumption audit: exact rational shares and target scope are inherited native
conventions; inspect them through adverse bindings, fractions and coverage.
The authored later collection schedule is held fixed deliberately to reveal
cross-year dependence. This is not a fair empirical comparison of business
policies and cannot establish an optimal fraction or behavior.

Pre-mortem: a transformer may validate and produce a mathematically valid local
allocation while the full path fails. Execute the whole native path, inspect
its first refusal and preserve earlier valid years. The 9/10 control also
exposes accidental changes outside the target allocations.

## Work and artifact

Use a separate checker in company-state-relationship-dependencies-20261028;
read the existing policy module and source only. Save full transformed paths,
relationship traces, adverse controls, manifest and decision in policy-attempt-01.
Command: python3 -B data/accounting-master/company-state-relationship-dependencies-20261028/check_policy_connection.py --output data/accounting-master/company-state-relationship-dependencies-20261028/policy-attempt-01
Environment: existing Python/jsonschema; CPU-only rational operations, no GPU
imports. No seeds apply. No full-document build or historic writer runs.

Stop this bounded unit when the criteria pass and refresh the live master.
Then continue source-backed identities, other operation/sector dependencies and
the connected survey; the broad program remains open.
