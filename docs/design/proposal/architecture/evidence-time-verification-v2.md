# Evidence/time verification — bounded P16 repair

Status: all 18 evidence and 37 time examples inspected. Targeted file, population, arithmetic and boundary checks passed; independent bounded review remains pending.
This is author verification of proposal examples, not runtime execution or
independent acceptance. The accepted P15 requirements and reviewed recovery
plan are the comparator. MC01–MC05, MC25 and MC27 are addressed in part;
G2/G11/G13/G17/G18 and every other mission obligation remain open.

## Evidence group: all 18 examples

| Fixture or population | Contract rule | Inspection and disposition |
| --- | --- | --- |
| E-package-1 contents and occurrences | E1–E2 | Seven occurrence IDs retain all locators. cDebt has three occurrences, yielding two duplicate-content occurrences; the five content bodies remain separate from six contextual candidates. Annual/quarterly/semiannual/external root counts are 3/1/2/1. |
| E-package-1 assertions | E2, E4 | aAnnual, aQuarter, aHalf and aAnnualDebt have accepted extraction; aHalfDebt is pending and aPolicy unresolved. Thus 4/1/1 accepted/pending/unresolved, zero rejected. aAnnualDebt has two aliases while aHalfDebt remains a distinct unreviewed context. No assertion denominator for the whole real report is inferred. |
| rPolicy, rCycle, rCopy | E2 | Existing targets resolve the policy, close the two-edge cycle and identify the copied reference. The source occurrences remain retained. |
| rContinuation, rAmbiguous, rUnavailable, rBudget | E2, E5 | Missing continuation, two possible agreements, absent annex and exhausted target budget remain four distinct blockers. The unvisited appendix/target-4 frontier survives. Package closure and semantic completion are false. |
| qAnnual, qQuarter, qHalf | E2, E4 | Accepted extraction with explicit reporting contexts supports only displayed 260/60/110 lookups. No journal admission follows. |
| qDebtExposure, qGuarantee | E2, E4–E5 | Pending/unresolved readings and the named missing references leave both queries unresolved; no exposure value is returned. Query totals are three supported and two unresolved. |
| E-permission | E4 | The 2024 USD 50 permission constrains an exercised action only. Exercise and present payment remain unknown; payment=50 is rejected. |
| E-permission-conditional | E4 | Selecting exercise-20 makes the repurchase scenario conditional; accounting posting stays unsupported. |
| E-guarantee | E4 | Unknown default preserves both branches without probabilities or an unconditional payable. The predicate is contractual, not a recognition rule. |
| E-qualifier | E4 | Qualitative wording does not identify 95%; selecting threshold-95 makes only the model predicate conditional. |
| E-layers | E4 | Accepted extraction does not admit a proposed interpretation or accounting treatment. No journal is produced. |
| E-correction | E4 | Reading 720 is corrected to literal 120 without changing the source. mapping-old, calc-old and report-old are transitive descendants invalid for current use; other-report is unaffected. V1 retains the old result with an error warning. |
| E-conflict-synthetic | E1, E5 | Faithful same-context 120/110 readings with no supersession preserve both assertions and an unresolved query. This synthetic case does not satisfy E05. |
| E-round-even, E-round-odd | E3 | With explicit nearest/ties-to-even, 120 admits 119.5 and 120.5; 121 excludes 120.5 and 121.5. These are compatibility sets, not distributions. |
| E-round-tie-unknown | E3 | Nearest with unknown tie rule establishes interior compatibility only; the closed outer enclosure is not an exact feasible set. |
| E-round-convention-unknown | E3 | Display precision alone supplies no nearest-rounding interval. |
| E-round-assumed | E3 | nearest-model-v1 supplies a conditional outer enclosure; endpoints remain unknown, with no distribution. |
| E-display | E3 | Found a concrete contradiction: the assets context inherited positive_revenue. Corrected only that sign label to positive_assets in evidence-fixtures-v2.json. Exact scaled display is 364980000000 USD; underlying unrounded amount remains unknown. |
| E-parentheses | E3 | Explicit parentheses-mean-negative gives -13505000000 USD and retains (13,505). |
| E-dash | E3 | Unknown dash semantics yields unresolved, never zero. |
| E-currency-mismatch | E3 | USD and EUR without conversion cannot be added. The identical flow intervals also fail the nonoverlap rule; this is a rejection example, not an isolated test proving a currency validator. |
| E-apple-scope | E4 | Inspected retained Note 9 text: fixed-rate coupon classification coexists with swaps converting a portion of certain USD notes to floating. Combined exposure lacks allocation/terms. The passages are compatible; no genuine conflict, full-company semantics or rounding convention is established. |

The v1 documents and checks are preserved. evidence-contract-v2.md changes the
fixture reference and records the context repair; architecture.json now pins
both evidence v2 files. The fixture set retains 18 examples. P02's closed
half-unit model remains a prior compatibility hypothesis, not issuer support
for nearest rounding. Apple PDF bytes are pinned, but this repair has not
visually rechecked extraction against the PDF. Source text inspection does not
establish accounting treatment or historical byte availability.

## Time group: all 37 examples

| Fixture IDs | Contract rule | Inspection and disposition |
| --- | --- | --- |
| T-before-revision | T2, T4 | September 2024 cutoff excludes the March 2025 restatement and annual result; h1-original remains selected. |
| T-investor-late-ingest | T2, T4 | Public March 2 bytes pass March 3 even though ingestion is March 5. The explicit March 7 review snapshot admits readings of old bytes. h1-restated and fy are selected. |
| T-system-before-ingest | T2 | March 4 system time excludes both March 5 receipts; the original survives. |
| T-system-after-review | T2, T4 | March 7 possession/review and March 3 public cutoff admit the two revised-vintage records. |
| T-original | T4 | Eligible roots h1-original and fy survive original selection; h1-restated is not a lineage root. This does not authorise mixed-vintage subtraction. |
| T-system-before-review | T2 | March 5 noon receipts exist but March 6 review is future. The original is selected and the affected claim remains unresolved. |
| T-ingestion-absent-system, T-ingestion-null-system | T1–T2 | Absent and null ingestion give distinct INGESTION_ABSENT/INGESTION_UNKNOWN reasons; neither admits the source. |
| T-ingestion-absent-investor, T-ingestion-null-investor | T2 | Supported public byte vintage and explicit review suffice for the investor claim; possession is not its target. |
| T-publication-unknown-investor | T2 | Unknown publication prevents cutoff admission. |
| T-publication-unknown-pure-system | T2 | Receipt and timely review support possession with no investor cutoff, while public availability remains unknown. |
| T-publication-unknown-archive | T2 | No cutoff permits archival display only; historical admissibility is unestablished. |
| T-publication-unknown-archive-cutoff | T2 | Unknown publication remains an unresolved archival candidate, outside the selected set. |
| T-public-bytes-unverified | T2–T3 | A known date does not prove byte vintage; no investor selection. |
| T-system-receipt-unverified | T3 | A timestamp without the binding receipt cannot prove system possession. |
| T-source-integrity-failed | T3 | Altered inline bytes disagree with the retained digest and cause hard rejection, distinct from unknown vintage. |
| T-timezone-before, T-timezone-equal | T1–T3 | 2024-08-01 00:00 +08:00 equals July 31 16:00 UTC; one second earlier excludes, equality admits. |
| T-date-only-within, T-date-only-end | T3 | Hong Kong August 1 covers July 31 16:00 through August 1 16:00 UTC, upper endpoint excluded. Noon local remains unresolved; the exclusive upper boundary permits admission. |
| T-date-only-no-zone, T-timestamp-no-zone | T1, T3 | Date with unknown zone remains unresolved; zone-less timestamp rejects the instant comparison. No machine-local fallback. |
| T-ingestion-date-within | T3 | Noon within the UTC receipt date leaves possession unresolved even for raw-layer inspection. |
| T-selective-revision | T4 | Only H1 revenue is superseded. cost-h1 remains selected with h1-restated and fy. |
| T-conflicting-leaves | T4 | h1-restated and independent h1-other remain live; H1 revenue is unresolved. FY stays selected, and no average is substituted. |
| T-unknown-new-version | T2, T4 | Unknown restatement publication cannot suppress the original, but leaves the affected claim unresolved. FY remains selected. |
| T-cycle | T4 | Reciprocal supersession rejects the affected H1 lineage. |
| T-missing-ancestor | T4 | Missing target rejects the lineage; the descendant cannot be relabelled an original. |
| T-subtract-valid | T5 | Explicit compatibility for these quantities plus identical contexts/proper prefix gives 260−110=150 for [2024-07-01,2025-01-01). The shared v2 string alone would not suffice. |
| T-subtract-vintage | T5 | No revision bridge permits 260−120 as an H2 result. Financial value is null even though arithmetic alone gives 140. |
| T-subtract-calendar, T-subtract-perimeter, T-subtract-not-prefix | T5 | Each changed context violates a required compatibility condition. No bridge is supplied and no value is admitted. |
| T-harmonised-assumption | T2, T4; E2 | v1 was inconsistent: the expected conditional result had no selected assumption, and its records list differed from the documented composition rule. v2 selects bridge-assumed, declares record_subset, accepted synthetic transform review, byte support and h1-original information dependency. The derived 110 retains the original 120 and both lineage IDs; no issuer restatement is claimed. |
| T-harmonised-missing | T4 | v2 clarifies the same restricted record subset. Without a transform, harmonisation is unsupported and the source value survives without a derived value. |
| T-estimate-authority-missing | T5 | Calling a change prospective supplies no authority. TREATMENT_UNSUPPORTED blocks reclassification; no standards conclusion follows. |

All 29 selection outcomes were compared with the prose after resolving each
case's overrides/subset. No temporal selector was implemented or executed.
The base review snapshot is an explicit synthetic choice, not a current-time
fallback. The fixtures assume supported receipt/vintage links; actual receipt
structure belongs to the unfinished persistence/interface contracts. Public and
private/system possession are different claims. Current integrity errors veto
an affected record, while unknown publication/review/vintage preserves unresolved
possibilities rather than proving an empty feasible set.

The P06 low-level selector's require_known_bytes=False and absent-ingestion
fallback were inspected as historical implementation evidence. Its request
wrapper defaults require_known_bytes to True; the low-level default is not a
claim about every call path. Neither default defines this proposed contract.
The retained temporal example supplies synthetic 120/110/260 arithmetic only.

## Verification results and limits

The first fresh diagnostic (`consistency-check-v2.json`) passed 164 checks,
covering 19 reference occurrences and all 55 example IDs. It includes the exact
Python diagnostic for reproduction with a fresh output filename. A subsequent
`consistency-check-v3.json` pins this completed verification note; v2 remains a
record of the preceding draft. Neither diagnostic executes a temporal selector.
The final result note records the outcome of that subsequent check.

The registered command was
`PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_accounting_proposal.py --phase P16 --check`.
Its fresh `structural-check-v2.json` is nonempty valid JSON: exit 1, 62 checks,
61 passing, first failure `whole architecture contracts`. The execution record
preserves its command, exit, duration and checker digest. The checker raises on
this failure before per-contract fields/references, profile selection or open
decisions; none of those later checks can be claimed as passed. The separate
diagnostic verifies saved references and retained decisions within this slice.

The stop condition is met at the author-verification level: complete fixture
mapping, explicit repairs, retained source boundaries and accurate reporting.
No remaining fixture group is uninspected. This does not certify exhaustive
contract semantics. In particular, date-only review handling, daylight-saving
boundaries, a known but ineligible intermediate supersession ancestor, and every
later interface are not independently executable conformance results here.
They remain integration/conformance obligations; a rule in prose is not a run.

The next task is independent review with review_scope=bounded_partial_work.
After acceptance, investigate a genuine source conflict for E05 in a separate
bounded task; do not combine that authority/source investigation with a complete
lifecycle implementation. Full P16 remains incomplete with seven contracts,
profile comparison/acceptance/dependencies and fourteen blocking decisions open.
