# Pre-implementation audit — 24 October 2026

MC05/11/13/16/24/26/28/35;G2/G4;S2–S5. The engineering question is whether a
replacement cumulative assessment can follow allocated payments while retaining
actual state, loss history and both liability vintages. The exact comparator is
the frozen tax-vintage continuation and original carried opening. The old
same-period expense-minus-total-payments identity is wrong here. Reuse only its
checked pure declaration/reconciliation/loss-transition helpers.

The active plan passes with these explicit scoped choices: support one replacement
of the first current-period assessment, keep its current-vintage id stable, retain
all existing settlements unchanged, and attach the previous complete vintage and
loss-state hashes in supersession history. Changing assessment provenance never
changes the liability identity referenced by earlier payments. Repeated replacement
and subsequent continuation require a separate compatible consumer. An equal
endpoint is permitted for corrected declarations only when all events are covered;
a later endpoint is required when events follow the old assessment.

| Choice | Provenance/justification | Failure mode | Early diagnostic | Status |
| --- | --- | --- | --- | --- |
| Original carried loss inventory | Existing cumulative helper; avoids double use | Using provisional remaining losses understates deduction | Use19 twice as alternative assessments, not sequential consumption | Reviewed scoped default |
| Stable liability vintage id | Explicit payment references must survive | Renaming strands historic allocations | Compare payment records before/after exactly | Derived design |
| Same-endpoint correction allowed | Plan says nondecreasing endpoint | Uncovered later events accepted | Require through=end-1 and closing date<=through | Reviewed scoped choice |
| No credits/refunds | Existing positive-payable schema | Clamp negative current liability or net against old tax | New tax below current payments must refuse, even with positive old payable | Explicit representation limit |
| Pure inherited loss helper | Source-locked existing exact arithmetic | Misstated availability or history | Original opening validation and expiry/use controls | Baseline reuse |

Primary criteria: independently computed expense delta, old/current liability
separation, exact loss replacement, unchanged cash and settlements, full26-account
state, four carried-opening statement ties and full-result apply. Invalid hashes,
wrong oracles, absent declarations, broken conservation or date/scope mismatch veto
recording and trigger repair. Unsupported credits reject this candidate update;
they do not invalidate its predecessor or the broader repair direction. Counts,
smokes and runtime are explanatory only. No forecast, legal, statistical ranking,
annual readiness or complete-company inference. Preserve results, manifest,
source locks, tests and exact requests here. No long numerical experiment is run.
