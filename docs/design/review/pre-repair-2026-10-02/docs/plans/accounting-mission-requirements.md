# AccDSL mission requirements and acceptance evidence

Established 2 October 2026 (Asia/Hong_Kong).
Authority: [mission control](../../MISSION_CONTROL.md).
Scope: requirements for the governing design and the eventual product it
specifies. Current assessments concern the document, not implemented software.

## Provenance and assessment rules

- **U1:** original user request on heterogeneous annual/interim reports, all
  footnotes, accounting standards, industries, company labels, time, financial
  institutions, bonds and equities; saved-session record 10.
- **U2:** explicit request to preserve different possible journals,
  interpretations and scenario-dependent future distributions; record 115.
- **U3:** explicit request for a detailed governing LaTeX design, broad
  literature collection, open-source survey, concrete methods, DSL comparison
  and adherence to the user's policies; record 145.
- **P:** applicable scientific coding, literature and prose policies.
- **D:** a derived engineering/scientific requirement needed to make U1–U3
  concrete. It does not make the particular proposed implementation immutable.

The current instruction authorises installing this register as mission control.
It does not retrospectively approve every technical choice in the manuscript.
Traceability uses MC IDs to avoid confusing this register with the manuscript's
older R1–R10 summary. M1–M8 are goals in the root mission document. G1–G10 refer
to the [initial gap audit](../design/review/gap-audit-2026-10-02.md); G11–G18 refer
to the [expanded audit](../design/review/mission-gap-audit-2026-10-02.md).

`Partial` means the draft addresses the topic but its required design evidence
is incomplete. `Open` means the essential concrete deliverable is still absent.
`Specified` and `Checked` require explicit evidence and scope. An implemented
feature, accounting-valid treatment and empirically supported forecast each
need their own evidence; no design status implies any of them. The acceptance
column describes work to supply, not tests already performed. Chapter references
identify inspected evidence, not blanket certification of that chapter.

## M1 — Historical record and meaning

| ID | Requirement and origin | Evidence needed to complete the design | Current assessment and related gaps |
| --- | --- | --- | --- |
| MC01 | Account for complete annual, quarterly and semi-annual disclosure packages, including notes and relevant referenced material. U1, U3. | Define the source inventory, coverage units, cross-reference closure and disposition rules. A worked filing package must account for retained, structured, duplicated and unresolved content without treating page extraction as semantic completion. | Partial: Chapters 2 and 7 describe coverage/dispositions but do not instantiate the complete procedure. G5, G11. |
| MC02 | Preserve numeric meaning: entities, perimeter, concept, dimensions, currency, units, scale, sign, basis and precision. U1, D. | Complete context/value types and compatibility rules, with valid/invalid examples and faithful rendering of the original disclosed amounts. | Partial: Chapters 2, 6 and Appendix A have useful types but incomplete contextual and numeric contracts. G2, G3, G12. |
| MC03 | Represent narrative policies, qualifications, commitments and cross-references, including material that is not executable yet. U1, U3, D. | Specify narrative assertion types, modality/quantifiers, links to affected amounts and obligations, and reviewed translation into constraints without inventing thresholds. | Partial: Chapter 2 explains the issue; a complete schema, coverage example and semantics are absent. G2, G11. |
| MC04 | Separate reported assertions, extraction readings, derivations, assumptions and conflicts. U1, U2, P, D. | Define source/derived/assumed status propagation and conflict handling; show both extraction error and a genuinely conflicting disclosure without silently changing either source. | Partial: Chapters 2, 6 and 9 preserve the distinction in prose; decision/state contracts need completion. G2, G15, G17. |
| MC05 | Represent economic, reporting, publication/availability and system times; preserve original and revised history. U1, U3, D. | Specify original, latest-available and harmonised queries, cutoffs, supersession, calendar/interval rules and retrospective/prospective changes. Include exact annual/interim/restatement fixtures. | Partial: Chapters 2, 9 and Appendix A list fields/views but leave selection and transition rules incomplete. G2, G4, G13. |
| MC06 | Distinguish legal entities, ownership, control, group perimeter and consolidation. U1, D. | Provide dated entity/control and adjustment-book types, acquisition/disposal and intragroup examples, and rules preventing unexplained consolidation plugs. | Partial: Chapters 2 and 8 state requirements; the worked structural/accounting procedure is missing. G4, G7, G12. |
| MC07 | Align differing company labels and overlapping dimensions without equating unlike measurements or double counting. U1, D. | Specify concept/mapping relationships, applicability and aggregation rules; demonstrate company extensions and product/geography totals over the same population. | Partial: Chapter 2 names mapping kinds and Chapter 6 requests declared partitions; the operational mapping model is unfinished. G2, G12. |

## M2 — Histories, interpretation and uncertainty

| ID | Requirement and origin | Evidence needed to complete the design | Current assessment and related gaps |
| --- | --- | --- | --- |
| MC08 | Preserve jointly consistent discrete alternatives and continuous unknowns across accounts, notes and dates. U2, D. | Define history-family and choice/constraint semantics; provide cases preserving linked alternatives and rejecting incompatible combinations without independent account-by-account selection. | Partial: Chapters 5–7 supply the principle and simple example; complete construction/representation is absent. G1, G2, G15. |
| MC09 | Construct historical families through a specified method, with honest scope and search completeness. U2, U3, D. | Define candidate templates, model-scope records, instantiation and constraint lowering, feasible/infeasible/unknown results, truncation and coverage evidence. | Partial: Chapters 5 and 7 define the target set and procedural outline rather than a complete reconstruction algorithm. G1, G3. |
| MC10 | Distinguish uncertainty about facts, disclosure readings, admissible accounting treatment, estimates, behaviour and future shocks. U2, P, D. | Specify the categories, dependencies and admissibility checks; show why a factual unknown, permitted election and unsupported treatment cannot be substituted for one another. | Partial: the distinction is explained in Chapter 1 but does not carry through all records and APIs. G6, G15. |
| MC11 | Preserve the economic memory and scenario responses needed when histories are aggregated or refined. U2, D. | Define required state by contract/lot/cohort, permitted grouping transformations, supported horizon/scenarios, exact versus approximate status and invalidation when the query changes. | Partial: Chapter 5 defines equality of conditional laws; a usable resolution policy and tests are missing. G1, G16. |
| MC12 | Add probabilities only under an explicit justified joint measure, and retain unweighted alternatives when weights are unsupported. U2, P, D. | Specify optional weight/prior/likelihood records, dependence, overlaps, updates and mass preservation; provide a worked weighted and unweighted example with clear interpretation. | Partial: Chapter 5's mixture mathematics is useful; the probabilistic method and interface are not fully specified. G2, G6, G15. |

## M3 — Economic events, journals and forecasts

| ID | Requirement and origin | Evidence needed to complete the design | Current assessment and related gaps |
| --- | --- | --- | --- |
| MC13 | Drive economic events from contract state and explicit behaviour, then apply accounting rules and atomic journal/state updates. U2, D. | Specify one reference economic model, event payloads, recognition/measurement operations, preconditions, ordering and atomic transitions. Prove the stated bookkeeping invariant and separately define admissibility. | Partial: Chapters 5 and 7 give the invariant and execution abstraction; the complete reference model is absent. G2, G4, G6. |
| MC14 | Give scenarios and decision information explicit meanings. U2, P, D. | Define supported exogenous stress, observational-conditioning and intervention modes, or explicitly scope unsupported modes; enforce information dates and distinguish real-world from pricing measures. | Partial: Chapters 3 and 5 discuss the distinctions; scenario types and information-access contracts are incomplete. G6, G14. |
| MC15 | Specify ordinary corporate operations and accounting across periods. U1, U2, U3, D. | Provide a bounded coherent package for revenue/collections, purchases/payments, inventory/costs, assets/depreciation, payroll, financing and applicable closing/tax assumptions, with explicit exclusions. | Partial: Chapter 8 lists duties; complete rule and transition specifications are missing. G4, G5. |
| MC16 | Produce coherent financial statements, movements and supported note schedules from the same underlying history/path. U1, U2, D. | Define balance sheet, income/comprehensive income, cash flow and equity mappings, non-cash movements, closing and note relationships; supply a full set of expected outputs. | Partial: Chapters 5 and 7 define the reporting function and obligations, without a complete reporting package. G4, G5, G6. |
| MC17 | Represent financing instruments and their economic/accounting lifecycles, particularly bonds and equity. U1, U2, D. | Specify proceeds, principal, carrying/fair values, rates, calendars, maturities, rights and share quantities; work issuance, accrual, settlement and relevant modification/conversion/default cases under declared treatments. | Partial: Chapters 7 and 8 have basic financing examples and broader field lists; richer contracts and lifecycle rules remain open. G4, G7. |
| MC18 | Preserve joint conditional future outcomes, honest bounds and distinct failure/completeness states. U2, P, D. | Define result payloads and queries that retain branch/path dependence, distinguish sampled ranges from certified bounds and distinguish default from unsupported/numerically failed output without silent dropping or renormalisation. | Partial: Chapters 5, 7 and 9 express the right intentions; complete result and partial-execution semantics are missing. G2, G3, G6. |

## M4 — Standards, sectors and company variation

| ID | Requirement and origin | Evidence needed to complete the design | Current assessment and related gaps |
| --- | --- | --- | --- |
| MC19 | Accommodate IFRS, US GAAP and China GAAP/ASBE with dated treatments, elections and transitions. U1, U3. | Define the supported treatment matrix, rule authority and version selection; show matched economic events under selected genuinely different treatments and identify unimplemented operations. | Partial: Chapter 8 is primarily a scope statement, with overview sources and deferred primary-rule work. G7, G8, G13. |
| MC20 | Support materially different industry and company concepts without bypassing the common accounting semantics. U1, D. | Specify extension points, concept mappings and rule admissibility; include representative industry differences and an invalid company override. | Partial: Chapters 2, 6 and 8 describe layers but lack complete extension contracts and worked examples. G2, G7, G12. |
| MC21 | Represent banks' liabilities, assets, deposits, capital and regulatory/economic constraints. U1, U2. | Define core bank structural records now and operation-level later methods for funding, credit, liquidity and capital, including accounting/prudential reconciliation and an appropriate worked case. | Partial: Chapter 8 contains requirements and an illustrative credit-loss calculation, not a bank method specification. G7, G8. |
| MC22 | Represent insurers' contract groups, claims, service/finance components, assets and reinsurance. U1, U2. | Define cohort/group state and movements, declared measurement approaches and interfaces, reinsurance links and a complete structural/roll-forward example; expand actuarial/accounting support. | Partial: Chapter 8 names the necessary components; executable-method details and a worked cohort are missing. G7, G8, G16. |

## M5 — Concrete methods, DSL and implementation contracts

| ID | Requirement and origin | Evidence needed to complete the design | Current assessment and related gaps |
| --- | --- | --- | --- |
| MC23 | Explain the DSL's role and tradeoffs against credible alternatives, including typed ordinary code, XBRL, ledgers, rule languages and probabilistic tools. U1, U3, P. | Tie each claimed benefit to the same concrete tasks and shared semantic requirements; state costs and a fair authoring comparison protocol. Keep empirical superiority unclaimed until evaluated. | Partial: Chapter 4's comparison and Chapter 10's proposed evaluation are useful; worked task comparisons and precise frontend contracts are still needed. G2, G9. |
| MC24 | Specify the core language and IR completely enough for compatible independent implementations. U3, D. | Provide complete grammar/lexical rules, AST/IR schemas, types, context rules, built-ins, errors, package interfaces and source-to-IR-to-result fixtures, including the demonstration package. | Partial: Chapter 6 and Appendix A contain selected definitions rather than a complete normative specification. G2, G12, G15. |
| MC25 | Specify APIs, adapters, storage, versioning, identity and deterministic recovery. U3, P, D. | Define complete arguments/results, state ownership, migration semantics, evidence/model/run identity, event idempotency, random-stream allocation and replay requirements with examples. | Partial: Chapter 9 names operations and invariants but leaves substantive interface and identity decisions open. G2, G9, G18. |
| MC26 | Specify supported numerical/solver operations and their limits. U3, P, D. | Define formula fragments, reformulations, exact/approximate monetary treatment, rounding, strict-domain bounds, infeasibility/conflict evidence, timeout and resource behaviour. | Partial: the linear scope is explicit but realistic symbolic and rounding cases are not fully connected to it. G3, G10. |
| MC27 | Specify analyst/LLM review and correction as a traceable local workflow. U1, U3, D. | Define proposal, acceptance, alternative, rejection and supersession actions, with evidence requirements, consistency checks and derived-result invalidation; show an actual conflict-resolution example. | Partial: Chapter 9 lists actions but lacks their complete lifecycle and consequences. G2, G17. |
| MC28 | Connect the full design through complete synthetic and real disclosure cases. U1, U2, U3, D. | Supply a known-history synthetic company and a named annual/interim real package across multiple dates; trace representative notes through records, constraints, alternatives and all affected future statements. Add structural finance/sector cases before fixing the core types. | Open: these are proposed in Chapters 1 and 10 but not instantiated in the current document. G4, G5, G7. |

## M6 — Literature, sources and reusable software

| ID | Requirement and origin | Evidence needed to complete the design | Current assessment and related gaps |
| --- | --- | --- | --- |
| MC29 | Conduct a broad, technically grounded literature survey beyond the original collection. U3, P. | Inspect relevant primary methods/theory/evaluation/appendices and official code where available; compare direct alternatives; make genuine backward/forward screening, source-specific omissions, corrections and claim support inspectable. | Partial: Chapter 3 and the six ledgers have breadth; generic generated exclusions and module-specific coverage remain unresolved. G8. |
| MC30 | Preserve the relevant source library and precise provenance. U3, P. | Archive accessible relevant papers under the required naming convention, retain exact versions/anchors, preserve original files, and document unavailable sources without relying on their uninspected claims. | Established for the currently indexed 31 PDF files at the mechanical-integrity level; broader source acquisition and technical support remain open. G8. |
| MC31 | Survey open-source tools and define evidence-based reuse boundaries. U3, P, D. | Inspect official interfaces/licences, identify supported subsets, specify adapter exchanges and version assumptions, and separate inspected capabilities from later integration/performance evidence. | Partial: Chapter 4 and tools.json form an inspected shortlist; selected adapter contracts and checks remain open. G9. |

## M7 — Governing scholarly design

| ID | Requirement and origin | Evidence needed to complete the design | Current assessment and related gaps |
| --- | --- | --- | --- |
| MC32 | Deliver a detailed, readable LaTeX/PDF document that governs the intended implementation. U3, P. | Explain the whole problem, justify chosen methods, stage mathematical prerequisites, define supported behaviour and disclose open scope; connect derivations and sources to complete examples and interfaces. Preserve mathematical/source fidelity during revisions and inspect the rendered result. | Partial: the 60-page draft builds and communicates the architecture, but governing method detail and complete cases are missing. G1, G2, G4, G5, G7, G10. |

## M8 — Validation, completion and sustained direction

| ID | Requirement and origin | Evidence needed to complete the design | Current assessment and related gaps |
| --- | --- | --- | --- |
| MC33 | Define meaningful acceptance and separate engineering, accounting and scientific evidence. U3, P, D. | Provide canonical conformance inputs/outputs, corpus/annotation rules, justified release-specific criteria, review status and later forecast baselines/uncertainty protocols. Existing arithmetic/build checks keep their limited meanings. | Partial: Chapter 10's test intentions and evidence separation are useful, but fixtures, corpus, release criteria and final author review remain open. G5, G10. |
| MC34 | Stage implementation without losing the full mission or concealing unresolved decisions. U1, U2, U3, P, D. | Maintain requirement-to-section/case/gap traceability, explicit current-versus-later support, dependency order, workload assumptions and open decisions. Re-audit after material changes and test interactions, not just individual rows. | Mission control is now installed. The manuscript still needs scope/support and method completion against this register; installation does not close the scientific or design gaps. G1–G18. |

## Current disposition and maintenance

No whole-product or whole-document completeness claim follows from this
register. The existing build, source/PDF integrity and illustration checks are
real evidence for their limited targets. All larger acceptance obligations
above remain subject to their identified repairs and reviews.

The next specification work should use MC28 to expose and close the required
MC01–MC18 and MC24–MC27 details in a bounded complete case, while using early
MC19–MC22 structural examples to avoid a corporate-only core. MC29–MC31 must
support actual method choices. MC32–MC34 control whether the result can be
described as implementation-governing.

On each substantive revision, update the affected rows with the actual source
and evidence. Do not change `partial` to `checked` because a subsection, JSON
record or test name has been added. If a requirement is narrowed, preserve its
prior meaning and record the user instruction authorising the scope change.
New requirements and gaps may be added when evidence reveals an omission;
these 34 rows are the current traceable baseline, not a proof that no further
requirements can be discovered.
