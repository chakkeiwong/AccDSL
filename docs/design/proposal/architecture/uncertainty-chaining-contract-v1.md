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
