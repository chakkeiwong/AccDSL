# P16 bounded result: scalar event_refs rejection

Completed the reviewed paired malformed-field supplement. P16 remains PARTIAL;
product implementation is disabled. Scope is MC12/G15 with MC08, MC10, MC14,
MC18 and MC25. All MC01–MC35/G1–G18 and all four P16 criteria remain active.
The preceding result is preserved byte-for-byte in
`docs/design/proposal/architecture/uncertainty-malformed-prior-result-v1.md`.

The two complete controls derive from SC01 and retain both available model
versions while selecting the old compatible bindings. Each specifies probability
5/6. The two complete malformed submissions change only event_refs from an array
to its scalar element, plus mechanical identities. Each specifies REQUEST_INVALID
and the proposed REQUEST_FIELD_TYPE_INVALID refinement at /event_refs, expected
array, actual string. Requested structure is invalid, requested mathematics
unresolved, computation not_computed and probability null. Empirical justification
remains not_established; capability remains specified_only_no_runtime.

Rejection precedes semantic and dependency resolution. Receipts retain the scalar,
request identity and content hash, all supplied records, unchanged family/view/
attachment hashes, dependency roles and an empty validated-dependency list. The
old attachment is unchanged_not_revalidated by the failed operation. Its separate
pre-state remains an attached assumption with a normalized finite law, checked
independently by the author diagnostic. Correction requires a newly identified
array-valued request and full validation; nothing is automatically repaired,
admitted, migrated or evaluated. Expected receipts are proposed behavior, not
executed product responses or evidence of atomic storage.

Actual document-diagnostic command:
`PYTHONDONTWRITEBYTECODE=1 python3 docs/design/proposal/architecture/uncertainty-malformed-diagnostic-v1.py --output docs/design/proposal/architecture/uncertainty-malformed-verification-v1.json`

The nonempty JSON records 298 passing checks and no failures: pinned controls,
complete declarations and transitive closure, both versioned bijections and
assignments, independent Fraction arithmetic, actual-value type findings, exact
input deltas, full receipt correspondence and preservation hashes. The first
attempt stopped before writing a report because support_restrictions was looked
up on the linked model instead of the request; the diagnostic was corrected to
compare the declared request fields and rerun. No fixture input changed in that
repair. The report includes this history, the command, input hashes, environment,
elapsed time and limitations. No new production module or test suite was added.

Recovery checks matched 75 architecture reference occurrences, ten saved
stale-diagnostic hashes and all 153 saved structural inputs at initial recovery.
progress.md was not among those inputs. After the architecture/result edits,
151 prior structural inputs remained unchanged, as the final integrity record states.
Prior suites were not rerun. New sources, fixtures and the diagnostic are proposal
materials in the allowed architecture directory.

| Decision | Primary criterion status | Veto diagnostic status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Bounded supplement author-complete | Paired controls 5/6 and scalar type rejection with full receipts | 298 document checks pass after diagnostic repair | Independent semantic review pending | Review this slice; next specify remaining malformed-input cases | General equivalence, architecture preference or runtime correctness |
| Keep P16 partial | Six whole-product contracts unfinished | Registered checker: 185/186 pass; whole architecture contracts fails | Initial profile, integrated criteria, dependency order and fourteen decisions unresolved | Continue bounded proposal work | Product readiness or human acceptance |

Engineering evidence consists of specified examples and deterministic author
checks. Numerical evidence is exact arithmetic on two synthetic finite laws.
Scientific evidence does not establish accounting or empirical forecast validity.
There is no stochastic comparison or ranking. Strict array typing and the reason
code are provisional design choices, not an architecture-selection result.

Post-run red team: both encodings and expected receipts were authored together;
a shared semantic mistake could survive correspondence checks. A missing typed
dependency or conflicting validation rule would require repair. The weakest
part is completeness beyond this one malformed field; no general malformed-input
coverage or persistence implementation is established.

Changed existing files: `data/accounting-master/deliverables/P16/architecture.json`,
`data/accounting-master/deliverables/P16/result.md` and
`data/accounting-master/deliverables/P16/progress.md`.
New files in `docs/design/proposal/architecture/`: `uncertainty-malformed-comparison-v1.md`,
`uncertainty-malformed-fixtures-v1.json`, `uncertainty-malformed-diagnostic-v1.py`,
`uncertainty-malformed-verification-v1.json`, `uncertainty-malformed-prior-result-v1.md`.
Fresh records in the same directory: `uncertainty-malformed-structural-v1.json`,
`uncertainty-malformed-structural-execution-v1.json`,
`uncertainty-malformed-structural-v2.json`,
`uncertainty-malformed-structural-execution-v2.json` and
`uncertainty-malformed-integrity-v1.json`.

Next task: malformed envelopes, missing fields and registry identities. Then
remaining family/support/purpose and partition/projection failures, followed by
conditioning, duplicate-evidence protection, likelihood updates and conditional
outcomes. Six contracts (uncertainty, accounting, language/IR, persistence,
interfaces, failure semantics), the initial profile, integrated acceptance and
dependency order, fourteen decisions, E05 source limits, P17 authority/research/
real-company obligations, independent P16 review and human acceptance remain open.

Registered check command:
`PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_accounting_proposal.py --phase P16 --check`

The first fresh check exited 1: 185 of 186 checks passed; the sole failure is
`whole architecture contracts`. That gate prevents individual-contract and
initial-profile checks from being reached. This is expected incompleteness, not
full P16 acceptance. No check was weakened. The v1 output and execution record
preserve that run; v2 records the final run after this result/checkpoint update.
Final reference and preserved-input integrity is recorded separately. Structural
checks and the author diagnostic do not replace independent substantive review.
