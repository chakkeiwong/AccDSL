# AccDSL documents

The canonical governing document is [AccDSL-latest.pdf](AccDSL-latest.pdf),
currently **Version 5.21, 765 pages**, dated 26 October 2026. Its
[LaTeX entry point](AccDSL-latest.tex) points to the same source package.

Read [Company Histories and Scenario Simulation](AccDSL-simulation-foundations.pdf)
for the new 26-chapter treatment of historical ambiguity, financing, learning,
scenario computation and failure cases. This standalone edition has **198 pages**,
including **180 body pages**; its [LaTeX root](AccDSL-simulation-foundations.tex)
uses the same chapter files as Part I of the governing document.

The proposal recommends joint families of economic histories, explicit contract
and ownership state, actor-specific information, and computation tailored to the
question. Worked cases explain where symbolic sharing, aggregation, sampling,
scenario reduction and robust decisions can fail, and how to preserve unresolved
possibilities and report defensible results.

- [Current master program](plans/accounting-master-current.md).
- [Full remaining-work queue](../data/accounting-master/gap-memory-refresh-20261026/remaining-work.md).
- [Two-date cash and contractual memory](../data/accounting-master/two-date-continuous-memory-20261026/result.md).
- [Exact continuous guard comparison](../data/accounting-master/continuous-guards-20261026/result.md).
- [Current integration and checks](../data/accounting-master/two-date-memory-integration-20261026/result.md).
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
