# Current interface compatibility — 28 October 2026

Selected candidate **5.55-R1 remains not_ready**. This reference reconciles 18 inspected interfaces. Exact native owners and signatures below control; older profiles do not migrate implicitly. Historical maps and selected manuscript bytes remain unchanged.

## Delivered successors

The earlier profile map proposed an ordered term-program envelope. **SelectedTermProgram/1 is delivered** and delegates to the selected term-event executor. The earlier source-opening map described a missing selected-reading attachment. **SelectedReadingHistoryAttachment/1 is delivered** as an explicit adapter; the older RetainedNetworkHistoryAttachment/1 API still has no selected-parent argument. Neither delivery establishes a whole-company language or an actual issuer opening.

All operations below preserve their native exceptions, returned statuses and refusal order. Compiling, solving and proposing effects confer no source/accounting admission, durable commit or historical information cutoff. Canonical JSON identities and raw source-byte hashes are distinct.

## Exact interfaces

### CompanyMethodAuthoring/1

Native owner: `data/accounting-master/complete-method-authoring-20261026/frontend.py`.
Entry points: `lower(source)`; `compile_typed(method, transition_profile, environment)`; `compile_text(source, environment)`.

Inputs: UTF-8 method source and a closed environment: book, event, schemas; memory_definition additionally required for transition /2.

Actor, time and context: Use the exact book/event/schema and memory context required by this native interface; compilation does not establish historical information availability. Method compilation is contextual, not eligibility or accounting admission. Only declared monetary operators and memory writes are supported.

Effect owner: company_book_transition_v1 or company_book_transition_v2 prepare; execution requires the selected engine propose call.

Outcomes: lowered_syntax_only or compiled_method with complete method/request and identities; flags executed/committed/admission remain false.

Refusals: Raises core.Invalid; source lowering embeds a physical line number in the reason. It is not a uniform returned error envelope.

Permitted successors and limits: Method compilation is contextual, not eligibility or accounting admission. Only declared monetary operators and memory writes are supported.

Detailed reference: `data/accounting-master/profile-compatibility-20261027/compatibility.md`. Exact code and evidence identities are in `source-lock.json`.

### AuthoredCompanyText/1

Native owner: `data/accounting-master/common-program-authoring-20261026/common_text.py`.
Entry points: `compile_text(source, resources)`; `execute_text(source, resources)`.

Inputs: Company source with exact digest-keyed opening/schemas/mapping/memory resources, inline full methods, selected invariant resource, registries and ordered event/report/carry commands.

Actor, time and context: Use the exact book/event/schema and memory context required by this native interface; compilation does not establish historical information availability. Does not itself author the complete invariant, dynamic nested term selection or arbitrary company methods. Later source profiles do not automatically change this parser.

Effect owner: contracted or guarded authored-program runner selected by exact target profile; method financial effects remain in shared transition engines.

Outcomes: compiled_structural containing complete program and source/resource/method spans; execute_text delegates to the exact target runner.

Refusals: compile_text catches exceptions into status=invalid with reason, stage, location and false admission flags. Runtime runner has its own complete/partial result.

Permitted successors and limits: Does not itself author the complete invariant, dynamic nested term selection or arbitrary company methods. Later source profiles do not automatically change this parser.

Detailed reference: `data/accounting-master/profile-compatibility-20261027/compatibility.md`. Exact code and evidence identities are in `source-lock.json`.

### AuthoredCompanyText/2

Native owner: `data/accounting-master/invariant-source-authoring-20261026/program_text.py`.
Entry points: `compile_text(source, resources)`; `execute_text(source, resources)`.

Inputs: Company source with exactly one inline invariant block; remaining digest-keyed resources exclude the inline invariant digest.

Actor, time and context: Use the exact book/event/schema and memory context required by this native interface; compilation does not establish historical information availability. The later Unicode repair selects different wrappers; it is not proof that this original /2 module itself was repaired.

Effect owner: Original invariant_text.lower then common_text.compile_text; no new financial evaluator.

Outcomes: AuthoredCompanyText/1 lowering with added invariant-source identity/span and exact restoration of outer source positions.

Refusals: Returns status=invalid and location on compilation failure; delegates execution after structural success.

Permitted successors and limits: The later Unicode repair selects different wrappers; it is not proof that this original /2 module itself was repaired.

Detailed reference: `data/accounting-master/profile-compatibility-20261027/compatibility.md`. Exact code and evidence identities are in `source-lock.json`.

### SelectedCompanyText/1

Native owner: `data/accounting-master/invariant-unicode-repair-20261026/company_text_unicode.py`.
Entry points: `lower(source, resources)`; `execute_source(source, resources)`.

Inputs: Exact four resource classes plus inline opening, corrected invariant, eligibility, scalar/ordered recipes and ordered event/report/carry commands.

Actor, time and context: Use the exact book/event/schema and memory context required by this native interface; compilation does not establish historical information availability. Selected DeclaredReceivableLifecycle/1 correspondence; supplied resources and source selection do not establish actual source/accounting admission.

Effect owner: AdmittedDeclarativeProgram/1 and its composer; selected opening and full command projection are checked before execution.

Outcomes: lowered_structural with selected contract, native input projection, full declarative program and bound call; execution delegates to admitted-program binding.

Refusals: Raises source Invalid(reason, location); binding/executor return stage-aware refusal or complete/partial execution.

Permitted successors and limits: Selected DeclaredReceivableLifecycle/1 correspondence; supplied resources and source selection do not establish actual source/accounting admission.

Detailed reference: `data/accounting-master/profile-compatibility-20261027/compatibility.md`. Exact code and evidence identities are in `source-lock.json`.

### CompleteClaimsCompanyText/1

Native owner: `data/accounting-master/invariant-unicode-repair-20261026/complete_text_unicode.py`.
Entry points: `lower(source, resources, reviewed_selection)`; `execute_source(source, resources, reviewed_selection)`.

Inputs: SelectedCompanyText/1 embedded source, exact resources and independently supplied reviewed_selection; population status complete/partial/unknown and residuals explicit.

Actor, time and context: Use the exact book/event/schema and memory context required by this native interface; compilation does not establish historical information availability. Completeness declaration concerns supplied synthetic population; false actual_population_completeness flag is explicit.

Effect owner: Complete-claims opening admission plus selected company binding; no inferred actual population completeness.

Outcomes: lowered_structural with derived contract, completeness, complete program and identities; execution calls complete_opening.execute.

Refusals: Raises located Invalid for source/selection mismatch; downstream complete-opening executor preserves its status and delegated result.

Permitted successors and limits: Completeness declaration concerns supplied synthetic population; false actual_population_completeness flag is explicit.

Detailed reference: `data/accounting-master/profile-compatibility-20261027/compatibility.md`. Exact code and evidence identities are in `source-lock.json`.

### SelectedTermStateText/1

Native owner: `data/accounting-master/nested-contract-source-20261026/contract_text.py`.
Entry points: `lower(source)`; `compile_text(source, memory_definition)`; `assess_source(source, memory_definition, state, coverage, selection, call)`.

Inputs: One complete explicit nested-state contract source, memory_definition; assessment additionally needs state, supplied coverage, selection and call.

Actor, time and context: Use the exact book/event/schema and memory context required by this native interface; compilation does not establish historical information availability. Does not validate future commands or infer missing population coverage; no source import of opaque algorithm-bearing definitions.

Effect owner: SelectedTermStateContract/1 structural and semantic validators; state admission is separate from source/accounting admission.

Outcomes: Exact structural contract, canonical and insertion-order identities plus source locations; assessment calls structure.admit.

Refusals: Raises located Invalid from nested postorder validation; assess_source returns selected-state admission status.

Permitted successors and limits: Does not validate future commands or infer missing population coverage; no source import of opaque algorithm-bearing definitions.

Detailed reference: `data/accounting-master/profile-compatibility-20261027/compatibility.md`. Exact code and evidence identities are in `source-lock.json`.

### SelectedTermEventText/1

Native owner: `data/accounting-master/term-event-source-20261026/event_text.py`.
Entry points: `lower(source, carry=False)`; `compile_rule(source, book, definition)`; `execute_sources(contract_source, rule_sources, definition, state, request, coverage, selection, call)`.

Inputs: Contract source plus exactly assessment/amendment/collection/carry source entries; definition, complete state, request, coverage, independent selection and exact call.

Actor, time and context: Use the exact book/event/schema and memory context required by this native interface; compilation does not establish historical information availability. Caller supplies sequential state/request/coverage and selection. Carry policy is exactly selected preserve-terms/reset-cursor. This is an existing complete event path, not a missing frontend.

Effect owner: SelectedTermCommand/2; ordered eligibility, parameterized constructor and typed transition /2; carry delegates to company_book_carry_v1.

Outcomes: execute_sources returns full SelectedTermCommand/2 execution, source diagnostics, per-rule source hashes and contract-source hash.

Refusals: Source/eligibility compile may raise Invalid; runtime failures are inside execution with failed_stage, and construction/eligibility adds source location.

Permitted successors and limits: Caller supplies sequential state/request/coverage and selection. Carry policy is exactly selected preserve-terms/reset-cursor. This is an existing complete event path, not a missing frontend.

Detailed reference: `data/accounting-master/profile-compatibility-20261027/compatibility.md`. Exact code and evidence identities are in `source-lock.json`.

### SelectedDebtReadingNetwork/1

Native owner: `data/accounting-master/debt-reading-network-20261027/compose.py`.
Entry points: `prepare(parent, reading, rounding)`; `assess(parent, reading, rounding, budget)`.

Inputs: Exact source parent, independent reading, rounding premise and explicit assessment budget.

Actor, time and context: Same source contexts, dated measurements and explicit nearest-million rounding; source knowledge availability is unestablished.

Effect owner: Selected reading constructor and TemporalMeasurementConstraints/1.

Outcomes: Prepared temporal definition or unresolved/invalid; assessment delegates feasibility/unknown.

Refusals: Exact-parent or rounding violations are invalid; absent reading/rounding remains unresolved.

Permitted successors and limits: Temporal assessment or explicit SelectedReadingHistoryAttachment/1; never a direct executable opening.

Detailed reference: `data/accounting-master/source-opening-compatibility-20261027/compatibility.md`. Exact code and evidence identities are in `source-lock.json`.

### TemporalMeasurementConstraints/1

Native owner: `scripts/temporal_measurement_constraints_v1.py`.
Entry points: `lower(definition, budget)`; `assess(definition, budget)`.

Inputs: Closed typed observations, intervals/premises, same-time or stock-flow relations and budget.

Actor, time and context: Exact context, unit/scale, measurement dates and relation dates; no implied event history.

Effect owner: Temporal constraint compiler and selected numeric solver.

Outcomes: Native temporal lowering/assessment including conditional feasibility and witness.

Refusals: Native invalid, unresolved, infeasible, unknown or unsupported results retain their meanings.

Permitted successors and limits: Explicit typed history attachment requires full history, mappings and obligations.

Detailed reference: `data/accounting-master/source-opening-compatibility-20261027/compatibility.md`. Exact code and evidence identities are in `source-lock.json`.

### RetainedNetworkHistoryAttachment/1

Native owner: `scripts/retained_network_history_v1.py`.
Entry points: `assess(body, budget)`; `verify_result(body, budget, result)`.

Inputs: Closed source_request and exactly one supplied history/bindings entry per source context; separate budget.

Actor, time and context: Context identity is exact; cross-context relations require conversion; availability is not supplied.

Effect owner: Native retained source engine, context partitioning and typed attachment.

Outcomes: Complete source result and context attachments; conditional_candidates_with_unresolved_facts retains obligations.

Refusals: Invalid source/shape; invalid_history_attachment, supplied_history_incompatible, unresolved or unknown under native precedence.

Permitted successors and limits: No selected-parent parameter. Use the separate selected-reading adapter; do not relabel a result or replace its parent.

Detailed reference: `data/accounting-master/source-opening-compatibility-20261027/compatibility.md`. Exact code and evidence identities are in `source-lock.json`.

### TypedHistoryMeasurementAttachment/1

Native owner: `scripts/typed_history_measurement_attachment_v1.py`.
Entry points: `prepare(definition, budget)`; `assess(definition, budget)`; `replay_witness(definition, budget, witness)`.

Inputs: Complete typed history, temporal measurements, explicit bindings, obligations and budget; replay also requires full witness.

Actor, time and context: History and measurement dates and contexts remain explicit; feasibility is not actual history or knowledge admission.

Effect owner: Typed history and temporal constraint engines.

Outcomes: Conditional witness/replay with remaining target obligations.

Refusals: Missing premises remain unresolved; invalid, infeasible, unknown and unsupported retain native scope.

Permitted successors and limits: ConditionalCompanyOpening/1 accepts the full definition and complete witness, subject to its separate mapping and status checks.

Detailed reference: `data/accounting-master/source-opening-compatibility-20261027/compatibility.md`. Exact code and evidence identities are in `source-lock.json`.

### ConditionalCompanyOpening/1

Native owner: `scripts/conditional_company_opening_v1.py`.
Entry points: `map_opening(request)`.

Inputs: Complete attachment, budget, witness, account/memory/context and boundary mapping.

Actor, time and context: Next civil day after final history snapshot, explicit no-intervening-event premise; unit money scale 1/1; no investor-cutoff claim.

Effect owner: Opening mapper replays all parent constraints and final snapshot.

Outcomes: conditional_opening or candidate_opening_with_unresolved_obligations, with full parent provenance.

Refusals: Unresolved premises before construction; invalid witness, mapping, unit, context or date.

Permitted successors and limits: Only a recomputed conditional_opening can clear ConditionalCompanyContinuation/1; a candidate with obligations cannot.

Detailed reference: `data/accounting-master/source-opening-compatibility-20261027/compatibility.md`. Exact code and evidence identities are in `source-lock.json`.

### CompanyBookTransition/1

Native owner: `scripts/company_book_transition_v1.py`.
Entry points: `prepare(book, request)`; `propose(book, request)`; `apply(book, request, proposal)`.

Inputs: Complete CompanyBook/1, method/event/schema bindings and exact proposal for apply.

Actor, time and context: Exact book entity, context, event date, schemas and expected-state identities.

Effect owner: Shared transition engine owns monetary and memory effects.

Outcomes: Native proposed/applied provisional monetary and memory effects.

Refusals: Native validation and requirements refusals; never rewrite a stale state request.

Permitted successors and limits: Report only using the full before/after books, declared flows, maps and movements; no durability or admission is implied.

Detailed reference: `data/accounting-master/source-opening-compatibility-20261027/compatibility.md`. Exact code and evidence identities are in `source-lock.json`.

### ConditionalCompanyContinuation/1

Native owner: `scripts/conditional_company_continuation_v1.py`.
Entry points: `run(body)`.

Inputs: Opening request and exact result, transition request, equity movements and notes.

Actor, time and context: Same opening context and declared event/report period; unknown history obligations are not removed by chronology.

Effect owner: Recomputed opening, native transition and report engines.

Outcomes: conditional_continuation with full delegated transition/report.

Refusals: Opening mismatch invalid; recomputed unresolved or candidate opening gives unresolved; financial status propagates; report failure invalid.

Permitted successors and limits: Full report may support the native carry interface only with exact report identity and complete policies.

Detailed reference: `data/accounting-master/source-opening-compatibility-20261027/compatibility.md`. Exact code and evidence identities are in `source-lock.json`.

### CompanyBookReport/1

Native owner: `scripts/company_book_reports_v1.py`.
Entry points: `request(opening, closing, schemas, mapping, equity_movements=None, notes=None)`; `report(body)`.

Inputs: Full opening/closing books, schemas, CompanyStatementMap/1, equity movements and note obligations.

Actor, time and context: Same entity, period, basis, scale and schema identities; all declared flows and equity/noncash movements remain.

Effect owner: Report engine; no new postings.

Outcomes: Complete recorded-period statements and reconciliations.

Refusals: Incomplete map, correspondence or movement reconciliation returns native invalid.

Permitted successors and limits: CompanyBookCarry/1 requires complete report request and bound report identity.

Detailed reference: `data/accounting-master/source-opening-compatibility-20261027/compatibility.md`. Exact code and evidence identities are in `source-lock.json`.

### CompanyBookCarry/1

Native owner: `scripts/company_book_carry_v1.py`.
Entry points: `request(report_request, close_id, retained_account, next_end_exclusive, memory_policies)`; `propose(body)`; `apply(body, proposal)`.

Inputs: Valid report request, close ID, retained-equity account, next period end and per-leaf memory policies.

Actor, time and context: Declared closing period and next opening; no silent memory reset, currency conversion or durable commit.

Effect owner: Carry engine owns closing proposals and explicit memory policies.

Outcomes: Provisional closing journal, archive and next opening.

Refusals: Stale report, early carry, incomplete policies and unreconciled movement are invalid.

Permitted successors and limits: Only declared supported next-period state; term programs additionally enforce preserve-terms/reset-cursor policy.

Detailed reference: `data/accounting-master/source-opening-compatibility-20261027/compatibility.md`. Exact code and evidence identities are in `source-lock.json`.

### SelectedTermProgram/1

Native owner: `data/accounting-master/selected-term-program-20261027/program.py`.
Entry points: `compile_program(program, selection, expected_selection_sha256)`; `execute(program, selection, expected_selection_sha256)`.

Inputs: Closed program, independent selection and expected selection digest; exact opening/coverage and 1–64 ordered requests.

Actor, time and context: Each request binds full current state; explicit ordered selection, source bytes and population; no inferred availability or automatic re-selection.

Effect owner: SelectedTermEventText/1 owns execution; program only advances successful proposed states and inherited coverage.

Outcomes: compiled_structural or complete_provisional, refused or partial with full successful prefix and untouched remaining commands.

Refusals: invalid_program before execution; first refusal gives refused, later refusal gives partial preserving native failed result.

Permitted successors and limits: Selected carry only; no generic SelectedCompanyText migration or standalone report command.

Detailed reference: `data/accounting-master/selected-term-program-20261027/contract.md`. Exact code and evidence identities are in `source-lock.json`.

### SelectedReadingHistoryAttachment/1

Native owner: `data/accounting-master/selected-reading-history-20261027/compose.py`.
Entry points: `prepare(body)`; `assess(body)`.

Inputs: Closed source_parent, reading, rounding, histories and budget; all exact selected contexts present.

Actor, time and context: Keep original source parent, selected reading, rounding, source/history budgets, measurement contexts and all obligations distinct.

Effect owner: Pinned selected reading, unchanged native context partitioning and typed attachment engines.

Outcomes: Selected source plus complete context attachments; conditional_candidates_with_unresolved_facts leaves actual history unknown.

Refusals: Missing reading/rounding unresolved without history assessment; invalid inputs/dependencies invalid; native invalid_history_attachment, supplied_history_incompatible, unresolved or unknown.

Permitted successors and limits: Typed attachment definitions/witnesses remain candidates. Wrapper is not opening input; actual issuer opening and cross-context history remain unestablished.

Detailed reference: `data/accounting-master/selected-reading-history-20261027/result.md`. Exact code and evidence identities are in `source-lock.json`.

## Composition decisions

- `method → authored_program`: **checked_embedding**. Full method source lowered for registry entries; contextual compilation/execution belongs to actual command state.
- `inline_invariant_program → authored_program`: **checked_lowering**. Inline invariant becomes the exact imported invariant resource with translated locations.
- `selected_company → complete_claims`: **checked_embedding**. CompleteClaims wraps selected-company lowering and binds an independently supplied selection and population declaration.
- `nested_contract → term_event`: **checked_dependency**. execute_sources compiles the contract and executes all selected event rules using the same state/coverage call.
- `term_event → selected_company`: **no_direct_embedding**. Selected-company rule grammar consumes flat eligibility and scalar/ordered recipes; no term-event source dispatcher or SelectedTermCommand/2 branch exists in the inspected runner. A new adapter requires explicit state, coverage, carry/report and selection mapping.
- `historical_core0 → method`: **no_implicit_migration**. Historical Core 0 debt IR and current method records have distinct schemas/owners; the inspected compiler accepts its named method profile only.
- `term_event → term_program`: **implemented**. Ordered program delegates each request to the unchanged selected event executor; preserves source/state/selection identities and full prefix.
- `selected_reading → selected_history`: **implemented**. Explicit selected-parent adapter retains original and selected source parents and all contexts; old retained-history API is unchanged.
- `selected_reading → temporal`: **implemented**. Exact prepared definition, explicit premises and budget.
- `temporal → opening`: **refused_direct_transfer**. Measurement witness alone is not a complete typed history/opening request.
- `selected_history → opening`: **refused_direct_transfer**. The wrapper is not an opening request. A separately complete typed definition, witness and mapping must meet opening requirements.
- `typed_history → opening`: **conditional**. Full definition, complete witness, unit-scale mapping and premises required; target obligations survive.
- `opening → continuation`: **conditional**. Exact recomputation and conditional_opening status required; obligations block clearance.
- `transition → report`: **conditional**. Complete before/after books, flows, mapping, equity movements and notes required.
- `report → carry`: **conditional**. Exact report request/identity, dates, retained account and complete leaf policies required.
- `term_program → selected_company`: **no_implicit_migration**. Distinct grammar, state, population and report/carry semantics; no generic embedding is claimed.

## Remaining scope

The 18 rows are a bounded union of already inspected profiles, not a denominator for complete DSL acceptance. Other company/model profiles, sector/group composition, actual source/history/opening admission, full recipient dependencies and independent acceptance remain open. Full native replays and invalid-transfer controls are recorded separately; passing them does not convert the remaining 180 issuer obligations into established facts.
