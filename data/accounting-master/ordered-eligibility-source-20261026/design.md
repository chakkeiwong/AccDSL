# Direct source for ordered eligibility

26 October 2026. Active plan: docs/plans/accounting-ordered-eligibility-source-20261026.md. MC20/24/25/33/34; S3/S4.

## Question and skeptical audit

Can an author state every selected eligibility stage, full input type, binding and guarded predicate directly, obtaining exactly the existing typed gate and its complete results? The comparator is the six protected OrderedEventEligibility/1 templates and the saved 38 eligible and 34 refused cases, not a second hand-written eligibility implementation. Source lowering, contextual compilation and event evaluation are distinct. Counts are explanatory; complete equality is the pass criterion.

The audit passes with two safeguards: a semantic error may identify a whole stage, and that span must say so; a canonical hash cannot represent declaration-map insertion order, so source identity and semantic identity remain separate. No changed gate semantics, arbitrary rule equivalence, wider language completeness, accounting compliance or independent acceptance is inferred. A failed implementation case triggers repair; changed protected evidence, unavailable comparator or ambiguous target stops this unit until repaired.

## Closed grammar

One declaration per nonblank line, terminated by a semicolon. Existing strict JSON literals are retained for context, types, reference lists and constants. Algorithms and binding expressions are source declarations, never whole-template JSON or callbacks.

    ordered_eligibility "OrderedEligibilityText/1" "OrderedEventEligibility/1" "collect";
    context CONTEXT_JSON;
    full_input "name" TYPE_JSON;
    residual "text";
    stage "id" "failure reason";
    bind "input" (event_input "name");
    begin_rules "MethodRequirements/3" "method_id" "version";
    input / guarded / required_known / capability / residual declarations;
    end_rules;
    end_stage;
    end_eligibility;

Binding prefix expressions are exactly: event_input(name), event_metadata(id or date), book_date(), period_end(), memory_leaf(pointer), map_contains(pointer,key_input), map_field(pointer,key_input,field,prior_stage), and calendar_adjacent(left,right), written with parentheses and space-separated JSON strings. A row field needs the gate compiler's earlier unconditional membership proof for the same map/key. Every stage is compiled, including skipped stages and stages over empty maps.

Nested rules reuse MethodRequirements/3 declarations and expression parsing. Lowering computes identities; authors do not maintain selection digests. Context and stage order are explicit. Duplicate/missing declarations, unknown bindings and unbound inputs are refused.

## Locations and resource bounds

UTF-8 byte offsets are half-open and measured in the original source, including CRLF. Token errors identify their token; missing tokens identify a zero-width insertion position. Semantic errors identify a named declaration, stage or document span, with that granularity stated. Never present a whole-stage error as an exact offending token. The original tokenizer remains the lexical authority.

Use the existing 1 MB source bound, 4096 nonblank declarations, expression/binding depth and node bounds, and 64-stage bound. Their provenance is the reused parser/gate, and their status is an engineering compatibility choice, not a scientific optimum. An early boundary probe checks each. Whitespace/CRLF changes source identity but preserves lowered semantics.

## Evidence and next action

Save six sources, roundtrips, complete replay results, meaningful predicate/order edits, malformed-source and skipped-stage controls, UTF-8/CRLF location checks, protected hashes, command/environment manifest and result note. Disable native lifecycle functions while replaying. Run CPU-only deterministic checks; no stochastic or performance ranking. A pass supports this selected grammar only. After this unit, proceed to opening-stage source, parameter/row recipes and complete selected-company source. E3 remains deferred.
