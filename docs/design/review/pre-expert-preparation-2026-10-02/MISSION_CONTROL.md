# AccDSL mission control

Established 2 October 2026 (Asia/Hong_Kong) at the user's request.
Status: active mission; Version 1.1 is a repaired design candidate with checked
reference cases. Full product, domain and human acceptance remain pending.

## Purpose

Design a system that represents a company's historical financial disclosures,
preserves economically different histories and interpretations compatible with
the evidence, and carries those alternatives into scenario-dependent future
journals and financial statements. Preserve their separate conditional outcome
distributions or feasible sets, including uncertainty that cannot be assigned
defensible probabilities.

The immediate deliverable is a detailed, readable LaTeX product and method
design, with compiled PDF, supporting literature and software investigation,
precise implementation contracts and acceptance examples. The eventual product
is the working representation and simulation engine. A document build, a small
financing example and an implemented prototype are different achievements.

## Authority and origin

This mission records the user's existing directions; it does not replace new
user instructions or higher-priority instructions. The three original requests
are preserved in saved session `01a0f8e0-0c0b-7332-8f7e-d6b93ce32761`, at JSONL
records 10, 115 and 145. They establish whole-company history, heterogeneous
accounting, preservation of alternative journals/outcomes, a broad literature
and software survey, and an implementation-governing LaTeX document. The current
request establishes this durable mission and a requirements-based gap audit.

The [requirements register](docs/plans/accounting-mission-requirements.md)
distinguishes direct user requirements from policy obligations and engineering
requirements derived from those goals. Python, storage engines, parser design,
solver libraries and a particular first-company example remain replaceable
implementation proposals. Designing a DSL is part of the work; claiming it is
better than all alternatives is not a predetermined conclusion.

## Main goals

| Goal | Required outcome |
| --- | --- |
| M1 — Represent the historical record | Preserve annual, quarterly and semi-annual statements, notes, policies and relevant referenced disclosures, with their source, context, temporal meaning and unresolved content. |
| M2 — Preserve alternative explanations | Represent joint families of admissible histories, journal movements, contract states and interpretations; distinguish absent facts, accounting choices, estimates and future randomness. |
| M3 — Simulate financial evolution | Apply explicit economic scenarios and behaviour to economic state, generate admissible journal entries, and produce coherent future statements and conditional results. |
| M4 — Handle accounting and sector diversity | Accommodate IFRS, US GAAP and China GAAP/ASBE, industry and company differences, group boundaries, banks, insurers, liabilities, capital, bonds and equity. |
| M5 — Specify implementable methods and language | Define reconstruction, accounting, inference and execution procedures, types, IR, DSL, interfaces, failure behaviour and persistence precisely enough for compatible implementations. |
| M6 — Ground choices in research and reusable tools | Inspect primary literature beyond the existing collection and official software, archive relevant sources, compare credible alternatives and document justified inclusion/exclusion and reuse decisions. |
| M7 — Deliver the governing design | Produce one rigorous, understandable LaTeX/PDF argument with complete worked cases, explicit scope, source support, method details and an implementation sequence. |
| M8 — Establish evidence and maintain direction | Define conformance and release evidence, preserve reproducibility, keep engineering/accounting/scientific conclusions separate, and maintain requirements and open decisions as work proceeds. |

## Requirements that must survive every implementation choice

1. Source preservation is broader than numerical extraction. Account for all
   source material within the declared disclosure package, including notes and
   cross-references. Content that cannot yet be formalised stays visible with
   a reason; it is not silently excluded from a completeness claim.
2. Preserve reported assertions, derived consequences and modelling assumptions
   separately. A missing value is not zero; a reported number is not automatic
   proof of the underlying economic state. Source conflicts remain inspectable.
3. Carry entity, group perimeter, concept, dimensions, units, currency, basis,
   precision and time through every calculation. Label mapping does not itself
   convert between accounting standards. Avoid double counting overlapping
   classifications.
4. Preserve original and revised information. Economic time, reporting periods,
   availability/publication and system ingestion/version time answer different
   questions. Historical forecasts cannot use later evidence inadvertently.
5. Keep alternatives jointly consistent across statements, notes, dates,
   contracts and accounts. Include economic state beyond journals: identical
   historical postings can conceal different future exposures.
6. Every reconstructed family has an explicit model scope and completeness
   status. A selected witness, bounded search or convenient aggregate cannot be
   presented as all real histories. Scope exclusions remain mission limitations.
7. Preserve conditional results by explanation and scenario. A set or interval
   does not become a probability distribution without a declared measure. No
   weights from representation counts, arbitrary equality or LLM confidence.
   Keep dependence between statement amounts and through time.
8. Generate events from explicit contract and behavioural assumptions, then
   apply recognition/measurement and posting rules. Balanced journals are
   necessary but do not prove accounting treatment or economic correctness.
9. Treat unsupported calculations, unresolved branches, numerical failure and
   economically meaningful default as distinct outcomes. Do not silently drop
   failed branches, manufacture financing or report sampled extrema as exact
   bounds.
10. Compare a DSL with credible alternatives on the same tasks, especially the
    typed-library/shared-IR baseline. Reuse software where its inspected
    capabilities fit, with explicit adapter contracts and limits.
11. Support imported technical claims with inspected primary sections and local
    copies. Preserve relevant papers under `docs/papers` using
    `Title First-author-surname (year).pdf`; preserve the original collection.
    Technical reading, actual literature screening and source corrections must
    be recorded, not inferred from metadata or generated status labels.
12. Make assumptions, derivations, scope and limits understandable in the
    manuscript itself. Full company cases and precise expected outputs must
    connect the concepts to implementation. Page count and polished prose are
    not substitutes for these requirements.

## What counts as completion

The [requirement register](docs/plans/accounting-mission-requirements.md)
defines evidence needed for MC01–MC34. Each requirement must have an identified
document location, stated behaviour/method, a suitable worked case or other
check, and an honest assessment. A mention is `partial`; promised future work
is `open`; a precise design is `specified`; checked evidence can support
`checked` within its stated scope. `Not checked` is never silently converted
to `passed`. These are design statuses, not implemented-product statuses.

A proposed implementation-governing design requires:

- complete scope and methods for the declared initial executable profile;
- a concrete structural design and method/support obligations for every
  explicitly requested domain, including later bank and insurance modules;
- source-to-record-to-history-to-journal-to-statement worked cases, with
  uncertainty, revisions and failure cases;
- exact interfaces and conformance fixtures for the supported language/model;
- inspected support for imported claims and explicit disposition of genuine
  source gaps;
- checked mathematics, references and rendered presentation, with review
  records identifying what was and was not checked.

A source gap blocks its unsupported claim. A missing later engine does not
block the initial core, but a method that is still unspecified remains open
in the full design. Do not close the wider mission merely by making a tiny
model's scope exclude every difficult case. Scope reductions require actual
user direction; routine choices within the scope do not require repeated
permission.

Human comprehension, independent domain review, executable conformance and
scientific forecast validation retain their own pending or completed states.
Missing feedback does not block provisional drafting and repair. Do not
invent acceptance or claim a compliant engine from author self-review.

## How work is controlled

Before a nontrivial work unit, identify its MC requirements, current gaps,
assumptions and smallest useful validation. Perform the skeptical plan audit
required by the project policies. Use the existing research-plan/evidence
workflow for actual experiments; document-only edits do not need invented
research metrics or a performance campaign.

After a substantive change, update the affected requirement assessments and
the [checkpoint](docs/plans/accounting-product-design-checkpoint.md). A gap
closes only against its stated evidence. Maintain continuity between the
original [G1–G10 audit](docs/design/review/gap-audit-2026-10-02.md) and the
[expanded audit](docs/design/review/mission-gap-audit-2026-10-02.md). New findings
can be added; neither list is asserted to be permanently exhaustive. Review
interactions between requirements, not only the rows separately.

Use separate judgements for the document, engineering implementation,
accounting validity and scientific interpretation. Follow the applicable
policies in `/home/chakwong/python/claudecodex/policies`, including scientific
coding, literature audit and natural reader-facing prose. Operational mission
records belong here, not as repeated administrative scaffolding in the paper.

Current next substantive work: implement and independently test Core 0 reference
resolution, semantic validation and shared-IR compilation, then the bounded
Northstar reconstruction/execution path. Use the new cases to validate selected
adapters. Acquire missing accounting authority and expand the real corpus as
bank/insurer and broader standards methods advance. These stages preserve the
full mission; their unimplemented status does not erase the design delivered.

## Current assessment and open decisions

The [reviewed repair plan](docs/plans/accounting-gap-repair-2026-10-02.md) has
been executed as a bounded document/specification campaign. The revised
[design](docs/design/accounting-product-design.pdf) has 11 chapters and two
appendices, a complete synthetic company, a named Apple disclosure case,
rounded reconstruction, finite probability examples, corporate/sector cases,
Core 0 contracts and acceptance protocols. The [result map](docs/design/review/gap-repair-results-2026-10-02.md)
records G1–G18 repairs and remaining obligations. All MC01–MC34 assessments
have been updated without changing their requirement or acceptance wording.

Reference arithmetic, solver, grammar/schema and review checks support their
stated examples only. The full compiler/runtime and non-Z3 adapters are not
implemented. The real filing has complete acquired-file inventory but partial
semantics and incomplete external incorporation closure. Full ASC authority,
official-current ASBE verification, richer bank/insurance methods, independent
accounting/implementability review and human comprehension remain open.

Decisions now recorded include Northstar/Apple, rational-linear reconstruction,
separate evidence clocks and review actions, deterministic operating assumptions,
optional finite weights, schema/identity/storage boundaries, corpus strata and
provisional workload limits. Future measured capacity, production library locks,
empirical forecast calibration and corpus adjudication need their own evidence.
The [checkpoint](docs/plans/accounting-product-design-checkpoint.md) preserves
commands, review records and the next justified steps. No scope reduction or
whole-mission completion is implied by this candidate.

No external deployment, global agent-policy installation, production-security
programme, full-economy equilibrium model or forecast-superiority claim is
implied by this mission. Such work needs its own substantive justification.
