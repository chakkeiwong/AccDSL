# Time contract v2 — proposed semantics

This contract addresses MC05 with MC04/MC25/MC27 interactions (G13/G17/G18).
It supplies the proposed answer to P15-E04. Its fixtures are specification
examples, not a runtime implementation. The existing P06 chronology selector
is a counterexample where it substitutes availability for absent ingestion and
allows unverified historical bytes by default. Neither behaviour is adopted
for a claim requiring the missing evidence.

## T1. Records and query dimensions

An assertion version identifies economic instant or event dates, reporting
interval and calendar, public availability evidence, ingestion event, review
events, source byte hash and evidence of byte vintage. These are different
clocks. A payment date does not establish recognition time; reporting period
end does not establish publication. A later acquisition may preserve bytes
known to have been public earlier without establishing system possession then.

Economic and reporting periods use ISO calendar dates and explicit calendar
versions; flow intervals are [start, end_exclusive). Timestamp comparisons use
timezone-aware instants converted to UTC. Preserve the original timezone,
precision and source representation. Missing timezone rejects an instant
comparison (`MISSING_TIMEZONE`); it never means the machine's local zone.
Absent ingestion and explicit-null ingestion are separate diagnostic states,
`INGESTION_ABSENT` and `INGESTION_UNKNOWN`, but neither establishes an instant.

A query specifies `admission_mode`, `selection`, economic/reporting target,
information cutoff when applicable, system-as-of when applicable, review
snapshot, requested layer, and calendar/perimeter/measurement basis. Selection
is `original`, `latest_available`, or `harmonised`. No selection overrides
admission. Omitted required cutoffs or a nonexistent review snapshot reject the
request, rather than silently choosing today's data. Outputs contain selected
IDs, known exclusions/reasons, unresolved candidates/dependencies, derivation
lineage, assumptions, and claim status. Historical simulation receives only
admitted evidence; diagnostic knowledge of later rejected IDs belongs in the
audit output and must not become scenario input.

## T2. Three admission modes

`archival_exploration` allows inspection of retained bytes, including unknown
publication or ingestion. Such rows are labelled `historical_admissibility:
unestablished`. With a cutoff and unknown publication they may be displayed only
as unresolved archival candidates, not as cutoff-qualified selections. Without
a cutoff all retained rows may be selected under explicit lineage rules, but
the result remains archival; no historical knowledge claim follows. Source
integrity checks still apply. Exploration does not authorise accounting posting.

`investor_information` requires information cutoff K, supported public
availability at or before K, and evidence linking the exact selected source
bytes to that availability. Later ingestion is permitted. Unknown publication,
unverified historical bytes or date precision straddling K leaves a candidate
unresolved and excludes it from the admitted set. Known publication after K
is a definite exclusion. An accepted extraction performed later may read an
eligible old document using an explicitly chosen review snapshot. Any derived
interpretation that consumes later information is inadmissible for a historical
decision rule; its full information dependencies must pass K separately.
This view establishes public availability of evidence, not actual investor
awareness or a tradeable execution opportunity.

`system_as_of` requires S and an immutable receipt proving exact bytes were
ingested no later than S. Ingestion cannot be inferred from publication. The
requested accepted layer additionally needs review decisions visible by S;
later review cannot be projected back. Retained raw evidence may be returned
with its then-unreviewed status if the requested layer is raw. System possession
alone does not establish public availability. If a query also requests an
investor cutoff K, it must satisfy both filters, including public byte-vintage
evidence. Unknown publication alone need not block a *pure* system-possession
query. This separation permits later legitimate private/local records without
claiming that they were public.

A known later revision is excluded by its actual time; it does not suppress
an earlier eligible assertion. An unresolved potentially relevant version
keeps a result unresolved even if an older candidate is selected. Unaffected
keys retain supported results. `unresolved` is different from an empty set
proved to contain no eligible records.

## T3. Date-only evidence and byte verification

A publication date D with named timezone Z denotes an interval from local
midnight D through (but excluding) the next local midnight. The physical
instant is unknown within it. If K is before the interval, exclude the record;
if K is inside, return `PUBLICATION_PRECISION_UNRESOLVED`; if K is at or after
the interval's exclusive upper boundary, admission is supported by that date
evidence. This is a conservative availability convention, not a claim that
publication occurred at midnight. No fixed 24-hour duration is assumed across
daylight-saving changes. Missing Z keeps the interval unresolved. Conflicting
publication sources remain alternatives until resolved; choose neither the
earliest nor latest silently.

An ingestion date without an instant similarly proves only bounded possession;
queries inside the date remain unresolved. Review date precision is treated
the same way. A receipt must bind timestamp evidence, source ID and byte hash;
`ingested_at` alone without a receipt is `INGESTION_RECEIPT_UNVERIFIED`.
Public byte-vintage evidence and system receipt evidence are different proofs.
Current byte integrity failure is a hard rejection (`SOURCE_HASH_MISMATCH`),
whereas missing historical linkage is unresolved. An issuer timestamp on a
current webpage cannot by itself prove unchanged historical bytes.

## T4. Selection, supersession and review state

Supersession edges identify assertion IDs and the exact concept, period,
perimeter and dimensions replaced, plus supporting evidence. The graph must be
acyclic and targets must exist; a cycle or missing target rejects the affected
lineage. A document-wide replacement is not inferred from one corrected fact.
Duplicated content with no assertion change remains an alias with its original
lineage. Distinct same-date records need a supported ordering or a retained
conflict; IDs and filesystem order never break a semantic tie.

`original` returns eligible root assertions for each requested key. A later
revision is not an original merely because its root is unavailable. Multiple
unrelated roots remain competing assertions. `latest_available` returns eligible
assertions with no eligible admitted descendant superseding them for that key.
Only the eligible graph may remove an older record; future review acceptance
or later ingestion has no backward effect. If an eligible descendant's
intermediate ancestor is known but ineligible, the supported transitive edge
can still establish replacement; missing graph evidence cannot. Multiple live
leaves for the same exact quantity produce `CONFLICTING_VERSIONS` and remain
visible, rather than being averaged.

`harmonised` starts from latest eligible records and applies explicit admitted
transforms to a declared target basis, calendar and perimeter. Each transform
states input IDs, formula, authority/assumption support, review snapshot and
information dependencies. The output is a derived reading with a new ID;
original rows and their labels are preserved. Transform availability must pass
the same admission rules as other dependencies. Missing authority or a missing
opening bridge returns `HARMONISATION_UNSUPPORTED`; it does not relabel an old
number as comparable. An algebraic synthetic transform tests lineage only.

## T5. Period arithmetic and change treatments

Subtract YTD A from longer YTD B only when concept, unit, currency, measurement
basis, perimeter, calendar, interval start, aggregation dimensions and evidence
revision compatibility match. The shorter interval must be a proper prefix.
The remainder is [A.end_exclusive, B.end_exclusive). Same vintage labels are
not sufficient if other context differs. Different vintage labels require a
specific admitted compatibility bridge covering the fact, not general claims
that both reports are audited. Original selection may return H1-v1 and FY-v2
for display while arithmetic between them is rejected.

The synthetic retained example is H1-v1 = 120, revised H1-v2 = 110, FY-v2 = 260.
Compatible subtraction gives H2-v2 = 260 - 110 = 150. Subtracting 120 gives
140 arithmetically but fails the compatibility contract, so the financial query
returns no H2 value. A 52/53-week calendar change or a changed group perimeter
also requires an explicit bridge; endpoints alone cannot establish comparability.

An extraction correction changes the reading of unchanged source bytes; issuer
revision changes the reported assertion; an estimate update changes prospective
model inputs; a policy/error correction may require retrospective treatment.
The time contract requires change kind, authority/rule version, effective date,
affected periods/accounts, opening-balance bridge, transition method and review
evidence. It does not determine the standards-specific classification. Missing
authority returns `TREATMENT_UNSUPPORTED` and preserves original/revised views.
No fixture here certifies IFRS, US GAAP or ASBE retrospective/prospective rules;
P17 must supply the supporting methods and authoritative cases.

## T6. Alternatives, invariants and interactions

Permissive fallback makes archival data easier to query but cannot establish
system history: two systems can ingest the same public filing on different
days. Strict receipt-based system admission and separately qualified exploration
are therefore proposed. Treating all missing publication data as fatal to every
operation would wrongly prevent a supported system-possession query. Combining
admission and revision selection in one “latest” switch hides these differences.
The proposed orthogonal fields make the requested historical claim explicit.

For date-only publication, start-of-day admission is convenient but admits
possible future information during that day. End-of-interval admission is
conservative and preserves the unknown instant. An arbitrary noon default is
unjustified. Exact research backtests requiring intraday availability must obtain
better evidence or leave those observations unresolved.

For every selection, selected and definitely excluded IDs are disjoint; selected
IDs can coexist with unresolved competitors, in which case the affected claim
is unresolved. Hashes and old views are immutable; a correction invalidates
current dependent results without rewriting historical records. Increasing K
may legitimately change latest selected values, so value monotonicity is not
an invariant. Eligibility grows only if the evidence/review snapshot and other
filters stay fixed. No view claims the issuer's assertions are economically true.

Evidence supplies immutable versions and layer decisions; history/uncertainty
must retain live alternatives; accounting supplies transition authority and
opening bridges; language/IR must serialize cutoffs, intervals and required
contexts; persistence supplies receipts, immutable snapshots and transitive
invalidation; interfaces expose unavailable versus unresolved versus unsupported
outcomes. Full definitions of those interfaces, identity/replay and domain
treatment remain later contracts. Human acceptance remains pending.

## Revision record and fixture conventions

The current examples are `time-fixtures-v2.json`; v1 remains preserved.
The harmonisation example previously expected a conditional result despite an
empty request assumption list. That is wrong relative to E2's explicit-selection
rule. v2 selects `bridge-assumed`, records accepted synthetic review and byte
support for the transform, and names its information dependency. A transform
with an unselected required assumption must remain unresolved, with no admitted
derived value. An assumption ID is selected only by its presence in the request's
`assumptions` list; merely appearing in the transform does not select it.

Both harmonisation examples now use the documented `record_subset` operation.
Their restricted universe contains only h1-original; they illustrate a derived
reading of that source, not selection from a complete restatement history.
The all-record investor example still selects h1-restated and fy. Base review
acceptance assumes no later information dependencies beyond the stated bytes
and context. These explicit synthetic premises supply no historical-publication,
accounting-authority or issuer-restatement evidence.
