# Results, incomplete work and failures, proposed version 1

A missing source, an insolvent company and a crashed solver are different
outcomes. Combining them into “failed” would either lose admissible histories or
publish results with stronger meaning than the evidence permits. This contract
addresses MC08–MC14, MC18, MC25 and MC33–MC35 and integrates the existing
uncertainty and accounting status rules.

## F1. Independent result dimensions

Once submission retention succeeds, every public operation returns an
`OperationResult` bound to its submitted bytes, validated request when available
and input snapshot. It contains a disposition, status envelope, typed payload,
diagnostics, unresolved obligations, domain coverage, nullable continuation and
commit observation. Disposition is one of `completed`, `partial`, `rejected`,
`unsupported`, `cancelled`, `internal_failure`, `commit_unknown` or `replayed`.
It is not an accounting conclusion. Successful completion within a declared
scope does not imply that scope describes every real history or disclosure.
Failure of submission retention itself follows I1's out-of-band transport-failure
rule and asserts neither a retained submission nor a known commit outcome.

The existing uncertainty envelope remains normative: structural validity,
mathematical status, computation status, empirical justification, capability
status, accounting validity and human acceptance have separate fields. An adapter preserves
the exact domain-native vocabulary in the payload; it does not invent a Boolean
“passed” from them. In particular, a pre-evaluation rejection uses
`structural_validity=invalid`, `mathematical_status=unresolved` and
`computation_status=not_computed`, as the rejection-status supplement requires.
Mathematical status cannot be `not_computed`. Empirical/capability/accounting/
human fields are copied from the governing operation evidence in their native
vocabulary, never assumed accepted.

For new platform envelopes, structural validity is `valid` or `invalid`;
mathematical status is `defined`, `failed`, `undefined`, `unresolved`, `infeasible` or
`not_applicable`; computation status is `complete`, `partial`, `not_computed`,
`cancelled` or `failed`. Domain-native subreceipts keep their own named schema
and vocabulary. The platform does not rewrite historical receipts to these
labels: its explicit versioned adapter maps their stated meaning. New platform
envelopes additionally retain `empirical_justification`, `capability_status`,
`accounting_validity`, `forecast_validity`, `product_readiness` and
`human_acceptance`. The first three copy a supported native value or use
`not_established`, `specified_only_no_runtime`, `not_assessed` respectively;
the last three are `not_assessed`, `not_implemented`, `pending` in these examples.
No map turns `specified_exact` into a claim of runtime execution: evidence mode
remains `specification_example`. The explicit mappings and unsupported cases
are in architecture-integration-v1.md.

Mathematical `infeasible` requires established emptiness of the declared model;
solver silence gives `unresolved`. Conditioning on a zero-probability event
under the specified finite law is `undefined`, even if computing its zero
normalizer completed successfully. A feasible symbolic family may have a
partial search. An economically defined default event is an outcome of a
successfully evaluated scenario when its default method is supported; it is not
a solver failure. A positive balance check establishes none of the accounting,
forecast, product or human acceptance fields.

## F2. Diagnostic and rejection order

`Diagnostic` has code, stage, record Ref or submitted-byte Ref, source locator,
field path, affected query/branch IDs, dependency path, observed value/category,
expected rule, retry advice and blocking diagnostic IDs. No fabricated numeric
substitute appears in place of an unavailable observation. Diagnostic prose
explains a typed code but cannot supply missing economic facts.

For new portable-only operations the stages are decode; field shape; reference integrity; cross-record
binding/context/time admission; capability/admission; requested calculation;
transaction comparison; publication. An operation may refine these stages,
but cannot reverse a required domain ordering. Existing native accounting uses
parse → recognizable dependencies → shape → source versions → bindings, as
specified in the field-validation supplement. For accounting, all specified
source field/binding checks precede receipt lookup; lookup precedes new-event
freshness and treatment calculation. Retried historical requests use their
pinned historical context, not today's review view. Domain profiles identify
which preconditions are checked before lookup and which only for a new event.

Return all independently decidable diagnostics within the earliest failed stage,
sorted by schema-defined stage rank, canonical field path and code. Later stages
are explicitly not evaluated. A malformed parent/controller suppresses its
dependent child predicates; it does not suppress independent sibling findings.
This incorporates the guarded C03/C05/C07/C09/C10 reason rules without turning
an unknown route into false or promoting contextual prose into evidence.
Invalid requests return no candidate result that could be used as admitted
output. Retained submitted bytes and separate audit receipts remain available.

## F3. Preserve the requested domain

Every aggregate identifies the full requested family/view/scenario domain and
partitions its work into completed, unresolved, unsupported, infeasible and
cancelled regions. Regions are predicates with identities and coverage relations,
not just counts. Overlap is explicitly represented or removed under a proven
partition; unexplored formulas remain available. A partial result states which
queries depend on unresolved regions and which are unaffected. “No completed
regions” is not an empty family.

With an admitted joint law, retain assigned mass for all regions, including
unsupported or failed evaluations. Do not renormalize successful regions.
Example FX01 assigns mass 3/5 to a path returning cash 120 and 2/5 to a path
whose calculation is unavailable. The returned known cash mass is 3/5 and
unresolved mass 2/5; neither mean 120 nor a complete cash distribution is
authorized. If the unresolved path has independently established cash bounds
[80,110], the unconditional mean is bounded by [104,116]; without those bounds
even that interval is unsupported. Computing a conditional mean given successful
evaluation is a different estimand and requires an explicitly requested,
meaningful conditioning event; computational success is not economic evidence.

Without an admitted law, return joint feasible regions or per-history conditional
results, never weights derived from witness/branch counts. Interval endpoints
from partial exploration are explored-only. An exact bound must identify the
full formula, proof/certificate or checked exact method, endpoint attainability
and numerical policy. A supremum of 1 for x<1 is not an attained maximum.
Approximate bounds retain method, error description and missing coverage.

## F4. Retry, cancellation and integrity

Retry advice distinguishes `same_request_after_service_recovery`,
`inspect_commit_then_retry_same_identity`, `new_request_after_input_repair`,
`new_model_or_capability_required` and `no_automatic_retry`. A model-input repair
gets a new fingerprint; it cannot reuse an existing business-event key to hide
a conflict. Availability failures preserve input and work checkpoints; an
unknown commit must first be reconciled under its original identity.

Caller cancellation stops new work at the next interruptible boundary and
returns the last committed checkpoint. Already committed events are not rolled
back by a cancelled response. Cancellation during a storage call may yield
unknown commit observation until recovery. A callback that cannot be interrupted
requires an external resource limit and a recoverable process boundary; a
cooperative progress report is not proof that a commit did or did not occur.

A mismatched required digest, invalid dependency cycle, corrupted committed
record or inconsistent checkpoint is an integrity veto on affected use. Preserve
the invalid bytes and report the mismatch. Do not resume, fabricate replacement
evidence or relabel the error as financial infeasibility. An unrelated corrupt
source does not block a query whose complete dependency closure excludes it.

FX02–FX07 specify zero conditioning mass, unsupported nonlinear bounds, economic
default, a timed-out worker, malformed source fields and unknown commit. They
make both allowed and forbidden conclusions explicit. The checks are finite
examples of the proposed semantics; accounting authority, empirical forecast
quality and production recovery remain separate evidence obligations.

## F5. Alternatives

A single success flag is simpler to transmit but conflates mathematical meaning,
computation, admission and acceptance. Throwing an exception for every partial
branch loses useful unaffected results and encourages selection bias. The
proposed typed result plus diagnostics preserves partial work while making
invalid or unsupported calculations unusable as complete results. Exceptions
may still signal implementation faults internally, but the public boundary
must retain the submitted identity, commit uncertainty and last durable work.
