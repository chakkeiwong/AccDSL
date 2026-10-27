# All native operation kinds have an explicit dependency inventory

28 October 2026. T01/C04; MC08/09/13/18/19/28/33/35.
Plan: docs/plans/company-state-native-operation-coverage-20261028.md.

Attempt-02 passes45 checks. The source-reviewed inventory covers all14 kinds
in CompanyOperationsDraft/1, including input/state reads, guard conditions,
account effects, memory/report effects and unsupported real-world premises.
The full baseline actually executes every kind. Opening validation, annual
ordering, intermediate controls, reporting and lifetime carry are listed
separately from operation-specific dependencies.

Ten additional controls preserve ineligible/headroom facility refusals, cash
shortage in payroll/dividends/debt interest/facility interest, unsupported loan
fees, invalid or unknown tax rates and non-final closing. Full native results
are retained. The first attempt's facility-rate100 control did not cause cash
shortage because the loan lasts only two days. The native result was correct;
the expectation was wrong. The repaired extreme rate1000 probe exceeds cash
and is refused. Both attempts and the exact arithmetic repair remain.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain14-kind dependency inventory | Exact schema population and inspected branch meanings agree | Declared controls pass after corrected expectation | Registry is source-reviewed, not automatic extraction | Integrate into one bounded common construction contract and review reader/implementer obligations | Exhaustive conformance of all guards |
| Keep original method boundaries | Full native result and unresolved scope retained | No accounting/source admission | Other sectors, legal obligations and richer policies | Assign implementations to T05 and sources to T03/C01 | Universal company simulator or standards compliance |
| Repair task sequencing | Original criteria/edges/statuses unchanged | No requirement relaxed | Common contract still needs coherent review | Finish T01 definition independently of downstream sector implementation | T01 or release completion |

Check counts describe deterministic engineering evidence. The inventory's
dependency claims come from inspected source, not the existence of fourteen
rows. Not every guard is independently exercised in this continuation. Legal
distributability, actual payment authority, title, counterparties and source
availability remain outside these synthetic profiles.

Post-run review: hand-curated dependencies can omit a source branch. The exact
native kind check prevents missing kinds but cannot prove complete field-level
coverage. A later source change or missed read requires a new review and
manifest. No stochastic ranking, new default or release acceptance follows.
