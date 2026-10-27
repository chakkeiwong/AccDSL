# Selected source and transition compatibility

Candidate 5.51 remains governing. This reference identifies seven inspected interfaces and six composition edges. It is a scoped implementation reference, not a replacement for the complete language specification.

Source syntax, structural compilation, state admission, proposed transition and actual accounting/source admission are different stages. Error representation also differs: several frontends raise located exceptions while the old company compiler returns invalid records. Consumers must use the named interface contract.

## CompanyMethodAuthoring/1

UTF-8 method source and a closed environment: book, event, schemas; memory_definition additionally required for transition /2.

Result: lowered_syntax_only or compiled_method with complete method/request and identities; flags executed/committed/admission remain false.

Failure: Raises core.Invalid; source lowering embeds a physical line number in the reason. It is not a uniform returned error envelope.

Semantic owner: company_book_transition_v1 or company_book_transition_v2 prepare; execution requires the selected engine propose call.

Limits: Method compilation is contextual, not eligibility or accounting admission. Only declared monetary operators and memory writes are supported.

- lower(source) — data/accounting-master/complete-method-authoring-20261026/frontend.py:32
- compile_typed(method, transition_profile, environment) — data/accounting-master/complete-method-authoring-20261026/frontend.py:109
- compile_text(source, environment) — data/accounting-master/complete-method-authoring-20261026/frontend.py:122

Retained evidence: data/accounting-master/complete-method-authoring-20261026/checks.json.

## AuthoredCompanyText/1

Company source with exact digest-keyed opening/schemas/mapping/memory resources, inline full methods, selected invariant resource, registries and ordered event/report/carry commands.

Result: compiled_structural containing complete program and source/resource/method spans; execute_text delegates to the exact target runner.

Failure: compile_text catches exceptions into status=invalid with reason, stage, location and false admission flags. Runtime runner has its own complete/partial result.

Semantic owner: contracted or guarded authored-program runner selected by exact target profile; method financial effects remain in shared transition engines.

Limits: Does not itself author the complete invariant, dynamic nested term selection or arbitrary company methods. Later source profiles do not automatically change this parser.

- compile_text(source, resources) — data/accounting-master/common-program-authoring-20261026/common_text.py:31
- execute_text(source, resources) — data/accounting-master/common-program-authoring-20261026/common_text.py:184

Retained evidence: data/accounting-master/common-program-authoring-20261026/checks.json.

## AuthoredCompanyText/2

Company source with exactly one inline invariant block; remaining digest-keyed resources exclude the inline invariant digest.

Result: AuthoredCompanyText/1 lowering with added invariant-source identity/span and exact restoration of outer source positions.

Failure: Returns status=invalid and location on compilation failure; delegates execution after structural success.

Semantic owner: Original invariant_text.lower then common_text.compile_text; no new financial evaluator.

Limits: The later Unicode repair selects different wrappers; it is not proof that this original /2 module itself was repaired.

- compile_text(source, resources) — data/accounting-master/invariant-source-authoring-20261026/program_text.py:14
- execute_text(source, resources) — data/accounting-master/invariant-source-authoring-20261026/program_text.py:78

Retained evidence: data/accounting-master/invariant-source-authoring-20261026/checks.json.

## SelectedCompanyText/1

Exact four resource classes plus inline opening, corrected invariant, eligibility, scalar/ordered recipes and ordered event/report/carry commands.

Result: lowered_structural with selected contract, native input projection, full declarative program and bound call; execution delegates to admitted-program binding.

Failure: Raises source Invalid(reason, location); binding/executor return stage-aware refusal or complete/partial execution.

Semantic owner: AdmittedDeclarativeProgram/1 and its composer; selected opening and full command projection are checked before execution.

Limits: Selected DeclaredReceivableLifecycle/1 correspondence; supplied resources and source selection do not establish actual source/accounting admission.

- lower(source, resources) — data/accounting-master/invariant-unicode-repair-20261026/company_text_unicode.py:21
- execute_source(source, resources) — data/accounting-master/invariant-unicode-repair-20261026/company_text_unicode.py:149

Retained evidence: data/accounting-master/invariant-unicode-repair-20261026/checks.json.

## CompleteClaimsCompanyText/1

SelectedCompanyText/1 embedded source, exact resources and independently supplied reviewed_selection; population status complete/partial/unknown and residuals explicit.

Result: lowered_structural with derived contract, completeness, complete program and identities; execution calls complete_opening.execute.

Failure: Raises located Invalid for source/selection mismatch; downstream complete-opening executor preserves its status and delegated result.

Semantic owner: Complete-claims opening admission plus selected company binding; no inferred actual population completeness.

Limits: Completeness declaration concerns supplied synthetic population; false actual_population_completeness flag is explicit.

- lower(source, resources, reviewed_selection) — data/accounting-master/invariant-unicode-repair-20261026/complete_text_unicode.py:20
- execute_source(source, resources, reviewed_selection) — data/accounting-master/invariant-unicode-repair-20261026/complete_text_unicode.py:113

Retained evidence: data/accounting-master/invariant-unicode-repair-20261026/checks.json.

## SelectedTermStateText/1

One complete explicit nested-state contract source, memory_definition; assessment additionally needs state, supplied coverage, selection and call.

Result: Exact structural contract, canonical and insertion-order identities plus source locations; assessment calls structure.admit.

Failure: Raises located Invalid from nested postorder validation; assess_source returns selected-state admission status.

Semantic owner: SelectedTermStateContract/1 structural and semantic validators; state admission is separate from source/accounting admission.

Limits: Does not validate future commands or infer missing population coverage; no source import of opaque algorithm-bearing definitions.

- lower(source) — data/accounting-master/nested-contract-source-20261026/contract_text.py:204
- compile_text(source, memory_definition) — data/accounting-master/nested-contract-source-20261026/contract_text.py:212
- assess_source(source, memory_definition, state, coverage, selection, call) — data/accounting-master/nested-contract-source-20261026/contract_text.py:239

Retained evidence: data/accounting-master/nested-contract-source-20261026/attempt-01/checks.json.

## SelectedTermEventText/1

Contract source plus exactly assessment/amendment/collection/carry source entries; definition, complete state, request, coverage, independent selection and exact call.

Result: execute_sources returns full SelectedTermCommand/2 execution, source diagnostics, per-rule source hashes and contract-source hash.

Failure: Source/eligibility compile may raise Invalid; runtime failures are inside execution with failed_stage, and construction/eligibility adds source location.

Semantic owner: SelectedTermCommand/2; ordered eligibility, parameterized constructor and typed transition /2; carry delegates to company_book_carry_v1.

Limits: Caller supplies sequential state/request/coverage and selection. Carry policy is exactly selected preserve-terms/reset-cursor. This is an existing complete event path, not a missing frontend.

- lower(source, carry=False) — data/accounting-master/term-event-source-20261026/event_text.py:156
- compile_rule(source, book, definition) — data/accounting-master/term-event-source-20261026/event_text.py:162
- execute_sources(contract_source, rule_sources, definition, state, request, coverage, selection, call) — data/accounting-master/term-event-source-20261026/event_text.py:168

Retained evidence: data/accounting-master/term-event-source-20261026/attempt-01/checks.json.

## Composition edges

- method → authored_program (checked_embedding): Full method source lowered for registry entries; contextual compilation/execution belongs to actual command state.
- inline_invariant_program → authored_program (checked_lowering): Inline invariant becomes the exact imported invariant resource with translated locations.
- selected_company → complete_claims (checked_embedding): CompleteClaims wraps selected-company lowering and binds an independently supplied selection and population declaration.
- nested_contract → term_event (checked_dependency): execute_sources compiles the contract and executes all selected event rules using the same state/coverage call.
- term_event → selected_company (no_direct_embedding): Selected-company rule grammar consumes flat eligibility and scalar/ordered recipes; no term-event source dispatcher or SelectedTermCommand/2 branch exists in the inspected runner. A new adapter requires explicit state, coverage, carry/report and selection mapping.
- historical_core0 → method (no_implicit_migration): Historical Core 0 debt IR and current method records have distinct schemas/owners; the inspected compiler accepts its named method profile only.

## Remaining complete interface

The term-event source runner already lowers and executes complete assessment, amendment, collection and carry commands. Its historical harness supplies their ordered program, current state, independent selection, population and calls. The selected-company source path does not directly admit that nested term rule family. A generic relabel or event injection would lose structural/semantic coverage and carry constraints.

The smallest complete next deliverable is an explicit selected-term program envelope over this existing executor: exact source/resource identities, ordered requests and independently bound opening/coverage/selection; full successful prefix and first-refusal result; declared carry/report boundary. It must not regenerate selections or silently accept changed source. Reuse the two retained complete traces as comparators and include refusal, replay, resource and boundary controls. This defines one missing composition interface, not a new accounting method or a general whole-company compiler.

The modern transitive dependency bundle remains open. Before promoting a packaged interface, relocate its pure consumers and pin all imported modules and protected source resources. No archival verifier should be rerun.
