# P11 execution record

Status: repaired bounded implementation; deterministic checks pass; independent result acceptance pending. MC23, MC25, MC31; G2/G9 remain open. Zero external integrations completed.

## Pre-execution evidence contract and research intent

Question: do captured upstream exchanges preserve declared semantics, and do independently authored DSL and typed programs produce the same accounting execution? The mechanism is validated P03 IR interpreted by one DemoDebt runtime. Comparators are the retained core-contract exchange specifications, DemoDebt@1, and independent rational arithmetic. Promotion requires actual upstream execution for an adapter and semantic/oracle agreement for matched frontends. Missing dependencies veto only the affected integration. Semantic mismatch is a repair trigger. Invalid harness, corrupted protected inputs or fabricated evidence are continuation vetoes for the affected run. Elapsed times and test counts are explanatory only. No accounting compliance, forecast validity, performance ranking, human authoring advantage or wider gap closure follows. Artifacts: integrations.json and this result.md. Seeds: N/A; deterministic cases. No stochastic comparison is planned.

Baseline ladder: identical typed and textual tasks share packages, evidence bindings, runtime and accounting methods; an independent rational oracle guards common runtime errors. This is conformance testing, not a method-performance comparison. Expected failures include absent engines and invalid contexts; these do not stop independent frontend work.

## Skeptical audit before implementation

Passed for this bounded execution: approved revised plan resolves both review objections. Environment will be rediscovered, all ledger candidates recorded in Beancount → Ledger → hledger order, selected versions frozen before exchange, no fallback after selected execution failure. No proxy metric is promoted. Thirty-second subprocess limits bound diagnostics; final 120 seconds reserved for checks/reporting. Retained-source inspections and imports cannot count as integration. Shared-runtime agreement is insufficient without independent arithmetic and poisoned-expected-value tests. A potential misleading pass is two frontends sharing a runtime bug; the independent oracle and variations are the early diagnostic. Missing assets may fail conversion without invalidating Docling as a research direction.

## Recovery audit before the final repair

The structured timeout record does not establish acceptance. Recovery inspection verified both deliverables, all nine fixture files, the 19/11 recorded test results, the call chain into the shared runtime, and current file hashes. The original evidence contract and baseline are retained.

Inspection found that a failed ledger discovery probe could be collapsed into an Unavailable family when no candidate was selected. The repair preserves Failed and its candidate reasons without selecting an unqualified backend. Extraction diagnostics/partial conversion and mismatched valuation dates must also veto the affected exchange even when expected cells or a present value happen to match. These are fail-closed reporting/validation repairs; they do not change accepted DemoDebt arithmetic or the environment policy. The focused regression tests and complete P11/P03 checker subsequently passed; their exact commands and results are retained in integrations.json. Missing external engines remain a scoped dependency limitation, not a reason to skip feasible deterministic checks.

## Material default and assumption audit

Environment audit — provenance: prior plan observed /home/chakwong/miniconda3/envs/tfgpu/bin/python3, Python 3.11.15. Justification: reuse the existing interpreter without installation. Failure mode: stale discovery or interpreter drift. Earliest diagnostic: record sys.executable, Python version, dependency metadata and executable paths before imports. Status: environment baseline, reverified by implementer.

CPU audit — provenance: project GPU policy and this deterministic slice. Justification: no accelerator is needed. Failure mode: automatic device initialization or asset retrieval. Earliest diagnostic: set CUDA_VISIBLE_DEVICES=-1 before imports and inspect selected conversion settings. Status: convenience choice; record intentional GPU hiding.

Timeout audit — provenance: prior plan's 30-second subprocess limit. Justification: bound each version probe/exchange within the worker budget. Failure mode: rejecting a functioning but slow engine. Earliest diagnostic: retain timeout stage, elapsed time and partial output. Status: convenience limit, not a capability or performance criterion; timeout records Failed with a timeout reason, never Unavailable.

Arithmetic/calendar audit — provenance: DemoDebt@1 and core-contract exchanges. Justification: preserve the specified synthetic comparator. Use rational USD calculations, cent half-even posting rounding, annual-simple rates, explicit one-year accrual and package dates; QuantLib separately uses Actual/365 Fixed, annual-effective yield, NullCalendar and unadjusted dates. Failure mode: mixed rate conventions, double rounding or shifted dates. Earliest diagnostic: verify year fractions, half-cent ties, payoff signs and exact baseline amounts. Status: fixture baseline, not a general accounting default.

Tolerance audit — provenance: prior plan's QuantLib check against rational PV 100. Justification: USD 1e-10 absolute tolerance is narrowly bounded for this small double-precision calculation. Failure mode: concealing a convention error or generalizing the threshold. Earliest diagnostic: retain raw PV, absolute error and computed year fraction. Status: test hypothesis; never loosen after failure without revising the recorded rationale.

Dependency/access audit — provenance: worker restrictions and prior local-discovery findings. Justification: use existing or already retained project-local engines/assets without downloads, accounts or installation in this slice. Failure mode: confusing missing assets with broken software or overstating availability. Earliest diagnostic: inspect local paths, exact versions, required assets and offline configuration. Status: bounded execution choice; absent capability stays unavailable.

Selection audit — provenance: core-contract names Beancount as the concrete-journal comparator. Justification: deterministic order Beancount, Ledger, hledger supports reproducibility. Failure mode: opportunistic substitution or version/path ambiguity. Earliest diagnostic: inventory every candidate and apply the explicit discovery rule in step 3. Status: engineering choice, not evidence that one backend is superior.

Frontend/oracle audit — provenance: P03 compilation interfaces and DemoDebt package. Justification: independent textual and typed inputs share accounting methods and runtime while rational equations constrain common bugs. Failure mode: copying authored expected values or relying only on frontend agreement. Earliest diagnostic: poison expected values and vary principal, stress and composition. Status: matched engineering baseline.

## Execution results

The artifact checker completed with exit status 0 at 2026-10-03T07:37:16.417799+00:00. Its retained subprocess records show **21 P11 tests and 11 P03 prerequisite tests passing**. Six independently authored DSL/typed cases have equal semantic projections and equal execution results under the same validated P03 IR, package, bindings, accounting methods and DemoDebt runtime. Each case also passes a separate Decimal arithmetic oracle. Complete commands, input programs, bindings, outputs, test stdout/stderr, environment and hashes are in `integrations.json`.

| Matched case | Interest USD | Closing cash USD | Debt USD | Profit USD | Equity USD | Result |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| fixed | 5 | 90 | 100 | -5 | -10 | Completed |
| floating | 7 | 88 | 100 | -7 | -12 | Completed |
| interior | 13/2 | 177/2 | 100 | -13/2 | -23/2 | Completed |
| changed_principal_stress | 12 | 133 | 150 | -12 | -17 | Completed |
| renamed | 7 | 88 | 100 | -7 | -12 | Completed |
| insufficient_cash | 5 | 4 | 100 | 0 | -96 | Defaulted |

Fractions are exact USD amounts. The interior case explicitly conditions the fixed fraction on 1/4 and assigns no probability. The changed-input case uses principal 150 and an 8% floating rate. The insufficient-cash case retains an unpaid interest obligation of 5, commits only the reset event and produces no partial settlement or closing postings; its statements are explicitly incomplete. Its reported zero recognised profit is the halted DemoDebt state, not a claim about the accounting treatment of a real default.

The runtime consumes principal, composition, rates, opening state, scenario and alternative constraints from validated IR. It implements only the locked DemoDebt method and Gregorian 2026 annual horizon. It rejects unsupported currency/calendar/package semantics, invalid contexts and branch violations. Tests cover altered principal/stress, conditioned interior values, renamed declarations, formatting, exact half-even ties, insufficient cash, branch isolation, replay/conflict identity and unbalanced posting rejection. Poisoned expected values are tested in a temporary package root: P03's fixed package-path check remains active, both frontends still execute interest 5, and the protected package stays unchanged.

The repair corrected binary-float conversion of decimal principal inputs and fixed that isolated poison-test setup. Negative adapter tests now reject missing execution evidence, changed version pins, malformed/timeout responses, incorrect numerical/context/journal semantics and modified fixture hashes. All ledger-discovery combinations and no substitution after selected-backend failure are exercised. The final recovery repair also preserves failed ledger discovery as Failed, rejects mismatched valuation dates and rejects Arelle loader errors or partial Docling conversion even when expected values are present. Those simulated records are boundary tests only and are absent from the actual integration records.

## Adapter outcomes

| Family | Discovery result | Exact runtime version | Actual exchange |
| --- | --- | --- | --- |
| Arelle | Python module absent | null | None; Unavailable |
| ACTUS | Executable absent from captured PATH; declared local JAR candidates absent | null | None; Unavailable |
| QuantLib | Python module absent | null | None; Unavailable |
| Docling | Python module absent | null | None; Unavailable |
| Ledger family | Beancount, Ledger and hledger all absent | null | None; selected backend null |

**Zero external integrations completed.** The inventory is scoped to the recorded Python interpreter, PATH and declared local ACTUS paths; it does not establish absence from every environment on this machine. Import/version probes cannot count as exchanges. No dependency, model asset or service was downloaded or installed, and no network service was called. Runtime pins and outputs remain null for missing engines. Retained software-source versions and hashes are separate evidence and are never substituted for executable engine versions.

Input records preserve literal bytes, hashes and conventions. They include a synthetic XBRL instance with duplicate values and a nil, a minimal locally authored taxonomy stand-in, locked PAM terms, a one-year valuation request, a small HTML table and concrete journal files. The local taxonomy is a bounded loader fixture, not an official complete XBRL schema or compliance test. The Docling input is HTML and has no physical pagination; the approved one-page PDF/table-location exchange and inline-XBRL scale check remain unfinished. ACTUS and Ledger/hledger wire translators also remain unimplemented. Arelle, QuantLib, Docling HTML and Beancount call paths have been authored but **not exercised against upstream engines**. Engine-specific compatibility, extraction completeness and accounting validity are not established by these files or mocks.

## Decision and evidence limits

| Decision | Primary criterion | Veto diagnostic | Main uncertainty | Next justified action | What is not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain bounded matched-frontend implementation for review | All six execution/oracle cases pass; 32 tests pass | No observed semantic mismatch; protected hashes match phase entry | Small common runtime and synthetic method | Independent result review; extend only against explicit requirements | General language equivalence or authoring superiority |
| Keep every external integration unavailable | Captured upstream exchange criterion unsatisfied | Missing engine vetoes each integration only | Compatibility and offline assets untested | After a known availability change, pin the actual version and execute the recorded exchange | Integration completion, library inferiority or research-direction rejection |
| Preserve wider obligations | No wider acceptance attempted | No scientific/accounting/human acceptance evidence | Real accounting treatments and empirical outcomes | Continue authorised domain and validation phases | G2/G9 or MC01–MC35/G1–G18 closure |

Specified behaviour, implemented code and tested invariants are separate: the synthetic runtime is implemented and checked; several adapter boundaries are authored but unexercised; all upstream executions remain unavailable. Professional accounting validity is unestablished, empirical forecast validity is unevaluated, and human acceptance is pending. No performance, stochastic ranking or human authoring/usability advantage is inferred.

Post-run red-team: the strongest alternative explanation for frontend agreement is a shared compiler/runtime defect. The independent arithmetic oracle, changed inputs, poison test and rejection cases constrain that explanation but cannot establish general correctness. A reproducible accepted-input counterexample or failed actual upstream exchange would overturn the affected engineering conclusion. The weakest evidence is upstream compatibility: no external engine ran. Missing dependencies reject current integration completion, not the research direction.

## Reproduction and provenance

Run from the project root:

```text
PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=-1 python3 -B -m unittest discover -s tests -p 'test_accounting_p11.py' -v
PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=-1 python3 -B -m unittest discover -s tests -p 'test_accounting_p03.py' -v
PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=-1 python3 -B scripts/check_accounting_p11.py --output-dir data/accounting-master/deliverables/P11
```

The checker executes both test commands and retains their outputs. GPU devices were intentionally hidden. Seeds are N/A for deterministic checks. No claims depend on elapsed time. The manifest records the actual interpreter/Python version, environment, CPU setting, exact commands, observed project Git commit, source/input hashes, plan/result paths and wall time. Unlike the older checkpoint's unusable-Git observation, this run's read-only Git probes succeeded and resolved to the AccDSL root; content hashes identify the executed working files, which are not asserted to match that commit.

All protected package/compiler/controller files checked by this slice match the supervisor's phase-entry inventory and remained unchanged through the run. No controller, catalog, master plan, frozen corpus or preserved snapshot was edited. Source/test/fixture contributions are listed in the manifest; phase deliverables are integrations.json, result.md and progress.md. No professional outreach, paid service, deployment or publication occurred.
