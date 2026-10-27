# AccDSL documents

The canonical governing document is [AccDSL-latest.pdf](AccDSL-latest.pdf),
currently **Version 5.50, 827 pages**, dated 27 October 2026. Its
[LaTeX entry point](AccDSL-latest.tex) points to the same source package.

Read [Company Histories and Scenario Simulation](AccDSL-simulation-foundations.pdf)
for the new 26-chapter treatment of historical ambiguity, financing, learning,
scenario computation and failure cases. This standalone edition has **261 pages**,
including **240 body pages**; its [LaTeX root](AccDSL-simulation-foundations.tex)
uses the same chapter files as Part I of the governing document.

The proposal recommends joint families of economic histories, explicit contract
and ownership state, actor-specific information, and computation tailored to the
question. Worked cases explain where symbolic sharing, aggregation, sampling,
scenario reduction and robust decisions can fail, and how to preserve unresolved
possibilities and report defensible results.

- [Current master program](plans/accounting-master-current.md).
- [Full remaining-work queue](../data/accounting-master/gap-credit-recovery-refresh-20261027/remaining-work.md).
- [Conditional acquisition design](../data/accounting-master/acquisition-symbolic-20261027/result.md).
- [Dated acquisition authority](../data/accounting-master/acquisition-period-authority-20261026/result.md).
- [Actor observation maps and reuse](../data/accounting-master/observation-map-binding-20261027/result.md).
- [Partial temporal policy conclusions](../data/accounting-master/partial-frontier-policy-20261027/result.md).
- [Resumable exact temporal partitions](../data/accounting-master/temporal-frontier-20261027/result.md).
- [Complete temporal-family binding](../data/accounting-master/temporal-family-binding-20261027/result.md).
- [Policies across uncertain observation mechanisms](../data/accounting-master/cross-mechanism-policy-20261027/result.md).
- [Exact temporal source-view families](../data/accounting-master/source-time-intervals-20261027/result.md).
- [Control-history and group-method scope](../data/accounting-master/control-group-boundary-20261027/result.md).
- [Conditional whole-interval control history](../data/accounting-master/control-history-contract-20261026/result.md).
- [Source revision and actor views](../data/accounting-master/certified-source-views-20261026/result.md).
- [Dependency-scoped policy reuse](../data/accounting-master/source-policy-invalidation-20261027/result.md).
- [Certified observation policies](../data/accounting-master/certified-observation-policy-20261026/result.md).
- [Conversion control and reporting scope](../data/accounting-master/conversion-control-scope-20261026/result.md).
- [Control-history boundary repair](../data/accounting-master/control-boundary-repair-20261026/result.md).
- [Exact region proofs and saved queue](../data/accounting-master/exact-region-certificates-20261026/queue-result.md).
- [Common accounting and checkpoint evidence](../data/accounting-master/guarded-memory-runtime-20261026/result.md).
- [Two-date cash and contractual memory](../data/accounting-master/two-date-continuous-memory-20261026/result.md).
- [Exact continuous guard comparison](../data/accounting-master/continuous-guards-20261026/result.md).
- [Current integration and checks](../data/accounting-master/credit-recovery-integration-20261027/result.md).
- [Prior complete-claims integration](../data/accounting-master/complete-claims-integration-20261026/result.md).
- [Literature closure: plan, execution and remaining gaps](../data/accounting-master/literature-closure-20261026/result.md).
- [Particle-MCMC proof and rejection-state counterexample](../data/accounting-master/literature-closure-20261026/pmcmc-dependency.md).
- [Technical supplement: learning, compression and financing](design/research/simulation-literature-closure-20261026/supplement.pdf), with [LaTeX source](design/research/simulation-literature-closure-20261026/supplement.tex).
- [Documentation result and checks](../data/accounting-master/simulation-monograph-20261026/result.md).
- [67 failure mechanisms and proposed remedies](../data/accounting-master/simulation-monograph-20261026/failure-index.md).
- [Citation/source records](../data/accounting-master/simulation-monograph-20261026/source-support.json).
- [Mission control](../MISSION_CONTROL.md), [requirements](plans/accounting-mission-requirements.md), and [current checkpoint](plans/accounting-product-design-checkpoint.md).
- [Archived Version 1.2](archive/accounting-product-design-v1.2-20261026/ARCHIVE.md), including its original PDF, sources and hash manifest.

These stable relative links are updated only after a successor is built and
checked. Build from the resolved source directory, not from the docs alias,
so relative chapter and bibliography paths resolve. The source package includes
LuaLaTeX build instructions.

The manuscript remains a design candidate (not_ready). Independent reader and
domain acceptance, broader implementation and real-company validation remain
pending. The failure catalogue and literature survey are extensible; neither
claims to enumerate every possible case or source.
