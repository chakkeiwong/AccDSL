# AccDSL Product Design: Gap Analysis and Completeness Review

**Review Date:** 5 October 2026  
**Reviewer:** Claude Opus 5.5  
**Document Reviewed:** AccDSL Product Design v1.2 (2 October 2026)

---

## Executive Summary

The AccDSL design document presents a rigorous, evidence-based architecture for representing company financial histories and simulating alternative accounting and economic scenarios. It demonstrates careful attention to temporal semantics, provenance, partial information, and the distinction between feasible sets and probability distributions.

However, the document explicitly acknowledges it is a **design specification, not a completed implementation**. Significant gaps remain in:

1. **Literature foundations** – several foundational papers inaccessible
2. **Standards compliance** – paragraph-level IFRS/US GAAP/ASBE implementations pending
3. **Industry coverage** – banking and insurance modules incomplete; many industries deferred
4. **Implementation artifacts** – extraction pipeline, compiler, solver integration not built
5. **Evaluation evidence** – no forecast evaluation, limited extraction benchmarks
6. **Practical tooling** – review interfaces, error messages, IDE support undefined

This analysis identifies **missing citations, incomplete technical coverage, deferred design decisions, and gaps relative to the stated goal of a fully generic DSL** for accounting that handles the breadth of real-world financial reporting.

---

## 1. Missing and Incomplete Literature Foundations

### 1.1 Inaccessible Foundational Sources

The document acknowledges but cannot use technical results from:

- **McCarthy (1982)** – REA (Resources, Events, Agents) model, foundational for event-based accounting
- **Imieliński & Lipski (1984)** – original incomplete-database paper; design uses Libkin (2014) as substitute
- **Tamer (2010)** – partial identification; blocked during retrieval
- **Caiani et al. (2016)** – stock-flow-consistent agent-based macroeconomic models

**Impact:** The design cannot claim to be grounded in REA foundations or stock-flow-consistent multi-company equilibrium theory. These are acknowledged as expansion work, but their absence limits theoretical coverage.

### 1.2 Incomplete Standards Authority

**IFRS:**
- Uses "orientation" overviews from IFRS Foundation website (IFRS 9, IAS 32, IFRS 17, IFRS 18)
- Paragraph-level implementation and compliance review **explicitly pending**
- No claim of full IFRS compliance in current design

**US GAAP:**
- ASC (Accounting Standards Codification) access incomplete
- Caterpillar LIFO example cited from company report, not official ASC 330 authority
- Cannot claim US GAAP compliance without full ASC paragraph mapping

**ASBE (Chinese standards):**
- Uses **reproduced** ASBE 1 text, not official Ministry of Finance source
- All ASBE semantic modules marked **source-provisional**
- Official verification pending

**Impact:** No accounting-standard package can be certified as compliant. All three major reporting regimes require additional acquisition, paragraph-level implementation, and independent accounting review before promotion.

### 1.3 Deferred Citation Follow-ups

The research appendix identifies **179 unique forward-citation candidates** with explicit relevance decisions, but defers technical reading for:

- Provenance and temporal-query extensions
- Bank optimization and management-response calibration
- Advanced extraction and document understanding
- Actuarial inference and reserving methods beyond simple chain-ladder

**Impact:** Design acknowledges these as expansion risks. Current coverage is scoped to demonstrate feasibility, not exhaust relevant literature.

---

## 2. Incomplete Accounting and Financial-Instrument Coverage

### 2.1 Recognition and Measurement Gaps

The following instruments and transactions are **mentioned but not fully specified**:

| Area | Status | Missing Detail |
|------|--------|----------------|
| **Leases** (IFRS 16 / ASC 842) | Mentioned in scope; no event templates or measurement rules | Lease classification, right-of-use asset, lease liability, modification, sale-leaseback |
| **Pensions & Employee Benefits** (IAS 19 / ASC 715) | Not covered | Defined-benefit obligations, actuarial assumptions, service cost, remeasurement |
| **Share-based Payment** (IFRS 2 / ASC 718) | Employee share awards mentioned; no valuation or vesting rules | Grant-date fair value, vesting conditions, forfeitures, modification |
| **Revenue from Contracts** (IFRS 15 / ASC 606) | Performance obligations mentioned; full 5-step model not implemented | Contract liabilities, variable consideration, contract modifications, principal vs. agent |
| **Business Combinations** (IFRS 3 / ASC 805) | Acquisition mentioned; purchase-price allocation sketched | Fair value measurement, contingent consideration, goodwill impairment, step acquisitions |
| **Impairment** (IAS 36 / ASC 350/360) | Inventory impairment illustrated; broader CGU/asset-group impairment incomplete | Cash-generating units, value-in-use, impairment triggers, reversal rules |
| **Fair Value Measurement** (IFRS 13 / ASC 820) | Mentioned; no Level 1/2/3 hierarchy or valuation-technique detail | Observable inputs, unobservable inputs, credit valuation adjustment, bid-ask spreads |

### 2.2 Derivatives and Hedge Accounting

**Status:** Contracts mention hedges, swaps, and conversion features; full derivative lifecycle incomplete.

**Missing:**
- Embedded derivative separation (IAS 32 para 28–32, IFRS 9)
- Hedge effectiveness testing (IFRS 9 hedge accounting requirements)
- Cash-flow hedge reserves and reclassification (OCI treatment)
- Net investment hedges of foreign operations
- Hedge documentation and designation requirements

**Impact:** Cannot simulate realistic corporate hedging programs or evaluate hedge accounting elections without these rules.

### 2.3 Credit Loss and Allowance Models

**Status:** Simple EAD × PD × LGD formula illustrated (Chapter 8); full IFRS 9 / CECL implementation **explicitly deferred**.

**Missing:**
- IFRS 9 staging (12-month vs. lifetime expected credit loss)
- Significant-increase-in-credit-risk criteria
- Forward-looking macroeconomic scenarios
- Purchased credit-impaired assets
- Modification and write-off accounting
- CECL vintage curves and qualitative adjustments

**Impact:** Banking package cannot be promoted to production without these implementations.

### 2.4 Insurance Contracts

**Status:** Premium allocation approach (PAA) illustrated; longer-duration fulfilment cash flows and contractual service margin (CSM) sketched.

**Missing:**
- Full IFRS 17 general measurement model (GMM)
- CSM allocation and loss-component mechanics
- Variable fee approach (VFA) for participating contracts
- Onerous-contract grouping and loss recognition
- Risk adjustment methodologies (confidence-level calibration, cost-of-capital)
- Reinsurer default and non-performance treatment

**Impact:** Insurance package remains demonstration-only until actuarial and accounting review complete.

### 2.5 Income Taxes

**Status:** 20% flat-rate demonstration; deferred tax, losses, and jurisdictional complexity **not implemented**.

**Missing:**
- Temporary differences and deferred tax assets/liabilities (IAS 12 / ASC 740)
- Valuation allowances and recoverability assessments
- Tax loss carryforwards and carrybacks
- Uncertain tax positions (ASC 740-10)
- Multi-jurisdictional allocation and transfer pricing
- Tax-rate changes and their recognition timing

**Impact:** Cannot simulate realistic tax planning, NOL utilization, or multinational tax effects.

### 2.6 Foreign Currency

**Status:** Mentioned; translation effects separated from cash flows.

**Missing:**
- IAS 21 / ASC 830 functional-currency determination
- Translation of foreign operations (CTA in OCI)
- Monetary vs. non-monetary distinction
- Hyperinflation adjustments (IAS 29)
- Net investment hedges

**Impact:** Multinational companies cannot be fully modeled without these rules.

---

## 3. Missing Industry and Sector Packages

### 3.1 Industries with No Coverage

The design focuses on **non-financial corporates, banks, and insurers**. The following industries are **not addressed**:

- **Construction & Engineering** – percentage-of-completion, contract assets/liabilities, claims and variations
- **Extractives (Oil & Gas, Mining)** – reserves, depletion, asset retirement obligations, joint operations
- **Software & Technology** – capitalization of development costs, cloud arrangements, open-source obligations
- **Pharmaceuticals & Biotech** – research vs. development, regulatory milestones, acquired in-process R&D
- **Telecommunications** – spectrum licenses, network infrastructure, revenue-sharing arrangements
- **Utilities & Regulated Industries** – regulatory assets/liabilities, rate-setting mechanisms
- **Real Estate** – investment property (IAS 40), real-estate development, sale-leaseback
- **Agriculture** – biological assets (IAS 41), bearer plants, fair value less costs to sell
- **Not-for-Profit & Governmental** – fund accounting, restricted contributions, capital assets

**Impact:** Industry extensions mentioned as "expansion work"; no guidance on how they would integrate with the core.

### 3.2 Banking Package Gaps

**Status:** Credit cohorts, deposits, collateral, liquidity, capital reconciliation illustrated.

**Missing:**
- Securities portfolio accounting (held-to-maturity, available-for-sale, trading)
- Repo and securities financing transactions
- Securitization and special-purpose entities
- Loan modifications and troubled debt restructuring
- Complex derivatives (credit derivatives, structured products)
- Counterparty credit risk (CVA, DVA)
- Stress testing and CCAR/DFAST reporting frameworks
- Liquidity coverage ratio (LCR) and net stable funding ratio (NSFR) mechanics

**Impact:** Banking package cannot model investment-bank or universal-bank activities.

### 3.3 Insurance Package Gaps

**Status:** PAA illustrated; GMM and CSM mechanics sketched but not implemented.

**Missing:**
- Life insurance (mortality/longevity modeling, guaranteed benefits)
- Annuities (payout phase, guaranteed minimum benefits)
- Health insurance (claims reserving, medical cost trends)
- Property & casualty (catastrophe modeling, loss triangles beyond simple chain-ladder)
- Reinsurance structures (quota-share, excess-of-loss, stop-loss)
- Embedded derivatives in insurance contracts

**Impact:** Only simple short-duration insurance can be modeled with current design.

---

## 4. Implementation and Tooling Gaps

### 4.1 No Complete Extraction Pipeline

**Status:** Arelle (XBRL), Docling (PDF), Table Transformer mentioned as candidates; **no integrated pipeline built**.

**Missing:**
- End-to-end document → structured observations workflow
- OCR correction and table-structure repair interfaces
- Concept-mapping review UI
- Automated reconciliation checks
- Duplicate-fact resolution
- Cross-note reference traversal (acquisition protocol defined but not executed)

**Impact:** Cannot ingest real filings without manual intervention. Extraction evaluation (Chapter 10) described but not run.

### 4.2 DSL Compiler and Frontend Not Implemented

**Status:** Grammar provided (`core-0.lark`); semantic contract specified; **compiler not built**.

**Missing:**
- Lexer/parser implementation
- Name resolution and module loader
- Type checker and context validator
- IR lowering and canonicalization
- Error messages and diagnostics
- IDE integration (syntax highlighting, jump-to-definition, hover hints)
- Debugger and profiler

**Impact:** Cannot test whether the DSL syntax is learnable, whether error messages are comprehensible, or whether the language reduces ambiguity vs. the Python API. Evaluation protocol defined (Chapter 10) but not executed.

### 4.3 Solver Integration Incomplete

**Status:** Z3 mentioned as "first solver candidate"; linear fragment specified.

**Missing:**
- Actual Z3 adapter implementation
- Conflict-core minimization
- Incremental solving (reuse across branches)
- Timeout and resource-limit tuning
- Unsupported-theory diagnostics
- Alternative solvers (CVC5, Yices, SMT-LIB export)

**Impact:** Cannot verify that linear-bridge reconstruction works on real companies. T05–T10 conformance tests defined but not run.

### 4.4 No Contract and Valuation Adapters

**Status:** ACTUS and QuantLib interfaces specified; **no implementations**.

**Missing:**
- ACTUS risk-factor→event-schedule adapter
- QuantLib curve/instrument setup for specific contract types
- Calendar alignment (business-day conventions, holidays)
- Fixing and reset mechanics
- Numerical convergence and error handling

**Impact:** Cannot simulate realistic floating-rate debt, interest-rate swaps, or exotic options.

### 4.5 Review and Annotation Interface Missing

**Status:** Protocol described (Chapter 9); **no UI built**.

**Missing:**
- Source-beside-interpretation display
- Accept/reject/alternative workflow
- Symbolic-unknown editor
- Reconciliation-impact preview
- Conflict-set resolution
- Multi-user review and approval

**Impact:** System is architected for deterministic re-execution but lacks practical interface for analyst collaboration.

### 4.6 No Testing Corpus Assembled

**Status:** Apple 10-K and 10-Q archived; Caterpillar LIFO cited; **other strata pending** (Chapter 10).

**Missing:**
- IFRS corporate issuer (3 dates, restatement, full notes)
- ASBE corporate issuer
- Bank (annual + interim, allowance bridge, regulatory capital)
- Insurer (cohort movements, reinsurance, actuarial reserves)
- Construction, extractives, software (not even planned)

**Impact:** Cannot evaluate extraction quality, reconstruction coverage, or forecast performance. Acceptance thresholds defined but no comparison executed.

---

## 5. Theoretical and Mathematical Gaps

### 5.1 Nonlinear and Discrete Optimization Out of Scope

**Status:** First implementation limited to "linear constraints and finite Boolean choices" (Chapter 5).

**Missing:**
- Nonlinear contractual relationships (e.g., option payoffs, piecewise schedules)
- Integer programming (lot-level inventory, discrete investment decisions)
- Mixed-integer nonlinear programs (MINLP)
- Automatic model reformulation and relaxation

**Impact:** Many realistic scenarios require nonlinear or combinatorial decisions. System must delegate to plugins or declare them unsupported.

### 5.2 Causal Inference Beyond Basic Interventions

**Status:** Pearl's do() operator cited; structural interventions distinguished from observational conditioning.

**Missing:**
- Identification of causal effects with unobserved confounders
- Instrumental variables and control functions
- Difference-in-differences for policy changes
- Synthetic control methods
- Mediation and path analysis

**Impact:** Cannot rigorously attribute scenario outcomes to specific mechanisms vs. confounded effects.

### 5.3 Continuous Probabilistic Inference Optional and Underspecified

**Status:** Finite Bayes updating illustrated; Stan/Pyro/PyMC mentioned as "optional inference backends" (Chapter 4).

**Missing:**
- How to specify priors over continuous parameters (conjugate families, weakly informative defaults)
- Likelihood construction for deterministic accounting constraints (measure-theoretic treatment)
- MCMC sampler selection and tuning
- Convergence diagnostics (R-hat, effective sample size)
- Posterior predictive checks
- Sensitivity to prior specification

**Impact:** Unweighted feasible families are well-defined; weighted inference remains research extension. No default Bayesian workflow provided.

### 5.4 Model Discovery and Automatic Structure Learning

**Status:** Declared out of scope: "automatic model discovery ... [is a] research extension[], not [a promise] made by the core language" (Chapter 5).

**Missing:**
- Learning event templates from data
- Discovering hidden contract terms from observed cash flows
- Structure learning for dependencies among accounts
- Anomaly detection and outlier treatment

**Impact:** Reconstruction requires declared model scope; cannot automatically infer missing mechanisms.

---

## 6. Validation and Evaluation Gaps

### 6.1 No Forecast Evaluation Completed

**Status:** Evaluation protocol specified (Chapter 10); **no results**.

**Missing:**
- Historical information cutoffs and proper train/test splits
- Baseline comparators (naive persistence, financial ratios, trailing growth)
- Evaluation metrics (RMSE, directional accuracy, calibration)
- Regime-specific performance (stable vs. stressed periods)
- Uncertainty quantification (coverage of prediction intervals)
- Out-of-sample forecast comparison

**Impact:** Cannot claim forecasting advantage over simpler models. Comparative performance unknown.

### 6.2 Extraction Benchmarks Described but Not Run

**Status:** FinQA, TAT-QA, PubTables-1M, GTE, FinTabNet cited as "useful development material" (Chapter 10); **no evaluation executed**.

**Missing:**
- Extraction accuracy on financial tables
- Source-linking precision and recall
- Context correctness (entity, period, unit)
- Note-obligation coverage
- Fabricated-citation detection
- Extraction confidence calibration

**Impact:** Cannot assess practical extraction quality or compare with state-of-the-art document understanding.

### 6.3 DSL vs. API Comparison Not Run

**Status:** Comparison protocol defined (Chapter 10); **no participants, no results**.

**Missing:**
- User study with tasks (encode schedule, add alternative, explain forecast)
- Completion rates and error rates
- Time-on-task measurements
- Qualitative feedback on learnability
- Maintenance effort over multiple iterations

**Impact:** Cannot justify DSL maintenance cost vs. Python API. Textual language remains unvalidated.

### 6.4 Accounting Review Pending

**Status:** Every standards package explicitly requires "independent domain review" before promotion (Chapter 10).

**Missing:**
- Certified Public Accountant (CPA) or equivalent review
- Paragraph-level mapping to IFRS/US GAAP/ASBE
- Treatment of controversial or judgment-intensive areas
- Comparison with Big Four accounting-firm guidance
- Validation of consolidation, hedge accounting, revenue recognition

**Impact:** No package can be certified compliant without this review. All current content is design intent, not validated implementation.

### 6.5 Human Comprehension Review Pending

**Status:** Acknowledged as "separate from ... engineering, accounting, and forecast release" (Chapter 10).

**Missing:**
- Usability testing with financial analysts
- Explanation-graph comprehension
- Error-message clarity
- Report-interpretation accuracy
- Trust and adoption barriers

**Impact:** System may be correct but incomprehensible. No evidence of practical usability.

---

## 7. Gaps Relative to "Fully Generic DSL" Goal

The stated mission is a **domain-specific language for accounting that handles the goals stated in the document**. Those goals (Chapter 1) include:

> "reconstruct three reporting dates ... for one company, including at least one restatement ... A synthetic company supplies known hidden history; a public company supplies realistic disclosure ... extending beyond a debt maturity requires schedule detail"

The design is **scoped to demonstrate feasibility**, not to provide production-ready coverage of all accounting scenarios. Specific gaps relative to "fully generic":

### 7.1 Not All Transaction Types Covered

**Generic requirement:** Handle any accounting event in any industry.

**Current scope:** Non-financial corporates (sales, purchases, payroll, capex, depreciation, debt, equity), banks (loans, deposits, allowances), insurance (simple PAA).

**Gaps:**
- Construction contracts and milestone accounting
- Extractive industries (reserves, depletion, ARO)
- Software capitalization and cloud arrangements
- Agricultural biological assets
- Real-estate investment property
- Government and fund accounting
- Many specialized transactions (see Section 3.1)

### 7.2 Not All Standards and Jurisdictions

**Generic requirement:** Support IFRS, US GAAP, and other major reporting frameworks with full paragraph-level fidelity.

**Current scope:** Demonstration rules inspired by IFRS/GAAP overviews; paragraph-level authority **explicitly pending**.

**Gaps:**
- No certified IFRS compliance
- No certified US GAAP compliance
- ASBE implementation source-provisional
- No support for Japanese GAAP, IPSAS, or other national frameworks
- No explicit treatment of first-time adoption (IFRS 1)
- No detailed transition provisions for standard changes

### 7.3 Not All Disclosure Formats

**Generic requirement:** Ingest any filing format and extract all material information.

**Current scope:** XBRL, PDF, HTML with table detection mentioned; **extraction pipeline not built**.

**Gaps:**
- No Word/DOCX ingestion
- No audio/video (earnings calls, presentations)
- No multi-language extraction beyond UTF-8 strings
- No OCR for scanned or image-embedded PDFs
- No interactive HTML/JavaScript-rendered disclosures
- No exhibit parsing (contracts, registration statements)

### 7.4 Not All Uncertainty Representations

**Generic requirement:** Preserve all uncertainty: missing data, discrete alternatives, continuous parameters, probabilities.

**Current scope:** Shared symbols, finite choices, linear domains, optional weights well-defined; **nonlinear continuous inference optional and underspecified**.

**Gaps:**
- No automatic prior elicitation
- No default credible-interval construction for continuous parameters
- No treatment of epistemic vs. aleatoric uncertainty
- No robust optimization under ambiguous distributions
- No sensitivity analysis dashboard

### 7.5 Limited Scenario Richness

**Generic requirement:** Simulate any economic scenario with any management-response policy.

**Current scope:** Exogenous stress paths, simple funding waterfalls, demonstration behavioral rules.

**Gaps:**
- No equilibrium models (prices, quantities, interest rates jointly determined)
- No game-theoretic interactions (competitors, regulators)
- No learning and adaptation (Bayesian updating of management beliefs)
- No regime-switching models
- No agent-based multi-company simulation (Caiani literature inaccessible)

### 7.6 No Workflow Automation

**Generic requirement:** Support end-to-end workflow from filing ingestion to forecast dissemination.

**Current scope:** Conceptual architecture defined; **no orchestration, queuing, or monitoring**.

**Gaps:**
- No automated filing retrieval (SEC EDGAR API, regulatory feeds)
- No scheduled updates and alerting
- No multi-user collaboration (locks, merges, approvals)
- No version control for model packages
- No CI/CD for accounting-rule deployments
- No export to analyst tools (Excel, Tableau, Bloomberg)

### 7.7 No Regulatory Reporting Integration

**Generic requirement:** Generate not just GAAP statements but also regulatory filings.

**Current scope:** Prudential capital mentioned for banks; **no filed-form templates**.

**Gaps:**
- No SEC forms (10-K, 10-Q, 8-K, DEF 14A generation)
- No Basel regulatory reporting (COREP, FINREP)
- No Solvency II templates
- No local tax filings
- No management certification workflows

---

## 8. Specific Missing Citations and Unverified Claims

### 8.1 Accounting Mechanics Without Paragraph Authority

The document makes specific accounting claims without citing paragraph-level authority:

| Claim | Chapter | Missing Citation |
|-------|---------|------------------|
| "IAS 32 requires separate liability and equity components" | 8 | Cites AG30–AG32 from AASB 132 (Australian text); original IAS 32 not cited |
| "IFRS 17 premium allocation eligible when..." | 8 | Cites AASB 17 paragraphs; original IFRS 17 not directly retrieved |
| "IFRS 9 staging determines 12-month vs. lifetime ECL" | 8 | IFRS 9 overview cited; paragraph-level classification rules not implemented |
| "ASC 330 permits LIFO" | 8 | Inferred from Caterpillar disclosure; ASC 330 text not acquired |
| "Deferred tax requires temporary differences per IAS 12" | Section 2.5 | IAS 12 mentioned but not cited with paragraphs |

**Impact:** Cannot claim rules are compliant without these citations verified.

### 8.2 Papers Cited but Not Fully Read

The research appendix records "targeted technical reading" and admits "no claim is made that every theorem, appendix or empirical result in every archived paper was independently replicated."

**Examples where limited reading acknowledged:**
- Halaj & Kok (2016) – bank model "motivates interfaces" but "parameterisations must be calibrated"
- Behn et al. (2019) – "structure follows the need ... without transferring ... preferences or shock parameters"
- Pierson (2020) – "AccDSL can use these structures as examples" but "approximations ... remain modelling choices"

**Impact:** Literature provides inspiration and partial validation, not full authority. Each borrowed structure needs independent derivation or testing.

### 8.3 Tools Inspected but Not Integrated

The architecture chapter lists tools with "inspected" interfaces but no execution:

| Tool | Status | What Was Checked | What Remains |
|------|--------|------------------|--------------|
| Arelle | "Inspected ModelFact, context accessors" | Interface signatures | XBRL validation, calculation linkbase, formula processing |
| Docling | "Inspected converter interface" | API shape | PDF parsing quality, table-structure accuracy, page-layout errors |
| Table Transformer | "Check finance-domain performance before selection" | Paper and repo metadata | Actual extraction benchmark |
| Z3 | "Reference checks exercise Z3" | SMT-LIB syntax, theory support | Conflict cores, incremental solving, timeout tuning |
| ACTUS | "Verify event schedules against ACTUS tests" | Technical spec | Differential testing not run |
| QuantLib | "Candidate valuation adapter" | Floating-coupon source | No actual valuation comparisons |

**Impact:** No tool has been integrated and validated. All remain "candidate" or "first choice" pending implementation.

---

## 9. Deferred Design Decisions

### 9.1 Aggregation and Resolution Trade-offs

**Issue:** How much detail to preserve?

**Current guidance:** "Safe exact transformations are deliberately few" (Chapter 5); grouping requires proof of additivity.

**Deferred:**
- Default aggregation policies for common cases
- Performance vs. fidelity trade-offs
- Automatic coarsening for tractability
- User control over state resolution

### 9.2 Error Recovery and Partial Results

**Issue:** What to do when a branch fails?

**Current guidance:** "Preserve last committed state, completed outputs, unavailable outputs and reason" (Chapter 7).

**Deferred:**
- User notification and remediation workflows
- Automatic retries with relaxed tolerances
- Graceful degradation (e.g., report historical statements even if forecast fails)
- Result caching and resumption strategies

### 9.3 Multi-User Collaboration and Access Control

**Issue:** How do teams work together?

**Current guidance:** "Multi-user approval hierarchies, cryptographic attestations ... outside this initial design" (Chapter 9).

**Deferred:**
- Role-based access control (viewer, editor, reviewer, admin)
- Review and approval workflows
- Audit trails and change tracking
- Merge conflicts in model packages

### 9.4 Performance and Scalability Targets

**Issue:** How large a company can the system handle?

**Current guidance:** "Provisional engineering limits: 10,000 observations, 100 event slots per period, 64 finite-choice cells, 30-second solver budget" (Chapter 10).

**Deferred:**
- Actual capacity measurements
- Optimization strategies (caching, incremental compilation, parallelization)
- Memory footprint and streaming for large simulations
- Benchmarking and profiling infrastructure

### 9.5 Deployment and Packaging

**Issue:** How is AccDSL distributed and installed?

**Current guidance:** Python package, CLI, "desktop app ... IDE extensions" mentioned in environment section.

**Deferred:**
- Package manager (pip, conda)
- Dependency locking and reproducibility
- Docker/container deployment
- Cloud-native operation (serverless, managed services)
- Versioning and upgrade paths

---

## 10. Critical Risks to Feasibility

### 10.1 Accounting Review May Require Major Changes

**Risk:** Independent CPA review may find that proposed recognition or measurement rules violate standards.

**Example:** Debt classification, hedge accounting, revenue recognition are "judgment-intensive."

**Mitigation:** Design explicitly flags accounting packages as "demonstration" until reviewed. But large rewrites could invalidate dependent implementations.

### 10.2 Extraction Quality May Be Insufficient

**Risk:** Tables and notes may be too complex, inconsistent, or ambiguous for automated extraction to achieve required accuracy.

**Example:** Multi-page tables, footnoted exceptions, narrative-only disclosures.

**Mitigation:** Design allows human review and correction. But if manual intervention is always required, automation value is limited.

### 10.3 Solver Scalability May Be Inadequate

**Risk:** Real companies with hundreds of accounts, dozens of periods, and multiple alternatives may produce constraint systems too large for reasonable solve times.

**Example:** Symbolic families over continuous parameters may not admit efficient bounds.

**Mitigation:** Design limits first implementation to linear fragment. But if most realistic cases require nonlinear solvers, core value proposition weakens.

### 10.4 DSL May Not Improve Over Python API

**Risk:** User study (Chapter 10) may find that DSL syntax is harder to learn, debug, and maintain than typed Python.

**Mitigation:** Design specifies "reversible product decision" and preserves IR and library. But DSL development effort may be wasted.

### 10.5 Forecast Evaluation May Show No Advantage

**Risk:** Comparative evaluation (Chapter 10) may find that preserving alternative histories does not improve forecast accuracy over simpler baselines.

**Example:** Naive persistence or financial-ratio models may dominate.

**Mitigation:** Design emphasizes rigorous evaluation protocol. But poor forecast performance would limit adoption and require pivoting to pure accounting-representation use cases.

---

## 11. Recommendations for Version 2

To address these gaps and move toward a fully generic accounting DSL, Version 2 should:

### 11.1 Immediate Priorities (P0/P1)

1. **Acquire missing standards authority** – Obtain IFRS bound volume, ASC subscription, official ASBE texts. Map paragraph-level recognition/measurement rules.

2. **Build minimal extraction pipeline** – Integrate Arelle for XBRL, Docling for PDF. Test on Apple fixture. Measure accuracy.

3. **Implement core compiler and solver** – Parse Core 0, lower to IR, call Z3 for linear bounds. Verify conformance tests T01–T10.

4. **Document conformance test results** – Run fixed/floating debt example, Northstar rollforward, bank funding failure. Record passes/failures.

5. **Expand literature coverage** – Prioritize REA (McCarthy) via alternative sources if original inaccessible. Fill temporal-database and provenance gaps.

### 11.2 Near-Term Extensions (P2/P3)

6. **Add critical instrument types** – Leases (IFRS 16), pensions (IAS 19), share-based payment (IFRS 2), revenue (IFRS 15). Paragraph-level mappings.

7. **Build contract adapters** – Integrate ACTUS for loan/bond schedules. Differential test against ACTUS reference implementation.

8. **Expand corporate package** – Foreign currency (IAS 21), income taxes (IAS 12), impairment (IAS 36). Worked examples.

9. **Implement review interface** – Source-beside-interpretation UI. Accept/reject workflow. Conflict resolution.

10. **Assemble testing corpus** – Add IFRS issuer (3 dates, restatement). ASBE issuer. Annotate for extraction evaluation.

### 11.3 Medium-Term Goals (P4/P5)

11. **Complete banking package** – Securities portfolio, securitization, CVA/DVA, regulatory capital, stress testing. Accounting review.

12. **Complete insurance package** – GMM, CSM mechanics, reinsurance, actuarial reserves. Actuarial and accounting review.

13. **Add industry packages** – Construction (IFRS 15 over time), extractives (IFRS 6, IAS 16), software (IAS 38). Prioritize by user demand.

14. **Probabilistic inference** – Integrate Stan or Pyro. Specify prior families, likelihood construction, convergence diagnostics. Sensitivity analysis.

15. **Forecast evaluation** – Historical cutoffs, baseline comparators, out-of-sample metrics. Publish results.

### 11.4 Long-Term Research (P6+)

16. **Nonlinear optimization** – MINLP solvers, automatic reformulation, heuristic search. Expand beyond linear fragment.

17. **Causal identification** – Instrumental variables, synthetic controls, mediation analysis. Support policy evaluation.

18. **Model discovery** – Learn event templates, infer hidden contracts, structure search. Requires ML/AI research.

19. **Multi-company equilibrium** – Stock-flow-consistent models, agent-based simulation. Revisit Caiani literature.

20. **Regulatory reporting** – SEC forms, Basel templates, Solvency II. Integration with filing systems.

---

## 12. Conclusion

The AccDSL design document is a **rigorous, well-architected proposal** for a system that addresses fundamental gaps in financial-statement interpretation and scenario analysis. It correctly distinguishes:

- **Evidence vs. interpretation**
- **Feasible sets vs. probability distributions**
- **Economic state vs. journals**
- **Recognition rules vs. measurement assumptions**

These distinctions are scientifically sound and practically important.

**However**, the document is explicit that it is a **design, not an implementation**. Significant work remains:

- **Literature:** Foundational papers inaccessible; standards authority incomplete
- **Accounting:** Paragraph-level IFRS/GAAP/ASBE implementations pending
- **Industry:** Banks and insurance sketched; most industries deferred
- **Implementation:** No compiler, no extraction pipeline, no solver integration
- **Evaluation:** No forecast comparison, no extraction benchmarks, no user studies

The design **demonstrates feasibility** for a scoped problem (non-financial corporate with debt, synthetic and real examples). It **does not claim** to be production-ready, comprehensive across industries, or validated through comparative evaluation.

**To achieve the goal of a "fully generic DSL for accounting,"** Version 2 must:

1. Close literature and standards-authority gaps
2. Implement and test the compiler, solver, and extraction pipeline
3. Expand accounting and industry coverage with independent review
4. Execute the evaluation protocols and publish results
5. Iterate based on user feedback and forecast performance

The current v1.2 design provides an excellent foundation. Version 2 should be a **documented implementation with evaluation evidence**, not just an expanded design specification.