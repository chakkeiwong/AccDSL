# Focused P18 integration-repair review

Act as a read-only reviewer with no tools/edits/commands. This is a bounded review of two previous blocking findings and their nearby repairs. Do not restart a whole-proposal review. The original manuscript was independently reviewed in six packets: type, corporate, sectors and inference returned AGREE; transactions and argument returned REVISE. Full domain, source and human-readiness gaps remain explicit and are not the repair target.

Check: (1) copied storage table now includes transactionally owned branch heads, authorization, economic deltas, receipts, views and checkpoints with no speculative journal publication; (2) the single P0–P6 implementation sequence now maps portable records/review/time/receipts and typed authoring to P0, admitted histories to P1, connected corporate methods plus the matched debt text frontend to P2, preserving broader P3–P6 obligations. Product implementation remains future work.

Also inspect the nearby corrections: execute_event now takes the OperationRequest; complete fingerprint identity is explicit; corrections are new linked events; migration expected_head lives only in the envelope; unknown solver outcome is not infeasibility. Forecast comparison ladders were merged without dropping the single-interpretation comparison, and actual issuer cadences explain 192 reports. The provided persistence/cross-contract documents are accepted baselines. Do not propose changing frozen fixtures or accepted architecture.

Return only actual remaining repair blockers or introduced contradictions, with file/section and minimal fix, plus a brief reason. Limit answer to 800 words and finish VERDICT: AGREE or VERDICT: REVISE. Successful build/render records are being regenerated separately and are not certified by this review.

## ORIGINAL FINDINGS transactions
**Scope checked:** journal authorization (authorization.tex vs A1), replay-before-freshness (authorization.tex, 07 pseudocode, 09 identity section vs P2/P3), immutable review views and correction (09, operations-storage vs P4/A4/A6), migration/checkpoint (operations-storage, 09 vs P3/P5), adapter failure descriptions (adapter-methods, 09 adapters). The core transaction contract is transcribed consistently: assess@1 read-only, authorize@1 producing PostingAuthorization, four-ref commit arguments with expected head only in the outer request, four-tuple lookup key, fingerprint containing payload/version/opening state/request settings, equal-fingerprint replay → conflict → absent-key freshness → atomic recheck, three-valued commit observation, no fresh event ID on timeout. Book_mode/evidence-scope gating, candidate-set invalidation, selection-owner behaviour, checkpoint manifest rules and representation-only migration constraints all match the P16 records. The worked arithmetic (95/100/−5; 90=100−10; 110.25 bond; 120/10/110 equity; 1.234 scaling) is correct. Retained open gaps (ASC, insurance, real data, acceptance) are not counted below.

**Findings**

1. **09-implementation.tex, §Persistent records (longtable) — blocking.** The relation list is old prose that predates the transaction contract. It has no `branch` (branch_key, immutable definition Ref, required `book_mode`, mutable head `(state_ref, generation)`), no `committed_receipt` index, no `economic_delta`, no `posting_authorization`, no `review_view`, no `search_checkpoint`, although operations-storage.tex says "One logical transactional store owns records, dependency edges, review views, branch heads, journals, economic deltas, receipts and search checkpoints" and P2's four domains are state/journal/delta/receipt index. Worse, `journal_batch` carries an "atomic commit status" column, which implies non-committed journals living in the journal relation, contradicting P2 ("No speculative candidate is published as committed… Candidate scratch data and diagnostics are not members of those domains"). `economic_event` is keyed by "Stable event ID… scenario and branch" without entity/book, so it does not expose the four-tuple. **Repair:** add rows for branch/head, posting_authorization, economic_delta, committed_receipt, review_view and search_checkpoint; key `economic_event` by the four-tuple; remove "atomic commit status" from `journal_batch` (or state that only committed journals appear there and candidates are separate scratch records).

2. **09-implementation.tex, §Reference implementation and §Identity (storage ownership) — nonblocking.** "SQLite for transactional metadata… columnar files for large scenario outputs" and "SQLite owns source, review and run metadata transactions" leave it ambiguous whether committed journals, deltas, receipts and heads of simulation branches are in the transactional store or in columnar output files. operations-storage/P1 require them in the one transactional owner, with columnar tables as derivatives. **Repair:** one sentence stating that committed journals/deltas/receipts/heads are transactional-store members and columnar files hold only derived analytical exports of them.

3. **07-execution.tex, §Schedule and commit events, pseudocode — nonblocking.** The signature `execute_event(event_basis, posting_profile, original_request)` takes a posting profile as input, but the contract takes `AccountingCommitArguments {basis_ref, authorization_ref, journal_ref, delta_ref}` inside an `OperationRequest`; the profile is already bound inside the PostingAuthorization produced by authorize@1. The body ("validate separate posting authorization, journal and delta") is correct; only the header is stale. **Repair:** change the signature to `execute_event(operation_request)` or list the four refs plus expected_head.

4. **07-execution.tex, same section, "A repeated event ID with identical inputs returns the existing result; the same ID with different inputs is a conflict" — nonblocking.** operations-storage.tex states the fingerprint includes request_id and expected generation, and that changing request_id for a committed event conflicts. A reader of 07 alone could infer that resubmitting the identical payload under a fresh request_id replays. **Repair:** add "inputs include the request identifier, expected head and execution settings" or cross-reference the fingerprint definition.

5. **authorization.tex §replay / 09 §Review decisions — missing premise, nonblocking.** P4 states that correcting a committed economic event is a new business event linked to its predecessor with a specified correction method (reversal/replacement or dated adjustment), never an overwrite, and that a version bump alone does not post it. The manuscript states that a bumped version "cannot evade a conflict" but never says how a committed event is corrected; the review section covers readings only. Likewise operations-storage's migration input omits P5's `expected_head`. **Repair:** add one sentence to §replay on event correction as a new linked business event (treatment authority from P17, unresolved if absent), and mention expected_head in the migration input list.

6. **07-execution.tex (`SolverIncomplete`), 09 §Plugin interfaces (`unknown`), A2 (`solver_unknown` → unresolved) — nonblocking naming drift.** Not contradictory (engine result vs adapter result vs coverage label), but no sentence links them. **Repair:** state that the adapter's `unknown` surfaces as `SolverIncomplete` in HistoryFamily and maps to the `unresolved` coverage subtype.

**Reason for verdict.** Authorization, replay ordering, immutable views, checkpoint/migration and adapter failure prose are faithful to A1/A2/A4/A6 and P1–P5, and the worked examples hold. However, the implementation chapter's persistent-records table—the one place a reader expects the stored objects behind P2's replay—omits receipts, heads, deltas, authorizations and views and carries a journal "commit status" that conflicts with the no-speculative-publication rule. That is an actual missing premise in copied old prose relative to the new transaction contract and should be corrected before this integration scope is accepted; the remaining findings are minor.

VERDICT: REVISE

## ORIGINAL FINDINGS argument
# Bounded P18 integration review

Scope accepted as stated: manuscript argument, requirements and acceptance exposition only; P16/P17 are baselines; retained domain/source gaps are not new failures.

## Findings

**F1 (material) — Disconnected implementation sequence, `10-validation.tex`, §"Decisions and replaceable assumptions".**
The paragraph states "The proposed dependency order begins with portable records, review/time selection and durable receipts, then typed authoring, admitted history templates and connected corporate methods. The implementation stages below are a design sequence…". Two defects: (a) the milestone table (P0–P6) is *above* this paragraph, not below; (b) its vocabulary ("portable records", "durable receipts", "admitted history templates", "connected corporate methods") does not appear anywhere in the P0–P6 deliverables ("evidence registry, contextual types, versioned IR, exact posting engine…"). A reader is given two dependency orders that are never reconciled. Repair: either map each phrase onto a named stage (e.g. "portable records/receipts = P0 evidence registry and replay; typed authoring = P2 Core 0 frontend; admitted history templates = P1 bridges; connected corporate methods = P2–P3 corporate package") or delete the second ordering and fix "below" → "above". This is the only blocking item.

**F2 (minor, nonblocking) — Review-cycle residue presented as manuscript content, `10-validation.tex` §"Concrete conformance…" and §"Workload limits…", `12-research.tex` §"Companion records and status".**
"The present repair supplies a richer design candidate", "The repair adds Mack's reserving paper…", "The retained panel now contains…", "Every one of the 179 unique candidates … now has…". A product proposal reader has no referent for "the repair" or the implied prior state; the wording describes editing history, not the specification. Repair: replace with stative phrasing ("This version supplies…", "The research library includes Mack…", "The retained panel contains…"). The script name `check_repair_conformance.py` may stay since it is a literal file reference.

**F3 (minor, nonblocking) — Corpus arithmetic not taught, `10-validation.tex` §"Concrete conformance and corpus protocol".**
"192 target annual/interim reports … across nine issuers … eight consecutive complete years per issuer" does not divide evenly (192/9 ≠ integer) and is reconcilable only if issuers have different interim cadences (e.g. three quarterly filers × 32 + six semi-annual filers × 16 = 192). The counts 136 + 56 = 192 and 244 ≥ 192 are internally consistent. Repair: add one sentence giving the per-issuer report mix so the total is derivable; otherwise the count reads as unverifiable. Not labelled an error — the number may be correct.

**F4 (minor, nonblocking) — Duplicated baseline prescription, `10-validation.tex` §"Forecasting evaluation comes later".**
Paragraph 1 ("comparator ladder … naive, contractual runoff, tuned classical, structural, extensions") and paragraph 4 ("Baselines should include a naive persistence or ratio model, a tuned conventional financial model, the structural model with a single selected interpretation, and the same model preserving alternatives") specify overlapping but not identical ladders; the second adds the single-interpretation vs. alternatives split absent from the first. Repair: merge into one ladder so a later experiment plan has one normative list.

**F5 (minor, nonblocking) — Forward reference out of the literature chapter, `03-literature.tex` §"Accounting structure…".**
"AccDSL's event and counterparty records are specified and justified directly below" — nothing below in that chapter does so; the specification is in later chapters. Repair: "in Chapters~\ref{ch:math}–\ref{ch:execution}" or equivalent.

**F6 (minor, nonblocking) — Boundary of "render inspection", `12-research.tex` §"Companion records and status".**
The chapter states companion records cover "rendered-page inspection". The packet treats render inspection as separate from this review; the sentence is acceptable only if that record exists independently. Repair: none required for this packet; note that this review does not confirm it.

## Checks that passed

- Readiness language is consistently hedged: title page ("not a completed product or a claim of full proposal readiness"), Ch. 10 opening ("do not constitute a production implementation"), "No such forecast experiment has been run", "The present document runs only deterministic checks of its own examples". No unearned readiness claim found.
- Source boundaries: Ch. 3 and Ch. 12 agree on blocked candidates (McCarthy, Imieliński–Lipski, Caiani), on version discrepancies (Doshi 2024, Mernik 2003 report, Giacomini–Kitagawa 2020 WP, Docling/Auer, Libkin DOI), and on the 2 October 2026 freeze; 25 + 7 = 32 PDFs; six ledgers enumerated = six. Search-provenance is frozen as required.
- Test coverage: T01–T18 are each assigned to exactly one stage (P0: T01–T04, T09, T17; P1: T05–T10, T14, T18; P2: T11–T13; P3: T15; P4: T16). T05/T06 agree with eq. (1) in Ch. 1 (5, 7, $7-2\alpha$).
- Ch. 1 requirements R1–R10 are matched by Ch. 4 responsibilities and Ch. 10 veto conditions (source span, entity/unit/period/basis, invented evidence, hidden financing, dropped branch, cash reconciliation).
- Retained gaps (ASC access, ASBE 1 verification, actuarial/regulatory data, human review, 136 unverified publication dates) are stated at the operations they affect and are not treated as closed.

## Verdict reason

The integration is sound in its claims, boundaries and counts; the single material defect is that the manuscript now carries two unreconciled implementation sequences with a misdirected pointer, which is precisely the "disconnected implementation sequence" failure class. F2–F6 are editorial and nonblocking.

VERDICT: REVISE


## FILE docs/design/proposal/manuscript/chapters/09-implementation.tex
\chapter{Implementation contracts}
\label{ch:implementation}

\section{Reference implementation and component boundaries}

The proposed reference implementation uses Python for orchestration and a deterministic
reference evaluator, exact decimal/rational arithmetic for booked amounts,
SQLite for transactional metadata and versioned records, and columnar files
for large scenario outputs. DuckDB is an optional analytical reader. These
are convenience choices justified by inspectability and modest initial scale;
they do not establish production performance. The IR and conformance tests
allow a later compiled executor without changing accounting meaning.
Committed journals, economic deltas, receipts and branch heads belong to the
one transactional store, including for simulation branches. Columnar files
hold derived analytical exports, never independently writable committed books.

\begin{lstlisting}
accdsl/
  evidence/       documents, spans, filing contexts, extraction versions
  model/          typed IR, entities, books, symbols, contracts
  language/       grammar, parser, resolver, type checker, lowering
  constraints/    propagation, solver adapters, bounds and conflict cores
  accounting/     rule selection, posting validation, closing, consolidation
  economics/      contract and behavioural plugin interfaces
  execution/      scheduler, branch state, stochastic streams, run records
  reporting/      statements, notes, movement schedules, explanations
  storage/        versioned records, migrations, result readers
  interfaces/     Python API, CLI, structured import/export
  packages/       reviewed demonstration and accounting modules
\end{lstlisting}

The first service boundary is local and synchronous. A job abstraction can be
added for extraction and simulation without requiring distributed execution.
The model compiler returns an immutable execution plan; the executor receives
that plan and run inputs. Neither should retrieve live market data implicitly.
Input datasets and rule packages are selected and versioned before execution.

\section{Persistent records}

The table identifies logical storage relations and their obligations; exact
versioned record schemas determine their payloads. Candidate calculations and
diagnostics remain separate from the committed accounting relations.

\begin{longtable}{L{40mm}L{96mm}}
\toprule Relation & Key information and constraints\\\midrule\endhead
\code{document} & Hash, original path/URI, filing ID, entity, publication and
availability times, media type, revision links. Original bytes are retained.\\
\code{source\_span} & Document hash, page/element locator, bounding box,
text/table representation, extraction run ID.\\
\code{observation} & Context ID, value or missingness tag, precision domain,
source-span IDs, semantic-reading ID, review status.\\
\code{context} & Entity/perimeter, concept, basis, currency/unit, instant or
interval, dimensions and taxonomy version. Contexts are immutable.\\
\code{assertion\_version} & Logical assertion ID, payload hash, economic
validity, ingestion time, public availability, superseded version and reason.\\
\code{model\_node} & IR node ID, type, serialised payload, dependency IDs,
package/model version; no executable arbitrary text.\\
\code{constraint} & Expression, scope, source/assumption references, supported
solver fragment, applicable alternative condition.\\
\code{alternative} & Parent model, added conditions, rationale, evidence,
coverage declaration and rejection history.\\
\code{economic\_event} & Stable entity/book/branch/business-event key;
versioned event, contract/cohort, dates, quantities and dependencies.\\
\code{branch} & Branch key and immutable definition reference, including
entity, book and required synthetic or real book mode.\\
\code{branch\_head} & Branch owner, current state reference and generation;
updated only by the expected-head transaction.\\
\code{posting\_authorization} & Exact basis, posting profile, method,
authority, findings, permission and historical view. A permission record
alone does not establish a committed event.\\
\code{journal\_batch} & Committed balanced postings with event key, book/basis,
date, method and measurement references. Candidate journals are separate;
membership here requires the complete accounting transaction.\\
\code{economic\_delta} & Committed contractual and physical state change,
bound to the same basis and authorization as its journal.\\
\code{committed\_receipt} & Unique stable event key, full request fingerprint,
original request, opening/closing state, journal and delta references.
Published atomically with those records and the advanced head.\\
\code{review\_view} & Immutable parent view, decisions and dependency
selection revisions; preserves historical interpretation.\\
\code{dependency} & Typed source and derived-record edges, including
candidate-set membership needed for transitive invalidation.\\
\code{search\_checkpoint} & Semantic manifest, partition, explored/unresolved
regions, frontier, used budget and result references, committed together.\\
\code{run} & Evidence and model hashes, cutoff, scenarios, branch selection,
weight model, solver/numerical settings, seeds and environment.\\
\code{report\_cell} & Run, branch/scenario, context, amount or result family,
dependency references and completeness status.\\\bottomrule
\end{longtable}

Persistent identifiers are opaque; display labels can change without changing
identity. References use foreign keys or validated content-addressed links.
The full logical key of a reported fact includes its dimensions, not merely
company, label and year. Duplicate assertions are stored as distinct source
claims until a documented duplicate-resolution operation relates them.

Version records are append-only. A derived transaction-time interval can be
closed by the next version event without deleting the original payload.
Validity intervals can overlap when assertions conflict. Such overlap is
diagnosed and resolved by the evidence view, not prohibited by a database
constraint that would erase one assertion. Scenario states use structural
sharing of immutable historical nodes and branch-local changes.

Large simulation output is indexed by run, explanation, parameter draw,
scenario, innovation path, entity, book, date and account. Reducing this to
means across all dimensions would destroy the product's central feature.
Online summaries may compress draws within a declared distribution, while
retaining conditional summaries and representative replay identifiers. A
retention policy that removes individual traces must state which explanations
can still be reconstructed.

\begin{minipage}{\linewidth}
\section{Public API and result types}

The following unversioned names describe the user workflow. They are conceptual
shorthand, not the portable operation registry. The exact versioned requests
are specified below; Python, command-line and any service binding must exchange
the same typed values:
\begin{lstlisting}
ingest(manifest, extractor_config) -> EvidenceVersion
compile(source_or_ir, evidence_view, package_lock) -> ModelPlan | Diagnostics
reconcile(plan, cutoff, solver_config) -> HistoryFamily | Diagnostics
condition(family, assumptions) -> ConditionalFamily | Infeasible
simulate(family, scenario_set, run_config) -> RunResult
render(run_id, report_request) -> ReportBundle
explain(node_id, evidence_view_or_run_id) -> ExplanationGraph
compare(run_a, run_b, alignment_spec) -> Comparison
\end{lstlisting}
\end{minipage}

\code{HistoryFamily} contains a model-scope declaration, shared variables,
constraints, finite choices, feasibility status and solver-completeness status.
It may contain witness histories without claiming that those witnesses
enumerate the family. \code{RunResult} is a tagged union of concrete outputs,
conditional samples, certified bounds, explored ranges and unresolved outputs.
Probability-bearing results reference a probability-model record. Results
without that reference cannot be presented as probabilities.

Comparison requires an alignment specification: entity/perimeter, dates,
reporting basis, scenarios and shared innovations where applicable. Comparing
IFRS and US GAAP books holds economic events fixed and changes accounting
rules. Comparing management responses holds the specified scenario and
initial information fixed and changes the behavioural model. These are
different questions and must not be combined into an unexplained difference.

\input{sections/operations-storage}

\section{Plugin interfaces}

Every plugin declares a version, supported types, input information dates,
determinism, numerical measure and capabilities. A contract plugin implements
\code{schedule}, \code{observe}, \code{transition} and \code{payoff}; it may
return future conditional events. A behaviour plugin implements
\code{decide} and declares which state and scenario information it uses.
A measurement plugin implements \code{measure} and returns an amount or
vector with a basis and numerical status. A reporting plugin maps classified
journals and balances to output contexts.

The plugin response must include all inputs that materially affect results.
An external calculator's global evaluation date, market-curve cache, calendar
version or random seed cannot remain invisible. For example, QuantLib's
floating coupon interface makes fixing-date conventions and pricing objects
relevant inputs; the adapter records them rather than relying on process-global
state. ACTUS risk-factor observations receive explicit dates and identifiers.

The constraint interface accepts a typed formula and a requested operation:
feasibility, witness, enumeration of declared finite choices, or bound. It
returns \code{sat}, \code{unsat} or \code{unknown}, plus evidence appropriate
to the operation. Timeouts and unsupported theories return \code{unknown}.
The history layer exposes that solver outcome as \code{SolverIncomplete},
retains the affected region and marks its coverage unresolved. These are
layer-specific descriptions of incomplete computation, not infeasibility.
A witness proves existence within the formula, not completeness of a recovered
historical family.

\section{Human review and model-assisted extraction}

The review interface should put the source passage beside the proposed
observation, context and reconciliation impact. An analyst can accept a
mapping, add an alternative, reject an extraction, define a symbolic unknown
or request more evidence. These actions create structured changes with
reasons. The useful unit of review is a coherent disclosure and its links,
not an isolated number detached from its note.

A language model can identify candidate tables, draft concept mappings,
propose contract terms and suggest alternative readings. Its output must
reference source spans and a schema. Deterministic checks reject fabricated
source references, invalid units, inconsistent periods and unbalanced
postings. A model-generated interpretation that passes those checks remains
a proposal until its evidentiary status is established. Token probabilities
and self-reported confidence are never automatically used as weights over
economic histories.

For routine local research use, a lightweight interface and immutable source
versions are sufficient. Multi-user approval hierarchies, cryptographic
attestations and deployment security systems are outside this initial design.
They can be added for a concrete operational requirement without changing the
scientific representation.

\section{Failure recovery and reproducibility}

Extraction jobs and simulation jobs write explicit progress records and atomic
results. Restarting a failed document conversion reuses its document hash and
creates either the same idempotent extraction result or a new version under
changed settings. Restarting a simulation resumes only from a committed state
whose model and input hashes match the run. Numerical failures retain the
inputs needed for a focused diagnostic.

A run manifest records code revision when available, package lock, source
hashes, cutoff rule, model hash, scenario data, priors or weights, seed/stream
scheme, solver settings, decimal and rounding conventions, calendars,
environment and result locations. Absence of a usable Git revision is recorded
as unavailable with content hashes, rather than inventing a commit.

\section{Review decisions have consequences for later results}

A proposed reading starts in \code{Proposed}. Acceptance records a reviewer,
date, reason, verified locator and context, together with the reconciliation
result. Acceptance means that the stated layer has been reviewed: accepting
an extraction of a company's sentence does not accept its accounting
treatment. Competing defensible readings enter \code{AcceptedAlternative}
under a choice group. Rejection preserves the source and reason.
A correction creates a new reading; replacing an accepted reading requires
an explicit \code{Supersede} action. A prior reading therefore remains
reproducible without entering the latest model.

Suppose OCR reads Northstar's original 120 as 720. The source span supports
120; correcting extraction creates a new reading linked to the erroneous
one. The later revenue correction from 120 to 110 is different: it changes
the company's reported assertion. The original extraction remains faithful
to its document. Finally, a reviewer may accept that two notes conflict
without accepting either as a unique model constraint. The view then contains
a conflict set requiring alternatives or further evidence.

A changed reading or mapping invalidates descendant constraints, families,
measurements, reports and cached runs for a new view. Unaffected dependencies
can be reused. Old frozen runs retain their original decisions and evidence
IDs; they are marked stale for current use, not overwritten. A journal derived
under the old view is never silently attached to a new source. The local
workflow needs no multi-user approval hierarchy to enforce these rules.

\section{Identity must survive harmless reordering}

The portable serialisation in Section~\ref{sec:portable-record} preserves
decoded Unicode code points without global NFC normalisation. It uses sorted
ASCII keys and exact rational financial quantities, while integer metadata
remains integer. Only schema-declared sets are sorted. Source identity hashes
original bytes. The old Core 0 encoding survives only for its historical
fixtures through an explicit legacy import; it does not define new portable
digests. Neither encoding proves arbitrary economic equivalence.

SHA-256 with a domain/version prefix identifies three different closures.
Evidence identity includes source bytes, locations, extraction and review
versions. Model identity includes typed IR, assumptions, rules, calculator
locks and resolution, while excluding formatting and source byte offsets.
Run identity adds the evidence view, horizon, scenarios, outputs, calendars,
numerical policy, random-stream scheme and environment. A corrected
source can change evidence and run identity without changing the numerical
model; a new rate assumption changes the model as well.

Each economic business event has a stable identity within its entity, book
and branch. Its lookup key is the four-tuple in Section~\ref{sec:replay};
event version, payload, expected head and request settings belong to the full
fingerprint. Exact replay returns the original receipt before a new-event
freshness check. Changed inputs under that key conflict. A new run label or
version cannot make the event post again. Independent events
may reorder only when read/write sets are disjoint or a package proves
commutation, including funding constraints. Alphabetical ordering cannot
settle an economic timing ambiguity.

Stochastic keys contain seed, coupling group, entity, contract/cohort,
economic date, shock kind and draw index. Branch enumeration order is absent.
Shared coupling groups may use the same uniform draw with different marginal
transforms. The reference fixture maps the first 64 bits of a SHA-256 key
digest, interpreted as unsigned big-endian integer $v$, to
$(v+1/2)/2^{64}$. This fixes example replay; it does not validate a production
Monte Carlo generator. Research runs select an assessed counter-based
generator and record transforms and numerical environment. Inner measurement
draws have different shock domains from outer realised defaults.

Schema migration preserves old and new payloads and a field/meaning mapping.
A representation-only migration must demonstrate equivalent supported
semantics; a changed recognition rule creates a new model. Restart resumes
only a committed state whose locks and identities match. SQLite owns source,
review and run metadata transactions; content-addressed files hold immutable
bytes and JSON, while DuckDB reads versioned analytical exports. Each mutable
transition has one owner.

\section{Adapters exchange typed records}

The portable interfaces described in this chapter govern new exchanges.
The original \code{spec/core-contract.md} and
\path{spec/core-ir.schema.json} retain the historical Core 0 examples.
A named decoder and comparison link those examples to the portable records;
their older fields do not silently extend a new closed signature. Every method returns a success record or a
diagnostic with code, source IDs, entity/period, dependency path and retry
status. The principal sequence is \code{ingest}, \code{review},
\code{compile}, \code{reconstruct}, \code{simulate}, \code{report}, with
\code{bound}, \code{explain} and \code{replay} over frozen identities.

Arelle supplies candidate facts with QName, entity, context, period,
dimensions, unit, accuracy, nil status and locator. Duplicates survive for
review. Its archived \code{ModelInstanceObject} interface exposes these
properties; validation success does not establish economic truth. Docling
supplies page/table proposals, locations and conversion status. Missing
headers and failed pages remain unresolved. Z3 receives named rational-linear
assertions and finite choices; witnesses are checked against exact inputs and
unknown results retain their reasons. The reference checks exercise Z3;
the other selected adapters remain interface designs grounded in inspected
official source snapshots.

ACTUS receives contract terms, calendars and dated risk factors and returns
schedules, transitions and payoffs. AccDSL applies accounting separately.
QuantLib receives an explicit evaluation date, instrument, curves, fixings,
calendar/day-count and measure; it returns dated measurements with numerical
status. No process-global valuation date may leak between branches.
Beancount exports concrete journals for later differential checks; it does
not own symbolic families. Import failures retain request ID and source hash
so retries are idempotent. Licence/version evidence remains in the software
ledger; integration acceptance requires pinned releases or source digests.

\input{sections/adapter-methods}


## FILE docs/design/proposal/manuscript/sections/operations-storage.tex
\section{Versioned requests and independent results}
\label{sec:versioned-operations}

The workflow names above become portable operations only when their arguments,
input versions and effects are fixed. Each request names an exact operation,
profile and signature; an immutable view; typed arguments; execution settings;
and the expected head for a mutation. The body is closed:
\begin{lstlisting}
OperationRequest {
  operation, request_id, workspace_key,
  profile_ref, signature_ref, view_ref, arguments,
  execution: {mode, budget, environment_ref},
  expected_head: null | {owner_key, state_ref, generation}
}
\end{lstlisting}
All fields are present. The mode distinguishes a specification example from a
runtime request. Budget states operation-count and elapsed-time limits, or a
reason either is inapplicable. The expected head appears only in this envelope.
For accounting its owner is the entity/book/branch; for review it is the review
namespace; for probability selection it is the family/evidence/time owner.
Resolving a mutable ``current'' alias happens before constructing the request,
and a mutation compares the resolved revision again.

The fingerprint covers the complete request, including its request identifier,
expected generation and execution settings. In accounting the lookup namespace
is still the business-event tuple in Section~\ref{sec:replay}, not request ID.
Changing the request ID for a committed event changes the fingerprint and
conflicts. Source and review mutations use their own operation/workspace/request
namespace. A transport correlation identifier and an economic event are not
interchangeable identities.

The result preserves the submission even when decoding fails. Once exact-byte
retention succeeds, it has the following fields:
\begin{lstlisting}
OperationResult {
  submission_ref, request_ref, operation, input_view_ref,
  disposition, statuses, payload, diagnostics, coverage,
  unresolved, continuation_ref, commit_observation,
  receipt_ref, evidence_mode
}
\end{lstlisting}
The validated request reference remains null until all required input checks,
including bindings and authorization, pass. Rejected input has null payload.
If submission retention itself fails, the caller receives a transport failure
with its original correlation, not a fabricated stored submission or a known
commit outcome. A read can inspect an earlier committed receipt while its own
commit observation says no new commit occurred.

Completed, partial, rejected, unsupported, cancelled, internal failure, unknown
commit and replay are operation dispositions. They do not replace the separate
structural, mathematical, computational, empirical, accounting, forecast,
product and human statuses. Computing a zero normalizer can complete while
conditioning on that event is undefined. A valid symbolic family can have only
partly explored regions. A supported insolvency scenario can be fully evaluated
while its company defaults. These distinctions prevent an infrastructure error
from erasing an economically important path.

For example, let an admitted law assign mass $3/5$ to a path with cash 120 and
$2/5$ to an unavailable cash calculation. The output retains both regions and
their masses. If separate evidence bounds the unavailable cash by $[80,110]$,
the unconditional mean is bounded by
\[
  \tfrac35(120)+\tfrac25[80,110]=[104,116].
\]
Without those bounds, even this mean interval is unsupported. Reporting a mean
of 120 would silently condition on computational success.

Portable-only validation proceeds through decoding, field shape, reference
integrity, cross-record binding and time context, capability and admission,
calculation, transaction comparison and publication. Native interfaces preserve
their own explicit stage order; the native accounting sequence checks
recognizable dependencies before shape and source versions before bindings.
At the earliest failed stage, return every independently decidable diagnostic
in canonical field order. A malformed parent prevents its dependent checks,
but does not hide unrelated sibling errors. Later stages are marked unevaluated.

Appendix~\ref{app:portable-interfaces} gives the exact operation names and
argument meanings. Financial method names such as delivery or claim settlement
are versioned members of a package; they are not invented new platform
endpoints. In particular, continuous inference and causal methods need their
own admitted extension signatures before the finite/exogenous initial profile
can execute them.

\section{Correction changes a view without rewriting its history}

A correction can affect a result that never explicitly selected the corrected
source. Suppose a query selected one available report because it was the only
eligible candidate. Admitting a second report may create a conflict. The query
therefore depends on candidate-set membership as well as on its selected
record. Invalidation must follow both dependencies transitively.

Each correction creates an immutable new view with parent and changed decisions.
Old frozen outputs retain their original views. A current query must check
ancestor dependencies even for descendants created after an invalidation scan;
otherwise delayed computation could revive a stale reading. Unrelated closures
remain usable. Self-supersession, incompatible replacement scope and a missing
required predecessor reject before mutation.

The mathematical correction and the audit of affected work are separate records.
A \code{CorrectionBasis} depends on the unaffected base law, replaced reading,
corrected source, target admission and replacement method. An
\code{InvalidationReport} additionally depends on the inspected store snapshot
and lists affected descendants. Computing another optional descendant changes
the report, not the corrected law. This also keeps the content-reference graph
acyclic.

Probability calculation, admission and selection are three effects. A selected
law belongs to the owner consisting of family, target evidence view, target time
and purpose. Correcting a source does not mutate the old owner's selected
pointer or automatically select the new candidate posterior. In the new owner,
an inherited stale selection returns selection superseded with an explicit
readmission and reselection obligation. With no inherited selection it returns
selection required. A historical query naming the old view remains valid in
that frozen scope.

\section{Durability and migration have observable obligations}
\label{sec:durability-migration}

One logical transactional store owns records, dependency edges, review views,
branch heads, journals, economic deltas, receipts and search checkpoints.
Original documents reside in immutable byte storage. Their exact bytes must
be durable and verified before a metadata transaction refers to them. A crash
between blob creation and metadata commit may leave an unreferenced blob; it
must not leave an accepted reference to absent bytes. Analytical tables, caches
and PDFs derive from a named snapshot and do not become separate writable
versions of truth.

The proposed local store serializes commits even when several clients submit
requests. A single writer still needs expected-head comparisons. An event-log
implementation is also possible if its commit marker, projection visibility and
replay obey the same observable rules. Neither a document trace nor a choice
of SQLite establishes physical-media durability or multiwriter throughput.
Those require crash, reopen and fault-injection evidence in the selected
environment.

A search checkpoint commits the semantic manifest, partition identity, explored
and unresolved regions, frontier, used budget and result references together.
A cell is not complete before its result and frontier transition are durable.
Resume names that exact checkpoint and manifest. Increasing a scheduling budget
can continue it; changing evidence, methods, scenario, family or traversal meaning
requires a new manifest and an explicit reuse relation. Cancellation preserves
the last committed frontier.

Export first stages a closed manifest, verifies every required record and blob,
then publishes the manifest atomically. An incomplete export remains explicitly
incomplete. Import verifies required bytes before committing metadata and grants
no new financial admission. A failed report export cannot undo a journal or
justify posting it again.

A representation-only migration retains old and new bytes and IDs plus a
field/meaning mapping. Its input names the old and new schemas, migration
method, source snapshot and declared semantic relation; the common request
envelope supplies the expected head for its transaction. It must preserve typed quantities, context, uncertainty
category, reference closure, admission, event identity and supported reference
query results. Changing a rounding policy, calendar, recognition rule or
probability law is a new model, not a format migration. A failed comparison
leaves old heads and objects usable.

Exact reruns compare values on the same evaluated domain. An elapsed-time cap
can visit different search cells on different machines, so equal partial
coverage cannot be presumed. Reproducible prefix comparisons need a pinned
traversal and operation-count budget; resume uses the saved frontier. Approximate
methods use their declared financial error comparison, and random streams name
economic owner, date, shock kind and draw index independently of branch order.


## FILE docs/design/proposal/manuscript/sections/authorization.tex
\section{From an economic event to permission to post}
\label{sec:posting-permission}

A delivery can change revenue, inventory and receivables at once. Before any
book changes, the method needs to know which contract was performed, which
opening state it consumes, which evidence supports that reading and which
accounting profile applies. Balance alone cannot supply those facts. AccDSL
therefore separates the economic basis, permission to use a treatment, proposed
entries and the transaction that makes them durable.

The event basis binds an immutable event to opening state, context, branch,
time view, chart, authority, method, evidence, admissions, assumptions and view.
Its business identity is the four-tuple of entity, book, branch and business
event. The branch declares whether it is synthetic or real. A synthetic teaching
profile can justify a teaching posting; it cannot authorize a real book merely
because the resulting arithmetic is identical.

The method first evaluates reporting framework, jurisdiction and dates; then
entity and transaction scope; contract and recognition facts; elections;
numerical capability; and account/context bindings. Every material finding
survives. A false required fact is ineligible, an unknown required fact is
unresolved, and an event outside the method is outside scope. A known false
finding must not disappear behind a later unknown one. Missing operative
authority never becomes source-supported permission.

The native operation \code{accounting.assess@1} remains read-only assessment.
Its \code{assess\_only} request and false posting permission cannot be promoted
by editing a flag. The separate \code{accounting.authorize@1} operation produces
a \code{PostingAuthorization} from the complete basis and a supported posting
profile. It permits posting only when the treatment is eligible, the method is
fully specified for the event and the branch mode matches the profile's
evidence scope. An unresolved or unsupported assessment is still a useful
completed assessment, but it contains no permission to post.

An authorized proposal contains both a journal and an independent economic
delta, each bound to the same basis and authorization. Journal lines name
account role, debit or credit, positive exact quantity, currency/context,
entity, book, event and method. Zero lines are omitted; a negative effect reverses
sides. The journal balances within each currency and book. The delta separately
checks quantities and contractual memory: inventory movements consume available
lots, cash follows settlement, share counts follow ownership events and debt
face amount remains distinct from carrying value.

The commit arguments have exactly four references:
\begin{lstlisting}
AccountingCommitArguments/v1 {
  basis_ref, authorization_ref, journal_ref, delta_ref
}
\end{lstlisting}
The expected opening state and branch generation appear once, in the outer
operation request. A reference to a native assessment in the authorization
field fails its reference type. False posting permission fails authorization.
An unknown posting schema returns unsupported operation with no journal commit.
All bindings are checked before looking up a prior receipt.

\begin{figure}[htbp]
\centering
\begin{tikzpicture}[node distance=5mm,>=Stealth,
 box/.style={draw,rounded corners,align=center,text width=29mm,minimum height=13mm,font=\small}]
\node[box] (basis) {Economic event\\and opening state};
\node[box,right=of basis] (auth) {Eligible method\\and permission};
\node[box,right=of auth] (proposal) {Journal and\\economic delta};
\node[box,right=of proposal] (commit) {Atomic state\\and receipt};
\draw[->] (basis)--(auth);
\draw[->] (auth)--(proposal);
\draw[->] (proposal)--(commit);
\end{tikzpicture}
\caption{Each step answers a different question. Accounting assessment may
inform the permission decision, but only the final transaction changes the book.}
\end{figure}

For a delivery, the basis identifies the exact performance obligation,
quantity, allocation and control finding. The opening state contains cumulative
revenue, billing, collection and inventory. The selected method derives the
recognition and lot movements; the report later consumes that same committed
path. Combining a journal from one method version with a delta or opening state
from another is invalid even if the totals happen to balance.

\section{A lost acknowledgement must not create a second sale}
\label{sec:replay}

Suppose a sale commits but the response is lost. The client knows the request,
but cannot tell whether the server committed it. Retrying under a new event ID
could duplicate revenue. Retrying the original request must instead return the
original immutable receipt.

The lookup key is
\[
  (\text{entity},\ \text{book},\ \text{branch},\ \text{business event}).
\]
Payload, event version, opening state and request settings belong to the complete
fingerprint, not this key. A renamed run or bumped event version cannot evade a
conflict. A separately commissioned hypothetical projection uses a new branch
namespace; reopening the same projection uses its existing one.

A correction of an already committed event is a new business event linked to
its predecessor and an admitted correction method, such as reversal and
replacement or a dated adjustment. It preserves the original receipt.
The accounting treatment must apply to the actual correction; absent treatment
authority leaves it unresolved rather than licensing a generic reversal.

Commit first validates input shape, closure, bindings and authorization in the
requested historical view. It then looks up the stable event key. An equal
fingerprint returns the old receipt with no additional commit; a different
fingerprint returns an event-identity conflict. Only an absent key proceeds to
the expected-state and generation comparison. This order is essential: after
a successful sale the current head has changed, so checking freshness before
replay would reject the very retry needed to resolve the lost response.

A new candidate is assessed and constructed without mutation. One transaction
then rechecks key absence and the expected head, inserts journal, delta, closing
state, dependencies and receipt, and advances the head. It commits all or none.
If another client has committed the identical event, return that receipt. A
different event that advanced the head makes this request stale. A changed
payload under the same key conflicts. Diagnostic or scratch records never count
as economic transitions.

A timeout consequently has three possible observations: committed, not committed
or unknown. Unknown retains the original key, fingerprint and expected head for
receipt lookup or exact retry. Refreshing the head changes the request and cannot
be presented as the same retry. Missing committed dependencies are an integrity
failure, not permission to reconstruct an approximately similar receipt.


## FILE docs/design/proposal/manuscript/chapters/07-execution.tex
\chapter{Reconstruction and execution procedures}
\label{ch:execution}

\section{Ingest, reconcile and construct histories}

The historical procedure starts with a filing manifest. It records documents,
reporting dates, publication dates, revisions and expected statements and
notes. Tagged filings are parsed through an XBRL adapter; PDF and HTML sources
are segmented into text, tables, captions and references. The original bytes
and extraction output remain immutable. Re-running an improved extractor
creates a new extraction version with links to the same source.

For each table, the importer first resolves headers, units, signs, periods and
dimensions. It then proposes concept mappings. A deterministic validator checks
subtotal arithmetic, duplicate facts, comparative consistency and cross-note
references. Every proposed repair creates a new reading. The system may suggest
that an OCR value is 10 rather than 70, but only a reviewed correction or an
explicit alternative allows that reading into a validated model.

Reconciliation proceeds from local totals to movement schedules. A debt bridge
may contain opening debt, issuance, repayment, acquired debt, interest
accretion, currency effects, fair-value changes and closing debt. Every
component receives a movement type. An unexplained residual is stored as a
residual with a source and period; it is not automatically classified as
repayment or issuance. A model can introduce an unknown decomposition of that
residual, subject to evidence and economic constraints.

The reconstruction engine then performs the following finite procedure within
a declared model scope:
\begin{enumerate}
\item Build shared variables for observations, opening states, contract terms
and supported movement amounts. Attach original rounding domains.
\item Add identities, roll-forwards, account restrictions, contractual
relationships and cross-period links. Add each semantic reading as a condition
on the same joint model.
\item Propagate types, units, intervals and simple equalities. Reject context
mismatches before invoking a numerical solver.
\item Ask the solver for feasibility. On infeasibility, return a sufficient
conflicting subset of constraints, its source spans and model assumptions.
A solver's conflict core need not be the smallest possible explanation.
\item Retain finite alternatives and continuous solution families symbolically.
Materialise example histories only when needed for review or execution.
\item Check whether each requested simulation has sufficient economic state.
Missing maturities, reset dates or cohort composition become declared
assumptions or explicit unresolved inputs.
\end{enumerate}

Unrestricted journal enumeration would be unbounded: arbitrary offsetting
transactions can be inserted without changing reports. The model therefore
declares allowed event types, time resolution, relevant accounts, lot/cohort
resolution and limits on latent contract instances. These limits describe the
represented family; they are not evidence that all real possibilities were
searched. The compiler canonicalises syntactic duplicates and equivalences
established by its supported rewrite rules. It does not decide arbitrary
economic equivalence. Probability measures attach to declared economic
hypotheses or parameters, never to a count of encodings; adding a duplicate
representation therefore cannot create extra probability mass or coverage.

The first implementation uses symbolic linear bridges and finite structural
choices. Nonlinear economic models can be evaluated on feasible states through
plugins. A solver timeout preserves the unresolved family and returns
\code{SolverIncomplete}; it does not prune the family as impossible. Search
budgets belong to run configuration and are recorded with the results.

\section{Condition a run without rewriting history}

A run selects an evidence view and cutoff, a historical family, a forecast
starting date, scenario definitions, accounting packages, management policies,
output queries and numerical settings. A run may use a concrete history,
an exact symbolic family, a finite set of conditional histories, or weighted
draws from a declared distribution. The output records which mode was used.

Suppose no debt maturity is disclosed. An analyst may run a conditional case
that assumes all debt matures after the forecast horizon. The run is valid
under that assumption even though the historical representation remains
incomplete. The interface must display the assumption next to the result and
provide sensitivity cases when the assumption is material. It must not label
the assumed maturity as a discovered historical fact.

Management behaviour normally uses only information available at the decision
date. A perfect-foresight stress case is a separate, explicitly labelled
policy. Scenarios should share the same underlying innovations when estimating
paired differences where appropriate, with stable stream identifiers so
branch order does not change the draws. Common random numbers improve the
comparability of paired simulations; they do not imply that every branch has
the same economic event counts or shock distribution.

\section{Schedule and commit events}

Each event carries an economic occurrence time, accrual interval when relevant,
settlement time, entity, contract or cohort identifier, currency, inputs and
provenance. Its ordering key consists of date, declared phase, dependency edges
and a deterministic tie identifier. The reference phases are: opening and
scheduled contractual changes; market observations and rate resets; business
events and decisions; accrual and measurement; settlement; period closing and
reporting. A contract can require a more specific dependency. These phases are
an engineering starting point, not a universal description of market timing.

Two events may share a tie order only if their order is either specified or
irrelevant to the result. If payment before remeasurement and payment after
remeasurement differ, an unresolved ordering is a model ambiguity or an error.
The engine does not conceal it behind alphabetical event IDs.

\begin{lstlisting}
execute_event(operation_request):
    validate exact input closure, bindings and historical admission
    validate separate posting authorization, journal and delta
    lookup stable entity/book/branch/business-event key
    if exact committed fingerprint: return original receipt
    if different committed fingerprint: return event conflict
    compare expected opening state and head generation
    atomically recheck key/head and commit journal, delta, state, receipt
    return receipt, emitted dependent events and diagnostics
\end{lstlisting}

The atomic unit includes the economic state and its accounting effects.
If posting fails, neither state changes. A repeated event ID with identical
inputs returns the existing result; the same ID with different inputs is a
conflict. Here the inputs include the request identifier, expected head and
execution settings, not only the financial payload. Section~\ref{sec:replay}
defines the stable key and full fingerprint. Consolidation runs after entity books reach the required date and
stores its adjustments separately. A failure in one scenario branch cannot
mutate another branch's state.

\input{sections/authorization}
\section{Funding, tax and other simultaneous relations}

Some financial models have circular dependencies. Interest affects taxable
profit; tax and investment affect funding needs; funding affects interest.
The reference executor first tries to resolve these through explicit timing.
For example, beginning-of-period debt can determine current interest, with
new borrowing affecting the next accrual period. That is acceptable only when
the model's timing assumption is stated and appropriate.

Where the economic model genuinely requires simultaneous decisions, the
dependency graph identifies the strongly connected component and delegates it
to a declared equation or optimisation solver. The solver must return a
solution, residuals, admissibility checks and uniqueness or multiplicity
status. A contraction iteration requires a justified convergence condition;
an arbitrary fixed iteration count is not a mathematical solution. Multiple
admissible equilibria become alternatives when material. No solution produces
a model outcome such as financing failure, or an explicit numerical failure,
depending on the cause.

Funding policy must include available facilities, limits, covenants, collateral
and allowed capital actions. The program cannot issue unlimited debt to keep
cash positive. An inability to meet payments may be a legitimate default
outcome. Default ends or changes contractual and accounting processes under
the relevant event rules; it is not quietly discarded as a bad simulation draw.

\section{Worked example: identical history, different future journals}

Return to the company in Chapter~\ref{ch:purpose}. Immediately after the
historical interest payment and closing, cash is 95, debt is 100 and equity
is $-5$. There are no other assets, liabilities or transactions. Next year's
expense is 5 in the all-fixed branch and 7 in the all-floating branch under
the rate shock. The generated entries and closing statements are:

\begin{center}
\begin{tabular}{lrr}
\toprule Output & All fixed & All floating\\\midrule
Debit interest expense / credit cash &5&7\\
Closing cash &90&88\\
Closing debt &100&100\\
Current-year profit & $-5$ & $-7$\\
Closing equity after profit transfer &$-10$&$-12$\\
Cash change &$-5$&$-7$\\\bottomrule
\end{tabular}
\end{center}
The balance-sheet identity holds in each branch: $90=100-10$ and
$88=100-12$. The demonstration reporting profile classifies interest paid as
operating cash flow. A different permitted reporting profile changes that
classification, while preserving the cash movement and source event. This
example proves the intended distinction and its arithmetic; it does not
estimate the probability that either debt structure describes a real company.

\section{Worked example: a bond has several relevant amounts}

A two-period zero-coupon bond raises cash of 100 and promises 110.25 at maturity.
Assume a 5\% effective rate per period, no transaction costs, no default, and
amortised-cost treatment under a demonstration rule. The effective-interest
schedule follows directly from $100(1.05)^2=110.25$:
\begin{center}
\begin{tabular}{lrrr}
\toprule Date & Opening liability & Interest accretion & Closing liability\\\midrule
Issue &0&0&100\\
End of period 1 &100&5&105\\
End of period 2, before payment &105&5.25&110.25\\
Redemption &110.25&0&0\\\bottomrule
\end{tabular}
\end{center}
Issuance debits cash and credits the liability by 100. Each accretion debits
interest expense and credits the liability. Redemption debits the liability
and credits cash by 110.25. Legal face amount, carrying amount and market
fair value remain separate fields. A market-rate shock may change fair value
without changing this contractual payment schedule or this demonstration
amortised-cost path.

Cash-flow reporting uses the actual payment event and its economic components;
the annual accretion is non-cash. The applicable reporting package decides how
to classify the maturity payment, rather than inferring it solely from the
liability debit. Fees, modifications, early redemption, embedded options,
hedges and foreign currency require additional event and measurement rules.

Ordinary equity issuance similarly separates cash, share quantity and legal
capital. Ten new shares at 12, with par value 1, produce cash of 120, share
capital of 10 and premium of 110 under a simple par-value profile. Shares
outstanding increase by ten units. Direct issuance costs of 3 reduce the
specified equity account and cash under the chosen illustrative treatment.
The accounting rule and the cost's eligibility must be explicit; this example
does not prescribe every jurisdiction's treatment.

\section{Reporting and explanations}

The reporting engine produces the balance sheet, income statement, comprehensive
income, cash-flow statement, changes in equity and note schedules when the
necessary modules are present. Each output carries its basis, perimeter,
period, scenario and interpretation. A comparative table cannot combine an
original prior-year figure and a restated current-year comparative without
displaying that choice.

An explanation is a dependency graph with typed edges: extracted from,
interpreted as, assumed by, constrained by, generated by, measured by,
posted by, aggregated into and supersedes. A cash-flow line must lead back
to payment events; a fair-value movement must lead back to valuation inputs;
a consolidated amount must show eliminations. A provenance path establishes
how a result was obtained. It does not by itself establish that the underlying
economic model is correct.

\section{The corporate reference package as operations}

The Northstar example defines a closed, reproducible corporate package rather
than a universal standard. Its events separate performance, invoicing and
settlement even where the example makes the first two simultaneous. Every
payload includes entity/book, currency, economic date, period, source or
assumption IDs and an information-view ID. Amounts are exact before the
declared posting quantisation. Quantities and money are checked separately.

\begin{longtable}{L{27mm}L{60mm}L{49mm}}
\toprule Event & Preconditions and state change & Posting\\\midrule\endhead
Deliver/invoice & Goods owned and available; control transferred; quantity
removed at selected cost; unconditional amount due added & Debit receivable,
credit revenue; debit cost of sales, credit inventory\\
Collect & Receipt no greater than selected unpaid receivable; reduce that
balance; excess must be separately classified & Debit cash, credit receivable\\
Receive goods & Accepted owned quantity at supported unit cost; create supplier
obligation and inventory lot & Debit inventory, credit payable\\
Pay supplier & Identified obligation and sufficient available cash; reduce
both & Debit payable, credit cash\\
Payroll & Service period and cash obligation evidenced or assumed & Debit
payroll expense, credit cash; accrual variant uses a payable\\
Acquire plant & Control obtained, cost known, in-service date/life/residual
recorded; add asset cohort & Debit plant cost, credit cash or payable\\
Depreciate & In-service asset with remaining depreciable amount; apply dated
schedule, capped by that amount & Debit depreciation, credit accumulated
depreciation\\
Interest & Contract, reset state and accrual fraction known; create interest
obligation, then settle if cash available & Debit interest, credit interest
payable; debit payable, credit cash\\
Current tax & Reference tax base positive; 20\% teaching rule; apply prepaid
tax before further payment & Debit tax expense; credit prepaid tax or payable;
settlement separately affects cash\\
Dividend & Explicit authorised distribution, sufficient funds and permitted
capital action & Debit retained earnings, credit dividend payable; then settle\\
Close & Required period operations completed; preserve original movements &
Transfer temporary income/expense balances to retained earnings\\\bottomrule
\end{longtable}

The current example combines accrual and settlement when they share a date,
but the separate obligation remains the general operation. Customer advances
are debit cash/credit contract liability and become revenue only on the
supported performance event. Inventory costing requires an admissible policy;
negative inventory and collection beyond an identified claim are rejected.
Non-cash acquisitions, write-offs, impairment and currency movements require
their own classified templates. An unknown residual never enters one of these
operations merely to force a reconciliation.

Reporting maps asset and contra-asset balances into the balance sheet and
liability/equity balances with their opposite sign. Before closing, current
profit is included once in equity; after closing it is already in retained
earnings. Income uses period movements in income/expense accounts, and OCI
uses its own designated accounts. Cash flow sums cash legs by economic
operation: Northstar's collections, suppliers, payroll, interest and taxes
are operating, plant payments investing, and debt/equity proceeds or repayments
and dividends financing. Non-cash depreciation is excluded from direct cash
flow and added back only in the indirect reconciliation. Note schedules use
the same contracts, lots and classified movements as the statements.

\section{Scenario meaning and information access}

An \code{ExogenousStress} supplies a path or joint driver law while holding the
historical evidence model fixed. \code{ObservationalConditioning} additionally
supplies actual observations and a joint probability model; the finite method
in Chapter~\ref{ch:math} evaluates the conditional distribution when its
normalising mass is positive. \code{StructuralIntervention} requires a named
structural model and replaces designated equations, retaining its exogenous
noise. An absent structural model gives \code{UnsupportedScenario}, not an
intervention inferred from an accounting identity \citep[Section 3.2.1]{pearl2009}.
The textual Core 0 \code{scenario} declaration is an exogenous stress only;
the other modes require the explicit typed API records.

At each decision date the runtime constructs an information view containing
eligible disclosures, committed state through that date, currently observed
drivers and the declared forecasting model. Future realised innovations and
future outcomes are inaccessible. A stress path may be announced in advance,
but this is an explicit visibility policy. Otherwise management sees only its
current and past values. A bank's allowance at the opening date may use a
forecast distribution of defaults; it must not inspect the outer simulation's
future realised default. Inner valuation randomness has a separate stream
domain from outer realised outcomes.

Funding follows a declared waterfall: available cash, committed eligible
facilities up to their limits, and separately authorised capital actions.
Each action checks collateral, covenants and settlement timing. If an amount
remains due, record an economic funding failure and the unpaid obligation.
If required valuation or accounting is unsupported, stop the affected
dependencies as incomplete. The branch manifest preserves the last committed
state, completed outputs, unavailable outputs and reason. These distinctions
let an analyst see a meaningful bad outcome without confusing it with broken
computation.


## FILE docs/design/proposal/manuscript/chapters/10-validation.tex
\chapter{Acceptance and implementation sequence}
\label{ch:validation}

The reference cases now make several of the acceptance obligations executable
as design checks. Northstar provides full statements and a known compatible
history; Apple supplies real source contexts and a bounded marginal stress;
bank, insurance, consolidation and inventory fixtures test the core's broader
state requirements. They do not constitute a production implementation.

\section{Three different questions require different evidence}

Engineering correctness asks whether the implementation follows the specified
types, transitions and arithmetic. Accounting validity asks whether the
selected rules faithfully implement the applicable standards and disclosed
policies. Scientific validity asks whether the economic assumptions and
uncertainty representation support the intended forecasts or comparisons.
A balanced journal answers only part of the first question.

The implementation must therefore maintain separate validation results.
Compilation and deterministic examples cannot establish forecasting quality.
Agreement with a public report cannot identify an undisclosed contract term.
A lower extraction error on a document benchmark cannot establish that the
engine preserved every materially different scenario response.

\section{Core conformance cases}

\begin{longtable}{L{16mm}L{73mm}L{47mm}}
\toprule Test & Required case & Pass condition\\\midrule\endhead
T01 & Exact debit/credit batches, including reversals and period closing &
Every committed book conserves signed balances; imbalance rejected atomically.\\
T02 & Money, quantities, currencies, instants and interval flows &
Invalid additions and context combinations rejected; explicit conversions traced.\\
T03 & Original filing, later correction and as-known cutoff &
Earlier query reproduces the original evidence view; later view shows revision.\\
T04 & Annual and interim cumulative flows with revised comparatives &
Quarter derivation only across compatible contexts and vintages.\\
T05 & Fixed/floating borrowing with identical historical postings &
Both explanations survive; next-year expense is 5 and 7 under the stated shock.\\
T06 & Continuous fixed share $\alpha\in[0,1]$ &
Exact model returns $I=7-2\alpha$ and extrema 5, 7 without assigning probabilities.\\
T07 & Duplicated encoding of one history &
Canonical duplicates preserve results and declared weights; no extra
probability mass from an additional encoding.\\
T08 & Linked interpretation across debt classification and payment treatment &
Impossible combinations rejected through shared constraints.\\
T09 & Rounded totals, duplicate facts and contradictory notes &
Correct interval compatibility; no automatic zero or balancing plug.\\
T10 & Infeasible or unsupported constraint problem &
Conflicting sources exposed; timeout/unsupported case reported as unknown.\\
T11 & Zero-coupon bond and ordinary equity examples &
Carrying amounts, payments, share quantities and report mappings match derivations.\\
T12 & Foreign-currency asset, translation and cash movement &
No mixed-unit balance test; translation effects separated from cash flows.\\
T13 & Acquisition and intragroup balance elimination &
Perimeter and adjustment book reproduce group totals without inventing capex.\\
T14 & Conflicting recognition rules and unknown guards &
Explicit conflict or symbolic partition; file order has no effect.\\
T15 & Insufficient cash with constrained funding &
Funding failure/default retained as an outcome; no hidden borrowing.\\
T16 & Expected-loss measurement before future default is realised &
Measurement uses only information allowed at that date.\\
T17 & Repeated/reordered independent events and interrupted execution &
Idempotent replay; branch isolation; identical committed outputs.\\
T18 & Conditional distributions and optional weighted mixture &
Branch distributions retained; mixture agrees with declared weights and total
probability; unweighted family never labelled probabilistic.\\
\bottomrule
\end{longtable}

For synthetic cases, expected histories, excluded histories and scenario
consequences are known by construction. Tests should include counterexamples
that balance but have the wrong economic effect, such as treating a
non-cash acquisition movement as operating cash. Such tests discriminate
between arithmetic validity and the intended semantics.

Differential tests against an existing ledger check only the shared supported
subset. ACTUS schedule comparisons check contractual events, and QuantLib
comparisons check selected valuation calculations under matched conventions.
Disagreements must be classified as different conventions, unsupported cases
or implementation errors before one tool is treated as an oracle.

\section{Extraction and reconstruction evaluation}

A company corpus must include different standards, industries, languages,
filing formats, extensions, interim calendars and restatements. Company and
time splits are required so repeated report templates or revised versions do
not leak into evaluation. Public benchmark tables are useful development
material, while acceptance uses complete disclosure packages that include
notes and their relationships.

Reviewers annotate source facts, contexts, mappings, required relationships,
known ambiguities and unsupported assertions. Relevant measures include
correct source-linked values and contexts, unresolved extraction volume,
coverage of note obligations, reconciliation failures and invented facts.
Report each separately. A single overall score can hide a serious error in a
small but consequential financing note.

Historical reconstruction should test whether the known synthetic history
remains feasible, whether known incompatible histories are rejected, and
whether economically distinct alternatives are preserved. On real companies,
public data generally cannot establish the true journal. Review instead
assesses evidential compatibility, unsupported commitments and conditional
economic consequences. Later disclosures may provide discriminating evidence
for previously ambiguous terms.

No universal numerical threshold for semantic coverage or extraction accuracy
is fixed in this document. Before a release evaluation, an accounting-reviewed
test corpus and task-specific acceptance thresholds must be recorded in an
evidence contract. Hard conformance failures, fabricated citations, silent
discarding of valid alternatives and undocumented accounting adjustments veto
acceptance regardless of an aggregate score.

\section{Evaluate the DSL against the strongest practical baseline}

The comparison uses the same IR, accounting examples and tasks. One group of
models is authored through the typed Python API; another through the DSL.
Both receive equivalent documentation and examples. Tasks include encoding a
movement schedule, adding an alternative interpretation, changing an effective
date and tracing a simulated amount. Measure correctness, material omissions,
time to a reviewed result, ease of explaining a change and maintenance effort.

This comparison tests whether the notation and compiler help users; it is not
a comparison between careful DSL code and unstructured spreadsheets. If the
DSL offers little advantage, retain the shared IR and library and narrow the
textual language. Small pilots nominate improvements. A claim of superiority
requires a predeclared comparison and uncertainty evidence, not a few favourable
demonstrations.

\section{Forecasting evaluation comes later}

The proposed experiment asks whether a conditional company method adds
out-of-time predictive information while preserving statement coherence and
unresolved exposure. The comparator ladder uses the same available sources and
targets: last-observation and seasonal naive forecasts; contractual runoff and
accounting-identity forecasts; tuned classical statistical and conventional
financial models; the structural model with one selected interpretation;
the same structural model preserving alternatives; and declared extensions.
This separates changes in economics from changes in the representation of
ambiguity. Tuning stays within training
windows. Test issuers or time blocks remain untouched, and unavailable
predictions stay in the reported denominator.

For probabilities, predeclare proper scores, calibration, interval coverage,
sharpness and dependence-sensitive joint checks. Unweighted feasible sets have
coverage and width under a stated set interpretation, not probability intervals.
Promotion needs a declared score difference with uncertainty evidence on matched
eligible targets and no accounting or information-time veto. Issuer and time
dependence require a justified paired resampling or equivalent inference design;
overlapping reports are not independent replications. Runtime, a few losses and
small-seed tail differences remain descriptive without that support. No such
forecast experiment has been run for this proposal.

Look-ahead, broken conservation, a changed target or missing scope can invalidate
an experiment. A valid comparison in which the proposed predictor performs
poorly instead rejects that candidate and motivates its stated repair. The two
outcomes must not be conflated when choosing the next experiment.

Forecast evaluation uses historical information cutoffs, fixed data vintages,
declared economic scenarios and proper separation of training and testing
periods. Every level of the comparator ladder above uses that same information
boundary, so extra information cannot silently account for an apparent benefit.

Construct the inexpensive comparators before choosing a complex forecasting
method. A no-growth operating forecast with scheduled contractual financing
tests whether the model adds value beyond existing obligations. A constant
margin and turnover model tests whether detailed operations improve on familiar
financial ratios. A trailing-average growth model tests whether fitted dynamics
improve on recent experience. A fixed-exposure contractual stress model tests
whether estimated management responses help beyond repricing the existing
book. Each comparator must generate coherent accounts through the same reporting
rules and use the same historical information. In synthetic cases, the known
hidden state also supplies an oracle conditional on the stipulated scenario.

Evaluate these comparisons separately under stable conditions, large rate
resets, refinancing pressure, credit deterioration and changes in reporting
perimeter. A pooled average can conceal failure in the situation the product
is intended to explain. Supported underperformance against a cheap comparator
in a declared critical situation vetoes promotion of the complex forecasting
method and must lead the result discussion. These checks are falsification
tests, not training targets or evidence of superiority when merely passed.

Evaluate point forecasts where they are a stated target, distributional
calibration when probabilities are justified, and decision-relevant robustness
when only feasible sets are available. A wide feasible set is not automatically
a good prediction, and an unweighted set cannot be assessed as if it were a
95\% predictive interval. In multi-scenario stress tests, scenario severity and
probability remain separate inputs.

Any serious numerical comparison must follow the repository's research plan,
assumption audit, baseline, veto, uncertainty and result-record policies. The
present document runs only deterministic checks of its own examples. It
neither selects a scientific forecasting default nor reports comparative
performance.

\section{Capability contracts for sector packages}

\begin{longtable}{L{26mm}L{55mm}L{55mm}}
\toprule Package & Required state and operations & Minimum acceptance evidence\\\midrule\endhead
Core corporate & Working-capital bridges, lots/assets, ordinary debt and equity,
period closing and cash-flow mappings & Exact synthetic cases, reviewed public
filing reconstruction, all statement reconciliations.\\
Financial instruments & Terms, calendars, resets, options, measurement
categories, modifications and hedges & Contract schedule comparisons, valuation
checks, paragraph-based posting cases and transition cases.\\
Banking & Credit cohorts, deposits, collateral, liquidity, regulatory capital,
management actions & Allowance roll-forwards, repricing and runoff stresses,
capital reconciliation and default/funding-failure cases.\\
Insurance & Policy groups, future cash flows, service and finance components,
reinsurance and asset interaction & Cohort movement reconciliation, assumption
change cases, service recognition and reviewed actuarial calculations.\\
Multi-basis reporting & Versioned IFRS/US GAAP/ASBE rules, entity elections and
transition treatment & Matched economic-event cases with explained basis
differences and independent accounting review.\\\bottomrule
\end{longtable}

Every package declares capabilities at operation level. ``Supports bonds'' is
too vague; ``supports fixed-rate, single-currency, non-callable amortised-cost
issuance and redemption under this reviewed rule set'' is implementable and
testable. Unimplemented operations retain their source and contract
representation while producing an explicit capability error when execution
requires them.

\section{Implementation milestones and dependency order}

\begin{longtable}{L{16mm}L{76mm}L{44mm}}
\toprule Stage & Concrete implementation deliverable & Exit evidence\\\midrule\endhead
P0 & Portable records and contextual types; source/review/time selection;
typed constructors and versioned IR; separate posting authorization and atomic
journal/delta/state/receipt transactions for the running cases
& T01--T04, T09 and T17; source inspection and exact receipt replay.\\
P1 & Admitted history templates, finite choices, shared symbols, linear solver
adapter and historical bridges; conditional simulation and report explanations
& T05--T10, T14 and T18;
synthetic family preserved.\\
P2 & Matched debt text frontend with identical portable IR; connected corporate
methods through the typed authoring API;
document/XBRL import adapters & Parser/API equivalence; T11--T13; reviewed
three-date public-company case.\\
P3 & Contract and valuation adapters, dated standard packages, richer financing
and tax/funding policies & Contract/valuation differential cases; accounting
review; T15 and transition cases.\\
P4 & Bank package, allowance models, regulatory reconciliation and management
response alternatives & T16; banking-specific reviewed histories and stresses.\\
P5 & Insurance cohort package, reinsurance and actuarial measurement adapters &
Reviewed cohort roll-forwards, information-date and service/finance tests.\\
P6 & Optional probabilistic inference, model-weight sensitivity and broader
scenario research & Explicit targets, sampler/numerical validity, prior
sensitivity and downstream evaluation.\\\bottomrule
\end{longtable}

These stages specify dependency order, not dates or staffing estimates.
Banking and insurance representation requirements influence P0 types, although
their measurement engines arrive later. Probability weighting is optional;
P1 already produces useful conditional cases and bounds. A failure of a chosen
extractor or inference algorithm triggers a local replacement or repair,
rather than abandoning the product's representation requirements.
The parser/API comparison in P2 covers the matched debt fragment. Complete
textual authoring of the corporate profile is a further frontend task;
its absence does not remove corporate declarations from the typed API.

\section{Decisions and replaceable assumptions}

The requirements fixed by this design are preservation of evidence and
alternatives, explicit time and basis, balanced and admissible posting, economic
state beyond journals, and distinct set/probability semantics. Replaceable
choices include the storage engines, parser generator, solver, numerical
libraries, aggregation resolution and user interface. Every scientifically
material aggregation, behavioural parameter, prior or truncation rule must
record provenance, purpose, failure mode and a diagnostic before it becomes a
default.

The immediate work is to finish and review the governing proposal, including
its real-source, authority, domain and research obligations. Product
implementation follows completion of that work and explicit implementation
authorization. In the table above, P0 establishes portable records, review/time
selection, durable receipts and typed authoring; P1 builds admitted histories;
P2 connects the corporate methods and matched textual frontend. These stages
are a design sequence, not an already running product campaign.

\section{Concrete conformance and corpus protocol}

The fixture directory contains independently entered inputs and expected
outputs for Northstar, rounded borrowing, evidence views and sector cases.
\code{check\_repair\_conformance.py} recomputes exact journals and statements,
constructs the joint linear bridges in Z3, checks strict bounds, and exercises
replay, atomic rejection, finite Bayes updating and funding failure.
\code{check\_core\_contract.py} checks grammar/schema examples, canonical
identities, stable streams, information restrictions and source inventory.
These scripts are reference oracles for portions of the design. They do not
test an unimplemented full DSL compiler, all adapters or standards compliance.

Every conformance case must specify input files, the operation requested,
expected values or typed errors, comparison convention and supported scope.
Exact money, finite probabilities, linear witnesses and example journals
compare as rationals. Approximate valuations require an error bound or a
justified tolerance tied to the valuation scale. A missing expected result
cannot become a passing test simply because the operation returned something.
An implementation release must pass all applicable positive and negative
fixtures and preserve unresolved operations; the arithmetic oracle alone
does not release it.

The retained panel contains all 192 target annual/interim reports for
2018--2025 across nine issuers and three evidenced accounting families, with
eight consecutive complete years per issuer. Apple, Caterpillar and JPMorgan
Chase each contribute one annual and three quarterly reports per year; the
other six issuers each contribute one annual and one half-year report. Thus
$3\times8\times4+6\times8\times2=192$. This is source acquisition, not
semantic closure or a representative random sample. The 244 retained original
versions include historical alternatives to the active panel. Apple remains
a detailed development package, with Caterpillar supplying a contrasting
inventory policy; bank, insurer, IFRS and ASBE reports are also retained.

Publication dates remain unverified for 136 of the 192 accepted reports; 56 have
filing-date metadata. A historical forecasting population needs the actual
byte-availability evidence described in Section~\ref{sec:time-admission},
not imputed publication dates. The 31 provisional annotations across four
reports are exposed development material, not heldout answers. Policies, note
links, incorporated documents, changed comparatives and adjudicated meanings
still require task-specific preparation. Synthetic revisions provide controlled
cases without substituting for a required real conflict. The corpus protocol
and active panel preserve their distinct populations and versions.

Annotators first record literal/context readings without seeing the model's
predictions, then mark source conflicts, mapping relationships, narrative
qualifications and admissible alternatives. A second accounting-aware reviewer
adjudicates material disagreements while preserving both initial annotations.
Reports from the same issuer family and duplicated tables cannot be split
between development and heldout evaluation. Forecast tests freeze the actual
publication cutoff; later revisions are separately labelled outcomes and may
not enter predictor inputs. Extractor upgrades rerun the same frozen corpus.

For the initial supported release, loss of a source span, wrong entity/unit/
period/basis, invented evidence, hidden financing, dropped feasible branch,
incorrect cash reconciliation or unreported unsupported treatment blocks
acceptance. All selected critical facts and operations must have exact
reviewed answers or the expected unresolved response. These zero-tolerance
conditions follow from the product's meaning-preservation requirements.
Non-critical extraction quality is reported by stratum and error category;
no arbitrary overall accuracy threshold certifies whole-report understanding.
An extraction benchmark needs its own sample size and uncertainty protocol
before making statistical accuracy claims.

The DSL and typed-library comparison uses identical packages, evidence,
schemas and runtime. Users perform the same tasks: correct a context, add a
shared uncertainty, represent a restatement, add a supported event and explain
a forecast difference. Task order is counterbalanced and experience recorded.
Both frontends receive the same validation and error messages. Measure
successful completion, material semantic errors, time and maintenance effort
with uncertainty appropriate to the participants; report no winner from the
current syntax checks. A textual language earns its maintenance cost only if
that comparison supports its use.

\section{Workload limits and release evidence}

The first integration workload is one local company package, up to 10,000
observations, 100 declared aggregate event slots per period, 64 materialised
finite-choice cells and a 30-second budget per solver operation. These are
provisional engineering limits for bounded failure behaviour, not measured
capacity or scientific defaults. They must be configurable and recorded.
Reaching a limit yields partial coverage with the unvisited formula/cells,
never an exhaustive-history claim. Peak memory and latency are measured only
after an implementation exists; a slower but semantically correct result
does not become a scientific failure.

Engineering release needs compiler/API equivalence, transactional replay and
adapter subset checks. Accounting release additionally needs paragraph-level
authority, dated applicability, exact fixtures and independent domain review
for every promoted operation. Forecast promotion additionally needs preserved
information sets, the stated baseline ladder, statistical uncertainty and
critical-regime vetoes. Human comprehension review remains separate from all
three. This version supplies a richer design candidate and reference
checks while preserving these outstanding acceptance decisions.


## FILE docs/design/proposal/architecture/persistence-contract-v1.md
# Persistence, correction and recovery, proposed version 1

A completed accounting transition is one committed fact about a particular
book and branch. A lost network response must not post it again; a correction
must not rewrite what an earlier information view contained. This contract
addresses MC04–MC06, MC18, MC25, MC27 and MC33–MC35, especially G17/G18. It
specifies observable storage behavior. The examples are transaction traces,
not an implemented database or a durability experiment.

## P1. Ownership and retained objects

One transactional store owns immutable portable records, dependency edges,
review snapshots, branch heads, committed journals/state deltas, operation
receipts and continuation checkpoints. Original source bytes live in immutable
content-addressed storage. A metadata transaction may reference a blob only
after its exact bytes are durably available and verified. A crash between blob
creation and metadata commit can leave an unreferenced blob; it cannot leave an
accepted source reference to absent bytes. Existing originals are retained.
Exports, caches, Parquet tables and rendered reports are derivatives of a named
store snapshot, not additional writable truth. An export failure does not undo
a committed transaction or justify posting again.

Each branch has a stable `branch_key`, an immutable branch definition Ref and a
mutable head `(state_ref, generation)`. Its required `book_mode` is exactly
`synthetic` or `real` and is immutable for that branch. Posting profiles declare
the modes they support; authorization checks mode and evidence scope. Changing
mode requires a new branch and fresh admission, not an in-place relabeling.
The branch definition names its family,
evidence/model/scenario versions and projection namespace. A separately
commissioned hypothetical run uses a new projection namespace/branch key;
reopening the same run uses its original key. A branch revision, renamed run or
retry cannot evade an event conflict inside that namespace. Aggregating branches
requires the declared family/view semantics and never counts projections as
multiple realized transactions.

The initial local implementation is proposed to have one logical transaction
writer. Multiple clients may submit requests, but the store serializes commits.
Other implementations must provide the same atomic comparisons and isolation;
“single writer” is not permission to omit stale-state checks. SQLite is an
implementation candidate based on P07's bounded probe. Distributed consensus,
specific filesystem durability and physical media failure guarantees require
their own implementation and evidence; no document calculation establishes them.

## P2. Event commit and replay

The stable accounting lookup key remains the tuple `(entity_id, book_id,
branch_key, business_event_id)` from accounting-replay-contract-v1. Event version,
payload and expected opening state belong to the complete request fingerprint,
not the lookup key. The generic Core 0 run/event key is historical exploratory
evidence and does not override this rule. Legacy fixture digests are retained
through the import mapping in L1, never silently compared with portable digests.

For one requested event the store performs:

1. Validate the request's decoding, field shapes, exact reference closure,
   internal bindings and admissible historical context. Corrupt or inconsistent
   input fails before any receipt lookup. Validate independent fields in the
   declared stage order; do not derive fresh accounting assumptions here.
2. Read the committed receipt index under the stable key. An equal fingerprint
   returns the original immutable receipt with `additional_commit=false`.
   A different fingerprint yields `EVENT_ID_CONFLICT`, including when its event
   version differs. Replaying a valid historical request is not reassessment
   against today's source or method version.
3. For an absent key, compare both expected opening state and expected head
   generation. A mismatch returns `STALE_OPENING_STATE`. Assess treatment and
   construct the candidate journal, economic delta and closing state outside
   mutation. Arithmetic/balance alone cannot authorize a treatment.
4. In one transaction, recheck absent key and the same head comparison, validate
   the candidate dependencies, then insert the journal, delta, closing state,
   dependency edges and immutable committed receipt, and advance the head.
   Commit all or none. A competing identical commit returns the original
   receipt; a different fingerprint conflicts; a competing different event
   advancing the head makes this request stale. No speculative candidate is
   published as committed while the comparison is unresolved.

The observation returned with replay may identify today's branch head, but the
receipt's original opening/closing states, assessment and journal never change.
The four accounting domains in the existing fixtures—state, journal registry,
delta registry and committed receipt index—remain identical on rejection/replay.
Candidate scratch data and diagnostics are not members of those domains.
Rejected requests may append a separately typed audit record after validation;
it cannot appear in the committed event index or count as an economic transition.
If an operation promises an audit receipt and its audit write fails, report that
failure explicitly while retaining the established unchanged-domain outcome.

## P3. Crash ambiguity, resume and exports

A response has `commit_observation` equal to `committed`, `not_committed` or
`unknown`. A crash before the atomic commit leaves the old head and no new
receipt. A crash after commit but before acknowledgement leaves the complete
new head and receipt. The client's timeout alone cannot distinguish those cases;
return `unknown` with the original key/fingerprint and query/retry that identity.
Do not retry under a fresh event ID. Once storage recovers, receipt lookup
resolves the ambiguity. Missing/corrupt committed dependencies are an integrity
failure, not a reason to reconstruct an apparently similar receipt.

A search checkpoint atomically records the semantic manifest, partition identity,
completed/explored cells, preserved unresolved formulas/regions, frontier order,
budget used and resulting objects. A cell is not complete before its evidence
and frontier transition commit together. Resume requires the original semantic
manifest and partition/traversal identity. An increased explicitly supplied
budget is a new scheduling request linked to the old checkpoint, not a new
financial model. Changed source, context, method, scenario, family or ordering
requires a new applicable manifest and a stated reuse relation; it cannot reuse
an old suffix by position. Cancellation preserves the last committed frontier.

Immutable export manifests name every record/blob, format/decoder, digest,
root query/view and required reference closure. Stage an export in a temporary
location, verify its closure, then publish its manifest atomically. An incomplete
export is explicitly incomplete and cannot be loaded as a closed bundle. Import
verifies all referenced bytes before committing metadata; an unavailable
optional attachment remains a located coverage obligation. Missing required
closure rejects dependent use, even if the manifest itself hashes correctly.

## P4. Review, correction and invalidation

Source and review requests have their own idempotency namespace
`(operation_kind, workspace_key, request_id)` and fingerprints. A repeated exact
request returns its immutable receipt; changed payload conflicts. A new review
uses an expected prior view and generation. It records reviewer, rationale,
accepted layer, referenced evidence and operation (propose, accept,
accept-alternative, reject or supersede). Legal state transitions follow the
evidence contract. Self-supersession and mismatched replacement scope reject
before mutation. Only review admission records can advance a reading's layer.

A new immutable view records its parent, changed decisions and dependency
selection revisions. It never mutates the old view. Invalidation follows the
reverse dependency graph transitively, including dependencies on candidate-set
membership, not only on the previously chosen members. Therefore adding a newly
eligible filing can stale a selection that formerly had one member. Newly
created descendants must check all ancestors against their requested view;
they cannot escape invalidation by being created after the invalidation scan.
Unrelated dependency closures remain usable. `explain` always uses the output's
frozen view; a current-view query explicitly reports stale dependencies.

A correction to an economic event is a new business event linked to its
predecessor and a specified correction method (reversal/replacement or a dated
adjustment, as applicable). It does not overwrite the original receipt and a
version bump alone does not post it. Corrected historical disclosure creates a
new evidence/model projection; it does not retroactively change what an investor
or the system knew. P17 supplies the accounting treatment of each correction;
missing treatment authority remains unresolved rather than a generic reversal.

## P5. Migration and reproducibility

Migration input is `(old_schema, new_schema, migration_method_ref, source_snapshot,
expected_head, declared_semantic_relation)`. Output retains original bytes/IDs,
new bytes/IDs, a complete mapping and the comparison evidence. A
representation-only migration must preserve decoded typed quantities, contexts,
uncertainty categories, references, admission states, event identities and exact
reference-query outcomes. Invertibility over the retained source domain or an
explicit lossless retained original is required. Changed model meaning, rounding,
calendar, probability or operation order is a new model/version, not a successful
representation-only migration. Failed mapping or comparison leaves all prior
heads and objects usable; migration never silently fills missing metadata.

Replay locks the model, view, package/calculator versions, scenario, requested
outputs, numeric/calendar policies, algorithm/capability manifest and relevant
environment. Exact rational operations on the same evaluated domain require
exact equality. Receipt replay returns the original recorded partition and
values. Re-executing a partial search with a wall-time limit need not visit the
same cells on another machine: compare answers on matched cells, retain both
frontiers and make no claim that partial coverage is identical. Reproducible
prefix comparisons use a pinned traversal and operation-count budget;
elapsed-time limits are resource stops, not semantic equality criteria.
Resume uses P3's exact saved frontier. Approximate
operations require predeclared method-specific error comparisons and retain both
values; a generic float tolerance cannot establish financial equivalence.
Random-stream identity names seed, coupling group, economic owner, date,
shock-kind and draw index, with pinned generator and transforms. Branch traversal
position is absent. The retained SHA-based reference primitive remains only an
identity illustration; no production generator or calibration is selected here.

PX01–PX08 in the shared examples specify lost acknowledgement, exact replay,
changed payload, two writers at one head, correction invalidation, branch
isolation, incomplete export and migration outcomes. Their finite traces make
the expected behavior reviewable. The future implementation must additionally
pass crash/reopen/fault-injection tests on the selected storage/environment.

## P6. Alternatives and tradeoffs

Mutable documents with periodic checkpoints cannot establish the atomic
receipt/state relation above without an additional transaction protocol.
An event log with deterministic projections is viable if its commit marker,
projection visibility and replay checkpoints obey the same contract. The
proposed transactional metadata store plus immutable blobs separates large
source bytes from small atomic changes and fits existing local probes. Its
single-writer throughput and crash guarantees are unmeasured. Analytics engines
and storage libraries remain replaceable behind these observable semantics.


## FILE docs/design/proposal/architecture/cross-contract-amendment-v1.md
# P16 interaction amendments after independent review

This supplement resolves the material cross-contract findings from the direct
platform and domain reviews. It applies to the named fields/operations below,
not to all older records by date. Historical fixture bytes and identities remain
unchanged. The architecture index pins this amendment with the other contracts.
It addresses MC04, MC08–MC14 and MC24–MC27/MC33–MC35. All exchanges described here
are proposed behavior; P17 supplies actual domain methods and authority.

## A1. A commit request that cannot promote assess-only permission

Native accounting request v2 remains exactly `operation=assess_only`. Its
assessment has posting_permitted=false and is not an authorization to commit.
Changing that field or attaching its eligible finding to a commit is invalid.
The portable commit path uses the following separate closed records; no native
request schema is extended silently. Every Ref has the L1 kind/schema/digest,
all referenced records/blobs resolve, and additional fields are rejected.

`AccountingEventBasis/v1` has exactly `identity`, `event_ref`, `opening_ref`,
`context_ref`, `branch_ref`, `time_ref`, `chart_ref`, `authority_refs`,
`method_ref`, `evidence_refs`, `admission_refs`, `assumptions_ref`, `view_ref`.
`identity` has exactly entity_id, book_id, branch_key and business_event_id,
all nonempty ASCII identifiers. Each `_ref` is a nonnull typed Ref; plural
Refs are schema-declared sets. Evidence/admissions may be explicitly empty only
when the method's admitted assumption scope allows that and records why.
Authority_refs must identify actual applicable support or a specifically typed
SyntheticAuthority for a declared synthetic example; it cannot be an untyped
claim of compliance. The economic event contains its payload/version/date,
not a reference to a future commit request. All identity/context/branch/time/
chart/method/authority/admission bindings are checked as in the domain contracts.

`PostingAuthorization/v1` has exactly `basis_ref`, `posting_profile_ref`,
`method_ref`, `authority_refs`, `status`, `findings`, `posting_permitted`,
`evidence_level`, `view_ref`. Status is eligible, unresolved, ineligible or
outside_scope. Findings retain each method precondition and its reason/source;
no early summary suppresses other material findings. posting_permitted is an
exact Boolean, true only for eligible status under a posting profile that
explicitly supports this event/treatment/method in this view. All other statuses
require false. Evidence level states source-supported or authored-synthetic
scope; synthetic eligibility cannot authorize a real-book posting. A method
without a complete posting specification returns outside_scope and false.
The branch definition has required `book_mode`, exactly `synthetic` or `real`,
and the posting profile has required nonempty `supported_book_modes`, a set of
those literals. Authorization verifies membership and the following evidence
scope. A synthetic branch requires evidence_level=authored-synthetic
and cannot be committed into a real branch. A real branch requires a
source-supported posting authority and separately admitted real-workspace
facts/assumptions; an admitted assumption retains its assumption label. Copying a
synthetic label into a real branch is a binding failure. This discriminator is
checked by `accounting.authorize@1`, which produces this record from the
EventBasis and profile;
it does not mutate a book or reuse native assess-only permission.

`AccountingCommitArguments/v1` has exactly `basis_ref`, `authorization_ref`,
`journal_ref`, `delta_ref`. All are nonnull typed Refs to EventBasis,
PostingAuthorization, JournalProposal and EconomicDelta respectively. The
proposal and delta each name the same basis and authorization and contain the
domain journal lines/independent state effects. Their types, signs, contexts,
rounding and roll-forwards obey the accounting contract. Their dependency graph
ends at the immutable basis/authorization, not at the later final commit request.

The outer `OperationRequest` has operation accounting.commit@1 and a nonnull
expected_head whose owner matches the basis's entity/book/branch and state_ref
matches opening_ref. Its generation is the original expected branch generation.
The P2 lookup key is derived solely from basis.identity. A `Ref` to a native v2
assessment in authorization_ref fails INVALID_REFERENCE_KIND; a portable record
with false posting permission fails POSTING_NOT_AUTHORIZED. No flag edit can
pass the recomputed profile/method/admission checks. For a genuinely supported
profile, verify all proposal/authorization/basis bindings before receipt lookup,
then follow exact replay/conflict, absent-key freshness and atomic recheck/commit.
The final receipt refers back to the request/proposal and new state. None of
those earlier records refers forward to that receipt, so L1's graph stays acyclic.

The profile package and domain schema lock define the JournalProposal and
EconomicDelta payload for that operation, including expected account and
economic-state effects. An unknown schema or missing eligible profile yields
UNSUPPORTED_PROFILE_OPERATION, no commit. This is a defined commit interface,
not a claim that P16 supplies every corporate or sector posting method. Existing
R01–R06 remain legacy replay examples under their original schemas. `A1-positive`
is a specified request under an authored equal-price example profile with the
100 asset/2 expense/102 cash candidate; `A1-negative` substitutes the native
assess-only record and must reject before lookup. Equal arithmetic alone does
not satisfy the authorization.

## A2. Accounting results and coverage mapping

These explicit rows extend the integration status table. They consume the full
tagged native response and assessment, not a selected string in isolation.

| Native accounting combination | Platform result |
| --- | --- |
| status=assessed, assessment eligible, computation specified_exact, math unresolved | disposition completed; structural valid; mathematical unresolved; computation complete; native assessment retained; no new commit |
| status=assessed, assessment unresolved, computation specified_exact, math unresolved | completed assessment operation; structural valid; mathematical unresolved; computation complete; no journal or permission |
| status=assessed, assessment ineligible or outside_scope, computation specified_exact, math unresolved | completed assessment operation; structural valid; mathematical unresolved; computation complete; adverse assessment retained; no journal or permission |
| native input rejection invalid/unresolved/not_computed | rejected; same status meanings; request_ref and payload null; submission retained |

`completed` answers whether the assessment request was processed. It says neither
that the proposed treatment is eligible nor that its mathematics was established.
Native accounting_validity=not_assessed remains not_assessed. All specified_exact
examples retain evidence_mode=specification_example and capability
specified_only_no_runtime. X007 therefore maps successfully as a completed
assessment with an unresolved treatment, without inventing `defined` mathematics.
Unknown combinations return STATUS_MAPPING_UNSUPPORTED with the native record
retained and no asserted platform completion.

Coverage mapping preserves every native region predicate and its original
reason/subtype. Native completed → platform completed; unsupported → unsupported;
numerical_failure, solver_unknown and unexplored → unresolved; cancelled →
cancelled. Native proved-empty model regions → infeasible only with their proof
and original model scope. A service failure does not establish such emptiness.
The source partition/overlap relation, parent domain, mass value or explicit
unknown-mass obligation and law/view/admission Refs travel with every region.
Mapping does not merge records solely because they have the same platform label.
Any label without an explicit mapping returns STATUS_MAPPING_UNSUPPORTED.

For mass 3/5 completed and 2/5 numerical_failure, platform output retains both
regions, unresolved subtype numerical_failure and mass 2/5. No normalizing by
3/5 occurs. A region with unknown mass remains unknown, not zero. A read-only
assessment's singleton coverage can be completed even when its treatment is
unresolved; that denominator describes assessment work, not all financial
histories. The financial obligations remain in the typed assessment/unresolved
fields and cannot disappear into the singleton count.

## A3. Repeated conditions and information reuse

The native update operation distinguishes an authored event condition, an
observed likelihood block and a condition proposed as a new observation. Repeating
the identical admitted condition identity in a descendant law is idempotent:
new request ID may produce a new derivation receipt, with denominator one,
unchanged masses, no new atom and the original condition's information lineage
retained. This includes a condition whose lineage traces to an already consumed
observation. It does not multiply that observation's likelihood a second time.

DUPLICATE_INFORMATION applies when the caller submits an already consumed
observation as an incremental likelihood block, or falsely presents the repeated
condition as new information. Matching member sets alone does not establish
matching condition identity. Changed meaning/coordinates/evidence must be bound
and reviewed under their own request. UC01's A and A_then_A are authored
conditions, with no observed-information atoms; D and E are observed blocks with
the specified conditional kernel. This amendment resolves the apparent overlap
between uncertainty §3's idempotence rule and §4's new-information table.

## A4. Selection after correction

Selection owner identity is `(family_ref, target_evidence_view_ref,
target_time_ref, purpose)`. Every owner has its own immutable selection revisions
and mutable selected pointer. A historical query naming an old evidence/time
view reads that view's selection and exact lineage. A correction creating a new
evidence view does not mutate the old pointer or implicitly admit/select its
new candidate posterior. UC08's unchanged state_after therefore refers to the
old owner, not a current pointer in the newly corrected evidence view.

For a current-view query in the new owner, an inherited selection whose
dependencies are superseded returns SELECTION_SUPERSEDED, no usable probability
result, and an explicit re-admission/re-selection obligation. If no inherited
selection exists, return SELECTION_REQUIRED. Resolving either requires an
admissible new attachment and the owner's expected revision; it cannot fall
back silently to an older evidence owner. Historical requests remain valid in
their frozen scope. Numeric correction, admission and selection remain three
distinct effects. This also governs descendants created after the correction.

## A5. Native request versions and validation meanings

For uncertainty attachment storage, `representation_validity` assesses record
shape separately from normalization and reuse. The historical attachment-v2
text's structural_validity label is interpreted as that record-level field.
For an operation result, structural_validity is request validation, including
shape, exact reference binding and admission in the requested view. Retaining
a well-shaped old attachment as RETAINED_ONLY does not make a stale-law request
valid. Platform adapters name their source schema and target field, preserving
both meanings. A malformed supplied record stays invalid at both boundaries;
no status is silently reinterpreted without its record/operation discriminator.

`UncertaintyRequest/chaining-1.1` extends the §2 base request list explicitly.
Base fields remain required and unchanged. A request using a derived admitted
bundle additionally requires admission_receipt_ref, bound to its attachment,
law, view, purpose and admission. Operation `correct_and_rebase` additionally requires
target_time_ref, target_evidence_view_ref and target_admission_ref, each bound
to the corrected inputs and proposed output view. Base law/view/attachment
refer to the frozen calculation input; target fields refer to the revised
authorization context. A target field is not required to equal its base field.
For `likelihood_update`, the three target fields are optional only as an
all-or-none tuple authorizing a proposed changed observation; they do not permit
reuse of a consumed atom. Thus the retained correction submitted incorrectly
as an incremental update passes that shape rule and then fails
CORRECTION_REQUIRES_REBASE. Other operations reject these target fields.
Unknown extra fields and a partially supplied target tuple reject.

The existing CH fixture registry explicitly selects this request profile through
its import adapter; stored native bytes/digests are preserved as historical
examples. New wire requests must advertise the profile in the enclosing
signature/schema lock, never rely on implementation inference from a CH prefix.
No old uncertainty v1 exact field list accepts these extra fields by accident.

## A6. Semantic correction input versus affected descendants

Portable correction uses two separate records. `CorrectionBasis` depends on
the unaffected base law, superseded reading/semantic atom, corrected source,
target time/evidence admission, replacement rule and calculation method.
It does not depend on which optional descendants happen to have been computed.
`InvalidationReport` depends on that CorrectionBasis plus the inspected store
snapshot, and lists affected descendants and why they cannot be reused. Adding
a stored descendant changes the report identity, not the corrected calculation
or its semantic family/law identity. Reverse-dependency discovery and query-time
ancestor checks enforce invalidation for descendants absent from that report.

L1 still requires every typed Ref in each portable record to be listed among
that record's dependencies. Affected descendant Refs are dependencies of the
audit report, not inputs to the corrected mathematical model. This split avoids
both dangling audit references and semantic dependence on optional work.
The native `CH.evidence.corrected@1` is a combined historical audit/context
record. Its LegacyImport retains its ID and maps its corrected inputs to
CorrectionBasis and invalidated_descendant_refs to InvalidationReport. Its old
audit digest is not asserted to be the portable correction's semantic identity.
No retained fixture is rewritten or claimed to have this portable encoding.
