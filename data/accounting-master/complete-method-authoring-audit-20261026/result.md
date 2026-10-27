# Full method authoring audit: preserve the v2 state-growth baseline

26 October 2026. Four complete retained definitions were inventoried: payment
and claim-creating sale across alpha and beta charts. Existing prepare validation
passes. The field inventories contain 369, 373, 440 and 440 leaves; those counts
are coverage diagnostics, not correctness evidence. Original source hashes are
recorded in inventory.json. No financial result was rerun in this audit.

The complete method has profile/id/version/context, account_map, preconditions,
monetary, memory, postconditions and residual_prerequisites. Preconditions and
postconditions each have a guarded manifest and account/event/memory bindings.
Monetary effects have input declarations, calculations, account types, postings,
gross flows and bindings. Memory effects bind schema identities, ordered writes
and input sources. These fields must all survive authoring; a function expression
or imported registry alone does not supply the method.

Reuse: existing versioned requirement text supplies guarded predicates;
MethodMonetaryEffects/1 supplies financial expression semantics; memory staging
and CompanyBookTransition/1–2 supply write, account, type and atomicity checks.
The method-level frontend should add declarations and source locations, then
delegate semantic compilation to these exact owners. No new evaluator is needed.

Critical audit correction: the original v1 accepts fixed scalar replacements,
while the v2 successor supports typed map insertion and adds memory_definition
to its request. Both still carry CompanyBookMethod/1. The frontend must select
the transition profile explicitly and preserve that external memory-type
definition, or it would exclude the already implemented identified-claim case.

| Decision | Primary criterion | Veto | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Add a bounded complete-method frontend | Every method field and semantic owner located; v1/v2 distinction explicit | No new language evaluator or loss of state-growth support | Syntax usefulness and general method coverage | Author full definitions and compare complete native results/refusals | General all-sector DSL or source/accounting eligibility |

No continuation veto fired. Input schemas, book/event imports and v2 typed memory
definitions remain explicitly supplied data; authoring a method does not author
or authenticate those sources. Plan and grammar must state that boundary.
