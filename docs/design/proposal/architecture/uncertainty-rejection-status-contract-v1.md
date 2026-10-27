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
