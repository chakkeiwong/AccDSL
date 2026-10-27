# Pre-implementation audit — 24 October2026

MC05/11/13/16/24/26/28/35;G2/G4;S2–S5. Question: can fresh conditional deferred
recognition consume the exact reassessed following-period book without renewing
old recovery capacity or losing current-tax settlement history? Comparator:
full following-period reassessment plus its recorded carried DTA8/DTL10 and
archived prior recognition schedule. The old deferred caller's predecessor type
and statement opening are incompatible; projection would evaluate the wrong book.

The inspected old calculation reads basis declarations supplied before the
current-tax journal. That journal changes income_tax_payable. Those declarations
cannot silently serve as post-journal measurements. Resolve the gap with a fresh
measurement record containing exact state digest,date,jurisdiction/regime,complete
account bases and complete current lease-right bases. Known declarations with
provenance are required for every value. Unchanged bases may be explicitly
redeclared; nothing is copied automatically. Item bases reconcile to these fresh
totals and retained lot bases. No tax treatment for accrued tax is inferred.

Retain existing single-pool gross profit/loss equations under an explicitly
selected hypothetical model. Implement a compatible full-result caller and
scoped pure population/calculation functions; do not fake the old result schema.
Historical capacity remains only in the predecessor. New capacity and support
must be supplied. Old item allocations must sum to actual carried balances.

| Choice | Provenance and justification | Failure mode | Early diagnostic | Status |
| --- | --- | --- | --- | --- |
| Fresh post-journal bases | Identified timing mismatch | False difference from stale payable base | Wrong-state/date rejection and independent payable reconciliation | Reviewed scoped repair |
| Single recovery pool | Existing declared hypothetical model | Double-counted capacity across debt/loss | Competing debt and loss deductions | Baseline model,not legal default |
| Positive carrying and base amounts | Existing closed population | Hidden contra accounts or negative bases | Explicit refusal and complete population check | Representation limit |
| Profit/loss-only movement | Existing explicit route | Missing OCI/equity effects | Unsupported route controls | Optional scoped model |
| Full-state original-opening statements | Following-period contract | Wrong retained/cash bridge | Four exact ties after DTA/DTL change | Reviewed engineering requirement |

Primary criteria: independent desired-minus-recorded arithmetic,complete current
population and fresh measurement,shared capacity,recorded allocation,exact tax
vintages/cash/loss state,source binding,four statement ties and complete apply.
Broken hashes,missing measurement/support,wrong oracles or failed conservation
veto recording and trigger repair. Candidate refusals do not veto the broader
repair direction. Counts/runtime are explanatory. No law,company recovery forecast,
annual readiness or whole-company completeness is established. Preserve tests,
requests/results,manifest,replay and exact commands here. No GPU or stochastic run.
