# Available versions and stale measure bindings

This bounded P16 proposal supplement addresses MA05c: an event request selects
model v2 while its admitted attachment and event still name v1. Both model
versions exist and have identical numerical definitions. The comparison covers
MC12/G15 and its MC08, MC10, MC14, MC18 and MC25 interactions. It selects neither
architecture. Product implementation and human acceptance remain pending.

## Question, evidence contract and stop

Can both a family-linked model and a self-contained numerical model reject this
incompatible request without losing the valid old law? Attachment contract v2,
its exact MA05c fixture, the prerequisite-failure supplement, and the earlier
representation/event comparisons are the provisional specification baseline.
Their paths, SHA-256 hashes and locators are pinned in the companion fixture's
`source_evidence`. Historical prototypes are not normative behavior.

The primary pass criterion is matching version-binding decisions and complete,
separately qualified expected receipts in the two encodings. A valid control
requests v1 while v2 remains available and must specify probability 5/6. The
matched failure requests v2 without changing its old attachment/event. Missing
records, changed laws, incomplete declarations, nonbijective maps, altered
admission or unsupported receipt correspondence invalidate the comparison and
require repair; they are not evidence against either architecture. Unit-mass
checks are numerical prerequisites. The equality of the two laws is explanatory
only: it isolates version policy, not authority to migrate. No empirical,
performance, accounting, general-equivalence or production-readiness claim
follows. The saved fixtures and verification JSON preserve the result.

Research intent: the mechanism under examination is explicit immutable binding;
the expected failure is MODEL_VERSION_STALE despite successful prerequisite
resolution. A mismatch in the authored receipts triggers repair of this example.
Invalid source pins or unresolved prerequisites veto continuing the comparison
until fixed. A stale candidate's rejection is the intended result, not a reason
to abandon the architecture investigation. Stop after these two pairs and their
checks. Malformed inputs and remaining rejection families are the next task.

## Defaults and skeptical audit

| Choice and provenance | Justification and status | Failure mode | Early diagnostic |
|---|---|---|---|
| Exact versions; attachment v2 and failure-order supplement | Provisional design invariant preserving admission history | Replacing an explicit old version with the latest version | Resolve both versions and inspect the old-version control |
| Masses 1/2, 1/3, 1/6; MA05c | Synthetic convenience example, tractable exact arithmetic | Numerical equality mistaken for empirical justification or rebinding permission | Fraction totals and version comparisons kept separate |
| Bijective local-to-family mapping; representation v1 | Provisional finite comparator, preserves elementary histories | Coordinate/outcome relabeling conceals a different law | Check assignments, units, order, masses and both bijections |
| Shared evidence, cutoffs and admission; MA03a | Matched baseline boundary | Copied model treated as independent evidence | Compare external support and admission fields |
| Resolve declarations before binding, then evaluate | Proposed precedence inherited from failure supplement | Missing v1 declaration masks the stale-model case | Compute transitive closure independently |
| Same complete available registry in both cases | Convenience control for version availability | Newer version alone treated as invalidation | Only request selection changes within each representation |

The skeptical audit passes for this bounded question: baselines are matched,
stop conditions explicit, no proxy selects an architecture, no runtime or
hardware comparison is claimed, and all intended checks use the existing Python
standard library. The baseline's two omissions are amended explicitly below.

## Valid control and stale request

The companion JSON contains concrete inputs and expected receipts for
`SC01_old_version_control` and `SC02_MA05c_stale`. In both, model:tri@1 and
model:tri@2 remain available with outcomes a, b, c, assignments (A,1), (B,2),
(C,3), and masses 1/2, 1/3, 1/6. Event A selects a and b. The valid request names
v1, attachment:tri@1 and event:A@1, giving 1/2 + 1/3 = 5/6. Availability of v2
creates no implicit request to change the law.

The failure changes only the selected model to v2, plus request identity and
encoding-required mapping selection. Both versions are declared in both cases,
so prerequisite resolution cannot substitute for the intended binding check.
The old attachment and event continue to identify v1. Equality of mass tables
does not change these references or supply an admission decision for v2.

| Semantic identity | Family-linked form | Owned numerical form |
|---|---|---|
| Old/new model | model:tri@1 / model:tri@2 | joint-model:stale-owned@1 / @2 |
| Old/new family binding | Model family/view references | mapping:stale-owned-to-family@1 / @2 |
| Preserved attachment | attachment:tri@1 | attachment:stale-owned@1, bound to local model/map v1 |
| Preserved event | event:A@1 | local-event:stale-A@1, bound to local model v1 |
| Family and current view | family:tri@1, view:tri@1 | Same external records |

The owned request contains both immutable numerical models and both versioned
maps in local registries. This is an explicit envelope extension of the earlier
single-model example, not a runtime feature. Each map resolves to its own local
model and exact semantic model version; the maps preserve coordinate and outcome
bijections to the unchanged family. `event_correspondence` compares the old event
to its old semantic counterpart independently of the selected mapping: selecting
map v2 does not rebind that event. Local numerical availability still does not
supply external family admission, provenance or time authority.

For linked input, the selected model disagrees with the attachment's model and
with the event's model. For owned input the same two disagreements occur, plus
the selected mapping differs from the old attachment's mapping. This third
mismatch encodes the same stale binding, not a third scientific failure. Each
attachment remains consistent with its own old map/model. The new map remains
consistent with v2; there is no malformed mapping or changed support.

## Validation and receipt correspondence

First validate immutable identities and the request envelope. Resolve direct
references, then every declared dependency and their transitive closure. Only
then check bindings. Return MODEL_VERSION_STALE at this binding stage before
attempting event evaluation. Neither a mass sum nor the valid old selector
licenses evaluating the incompatible request. The specification does not promise
a general invalidation graph or transactional persistence.

| Receipt field | Control | Stale request |
|---|---|---|
| disposition | EVALUATED | RETAINED_ONLY |
| structural_validity | valid | invalid for the requested binding |
| mathematical_status | satisfied | unresolved for the requested computation |
| attachment_status | attached_assumption | attached_assumption for preserved v1 |
| computation_status; probability | evaluated; 5/6 | not_computed; null |
| empirical_justification | not_established | not_established |
| capability_status | specified_only_no_runtime | specified_only_no_runtime |
| old_view; proposed_view | view:tri@1; view:tri@1 | view:tri@1; view:tri@1 |
| family_effect | unchanged | old_view_preserved |
| reason_codes | empty | MODEL_VERSION_STALE |
| next_permissible_operations | evaluate_event | revise_request, attach_measure |
| future_dependencies | model_migration | model_migration |

The old law independently still has nonnegative masses totaling one. That fact
is recorded as a document-diagnostic observation, not as mathematical success
of the rejected request. Expected receipts preserve the submitted request, all
available dependencies, the old attachment/event and both model versions.
Owned receipts additionally retain both local models, maps and event/attachment
records. Encoding translations identify corresponding model/event/attachment
records; mapping records are additional structural support. Numerical,
admission and comparison-audit dependencies are listed separately; audit copies
provide no new evidence. Every receipt field is classified for comparison in
`receipt_correspondence`, including identities, support, observations and the
owned-only model/mapping fields.

MA05c's original declaration omits transitive model:tri@1 although the referenced
attachment and event require it. This supplement explicitly declares v1 and v2.
Its original receipt also asks for migration review while listing no future
dependency. These new receipts include `model_migration` in future_dependencies.
This is a deliberate specification amendment, recorded in `baseline_amendments`;
the preserved comparator is not rewritten. Migration is deferred and unavailable,
never a current operation or an implemented repair. A revised request may target
the already admitted v1; attaching a different version requires its own explicit
review. No migration result is fabricated.

## Acceptance boundary

A standard-library diagnostic independently resolves both encodings, checks
closure, pins, bijections and exact arithmetic, derives mismatches from the
inputs, and compares receipt dimensions. Expected receipts remain specified
behavior rather than product responses. The registered checker assesses proposal
structure only. Independent substantive review is still required. Six contracts,
the initial profile, integrated acceptance/dependency order and fourteen decisions
remain unresolved; all MC01–MC35/G1–G18 obligations, E05 source limits and P17
research/authority/real-company obligations remain active.
