# Integrated uncertainty operations — proposed contract v1

This specification completes the operation layer above uncertainty admission,
joint-measure attachment and history-family construction. It addresses MC08–MC14,
MC18, MC25, MC27 and MC33–MC35, principally G1, G6, G15 and G16. Its finite examples
are authored assumptions. They establish neither company probabilities nor an
accounting treatment. Product implementation and independent acceptance remain
pending. The initial profile and all fourteen P15 decisions remain open.

## 1. Question, evidence and default audit

Can a retained family support conditioning, new evidence and conditional outcomes
without invented weights, repeated information or discarded unresolved regions?
The baseline is the proposed admission U1–U6, attachment v2 A–F and history H1–H7
contracts. Core 0's uncertainty section and chapter 5's finite-model derivation
are mathematical design evidence, not approved product behavior. This document
extends their operation semantics; earlier supplements' deferrals describe their
historical scope. Their unchanged records and failure examples remain applicable.

The pass criterion for this bounded task is a coherent specified exchange and
independently recomputable finite examples, with preserved identities and failure
receipts. Invalid arithmetic, lost dependencies or contradictory state assertions
veto this document's internal check and trigger repair. Missing empirical support
vetoes an empirical claim, not continued specification. Checker counts and example
coverage are explanatory only. No stochastic experiment or architecture ranking
is performed. Results are retained in uncertainty-fixtures-v1.json and the P16
result note with fresh check records. Stop after this group; accounting is next.

| Choice and provenance | Reason; misleading failure | Early diagnostic; status |
| --- | --- | --- |
| Optional law, MC12 and attachment B | Facts and feasible alternatives need not have weights; uniform branch weights would invent information. | Unweighted fixture forbids aggregate mean/quantile; proposed invariant. |
| Immutable linked records, evidence/time/history contracts | Corrections must preserve earlier answers; pointer substitution would leak later evidence. | Parent hashes and explicit cutoff checks; provisional representation choice. |
| Exact finite rational examples, approved plan | Independently check normalization; finite success could be mistaken for continuous inference. | Fractions recomputation plus unsupported point-conditioning example; fixture convenience only. |
| Observation blocks, chapter 5 and extraction identity rules | Capture reused information; different files or IDs could disguise one observation. | Repetition, components, alternative extraction and correction examples; proposed invariant. |
| Dependence declared, never inferred from absence of links | Multiplying factors requires a conditional model; unjustified independence overstates information. | Unknown overlap rejects independent multiplication; proposed invariant. |
| Preserve every requested region, history H4 and chapter 5 | Solver failure is not an economic outcome; successful-only means would change the question. | Partial mass and explicit completion-condition examples; proposed invariant. |

Skeptical audit: the comparison fixes semantic inputs; neither prior prototypes,
branch counts nor execution success define the baseline or promotion rule. There
is no runtime/environment comparison. Continuous inference and causal evaluation
remain explicit capability limits, not evidence against those research directions.

## 2. Exchange, identities and validation

An immutable `UncertaintyRequest` has `request_id`, `version`, `predecessor`,
`operation`, `family_ref`, `view_ref`, `attachment_ref` (explicit null if absent),
`model_ref` (explicit null if unweighted), `time_ref`, `evidence_view_ref`,
`admission_ref`, `purpose`, `information_cutoff`, `evidence_cutoff`, `query`,
`dependencies` and `provenance`. References bind exact `id@version` records;
payload changes require a new version or identity. Time mode, publication and
byte-vintage eligibility follow T1–T3; a new observation can produce a later
view only with an explicit new time/admission record. Frozen earlier views remain
queryable. Source occurrence, semantic assertion, interpretation, observation
block and likelihood factor have separate identities.

The query declares the operation-specific condition, evidence update or outcome
selection, including scenario/path/date and typed quantities. Dependencies include
the transitive closure of all typed record references, including assumptions,
review selection, law, accounting method and source lineage. An empty selection
never means all. Outcome labels such as `a` are domain members, not record keys.
The fixture registry is self-contained: it instantiates this exchange without
silently importing the predecessor fixtures' registry. File references pin source
contracts by SHA-256; they do not count as observation blocks.

`UncertaintyResult` retains request identity, old/proposed view, disposition,
reason codes, support and preserved records, unresolved obligations, future
dependencies, `family_effect`, payload, and separate statuses:

* `structural_validity`: valid/invalid;
* `mathematical_status`: satisfied/failed/undefined/unresolved;
* `empirical_justification`: stipulated/not_established/supported_for_named_scope;
* `capability_status`: specified_only_no_runtime/unsupported;
* `computation_status`: specified_exact/specified_partial/symbolic/not_computed.

Fixture computations are expected outputs, never runtime success claims.
Accounting validity and human acceptance are separate fields, neither inferred
from mathematical status. Successful derivation creates a candidate child view;
it preserves the parent and changes no active view pointer. Admission/selection
is a separate explicit operation. Rejection stores submitted bytes and a receipt
but creates no child view, posterior, aggregate result or partial domain write.
`state_before` and `state_after` name the same selected family/view/attachment
and parent hashes on rejection. Receipt storage itself is not a domain update.
Retrying identical request bytes returns the same logical receipt; a reused
identity with different bytes fails `IDENTITY_CONFLICT`. Actual atomic storage,
crash recovery and concurrency are obligations for the later persistence contract.

| Validation stage | Invalid or unresolved condition | Disposition and consequence |
| --- | --- | --- |
| Envelope/registry | Missing field, scalar where reference array required, identity collision, unresolved reference | REQUEST_INVALID; record exact field/reference and preserve submission. |
| Binding/admission | Wrong family/view/model, event outside domain, incompatible unit/purpose, missing dependency, inadmissible cutoff | REQUEST_INVALID; no substitution of nearest/newest record. |
| Law/event | Missing masses, negative/nonfinite mass, nonunit total, unresolved measurability | Invalid laws fail mathematics; unresolved obligations remain symbolic; no computed probability. |
| Evidence reuse | Repeated information, unmodeled overlap, correction applied atop superseded evidence | REQUEST_INVALID with the specific reuse code; old law retained. |
| Normalization | Zero denominator/normalizer | UNDEFINED; undefined mathematics, no posterior. |
| Capability | No admitted law, unavailable evaluator, continuous point without conditional model | UNSUPPORTED or RETAINED_SYMBOLIC; preserve feasible family and expressions. |
| Outcome coverage | Unsupported method, numerical failure, unexplored domain | PARTIAL; retain region and mass/unknown mass, never silently condition on completion. |

These stages reuse the saved attachment/malformed supplements. Error lists are
ordered by stage then record key; later numerical evaluation does not run after
an earlier invalid prerequisite. Preserve all unresolved references in receipts.

## 3. Conditioning and scenarios

An observational condition names an admitted event A, the parent law P, the
information used to define A and its role. For finite elementary outcomes S,
require a measurable A subset of S and P(A)>0. Define

    P_A(s) = P(s) 1{s in A} / P(A),
    P(B | A) = sum_{s in A intersect B} P(s) / P(A).

The numerator sums elementary outcomes once even when display labels overlap.
The child retains S and records zero mass outside A, the event identity,
denominator and parent law. Keeping zero-mass members distinguishes the declared
domain from its positive-mass support. Reapplying A is mathematically idempotent;
it records no new information factor. If A came from observation block D, the
child's consumed-information set includes D and its semantic lineage, preventing
subsequent likelihood multiplication by the same information. A hard constraint
already used to construct the family is likewise consumed, even if it did not
appear as a numerical likelihood. Evidence used to fit a prior/model is declared
in that model's training/calibration lineage for the same check.

With masses a=1/2, b=1/3, c=1/6, A={a,b}, B={b,c}, the denominator is 5/6,
intersection mass is 1/3, and P(B|A)=2/5. The conditional masses are (3/5,2/5,0).
P(A)=0 returns `ZERO_CONDITION_MASS` and no child; an empty feasible subset in
an unweighted family is instead scoped infeasibility. An unweighted nonempty
restriction yields a feasible subset with `probability=null`, not a distribution.

An exogenous stress changes a declared driver/scenario while retaining history
weights unless an explicit observation model says that observing the scenario
provides information. Its result is labeled scenario-assumed, not P(.|observed
scenario). A structural intervention requires a causal model, modified equations,
intervened variables and an identification/validation argument; `do(X=x)` is
never lowered to filtering `X=x`. This proposal retains such requests as
unsupported until a declared evaluator and its evidence are supplied in P17.

For continuous/mixed laws, event conditioning uses the same measure formula when
the event has positive mass and the evaluator is supported. A continuous point
event of zero mass requires an explicit regular conditional kernel/version (or
justified reduced parameterization) with the conditioning variable, base measure,
support and chosen version at the queried point. A density value is not the
probability of that point. No epsilon window or Gaussian penalty is invented.
General existence, uniqueness at null points and numerical evaluation remain
method obligations; symbolic expressions may be retained without a numeric answer.

## 4. Evidence updates and information reuse

An `ObservationBlock` records its immutable identity, purpose, observed values and
full financial context, source occurrences and assertion/reading references,
`information_atoms`, relations (`same_information`, `component_of`, `derived_from`,
`supersedes`), availability/time view, admission and dependencies. Information atoms
name semantic observations, not bytes: a duplicated PDF, a new extraction or a
repeated table entry does not automatically supply new information. Where semantic
equivalence cannot be decided, overlap is `unknown`; new IDs alone cannot prove
independence. No general automatic duplicate detector is claimed.

A `LikelihoodModel` records target family/coordinates, law purpose, observation
block(s), base measure for observed data, conditional arguments, parameter version,
units, support, consumed information and justification. Its output is a
nonnegative measurable L(s). For discrete observations L is a probability of the
specified observation; for continuous observations it can be a density and may
exceed one. Extraction confidence, expert preference and solver success are not
likelihoods. A finite update requires finite nonnegative values on all S and

    Z = sum_s P(s)L(s) > 0;    P_new(s) = P(s)L(s)/Z.

The result records unnormalized masses, Z, the complete posterior including zeros,
new consumed-information set and parent view. With P=(1/2,1/3,1/6) and
L=(1/2,1,0), unnormalized masses are (1/4,1/3,0), Z=7/12 and posterior
(3/7,4/7,0). If Z=0, return `ZERO_NORMALIZER`; do not substitute equal weights or
silently broaden support. A later observation inconsistent with every positive-mass
history calls for an explicit model/family revision, not an invisible numerical fix.

Two observation blocks can enter one joint likelihood L(D1,D2|s). Sequential
updating must use L(D2|D1,s); replacing this by L(D2|s) requires an explicit
conditional-independence assumption with target-specific justification. Different
information atoms are necessary bookkeeping, not a proof of independence. A
dependent conditional model may legitimately reuse D1 as a conditioning argument;
it must name D1 as already consumed and add only D2 as incremental information.
Unknown dependence blocks the independent-factor route while retaining the blocks
for a later joint model. Marginal likelihood tables alone do not define the joint
likelihood.

| Submission | Required result |
| --- | --- |
| Same immutable request/bytes | Idempotent receipt lookup, no second child or factor. |
| New request, same source occurrence/information block | `DUPLICATE_INFORMATION`; preserve prior posterior. |
| Total plus all its components as independent factors | `DERIVED_INFORMATION_REUSE`; one joint block or an explicit conditional model is required. A deterministic total adds no independent information beyond all components. |
| Alternative extraction of one source span | `ALTERNATE_READING_NOT_NEW_OBSERVATION`; resolve/branch the reading under admission U rules. A new noisy measurement model must be explicitly justified if intended. |
| Potentially overlapping blocks with unknown relation | `DEPENDENCE_UNRESOLVED`; no independent update. |
| Corrected reading multiplied into an old posterior | `CORRECTION_REQUIRES_REBASE`; retract/supersede in a new evidence view and recompute from a retained base preceding the affected block. |

A correction supplies the superseded block, corrected block, base view and the
ordered retained incremental updates to replay. Validate that none of the old
block's descendants survives without revalidation. Recompute from the base with
the corrected likelihood and any still-admissible downstream conditional factors.
Do not divide by the old likelihood: it may be zero and its support restriction
may already have removed alternatives. The old posterior, evidence view and
receipt remain unchanged. The illustrative corrected L=(1,1/2,1) on the original
P gives Z=5/6 and (3/5,1/5,1/5). This is a newly specified view, not historical
knowledge rewritten in place. Full crash-safe replay is a persistence obligation.

## 5. Conditional outcome payloads

A query selects exact family/view, condition, scenario, path set, dates, accounting
methods and output quantities. Each row key is `(history_ref, condition_ref,
scenario_ref, path_ref, date)`. Cells carry entity/perimeter, concept, dimensions,
currency/unit/scale/sign, instant or interval and measurement basis, together with
state/journal/report references, assumptions and dependencies. A joint statement
vector shares its path and state references; marginals from incompatible histories
cannot be recombined into a synthetic balance sheet. Expected statements need not
describe any admissible history and remain summaries, not journal postings.

Cell status is `exact`, `symbolic`, `sampled`, `certified_bound`, `explored_range`
or `unresolved`. Exact means exact under the declared model and inputs. Sampled
requires sampler/seed/stream, weighting and uncertainty metadata; it is not exact.
Certified bounds require a cited proof/certificate, domain and endpoint semantics;
explored ranges describe only visited regions. Symbolic values retain expression,
domain and unresolved dependencies. No computational tag asserts accounting
eligibility or empirical forecast validity.

For weighted finite reporting, allocate every elementary outcome once to a
disjoint partition `completed`, `unsupported`, `numerical_failure`,
`solver_unknown`, `cancelled` or `unexplored`. Coverage masses total one (or the
explicit parent event mass for an unnormalized subquery); unknown mass stays
unknown and prevents a false exact total. Economic default is an economic-state
flag orthogonal to this partition: a fully computed default belongs to completed;
an unsupported default branch can remain unresolved. Report default mass separately
with its overlap with completion so it is never added twice. Default retains legal
obligations and usable state. Stop only affected descendants when a required method
is unsupported, retaining independent quantities through their dependencies.

Suppose a,b have exact expense 10,20 and c's valuation is unsupported. Under
P=(1/2,1/3,1/6), completed mass is 5/6, unresolved mass 1/6 and the completed
unnormalized contribution is 35/3. The unconditional mean and quantiles are
unresolved; 35/3 is not the mean of the full outcome. A separately requested
`condition_on_completion` query reports event {a,b}, denominator 5/6 and mean 14.
Its labels state that this is a computational selection, not an economic forecast
condition or evidence update. This view cannot silently feed back into historical
probabilities. Partial values may support bounds only with explicit bounds for
the missing region; a missing value is neither zero nor default.

When history weights are absent, retain the feasible set and separate within-history
future laws K(h,scenario) if available. No uniform averaging across histories.
Without a within-history law retain a deterministic/symbolic feasible outcome set.
A complete finite set {10,20,30} has exact range [10,30] but no mean or quantile.
If only {10,20} was explored and c is unresolved, [10,20] is merely an explored
range and cannot become a full-family bound. Even when every K is valid, an
envelope of their quantiles is not a predictive distribution. An optional history
law plus a measurable kernel defines a mixture; discrete reporting sums disjoint
history/innovation atoms, and continuous mixtures require a supported integrator.

## 6. Interactions, alternatives and acceptance boundary

Evidence supplies contextual assertions and observation lineage; time determines
admissible information; admission separates the six uncertainty categories. History
families supply compatible joint states, scope, residual regions and refinement
maps. Accounting consumes a history/scenario/path and returns typed states and
journals with eligibility status; uncertainty never makes an unsupported treatment
admissible by giving it positive probability. Language/IR must type conditions,
measures, units, model purpose and requested aggregation; implicit casts from sets
to distributions are forbidden. Interfaces expose denominators, unresolved mass,
view lineage and evidence reuse receipts. Persistence retains immutable requests,
models and child derivations with resumable frontiers; failure semantics propagate
dependency-scoped unknowns. These are requirements on unfinished counterpart
contracts, not evidence that they are complete.

The two credible storage alternatives are a law linked to a family registry and
a self-contained joint model carrying its definitions. Compare them with identical
S, typed assignments, masses, evidence blocks, cutoffs, parent lineage and queries.
Under a bijection f of elementary outcomes require equal assignments and
P_embedded(x)=P_linked(f(x)); also preserve event sets, likelihood values and consumed
information. Finite conditioning and normalization then have equal sums by a change
of index. Registry links simplify shared revisions but require dependency closure;
self-contained packages simplify portable inspection but risk copied evidence being
counted twice. Both must retain semantic observation identities. A paired fixture
specifies the same conditional and posterior values in both forms; no throughput,
memory, empirical or general continuous-equivalence conclusion follows.

The provisional preference is explicit immutable shared identities with a
self-contained export containing the same identities and definitions. It follows
from traceable revisions and reuse, not from prototype convenience. Ownership and
initial-profile selection remain open. Weighted and unweighted reporting answer
different questions and are not competing estimators to rank on these examples.
Single joint likelihood and conditional sequential factorization are both credible
when their models match; naive multiplication is valid only under the stated
conditional independence. Correction by replay is chosen over division because
zero likelihoods make division lose recoverable histories.

This group is ready for independent substantive review when the full exchange,
fixtures and internal arithmetic/reference checks agree. Its finite capability
boundary is specified; continuous/mixed inference, causal identification,
calibration and empirical validation remain P17 obligations. Accounting, language,
persistence, interfaces, failure semantics, integrated profile/acceptance order,
E05 source conflict and full MC01–MC35/G1–G18 reconciliation remain open. Neither a
successful checker nor this candidate contract enables product implementation.
