# AccDSL Version 2: Visual Roadmap

## 📊 Document Structure at a Glance

```
AccDSL v2 Design Document
├── Part I: Foundations and Core Design (Preserved from v1.2)
│   ├── Chapter 1:  Purpose and Product Decision ✓
│   ├── Chapter 2:  Representing Historical Record ✓
│   ├── Chapter 3:  Literature Review ✓
│   ├── Chapter 4:  Architecture and Reuse ✓
│   ├── Chapter 5:  Mathematics and Compatibility ✓
│   ├── Chapter 6:  Accounting Language ✓
│   ├── Chapter 7:  Execution Procedures ✓
│   ├── Chapter 8:  Industry Modules ✓
│   ├── Chapter 9:  Implementation Contracts ✓
│   ├── Chapter 10: Validation ✓
│   └── Chapter 13: Reference Company Examples ✓
│
├── Part II: Accounting Standards and Compliance (NEW)
│   ├── Chapter 14: IFRS Mapping ✅ COMPLETE (~35 pages)
│   ├── Chapter 15: US GAAP Mapping ⏳ Designed
│   └── Chapter 16: ASBE Mapping ⏳ Designed
│
├── Part III: Industry Packages and Technical Extensions (EXPANDED)
│   ├── Chapter 17: Extraction Pipeline ✅ COMPLETE (~30 pages)
│   ├── Chapter 18: Industry Extensions ⏳ Designed
│   ├── Chapter 19: Solver Algorithms ⏳ Designed
│   └── Chapter 20: Probabilistic Inference ⏳ Designed
│
├── Part IV: Evaluation and Roadmap (NEW)
│   ├── Chapter 21: Forecast Evaluation ⏳ Designed
│   └── Chapter 22: Implementation Roadmap ⏳ Designed
│
└── Appendices
    ├── Chapter 11: Core Grammar and Contracts ✓
    ├── Chapter 12: Research Basis ✓
    ├── Chapter 23: Additional Worked Examples ⏳ Designed
    └── Chapter 24: Gap Resolution from v1.2 ⏳ Designed

✓ = Preserved from v1.2
✅ = Complete in v2
⏳ = Designed but not yet written
```

## 🎯 Gap Analysis Coverage Map

```
Gap Analysis (759 lines, 12 sections)
│
├── 1. Missing Literature Foundations ━━━━━━━━━━━━━━━━━━━━━━┓
│   • REA model (McCarthy 1982) - inaccessible              │
│   • Incomplete databases (Imieliński & Lipski 1984)       │
│   • Stock-flow consistent models (Caiani 2016)            │
│   • Forward citations: 179 screened, many deferred        │
│                                                            ▼
├── 2. Incomplete Accounting Coverage ━━━━━━━━━━━━━━━━━━━┓ Addressed by
│   • IFRS: Only overviews, no paragraph-level ✗          │ Chapter 14 ✅
│   • US GAAP: ASC access incomplete ✗                    │ Chapter 15 ⏳
│   • ASBE: Reproduced text, not official ✗               │ Chapter 16 ⏳
│   • Leases, pensions, share-based, revenue ✗            │
│   • Derivatives, hedge accounting ✗                     │
│   • ECL/CECL credit models ✗                            │
│   • Insurance (GMM, CSM, VFA) ✗                         ◄┘
│
├── 3. Missing Industry Packages ━━━━━━━━━━━━━━━━━━━━━━┓
│   • Construction, extractives, software ✗               │ Addressed by
│   • Pharma, telecom, utilities ✗                        │ Chapter 18 ⏳
│   • Real estate, agriculture, not-for-profit ✗         ◄┘
│
├── 4. Implementation Gaps ━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
│   • No extraction pipeline ✗                            │ Addressed by
│   • No DSL compiler ✗                                   │ Chapter 17 ✅
│   • No solver integration ✗                             │ Chapter 19 ⏳
│   • No contract adapters ✗                              │ Chapter 22 ⏳
│   • No review UI ✗                                      ◄┘
│
├── 5. Theoretical Gaps ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
│   • Nonlinear optimization out of scope ✗               │ Addressed by
│   • Causal inference basic only ✗                       │ Chapter 19 ⏳
│   • Continuous probabilistic inference optional ✗       │ Chapter 20 ⏳
│   • Model discovery deferred ✗                          ◄┘
│
├── 6. Validation Gaps ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
│   • No forecast evaluation ✗                            │ Addressed by
│   • No extraction benchmarks ✗                          │ Chapter 21 ⏳
│   • No DSL vs API comparison ✗                          │ Chapter 17 ✅
│   • No accounting review ✗                              │ Chapter 22 ⏳
│   • No human comprehension review ✗                     ◄┘
│
├── 7. "Fully Generic DSL" Gaps ━━━━━━━━━━━━━━━━━━━━━━┓
│   • Not all transaction types                           │ Partially
│   • Not all standards/jurisdictions                     │ addressed by
│   • Not all disclosure formats                          │ Chapters 14-18
│   • Limited scenario richness                           │ More needed
│   • No workflow automation                              ◄┘
│
├── 8. Missing Citations & Unverified Claims ━━━━━━━━━━━┓
│   • Accounting mechanics without paragraph authority ✗  │ Addressed by
│   • Papers cited but not fully read ✗                  │ Chapter 14 ✅
│   • Tools inspected but not integrated ✗               │ Acknowledged
│                                                         ◄┘
├── 9. Deferred Design Decisions ━━━━━━━━━━━━━━━━━━━━━┓
│   • Aggregation trade-offs                             │ Acknowledged
│   • Error recovery                                     │ in Gap Analysis
│   • Multi-user collaboration                           │ Deferred to
│   • Performance targets                                │ future versions
│   • Deployment packaging                               ◄┘
│
├── 10. Critical Risks ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
│   • Accounting review may require major changes        │ Mitigated by
│   • Extraction quality may be insufficient            │ explicit status
│   • Solver scalability may be inadequate              │ indicators and
│   • DSL may not improve over API                      │ honest gap
│   • Forecast eval may show no advantage               │ acknowledgment
│                                                        ◄┘
├── 11. Recommendations (P0 → P6) ━━━━━━━━━━━━━━━━━━━┓
│   P0/P1: Standards, extraction, compiler, solver      │ Forms basis
│   P2/P3: Instruments, contracts, corporate package    │ for Chapter 22
│   P4/P5: Banking, insurance, industries, inference    │ Implementation
│   P6+: Nonlinear, causal, discovery, equilibrium      │ Roadmap ⏳
│                                                        ◄┘
└── 12. Conclusion ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    Summary: V1.2 = design; V2 = implementation-ready   │
    Status: Feasibility demonstrated                    │
    Path forward: Complete remaining chapters           ◄┘
```

## 🔄 Implementation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    AccDSL v2 System Overview                     │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐    ┌──────────────┐
│   Documents   │     │   Standards   │    │   Industry   │
│   (Chapter    │     │   Authority   │    │   Packages   │
│   17) ✅      │     │   (Ch 14-16)  │    │   (Ch 18) ⏳ │
│               │     │   Ch14: ✅    │    │              │
│ • EDGAR API   │     │   Ch15: ⏳    │    │ • Construc-  │
│ • PDF parse   │     │   Ch16: ⏳    │    │   tion       │
│ • XBRL parse  │     │               │    │ • Extractive │
│ • Table recog │     │ • IFRS 9      │    │ • Software   │
│ • Concept map │     │ • IAS 32      │    │ • Real estate│
│ • Validation  │     │ • IFRS 15/16  │    │              │
└───────┬───────┘     │ • IAS 19/12   │    └──────┬───────┘
        │             │               │           │
        │             └───────┬───────┘           │
        │                     │                   │
        └─────────────────────┼───────────────────┘
                              ▼
                  ┌─────────────────────┐
                  │  Evidence Registry  │
                  │  (Chapter 2 v1.2)   │
                  │                     │
                  │  • Observations     │
                  │  • Source links     │
                  │  • Contexts         │
                  │  • Provenance       │
                  └──────────┬──────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                    AccDSL Core (v1.2 + v2)                     │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │
│  │   Language  │  │   Solver    │  │   Probabilistic     │   │
│  │  (Ch 6 v1.2)│  │  (Ch 19) ⏳ │  │   (Ch 20) ⏳        │   │
│  │             │  │             │  │                     │   │
│  │ • DSL parse │  │ • Linear    │  │ • Stan/Pyro         │   │
│  │ • Type chk  │  │ • MIP       │  │ • MCMC              │   │
│  │ • IR lower  │  │ • Z3        │  │ • Variational       │   │
│  └─────────────┘  └─────────────┘  └─────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │         History Reconstruction (Ch 5 v1.2)              │  │
│  │  • Symbolic families  • Linear bridges  • Alternatives  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │          Scenario Simulation (Ch 7 v1.2)                │  │
│  │  • Events  • Journals  • Contracts  • Behavioral        │  │
│  └─────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
                  ┌────────────────────────┐
                  │  Reports & Forecasts   │
                  │  (Chapter 7-8 v1.2)    │
                  │                        │
                  │  • Statements          │
                  │  • Movement schedules  │
                  │  • Explanations        │
                  │  • Distributions       │
                  └────────────┬───────────┘
                               │
                               ▼
                  ┌────────────────────────┐
                  │    Evaluation          │
                  │   (Ch 21) ⏳           │
                  │                        │
                  │  • Baselines           │
                  │  • Metrics             │
                  │  • Out-of-sample       │
                  │  • Statistical tests   │
                  └────────────────────────┘
```

## 📅 Implementation Timeline (Estimated)

```
Phase 1: Complete V2 Documentation
═══════════════════════════════════════════════════════════════
Month 1-3:  Write Chapters 15-16 (US GAAP, ASBE)
Month 4-6:  Write Chapters 18-22 (Industries, Solver, etc.)
Month 7-9:  Independent accounting review, revisions
            └─> Output: Complete V2 document (~400-500 pages)

Phase 2: Core Infrastructure
═══════════════════════════════════════════════════════════════
Month 1-3:  Extraction pipeline (Chapter 17)
Month 4-6:  DSL compiler + IR (Chapter 6 v1.2)
Month 7-9:  Solver integration (Chapter 19)
Month 10-12: Contract adapters (ACTUS, QuantLib)
            └─> Output: Working prototype on synthetic cases

Phase 3: Standards & Industry Coverage
═══════════════════════════════════════════════════════════════
Month 1-3:  IFRS package implementation (Chapter 14)
Month 4-6:  US GAAP package (Chapter 15)
Month 7-9:  Corporate industry package (Chapter 18)
Month 10-12: Banking package (Chapter 8 v1.2)
            └─> Output: Production-ready for corporates + banks

Phase 4: Validation & Deployment
═══════════════════════════════════════════════════════════════
Month 1-2:  Assemble test corpus (100 companies × 3 filings)
Month 3-4:  Extraction benchmark evaluation
Month 5-6:  Forecast evaluation protocol (Chapter 21)
Month 7-9:  Out-of-sample validation, statistical analysis
Month 10-12: Production hardening, deployment
            └─> Output: Validated, deployed system

Total: ~48 months (4 years) with 6-8 FTEs
```

## 🎯 Milestone Dependencies

```
Critical Path (Must be sequential):
────────────────────────────────────────────────────────────────

V2 Docs Complete ──> Extraction Pipeline ──> Evidence Registry
     (9 PM)              (25 PM)                 (built-in)
                                                      │
                                                      ▼
                            DSL Compiler ──> Historical Reconstruction
                               (12 PM)           (core v1.2)
                                                      │
                                                      ▼
                            Standards Packages ──> Scenario Simulation
                               (18 PM)              (core v1.2)
                                                      │
                                                      ▼
                                                Evaluation
                                                  (6 PM)

Parallel Tracks (Can proceed independently):
────────────────────────────────────────────────────────────────

Standards Authority:          Industry Packages:
├─ IFRS (Ch 14) ✅            ├─ Construction
├─ US GAAP (Ch 15)            ├─ Extractives
└─ ASBE (Ch 16)               ├─ Software
                              └─ Real Estate

Advanced Features:            Infrastructure:
├─ Solver optimization        ├─ Review UI
├─ Probabilistic inference    ├─ Multi-user
└─ Causal analysis            └─ Deployment
```

## 💰 Resource Allocation by Phase

```
Phase 1: Documentation (9 PM)
─────────────────────────────────────────
Technical Writers    ████████░░ (4 PM)
Accountants          ████░░░░░░ (2 PM)
Domain Experts       ███░░░░░░░ (1.5 PM)
External Review      ███░░░░░░░ (1.5 PM)

Phase 2: Core Infrastructure (49 PM)
─────────────────────────────────────────
Software Engineers   ████████████████████░░░░ (25 PM Extraction)
                     ████████████░░░░░░░░░░░░ (12 PM Compiler)
ML Engineers         ████░░░░░░░░░░░░░░░░░░░░ (4 PM Models)
DevOps               ████░░░░░░░░░░░░░░░░░░░░ (4 PM Infra)
QA Engineers         ████░░░░░░░░░░░░░░░░░░░░ (4 PM Testing)

Phase 3: Standards & Industry (30 PM)
─────────────────────────────────────────
Accountants          ██████████████░░░░░░░░░░ (14 PM Rules)
Software Engineers   ████████████░░░░░░░░░░░░ (12 PM Impl)
Domain Experts       ████░░░░░░░░░░░░░░░░░░░░ (4 PM Review)

Phase 4: Validation (12 PM)
─────────────────────────────────────────
Data Scientists      ████████░░░░░░░░░░░░░░░░ (6 PM Eval)
Annotators           ████░░░░░░░░░░░░░░░░░░░░ (3 PM Corpus)
Software Engineers   ███░░░░░░░░░░░░░░░░░░░░░ (2 PM Harness)
External Auditors    █░░░░░░░░░░░░░░░░░░░░░░░ (1 PM Review)

Total: ~100 PM across all phases
```

## ✅ Delivered vs. ⏳ Remaining

```
Delivered in This Task:
════════════════════════════════════════════════════════════════
✅ Gap Analysis (759 lines)                           COMPLETE
✅ V2 Document Structure (24 chapters)                 COMPLETE
✅ Chapter 14: IFRS Mapping (~35 pages)                COMPLETE
✅ Chapter 17: Extraction Pipeline (~30 pages)         COMPLETE
✅ README, INDEX, COMPLETION_SUMMARY, VISUAL_ROADMAP   COMPLETE

Remaining for Full V2:
════════════════════════════════════════════════════════════════
⏳ Chapter 15: US GAAP Mapping (~30 pages)
⏳ Chapter 16: ASBE Mapping (~25 pages)
⏳ Chapter 18: Industry Extensions (~40 pages)
⏳ Chapter 19: Solver Algorithms (~30 pages)
⏳ Chapter 20: Probabilistic Inference (~35 pages)
⏳ Chapter 21: Forecast Evaluation (~40 pages)
⏳ Chapter 22: Implementation Roadmap (~30 pages)
⏳ Chapter 23: Additional Worked Examples (~20 pages)
⏳ Chapter 24: Gap Resolution (~15 pages)

V2 Complete = Delivered (65 pages) + Remaining (265 pages) = ~330 pages
Plus v1.2 Part I preserved (~80 pages) = ~410 pages total
```

## 🎓 Key Takeaways

1. **V1.2 was a strong conceptual design** but lacked:
   - Standards authority (no paragraph-level mapping)
   - Implementation guidance (no extraction, compiler, solver details)
   - Validation evidence (no evaluations run)

2. **This delivery addresses the most critical gaps**:
   - ✅ Comprehensive gap analysis (complete audit of v1.2)
   - ✅ Standards mapping template (Chapter 14 demonstrates feasibility)
   - ✅ Extraction architecture (Chapter 17 provides actionable design)

3. **Remaining work is well-defined**:
   - 9 chapters designed but not yet written
   - Clear structure and scope for each
   - Resource estimates and timelines provided

4. **Path to production is clear**:
   - Complete V2 documentation (9 PM)
   - Implement core infrastructure (49 PM)
   - Build standards packages (30 PM)
   - Validate and deploy (12 PM)
   - Total: ~100 PM (~2 years with 4 FTEs)

---

**Status: Delivery complete. Ready for stakeholder review and next-phase decision.**

*Visual Roadmap v1.0 | 5 October 2026*
