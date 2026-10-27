# GroupForeignOperation/1: dated books, group state and replay

15 October2026. R03-D. This finite extension uses the common I1 request/result
fields and L1 content references. It registers group-specific closed bodies
and argument unions; it does not modify CorporateJointHistory/1. The required
schema, method, retained source case and source manifest are exact blobs in
the companion packet. No runtime endpoint or financial posting is executed.

## Entities, time and scope

Parent-P has USD functional currency and Subsidiary-S has EUR functional
currency. Their display names are not identifiers. A separate consolidated
reporting entity Group-P owns the group book; it is not a legal entity.
The authored relative calendar has ordered A-pre,A,O,R,D instants, with R
immediately before D. It conveys no actual public-information dates. Use is
archival synthetic illustration; a historical-investor request is unsupported
without a dated information-availability record.

EntityBook pins entity, legal-book identity, exact relative instant, currency,
signed balances and source case. Parent's acquisition investment and cash
movement remain in its own book. Subsidiary's inventory sale and payable
payment remain in EUR. Group adjustments reference those inputs and mutate
only Group-P/Consolidated/branch. The legal books are never rewritten to
record translation or elimination.

ControlAssessment pins investor, investee, event interval, rights/returns/
power findings and supporting assumptions. This example conditionally admits
the2.81 facts; it neither estimates control from share percentage nor applies
the sources to an actual issuer. PerimeterVersion pins the assessment,
functional/presentation currencies, ownership class/fractions, measurement
policy and source books. A GroupState retains a dated perimeter and rates,
signed USD balances, cumulative profit/OCI by owner/NCI and cash movements.
Zero closing NCI does not delete its earlier income attribution.

Rate specifies base EUR, quote USD, USD per EUR, a relative instant and exact
rational value. A label containing1.30 cannot substitute for currency direction
and time. The supported profile requires exact matching A/O/R rates, aligned
book dates and the selected legal entities. Missing/unknown control or rate
keeps dependent computation unresolved; a supplied incompatible record rejects
the affected use. No nearest-date join is implemented.

## Economic transitions

The protected2.81 history supplies A acquisition, O translation before
operating entries, R closing translation/attribution, and two alternative D
loss-of-control events. The packet retains its original journal rows as
ordered atomic groups. Full sale and retained20% have separate branch owners
forked from the same immutable R state, with explicit fork provenance.
They are never composed as sequential disposals.

Acquisition includes all subsidiary cash24, although parent consideration is
115.2. Loss of control removes all subsidiary cash156, although the parent
receives169 or126.75. Group net investing cash13 or−29.25 is therefore not the
parent's sale receipt. The retained investment42.25 is noncash. The group
gain33.8 includes parent reserve10.4; NCI reserve2.2 leaves within NCI31.2.
Report records preserve profit58.8, parent profit53.8, NCI profit5, OCI2.2,
NCI introduction24 and removal31.2 alongside ending equity353.8.

An AccountingEventBasis pins group identity, branch/event, opening state,
target perimeter, exact legal-book/settlement read set, rates, method,
historical source anchors, assumptions and information view.
PostingAuthorization is authored synthetic permission for that exact basis;
it conveys no real authority. JournalProposal contains ordered signed USD
entries; EconomicDelta independently states the resulting state and
performance/cash changes. A balanced journal with wrong subsidiary cash,
reserve ownership or retained-cash classification fails before publication.

The read set can contain immutable entity books from before an event and a
separate settlement fact. In particular the retained-interest disposal does
not invent a subsequent parent-only accounting policy for the retained asset.
Its group method still has sufficient admitted consideration and fair value.
Partial-transfer, different-rights, tax, impairment, hyperinflation and actual
exchangeability methods remain outside this finite extension.

## Common transaction and reporting behavior

accounting.commit@1 takes basis, authorization, journal and delta Refs.
The single envelope expected_head names the group owner, opening Ref and
generation. Validate the profile/signature/tag, complete reference closure,
view, selected source identities, temporal/currency compatibility, authorization
and financial consequences before business-event lookup. Business identity
is entity/book/branch/event. The complete request fingerprint includes
request_id, budget and expected_head.

An exact previously committed request returns the original receipt with no
new effect before checking current-head freshness. Different bytes for the
same event conflict. A new event requires the exact expected current head.
Successful publication atomically includes dependency closure, journal, delta,
closing state, receipt, event lookup and head. Every other owner and every
entity-book record stays unchanged. A candidate in the fixture registry is
not necessarily published in any store world.

Lost acknowledgement is a TransportObservation with unknown commit outcome.
Two complete worlds accompany the same exact submission: one before and one
after publication. Resubmission commits in the former and replays in the
latter. Partial publication is invalid, never a third successful outcome.

report.build@1 is read-only. It pins GroupState, map, view and requested
interval. The state has already retained the interval movements, so closing
balances alone cannot reconstruct them. A report combines only one branch,
perimeter and selected dependency view. A source correction creates a new
view and invalidates dependent current use. Frozen explanation/reporting under
the old view remains available. Rebuilding a current group history requires
new proposals and explicit corrections, never mutation of old records.

Exact submission bytes precede input validation. Invalid binding keeps the
validated request_ref and payload null. A valid request with missing admitted
control/rate returns an unresolved obligation without creating monetary zero.
Coverage names the singleton request decision; it does not claim an exhaustive
economic history family. Capability remains specified_only_no_runtime and
human acceptance pending in every result.
