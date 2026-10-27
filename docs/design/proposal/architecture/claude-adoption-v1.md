# Disposition of Claude's proposed additions

The useful contribution is a clearer structure for specifying accounting methods
and preparing filing evidence. Adopt that structure with the repairs below.
Claude's original chapters and response remain external drafts. The active
candidates are the repaired specifications linked here; none enables product
implementation or establishes full proposal acceptance.

The response accepts the earlier findings but leaves a defective revenue repair:
Dr ContractAsset 10 / Cr Revenue 60 plus Dr Receivable 50 / Cr Billings 50 has
debits 60 and credits 110. The replacement specifies the whole revenue/billing
sequence. Also, AASB 9 B5.4.8 describes included/excluded transaction costs;
recognition follows the applicable measurement rules and facts. Source inspection,
arithmetic, semantic review, runtime checks and professional review have separate
statuses. MC35 requires feasible internal preparation before any paid review.

| Idea or claim | Final disposition | Active candidate and remaining obligation |
| --- | --- | --- |
| Eight-part accounting mapping | Adopt as a method-record structure, with versioned authority, facts, timing, measurement, state/journals, presentation, examples and evidence. | [Standards mapping](../methods/standards-mapping-v1.md). P16 must complete accounting/interface contracts; P17 must fill substantive domain methods. |
| Eight extraction stages | Adopt, with immutable source occurrences, contextual assertion identity, explicit reference budgets and retained unknowns. | [Extraction contract](extraction-contract-v1.md) and [fixtures](extraction-fixtures-v1.json). Integrate with P16 evidence/time/interfaces/persistence. |
| Acquisition, rates, impaired assets, revenue and cumulative costs | Replace the defective examples with source-scoped rules and independently checked calculations. | [Standards fixtures](../methods/standards-fixtures-v1.json) and [source register](../methods/standards-source-register-v1.json). The examples apply to stated historical facts; full lifecycle and current applicability remain P17 work. |
| Exact sources, preconditions, alternatives and failures | Adopt. A balanced journal is necessary but cannot establish treatment eligibility. | Sources distinguish inspected text from local deductions. P17 must supply missing authority, transitions and competing interpretations. |
| Repeated-event handling and review history | Adopt as proposed behavior. Identical replay returns its original receipt; conflicts and stale new requests do not post. | Standards and extraction contracts. P16 still owes portable identities, atomicity and concurrency semantics; no transaction engine was tested. |
| Coherent work groups | Adopt. Complete substantive contract sections with representative success/failure examples and timely partial saves. | Resume uncertainty integration, then accounting, language/interfaces, persistence/failure semantics and profile decisions. Reuse completed supplements; group routine schema errors. |
| Broad absent-implementation claims | Reject the stale baseline. | P03/P04 bounded prototypes and the 192-report corpus remain evidence with their recorded limits. No new acquisition campaign replaces them. |
| Reviewed/complete, feasibility and production claims | Reject without named evidence. Internal reviews remain useful while domain/human acceptance is pending. | P19 requires complete contracts, methods, worked cases and independent result review. No mandatory paid CPA stage is introduced. |
| 410 pages, 24 chapters, staffing/time estimates | Do not adopt as requirements or completion evidence. | P18 must build and inspect one integrated manuscript whose length follows the argument and specification. The original incomplete TeX skeleton is preserved as review input. |
| Fixed accuracy percentages, FinBERT, confidence/depth thresholds, performance targets | Do not adopt as defaults. | P17 must inspect candidate adapters and define target-task evaluation, denominators, strata and calibration on the retained corpus before selection. Detected unsupported readings cannot enter accepted source facts. |
| Extra features such as regulatory filing generation | Optional proposals, outside mandatory acceptance unless separately justified. | Preserve MC01–MC35/G1–G18 as the governing scope. Forecast assessment must address conditional distributions/sets and information cutoffs. |
| Separate directory for concurrent authoring | Insufficient isolation for the master's worktree inventory. | Keep one writer during execution. Parallel authoring needs a separate checkout and controlled import between work windows; integrity checks stay intact. |

The bounded [diagnostic](../../../../data/accounting-master/claude-adoption-20261005/diagnostics.json)
passes 109 checks. It compares journals with independent balance equations,
checks positive/negative/zero effective rates, cumulative cost and receipt cases,
and inspects identity, traversal/resume and source locators. It reproduces the
original acquisition imbalance of −2 and the response's revenue imbalance of −50.
The 17 existing proposal tests also pass. These are deterministic specification
checks; no accounting, extraction or persistence runtime was implemented.

Current requirement assessments are partial: MC01–MC07/MC25/MC27 gain a concrete
extraction proposal; MC08/MC10/MC16–MC17/MC20–MC23/MC28 gain corrected method
examples; MC29–MC30/MC35 gain retained source/version support and explicit review
classes. MC32–MC34 gain a traceable integration obligation. No wider requirement
or gap closes here. The protected mission register and product checkpoint remain
historical baselines; current assessments are recorded in this note and P16.

P16 must integrate the candidates without marking accounting or interfaces
complete from these additions alone. P17 must cover leases, tax, groups/FX,
liabilities/equity, banks, insurers, IFRS/US GAAP/ASBE, forecasting and software
reuse with exact methods and source limitations. P18 must carry the repaired
reasoning and examples into the governing manuscript. P19 must reconcile this
disposition against that manuscript and retain unresolved professional/human
acceptance separately from internal preparation. All fourteen current proposal
decisions and the six unfinished P16 contracts remain open at this intake.
