# Connected insurance groups: one owner, separate measurements

14 October 2026. Optional authored-synthetic posting profile for the existing
accounting.commit@1 operation. The common request/result and commit-argument
fields, P2 business-event key and historical replay order are unchanged.
This specification uses the checked A/B/R example, not real insurer permission.

## Scope and state

The owner is Insurer/Pretax/connected-2024: one entity, one book and one branch.
Its opening has cash 250, issued remaining-coverage liabilities A=120 and B=130,
held remaining-coverage asset R=85 and equity 85. Component values are separate
economic memory: A has claim PV 80, RA 10, CSM 30; B has PV 120, RA 10, CSM 0
and loss component 30; R has PV 60, RA 5, cost CSM 20 and loss-recovery
component 15. Loss components are already within the coverage amounts.
Neither is an additional asset/liability account.

The source calculation is the Version 2.83 timely treaty path. Its retained
AASB 17 December 2022 compilation and historical Australian private-sector
calendar 2024–2025 scope continue to apply. Rates, RA, complete 50% cover,
collectability and equal coverage units remain supplied synthetic assumptions.
No current real-company accounting authorization or actuarial calibration is
created by this profile. Uncertainty/model admission remains a separate step.

Group records preserve group ID, issued/held role, portfolio, issue year,
profitability, covered-group relation, PV, RA, CSM, loss component, incurred
balance and remaining coverage units. Company state preserves context, branch,
chart, sequence and event phase, all signed account balances and all group
records. Debits are positive and credits negative. One equity-opening account
and the explicit profit/expense accounts close the trial balance; computed
equity equals opening equity minus the signed sum of profit/expense accounts.
Coverage amounts equal PV+RA+CSM, never that sum plus a loss component.

## Four dated events, with intermediate states retained

The authored year-end sequence is finance → service → incurrence → settlement.
Each phase has a distinct business_event_id and names required groups A/B/R.
Each group is measured independently, but the declared event depends on the
complete set because R's component tracks B. This does not require every event
in every insurer to update all its groups. A future profile can declare another
dependency-closed event set. This one supports exactly these three groups.

Finance increases A's PV by 8 and CSM by 3, B's PV by 12, and R's PV by 6 and
CSM by 2. B's loss component gains (3/13)*12=36/13 and R's gains half that,
18/13. Journals debit A/B finance expense 11/12, credit their liabilities,
debit R's asset 8 and credit finance income 8. Coverage becomes 131/142/93;
cash stays 250 and equity becomes 70. Component changes alone add no journal.

Service releases A's claim PV 44, RA 5 and CSM 16.5: debit A liability 65.5,
credit revenue 65.5. B releases PV 66 and RA 5: debit liability 71, credit
revenue 710/13 and loss reversal 213/13. R releases PV 33, RA 2.5 and CSM 11:
credit its asset 46.5, debit premium allocation 498/13 and loss-recovery
reversal 213/26. B/R loss components close at 213/13 and 213/26. Remaining
coverage units become one. Cash is still 250 and equity is 160 before claims.

Incurrence debits issued claims expense 110 and credits A/B incurred-claims
liabilities 44/66. It debits R's incurred-recovery asset 33 and credits recovery
income 33. Cash remains 250, while equity is now 83. Settlement debits the
incurred liabilities, credits cash 110, debits cash 33 and credits the recovery
asset. Cash becomes 173 and all incurred balances return to zero. Coverage
65.5/71/46.5 and equity 83 agree with the existing full year-one calculation.

The schema lock specifies the finite profile's account map, exact rational
numeric representation, allowed phases and group record bodies. Each
GroupMeasurement names its group, phase, input/output state, context, branch,
view, method, source and complete/unresolved status. A complete measurement
must reproduce the declared phase calculation. Unknown output is null with a
specific reason; zero is a measured value. The dated event names every group
measurement and required group ID. Mixed views, methods, books, duplicate or
missing groups fail before receipt lookup.

## Authorization and publication

AccountingEventBasis retains the immutable opening, event, assumptions,
historical source, admissions, method and view. PostingAuthorization binds that
basis to the declared synthetic profile. Every required group must have a
complete eligible measurement. An unresolved R measurement makes permission
false for the entire event. A/B's completed diagnostic candidates remain
inspectable outside committed domains. They cannot become a partial closing
company state or a completed book outcome.

JournalProposal contains the ordered debit/credit lines, identified by group,
and EconomicDelta contains the complete before/after group states and all
account changes. Both bind the same basis and authorization. The store checks
independent group/component calculations, balanced lines, signed account deltas
and complete closing company state. A balanced extra entry that counts a loss
component twice fails. Schema correctness or numerical balance alone cannot
authorize the entry.

Commit arguments remain exactly basis_ref, authorization_ref, journal_ref and
delta_ref. expected_head appears only in the common envelope. It names this
owner, the exact opening state and original generation. Validated input must
have complete binding/admission/authorization before any receipt lookup.
Candidate reconciliation occurs for an absent-key fresh request; its failure
retains request_ref while publishing no state, journal, delta or receipt.
Input rejection retains the exact Submission and has null validated request
and coverage. An optional audit candidate links the submission and retained
diagnostic measurements; it is not an accounting receipt.

P2 publication atomically inserts the journal, delta, closing state, dependency
edges and immutable receipt and advances the owner head. It rechecks key and
head inside that transaction. A required group's failure leaves all committed
domains unchanged. This is an observable requirement, not tested storage code.
Cross-book or cross-entity events are unsupported by this profile; it supplies
no distributed atomicity promise.

Each documentary storage world lists retained committed states and the complete
published record/dependency closure, including explicit directed edges. The
global exchange registry also holds uncommitted proposals; its mere possession
of a record is never evidence that the record was published in a book.
Wrong branch bindings and incorrect completed group calculations reject before
lookup, just as wrong book/view/method bindings do.

## Replay, interference and lost acknowledgement

Lookup uses (entity_id, book_id, branch_key, business_event_id). The complete
portable request fingerprint includes all request bytes, request_id, budget,
expected head and dependencies. After input validation, equal fingerprint
returns the original immutable receipt before today's head freshness check.
After all four phases, replaying the finance request still returns its finance
receipt and original closing generation 1, while reporting the observed current
head at generation 4. additional_commit is false and this invocation's outer
commit_observation is not_committed.

Different bytes for an existing business key yield EVENT_ID_CONFLICT. A new
event key with an old expected head yields STALE_OPENING_STATE. A concurrent
identical commit discovered at final recheck returns the original receipt;
different bytes conflict; another event advancing the head makes this event
stale. Invalid historical bindings or false permission reject before lookup,
even if that business key has a stored receipt. Historical replay does not
reassess an unchanged valid request against today's source rules.

Client timeout records commit_observation=unknown and the exact retained
submission/request. It conveys no receipt and no claim of noncommit. The
documentary trace preserves two possible worlds: old head/no receipt, or the
complete new head/original receipt. After recovery the same request commits in
the first world and replays in the second. A timeout itself creates no new
request, event ID, expected head or economic fact. The fixture represents this
as a TransportObservation, not a fabricated received OperationResult.

The coverage domain of a returned validated operation is its singleton request
decision, not a distribution of financial histories. All financial uncertainty
and unresolved-group obligations remain separately identified. No statistical
ranking, financial probability mass or production readiness follows from the
finite examples. Runtime fault injection, actual persistence and independent
accounting/human acceptance remain later obligations.
