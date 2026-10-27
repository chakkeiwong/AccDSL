# Accounting request bindings — proposed supplement v1

An acquisition cannot use the event from one retained history and the opening
balance from another merely because both records have valid digests. A method
also cannot silently use a different authority version from the one named by
its caller. This supplement makes five relationships in the typed acquisition
exchange explicit. It addresses MC08, MC13, MC25 and MC34, with MC35 internal
preparation and G4/G18 interactions. It supplements accounting-records-contract-v1.md
without changing retained bytes or the accepted accounting-replay-contract-v1.md
order. Accounting eligibility and general lifecycle methods remain unfinished.

## Exact input relationships

Let q be the submitted request content, and resolve its references in the
immutable dependency bundle. The existing record version supplies required
fields, allowed kinds, canonical encoding, context and identity rules. Before
recognition, measurement or identity lookup, all five equalities below must
hold. Equality means the same retained record digest, not the same display name,
version number, apparent balances or inferred economic meaning.

| Rule | Required equality | Rejection reason |
| --- | --- | --- |
| B1 | resolve(q.event).branch = q.branch | EVENT_BRANCH_MISMATCH |
| B2 | resolve(q.opening).branch = q.branch | OPENING_BRANCH_MISMATCH |
| B3 | resolve(q.event).time = q.time | EVENT_TIME_MISMATCH |
| B4 | resolve(q.opening).chart = q.chart | OPENING_CHART_MISMATCH |
| B5 | resolve(q.method).authority = q.authority | METHOD_AUTHORITY_MISMATCH |

These rules supplement, rather than replace, digest/kind/required-field checks,
entity/book/context consistency, event identity, chart account membership and
evidence/admission alignment. In particular, request.identity.branch_id equals
the named branch's branch_id, and admission.time equals q.time. A source anchor
or authority digest proves neither applicability nor the truth of the facts.
Matching branch identifiers do not establish equality of branch versions.
Opening balances using identical account names can still name different chart
versions. A method's authority link must be the exact authority selected in the
request even when the two authority records cite the same source paragraphs.
Cross-version equivalence would require a separately specified migration; none
is assumed here. This is a proposed consistency rule, not an accounting-standard
interpretation or a choice of storage technology.

## Rejection and ordering

The receiver first retains submitted bytes and available dependencies, then
validates fields, reference closure, digests, kinds, context, admission and the
five bindings. A failed binding rejects before stable-key lookup, eligibility
assessment or comparison of the opening state with current state. No canonical
validated request is published. If several of B1–B5 fail, return all applicable
codes in B1–B5 order without duplicates after their dependencies validate;
malformed or missing dependencies are handled by the predecessor's structural
failure rules before equality evaluation.

The response uses the existing response kind, with status=rejected,
request=null, assessment=null, diagnostic_journal=null, diagnostic_delta=null,
receipt=null, observed_state=null, commit_status=not_committed and
additional_commit=false. Its submission reference retains the exact raw_text;
metadata identifies this submission response with operation=submit. Status is:
structural_validity=invalid, mathematical_status=unresolved,
computation_status=not_computed, empirical_justification=not_established,
capability_status=specified_only_no_runtime, accounting_validity=not_assessed
and human_acceptance=pending. An internally consistent request is necessary for
a mathematical/accounting assessment; the failure does not evaluate the
acquisition formula or conclude that a particular treatment is ineligible.

The identity index, committed journals, selected state and committed receipts
all remain byte-for-byte unchanged. Diagnostic retention is outside these four
domain components. observed_state=null avoids implying that lookup or freshness
was evaluated; the complete fixture before/after views describe the stipulated
world for the reader, not a state disclosed by the rejection response.

A diagnostic_content_digest hashes the submitted candidate using the retained
request encoding/domain so a reviewer can compare bytes. It has the explicit
role unvalidated_candidate and is never entered in the registry as a validated
request or returned in response.request. The submission digest separately binds
the raw transport text. Hash computation alone confers no validity. Rejections
retain both diagnostic information and the submitted dependency versions; they
do not rewrite references to make the request consistent.

After all validation succeeds, the accepted order remains stable-key lookup
before freshness: an equal fingerprint returns the original receipt, a different
fingerprint conflicts, and only an absent key proceeds to freshness and then
eligibility. Thus invalid dependencies cannot obtain a replay merely by naming
an existing event ID. This supplement adds no replay case or runtime mechanism.

## Six design examples and matched comparison

accounting-bindings-fixtures-v1.json imports the exact hashed registry and R01
exchange from accounting-records-fixtures-v1.json. B00 is that unchanged control.
B01–B05 each start from its submitted A01 facts and replace just one dependency
edge: event.branch, opening.branch, event.time, opening.chart or method.authority.
Each changed record and its submission/response has a recomputed digest. No
retained record is overwritten. Each case includes the transitive submitted
bundle, the exact unequal references, a concrete response and four-component
before/after views. The other four binding equalities, context, identity,
account membership and evidence/admission relationships remain valid.

The branch alternative keeps branch_id A and changes its version to 2; the
chart and authority alternatives likewise change only version. These are
synthetic record versions, not new accounting authority or evidence of a second
admissible real-company history. The time alternative changes economic_date to
2024-01-03 within the same reporting interval. Request time and evidence admission
remain aligned; the event's contradictory time is the sole binding failure.
The opening examples retain the original current world. Their different
opening references would be stale if they reached freshness, but they cannot
reach that stage: no freshness verdict is claimed or used to explain rejection.
This keeps the prior lookup-before-freshness rule intact.

On the identical six submitted bundles, the comparator checks valid digest,
reference closure and kind only. All six pass that limited screen. The proposed
five relationships pass the control and reject exactly the named relationship
in each of the five counterexamples. Digest/kind validation is necessary but
insufficient for this question; it is not a complete competing accounting
engine. The comparison establishes a finite information gap, not speed, storage
cost, scientific superiority or implementation correctness. A direct journal
interface or event-sourced design could both implement these same requirements.

## Evidence contract, defaults and stopping condition

Question: can the specified request distinguish individually valid dependencies
that disagree at one of these five boundaries? The baseline is digest/kind
validation on exactly the same six inputs. The primary criterion is one passing
control plus five isolated binding rejections with the specified null/status
fields and unchanged domain components. Hash mismatch, missing reference,
wrong kind, extra binding failure, broken context/admission, changed predecessor
or commitment on rejection veto these examples and trigger fixture repair.
The check count and retained A01 arithmetic are explanatory only. No stochastic
comparison, scientific run or environment-dependent numerical kernel is used.

| Choice and provenance | Status and justification | Failure mode and early diagnostic |
| --- | --- | --- |
| Sorted compact ASCII JSON and SHA256 from accepted replay/records | Inherited example encoding, not a general format selection | Wrong domain or omitted dependency; recalculate every digest and traverse closure |
| Equality of retained versions | Proposed rule for reproducible interpretation | Silent semantic aliasing; version-only branch/chart/authority counterexamples |
| A01 eligibility and branch admissibility | Stipulated synthetic hypotheses inherited from R01 | Balance mistaken for eligibility; retain not_assessed accounting status and do not evaluate authority |
| Two-decimal CU amounts and A01 date range | Convenience for unchanged finite inputs | Mistaken general currency/time support; no changes to amounts and explicit time-within-period check |
| Complete original current world on rejection | Controlled fixture setup | Mistaking a potential later stale check for rejection cause; require no lookup/freshness/eligibility evaluation |

Pre-execution skeptical audit: the baseline answers the limited binding question,
not whole-product correctness. All counterexamples preserve the same accounting
facts and stipulated source limitations. No proxy metric is a promotion criterion,
no technology comparison or new environment is involved, and the stop condition
is this saved supplement, six examples, finite verification and a fresh registered
P16 structural check. Four other contract groups, the integrated initial profile,
dependency order and fourteen decisions remain open. The existing whole-contract
checker failure is expected; it does not accept or reject this bounded argument.
Independent review of both the prior records work and this supplement remains
pending. Next, after that disposition, address accounting eligibility and
preconditions from retained authority before expanding lifecycle methods.
