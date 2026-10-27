# Explicit current-assessment timing

25 October 2026. MC13, MC15, MC16, MC24, MC28, MC32, MC35.
The recovered recorder completed successfully: 12 focused tests and 49
regressions (61 total), eight complete exchanges and 341 pinned input files.
Read-only replay passed for all eight exchanges and the pinned inputs/outputs.
The command, environment, duration and unchanged git base are in manifest.json.

MixedEventTimeline/2 adds an optional current-assessment operation to the
unchanged native annual book and decision scheduler. Its schedule date equals
interval.activity_through, which is one day before end_exclusive. It does not
invent event.date, assess against the initial book or alter tax rules.

## Checked consequence

The constructed book opens with cash 452, inventory 80 and carried tax payable
41/4. A one-unit sale for 15 with cost 10 precedes a same-day assessment.
Under explicitly authored zero adjustments and a 1/4 rate, taxable profit is
5, current tax is 5/4 and total payable is 23/2. Cash is 467 and inventory 70.
The assessment itself has no cash flow. Historical vintages remain unchanged.

Assessment first measures zero profit and seals that interval. The later
same-day sale stops with event_inside_assessed_interval; cash stays 452 and
the successful assessment prefix survives. This is the expected order
discriminator, not a failed research direction. The comparator preserves the
complete materialized decision, native transition and financial report.

A next-day half-unit sale produces cumulative profit 15/2, current tax 15/8,
cash 949/2 and inventory 65. Replacement posts only the incremental tax 5/8
and updates the same current vintage. Missing/unknown rate and a false model
selection preserve the successful sale prefix with their native statuses.
Malformed clocks, invented date aliases, stale initial state, duplicate IDs
and tied priorities refuse. Actual 32-native/64-total boundaries are tested.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Retain optional timeline successor | Full native/manual comparison and exact arithmetic pass | No lost prefix, altered inputs or clock alias; expected reverse-order refusal retained | Supplied tax findings are hypothetical | Integrate bounded result; audit deferred measurement and carry clocks | Tax-law validity, issuer admission, full fiscal completion or production readiness |

## Assumptions and interpretation

The inherited annual book, scheduler and authoring validator are pinned
comparators, not external accounting authorities. Their supplied rate and
policy findings are hypotheses for this synthetic case. Zero adjustments make
the tax result depend on actual-turn profit rather than an authored fixed
target. The 32/64 work limits are inherited reference limits; boundary tests do
not establish capacity. Exact deterministic tests support no stochastic
ranking. Deferred assessment, provisional carry and nested envelopes remain
outside this timeline version; their native kernels already exist.

Post-run red team: shared native code could make two paths agree on the same
accounting error. Independent cash, inventory, profit, expense, payable and
replacement arithmetic address the stated composition question but do not
validate the supplied tax model. A discrepancy in complete native transitions,
mutated inputs, silently refreshed evidence or inconsistent clocks would
invalidate this composition. No such discrepancy is observed in the retained
cases. Wider event combinations and fiscal boundaries require separate work.
