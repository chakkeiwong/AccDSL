# P02 bounded Apple case: implementation result

The repaired case covers the retained Apple FY2024 annual report, FY2025 Q1 interim report and disclosed comparatives. It contains 13 annual and 10 interim note dispositions, 125 monetary observations, 34 selected reconciliations and 698 checked anchors. Nine notes link selected quantities; all 23 retain specific unresolved meaning. No note is classified as fully formalised. Counts describe inventory coverage, not semantic completeness.

This completes implementation of the reviewed P02 slice for MC01, MC03, MC05, MC16 and MC28, subject to independent result review. G4, G5, G11, G12 and G13 retain wider obligations, as do all G1–G18. Human acceptance remains pending.

## Pre-execution evidence contract and audit

The engineering question was whether the partial adapter could produce a reproducible, source-anchored annual/interim case with correct selected bridges and explicit missing meaning. The comparators are the pinned annual PDF with independently regenerated layout text and original interim HTML fact/context/unit records. Generated case values and authored dispositions are not independent numerical oracles. The issuer-linked annual representation provides a separate selected-cell comparison.

Initial inspection confirmed the stale case and absent result note. The reviewed recovery plan was continued without restarting discovery. The old note-membership check used only a fact's start; the repair checks its complete span and extraction identity. The pre-run audit was recorded in progress.md before implementation. It considered wrong baselines, proxy promotion, missing stops, unfair comparisons, hidden defaults, stale saved output, environment mismatch and whether artifacts answer the question.

| Diagnostic role | Predeclared use |
|---|---|
| Primary pass criterion | All 23 notes have anchored dispositions, linked quantities or specific unresolved meaning; selected source-bound bridges and independent arithmetic pass; mandatory adversarial cases reject for intended reasons. |
| Acceptance veto and repair trigger | Missing or ambiguous required sources, altered hashes/quotations, unsupported contexts, broken relationships, failed arithmetic, stale output or missing mandatory tests. Repair and rerun affected checks. |
| Continuation veto | Essential inputs or extraction invalidity preventing the bounded case. None remains. |
| Explanatory only | Coverage counts, test counts, elapsed time and selected-table agreement do not prove complete semantics, accounting compliance, publication vintage or forecast validity. |
| External limitations | Missing agreement or publication evidence blocks dependent claims; independent work continues. |
| Preserved result | case.json, this note, tests/test_accounting_p02.py and progress.md. |

The first expanded run exposed test-fixture errors involving nonbreaking spaces in operative headings, repeated debt labels in separate schedules and an unattached mutated fact. Corrections narrowed the independent checks to the intended source sections without altering retained sources. Subsequent runs passed. These were fixture repairs, not failures of the accounting identities.

## Material assumptions

| Choice and provenance | Justification/status | Failure mode and earliest diagnostic |
|---|---|---|
| Exact rational USD; approved plan | Reviewed arithmetic representation; annual millions and interim tag scales remain explicit. | Scale/sign confusion; literal, tag and mutation checks. |
| Closed half-unit intervals; approved plan | Compatibility hypothesis; issuer tie rule and exact underlying amounts unknown. | False rounding acceptance; exact touching and disjoint fixtures with valid sources. |
| Consolidated US GAAP; filing policies | Source-supported case annotation, not a general XBRL default. | Entity/currency/perimeter/date/dimension mixing; strict contexts and independent HTML checks. |
| Fiscal durations; Note 1 and table dates | Case derivation preserves 52/53-week years. | Calendar-year or opening-date substitution; dated stock/flow rejection. |
| Separate product/geographic partitions; filing tables | Each is a distinct exhaustive revenue partition. | Double counting or invented cross-tab; mixed-axis and member rejection. |
| Existing pdftotext/BeautifulSoup | Environment compatibility assumption; no installation. | Changed offsets or parsing; exact text regeneration and original-ID validation. |
| Filing identity distinct from retained bytes; index/acquisition records | Date-resolution filing query; no inferred historical byte date. | Backdated proxy or automatic supersession; cutoff, unknown and conflict tests. |

## Implementation and checked results

scripts/apple_case_v1.py extracts values from pinned inputs, resolves contexts and IDs, retains quotations, reconciles exact amounts and rebuilds supplied cases to reject metadata changes. This repair adds complete-span containment with original/extraction hash identity, validates note links against observation sources, validates anchors before reconciliation and records recovery-plan provenance. Existing substantive Section 501, Exhibit 4.1 and issuer-cell repairs are regression-tested.

The tests obtain fresh pdftotext stdout and independently parse annual balance-sheet, debt, PP&E, revenue and cash-flow rows. They independently resolve every selected interim reading against real HTML concepts, contexts, units, dimensions, periods and amounts. Valid synthetic sources isolate numerical rounding rejection from real-source corruption.

| Checked relation | Result |
|---|---|
| Annual debt, USD millions | 97,341 − 321 − 358 = 96,662; 10,912 + 85,750 = 96,662. Comparative debt also checked. |
| Interim debt, USD millions | 10,848 + 83,956 = 94,804. Operand interval [94,803, 94,805] overlaps narrative 94.8 billion interval [94,750, 94,850]. The displayed difference is 4 million; conclusion is compatibility. |
| Annual PP&E | 119,128 − 73,448 = 45,680, matching the statement; comparative bridge also passes. |
| Revenue | Annual 2024/2023/2022 and interim current/comparative product and geography partitions each independently sum to consolidated revenue. |
| Cash | Opening cash including restricted cash plus signed movements equals closing cash. Annual opening 30,737 cannot be replaced by cash-only 29,965. |
| Source/context rejection | Missing/duplicate/reordered notes, final boundaries, complete-span/wrong-note/extraction links, quotation/hash/ID failures, scale/sign/currency/entity/perimeter/date, duplicate dimensions and conflicting readings. |
| Measurement rejection | Mixed product/geography aggregation, fair-value/notional substitution for carrying debt and cash-perimeter substitution fail. |
| Issuer representation | Six selected current-year cells agree; comparative/date/column, ambiguity and altered-value tests pass. Whole-document equivalence remains unestablished. |
| Temporal evidence | Later proxy excluded at annual filing cutoff; unknown byte vintage stays unknown; competing versions retained without automatic supersession; metadata edits rejected. |

Executed sequentially, in foreground:

1. `timeout 120s python3 -B scripts/apple_case_v1.py --output-dir data/accounting-master/deliverables/P02` — exit 0.
2. `timeout 120s python3 -B -m unittest discover -s tests -p test_accounting_p02.py -v` — exit 0; 20 tests passed in 19.530 seconds.
3. `timeout 120s python3 -B scripts/apple_case_v1.py --check --output-dir data/accounting-master/deliverables/P02` — exit 0; 23 notes, 125 observations, 34 reconciliations and 698 anchors pass.

Full outputs are retained in /tmp/accdsl-p02-repair; this note preserves the relevant outcomes. No controller, model worker or master runner was launched.

## Incorporation and publication evidence

The retained acquisition manifest records legitimate issuer-feed routes to the 2025 proxy, official annual HTML and 2021 shelf registration; originals and extracted text are locally preserved and hash-checked. A prior direct 2021 exhibit route timed out; the successful issuer-linked registration contains the indenture. This repair required no new acquisition.

Annual Part III Items 10–14 link annual incorporation passages to selected proxy passages covering board independence, compensation, beneficial ownership, related-party policy and audit fees. The ownership passage is dated January 2, 2025. These passages do not complete item-level semantics. The case preserves 70 annual/interim exhibit-index records with exact targets, versions, missing terms, consequences and routes; missing internal targets remain visible.

In the registration extraction, the indenture title is at offsets 97,710–97,845, substantive Section 301 at 151,482–162,742 and Section 501 at 190,993–194,649, ending at Section 502. Section 301 leaves principal/payment, interest and redemption terms to series-specific instruments. Section 501 includes series qualifications and conditional payment, covenant and insolvency defaults; no default occurrence is asserted. Annual Exhibit 4.1 contents are anchored separately from the index entry.

| Outstanding obligation | Specific missing evidence and next legitimate route |
|---|---|
| Annual Exhibit 4.2, April 29, 2013 indenture | Full terms/applicability uninspected; accession 0001193125-13-179942, d527270dex41, via SEC or issuer archive. |
| Annual Exhibit 4.19, November 5, 2018 indenture | Full terms/applicability uninspected; accession 0001193125-18-317844, d644900dex41. |
| Series certificates, including 4.27/4.28 | August 8, 2022 and May 10, 2023 certificates indexed but not acquired; routes 0001193125-22-214914 and 0001140361-23-023909. Current allocations, amendments and swap confirmations remain unknown. |
| Item 601(b)(4)(iii) omitted instruments | Filing expressly omits instruments; identities/terms cannot be invented. Inspect identifiable public issuer/SEC filings; no outreach. |
| Remaining proxy/exhibit semantics | Inspect retained proxy sections and exact case-index targets; index links and selected passages do not close incorporation. |
| Historical versions | Filing/acceptance metadata and 2026 retrieval do not establish historical availability of these exact bytes. Seek archived byte-specific evidence; selected-cell agreement is insufficient. |

Missing contract evidence prevents complete debt-contract reconstruction. Debt/swap allocation and resets, noncash debt movements, asset cohorts and contingent outcomes remain unidentified. Notional is not recast as floating-rate exposure; management's loss assessment is not a zero liability or probability distribution. No company forecast is generated.

## Decision and limits

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Submit bounded implementation for review | Dispositions, bridges and independent/adversarial checks pass | No remaining observed mandatory-check failure | Further source/annotation defects remain possible | Review actual adapter, tests and case | Whole-gap or semantic closure |
| Retain selected accounting identities | Source readings and exact arithmetic/rounding checks pass | Source/context/measurement mutations reject | Histories and issuer rounding tie rule | Extend only with sourced evidence | Accounting compliance or fully identified company history |
| Keep incorporation/version obligations open | Specific targets and missing evidence retained | Missing terms veto dependent claims | Series terms and historical byte availability | Follow exact public routes | Complete agreement package or historical publication equivalence |
| Forecast/human acceptance pending | No forecast criterion evaluated | No promotion claimed | Predictive performance and human acceptance unevaluated | Independent result review | Forecast validity or human acceptance |

Post-run red-team: mutually consistent annotations on limited rows remain the strongest alternative explanation for success. Independent extraction and perimeter checks reduce this risk without eliminating it. A source/column mismatch or omitted qualification would overturn the corresponding result. Full semantics, contract applicability and historical versions are the weakest evidence and remain unresolved. These deterministic checks support no stochastic ranking or numerical default promotion.

## Run manifest and changed files

- Earlier report timestamp origin: 2026-10-02T20:57:58Z; this is not a verified subprocess start. Manifest recorded: 2026-10-02T21:10:11.260754+00:00. The structured repair-1 process record reports 463.43 seconds of worker-process wall time.
- Python: /home/chakwong/miniconda3/envs/tfgpu/bin/python3, version 3.11.15; existing tfgpu environment; BeautifulSoup 4.14.3; pdftotext 22.02.0.
- Platform: Linux-6.6.87.2-microsoft-standard-WSL2-x86_64-with-glibc2.35. CPU text parsing/exact arithmetic only; no TensorFlow/JAX/PyTorch import and no GPU/CUDA detection or use. GPU hiding N/A for these non-accelerator imports.
- Git commit unavailable: existing marker is not a usable repository. No initialization or commit attempted. Seeds N/A: deterministic checks.
- Data version: original/extraction pins, P01 register and acquisition URL/hash/retrieval evidence retained in case.json.
- Plans: data/accounting-master/runs/20261002T181809-4cb566e0/P02/approved-plan.json; data/accounting-master/runs/20261002T201419-9b58ed81/P02/approved-plan.json; data/accounting-master/runs/20261002T205123-6b8e9a16/P02/approved-plan.json. Latest review: data/accounting-master/runs/20261002T205123-6b8e9a16/P02/review_plan-0.response.json.
- Original plan SHA256: 916a4c80553bebee3ca0b6399ba8d4e54a6f5d3bd2975cda75815b95e8f45f59. Recovery plan SHA256: 569a45ba5ce7d75d1e71ba5fc5a870de38f5dedcc7b6d81aa74b4f135f815bcd.
- Outputs: data/accounting-master/deliverables/P02/case.json, result.md and progress.md; tests/test_accounting_p02.py.
- Protected baseline: 211 source/release/controller/snapshot hashes unchanged. Sorted mapping digest: 453c3a97479d652817a29b7da30fad4df6e28368ad1304b931c1b5dd3cadc625. Full mapping retained locally in /tmp/accdsl-p02-repair/baseline.json.

Files changed in this recovery: adapter, tests, case, progress and this result note. No new source acquisition. This result note excludes its own hash to avoid self-reference; progress.md records its final hash.

| Changed implementation/output file | SHA256 |
|---|---|
| scripts/apple_case_v1.py | cd4de03bb9e574064ba79b7df2fe0ed868a1e36b59d5afe0eccdf3cdb6e6017f |
| tests/test_accounting_p02.py | c9b7355b7c56ca15422d665d531a4fb61f9788922a8754f3f917c6ddaa702028 |
| data/accounting-master/deliverables/P02/case.json | 52cea992b880e6bbba3d861cd59eded7fbe4712fce07b3fceff0ebc566799f81 |

Initial recovery hashes:

| File | SHA256 before repair |
|---|---|
| scripts/apple_case_v1.py | 1f5e179aff639a1e42db889fb06be98c3aa8a26542811104938328623b5e4bd8 |
| tests/test_accounting_p02.py | f2007952418118ff67fa55978d75e00eca8a86bb983514e51f9b94f486bf60f8 |
| data/accounting-master/deliverables/P02/case.json | f022beefa07a4737ccb392458e0d4cdf04085cf0dcb2a6b369b0c1a561033b99 |
| data/accounting-master/deliverables/P02/progress.md | 8377893c46e894291e0164be2674470a4e686fd31958ce721bc4373b38146301 |

Earlier phase source additions retained unchanged in this recovery:

| File | SHA256 |
|---|---|
| docs/design/cases/apple/p02-v1/acquisition.json | ac579dfc86edbf1aef69657135406fa54563d64c64352daa19a6ad31346e612c |
| docs/design/cases/apple/p02-v1/annual-2024-official.txt | 52994e20bd190ab19d986c5b8b30de24816aeec509d918a8752507d37479bf87 |
| docs/design/cases/apple/p02-v1/issuer-2021-feed.json | 0a74eb267708d32287b4734001c20392f08fcc40ad57e60543c32289a9ffe065 |
| docs/design/cases/apple/p02-v1/issuer-2021-s3asr-feed.json | e1562416c021469d9e778a5fc1f1daed23fd64bf636b379a61d949e2273a0127 |
| docs/design/cases/apple/p02-v1/issuer-2024-feed.json | d6efd8550a1a6e573e69f57ff67d98ff0e022a7cca65024e239b8cd762fbc93a |
| docs/design/cases/apple/p02-v1/issuer-2025-feed.json | f4daae3b22170e9691e0ca38cc7c489504bfbf3a59f9afaa1135b911b1716a4a |
| docs/design/cases/apple/p02-v1/proxy-2025.txt | bb1a2854d6e328634dbfd87383cc9dccb6537c809b3832c67b6ba63c0c5feba9 |
| docs/design/cases/apple/p02-v1/registration-2021.txt | 0736f98e4676e0111803445efce78b9bf4c3db33b1730feaa8272445edc46285 |

## Final verification record

Recorded 2026-10-02T21:11:18.538325+00:00. The earlier 800.5-second figure used an unverified timestamp origin and must not be read as worker-process runtime. The supervisor record at data/accounting-master/runs/20261002T205123-6b8e9a16/P02/execution-1/repair-1.process.json reports 463.43 seconds, exit 0 and no failure reason.

| Exact command | Exit | Wall seconds |
|---|---|---|
| timeout 120s python3 -B scripts/apple_case_v1.py --output-dir data/accounting-master/deliverables/P02 | 0 | 2.668 |
| timeout 120s python3 -B -m unittest discover -s tests -p test_accounting_p02.py -v | 0 | 19.927 |
| timeout 120s python3 -B scripts/apple_case_v1.py --check --output-dir data/accounting-master/deliverables/P02 | 0 | 2.803 |

Final suite: 20 tests passed in 19.714 seconds. CLI report: {"anchors": 698, "notes": 23, "observations": 125, "reconciliations": 34, "status": "pass"}.

A further independent in-memory build exactly equals the saved case. All 211 recorded protected files remain unchanged. Comparison: {"case_sha256": "52cea992b880e6bbba3d861cd59eded7fbe4712fce07b3fceff0ebc566799f81", "protected_changes": [], "protected_files": 211, "second_build_equal": true, "wall_seconds": 2.391}.

The required case, result and test files exist and the checkpoint is current. No mandatory repair is left known in this bounded implementation. Broader semantic, incorporated-package, unidentified-history, publication-vintage, forecast and human-acceptance residuals remain as specified above. Independent review_result remains the next acceptance step.


## Recovery verification: execution-2/repair-2

Verified on 2026-10-02T21:35:44.924810+00:00. The supplied recovery snapshot correctly reported all required files present. The adapter, tests, case and prior result initially matched their recorded SHA256 values. The structured review at data/accounting-master/runs/20261002T205123-6b8e9a16/P02/execution-1/review_result-1.response.json returned AGREE with issues=[]; its accompanying process record reports exit_code=0, reason=timeout and wall_seconds=240.048. The review content supports the bounded result, while the supervisor timeout leaves process acceptance pending. No controller status is inferred or changed.

The skeptical audit was recorded in progress.md before executing these checks. It retained the approved plan, original PDF/HTML comparators, source/context/rounding acceptance criteria and repair triggers. Coverage counts and a prior AGREE were not used as substitutes for file verification. No scientific experiment or comparison of methods was performed; the deterministic evidence contract and material assumptions above remain applicable.

| Exact foreground command | Exit | Wall seconds |
|---|---|---|
| timeout 120s python3 -B scripts/apple_case_v1.py --output-dir data/accounting-master/deliverables/P02 | 0 | 2.577 |
| timeout 120s python3 -B -m unittest discover -s tests -p test_accounting_p02.py -v | 0 | 19.965 |
| timeout 120s python3 -B scripts/apple_case_v1.py --check --output-dir data/accounting-master/deliverables/P02 | 0 | 2.79 |

The suite passed all 20 tests in 19.797 seconds, with no failures, errors or skips. The default temporary directory worked in this repair environment; the earlier review's read-only /tmp limitation is specific to that review environment. Full command outputs and structured timings are retained under /tmp/accdsl-p02-recovery-2; this declared result file preserves the substantive evidence.

The further in-memory source rebuild equals case.json exactly. Both implementation modules compile through Python's compile() without writing bytecode. Source and acceptance assertions pass: 13 annual and 10 interim notes, 125 observations, 34 reconciliations, 698 valid anchors and 70 exhibit-index records; nine notes link quantities, and all 23 preserve unresolved meaning. Selected operative indenture Sections 301 and 501 and the Exhibit 4.1 contents remain separate from summaries/index rows. The retained issuer acquisition records identify official public routes, and the unchanged case retains specific missing indentures, series terms, omitted instruments and byte-vintage evidence. None of these checks establishes complete note semantics.

Both protected-file comparisons pass: all 829 files captured in this attempt and all 211 files in the earlier baseline are unchanged. The new sorted mapping digest is 4f24d5e466b7bffcf30747dbe712a5b2a57a9f03d636cfd67b03d6c68c9ecf70; the earlier mapping digest remains 453c3a97479d652817a29b7da30fad4df6e28368ad1304b931c1b5dd3cadc625. Baselines and comparison details are retained in /tmp/accdsl-p02-recovery-2/baseline.json and verification.json. No new source acquisition occurred.

This attempt regenerated case.json with identical bytes and edited only result.md and progress.md to record verified state and correct the runtime attribution. The adapter and tests required no further repair; their existing hashes and all earlier source hashes above remain valid. The pre-edit result hash was 19bae0478422abfdd7b2896fc0ce61f6bd80614912f4c24c0361f0e20bb247ff; the pre-edit checkpoint hash was af0e10aa16977171b245a6a217e9b815564c0ff8b2ddb0be4a1cf329f67df66e. The checkpoint records the updated result hash, avoiding self-reference here.

Run provenance: /home/chakwong/miniconda3/envs/tfgpu/bin/python3 (3.11.15), BeautifulSoup 4.14.3, pdftotext version 22.02.0, Linux-6.6.87.2-microsoft-standard-WSL2-x86_64-with-glibc2.35. CPU text parsing and exact arithmetic only; no accelerator framework was imported. Random seeds and ML data splits are inapplicable. git rev-parse --verify HEAD returned 128 because the existing marker is not a usable repository; no Git provenance was fabricated. Data versions and input/output paths remain those recorded above and in case.json. Plan provenance remains data/accounting-master/runs/20261002T205123-6b8e9a16/P02/approved-plan.json (plan SHA256 569a45ba5ce7d75d1e71ba5fc5a870de38f5dedcc7b6d81aa74b4f135f815bcd). First captured baseline: 2026-10-02T21:30:04.289004+00:00; elapsed to this note: 340.6 seconds. This interval is explicitly local observation time, not a supervisor-measured process runtime.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Preserve and resubmit bounded P02 implementation | Actual deliverables, source checks and all 20 tests pass | No observed implementation veto; previous review process timed out | Supervisor acceptance and additional source/annotation defects | Supervisor performs bounded result review of current files | Whole-gap closure or human acceptance |
| Preserve external and history residuals | Specific missing evidence and exact routes remain recorded | Missing terms and byte-vintage evidence block dependent claims | Uninspected instruments, unidentified histories and historical availability | Continue those internal source tasks in their authorised slices | Complete agreement reconstruction, historical byte availability or any forecast |

No mandatory P02 implementation deliverable remains unfinished under the reviewed bounded criteria. Accounting evidence remains limited to selected source-bound identities and rounding compatibility. Forecast validity is unevaluated, human acceptance is pending, and all G1-G18 retain their wider obligations. A newly demonstrated source mismatch or missing required invariant would trigger a focused repair; the previous reviewer timeout alone does not demonstrate such a mismatch.
