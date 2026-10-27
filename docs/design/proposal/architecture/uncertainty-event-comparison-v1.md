# Overlapping events and projection: paired finite examples v1

The design question is whether a family-linked measure and a self-contained joint model preserve overlapping events and elementary history identity under projection. This supplement addresses MC12/G15 and interactions with MC08, MC10, MC14, MC18 and MC25. It extends the saved MA02a comparison without revising it. The semantic comparator is the provisional attachment v2 contract and its MA03a/MA04b fixtures. Historical prototype behavior is not normative. Both representations remain candidates.

## Evidence contract and stopping rule

Each pair uses the same family, view, coordinates, assignments, law, event meaning, evidence, purpose, admission and two cutoffs. Only ownership and encoding identities change. The pass criterion is exact correspondence of those inputs, independently derived finite probabilities and the specified receipt fields. A mismatched hash, unavailable claimed dependency, non-bijective identity binding, changed assignment or selector, omitted projection preimage, or changed admission is a validity veto and repair trigger. A failed example rejects that example's specification until repaired; it does not reject the research direction. Dependency counts and duplication of stored fields explain engineering tradeoffs only. Neither probability arithmetic nor structural check counts select the initial profile.

The output is a document, two paired requests/expected receipts, and a one-off authored-fixture diagnostic. Stop after these examples and partial registration. Detailed stale/malformed/partition/projection rejection comparisons and later uncertainty operations remain separate work. No runtime correctness, general representational equivalence, performance, accounting validity, empirical forecast validity or human acceptance follows from a pass.

| Choice | Provenance and justification | Possible misleading result | Early diagnostic | Status |
| --- | --- | --- | --- | --- |
| Finite rational masses | MA03a/MA04b; exact sums isolate representation errors | Synthetic masses mistaken for estimated probabilities | Recompute each arm with Fraction; check empirical status separately | Synthetic convenience |
| Local identifiers | Saved MA02a ownership convention; separates encoding from meaning | Equal labels collapse distinct histories | Injective and surjective outcome binding plus assignments | Design hypothesis |
| Bijective family binding | Finite reindexing argument in saved comparison | Mapping hides lost outcomes or changed coordinates | Compare complete domains, ranges and coordinate definitions | Provisional invariant for these finite examples |
| Many-to-one rate projection | MA04b; exposes loss of region | Projected display replaces the joint history | Full preimage and lost-coordinate checks; unchanged family/view | Provisional display convention |
| Exact file/version pins | Prior specification fixtures; inspectable availability | Local files mistaken for production persistence | Resolve every declared dependency and record ID | Document-verification convenience |
| Common admission and cutoffs | MC10/MC12 and supplied records | Numerically valid law presented as empirical authority | Separate receipt fields and equal support provenance | Required boundary |

Pre-execution skeptical audit: the baseline and inputs are matched; no stochastic ranking, timing comparison, training defaults or environment-dependent runtime is involved. The smallest useful diagnostic is independent finite evaluation plus a separate identity/receipt check. Missing later operations cannot be hidden by a successful subset. The audit passes for this bounded task, with attachment v2 explicitly provisional. Standard-library-only verification avoids numerical-environment changes.

## Pinned inputs

These are local specification evidence, not external accounting or empirical authority. The failure supplement is a prerequisite boundary, not a substitute for the rejection comparison still to be written.

- `docs/design/proposal/architecture/uncertainty-representation-comparison-v1.md`; SHA-256 `43a82d4921b2a94b7a10ec76f09aabe2c2d87a3cd86c9d187446c9caa89483a1`; Shared semantic boundary; both representations; correspondence.
- `docs/design/proposal/architecture/uncertainty-representation-fixtures-v1.json`; SHA-256 `f335fa35527fb809579cbf2b8f5b0e96461690d1ef3b33b215dd4d11672935ba`; /pairs/0: MA02a ownership convention.
- `docs/design/proposal/architecture/uncertainty-measure-attachment-contract-v2.md`; SHA-256 `3812e0f1f28f8bd77fbbd38f1b9b79810346a42ed47a42532b95d9aeb4a5a0b3`; Sections A–F: provisional finite law and events.
- `docs/design/proposal/architecture/uncertainty-measure-attachment-fixtures-v2.json`; SHA-256 `20c24b2d4d0627476537fb242401249b6726b29928a371e1c930c42e4e0306ee`; /groups/2/cases/0 MA03a; /groups/3/cases/1 MA04b; /records.
- `docs/design/proposal/architecture/uncertainty-measure-failures-contract-v1.md`; SHA-256 `b38ac18c92953b048776eb7c25dc2e8de26371582e5ecb0048fc3c0a7d98610a`; Ordered validation and complete receipts.
- `docs/design/proposal/architecture/uncertainty-measure-failures-fixtures-v1.json`; SHA-256 `a4370e6ca6079439a24a9664b8a6dc91ddf15bda4f9ba3a4af425fb1b22c2235`; /records; /controls; /cases.
- `docs/design/proposal/architecture/uncertainty-measure-failures-consistency-v1.json`; SHA-256 `544692ac2d742274ac9ce6ebe012a8fd2a2af10780d2d42cd4d60bdab8c3ffa3`; /input_hashes; retained prerequisite diagnostic.

## MA03a: overlapping events

The common family has three elementary outcomes: a=(region A, rate 1), b=(B,2), c=(C,3), with masses 1/2, 1/3 and 1/6. Event A selects {a,b}; event B selects {b,c}. Names of events and region labels are separate identifiers: event A includes region B through outcome b. The family-linked request resolves `event:A@1` and `event:B@1` against `model:tri@1`. The owned request embeds local events and binds them to those exact semantic event identities through `family_mapping.event_map`. Its local outcomes bind bijectively to `tri:a@1`, `tri:b@1`, `tri:c@1`; full coordinate definitions and assignments accompany the masses.

| Quantity | Selected elementary outcomes | Exact probability |
| --- | --- | --- |
| A | a,b | 1/2 + 1/3 = 5/6 |
| B | b,c | 1/3 + 1/6 = 1/2 |
| A intersection B | b | 1/3 |
| A union B | a,b,c | 1 |

Adding P(A)+P(B) gives 4/3 because it counts b twice. Subtracting P(A intersection B) restores the union probability: 5/6 + 1/2 - 1/3 = 1. Thus these named events are not disjoint partition cells and cannot be used as such. No probability normalization or history deletion repairs that category error. A partition-rejection receipt is deferred to the next comparison task.

Both specified receipts are EVALUATED with no reason codes, unchanged family and view, and the four structured probability observations above. The scalar `probability` stays null because the request asks for several results. The fixture retains separate structural validity, mathematical satisfaction, attached-assumption, empirical-not-established and specified-only/no-runtime statuses. Concrete dependencies and expected receipts are in `uncertainty-event-fixtures-v1.json`, pair `EC_MA03a`.

## MA04b: a projected value retains two histories

This example uses the separate `family:projection@1` and `model:projection@1`. Its elementary outcomes are `proj:a@1`=(region A, rate 1) and `proj:b@1`=(region B, rate 1), each with mass 1/2. Projection keeps rate and drops region. The complete preimage of the displayed value rate=1 is {proj:a@1, proj:b@1}, so its projected probability is 1/2 + 1/2 = 1. The region coordinate is explicitly recorded as lost in this display; neither history loses its region assignment in the underlying model.

The owned request embeds the two full assignments, two masses, local coordinate definitions and a local projection event. Its local-to-family outcome map is bijective. The rate projection is many-to-one. These are different maps with different obligations: the binding preserves semantic identity, while projection aggregates masses over preimages. Substituting the projected singleton for the elementary sample space would lose the region distinction and is wrong relative to the stated joint-history target.

Both requests therefore leave their family and view unchanged. The receipts retain `PROJECTION_COLLISION_RETAINED`, the projected mass one, and both elementary outcome identities (local IDs in the owned receipt, family IDs in the linked receipt). The scalar probability stays null; the structured observations describe the projected distribution and retained identities. The explicit source/target coordinate lists, lost coordinate, full mapping and selector are saved in `EC_MA04b`. No downstream accounting equality across regions is assumed.

## Receipt correspondence and ownership

Every baseline receipt field is accounted for below. Encoding translations are explicit fixture maps, not implicit equality of identifiers. Version is one throughout; all records and references are exact versions.

| Receipt fields | Correspondence rule |
| --- | --- |
| result_id, request_ref | Each request/result has a distinct encoding ID; append @version to result_id before translating to the baseline |
| version, operation, old_view, proposed_view | Equal directly; no new family view is introduced |
| disposition, reason_codes | EVALUATED; MA03a empty reasons, MA04b retains PROJECTION_COLLISION_RETAINED |
| structural_validity, attachment_status, mathematical_status, mathematical_obligations | valid, attached_assumption, satisfied, empty obligations; none implies empirical validity |
| empirical_justification, capability_status, computation_status | not_established, specified_only_no_runtime, evaluated |
| unresolved_obligations, next_permissible_operations, future_dependencies | Equal to baseline: no local unresolved item; evaluate_event only; conditioning, likelihood_update and conditional_outcomes remain dependencies |
| family_effect, probability | unchanged; null for both structured queries |
| attachment_ref | Linked request uses the existing baseline attachment; owned request carries a separately identified attachment with the same purpose, evidence and admission status, bound to its local model and mapping |
| observations | MA03a rational values equal directly; MA04b projected probabilities equal, while elementary IDs translate through the bijection |
| support_references | Same evidence, time, justification, admission, family/view and coordinate validation dependencies. Owned model, events and attachment replace corresponding numerical records; the binding record is additional structural support |
| preserved_records | Each preserves its request and support. Owned request also preserves all external comparator records as audit dependencies, plus its embedded model, events, attachment and binding |
| additional owned fields | joint_model_ref and mapping_ref identify structural ownership; audit_references identify external comparator model/events/attachment. They supply no new empirical evidence |

Event ownership follows model ownership: linked events are external versioned records tied to the common model/family/view; owned events carry local selectors and an explicit map to those semantic event identities. The owned attachment is supplied as a prior admitted-assumption record in this evaluation example, not inferred merely from normalized masses. Its binding/admission must still resolve externally. These fixtures specify the state required for evaluation; they do not implement attachment creation.

A linked request requires the exact external dependency closure to be available. An owned model can numerically sum its embedded law and events without that closure, but cannot issue the full family-bound/admitted receipt without validating its external binding and admission. Here baseline model/events/attachment also remain available for comparison audit. Neither representation is credited with offline admission or a different information set. A pinned exported registry can address linked availability; validating embedded definitions and maps can address owned synchronization. An external revision cannot silently overwrite either request's pinned versions. Detailed unavailable/stale/rejected receipts remain the next task.

The finite reindexing argument in the saved representation comparison applies to these bijective bindings: summing the mass of local preimages yields the same event probability. The projection itself need not be invertible; its complete preimages carry the projected masses. These two examples check that distinction concretely and do not establish a general implementation theorem, a continuous/mixed model, or an architecture preference.

## Verification and remaining decisions

The one-off document diagnostic independently derives event sets and probabilities from each representation before comparing its expected observations. It separately checks file pins, dependency availability, coordinate definitions, assignments, bijections, selectors, projection preimages and receipt dimensions. The exact command, hashes, observed values, failures and limits are retained in `uncertainty-event-verification-v1.json`. These checks examine authored fixtures; they do not execute a product evaluator or certify prose completeness.

The next bounded comparison concerns stale available dependencies, malformed inputs and partition/projection rejection receipts. Later uncertainty work still includes conditioning, duplicate-evidence protection, likelihood updates and conditional outcomes. Six contracts, initial-profile selection, integrated acceptance criteria, dependency order and fourteen decisions remain unresolved. E05 source limitations and P17 authority/research/real-company obligations remain visible; all MC01–MC35/G1–G18 retain their wider scope. Independent P16 review and human acceptance are pending.
