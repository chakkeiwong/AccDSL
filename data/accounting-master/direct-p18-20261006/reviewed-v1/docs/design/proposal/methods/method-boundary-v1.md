# The common boundary of a financial method

A financial method turns an admitted economic event and opening state into a
proposed accounting consequence. It does not acquire facts, decide a company's
reporting framework, calibrate a probability law or commit its own output. Those
responsibilities have separate owners in P16. This specification and the domain
methods below propose the implementation behavior required by MC02, MC04–MC25,
MC27–MC29 and MC34–MC35. No domain engine is implemented by these documents.

## M1. Method definitions and inputs

Each versioned MethodDefinition has the eight groups in standards-mapping-v1.md,
plus the following closed header. Its identity is a portable P16 Ref; its
contents include nonempty method_id/version, event_kind, state_schema,
event_schema, journal_schema, delta_schema, output_schema, required_contexts,
authority_requirements, preconditions, algorithm, account_roles,
report_mappings, numerical_capability, examples and unsupported_cases.
All schema names resolve through the posting profile's immutable schema lock.
Each precondition has an id, typed predicate, required input/admission references
and a defined consequence of false or unknown. Domain tables specify economic
fields; money is an exact rational with a Context Ref, dates use the P16 time
contract, counts are integers and rate conventions are named. Unknown is an
explicit tagged value, never an omitted field, zero, false or default rate.

The input is P16 AccountingEventBasis/v1. Its event_ref resolves to the named
domain event, opening_ref to the domain state and chart_ref to the account-role
mapping. Method-specific facts may be reached from evidence_refs or the admitted
assumptions_ref, but their provenance survives. The branch's immutable book_mode
and the posting profile determine whether synthetic or real-workspace evidence
can authorize posting. Neither a checked teaching example nor the native
assess_only response is a PostingAuthorization. A source-supported method still
needs the actual contract, entity, date and judgment inputs for a real branch.

Applicability is evaluated in order: framework/jurisdiction and operative dates;
entity/transaction scope; contract and recognition facts; elections; numerical
capability; account/context bindings. Evaluate every material precondition and
retain each finding. A false required fact gives ineligible, an unknown required
fact gives unresolved, and an event outside the declared method gives outside_scope.
Do not overwrite a known false finding merely because another fact is unknown.
Missing authority or unverified amendments cannot yield source-supported
permission. A standard's explicit presumption, such as the identified-asset
substitution rule, is itself a conditional rule requiring its stated conditions;
it is not interchangeable with a blanket missing-data rejection.

## M2. Proposed operation and journal semantics

The future method evaluator is a pure operation of the resolved EventBasis and
its posting profile. It produces findings, either a proposed journal/delta or
explicit absence, required disclosures, and numerical status. It reads only the
admitted evidence/time/information view. It cannot observe a future simulated
realization while measuring a current expectation or deciding today's behavior.
Source-period accounting is recomputed from that source's admitted view;
an updated view creates a new derivation with explicit invalidation lineage.

For eligible inputs, apply the domain recurrence to an immutable opening state,
then derive journal lines and the independent economic delta. A journal line has
account role, debit or credit, positive rational quantity, currency/context,
entity, book, event and method bindings. Zero lines are omitted. Negative effects
reverse sides; they are not negative debit quantities. Each currency/book journal
balances. Cross-currency exchanges name both legs, functional amounts and rate
evidence; their raw currency quantities are never summed as one unit.

Validate domain conservation separately: cash movement equals settlements;
inventory quantity/cost equals admitted lot movements; debt face amount is not
silently replaced by carrying value; share count is not a money balance; group
eliminations have matched counterpart and perimeter evidence. A balanced entry
with the wrong depreciation life or effective-interest base fails the method.

P16 A1 controls authorization and commit. accounting.authorize@1 recomputes the
method/profile findings and produces PostingAuthorization/v1. A proposed
JournalProposal and EconomicDelta bind the same basis and authorization. The
outer accounting.commit@1 request carries the sole expected head/generation;
AccountingCommitArguments carries only the four specified Refs. Exact replay
precedes freshness. A new valid request atomically commits journal, economic
state and receipt; failure commits none. Domain business-event identities remain
stable across retries and include actual contract/lot/cohort source identity.
The method definitions here do not add operations to a running registry.

The method identifiers below are package members, not new platform operations.
Their versioned records belong in an ExtensionPackage's `method_refs` and
`state_requirements`; required schemas, authority and capabilities are pinned
in the same package lock. An operation still uses its exact P16 I2 signature.

| Proposed method family | P16 operation and ownership |
| --- | --- |
| Corporate, financing, bank and insurance events | `scenario.project@1` constructs conditional future events; `accounting.assess@1` evaluates the native assess-only request. Separately, `accounting.authorize@1` evaluates EventBasis under a supported posting profile; `accounting.propose@1` returns journal and delta; `accounting.commit@1` requests the atomic mutation. `report.build@1` derives statements. No assessment result substitutes for authorization. |
| Group, FX and cross-basis adjustments | The same accounting sequence applies in a declared adjustment book with source entity-book and perimeter dependencies; `report.build@1` aggregates that compatible view. A method must not silently mutate legal-entity books. |
| Dated rule selection | Applicability predicates are part of the method/posting profile assessed by the accounting operations. A proposed authority/election reading uses `review.propose@1` and the separately authorized `review.commit@1`; selecting a framework is not itself posting permission. |
| Reconstruction and numerical queries | `history.construct@1`, `history.refine@1` and `history.query@1` retain their declared scopes, capabilities and coverage. A root/discount routine is a method dependency, not a replacement history endpoint. |
| Probability and forecast | Native supported operations use `uncertainty.evaluate@1` and separate `uncertainty.admit@1`/`uncertainty.select@1`. `scenario.project@1` supplies exogenous stress. Continuous and causal methods here are proposed extension capabilities: they remain unsupported by the initial P16 finite/exogenous profile until their schemas, signatures and conformance are separately admitted. |
| Source and software preparation | `source.prepare@1` returns candidates and traversal obligations; review operations handle admission, and `model.compile@1` constructs candidate IR. An extraction result never includes a fabricated acceptance receipt. |
| Literature support | Support records are evidence for `review.propose@1`; review decisions and `record.explain@1` preserve claim-specific admission and lineage. Literature checking creates no accounting or solver authority. |

For a corporate `deliver` event, for example, `event_ref` identifies its exact
contract/obligation/quantity/allocation/control record, `opening_ref` resolves
the R/B/C and inventory/receivable state, and `method_ref` names that scoped
delivery recurrence. The EventBasis also binds all P16 context, authority,
assumption, view, branch and chart fields; domain shorthand cannot omit them.
The authorization names that exact basis and profile. Proposed journal and
independent delta then carry the same basis/authorization Refs. Report methods
consume the resulting frozen branch, not an unrelated cumulative revenue value.

## M3. Financial boundaries and result status

Recognition time, event time, payment time and report availability remain distinct.
An obligation can exist when cash is insufficient; that shortage can trigger a
separate modeled default or funding action. It does not erase the obligation,
invent a loan or commit an impossible payment. Conditional forecasts retain
default states and their accrued liabilities. Unsupported law, failed numerical
evaluation and unexplored alternatives retain their own P16 coverage regions.

Run all statements and notes from one common path. The ledger view carries
signed account balances plus economic schedules; statement maps partition each
account's relevant movement and explicitly split mixed roles. Profit, OCI,
owner contributions/distributions and opening equity reconcile. Cash flows
exclude noncash recognition and separately reconcile FX effects on cash.
Parent, subsidiary, consolidation adjustment and tax books remain distinct;
their consolidation is a query over dated compatible books, not deletion of
the source entries. Intercompany cash is not group external cash.

Examples in this collection use unrounded rationals internally. Displaying
2.50 does not change its identity. A real posting quantum needs a declared
rounding/tie policy and a separate residual allocation rule. Numerical methods
that only enclose a value may post only if the whole certified enclosure maps
to the same authorized rounded amount; otherwise return rounding_unresolved.
An approximate estimate without that certificate remains approximate with its
own tolerance, provenance and downstream sensitivity. No library float or
sample maximum acquires exact status from its JSON serialization.

## M4. Aggregation and retention

Retain contract/lot/cohort detail unless the query's sufficient-state rule is
proved for the selected methods, horizon, scenarios and reporting maps. An exact
grouping map G must satisfy G(T(s,e))=Tg(G(s),e) and Q(s)=Qg(G(s)) for every
admitted state/event in that scope. This is a local proof obligation, not an
algorithm claiming to decide equivalence for arbitrary software.

Two fixed-rate bullet debts with identical currency, payment dates, seniority,
effective rate, accounting category and scenario response can sum principal and
carrying amount when all transitions/reporting are additive and no per-contract
threshold, fee or option is queried. Two loans of 50 at 2% and 8% instead produce
aggregate annual interest 5 only in that unchanged year. Replacing them by one
5% loan loses the response when the second resets, defaults or matures first.
Even identical current journals cannot prove that replacement safe. Grouping
bank loans across credit grades or insurance contracts across required groups
likewise requires preserved risk/cohort dimensions; arithmetic equality at one
date is insufficient.

A change of scenario, query, method, perimeter, authority, observation or horizon
invalidates the corresponding sufficiency certificate and its descendants.
Recompute from retained detail or return resolution_insufficient. Approximate
grouping needs a specified error bound for the actual queried quantity and its
supporting evidence; none is established merely by the examples here.
