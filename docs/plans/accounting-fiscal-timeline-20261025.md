# Deferred measurement and fiscal boundary in a mixed timeline

25 October 2026. MC13, MC15, MC16, MC24, MC28, MC32, MC35.
Baseline: accepted MixedEventTimeline/2, native AnnualProgram/1 and its existing
current/deferred assessment, vintage settlement and provisional-carry kernels.
The timeline composes these operations; it changes no accounting formula.

## Skeptical audit and research intent

Question: can one explicitly ordered timeline preserve a state-bound deferred
measurement and close a fiscal period without silently renewing evidence or
executing later actions under the wrong period? The native code already
supports both operations. The missing part is scheduling composition.

The main failure mode is treating every event as directly dated, regenerating
measurement.state_sha256 after earlier activity, or allowing a carry to make
the remaining calendar silently change periods. Deferred assessment instead
uses measurement.at and checks its original digest at its actual turn. Carry
uses next_period.start as its boundary date, requires contiguous periods and
is terminal. Subsequent activity uses a separate timeline bound to the new
book. The carry's resulting date and the timeline cursor must agree. A no-action
decision may advance the calendar cursor without financial movement; it cannot
renew measurement evidence.

Primary pass criterion: complete states, journals, reports, histories, vintage
allocations and actual-turn decision requests agree with manual native
interleaving. Independent profit/current/deferred tax and retained-earnings
arithmetic checks the consequential amounts. A supplied stale digest must
refuse while preserving the valid prefix. Missing deferred findings stay
unresolved; false deferred findings retain native refusal. Provisional carry
already retains its finding statuses (including unknown/false) without granting
admission; preserve that distinction rather than imposing a new rule.
Carry without fresh assessments must
refuse. Structurally malformed later entries must prevent all execution.

Promotion vetoes: input mutation, lost native result, refreshed measurement
digest, hidden date conversion, changed accounting or lost archive. A harness
or comparator defect is a continuation veto until repaired. Expected stale
measurement and incomplete-assessment refusals instead trigger the planned
explicit-new-evidence comparison. They do not reject the whole direction.
Test counts, runtime and build success are explanatory only. No statistical
ranking, real-company admission or fiscal completeness follows.

## Defaults and assumptions

| Choice | Provenance / justification | Failure risk | Early check | Status |
|---|---|---|---|---|
| Native annual kernels | Existing pinned code and complete reference cases | Shared accounting defect | Independent arithmetic and exact native transitions | Comparator |
| Deferred date from measurement.at | Native equality with financial date | Using stale pre-event state | Earlier payment changes digest; original request must fail | Reviewed clock mapping |
| Carry date from next_period.start | Native contiguous-period boundary | Running next-period events under old calendar | Terminal carry, new root for later events | Explicit bounded design choice |
| Terminal single carry | Avoid inventing multi-period calendar semantics | Narrower than a general fiscal scheduler | Reject later actions and duplicate carries | Optional scope, not product limit |
| Synthetic bases/rate/capacity | Retained authored fixture, not issuer facts | Mistaking supplied findings for authority | Preserve original provenance and negative flags | Hypothesis |
| 32 native / 64 total actions | Inherited reference budget | Misread as performance claim | Actual mixed bound plus overflow | Reference limit |

## Execution

1. Add optional MixedEventTimeline/3, pinning version 2 and reusing its
   validation/scheduler and native annual execution. Statically validate all
   deferred/carry shapes without applying them. Carry is unique, at the initial
   period's exclusive end, and last; all other dates remain within that book.
2. Record current -> deferred -> carry, stale deferred after payment, explicitly
   reauthored deferred after payment, missing evidence, early/missing assessment,
   malformed clocks, duplicate/tied entries and boundary limits. Compare every
   successful transition with complete native execution. Continue one new
   period under a separately bound request and verify archives/vintages.
3. Preserve exchanges, hashes, tests, command/environment and result table in
   data/accounting-master/fiscal-timeline-20261025/. Use CPU-only Python, no
   installations. Run focused unittest suite then direct scheduler/annual
   regressions. Freeze evidence only after checks pass.
4. Integrate a separate manuscript successor with bounded rendered review and
   preserve all 53/6/46 obligation records. Reassess the remaining simulator
   dependencies against actual code before selecting further work; do not
   repeat completed tax kernels, recovery, populations or source history.

Nonclaims: full fiscal event population, deferred-tax law validity, real
opening facts, complete language design, forecast quality or product release.
No commits, agents, installations, GPU, paid review, outreach or background work.

Early diagnostic: the inherited deferred example reproduces existing DTA/DTL
and gives a zero journal. That is insufficient alone to test a consequential
carry. Use an expressly authored recovery capacity/recognized deduction of 12
instead of 20 on the existing debt item: at rate 1/4 DTA becomes 3 instead of
5, DTL stays 5, and deferred expense is 2. This is a synthetic discriminator,
not estimated recovery or a new default. The sale's after-tax profit should
then be 5 - 5/4 - 2 = 7/4, with an equal retained-earnings transfer at carry.

First focused run: 12 of 13 tests passed. The continuation expected a full-unit
sale, but the inspected stock policy retains an explicitly supplied 1/2-unit
reserve. With one unit left, only 1/2 is sold: proceeds 15/2, cost 5, cash
949/2 and inventory 65. Correct the test's wrong baseline, preserve the rule
and reserve, and assert the generated sold quantity. This was an expectation
error, not a runtime failure or a reason to weaken the comparison.
