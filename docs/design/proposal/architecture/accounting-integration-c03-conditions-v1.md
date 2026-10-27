# C03 party and contractual date — proposal amendment v1

This amendment addresses MC08, MC13, MC25, MC34 and MC35 with G4/G18 interactions. It specifies the C03 date/party relationship in rows F185/F186. The original inventory, six-row reason amendment, C05/C07 amendment and all earlier examples remain unchanged. F182 unknown_reason retains its existing required string|null and nonblank-string rules; reason prose neither supplies a date nor overrides the party Boolean. Product implementation remains disabled.

## Question, evidence contract and audit

Can a source packet preserve a nonparty's supplied date, distinguish a not-applicable null, and reject malformed input before identity lookup? Exact E01/I01 and E03/I03 are synthetic preservation comparators. Acceptance of this bounded specification requires an explicit truth table, independently derivable diagnostics, complete matched exchanges, refreshed source/record identities and unchanged committed state. Changed predecessor bytes, lost facts, premature lookup, stale pins, contradictory findings or changed committed domains veto the result. Check counts are explanatory only; no accounting, forecast, runtime or human acceptance follows.

The skeptical audit passes for the revised scope: the false/non-null case is explicitly resolved, comparators preserve both true/date and false/null outcomes, the diagnostic uses submitted values, the environment is standard-library Python, and there is no statistical or performance comparison. Stop after this C03 amendment and fresh checks. C09/C10, other source predicates and V01–V16 diagnostics remain separate work.

## Representation and assessment

C03 and C03/value must be objects. Both party_to_contract and contractual_date are required. Party is an exact JSON Boolean: null, numbers, strings, arrays and objects are malformed. Date permits null or a string. Every string must match ASCII YYYY-MM-DD exactly and designate a valid proleptic Gregorian date in years 0001–9999. There is no trimming, date inference, timezone conversion or normalization. Leap years are divisible by four except centuries not divisible by 400. A calendar-valid date alone does not establish recognition timing or contractual enforceability.

| Party | Date | Representation | Consequence for this C03 condition |
| --- | --- | --- | --- |
| true | valid date | valid | Continue to assessment; retained E01 supplies the matched eligible case |
| false | null | valid | Date is not applicable; C03 remains ineligible |
| false | valid date | valid | Preserve the exact date as context; C03 remains ineligible |
| true | null | malformed | Reject at shape before lookup or assessment |

For the false/date exchange, retain E03's unaccepted-offer evidence and replace only its null date with 2024-06-03. That date can describe the supplied offer context; it cannot establish participation contrary to the explicit false fact. The assessment finding is `ineligible`, reason `not party to contract at recognition`, and the overall reason_codes are `["C03:ineligible"]`. No date-derived journal follows. A future contradictory-evidence policy may require further reconciliation; this amendment makes no such inference and does not erase the supplied date.

Mandatory-null rejection for false would discard a representable contextual fact; it is therefore not selected. Permissive true/null admission would let a missing required participation date pass under an unknown label; it is rejected. Inferring participation from either date or reason prose would change supplied facts. The selected rule keeps representation validity separate from the stipulated recognition finding.

## Findings and guards

All scoped defects are shape-stage findings. A missing party or date produces INVALID_CONDITION_PACKET at its missing leaf path. A present non-Boolean party, or date outside string|null, produces INVALID_FIELD_TYPE. A string with invalid date grammar or an impossible calendar day produces INVALID_CONDITION_PACKET. Exact true with null date produces INVALID_UNKNOWN_REPRESENTATION at source/C03/value/contractual_date. False/null and false/valid-date produce no scoped shape finding.

Check requiredness before type and type before parsing. Evaluate conditional null admissibility only when party is an exact Boolean. Thus a malformed Boolean with null date produces only the party type finding. Retain independently decidable missing, wrong-type or invalid-string date findings even if party is malformed. A missing or wrong-type value parent produces one parent finding; its descendants are not evaluated. The finite local examples assume the outer packet is an object; the retained packet rule still applies to other shapes.

Each finding carries stage, path, code, the matrix's expected rule and observed presence. A present observation also contains exact JSON type and value; missing observations have no invented value. Sort findings by path then code; preserve all diagnostic paths and deduplicate response reason_codes in first-occurrence order. Expected findings are authored in fixtures and checked against candidate values, not mutation descriptions.

## Complete exchanges

Import unchanged I01 and I03 by exact file hash and record identity. For changed examples, save a new complete_inputs source case and refresh its FileRef, CaseRef, eligibility ConditionRefs, request, submission and affected assessment/response records. Preserve opaque versions and every other source fact. Dependencies must resolve and hash correctly before shape evaluation, so a stale source identity cannot mask the intended date finding.

A valid exchange passes wire parsing, dependencies, shape, source_versions and bindings; identity/receipt lookup finds no prior identity in the retained empty index. Freshness then succeeds and assessment runs. The false/date response is assessed with non-null validated request and assessment references; commit_status is not_committed and additional_commit is false. Diagnostic journal, delta, receipt and observed-state references remain null. Retain I03's evidence-status fields and refresh assessment bindings. Identity index, committed journals, selected state and committed receipts are unchanged.

Malformed exchanges stop at shape. Lookup, freshness and accounting assessment are not performed. Preserve submission bytes as diagnostic evidence, without publishing a validated request, assessment, journal, delta, receipt or observed state. Return rejected/not_committed and additional_commit=false with the derived reason codes. The seven statuses are structural_validity=invalid, mathematical_status=unresolved, computation_status=not_computed, empirical_justification=not_established, capability_status=specified_only_no_runtime, accounting_validity=not_assessed and human_acceptance=pending. All four committed domains remain unchanged.

## Assumptions, limits and continuation

| Choice and provenance | Status and justification | Failure mode and earliest check |
| --- | --- | --- |
| E01/I01 and E03/I03 | Preservation baselines only | Changed evidence or wrong outcome; exact hashes and semantic fields |
| Calendar-date grammar in retained field-validation matrix, source_packet rule | Inherited representation rule made explicit | Permissive host parser; malformed grammar, leap-century and year-boundary controls |
| False/date contextual interpretation | Reviewed proposed rule | Date silently establishes participation; matched E03 false/date assessment |
| Exact Boolean typing | Retained JSON distinction | Python 0/1 treated as bool; explicit null, numeric and string controls |
| Finite document diagnostic | Convenience check, no runtime API | Expectations mirror implementation; separately authored outcomes and independent review |

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Submit C03 slice for review | Explicit rules, complete exchanges and fresh finite checks | Any preservation, identity, stage or response mismatch requires repair | Finite coverage may omit a combination | Independent bounded review | P16 completion or runtime correctness |
| Continue proposal | Wider criteria remain incomplete | Whole architecture failure blocks phase acceptance | C09/C10 and remaining contracts unresolved | C09/C10 next, then V01–V16 | Accounting/forecast validity or human acceptance |

Strongest alternative explanation: consistent fixtures could encode the same mistaken interpretation. A disagreement with the retained recognition condition or a demonstrated source/response mismatch overturns the affected example. Calendar validity is only representation evidence. No new accounting-authority claim is made, and all wider MC01–MC35/G1–G18 obligations persist.
