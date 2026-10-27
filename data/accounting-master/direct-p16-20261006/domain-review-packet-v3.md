READ-ONLY P16 SUBSTANTIVE REVIEW. Codex executes; do not edit, run shell/network, or launch agents. Read/Glob/Grep are available. Review the following actual draft contracts and inspect exact references as needed. Product implementation is disabled. These are governing design specifications, not evidence of runtime conformance. P17 source/accounting/sector method obligations, the E05 real conflict and a complete real-package case remain proposal blockers; do not invent closure, and do not mistake those explicit later tasks for a missing P16 architectural answer.

Find material semantic defects: identity/replay, native status mapping, information/admission loss, math, incomplete-result claims, hidden defaults and omitted bindings. Return concrete findings with file/section, counterexample, smallest repair and whether blocking P16 architecture acceptance. Report inspected scope. End VERDICT: AGREE or VERDICT: REVISE. Check counts are not acceptance evidence: current finite checks are 797 structural, 169 arithmetic, 2580 accounting-exchange assertions and 932 unchanged protected files. Read data/accounting-master/deliverables/P16/architecture.json for current index/decisions (ignore historical bounded-work status as current authority). The active plan is docs/plans/accounting-p16-direct-execution-20261006.md.

FOCUS: Existing evidence/time/history/uncertainty and new result mappings. Inspect active v2 chaining cases/admission/correction to supply the independent uncertainty review.

FILE docs/design/proposal/architecture/uncertainty-contract-v1.md
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


FILE docs/design/proposal/architecture/uncertainty-chaining-contract-v1.md
# Uncertainty operation chaining — proposed supplement v1

This supplement repairs the result-to-request boundary in uncertainty-contract-v1,
sections 2–4, and the UC01, UC02 and UC08 fixtures. Those immutable fixtures
contain correct illustrative masses but their child `model_ref` points to the
original prior. That reference is wrong as the governing law for a subsequent
query. The mappings in uncertainty-chaining-fixtures-v1.json replace that meaning
for this proposal; the original records remain historical evidence. No product
implementation or independent acceptance is claimed.

## 1. Bounded question and evidence contract

Can a specified uncertainty result become the next request without reverting to
prior masses, losing consumed information or silently granting admission? The
comparator is attachment v2 A–F and uncertainty admission U3: exact immutable
bindings, explicit selection and preserved parents. This task addresses MC12,
MC14, MC25, MC27, MC33–MC35, with MC08/G6/G15 interactions. It does not select
the initial profile, accounting policy, persistence engine or inference method.

Pass requires consistent complete bundles, an explicit admission boundary, exact
finite chained arithmetic and rejection receipts preserving domain state.
A mismatched law/view/attachment, repeated information or broken reference vetoes
internal consistency and requires repair. Structural checker counts explain
coverage only. There is no empirical comparison, stochastic ranking, accounting
eligibility finding or runtime transaction claim. Stop after these specifications
and bounded checks; independent uncertainty review is next, before accounting.

| Choice and provenance | Rationale and failure mode | Early diagnostic; status |
| --- | --- | --- |
| Immutable derived law, attachment B | Separate provenance from the law actually used; otherwise later queries use prior masses. | Consume UC02's output and reject an original-law substitution; provisional representation. |
| Separate admission/selection, uncertainty section 2 and admission U3 | A calculated candidate is not permission to use it in an admitted analysis. | Candidate-only request fails; admission receipt names exact bundle; proposed invariant. |
| Full finite space, attachment B.2 | A zero-mass outcome remains identifiable for future correction. | Retain c at zero through ordinary updates and restore it only by rebase; finite example convenience. |
| Stipulated binary observation kernel, uncertainty section 4 | Conditional factors require a joint model; distinct atoms alone do not justify independence. | Recompute sequential and joint posteriors; hypothetical model, no calibration claim. |

Skeptical audit passed for this bounded document repair: fixed semantic baseline,
explicit stop, no proxy promotion, no runtime/environment comparison and no
transfer of prototype defaults. Both representation alternatives below must
answer the same chained question. Five counterpart contracts, all fourteen open
decisions, the integrated initial profile and all wider mission obligations remain.

## 2. Complete derivation bundle

A successful weighted condition/update emits an immutable bundle containing:

* a child view with exact family, coordinate, time and evidence references,
  parent view, operation request, `model_ref` for its governing derived law,
  candidate attachment, consumed atoms and assumption-condition identities;
* a derived law with the same child view/family/ordered coordinates/purpose,
  full sample space, every mass including zero, parent law and `base_model_ref`;
* a candidate attachment binding that child and law, with status
  `candidate_not_admitted`, plus the input admission used to justify derivation;
* operation lineage naming parent, condition or likelihood/observation records,
  normalizer, unnormalized masses, incremental/conditioning atoms and applicable
  corrected/superseded records; and
* a result receipt naming all created records, payload and separate structural,
  mathematical, empirical, capability, accounting and human-acceptance statuses.

`base_model_ref` is origin/provenance, never an instruction to evaluate with the
base law. `parent_model_ref` identifies the immediate mathematical input;
`model_ref` identifies the law governing the child. A request's view, law and
attachment must agree on exact identities, not merely numerical masses. The
view's displayed masses, receipt posterior and governing-law masses must agree.
All typed references resolve; dependencies include their transitive closure.
Mutual view/law references are identity links, not recursive content hashes;
each registry record is hashed as canonical JSON separately.

For P on S and nonnegative factor f, the lineage stores w(s)=P(s)f(s),
Z=sum w(s)>0 and Q(s)=w(s)/Z. A condition uses f=1_A. Zero Z produces no bundle.
Consumed observations are the union of parent consumed atoms and the new
incremental atoms. Assumption conditions have separate semantic identities;
conditioning on an authored scenario does not itself consume a measurement.
If a condition represents observed information, its atom must instead be recorded
and protected against later likelihood reuse. Calibration atoms of the base law
remain in the information audit even if absent from the view's incremental list.

Output creation never changes the selected pointer. The receipt's domain writes
are exactly the new view/law/candidate attachment/lineage records; a stored receipt
is an audit write. Candidate presence alone never grants admission. Unsupported
continuous/mixed operations keep their symbolic obligations and do not manufacture
finite bundles. Unweighted results continue under the earlier feasible-set rules.

## 3. Admission and the next request

`admit_derived_bundle` takes the exact candidate/result, intended time/evidence
view and purpose, requested assumption scope, named reviewer/decision authority,
rationale and the expected selection revision. It verifies bundle closure,
normalization, binding, input admissibility, information lineage and complete
support. It returns an immutable admission decision, an admitted attachment
binding the same child/law, and a receipt. The candidate attachment is retained.
Neither law nor view is mutated to change its status. For these synthetic
fixtures the decision authority is the fixture author and the only admissible
status is `admitted_as_authored_assumption`; this is not accounting, empirical or
independent approval. Real authority and review policy remain caller obligations.

A separate `select_admitted_view` names that receipt and attachment, the expected
current selection revision and rationale. It returns a new selection revision
and receipt. Admission alone leaves the selected pointer unchanged. Explicit
queries may name any still-admissible frozen view without changing selection;
requests for the current view must match the current revision. Corrections record
supersession/reuse status in new records, preserving frozen historical queries.
A concurrent/stale selection revision rejects with `STALE_BASE_VIEW`.

The next probability request must name the child's governing law, admitted
attachment and admission receipt, with matching purpose/time/evidence scope.
A candidate-only attachment fails `ADMISSION_REQUIRED`; old prior-law or
parent-attachment substitutions fail `LAW_VIEW_ATTACHMENT_MISMATCH` before
arithmetic. No fallback to an earlier admission or newest record is permitted.
An admission decision missing authority/rationale or unsupported in its requested
scope fails `ADMISSION_INVALID`. Failed admission, selection or update creates
no domain records and leaves selection, admitted attachment and parent hashes
unchanged; only submitted bytes and the rejection receipt may be stored.
Request-identity retries retain the existing idempotence/conflict rules.
These are specified postconditions; persistence atomicity remains unimplemented.

## 4. Chaining and correction examples

UC02 has P=(1/2,1/3,1/6) and P(D=1|s)=(1/2,1,0). Its actual saved payload gives
Z_D=7/12 and Q_D=(3/7,4/7,0). The mapping copies that payload into a repaired
bundle, then explicitly admits and selects it. The next request refers to that
bundle, not to the separately authored UC.posterior fixture.

Specify binary E with P(E=1|D=1,s)=(1,1/2,1) and
P(E=1|D=0,s)=(1/4,1/4,1/4). Complements define the other outcomes. This kernel,
together with P(D=1|s), defines a coherent joint distribution of (D,E) for every
s. The E|D=1 value at c is a stipulated kernel value on a zero-probability D
branch; it does not restore c's posterior mass. No conditional independence is
assumed. The E update adds only measurement.E, retaining D as consumed and as a
conditional argument. The unnormalized masses are (3/7,2/7,0), Z_E|D=5/7 and
Q_D,E=(3/5,2/5,0). Direct joint weighting gives (1/4,1/6,0), Z_D,E=5/12 and the
same answer. Reusing D as an incremental observation rejects, even under a new
request ID. E's distinct atom alone would not suffice without the declared kernel.

UC01's condition A={a,b} yields (3/5,2/5,0) and P(B|A)=2/5 for B={b,c}.
After admission, repeating A uses a newly bound event record with the original
semantic condition identity and the child's exact view/law. Its denominator is
one and masses are unchanged. The second request is a new derivation receipt;
mathematical idempotence does not equate record identities. The same semantic
condition is stored once. A repeated request ID is separately receipt-idempotent.
The original event cannot be silently rebound. Equal member sets alone do not
prove equal semantic conditions across changed coordinates or evidence.

UC08's corrected likelihood (1,1/2,1) must apply to the unaffected original
prior, giving Z=5/6 and (3/5,1/5,1/5). The repaired mapping names the actual UC02
child as superseded and creates an explicit revised evidence/time/admission view.
The corrected block supersedes D's reading while retaining semantic atom D. It
replaces D once; it is not an extra independent observation. The old posterior
and its admission stay readable in their frozen scope, and their current-reuse
status is superseded in the new evidence view. The mapping's replay list is
explicitly empty. If the D,E descendant is present, it is invalid for current
reuse until the conditional E model is revalidated under corrected D and replayed;
this example does not silently reuse it. Correction can restore c because its
unaffected prior mass is positive; an ordinary update of Q_D cannot do so.

## 5. Representation alternatives and review boundary

The explicit bundle materializes masses and lets the next request inspect its
exact law. A lazy parent-plus-transformation law can avoid duplication, but must
have its own immutable law identity, child binding, complete dependency closure,
normalizer and consumed information. Its evaluator must resolve to exactly the
same measure and reject missing/stale inputs. A provenance pointer to P alone
is neither alternative. The fixtures compare both mathematical evaluations on
identical inputs, without performance or storage claims. Explicit materialization
is provisional here because it makes the boundary reviewable, not because it
has been shown superior. General lazy evaluators remain unspecified.

The mapping table and exact chains are proposed examples. Internal calculations
and structural checks cannot establish software behavior, accounting validity,
empirical forecasting, architecture superiority or human acceptance. Independent
review must inspect this supplement with the retained uncertainty/admission/
attachment contracts; it must not treat the original child references as repaired
in place. P17 still owns continuous/mixed inference, causal methods and calibration.

For a correction, the request's ordinary view/law/attachment/admission fields
bind the frozen mathematical input. The separate `target_time_ref`,
`target_evidence_view_ref` and `target_admission_ref` authorize the revised inputs
and output context. Validate each side against its own context; do not demand
that a newly corrected observation was admitted in the frozen base. All output
view/law/candidate records bind the target context. A submission of the corrected
block as an ordinary incremental update may supply this target authorization;
it still fails `CORRECTION_REQUIRES_REBASE` because D has already been consumed.


FILE docs/design/proposal/architecture/uncertainty-rejection-status-contract-v1.md
# Rejected uncertainty requests — status correction v1

This supplement corrects five specified rejection receipts in
`uncertainty-chaining-fixtures-v1.json`. The independent uncertainty review in
`data/accounting-master/runs/20261005T120206-bdb3a74d/P16/execution-0/review_result-0.response.json`
returned REVISE: its arithmetic agreed, but the receipts assigned `not_computed`
to `mathematical_status`, contrary to uncertainty-contract-v1.md §2. The current
fixtures are `uncertainty-chaining-fixtures-v2.json`. The original files and
records remain evidence of the defect, not active expected rejection outputs.
This proposal correction carries MC08–MC14, MC18, MC25, MC27 and MC33–MC35,
principally G1/G6/G15/G16. It requires independent result review.

## 1. Bounded question and acceptance

Can a consumer interpret all five rejected requests using the existing common
status vocabulary? The comparator is uncertainty-contract-v1.md §2 and the
unchanged chaining v1 requests and rejection consequences. Acceptance of this
slice requires all seven status fields below, exactly five explicit correction
mappings, unambiguous active expected receipts, and preservation of every original
registry record and every successful case. Changed requests, laws, payloads,
masses, normalizers, selected state, parent hashes, audit writes or rejection
reasons veto the correction. Missing reference closure or an active malformed
predecessor also veto it. These are repair triggers; they do not reject the wider
uncertainty research direction. Checker totals explain structural coverage only.

Skeptical audit: the baseline is the declared exchange, not prototype behavior;
no arithmetic reassessment, runtime experiment, statistical ranking or environment
comparison is needed. The same requests and consequences are compared. Stop after
the supplement, versioned fixture, focused preservation report, registered check
and updated P16 records. No accounting design begins in this slice.

The status interpretation is a proposed clarification, with provenance in the
reviewed repair plan and the governing vocabulary. Its risk is that `unresolved`
could be mistaken for permission to continue an invalid request. The decisive
`REQUEST_INVALID` disposition, unchanged reason code, explicit no-computation
status and no-output postconditions prevent that inference. A focused field and
state check is the early diagnostic; independent review decides semantic adequacy.
No new empirical, accounting or mathematical default is selected.

## 2. Common status envelope for pre-evaluation rejection

Request validation decides whether evaluation may proceed. Here it fails before
mathematical evaluation, so each corrected receipt contains:

| Field | Value | Meaning for this request |
| --- | --- | --- |
| `structural_validity` | `invalid` | Request validation failed, including semantic binding/admission/reuse checks. This does not mean the receipt itself is malformed. |
| `mathematical_status` | `unresolved` | The requested calculation was not evaluated. This is no finding that its mathematics is false or undefined. |
| `computation_status` | `not_computed` | Validation stopped evaluation; there is no computed result. |
| `empirical_justification` | `not_established` | The rejection establishes no empirical support. |
| `capability_status` | `specified_only_no_runtime` | This file specifies behavior; it reports no runtime execution. |
| `accounting_validity` | `not_assessed` | Rejection supplies no accounting eligibility judgment. |
| `human_acceptance` | `pending` | Neither fixture consistency nor the prior review establishes human acceptance. |

`disposition="REQUEST_INVALID"` and the existing `reason_codes` remain decisive.
`unresolved` never authorizes use of a result or admission of the request. Reserve
`undefined` for established undefined mathematics, such as the specified zero
normalizer; reserve `failed` for an established mathematical failure. Neither
finding was made for these five invalid requests.

The common envelope was chosen over a separate rejection schema because it uses
the vocabulary already required of consumers and retains one interpretation for
each status field. A separate schema could omit inapplicable mathematical fields,
but would require a new discriminator, consumer branches and explicit migration
rules. That broader change is unnecessary for this defect. This choice does not
settle the later language, interface or persistence design.

## 3. Versioned correction and active selection

The v2 fixture copies all 125 v1 registry records without canonical JSON changes.
It adds exactly five records with the same logical receipt IDs, `version=2`, and
the corresponding `@1` receipt as `predecessor`. The only record changes are
version, predecessor, the corrected/added status fields, correction provenance,
and dependency closure including that predecessor. Requests remain version 1.

| Active case | Corrected receipt | Preserved rejection reason |
| --- | --- | --- |
| `candidate_only` | `CH.rejection.candidate_only@2` | `ADMISSION_REQUIRED` |
| `duplicate_D` | `CH.rejection.duplicate_D@2` | `DUPLICATE_INFORMATION` |
| `stale_law` | `CH.rejection.stale_law@2` | `LAW_VIEW_ATTACHMENT_MISMATCH` |
| `stale_attachment` | `CH.rejection.stale_attachment@2` | `LAW_VIEW_ATTACHMENT_MISMATCH` |
| `correction_on_posterior` | `CH.rejection.correction_on_posterior@2` | `CORRECTION_REQUIRES_REBASE` |

`rejection_status_corrections` is the explicit old-to-new map;
`active_rejection_receipts` and the five `cases[].expected_ref` values agree with
it. The `historical_rejection_receipts` entries mark each predecessor ineligible
as an active expected output. Registry presence alone confers no eligibility.
Consumers of this proposal select the named v2 fixture and its explicit case
references; they must not infer a version by scanning for the latest ID. Successful
case references, bundles, admissions and representation alternatives are unchanged.

This is a revision of authored specification examples, not a runtime replay or
an exception to request idempotency. No runtime receipt has been overwritten or
reissued. A future runtime implementing a fixed specification must still return
the same logical receipt for identical request bytes; operational migration and
historical replay rules remain obligations of the unfinished persistence contract.

## 4. Unchanged rejection consequences and retained evidence

Every corrected receipt retains its request reference, exact reasons, selected
family/view/attachment/model snapshots, selection revision and parent hashes.
`state_before == state_after`, `domain_writes=[]`, the audit writes remain
`submitted_bytes` and `rejection_receipt`, and both `proposed_view_ref` and the
output `model_ref` remain null. No posterior, aggregate result or candidate view
is created. Corrected provenance identifies the pinned predecessor file and
terminal review; it is not a new observation or likelihood factor.

The current focused diagnostic is preserved in `uncertainty-rejection-status-check-v2.json`
with its command and input hashes; the fresh registered result and execution
record use `uncertainty-rejection-status-structural-check-v1.json` and
`uncertainty-rejection-status-structural-execution-v1.json`. Their actual outcomes
are recorded in P16/result.md. They test specification consistency, not runtime
enforcement. Five counterpart contracts, the integrated initial profile and
dependency order, fourteen open decisions, P17 methods, E05 and all wider mission
obligations remain. Accounting validity, empirical forecast validity, product
readiness and human acceptance remain unestablished.

Diagnostic correction: the first check treated the frozen `perimeter` value
`single_entity@1` as a registry reference solely because it contained `@1`.
It is a scope label in these fixtures; the v2 diagnostic excludes that field
from registry-reference traversal. The failed v1 report and checker source are
preserved. This changes no request or specified receipt. General perimeter
representation remains outside this bounded repair.


FILE docs/design/proposal/architecture/architecture-integration-v1.md
# Integration of the nine proposed contracts

The active contract list in P16 architecture.json is the document index. This
supplement resolves interactions among those contracts without altering earlier
evidence or treating saved fixture outcomes as executed product behavior. It
addresses MC02–MC14, MC18–MC27 and MC33–MC35. The baseline is the five existing
P16 contracts and their accepted amendments; Core 0/P03/P07 are investigated
prototypes, not automatic defaults.

## Meaning carried between contracts

| Boundary | Meaning that must survive | Rejection or unresolved consequence |
| --- | --- | --- |
| Evidence → time | Original bytes, source occurrence, review layer, economic/reporting/publication/ingestion clocks | Missing clocks cannot support stronger historical-knowledge claims |
| Evidence/time → history | Scoped admitted interpretation/assumption, joint symbols, conflicts and exclusions | Faithful reading alone cannot become an admitted accounting constraint |
| History → uncertainty | Full family/view, partition, dependence and query-relevant economic memory | No weights from witness counts; missing law gives a symbolic/unweighted result |
| Scenario/history → accounting | Branch opening, exact event identity, date/context, permitted information and eligible method | Unresolved or unsupported treatment produces no posting |
| Accounting → persistence | Validated request, source/method versions, proposal/delta and expected head | Exact replay before freshness; all-or-none transition; unknown commit reconciled under original identity |
| Calculation → report | Common history/scenario index, native statuses, unresolved regions/mass and unit/time semantics | No successful-subset renormalization or independent selection of line extrema |
| Correction → all descendants | Immutable old view, replacement scope, candidate-set membership and transitive dependency | Current reuse invalidated even for descendants created after the correction |
| Any contract → IR/interface | Versioned type, lineage and admission requirements | Unknown schema or required semantics cannot be ignored or coerced |

## Explicit amendments and precedence

L1's portable encoding applies only to new portable records. Existing native
record digests, original files, source byte hashes and receipts stay unchanged.
Integer metadata remains integer; financial quantities use exact rationals.
There is no global NFC normalization. A named legacy import retains both IDs
and checked decoded correspondence. Source-map identity is separate from model
identity, so formatting changes do not alter a model's financial meaning.

P2 resolves the early accounting contract's ambiguous “event/version” language:
the stable lookup key excludes version and payload. A correction uses a new
business-event identity with an explicit treatment/lineage; merely changing a
version under an existing key conflicts. Branch identity includes an explicit
projection namespace, distinguishing separately requested hypotheticals from
retries of the same projection. No double counting of hypothetical projections
is permitted when reporting realized transactions.

Native accounting retains its established validation order and assess-only
boundary. New portable wrappers validate their own envelopes and then delegate
to that native order. Dependency recognition is guarded by reference shape;
malformed refs are not followed. A shape error cannot be masked by finding an
old receipt. Output defects are distinguished from ineligible economic events:
reject publication as ASSESSMENT_OUTPUT_INVALID while retaining the validated
request and diagnostic candidate. All four committed accounting domains remain
unchanged for assess-only, rejection and replay.

Uncertainty fixture v2 rejection receipts supersede only their explicitly named
v1 predecessors. Their valid requests, joint laws, calculation payloads and
unchanged successes remain evidence. Derived law/view bundles require separate
admission and selection; a numerical posterior does not admit itself. No
platform wrapper changes an existing domain's status values in place.

## Status mapping at the new platform boundary

The native uncertainty schema has seven distinct statuses. The new platform
schema preserves the full native result and applies these mappings only with
the operation's tagged disposition and payload. Unknown combinations return
`STATUS_MAPPING_UNSUPPORTED`; they are not guessed.

| Native meaning | Platform interpretation |
| --- | --- |
| REQUEST_INVALID with invalid/unresolved/not_computed | rejected; invalid/unresolved/not_computed; no usable payload |
| satisfied + specified_exact, with a valid finite calculation payload | completed; valid/defined/complete; evidence_mode=specification_example |
| undefined, with established zero normalizer | completed; valid/undefined/complete; no posterior |
| specified_partial with retained unresolved regions | partial; valid/unresolved/partial, even when some local values are defined |
| symbolic without a requested executable evaluator | partial with retained formulas; valid/unresolved/not_computed |
| UNSUPPORTED operation/capability | unsupported; valid/unresolved/not_computed; retain input family |
| failed mathematics, such as an invalid proposed law | rejected; mathematical_status=unresolved at platform level with the exact native `failed` finding retained; never `infeasible` without proof of an empty family |

For the last row a platform diagnostic names the failed mathematical predicate
and preserves the native result; the requested probability result remains
unresolved. `structural_validity` is copied from the native request validation,
not inferred from the law's failure. A proof of infeasibility is a different
tagged result and maps to `infeasible`. Numeric/service failure has computation
`failed` and math `unresolved`, not mathematical infeasibility. These rules
prevent the platform's deliberately smaller vocabulary from changing a claim.

Native accounting `assessed` with `eligible` means the requested assessment was
specified, not that a journal was committed. Outer disposition is completed,
commit observation not_committed; its native accounting-validity field remains
not_assessed for the synthetic examples. `unresolved`/`outside_scope`/`ineligible`
remain explicit assessment results, with no JournalProposal. Input rejection
maps as above. A replay payload carries the original committed receipt and
additional_commit=false; outer disposition replayed, commit observation
not_committed. A lost acknowledgement of a requested write maps to commit_unknown
with unknown observation until the original identity is reconciled.

Empirical justification and capability values are preserved. Forecast validity,
product readiness and human acceptance cannot be inferred from any mapping.
All platform examples are specification examples; their finite arithmetic is
checked separately, and product_implemented remains false.

## Continuous company family and insufficient summaries

The protected Northstar example has one shared unidentified floating fraction
x∈[0,1]. Historical interest of 5 does not identify it when both loan types
charged 5%. The 2025 scenario changes floating interest, profit, tax, cash and
equity together. I3's statement payload must therefore retain their common x,
not just independent endpoint lists. The source package's closed synthetic
scope, teaching tax model, assumed intraperiod ordering and aggregate event
resolution all travel with the result.

Grouping two instruments with the same currency, rate/reset schedule, maturity,
seniority, collateral/guarantee rights and relevant accounting memory may preserve
a specified linear interest query by adding principals. Grouping fixed and
floating instruments only by their historical interest loses the stress exposure
and fails that query. Even the safe grouping must be reconsidered for a new
default, prepayment or instrument-specific tax question. This is a query-scoped
sufficiency rule, not a general compiler proof of economic equivalence.

The real source-backed conflict requested in E05 is still missing: seven inspected
candidates did not establish one. The fourteen synthetic conflict cases specify
behavior but cannot supply that source evidence. P17 must complete the exact
authority/method and real-source obligations. The initial-profile choice and
interface decisions are proposed answers now, with actual evidence and owning
phase in P16's decision records. Open source/method decisions remain proposal
blockers through P19; they are not closed by writing this integration document.


FILE docs/design/proposal/architecture/initial-profile-v1.md
# Proposed first implementation profile

The first implementation should connect a company's disclosures, alternative
histories, economic events and complete statements. A financing-only example
would leave the working-capital, operating-asset, tax and reporting interfaces
untested. The proposed domain is therefore a bounded corporate company; the
initial authoring interface is typed constructors into the portable IR, with a
matched, bounded textual notation. These are separate choices. This proposal
addresses MC01–MC35 without asserting that every requested method is now supplied.

## Scope and the alternatives compared

P15 compared four candidates. Corporate/shared-IR and typed-library-first can
have exactly the same domain and differ only in authoring. Instrument-first
would make financing lifecycle work earlier, but cannot meet the whole-company
goal until the operating-company continuation is added. Broad sector-first
would require bank, insurance, group and cross-standard methods at entry, with
more currently unresolved authority. The chosen order exposes interactions in
one connected company while specifying extension requirements now. It does not
establish that this order is cheapest, fastest or easiest to use.

The profile is `CorporateJointHistory/1`. It includes one legal entity and book
per branch, a declared domestic functional currency, annual/interim evidence,
multiple source vintages and reviewed alternatives. Context and schema design
retain multiple-entity/perimeter/currency fields so an unsupported operation
is explicit. “One book” is an execution scope, not a global uniqueness rule for
companies or future groups. A company with subsidiaries, leases or contingencies
cannot be admitted as a closed single-company model merely by omitting them.

Evidence preparation must account for the declared statement and note inventory,
incorporated references and unresolved source units. Readings, interpretations,+assumptions and treatment eligibility are separate layers. Investor-information,
system-as-of and exploratory archival questions use the time contract's distinct
admission rules. Exact financial quantities, source precision and conditional
rounding assumptions remain distinct. Source limitations accompany each dependent
query; there is no global “complete” flag inferred from pages parsed.

The initial economic methods must connect sales/delivery/collection, purchases/
inventory/cost of sales/payables, payroll, tangible-asset additions/depreciation,
simple debt/equity/dividends and a declared simple tax model. They produce profit,
balance sheet, cash flows and changes in equity from the same event histories.
The simple tax model is an authored teaching assumption; actual tax requires
P17's jurisdictional method. Northstar supplies a closed synthetic example,
not proof that these methods cover Apple or a representative real issuer.

The initial reconstruction method is the history contract's admitted-template,
rational affine family with finite choices and bounded integers. It preserves
unidentified debt mix, unknown payment timing and other query-relevant state.
The declared half-year event slots do not recover invoices or prove daily
liquidity. Querying a finer horizon requires refinement or an unresolved answer.
Exact bounds require whole-domain reasoning and endpoint attainability; search
witnesses and explored extrema are not promoted to complete families or bounds.

Scenario execution initially supports imposed exogenous paths with explicit
behavior and information restrictions. Joint finite rational probability is an
optional extension under the admitted-measure contract. Unweighted alternatives
remain valid initial results. Continuous inference, causal interventions,
calibration and empirically validated forecasts require P17 methods and later
execution evidence. An imposed interest-rate stress does not reweight historical
contract alternatives or become a probability forecast.

Typed constructors must express all included records without embedding opaque
Python functions. The bounded text frontend initially covers the matched debt
and constraint fragment; unsupported declarations produce located diagnostics.
Textual whole-company authoring is a later frontend obligation, with the same
domain semantics and validation. Deferring that parser does not defer the
whole-company typed model, the DSL design or the portable representation.

## Acceptance examples and limits

The primary integrated example is the protected Northstar disclosure fixture
and chapter, interpreted through the new contracts. Its opening and half-year
events support independently calculable statements and a continuous debt family.
For the 2025 stress, let x be the floating fraction. The common joint result is:

| Quantity | Conditional value in currency units |
| --- | --- |
| Debt interest | 5 + 2x |
| Profit before tax | 82 − 2x |
| Tax at the stipulated 20% rate | 16.4 − 0.4x |
| Profit | 65.6 − 1.6x |
| Operating cash flow | 48.6 − 1.6x |
| Closing cash | 95.2 − 1.6x |
| Closing equity | 148.2 − 1.6x |
| Closing assets | 288.2 − 1.6x |

Here 0 ≤ x ≤ 1, payables plus debt are 140, receivables 55, inventory 40 and
net plant 98. Every row uses the same x. The endpoints are not equiprobable
scenarios, and the output is not a rectangular box of independently selectable
amounts. Changing the floating rate to 9% changes the interest slope to 4 and
the cash/profit/equity slopes to −3.2; independent arithmetic must detect that
change even if both frontends share an erroneous constant.

Acceptance of the specification requires exact expected exchanges for the
following connected cases, with preserved sources and explicit assumptions:

1. Annual/interim source inventory, missing incorporated reference, alternative
   narrative translation, rounding unknowns and separately admitted constraints.
2. Joint working-capital reconstruction and unidentified fixed/floating debt
   mix, with known aggregate movements and unknown intraperiod timing.
3. Conditional 2025 events, eligible treatments, balanced proposals, reconciled
   complete statements and debt-mix dependence, plus a changed-rate control.
4. Original versus corrected interim information views without later-information
   leakage; no automatic source-derived accounting permission.
5. Partial or unsupported region preservation, unavailable methods, exact versus
   approximate capabilities and unweighted versus admitted-measure queries.
6. Valid replay, changed-payload conflict, concurrent stale-head rejection,
   unknown commit recovery, review correction/invalidation and failed migration.

The shared platform examples exercise these connections alongside retained
evidence/time/history/uncertainty/accounting examples. A bounded real filing
case must retain its full declared inventory and all unformalized disclosures;
Apple's partial source preparation cannot satisfy that case by itself. E05's
real source-backed conflict and P17's dated accounting methods remain proposal
work. A document calculation satisfies only the finite arithmetic part of this
list. Runtime acceptance additionally needs implemented source/typed lowering,
solver/simulator, transaction fault tests and adapter checks. Human understanding
and accounting/forecast validity have separate evidence.

## Dependencies and retained later work

Implementation should proceed in dependency order, after the proposal has been
completed and the user has authorized implementation:

1. Versioned record definitions, exact values/context, source byte retention,
   dependency closure and pinned package/schema loading.
2. Review and time selection, provenance/invalidation, immutable views and the
   initial transaction store's receipt/replay behavior.
3. Typed constructors and validation; the matched debt text fragment and source
   maps; independent expected IR and adverse input cases.
4. Admitted history templates, joint affine constraints, finite-choice search,
   partial checkpoints, typed capability failures and query-dependent refinement.
5. The connected corporate economic and accounting methods with their actual
   authority, event scheduling and information boundaries; statement mapping.
6. The integrated company case, source corrections, replay/recovery and bounded
   real-filing coverage; then optional justified measure operations and adapters.

P17 must complete actual source-grounded methods for corporate operations,
bonds/equity, groups/FX, IFRS/US GAAP/ASBE, banks and insurers. The extension
records in I4 make dependencies visible; they do not count as method completion.
Examples must include a changed group perimeter, intercompany elimination and
FX translation, credit loss and credit-risk memory, and insurance service/
measurement memory. Imported official rules and software interfaces require
located inspected sources and explicit limits. General nonlinear inference,
calibrated forecasting, multiwriter throughput and distributed durability are
later implementation/evaluation obligations, not inferred from prototype tests.

P18 integrates the completed methods and contracts into the governing LaTeX
manuscript and inspects its actual rendering. P19 assesses the full proposal
against MC01–MC35 and G1–G18. The current architecture may be judged specified
within its scope while those later proposal blockers remain open. Neither that
judgment nor a successful PDF build authorizes product implementation.


NORTHSTAR ORIGINAL INPUTS:
{"schema":"accdsl-design-fixture/1","entity":"Northstar Components (synthetic)","currency":"USD","units":"one currency unit","basis":"DemoCorporate/1; not GAAP certification","disclosure_scope":"Closed synthetic goods company; the listed source package is complete by construction","assumptions":{"historical_resolution":"half-year aggregate flows; existence of intraperiod schedules required, not recovered invoices","inventory":"one homogeneous good at cost 5; purchases before delivery; quantities equal costs/5","sales":"delivery transfers control; no returns, services, variable consideration or foreign currency","tax":"20% positive taxable profit, all expenses deductible, no deferred tax; excess payment is prepaid tax","plant":"opening cost 100, annual depreciation 10; end-H1 addition 10 lives 5 years; end-H2 addition 12 lives 12 years; zero residuals","debt":"100 throughout; fixed and floating both 5% in 2024; fixed 5%, floating resets to 7% in 2025; all maturities after forecast","time":"half-year accrual fractions 1/2, annual 1; explicit teaching convention","closing":"temporary accounts closed after each H1/H2; annual income uses movements excluding closing","universe":"no omitted company, OCI, acquisition, tax or off-balance-sheet operations inside this synthetic package"},"accounts":{"cash":"asset","receivables":"asset","inventory":"asset","plant_cost":"asset","accum_depreciation":"contra_asset","tax_prepaid":"asset","payables":"liability","debt":"liability","capital":"equity","retained":"equity","revenue":"income","cost_of_sales":"expense","payroll":"expense","depreciation":"expense","interest":"expense","tax":"expense"},"opening":{"cash":"60","receivables":"20","inventory":"30","plant_cost":"100","accum_depreciation":"-20","tax_prepaid":"0","payables":"-20","debt":"-100","capital":"-50","retained":"-20"},"historical_events":[{"id":"2024H1.sale","date":"2024-06-30","period":"2024H1","postings":[{"account":"receivables","signed_amount":"110"},{"account":"revenue","signed_amount":"-110"}],"cash_class":null,"state_changes":{}},{"id":"2024H1.collect","date":"2024-06-30","period":"2024H1","postings":[{"account":"cash","signed_amount":"110"},{"account":"receivables","signed_amount":"-110"}],"cash_class":"operating","state_changes":{}},{"id":"2024H1.buy","date":"2024-06-30","period":"2024H1","postings":[{"account":"inventory","signed_amount":"70"},{"account":"payables","signed_amount":"-70"}],"cash_class":null,"state_changes":{}},{"id":"2024H1.supplier","date":"2024-06-30","period":"2024H1","postings":[{"account":"payables","signed_amount":"65"},{"account":"cash","signed_amount":"-65"}],"cash_class":"operating","state_changes":{}},{"id":"2024H1.deliver","date":"2024-06-30","period":"2024H1","postings":[{"account":"cost_of_sales","signed_amount":"75"},{"account":"inventory","signed_amount":"-75"}],"cash_class":null,"state_changes":{}},{"id":"2024H1.wages","date":"2024-06-30","period":"2024H1","postings":[{"account":"payroll","signed_amount":"20"},{"account":"cash","signed_amount":"-20"}],"cash_class":"operating","state_changes":{}},{"id":"2024H1.plant","date":"2024-06-30","period":"2024H1","postings":[{"account":"plant_cost","signed_amount":"10"},{"account":"cash","signed_amount":"-10"}],"cash_class":"investing","state_changes":{}},{"id":"2024H1.depreciate","date":"2024-06-30","period":"2024H1","postings":[{"account":"depreciation","signed_amount":"5"},{"account":"accum_depreciation","signed_amount":"-5"}],"cash_class":null,"state_changes":{}},{"id":"2024H1.interest","date":"2024-06-30","period":"2024H1","postings":[{"account":"interest","signed_amount":"2.5"},{"account":"cash","signed_amount":"-2.5"}],"cash_class":"operating","state_changes":{}},{"id":"2024H1.tax","date":"2024-06-30","period":"2024H1","postings":[{"account":"tax","signed_amount":"1.5"},{"account":"tax_prepaid","signed_amount":"2"},{"account":"cash","signed_amount":"-3.5"}],"cash_class":"operating","state_changes":{}},{"id":"2024H1.dividend","date":"2024-06-30","period":"2024H1","postings":[{"account":"retained","signed_amount":"4"},{"account":"cash","signed_amount":"-4"}],"cash_class":"financing","state_changes":{}},{"id":"2024H2.sale","date":"2024-12-31","period":"2024H2","postings":[{"account":"receivables","signed_amount":"150"},{"account":"revenue","signed_amount":"-150"}],"cash_class":null,"state_changes":{}},{"id":"2024H2.collect","date":"2024-12-31","period":"2024H2","postings":[{"account":"cash","signed_amount":"135"},{"account":"receivables","signed_amount":"-135"}],"cash_class":"operating","state_changes":{}},{"id":"2024H2.buy","date":"2024-12-31","period":"2024H2","postings":[{"account":"inventory","signed_amount":"85"},{"account":"payables","signed_amount":"-85"}],"cash_class":null,"state_changes":{}},{"id":"2024H2.supplier","date":"2024-12-31","period":"2024H2","postings":[{"account":"payables","signed_amount":"80"},{"account":"cash","signed_amount":"-80"}],"cash_class":"operating","state_changes":{}},{"id":"2024H2.deliver","date":"2024-12-31","period":"2024H2","postings":[{"account":"cost_of_sales","signed_amount":"90"},{"account":"inventory","signed_amount":"-90"}],"cash_class":null,"state_changes":{}},{"id":"2024H2.wages","date":"2024-12-31","period":"2024H2","postings":[{"account":"payroll","signed_amount":"22"},{"account":"cash","signed_amount":"-22"}],"cash_class":"operating","state_changes":{}},{"id":"2024H2.plant","date":"2024-12-31","period":"2024H2","postings":[{"account":"plant_cost","signed_amount":"12"},{"account":"cash","signed_amount":"-12"}],"cash_class":"investing","state_changes":{}},{"id":"2024H2.depreciate","date":"2024-12-31","period":"2024H2","postings":[{"account":"depreciation","signed_amount":"6"},{"account":"accum_depreciation","signed_amount":"-6"}],"cash_class":null,"state_changes":{}},{"id":"2024H2.interest","date":"2024-12-31","period":"2024H2","postings":[{"account":"interest","signed_amount":"2.5"},{"account":"cash","signed_amount":"-2.5"}],"cash_class":"operating","state_changes":{}},{"id":"2024H2.tax","date":"2024-12-31","period":"2024H2","postings":[{"account":"tax","signed_amount":"5.9"},{"account":"tax_prepaid","signed_amount":"-2"},{"account":"cash","signed_amount":"-3.9"}],"cash_class":"operating","state_changes":{}},{"id":"2024H2.dividend","date":"2024-12-31","period":"2024H2","postings":[{"account":"retained","signed_amount":"5"},{"account":"cash","signed_amount":"-5"}],"cash_class":"financing","state_changes":{}}],"expected":{"2024H1":{"cash":"65","receivables":"20","inventory":"25","plant_net":"85","tax_prepaid":"2","assets":"197","payables":"25","debt":"100","equity":"72","revenue":"110","profit":"6","operating_cash":"19","investing_cash":"-10","financing_cash":"-4"},"2024H2":{"cash":"74.6","receivables":"35","inventory":"20","plant_net":"91","tax_prepaid":"0","assets":"220.6","payables":"30","debt":"100","equity":"90.6","revenue":"150","profit":"23.6","operating_cash":"26.6","investing_cash":"-12","financing_cash":"-5"},"2024FY":{"revenue":"260","profit":"29.6","operating_cash":"45.6","investing_cash":"-22","financing_cash":"-9","cash_change":"14.6"},"2025_fixed":{"cash":"95.2","receivables":"55","inventory":"40","plant_net":"98","tax_prepaid":"0","assets":"288.2","payables":"40","debt":"100","equity":"148.2","revenue":"300","profit":"65.6","interest":"5","tax":"16.4","operating_cash":"48.6","investing_cash":"-20","financing_cash":"-8"},"2025_floating":{"cash":"93.6","receivables":"55","inventory":"40","plant_net":"98","tax_prepaid":"0","assets":"286.6","payables":"40","debt":"100","equity":"146.6","revenue":"300","profit":"64","interest":"7","tax":"16","operating_cash":"47","investing_cash":"-20","financing_cash":"-8"}},"forecast":{"start":"2025-01-01","end_exclusive":"2026-01-01","demand_units":"30","price":"10","unit_cost":"5","target_inventory_units":"8","current_sales_collection_fraction":"0.9","legacy_receivable_collections":"10","old_payables_paid":"30","new_purchases_paid":"130","payroll":"50","capex_at_period_end":"20","dividend":"8","tax_rate":"0.2","funding_limit":"0"},"coverage_units":[{"id":"NS.opening","kind":"statement","disposition":"structured","content":"Opening balance sheet and account balances"},{"id":"NS.h1.original","kind":"statement","disposition":"superseded_reading_preserved","content":"Originally revenue 120, receivables 30, tax expense/payment 3.5, profit 14, equity 80"},{"id":"NS.h1.correction","kind":"note","disposition":"structured","content":"Premature invoice 10: reverse revenue and receivable; reduce tax expense 2 into tax prepayment; corrected profit 6"},{"id":"NS.fy","kind":"statement","disposition":"structured","content":"Annual and revised interim statements derived from listed events"},{"id":"NS.operations","kind":"policy","disposition":"structured","content":"Goods, inventory, asset and working-capital assumptions above"},{"id":"NS.debt","kind":"note","disposition":"alternative_family","content":"Principal 100, interest 5; fixed/floating composition undisclosed"},{"id":"NS.equity","kind":"note","disposition":"structured","content":"Capital 50; original retained 20; dividends H1 4, H2 5"},{"id":"NS.reference","kind":"cross_reference","disposition":"resolved","target":"NS.debt","content":"Financing note applies to debt and interest in every statement"}]}

Supporting inspection paths (all relative to repo):
- docs/design/proposal/architecture/accounting-complete-exchanges-v1.json: exchanges X002, X007, X008, X188, X202, X241, K01 and K04; resolve their records and imports.
- docs/design/proposal/architecture/accounting-complete-source-packets-v1.json: matching cases; compare original source refs.
- docs/design/proposal/architecture/accounting-integration-field-validation-fixtures-v1.json: V01–V16 actual adverse candidates and expected outcomes.
- docs/design/proposal/architecture/accounting-complete-exchanges-diagnostic-v1.py: context_findings and adverse_outcome independently classify these finite inputs.
- docs/design/proposal/architecture/uncertainty-chaining-fixtures-v2.json: cases, mappings, bundles, admissions, active_rejection_receipts; requested refs resolve in records.
- docs/design/proposal/architecture/platform-contract-examples-v1.json and platform-contract-calculation-v1.py: joint company outcomes, changed-rate control and finite arithmetic.
- docs/design/proposal/architecture/evidence-contract-v3.md; time-contract-v2.md; history-families-contract-v1.md; uncertainty-admission-contract-v1.md; uncertainty-measure-attachment-contract-v2.md: controlling domain rules.
- docs/design/proposal/architecture/accounting-replay-contract-v1.md and accounting-integration-contract-v1.md: native key, assess-only effects and validation order.

Tools may inspect these exact files. Do not claim exhaustive coverage if sampling; substantive architecture review with disclosed sample coverage is the intended result. Do not demand another packet approval cycle.
