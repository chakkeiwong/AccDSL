# Source, history, opening and reporting compatibility

27 October2026. SelectedSourceOpeningCompatibility/1, a bounded normative
composition reference for the exact profiles below. Candidate5.53 remains
provisional; this reference neither changes the native APIs nor defines a
universal company schema. Native definitions and complete retained exchanges
are locked by dependency-lock.json after verification. A conflicting later
profile is a different interface, not an implicit migration.

## Authority, identity and the supported boundary

Each profile owns its closed request/result fields and validation order.
JSON schemas and returned field names alone are insufficient. Callers preserve
the exact native profile, request, method/schema identities, source parents,
complete result and native reason. SHA256 semantic identities use each
profile's canonical JSON convention; source-file identities hash raw bytes.
They are different quantities. No wrapper grants source admission, accounting
admission, posting authorization or durability from a feasible/proposed result.

| Profile and entry point | Authoritative implementation | Accepted input / result meaning |
|---|---|---|
| SelectedDebtReadingNetwork/1: prepare(parent,reading,rounding), assess(parent,reading,rounding,budget) | debt-reading-network-20261027/compose.py | Exact selected parent/reading and explicit rounding premise; complete temporal definition and conditional numeric assessment. No executable opening. |
| TemporalMeasurementConstraints/1: lower(definition,budget), assess(definition,budget) | scripts/temporal_measurement_constraints_v1.py | Typed observations, intervals/premises and same-time or stock-flow relations; numeric lowering preserves context and measurement dates. |
| RetainedNetworkHistoryAttachment/1: assess(body,budget) | scripts/retained_network_history_v1.py | source_request plus a history/bindings entry for every exact source context; independently recomputes its own retained source parent. |
| TypedHistoryMeasurementAttachment/1: prepare, assess, replay_witness(definition,budget,witness) | scripts/typed_history_measurement_attachment_v1.py | Complete typed history, temporal measurements, explicit bindings and obligations; conditional joint witness or native unresolved/invalid/infeasible/unknown result. |
| ConditionalCompanyOpening/1: map_opening(request) | scripts/conditional_company_opening_v1.py | Complete attachment, budget, complete witness and account/memory/context/boundary mapping; one selected synthetic opening plus unchanged parent provenance. |
| CompanyBookTransition/1: propose(book,request), apply(book,request,proposal) | scripts/company_book_transition_v1.py | Complete CompanyBook/1 plus exact method/event/schema bindings; provisional monetary and memory effects after requirements pass. |
| ConditionalCompanyContinuation/1: run(body) | scripts/conditional_company_continuation_v1.py | Opening request/result, transition request, equity movements and notes; exact opening recomputation precedes one declared transition and report. |
| CompanyBookReport/1: request(...), report(body) | scripts/company_book_reports_v1.py | Complete opening/closing books, schemas, CompanyStatementMap/1, equity movements and note obligations; recorded-period statements and reconciliation. |
| CompanyBookCarry/1: request(...), propose(body), apply(body,proposal) | scripts/company_book_carry_v1.py | Valid report request, exact report identity, close ID, retained-equity account, next period end and per-leaf memory policies; provisional closing journal, archive and next opening. |

## Exact composition edges

1. The selected debt-reading result's definition can be assessed as temporal
   measurements, with the same budget and explicit premises. Its source_parent
   preserves the original PDF-only result, all256 source observations and143
   dispositions. Its selected definition preserves236 observations and101
   equations. The changed issuance interval is open(-1/2,1/2) USD million under
   the declared nearest-million ties-away hypothesis; exact zero and
   nonnegativity are not added. A different source, period, equation set or
   rounding rule requires a separately reviewed selection.

2. A temporal definition alone cannot feed an opening. Attachment additionally
   needs a complete typed economic history, explicit compatible mappings and
   a complete joint witness. A measurement witness is not an event history.
   RetainedNetworkHistoryAttachment/1 recomputes source_request via its own
   native source engine. Its public assess signature has no selected-parent
   parameter. Replacing its parent with SelectedDebtReadingNetwork/1 is
   therefore not an implemented migration. Such a successor must retain the
   original and selected parents, every context, every relation, the reading
   premises and all existing target obligations; it cannot merely overwrite
   a stored witness or relabel the original result.

3. The retained network partitions by exact value context. Every relation
   belongs to exactly one context; cross-context relations require an explicit
   conversion. A caller must supply exactly one history entry per context.
   Every selected observation remains, even if unmapped; every unmapped one
   creates an obligation. The adapter also adds actual_history and whole_source
   obligations in each context. Feasible per-context candidates do not establish
   a joint cross-context company history.

4. ConditionalCompanyOpening consumes a complete TypedHistoryMeasurementAttachment
   definition and witness, not the network wrapper result. It recompiles the
   parent constraints and replays every supplied witness variable. The mapping
   must cover every final account and every numeric memory field once. Account
   destinations are distinct; memory paths cannot overlap. The source date
   is the last declared history date; the synthetic opening is the next civil
   day, under explicit context and no-intervening-event premises. Only unchanged
   source entity/book, matching currency dimensions and unit money scale1/1
   are accepted. USD million source values cannot be relabeled as USD books.
   The whole source definition, source snapshot, witness, exclusions and
   obligations remain in provenance. The helper does not close nonzero income
   or expense balances to manufacture an opening.

5. ConditionalCompanyContinuation recomputes the exact complete opening result
   before inspecting the transition. Unresolved premises or outstanding target
   obligations return unresolved with no current book. A conditional opening
   must match the transition's expected state and memory schema. Native method
   requirements, financial effects and memory effects then run in order; report
   validation is the last condition for returning conditional_continuation.
   All native admission/authorization flags remain false. A report failure
   returns invalid and supplies no successful successor, although the method
   proposal may have been computed locally; no book was committed.

6. Report consumes a complete opening/closing pair from the same context,
   period, chart and cash account. Opening flows must be empty, temporary
   balances zero, and lifetime event IDs a prefix of closing IDs. Current-period
   gross flows reference the new IDs. Report lines partition every account
   exactly once with matching classification. Direct equity movements use
   reported-equity signs, not signed debit entries. A distribution of1 has
   cash posting-1, equity posting+1, reported equity movement-1 and financing
   flow-1. Balance, cash and equity reconciliations must all vanish. Notes and
   the unresolved indirect operating-cash bridge remain visible.

7. Carry consumes a valid report for a declared last-period-day closing book;
   an early-date report cannot be turned into a year-end carry. It requires a
   new close ID, an explicit retained-equity account, a later next period end,
   and exactly one policy for every memory leaf. Preserve, typed reset and
   next_period_start are distinct policies; the last requires a date leaf.
   Closing reverses every income/expense balance into the chosen retained
   account and changes no cash. The next opening preserves the complete
   account population and lifetime event IDs, adds the close ID, resets only
   current-period flows and applies the declared memory policies. The archive
   binds report, preclose, closed book, next opening and policy identities.

## Dates, units and information

Civil periods are half-open[start,end_exclusive); a stock-flow opening is at
start minus one day and closing is at end_exclusive minus one day. A history
movement binding sums declared events whose dates lie in that half-open period.
Snapshot bindings use opening fields plus every selected event through the
snapshot. Same-time equations require equal time and value types. Coefficient
products must exactly match the measured value type, including dimensions,
context and scale. There is no implicit currency, book, population or calendar
conversion.

CompanyBook/1 uses exact signed rational balances: assets/expenses have debit
sign and liabilities/equity/income credit sign. Report reverses the last three
classes and adds unclosed profit to reported equity. Source dashes, missing
values and uncertain intervals are not zero-valued balances. Numeric memory
retains its own dimensions; units of goods are not money.

These helpers check measurement and event chronology. They do not establish
exact-byte publication, ingestion or reviewer-knowledge dates, or a historical
investor information cutoff. ConditionalCompanyOpening records
investor_information_cutoff_checked=false. A next-day synthetic opening is
therefore not an as-of admissibility finding. The complete final snapshot rule
also prevents silently opening at an earlier date under later observations.

## Status precedence and refusal

Native reason strings are diagnostic, not a new common error-code standard.
When several conditions fail, retain the result of native validation order;
do not combine enums into a universal success Boolean.

| Interface | Decision order / permissible downstream action |
|---|---|
| Selected reading | Bad exact parent/reading or rounding gives invalid; missing reading/rounding gives unresolved; prepared definition delegates feasibility/unknown to temporal assessment. None supplies an opening. |
| Network/history | Invalid request/source fails first. Assembled attachment invalid precedes conditional infeasibility, then unresolved, then unknown/unsupported, then conditional_candidates_with_unresolved_facts. All child findings remain available. |
| Typed attachment | Invalid shape/type/mapping fails; missing premises return unresolved. Feasible witness with obligations is a candidate, not target existence. Complete verified infeasibility applies only to the stated family. Exhausted/unsupported search remains unknown/unsupported. |
| Opening | Missing attachment premises return unresolved before constructing any opening. Witness/mapping/type/date violations return invalid. Outstanding obligations permit candidate_opening_with_unresolved_obligations but never continuation clearance. |
| Continuation | Exact opening-result mismatch is invalid; recomputed unresolved/candidate opening gives unresolved; only conditional_opening reaches the financial method. Method status propagates with its nested result. Report failure is invalid. |
| Report/carry | Violated correspondence, incomplete map, unreconciled movement, stale report or incomplete carry policy returns invalid. proposed/applied_provisional are provisional data results, not durable or authorized postings. |

## Evidence and remaining implementation work

The bounded conformance check replays complete recorded requests/results for
four openings, four continuations and four carries. Independent expected
amounts accompany these replays; equality to old output alone is not the
financial oracle. Negative checks cover direct temporal-to-opening input,
missing premises, retained target obligations, unmapped measurements, lost
memory, wrong entity/scale, stale result/state, missing equity movement,
early carry and incomplete memory policy. The complete selected source result
and its existing controls are read, not regenerated. Exact results and command
are written only to a new attempt directory.

This map resolves the listed edge meanings at their exact versions. Required
issuer facts, full mixed/continuous history construction, the selected-source
network-to-history adapter, historical knowledge admission, populated claim
interfaces, broader sector/group interfaces, durable storage and independent
implementation acceptance remain open. Later higher-version profiles retain
their own semantics. No original MC acceptance requirement is waived.
