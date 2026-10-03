# Accounting representation and simulation product design

Date: 2026-10-02 (Asia/Hong_Kong). Authoring campaign; no production engine or
research-grade performance experiment is being executed.

Current authority: [mission control](../../MISSION_CONTROL.md) and its
[MC01–MC34 requirements](accounting-mission-requirements.md), installed on
2 October 2026 from the user's original and current directions. This authoring
plan remains the execution history; it cannot narrow those requirements.
The [initial gap audit](../design/review/gap-audit-2026-10-02.md) and
[expanded mission audit](../design/review/mission-gap-audit-2026-10-02.md)
show that substantive specification work remains. The earlier narrow
final-review phase below is superseded.

## Deliverable and reader

Produce `docs/design/accounting-product-design.tex` and its compiled PDF as the
proposed governing implementation specification. The readers are accounting,
financial-modelling and language-engineering researchers and implementers.
Explain the argument continuously, then specify executable interfaces, types,
semantics, algorithms, scope boundaries and acceptance tests precisely enough
to implement. Preserve source material under `docs/papers` using
`Title First-author-surname (year).pdf`; standards and software evidence have
separate directories. Do not rename or remove the user's existing collection.

The central requirement is a set of historically compatible company histories,
contract states and interpretations whose distinct conditional future journal
and statement distributions survive scenario simulation. Unknown facts,
interpretations, future randomness and optional probability weights are distinct.

## Skeptical plan audit

The initial plan passes with these corrections incorporated before execution:

* Compare a typed schema plus ordinary code, XBRL, ledger tools, rule languages,
  probabilistic languages and a small accounting DSL on the same requirements.
  A DSL is a design hypothesis, not a proven superior method.
* Compilation, journal balance, counts of papers, and extraction benchmark
  accuracy cannot certify source fidelity or forecasting validity.
* Inspect the technical portions of primary sources and original software;
  metadata and abstracts nominate sources only. Preserve blocked and omitted
  candidates, version conflicts and correction checks explicitly.
* Treat public disclosures as incomplete observations. Do not reconstruct a
  unique ledger by fiat, use equal branch weights by default, or infer causal
  responses from accounting identities.
* No model/API workers, training, GPU work, dependency installation or performance
  ladder is needed for this document. Existing local TeX and PDF utilities suffice.
* Numerical examples are derived illustrations checked with exact arithmetic;
  their checks support the examples only. Tool surveys report inspection level.
* Continue through localized retrieval/build failures; stop a source-specific
  claim when primary support is unavailable and substitute a qualified design
  decision or another checked source. Do not declare an exhaustive global survey.

## Evidence and source contract

Question: which representation, uncertainty semantics and implementation design
can preserve historical evidence and economically distinct alternatives while
producing coherent scenario-dependent journals and financial statements?

Primary acceptance: every requested topic has a concrete implementation contract;
important imported claims have inspected primary anchors; local mathematical
claims have derivations; all cited accessible papers are archived; the PDF builds
with resolved references and has undergone rendered inspection and substantive
author review. Missing support vetoes the affected claim, not continued drafting.

Explanatory diagnostics: paper counts, document length, typography checks and
software popularity. They are not scientific or readability acceptance metrics.
No claim of implemented product, regulatory completeness, extraction accuracy,
forecast superiority or human acceptance follows from this authoring campaign.

## Scope and method

1. Review the three policies in `/home/chakwong/python/claudecodex/policies` and
   the scholarly narrative, natural prose and readability skills.
2. Search primary/public indexes across accounting models, reporting standards,
   temporal and uncertain databases, provenance, inverse problems and partial
   identification, model uncertainty, financial contract languages, document
   extraction and financial reasoning, and scenario simulation.
3. Archive a broad, tractable core, use backward and forward snowballing, inspect
   technical support and software, and record six separate literature ledgers.
4. Draft the document around a borrowing/repricing example, extending it through
   evidence, identification, temporal history, language semantics and execution.
5. Specify the core grammar and intermediate representation; source/time/units
   and partial-information types; joint constraints; hypothesis families and
   optional weights; event/posting semantics; state and reporting interfaces;
   standards/industry modules; diagnostics; APIs; persistence; and acceptance.
6. Compile, check the worked arithmetic, audit claims and references, inspect the
   rendered manuscript in document order, repair confirmed findings and rebuild.

Assumptions: public filings are the initial evidence boundary; richer transaction
data can be added; the engine supports conditional scientific analysis. Python
reference execution, exact decimal/rational accounting arithmetic and an initially
bounded DSL are proposed engineering choices subject to implementation tests.
The manuscript must identify which choices are fixed requirements and which are
replaceable implementation choices. No arbitrary scientific threshold is promoted.

## Durable evidence

* `docs/design/research/source-support.json`
* `docs/design/research/citation-venue.json`
* `docs/design/research/backward-snowball.json`
* `docs/design/research/forward-snowball.json`
* `docs/design/research/claim-support.json`
* `docs/design/research/omissions.json`
* `docs/design/research/tools.json`
* `docs/design/review/` for build, arithmetic and manuscript review evidence.
* `docs/plans/accounting-product-design-checkpoint.md` for the current next action.

Human comprehension review and independent scholarly review are distinct from
author checks. Continue the complete requested draft now; record these reviews
as pending rather than inventing acceptance or stopping for another permission.

## Historical final author-review pass — superseded

The complete draft builds to 60 pages with 31 verified paper PDFs. The final
pass is bounded to notation, probability-measure assumptions, literal citation
lead provenance, code/table pagination, and navigation/reproduction records.
The skeptical audit finds no need for an experiment or an integration claim:
the examples remain derived illustrations and the tool survey remains source
inspection. Correct two possible overclaims before delivery: arbitrary semantic
equivalence is not a solved compiler capability, and cross-survey comparators
must not be represented as references cited by an earlier seed. Preserve a
pre-final source/PDF snapshot and inspect changed rendered pages after building.
Source, arithmetic, layout and human-comprehension evidence remain separate.
The user's requested core design can be delivered with explicitly documented
access gaps; no blocked paper supplies an imported technical claim.

## Current work sequence under mission control

The current task installed the mission and assessed completeness; it did not
repair the manuscript or start the engine implementation. Future work should
name the MC requirements it addresses and use the updated checkpoint.

First specify the full reference company/disclosure cases (MC28), including
coverage, narrative meaning, temporal views and concept mappings (MC01–MC07).
Use those cases to define the historical scope and reconstruction methods,
economic/accounting state, transitions, output families and supported solver
operations (MC08–MC18, MC24–MC27). Test the proposed core structurally against
the requested standards and bank/insurer/financing needs before freezing its
types (MC17, MC19–MC22). Perform targeted literature and software work for the
actual methods selected (MC23, MC29–MC31).

Acceptance then requires the concrete document and conformance evidence in
MC32–MC34, with accounting and human-review status recorded separately.
Resolve or explicitly retain open gaps; do not promote the draft merely from
its existing length, build success, archived paper count or arithmetic checks.
