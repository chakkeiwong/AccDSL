# Insurance composition audit — inspected baseline

27 October 2026. Plan: accounting-insurance-shared-group-audit-20261027.md.
MC03/05/11/13/15/17/18/19/20/24/25/26/28/33/34/35.

The plan survives initial inspection with a concrete boundary. The current
fiscal statement adapter calls declared_indirect_cash_v2 over retained
InsuranceFiscalBook results. That compiler calls insurance_loss_book_v1, whose
CASES tuple admits only loss-service-finance and zero-loss-boundary. These are
issued loss-allocation schedules. They do not establish fiscal composition for
the separate issued/held recovery_change operation.

InsuranceOrigins/1 already has recovery_change with source-qualified fixed quota,
zero rates and no other changes. It computes issued and held measurements,
loss recovery and final cash separately. The 2025/2026 identity-policy successor
adapts InsuranceComponents/1 transaction identities; its complete exchange tests
do not by themselves wire InsuranceOrigins/1 into fiscal reports.

The smallest diagnostic will call the existing nominal native calculator on its
retained recovery-change inputs and compare the independently authored results;
it will also invoke the actual loss-book selection endpoint with those IDs to
confirm the limitation. A separate immutable check of the 24 fiscal statement
records confirms their real two-case population. The 2026 identity evidence is
preserved as protocol evidence only. No new treaty term, mixed-origin termination
ordering, positive recovery, rate or source finding will be invented.
