# Finite joint-model representation comparison v1

This bounded design comparison addresses MC12/G15 and its MC08, MC10, MC14,
MC18 and MC25 interactions. The question is whether two ownership arrangements
can preserve the same finite attachment semantics: a measure linked to a
history family, and a model that carries its numerical definitions with it.
The comparator is the provisional attachment v2 specification, not the existing
prototype and not an approved architecture. Neither alternative is selected by
this document. All fourteen P15 decisions and the wider mission remain open.

The stopping condition is explicit definitions and one paired MA02a attachment
example, checked as a document. Overlap (MA03a), projection (MA04b), and detailed
rejection examples are subsequent work. This document specifies behavior;
there is no attachment runtime, transaction test, empirical model fit or
accounting-authority decision here.

## Shared semantic boundary

A finite model has an ordered list of typed coordinates, an elementary sample
space S with the full set of subsets as its event algebra, assignments of
coordinate values to every elementary outcome, and a mass function m on all of
S. The finite-law obligations are distinct IDs, complete assignments and mass
coverage, m(s) >= 0, and sum(m(s)) = 1. Explicit zero-mass outcomes remain in S.
The attached law also binds the exact family and view versions, declared
purpose, dependence, support restrictions, evidence and information cutoffs,
provenance and admission. A mass table never implies independence.

Encoding identity names a particular request, receipt or stored model.
Semantic identity names the family/view, coordinates and elementary outcomes
whose meaning must survive translation. Changing packaging gives a new
encoding identity; it does not create a new source, a new admissible history,
a probability estimate, or permission to use an accounting treatment.

For MA02a the outcome map is a bijection f from local embedded outcomes to the
family outcomes. Equality of the mapped assignments and masses is sufficient
for equality of every finite event probability: for any subset E of S,
sum over u in f^(-1)(E) of m_embedded(u) equals sum over s in E of m_linked(s).
This follows by substituting s=f(u), with exactly one u for each s. This is a
finite reindexing argument, not a proof of general representation equivalence
or of correctness for continuous, mixed or lossy projected spaces.

## Family-linked representation

The request carries exact family_ref, view_ref and model_ref IDs with versions.
Its declared coordinates, space, masses, purpose and dependence must agree
with the immutable external model; the model's space and coordinates must
agree with the referenced history family. The family owns assignments and
coordinate references. The coordinate records own entity, perimeter, concept,
dimensions, units, time, domain and type. The view identifies a particular
family version. The model owns the declared law, evaluator designation and
justification references. Redundant request fields are assertions to validate,
not overrides. No reference may float to a newer version.

The fixture provides exact path/hash/JSON-pointer locators for every required
external record. Resolving these locators is part of this design example's
availability check. A production identity service, content encoding and
resolver protocol remain to be designed under MC25. Missing bytes prevent
current evaluation; they do not invalidate an old receipt that accurately
records an earlier successful resolution. Export can mitigate this dependency
by shipping a pinned closure of referenced records. That export remains a
family-linked model with a bundled registry, not a different probability law.

## Self-contained joint-model representation

The request owns a versioned joint_model definition: immutable local coordinate
IDs and full coordinate definitions, their order, local elementary outcomes,
complete assignments, event algebra, masses, dependence, support restrictions,
purpose, cutoffs, provenance, justification and evaluator designation. Numeric
interpretation of this finite model needs no external family/model lookup.
The model is a new encoding, with its own immutable ID and version.

A separate versioned family_mapping binds this model to an exact family/view
and semantic model identity. It maps every local coordinate and outcome to a
semantic ID. For this example the mapping is total and bijective and preserves
coordinate definitions and assignments. It is an identity-preserving binding,
not a lossy projection. A future many-to-one projection needs its own explicit
semantics; it cannot silently replace this binding. The fixture gives actual
local IDs and definitions, not a pointer to the family-linked request.

“Self-contained” applies only to the numerical model. The source evidence,
justification, time view, category admission and family admission remain
external. Attaching to the family requires resolving the target family/view
and mapping; numerical inspectability alone does not establish admission.
The mapping also pins the comparator's model record to make this comparison
reconstructible. That comparator reference is an equivalence-audit dependency,
not a dependency needed merely to sum the embedded masses. No accounting
authority is supplied by this synthetic example; any future accounting use
requires separately identified authority and accounting checks.

Changing embedded definitions creates a new joint-model version and requires
revalidating the mapping. Source corrections likewise require explicit review
and a new mapping/admission decision where applicable. A copied definition
cannot follow a family revision automatically. Immutable digests, explicit
mapping versions and dependency invalidation mitigate drift; their persistence
implementation is still unspecified.

## Correspondence and interactions

| Concern | Family-linked input | Self-contained input | Required equality or boundary |
| --- | --- | --- | --- |
| Coordinates and assignments | External family and coordinate records | Owned coordinate definitions and assignments | All type/unit/entity/perimeter/time/domain fields and values match after mapping |
| Space, law, dependence | Request assertions plus external model | Owned local space and mass table | Same semantic outcomes, event algebra, masses, restrictions and dependence |
| Family/view binding | Direct exact references | Exact target references plus versioned mapping | Same family/view bytes; attachment appends a measure and changes no histories |
| Purpose and cutoffs | Request/model/time references | Model fields plus external time record | Scenario purpose and both cutoffs identical; no later evidence introduced |
| Evidence and admission | External provenance, justification and admission | Same external records | Synthetic assumption status retained; copying creates no evidence |
| Receipt | Request/attachment encoding IDs plus semantic result | Different request/attachment/model IDs plus explicit semantic correspondence | Same disposition, validity, obligations, capability, computation and future dependencies |
| Ownership and closure | External registry owns definitions | Model owns numerical definitions; family and authority remain external | Local availability and permission to attach are separately checked |
| Failure behavior | Reject mismatched redundant fields; unresolved unavailable references | Reject incomplete or inconsistent mapping/copy; unresolved external admission | Preserve submitted bytes and the old admitted law; never discard/renormalize mass |

Histories supply the family meaning in both alternatives; time supplies the
cutoffs and source vintage. Language/IR must encode exact versions and mapping
direction without interpreting display labels as outcome IDs. Persistence
must preserve bytes, mappings, dependency roles and receipts atomically and
track invalidation. Interfaces must show synthetic status, purpose, cutoffs
and unresolved obligations, and distinguish numerical inspection from admitted
attachment. Accounting receives a scenario assumption, not accounting approval.
Failure semantics must separate invalid input, missing prerequisites,
unsupported evaluation and computation failure. Detailed receipts for stale
available dependencies, malformed requests, partitions and projections are
explicitly deferred; neither representation has passed these cases here.

## Matched example and interpretation

The companion JSON supplies separate complete requests and expected receipts
for MA02a. The family-linked form retains tri:a@1, tri:b@1 and tri:c@1, with
(region, rate) assignments (A,1), (B,2), (C,3). The self-contained form owns
local outcome IDs and maps them one-to-one to those same outcomes. Their
respective masses are 1/2, 1/3 and 1/6. The common family is family:tri@1 and
the common view is view:tri@1, both unchanged by attachment.

The total is 3/6 + 2/6 + 1/6 = 1. All masses are nonnegative and every declared
outcome has a mass. These arithmetic properties support the specified finite
law only. Both receipts say ATTACHED_ASSUMPTION, empirical_justification =
not_established, and capability_status = specified_only_no_runtime.
The expected computation_status validated_attachment describes the proposed
operation; it does not say software performed it. Probability remains null
because attachment does not itself request an event evaluation.
Conditioning, likelihood_update and conditional_outcomes remain separate future
dependencies in both receipts. No receipt claims these operations are available.

## Assumption audit and decision boundary

| Material choice | Provenance and justification | Failure mode | Early diagnostic | Status |
| --- | --- | --- | --- | --- |
| Attachment v2 as comparator | Approved bounded plan; fixes a common semantic target | Inherited omissions mistaken for whole-product completeness | Record deferred overlap/projection/rejection and later operations | Provisional baseline |
| Rational finite masses | MA02a; exact finite arithmetic is inspectable | Arithmetic validity mistaken for empirical support | Fraction sum plus separate status checks | Synthetic diagnostic convention |
| Local IDs and bijection | New author encoding for a fair owned-model example | Labels or equal values collapse distinct outcomes | Check injectivity, surjectivity and assignments after mapping | Design hypothesis; finite example only |
| Fully owned numerical definitions | Credible export-oriented alternative | Embedded bytes drift from admitted family | Compare all coordinate fields, space and assignments to pinned target | Design hypothesis |
| Exact external versions | Prior evidence/history/time contracts | Unavailable or revised dependencies silently substituted | Pin hashes and resolve closure; defer adversarial stale case | Proposed invariant; resolver unimplemented |
| Pinned file locators | Existing JSON fixture convention | Local accessibility mistaken for network persistence/recovery | Check actual files and record IDs; state missing runtime | Convenience for document verification |
| Common external admission | MC10/MC12 and supplied synthetic admission | A standalone numerical model treated as authority | Verify identical category and empirical status | Required semantic boundary |

The skeptical pre-execution audit found no material objection to this narrow
comparison: inputs are matched; no timing, usability or empirical ranking is
planned; missing broader cases cannot be hidden by check counts. Author checks
must parse both encodings, verify pinned availability and mapping, derive exact
mass properties and compare receipt dimensions separately. The result is saved
in uncertainty-representation-verification-v1.json. A structural check can
still fail because six whole-product contracts remain unfinished.

Both representations remain candidates. Family linkage makes reuse of shared
history definitions explicit but requires available references. Ownership makes
the finite model inspectable in isolation but adds mapping and revision duties.
A pinned registry bundle and a validated mapping are credible respective
mitigations; neither has been evaluated as a production implementation. The
next task is MA03a overlap and MA04b projection, before rejection cases and later
uncertainty operations. Initial-profile choice and full independent P16 review
remain pending, as do source, accounting, empirical and human acceptance.

## Pinned inspected inputs

The following are local specification evidence, not external accounting or
empirical authority. Hashes bind the inspected versions; locators identify the
support used. Prior verification is retained evidence, not a new acceptance.

- `docs/design/proposal/architecture/uncertainty-measure-attachment-contract-v2.md`; SHA-256 `3812e0f1f28f8bd77fbbd38f1b9b79810346a42ed47a42532b95d9aeb4a5a0b3`; Sections A–F; provisional alternatives in E.
- `docs/design/proposal/architecture/uncertainty-measure-attachment-fixtures-v2.json`; SHA-256 `20c24b2d4d0627476537fb242401249b6726b29928a371e1c930c42e4e0306ee`; /groups/1/cases/0 (MA02a), /records; exact record keys take precedence over array position.
- `docs/design/proposal/architecture/uncertainty-measure-failures-contract-v1.md`; SHA-256 `b38ac18c92953b048776eb7c25dc2e8de26371582e5ecb0048fc3c0a7d98610a`; Ordered validation, complete receipts and five discriminating examples.
- `docs/design/proposal/architecture/uncertainty-measure-failures-fixtures-v1.json`; SHA-256 `a4370e6ca6079439a24a9664b8a6dc91ddf15bda4f9ba3a4af425fb1b22c2235`; /cases MF01–MF05; /controls; /records.
- `docs/design/proposal/architecture/uncertainty-measure-failures-consistency-v1.json`; SHA-256 `544692ac2d742274ac9ce6ebe012a8fd2a2af10780d2d42cd4d60bdab8c3ffa3`; /checks; /input_hashes; 266 saved passing author checks.
