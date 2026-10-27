# Native company-state construction contract, revision 1

28 October 2026. Bounded design and implementer reference for the existing
CompanyOperationPathDraft/1 family. This contract collects the supplied-state
construction responsibilities in one place. It does not replace the native
schemas, source admission or sector-specific contracts.

## Purpose and inputs

The construction request asks whether a supplied sequence of company operations
can execute from a specified opening, and what resources, claims, accounting
memory and history must remain available to explain that execution. It supplies
the complete native path, raw opening-source bytes and independently expected
canonical path digest. The source digest and opening-record digest within the
path are also checked by the native executor. These identities establish which
premises were used; they do not establish a real company's state.

The path contains one initial annual definition and its continuations. Entity,
book and currency belong to the opening context. Each period is a complete
calendar year, operations are ordered and timestamped, and monetary amounts are
canonical exact rational strings. The profile permits archival exogenous
stress inputs. A public or manager-information decision rule requires a
different admitted information contract; it cannot be obtained by renaming
this profile's information field.

Before execution, the modeler must distinguish the target from its evidence.
This contract evaluates one supplied conditional history. It returns neither
all histories compatible with a filing nor probabilities over them. Unknown
source coverage, missing counterparties and unsupported legal terms accompany
the supplied history; a successful run cannot resolve them.

## State categories and ownership

| Category | Native representation and responsibility | Meaning still required for actual use |
| --- | --- | --- |
| Economic resources and obligations | Cash, inventory units, supplied claims, fixed-asset cohorts, drawn facility amount and debt terms | Actual ownership, counterparties, instrument terms and complete population |
| Accounting memory | Account balances, cost convention, accumulated depreciation, claim recognition/settlement counters, retained earnings and tax convention | Applicable accounting basis and source-supported measurements |
| Persistent parameters | Unit cost, useful lives, coupon rates/shares, facility conditions, tax rate and declared method names | Provenance and admissibility of each modeling assumption |
| Actions and external inputs | Ordered purchases, deliveries, allocations, additions, payments and supplied amounts/dates | Which agent chose them and what that agent knew |
| Retained history | Complete journals, event prefixes, annual reports, claim lifetime memory and predecessor hashes | Coverage of additional historical queries and corrections |
| Information and analyst belief | Native archival_exogenous_stress declaration; no prior, likelihood or actor receipt is supplied | Separate justified information-time and inference definitions |

A financial quantity can have economic and accounting significance without
those meanings being identical. A receivable balance, for example, is linked
to named supplied claims; it is not evidence that the underlying rights are
enforceable. The distinction remains explicit in the inspected populations.
No interest accrual, cash payment or report line acquires a second posting
owner in the inspection layer. The native executor owns all financial effects.

## Construction and execution order

First compare the expected path digest with the supplied path. Then run the
unchanged native path executor against the supplied opening bytes. The native
schema, context, method, opening balance, claim totals, asset totals, date and
ordering rules decide whether that opening can execute. Unknown required
values remain unresolved with their exact native obligations. Invalid or
unsupported premises retain their different native classifications.

If no opening is executable, return the full native result and a null population
inspection. A null inspection denotes work not performed, not a zero balance
or an empty population. The guarded entrypoint is
data/accounting-master/company-state-population-admission-20261028/admission.py,
function inspect(path, source_bytes, expected_digest). The lower-level claim and
cohort inspectors require an executable opening and must not be used to bypass
that precondition.

For an executable opening, preserve the complete native chain. Inspect every
applied operation using its year-qualified event identity; local names repeat
across years. Trace claim creation and settlement relations, fixed-asset
additions and depreciation, and every intermediate population snapshot. The
trace must match native account effects and closing memory. Retain all other
native results, including refusal reasons and unexecuted operations.

A failed operation contributes no successful financial effect or relationship.
Earlier executed operations remain in the returned prefix. A later year whose
opening is unresolved cannot erase the prior complete year or supply a closing
state for subsequent years. Continuation requires a complete native predecessor,
consecutive periods, consistent facility identity and the declared carry rules.

## Operation dependencies and guards

The versioned inventory is
data/accounting-master/company-state-native-operation-coverage-20261028/attempt-02/inventory.json.
Its14 operation rows are checked against the exact native schema. Each row names
read inputs, guards, account effects, memory/report effects and unsupported
premises. The inventory is based on source inspection; it is not an automatic
static-analysis certificate or exhaustive independent execution of every guard.

Purchases and deliveries update inventory and create named trade claims.
Collections and supplier payments read each claim's ledger and remaining
amount; zero allocations retain those reads. Facility drawing depends on
eligibility and remaining headroom. Interest and repayment use the supplied
principal, rates, dates and drawn amount, and all cash outflows face the native
cash-availability check. Plant additions require new identities, positive
lives and supported service timing. Depreciation reads service eligibility
and remaining depreciable cost. Payroll and dividends use supplied amounts.
Tax reads the year's income and expenses under the declared immediate-tax
method. Closing transfers temporary accounts to retained earnings and creates
the annual report without discarding the retained journals.

Global checks are equally important. Every proposed journal balances. Inventory
cost/units, claim totals, fixed-asset cost/accumulation and cash prefixes remain
consistent after each applied event. The annual report reconciles cash, equity
and indirect operating cash flow. Those checks constrain admissibility even
when an individual final output cancels algebraically. An output-dependency
formula therefore cannot replace the complete feasibility conditions.

## Growing populations and historical queries

Claims and assets persist under stable identities. Purchases and deliveries
extend the claim population; additions extend the asset population. A claim
with zero outstanding amount is retained with its lifetime recognition and
settlement history. A fully depreciated or not-yet-served asset likewise remains
available. The annual adapter distinguishes the year's settlement counters
from lifetime claim memory.

The present historical-query contract returns the complete report for an
executed annual period, or a native unresolved/invalid result when that period
has not executed or is outside the path. Prefix snapshots are dated and are
not annual results. Other interval queries, disposals, merged/split instruments,
transfers and restatements require additional specified operations; retaining
raw history alone does not define their accounting meaning.

The deterministic sufficiency argument in
docs/design/research/company-state-inference-20261028/state-construction.md remains
task-relative. Two full states can share a reduced state only if they admit
the same actions, produce the same requested outputs/refusals and transition
to the same reduced successor for those actions. Induction then preserves
every finite permitted action sequence. Current examples reject particular
reductions: aggregate receivables hide claim allocations, and equal plant
carrying amounts hide future depreciation. These examples do not prove that
the retained state is minimal or sufficient for arbitrary industry operations.

## Typed requests for reports and histories

CompanyStateInspectionRequest/1 now supplies a closed audit request for this
single native owner. The request names the owner, canonical path digest, raw
source digest, entity/book/currency and explicit audit-only archival information
use. Its nonempty query list supports annual_report(period_start),
event_prefix(year_index, operation_id), claim_history(claim_id) and
asset_history(asset_id), each with a distinct query ID. Additional fields,
missing qualifiers and duplicate query IDs are refused. The schema and exact
dispatcher are in company-state-typed-request-20261028 under data/accounting-master.

An annual query delegates to the native report view. An event query returns
the complete recorded population prefix only if the event executed. Claim and
asset histories include origin and all executed prefix states in which the
identity is present. An absent supplied identity is not evidence of absence
from a real company. Unknown openings retain their native obligations and
supply no invented history. Wrong contexts and stale identities are invalid;
other owners, cross-profile joins and actor/public information requests remain
unsupported until their meanings and exact mappings are specified.

## Return semantics and unresolved work

The guarded result preserves the full native result, exact input identity and
optional population inspection. Its own statuses distinguish native_refusal,
opening_not_executable and inspected. Native invalid, unsupported, unresolved,
funding_failure, economic_failure, partial and complete_conditional meanings
remain visible inside that result. The inspection never upgrades them to
actual admission or complete economic coverage.

Counterparty, instrument, authority, physical location, title and population
completeness fields remain unknown where the input schema does not supply them.
Other profiles must explicitly bind compatible context, economic identities,
memory and financial-effect ownership. Source/actor admission belongs to T03
and C01; implementation of sector/basis composition belongs to T05. Their
requirements are preserved when this common definition is reviewed.

The immediate review must decide whether these dependencies, state categories,
historical queries and refusal rules are sufficient to implement this bounded
reference independently. Broader language design, source-supported company
construction, sector composition and independent release acceptance remain
open. The selected manuscript is unchanged.
