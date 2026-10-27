READ-ONLY, TOOL-FREE SUBSTANTIVE REVIEW. Review ONLY the actual self-contained specification and samples below. Do not fetch or request more files, do not execute, and do not launch agents. Missing exhaustive fixture coverage limits acceptance scope; it is not a reason to withhold concrete semantic review of supplied contracts. Earlier tool-reading reviews ended on turn limits without conclusions. Return a verdict in this single response.

Question: Is the supplied P16 architecture design coherent enough to govern later detailed methods, within its stated scope? Identify concrete semantic errors, unsupported claims or missing behavior preventing that. Distinguish P16 architecture defects from P17 accounting/sector/source methods, P18 manuscript and P19 readiness. Product runtime implementation is disabled. Counts (797 structural, 169 arithmetic, 2580 accounting assertions) show only finite document checks. 932 protected files are unchanged. Human/domain/forecast acceptance is not established.

Give at most six material findings with file/section, counterexample, repair and blocker status. State what you checked and what the evidence cannot establish. End VERDICT: AGREE or VERDICT: REVISE. Be concise but substantive.

Scope: domain contract integration and active uncertainty admission/chaining; verify finite posterior arithmetic and correction semantics.

FILE docs/design/proposal/architecture/evidence-contract-v3.md
# Evidence contract v3 — proposed semantics

This contract addresses MC01–MC04 and the admission boundary of MC27
(G2/G11/G17). It specifies evidence preparation for the whole product, including
later group, bank, insurance and cross-standard work. It does not select an
initial product profile. P15-E01–E03 receive concrete proposed answers; E05
still needs a real conflicting-disclosure walkthrough. Examples are in
`evidence-fixtures-v3.json`. Synthetic text is identified there and supplies
no accounting authority.

## E1. Input and output records

An input `SourceVersion` contains immutable original bytes, their SHA-256,
media type, source URL or original local origin, acquisition event, issuer,
document identity/version, and publication evidence. An extracted text file is
a separate derivative with its own hash, extraction method/version and link to
the original. Reacquiring different bytes creates a new version even if the URL
is unchanged. A URL, matching title or current download does not establish the
bytes available at an earlier date. The time contract determines that claim.

A `UnitOccurrence` identifies one source version and a locator: PDF physical
page plus printed page and bounding region where available; HTML element or
XBRL fact/context identifiers; text line/character span in a pinned extraction.
Locators retain table headings, footnotes and continuation links needed for
meaning. A text locator alone does not establish faithful PDF extraction.
Units identify parent section, annual/quarterly/semiannual package root, and
disposition. An occurrence is never deleted because another occurrence has the
same text. Byte-identical span content may share a content ID; semantic
equivalence additionally requires compatible context and an explicit review.

A `ReportedAssertion` links every supporting occurrence and preserves literal
text/value. An `ExtractionReading` identifies a candidate reading and its
review events. An `Interpretation` identifies the exact extraction versions,
financial scope, dependencies, modality and proposed meaning. A `Derivation`
records input versions, expression, result context and assumptions. An
`Assumption` has an author, rationale, scope and alternatives and cannot be
labelled issuer evidence. A `Conflict` links incompatible candidates and their
affected queries; conflicting faithful readings both survive.

Preparation returns (1) immutable source and reading records, (2) a package
coverage report with three separate populations, (3) proposed, admitted and
unresolved predicates, (4) query-specific evidence exposure, and (5) typed
issues containing record IDs, locators, dependencies and repair actions.
Every output identifies the evidence view and review snapshot. Neither an
extraction confidence score nor review acceptance supplies a probability over
company histories.

## E2. Package closure and three populations

Start with declared annual, quarterly and semiannual roots, dates, included
sections and expected statement/note indexes. Reconcile contents with actual
headings and tables, then follow references within the declared material scope.
A reference edge retains its source locator, target description, candidates,
resolution evidence and disposition. The permitted dispositions in these
fixtures are `resolved`, `duplicate_verified`, `cycle_closed`,
`missing_continuation`, `ambiguous_target`, `unavailable_target`, and
`resource_exhausted`. A verified cycle stops repeated traversal; its target must
exist and the closing edge remains visible. Similar names alone cannot resolve
an ambiguous target. A budget limit retains the unvisited frontier and the
limit reached, never an empty-success result.

The acquired-unit population counts retained occurrences and unique contents
separately. Its denominator is the declared inventory, with discovered missing
targets and unknown inventory extent reported alongside it. Parent and child
units cannot both contribute to a count of nonoverlapping leaf spans. A repeated
paragraph contributes two occurrence locators but one content body; this does
not merge assertions applying to different dates or entities.

The reviewed-assertion population counts identified assertion candidates at a
named layer, once per contextual assertion identity. It reports accepted,
rejected, pending and unresolved counts and aliases explicitly. It also retains
unread/unstructured source units, whose unknown assertion count cannot be
treated as zero. A denominator of six discovered candidates means six candidates
reviewed to some disposition, not six assertions in the whole real report.

The query-exposure population is the declared query set and each query's
transitive evidence dependencies. Each query is `supported`, `conditional`,
`unresolved`, or `unsupported` for its requested claim. `supported` means the
specified evidence-reading operation has met its admission rules, not that the
issuer's report is true or compliant. `conditional` requires explicit selected
assumptions; an unselected assumption leaves the query unresolved. Missing or
ambiguous references block only dependent claims, but uncertain relevance must
be reported as an unresolved dependency until reviewed. An unaffected disclosed
revenue lookup can succeed while debt-exposure reconstruction remains unresolved.

Package closure requires no unresolved material references, reconciled inventory
and a documented scope/materiality decision for exclusions. Semantic completion
additionally requires every in-scope unit to have its assertions and unresolved
meaning accounted for. Three root files, all retained known units, or a high
review count cannot establish either condition. The synthetic fixture has seven
occurrences, five unique contents, six contextual assertion candidates, seven
reference edges and five queries; its four unresolved edges veto package closure.

## E3. Numeric context and faithful display

A numeric reading includes legal entity and perimeter/version, concept and
mapping version, dimensions, instant or half-open reporting interval, fiscal
calendar/version, currency, unit, scale, sign convention, measurement basis,
reported lexeme, display decimals, and separately the rounding convention and
tie rule with their source or assumption references. Unknown fields are tagged
unknown, not supplied by a global currency/calendar default. Zero, missing,
not-applicable and a printed dash are distinct; a dash becomes zero only under
a supported interpretation.

For a reported lexeme 364,980 with USD and a million scale, the exact *scaled
displayed value* is 364,980,000,000 USD. That is not a claim that the issuer's
underlying unrounded amount equals it. Rendering must reproduce the lexeme,
scale label, sign convention and precision, including parentheses, without
round-tripping through binary floating point. Derived displays retain their
expression and do not masquerade as original disclosure.

For arithmetic, currencies, dimensions, bases, perimeters and concepts must
match or have an admitted explicit conversion/mapping. Flows require compatible
nonoverlapping intervals for addition; stocks are not summed over dates.
YTD subtraction follows T5 in the time contract. Mismatches return
`INCOMPATIBLE_CONTEXT`; unknown compatibility returns `UNRESOLVED_CONTEXT`.
Permissive archival display is possible without authorising arithmetic.

If source evidence establishes rounding to nearest unit u, a displayed value d
has interior compatibility d-u/2 < x < d+u/2. Endpoint membership follows the
specified tie rule. For ties-to-even, displayed integer 120 admits both half-unit
endpoints; 121 admits neither. With nearest established but tie rule unknown,
the closed interval is only an outer enclosure: both endpoint memberships are
unresolved. A query requiring exact endpoint feasibility must return unresolved.
If even the nearest convention is unknown, displayed precision alone supplies
no such interval. A user may explicitly choose assumption `nearest-model-v1`;
its interval and every dependent result then remain conditional. None of these
intervals supplies a distribution. P02's closed half-unit model is evidence of
a prior compatibility assumption, not issuer confirmation of that convention.

## E4. Narrative interpretation and admission

A narrative interpretation binds subject/entity, contract or instrument set,
valid dates, quantifier, modality (`reported_fact`, `permission`,
`conditional_obligation`, `policy`), predicate, exceptions, dependent facts and
affected quantities. Missing scope is unresolved, not universal. Literal wording
is retained even when no executable predicate is available.

“May repurchase up to 50” permits an action in the specified period and currency;
it imposes neither a purchase nor a payment. A selected scenario may add an
exercise decision and resulting cash flow, separately attributed as an
assumption. “Pays if borrower defaults” preserves the condition; with default
unknown it cannot become an unconditional payable. “Substantially all” supplies
no 95% threshold. A proposed threshold must be a named modelling assumption
and cannot replace the retained qualitative claim.

The source-backed Apple example uses Note 9 of the 2024 10-K (physical page 46, printed page 43),
the fixed-rate debt table and the adjacent swap paragraph. The coupon
classification applies to notes. The paragraph says certain USD notes are
effectively converted to floating rates by swaps; it does not identify each
instrument allocation here. Preserve a combined exposure query as unresolved
pending allocation and terms. Reject a translation stating all combined
note-and-swap cash flows are fixed. The adjacent Note 4 wording “may use” is a
policy/permission description, not evidence that every instrument is hedged.
These passages are compatible qualifications, not a genuine source conflict.

Review events name target ID/version, layer, action, reviewer/time and reason.
At each layer a candidate progresses `proposed -> accepted | rejected |
unresolved`. A new alternative starts at proposed. A correction creates a new
candidate and an explicit supersession link; it does not overwrite source bytes
or retroactively change old review snapshots. Rejected/unresolved candidates
can be reconsidered only by a new recorded decision. Extraction acceptance
means faithful reading; interpretation acceptance means accepted scoped meaning;
accounting admission additionally requires applicable treatment authority,
context and rule/version. No transition automatically accepts a higher layer.

Read-only disclosed-value queries can use accepted extraction and context.
Constraint queries require an accepted interpretation, admitted translation,
resolved predicates or explicit conditional assumptions. Posting requests also
require accounting admission. Dependency corrections invalidate current use of
transitive descendants; old results remain retrievable under their old evidence
view with a current superseded warning. Unrelated descendants stay usable.
The storage transaction and identity mechanics remain a later P16 contract.

## E5. Failure, alternatives and interaction obligations

Integrity mismatch or dangling required source IDs rejects the affected
record; missing meaning produces a retained unresolved record. A conflicting
accepted pair returns both alternatives plus affected-query status, never
last-write-wins. Unsupported translations return `UNSUPPORTED_PREDICATE` with
the original text. Resource limits return partial inventories and unfinished
frontiers; they cannot certify impossibility or complete coverage.

The main alternative is one aggregate completeness score. It is simpler to
display but hides missing contracts behind parsed pages; separate populations
are proposed because each answers a different question. Another alternative
lets accepted free text constrain a model implicitly. Explicit scoped admission
costs annotation work but prevents permissions, exceptions and qualitative
terms from acquiring invented mathematical meaning. Automatically inferring
nearest rounding is convenient but overstates source support; prohibiting all
conditional analysis is unnecessarily restrictive. Separate source facts and
named assumptions support both faithful reporting and useful conditional work.

Time supplies eligible source/review versions; history families receive admitted
constraints and unresolved predicates without manufactured weights; accounting
receives evidence plus authority requirements; language/IR must preserve every
scope and assumption; persistence must retain immutable versions and dependency
invalidation; interfaces must expose all three coverage populations and reasons.
Those counterpart contracts remain unfinished. Independent substantive review,
a real conflicting-disclosure case and later domain authority work are required
before closing E05 or the wider mission gaps.

## Revision record

v2 retains the v1 contract semantics and points to the corrected fixture set.
E-display describes assets and now names its sign convention `positive_assets`;
the v1 revenue sign label was wrong for that context. The scaled displayed
amount remains 364,980,000,000 USD. No source statement was changed.

## v3 source-locator correction

Original PDF inspection in e05-source-investigation-v1.md corrects the Note 9
locator. No substantive admission rule or expected output has changed; v3 fixtures
correct the same locator and remain the examples for E1–E5. E05 source evidence remains insufficient.

FILE docs/design/proposal/architecture/time-contract-v2.md
# Time contract v2 — proposed semantics

This contract addresses MC05 with MC04/MC25/MC27 interactions (G13/G17/G18).
It supplies the proposed answer to P15-E04. Its fixtures are specification
examples, not a runtime implementation. The existing P06 chronology selector
is a counterexample where it substitutes availability for absent ingestion and
allows unverified historical bytes by default. Neither behaviour is adopted
for a claim requiring the missing evidence.

## T1. Records and query dimensions

An assertion version identifies economic instant or event dates, reporting
interval and calendar, public availability evidence, ingestion event, review
events, source byte hash and evidence of byte vintage. These are different
clocks. A payment date does not establish recognition time; reporting period
end does not establish publication. A later acquisition may preserve bytes
known to have been public earlier without establishing system possession then.

Economic and reporting periods use ISO calendar dates and explicit calendar
versions; flow intervals are [start, end_exclusive). Timestamp comparisons use
timezone-aware instants converted to UTC. Preserve the original timezone,
precision and source representation. Missing timezone rejects an instant
comparison (`MISSING_TIMEZONE`); it never means the machine's local zone.
Absent ingestion and explicit-null ingestion are separate diagnostic states,
`INGESTION_ABSENT` and `INGESTION_UNKNOWN`, but neither establishes an instant.

A query specifies `admission_mode`, `selection`, economic/reporting target,
information cutoff when applicable, system-as-of when applicable, review
snapshot, requested layer, and calendar/perimeter/measurement basis. Selection
is `original`, `latest_available`, or `harmonised`. No selection overrides
admission. Omitted required cutoffs or a nonexistent review snapshot reject the
request, rather than silently choosing today's data. Outputs contain selected
IDs, known exclusions/reasons, unresolved candidates/dependencies, derivation
lineage, assumptions, and claim status. Historical simulation receives only
admitted evidence; diagnostic knowledge of later rejected IDs belongs in the
audit output and must not become scenario input.

## T2. Three admission modes

`archival_exploration` allows inspection of retained bytes, including unknown
publication or ingestion. Such rows are labelled `historical_admissibility:
unestablished`. With a cutoff and unknown publication they may be displayed only
as unresolved archival candidates, not as cutoff-qualified selections. Without
a cutoff all retained rows may be selected under explicit lineage rules, but
the result remains archival; no historical knowledge claim follows. Source
integrity checks still apply. Exploration does not authorise accounting posting.

`investor_information` requires information cutoff K, supported public
availability at or before K, and evidence linking the exact selected source
bytes to that availability. Later ingestion is permitted. Unknown publication,
unverified historical bytes or date precision straddling K leaves a candidate
unresolved and excludes it from the admitted set. Known publication after K
is a definite exclusion. An accepted extraction performed later may read an
eligible old document using an explicitly chosen review snapshot. Any derived
interpretation that consumes later information is inadmissible for a historical
decision rule; its full information dependencies must pass K separately.
This view establishes public availability of evidence, not actual investor
awareness or a tradeable execution opportunity.

`system_as_of` requires S and an immutable receipt proving exact bytes were
ingested no later than S. Ingestion cannot be inferred from publication. The
requested accepted layer additionally needs review decisions visible by S;
later review cannot be projected back. Retained raw evidence may be returned
with its then-unreviewed status if the requested layer is raw. System possession
alone does not establish public availability. If a query also requests an
investor cutoff K, it must satisfy both filters, including public byte-vintage
evidence. Unknown publication alone need not block a *pure* system-possession
query. This separation permits later legitimate private/local records without
claiming that they were public.

A known later revision is excluded by its actual time; it does not suppress
an earlier eligible assertion. An unresolved potentially relevant version
keeps a result unresolved even if an older candidate is selected. Unaffected
keys retain supported results. `unresolved` is different from an empty set
proved to contain no eligible records.

## T3. Date-only evidence and byte verification

A publication date D with named timezone Z denotes an interval from local
midnight D through (but excluding) the next local midnight. The physical
instant is unknown within it. If K is before the interval, exclude the record;
if K is inside, return `PUBLICATION_PRECISION_UNRESOLVED`; if K is at or after
the interval's exclusive upper boundary, admission is supported by that date
evidence. This is a conservative availability convention, not a claim that
publication occurred at midnight. No fixed 24-hour duration is assumed across
daylight-saving changes. Missing Z keeps the interval unresolved. Conflicting
publication sources remain alternatives until resolved; choose neither the
earliest nor latest silently.

An ingestion date without an instant similarly proves only bounded possession;
queries inside the date remain unresolved. Review date precision is treated
the same way. A receipt must bind timestamp evidence, source ID and byte hash;
`ingested_at` alone without a receipt is `INGESTION_RECEIPT_UNVERIFIED`.
Public byte-vintage evidence and system receipt evidence are different proofs.
Current byte integrity failure is a hard rejection (`SOURCE_HASH_MISMATCH`),
whereas missing historical linkage is unresolved. An issuer timestamp on a
current webpage cannot by itself prove unchanged historical bytes.

## T4. Selection, supersession and review state

Supersession edges identify assertion IDs and the exact concept, period,
perimeter and dimensions replaced, plus supporting evidence. The graph must be
acyclic and targets must exist; a cycle or missing target rejects the affected
lineage. A document-wide replacement is not inferred from one corrected fact.
Duplicated content with no assertion change remains an alias with its original
lineage. Distinct same-date records need a supported ordering or a retained
conflict; IDs and filesystem order never break a semantic tie.

`original` returns eligible root assertions for each requested key. A later
revision is not an original merely because its root is unavailable. Multiple
unrelated roots remain competing assertions. `latest_available` returns eligible
assertions with no eligible admitted descendant superseding them for that key.
Only the eligible graph may remove an older record; future review acceptance
or later ingestion has no backward effect. If an eligible descendant's
intermediate ancestor is known but ineligible, the supported transitive edge
can still establish replacement; missing graph evidence cannot. Multiple live
leaves for the same exact quantity produce `CONFLICTING_VERSIONS` and remain
visible, rather than being averaged.

`harmonised` starts from latest eligible records and applies explicit admitted
transforms to a declared target basis, calendar and perimeter. Each transform
states input IDs, formula, authority/assumption support, review snapshot and
information dependencies. The output is a derived reading with a new ID;
original rows and their labels are preserved. Transform availability must pass
the same admission rules as other dependencies. Missing authority or a missing
opening bridge returns `HARMONISATION_UNSUPPORTED`; it does not relabel an old
number as comparable. An algebraic synthetic transform tests lineage only.

## T5. Period arithmetic and change treatments

Subtract YTD A from longer YTD B only when concept, unit, currency, measurement
basis, perimeter, calendar, interval start, aggregation dimensions and evidence
revision compatibility match. The shorter interval must be a proper prefix.
The remainder is [A.end_exclusive, B.end_exclusive). Same vintage labels are
not sufficient if other context differs. Different vintage labels require a
specific admitted compatibility bridge covering the fact, not general claims
that both reports are audited. Original selection may return H1-v1 and FY-v2
for display while arithmetic between them is rejected.

The synthetic retained example is H1-v1 = 120, revised H1-v2 = 110, FY-v2 = 260.
Compatible subtraction gives H2-v2 = 260 - 110 = 150. Subtracting 120 gives
140 arithmetically but fails the compatibility contract, so the financial query
returns no H2 value. A 52/53-week calendar change or a changed group perimeter
also requires an explicit bridge; endpoints alone cannot establish comparability.

An extraction correction changes the reading of unchanged source bytes; issuer
revision changes the reported assertion; an estimate update changes prospective
model inputs; a policy/error correction may require retrospective treatment.
The time contract requires change kind, authority/rule version, effective date,
affected periods/accounts, opening-balance bridge, transition method and review
evidence. It does not determine the standards-specific classification. Missing
authority returns `TREATMENT_UNSUPPORTED` and preserves original/revised views.
No fixture here certifies IFRS, US GAAP or ASBE retrospective/prospective rules;
P17 must supply the supporting methods and authoritative cases.

## T6. Alternatives, invariants and interactions

Permissive fallback makes archival data easier to query but cannot establish
system history: two systems can ingest the same public filing on different
days. Strict receipt-based system admission and separately qualified exploration
are therefore proposed. Treating all missing publication data as fatal to every
operation would wrongly prevent a supported system-possession query. Combining
admission and revision selection in one “latest” switch hides these differences.
The proposed orthogonal fields make the requested historical claim explicit.

For date-only publication, start-of-day admission is convenient but admits
possible future information during that day. End-of-interval admission is
conservative and preserves the unknown instant. An arbitrary noon default is
unjustified. Exact research backtests requiring intraday availability must obtain
better evidence or leave those observations unresolved.

For every selection, selected and definitely excluded IDs are disjoint; selected
IDs can coexist with unresolved competitors, in which case the affected claim
is unresolved. Hashes and old views are immutable; a correction invalidates
current dependent results without rewriting historical records. Increasing K
may legitimately change latest selected values, so value monotonicity is not
an invariant. Eligibility grows only if the evidence/review snapshot and other
filters stay fixed. No view claims the issuer's assertions are economically true.

Evidence supplies immutable versions and layer decisions; history/uncertainty
must retain live alternatives; accounting supplies transition authority and
opening bridges; language/IR must serialize cutoffs, intervals and required
contexts; persistence supplies receipts, immutable snapshots and transitive
invalidation; interfaces expose unavailable versus unresolved versus unsupported
outcomes. Full definitions of those interfaces, identity/replay and domain
treatment remain later contracts. Human acceptance remains pending.

## Revision record and fixture conventions

The current examples are `time-fixtures-v2.json`; v1 remains preserved.
The harmonisation example previously expected a conditional result despite an
empty request assumption list. That is wrong relative to E2's explicit-selection
rule. v2 selects `bridge-assumed`, records accepted synthetic review and byte
support for the transform, and names its information dependency. A transform
with an unselected required assumption must remain unresolved, with no admitted
derived value. An assumption ID is selected only by its presence in the request's
`assumptions` list; merely appearing in the transform does not select it.

Both harmonisation examples now use the documented `record_subset` operation.
Their restricted universe contains only h1-original; they illustrate a derived
reading of that source, not selection from a complete restatement history.
The all-record investor example still selects h1-restated and fy. Base review
acceptance assumes no later information dependencies beyond the stated bytes
and context. These explicit synthetic premises supply no historical-publication,
accounting-authority or issuer-restatement evidence.

FILE docs/design/proposal/architecture/history-families-contract-v1.md
# History families: proposed contract, version 1

This contract specifies how one set of disclosures can support several joint
financial histories. It addresses MC08–MC11 and G1/G16, with evidence, chronology,
language and reproducibility dependencies under MC02/MC04/MC05/MC18/MC25/MC27.
It is a proposed specification. Its examples are deliberately synthetic;
independent review, accounting validity and human acceptance remain pending.
The companion `history-families-fixtures-v1.json` contains specified inputs and
expected results, not observations from an implemented engine.

## H1. Inputs and the question being answered

A reconstruction request supplies the following versioned records. References
mean immutable record versions and content hashes, not a mutable name such as
“latest”. A declared unknown differs from an omitted required field.

| Record | Required content | Admission consequence |
| --- | --- | --- |
| Evidence/time view | Source, reading, interpretation and review IDs; admission mode, selection mode, cutoffs, context-specific candidate-set revisions and unknown eligibility | Use the evidence v3 and time v2 rules. Unknown availability remains an affected-query obligation. |
| Observation | Concept, entity, perimeter version, economic instant or half-open reporting interval, calendar, basis, unit/currency, scale, sign and precision/rounding support; expression and source links | Two occurrences may refer to one quantity only through a supported context mapping. Never equate totals from different periods or bases by matching labels. |
| Interpretation and assumptions | Alternative IDs, conflict scope, admission layer, selected conditions, rationale, author and dependency versions; separate uncertainty category | Reading acceptance is not factual truth, treatment permission or a probability. An unselected assumption is not a constraint. |
| Opening state | Economic identities, rights/obligations, dated contract/lot/cohort state; accounting balances and reconciliation where supported; explicit unknown domains | Missing opening facts remain variables/obligations. Missing accounting support cannot be filled by balancing entries. |
| Model scope | Entities/perimeters, periods, candidate event/contract types, admissible domains, exclusions and reasons, template registry and mappings with versions | Finite slots or a bounded timeline are declared modeling restrictions, never evidence that excluded events did not occur. |
| Source obligations | Every in-scope observation/narrative obligation, applicability decision, dependent query and disposition | Unmapped, disputed, unsupported and not-yet-inspected content remains visible. An unexplained disposition prevents scope adequacy. |
| Query and budget | Requested layer, outputs, views/composition, scenario drivers and horizon, resolution, explicit resource ceilings, traversal policy and continuation reference | Omitted budget or view composition is a request error. Zero budget is valid; it is not an empty family. |

A template proposal must name its origin (source-supported, supplied assumption
or candidate requiring review), applicability conditions, economic state and event
effects, observation mappings, and accounting rules if it requests journals.
Each admitted constraint points to its exact support or selected assumption.
Unsupported accounting treatment is retained as an unresolved proposal with its
reason; it does not become an admissible treatment branch. Conversely, supported
reported-value arithmetic can proceed without claiming that a journal exists.

The output identifies its **target layer**. A conditional reported-value family
can be defined while the accounting-history family is unresolved. Calling both
simply “feasible” would conceal a different target. Any unresolved obligation
that can change membership in the requested family prevents an unconditional
admissibility claim, even if the currently enforced subset has a witness.

## H2. Joint trajectories, views and identity

Let h contain the chosen interpretations, dated economic states, events and,
where admitted, journals and balances. Within declared scope M and immutable
view v, define F(M,v) as the set of h satisfying all admitted opening,
transition, context-mapping and observation constraints jointly, conditional
on the listed assumptions. A missing required constraint leaves a partial
formulation; the implementation must retain the obligation and label witnesses
of the relaxed formulation as candidates, not validated members of the target.

Shared economic IDs link contracts across periods and accounts. Observation
IDs identify assertions; they are not substitute contract IDs. Two assertions
about the same balance constrain one shared variable after context alignment.
A bridge connects successive states using the same events. For example, the
synthetic opening 100 plus an event amount 20 implies closing 120. A candidate
closing 110 fails that bridge even if 110 appears elsewhere as a possible total.
This small identity assumes no omitted flows or valuation effects; actual
bridges require the accounting and domain contracts.

For the principal example, let nonnegative amounts x and y denote two components
of one reported total in synthetic USD. The disclosure condition is x+y=100.
The marginal ranges are each [0,100], but x=y=100 is impossible because its sum
is 200. Projection onto x may return [0,100], retaining the parent-family ID and
an extension obligation: any downstream use must find a y satisfying the same
family. Joining independent marginal ranges discards that obligation.

A named view is a predicate on the parent family, not another independent
history. Write A={h in F: x>=40} and B={h in F: x<=60}. Their intersection has
40<=x<=60 and y=100-x; their union is F. The overlap is not counted twice.
A request with several view IDs must say union or intersection. Views can also
leave parts of F uncovered. They provide no probability weights. Composition
across different family/view versions returns `FAMILY_CONTEXT_MISMATCH` unless
an explicit versioned alignment transformation proves the intended relation.

Family representation identity includes the full immutable semantic manifest:
view/review versions and candidate membership, scope, variables/domains,
constraints/support, selected assumptions, template/mapping versions and
resolution. Changing those fields creates a new family version. Merely changing
a search budget or traversal does not. A query has its own identity including
the family version, requested outputs, composition, layer, scenarios and horizon.

An individual witness identifies its family, complete assignments and dated
trajectory, interpretation choices and provenance. Two labels attached to the
same assignment do not create two witnesses. Different provenance manifests can
represent equal economic trajectories without sharing representation identity;
economic equivalence needs a stated comparison domain and argument. No solver
normal form or content hash proves that equivalence. A symbolic region is not
one witness and cannot be assigned one vote in a distribution.

For E05, an explicit conditional selector k in {A,B} gives
(k=A and revenue=120) or (k=B and revenue=110), with cash=40. These are assumptions
about which conflicting source to use, not evidence of a source's correctness.
The unconditioned reported-value response remains unresolved with both values;
the ratios conditional on A and B are 3 and 11/4. The target is not
revenue=120 and revenue=110. Choosing that conjunction would compute an empty
set for a different question. Missing treatment authority blocks journals in
both branches. Unknown source eligibility also propagates; constructing a
conditional branch cannot bypass time admission. E05 still lacks a qualifying
real-source conflict; this example does not repair that source gap.

## H3. Construction, search and continuation

The proposed interfaces are staged so that each decision has an accountable
input and an inspectable output. They do not select a solver or implement it.

| Operation | Input | Output and stopping rule |
| --- | --- | --- |
| ProposeCandidates | Reviewed view, opening state, scope and versioned template registry | Candidate instances, applicability reasons, exclusions and source-obligation dispositions. No arbitrary-disclosure discovery claim. |
| AdmitConstraints | Candidate instances plus category-specific evidence/assumption/treatment decisions | Supported constraints with origin IDs, rejected proposals with reasons, unresolved obligations and target-layer completeness. Stop target-dependent admission on missing authority. |
| BuildFamily | Admitted constraints, domains and full dependency manifest | Family formula/representation, shared symbol map, search partition specification, unresolved formulation obligations. Reject duplicate/conflicting IDs, missing context or undeclared symbols. |
| ValidateWitness | Family version and full candidate assignment/trajectory | Satisfied constraints with checked support, violated constraints, unsupported checks or missing fields. Valid only when every required target constraint is checked. |
| SearchFamily | Family version, explicit budget, capabilities, traversal and optional receipt | Evidence about regions, witnesses, infeasibility reasons/proofs, unresolved regions and a continuation receipt. A resource stop preserves the original formula. |
| QueryFamily | Family plus requested view/projection/scenario/resolution | Set/region or conditional results with completeness and dependency status. Bounds from explored regions are labelled explored-only. |

Source obligations use `mapped`, `not_applicable_with_reason`, `out_of_scope`,
`disputed` or `unresolved`. `Mapped` requires the actual constraint/support IDs;
several assertions can support one constraint without double-counting evidence.
`Not applicable` requires a reason and review version, not just a count.
Out-of-scope disclosures remain on the coverage report and wider mission queue.
A source count equal to a constraint count establishes none of these relations.
P17 must supply domain-specific candidate generation and applicability methods.

Search may partition a family into reproducible decision cells. Each cell
retains the original family formula AND its decision assignment/predicate.
A declared finite choice needs an explicit domain; continuous quantities remain
regions. The partition manifest states why its cells are exhaustive and
nonoverlapping. Named views are not automatically cells. If the backend cannot
establish a partition, retain the original region as unresolved instead of
inventing a finite-universe completeness claim.

For the examples, a cell key is the tuple (partition-version, decision-ID,
value-ID), or a sorted tuple of these assignments for several decisions. Decision
and value IDs come from the immutable manifest, never array positions or
traversal order. The retained key and manifest uniquely reconstruct the cell;
a digest can index them. General byte encoding belongs to language/IR. A search
receipt records the exact manifest, explicit traversal order, examined keys,
unvisited keys or a reconstructible range predicate, formulas, resource use,
backend/version and unresolved reasons. Ordinal suffixes are valid only with
the pinned ordering/domain manifest; changing order cannot reuse an old suffix.

A cell has one of three coverage dispositions: represented feasible region with
validated witness or another supported existence argument; proved infeasible
with checked contradiction/proof and scope; unresolved, retaining the region
and reason (`unvisited`, `unknown`, `unsupported`, `interrupted`, `cancelled`).
A feasible continuous region is preserved symbolically: one sample never
exhausts its points. “Every declared cell decided” means the whole family is
represented within M, not that every history was enumerated. All-cell
infeasibility proves emptiness only for the complete admitted formulation and
an exhaustive partition. Unsupported required operations or unresolved source
obligations veto that stronger conclusion.

The response therefore reports three independent fields: `existence` (witness,
proved_empty, unknown); `declared_search` (complete, partial, not_started);
`economic_scope` (supported_for_declared_scope, unresolved, explicitly_limited).
A scope may be explicitly limited even when search is complete. A partial
formulation also reports `formulation_complete=false`; its candidates do not
set target `existence=witness`. These statuses are scoped to the requested layer.
No value of these fields alone certifies whole-company coverage.

Resume requires exact semantic-manifest and partition identity. A changed
budget can continue unresolved cells. Changed evidence, assumptions, domains,
rules or partition create a new request and prevent blind continuation. Preserve
already committed partial work on cancellation; if a cell's result was not
committed, leave that whole cell unresolved. A zero-budget request returns the
entire original region unresolved and no proof of emptiness. No new solver is
required to specify this behavior.

## H4. Economic memory, grouping and refinement

A historical accounting balance does not describe all future contractual cash
flows. A principal of 100 with a fixed rate of 5% and a principal of 100 whose
floating rate was 5% can produce the same stipulated historical interest of 5.
If the next full-year rate is 7%, future interest is respectively 5 and 7. A
principal due next year and one due a year later can likewise have identical
current balances but different principal repayments within a one-year query.
The histories must retain rate/reset terms and maturity even when their
historical postings happen to agree. The example establishes arithmetic under
specified simple-interest assumptions, not a recognition or valuation method.

Required state is determined by requested scenarios, horizon and outputs plus
the applicable domain methods. It includes legal entity/perimeter, ownership and
rights, contract/lot/cohort identities, currency, principal/units, recognition
and measurement basis where applicable, rates/resets, schedules/maturities,
options/guarantees/collateral and linked dependencies whenever those affect the
query. “Unknown” is a value status requiring preservation; absence of a field
cannot silently mean no guarantee or no option. Later banks, insurance, groups,
FX, securities and cross-standard methods must extend these state requirements;
a scalar balance schema is not a whole-product substitute.

A grouping request names constituents, transformation/version, retained detail,
scenario domain, horizon, outputs, rules and exact/approximate claim. An exact
certificate must show that aggregation G commutes with every admitted transition
T for that domain, G(T(s,u))=T_group(G(s),u), and that requested outputs satisfy
O(s)=O_group(G(s)). These are proof obligations, not general facts about
financial balances. Missing proof/evaluation returns `GROUPING_UNSUPPORTED`;
it leaves detailed histories available and cannot delete them. A certificate is
part of query/resolution identity, with constituent and rule versions.

For the deliberately narrow simple-interest fixture, two principals 40 and 60
share entity, currency, a fixed 1/20 annual rate, a common day-count convention,
no intermediate principal change, and maturities after the half-year horizon.
Only total principal and interest are requested. Individual interest is
40*(1/20)*(1/2)+60*(1/20)*(1/2)=1+3/2=5/2. Grouping gives
(40+60)*(1/20)*(1/2)=5/2 by distributivity. Principal remains 100 under both
representations; any stipulated interest-payment cash transition subtracts the
same 5/2. This proves the named aggregate outputs/transitions for those
assumptions, not contract-level cash flows or other accounting measurements.
Constituent records remain linked so a later query can refine the group.

A changed output (individual contract exposure), rate/reset/maturity/guarantee
assumption, rule or horizon requires a new sufficiency decision. Reusing the old
certificate returns `RESOLUTION_REVALIDATION_REQUIRED`. Refinement produces a
new resolution version linked to its parent and constituent detail; if the
required detail was never preserved, return `DETAIL_UNAVAILABLE`, not fabricated
lots or contracts. Refinement can restore represented detail, not recover facts
that were never known.

Approximation is a distinct, optional future claim. Its record must name each
output, unit, scenario/horizon domain, absolute/relative tolerance, justification,
error argument or evaluation evidence, and exact-detail fallback. No tolerance,
empirical error bound or approximate grouping is approved by this contract.
Changing the query invalidates the approximation's applicability. Counts of
similar contracts and similarity of old postings are insufficient evidence.

## H5. Revisions, errors and layer interactions

Current eligibility depends on the candidate population as well as selected
assertions. Adding a competing source to an unchanged selection key creates a
new membership revision and invalidates affected family/query descendants.
Changed interpretation review, assumptions, template applicability, opening state
or treatment rules similarly changes the relevant semantic manifest. An old
result remains readable under its frozen view with a historical label. It must
not be relabelled current. Reuse requires a complete dependency comparison or an
explicitly supported independence argument; missing dependency information
means reuse is unestablished. An unrelated cash-only family can be reusable
while a revenue family is invalidated, subject to the same time/cutoff checks.

| Outcome | Required payload and consequence |
| --- | --- |
| `REQUEST_INVALID` / `CONTEXT_INCOMPLETE` | Missing fields, duplicate IDs or ambiguous composition with record locations; no admitted family is fabricated. |
| `CONSTRAINT_VIOLATION` | Candidate, failed original constraint and arithmetic/logic; candidate rejection is not family emptiness. |
| `PROVED_INFEASIBLE` | Complete target/formula, region, supported exhaustive scope and checked contradiction/proof; no conclusions about out-of-scope real histories. |
| `UNKNOWN` | Undecided formula and reason, even if no witness was returned. |
| `OPERATION_UNSUPPORTED` / `TREATMENT_UNSUPPORTED` | Exact operation or missing authority, affected target and retained formula/proposal; unsupported does not mean false. |
| `BUDGET_EXHAUSTED` / `CANCELLED` | Committed region results, all unresolved cells/regions and continuation receipt; partial valid witnesses survive. |
| `STALE_CONTINUATION` / `STALE_VIEW` | Expected and supplied immutable versions; require a new request or explicit frozen access, with no mutation of historical records. |
| `RESOLUTION_REVALIDATION_REQUIRED` | Changed query/rule/dependency fields and retained constituents; no use of an inapplicable certificate. |

These names specify distinctions for this contract. The later failure contract
must reconcile a common encoding with evidence/time/E05; this is not a claim
that a production exception hierarchy exists. A per-region outcome and a
request termination reason may coexist. For example, one feasible cell and
cancellation leave a partial family, not a cancelled mathematical truth.

| Neighbor | History-family input or output | Responsibility remaining outside this contract |
| --- | --- | --- |
| Evidence/time | Consume `SelectedEvidenceView`, contextual predicates, conflicts, membership revisions and unresolved eligibility; return dependency/obligation IDs | Complete source support and exact temporal admission belong to evidence v3/time v2. History construction cannot relax them. |
| Uncertainty | Consume category-labelled admission/selected assumptions; return joint family, conditional branch IDs and unresolved regions | Specify narrowing, elections, estimates, revisions and defensible joint measures. No equal weights or normalization over successful cells by default. |
| Accounting | Consume dated rule applicability, treatment constraints and opening/event bridges; return economic/history candidates plus unsupported obligations | Establish authority, recognition, measurement, journals and statements. Reported-value or economic feasibility cannot imply compliant accounting. |
| Language/IR | Supply shared identities, complete contexts, typed predicates, region/proof/status and source-location requirements | Define portable encoding, parser/typed authoring semantics, numerical capability and migration; symbolic prose is not an implemented IR. |
| Persistence | Supply immutable manifests, witness/region IDs, continuation receipts and dependency edges including membership | Define atomic commits, stale-write handling and reverse invalidation. Failed persistence cannot silently mark an unfinished cell complete. |
| Interfaces | Supply query layer, view composition, assumptions, scope/exclusions, coverage and unresolved outputs | Display those distinctions and allow conditional/frozen queries; avoid a single “complete” badge. |
| Failure semantics | Supply the outcome distinctions above with causal IDs and partial results | Harmonize names, retryability and recovery behavior without conflating mathematical and operational failures. |

## H6. Matched alternatives and proposed choices

Hold the same synthetic inputs x>=0, y>=0, x+y=100 and the same requested
outputs fixed: the joint feasible set, membership of (50,50) and (100,100),
and the A/B views from H2. A joint symbolic representation retains the line
segment, includes (50,50), rejects (100,100), and expresses overlap directly.
It is proposed because it preserves these meanings. Merely writing a formula
does not prove that construction captured all disclosures or that a backend can
solve it. An unsupported query still has to return its original region.

Explicit finite history enumeration is exact for an explicitly finite universe.
For example, if a separately justified scope limits x to {40,70}, enumerating
(40,60) and (70,30) represents that narrower family exactly. Under the original
continuous inputs, listing endpoints (0,100) and (100,0) alone misses (50,50).
An honest enumerator must report those as witnesses and leave the remainder
unresolved; it cannot change the input domain merely to report completeness.
Finite enumeration remains a suitable implementation candidate for genuinely
finite subproblems, with the same joint constraints and source obligations.

Independent account intervals [0,100] and [0,100] answer marginal questions, but
their Cartesian product admits (100,100). Using that product as the joint family
is wrong relative to the specified target. Retaining the linking equation with
the intervals repairs it, making them a presentation of the joint constraint
rather than an independent reconstruction. The proposed representation may
therefore expose intervals as summaries with their parent relation preserved.
No speed, usability or stochastic ranking is inferred from these examples.

| Choice and status | Provenance and justification | Failure mode and smallest diagnostic |
| --- | --- | --- |
| Joint constraints, proposed semantic requirement | MC08 and P15 audit; H2 proves the dependence counterexample | Independent marginal combination; HF01/HF02 reject it. |
| Region plus search evidence, proposed interface | MC09; historical P04 illustrates but does not authorize the design | Witness promoted to completeness; HF04/HF06/HF07 distinguish them. |
| Explicit scope/obligation report, proposed interface | G1/P15; supplied templates cannot discover omitted events | Complete cell count hides exclusions; HF05/HF09 preserve them. |
| Stable manifest and cell keys, proposed engineering choice | MC25 reproducibility; semantic keys survive traversal changes | Order-dependent replay; HF07/HF15 reject mismatched continuation. Byte encoding remains IR work. |
| Exact rational small examples, fixture convenience | Deliberately stipulated numbers make algebra independently checkable | Mistaken universal decimal/solver policy; HF04 preserves strict endpoints, accounting/numerics remain open. |
| Finite example decisions and cell budgets, fixture convenience | Two branches expose interruption with a tiny example | Whole-company or continuous completeness inferred from counts; H3 requires preserved regions and scope. |
| Query-dependent grouping, proposed interface | MC11/G16; H4 derives a narrow positive case and counterexamples | Same postings mistaken for same exposure; HF10–HF12 require detail/revalidation. |

Z3, Python, rational arithmetic, Boolean truth-cell expansion, slot limits,
traversal order, storage and compression are not chosen as whole-product defaults.
Historical `reconstruction-profile-v1.md` and `reconstruction_v1.py` (construction
and grouping functions) are bounded prototype evidence. P03's authored debt
lowering likewise does not establish disclosure-to-template discovery. The
current contract's arguments are the explicit set and arithmetic derivations
above; no uninspected paper or accounting authority is invoked.

## H7. Completion and remaining decisions

The companion fixtures cover joint dependence, contexts, source conflict,
continuous regions, scope, honest failure/search, economic memory, grouping,
revision invalidation and frozen access. Their algebra and file consistency can
be checked without building a product module. They do not establish semantic
completeness of this specification; that requires independent result review.

P15-E09 (partial outcomes), E11 (numerical capabilities), E12 (economic memory),
E13 (scenarios/weights), and E05 (layered review) now have concrete proposed
history-family consequences. They remain open pending counterpart contracts and
review. All fourteen P15 decisions and all MC01–MC35/G1–G18 obligations remain
active. In particular, sufficient state for every sector, source-grounded
candidate generation, dated accounting permissions, general grouping proofs,
and probability/calibration methods belong to further P16/P17 work. This slice
does not select the initial product profile or dependency order.

The stop condition is saved H1–H7, specified fixtures, architecture registration,
actual local/registered-check records, and explicit residuals. The next task is
a separately reviewed uncertainty contract. Pending E05/history-family bounded
result review and expected whole-architecture check failure do not prevent that
planning or authorised independent drafting. Full independent P16 result review
remains required before phase acceptance.

FILE docs/design/proposal/architecture/uncertainty-contract-v1.md
# Integrated uncertainty operations — proposed contract v1

This specification completes the operation layer above uncertainty admission,
joint-measure attachment and history-family construction. It addresses MC08–MC14,
MC18, MC25, MC27 and MC33–MC35, principally G1, G6, G15 and G16. Its finite examples
are authored assumptions. They establish neither company probabilities nor an
accounting treatment. Product implementation and independent acceptance remain
pending. The initial profile and all fourteen P15 decisions remain open.

## 1. Question, evidence and default audit

Can a retained family support conditioning, new evidence and conditional outcomes
without invented weights, repeated information or discarded unresolved regions?
The baseline is the proposed admission U1–U6, attachment v2 A–F and history H1–H7
contracts. Core 0's uncertainty section and chapter 5's finite-model derivation
are mathematical design evidence, not approved product behavior. This document
extends their operation semantics; earlier supplements' deferrals describe their
historical scope. Their unchanged records and failure examples remain applicable.

The pass criterion for this bounded task is a coherent specified exchange and
independently recomputable finite examples, with preserved identities and failure
receipts. Invalid arithmetic, lost dependencies or contradictory state assertions
veto this document's internal check and trigger repair. Missing empirical support
vetoes an empirical claim, not continued specification. Checker counts and example
coverage are explanatory only. No stochastic experiment or architecture ranking
is performed. Results are retained in uncertainty-fixtures-v1.json and the P16
result note with fresh check records. Stop after this group; accounting is next.

| Choice and provenance | Reason; misleading failure | Early diagnostic; status |
| --- | --- | --- |
| Optional law, MC12 and attachment B | Facts and feasible alternatives need not have weights; uniform branch weights would invent information. | Unweighted fixture forbids aggregate mean/quantile; proposed invariant. |
| Immutable linked records, evidence/time/history contracts | Corrections must preserve earlier answers; pointer substitution would leak later evidence. | Parent hashes and explicit cutoff checks; provisional representation choice. |
| Exact finite rational examples, approved plan | Independently check normalization; finite success could be mistaken for continuous inference. | Fractions recomputation plus unsupported point-conditioning example; fixture convenience only. |
| Observation blocks, chapter 5 and extraction identity rules | Capture reused information; different files or IDs could disguise one observation. | Repetition, components, alternative extraction and correction examples; proposed invariant. |
| Dependence declared, never inferred from absence of links | Multiplying factors requires a conditional model; unjustified independence overstates information. | Unknown overlap rejects independent multiplication; proposed invariant. |
| Preserve every requested region, history H4 and chapter 5 | Solver failure is not an economic outcome; successful-only means would change the question. | Partial mass and explicit completion-condition examples; proposed invariant. |

Skeptical audit: the comparison fixes semantic inputs; neither prior prototypes,
branch counts nor execution success define the baseline or promotion rule. There
is no runtime/environment comparison. Continuous inference and causal evaluation
remain explicit capability limits, not evidence against those research directions.

## 2. Exchange, identities and validation

An immutable `UncertaintyRequest` has `request_id`, `version`, `predecessor`,
`operation`, `family_ref`, `view_ref`, `attachment_ref` (explicit null if absent),
`model_ref` (explicit null if unweighted), `time_ref`, `evidence_view_ref`,
`admission_ref`, `purpose`, `information_cutoff`, `evidence_cutoff`, `query`,
`dependencies` and `provenance`. References bind exact `id@version` records;
payload changes require a new version or identity. Time mode, publication and
byte-vintage eligibility follow T1–T3; a new observation can produce a later
view only with an explicit new time/admission record. Frozen earlier views remain
queryable. Source occurrence, semantic assertion, interpretation, observation
block and likelihood factor have separate identities.

The query declares the operation-specific condition, evidence update or outcome
selection, including scenario/path/date and typed quantities. Dependencies include
the transitive closure of all typed record references, including assumptions,
review selection, law, accounting method and source lineage. An empty selection
never means all. Outcome labels such as `a` are domain members, not record keys.
The fixture registry is self-contained: it instantiates this exchange without
silently importing the predecessor fixtures' registry. File references pin source
contracts by SHA-256; they do not count as observation blocks.

`UncertaintyResult` retains request identity, old/proposed view, disposition,
reason codes, support and preserved records, unresolved obligations, future
dependencies, `family_effect`, payload, and separate statuses:

* `structural_validity`: valid/invalid;
* `mathematical_status`: satisfied/failed/undefined/unresolved;
* `empirical_justification`: stipulated/not_established/supported_for_named_scope;
* `capability_status`: specified_only_no_runtime/unsupported;
* `computation_status`: specified_exact/specified_partial/symbolic/not_computed.

Fixture computations are expected outputs, never runtime success claims.
Accounting validity and human acceptance are separate fields, neither inferred
from mathematical status. Successful derivation creates a candidate child view;
it preserves the parent and changes no active view pointer. Admission/selection
is a separate explicit operation. Rejection stores submitted bytes and a receipt
but creates no child view, posterior, aggregate result or partial domain write.
`state_before` and `state_after` name the same selected family/view/attachment
and parent hashes on rejection. Receipt storage itself is not a domain update.
Retrying identical request bytes returns the same logical receipt; a reused
identity with different bytes fails `IDENTITY_CONFLICT`. Actual atomic storage,
crash recovery and concurrency are obligations for the later persistence contract.

| Validation stage | Invalid or unresolved condition | Disposition and consequence |
| --- | --- | --- |
| Envelope/registry | Missing field, scalar where reference array required, identity collision, unresolved reference | REQUEST_INVALID; record exact field/reference and preserve submission. |
| Binding/admission | Wrong family/view/model, event outside domain, incompatible unit/purpose, missing dependency, inadmissible cutoff | REQUEST_INVALID; no substitution of nearest/newest record. |
| Law/event | Missing masses, negative/nonfinite mass, nonunit total, unresolved measurability | Invalid laws fail mathematics; unresolved obligations remain symbolic; no computed probability. |
| Evidence reuse | Repeated information, unmodeled overlap, correction applied atop superseded evidence | REQUEST_INVALID with the specific reuse code; old law retained. |
| Normalization | Zero denominator/normalizer | UNDEFINED; undefined mathematics, no posterior. |
| Capability | No admitted law, unavailable evaluator, continuous point without conditional model | UNSUPPORTED or RETAINED_SYMBOLIC; preserve feasible family and expressions. |
| Outcome coverage | Unsupported method, numerical failure, unexplored domain | PARTIAL; retain region and mass/unknown mass, never silently condition on completion. |

These stages reuse the saved attachment/malformed supplements. Error lists are
ordered by stage then record key; later numerical evaluation does not run after
an earlier invalid prerequisite. Preserve all unresolved references in receipts.

## 3. Conditioning and scenarios

An observational condition names an admitted event A, the parent law P, the
information used to define A and its role. For finite elementary outcomes S,
require a measurable A subset of S and P(A)>0. Define

    P_A(s) = P(s) 1{s in A} / P(A),
    P(B | A) = sum_{s in A intersect B} P(s) / P(A).

The numerator sums elementary outcomes once even when display labels overlap.
The child retains S and records zero mass outside A, the event identity,
denominator and parent law. Keeping zero-mass members distinguishes the declared
domain from its positive-mass support. Reapplying A is mathematically idempotent;
it records no new information factor. If A came from observation block D, the
child's consumed-information set includes D and its semantic lineage, preventing
subsequent likelihood multiplication by the same information. A hard constraint
already used to construct the family is likewise consumed, even if it did not
appear as a numerical likelihood. Evidence used to fit a prior/model is declared
in that model's training/calibration lineage for the same check.

With masses a=1/2, b=1/3, c=1/6, A={a,b}, B={b,c}, the denominator is 5/6,
intersection mass is 1/3, and P(B|A)=2/5. The conditional masses are (3/5,2/5,0).
P(A)=0 returns `ZERO_CONDITION_MASS` and no child; an empty feasible subset in
an unweighted family is instead scoped infeasibility. An unweighted nonempty
restriction yields a feasible subset with `probability=null`, not a distribution.

An exogenous stress changes a declared driver/scenario while retaining history
weights unless an explicit observation model says that observing the scenario
provides information. Its result is labeled scenario-assumed, not P(.|observed
scenario). A structural intervention requires a causal model, modified equations,
intervened variables and an identification/validation argument; `do(X=x)` is
never lowered to filtering `X=x`. This proposal retains such requests as
unsupported until a declared evaluator and its evidence are supplied in P17.

For continuous/mixed laws, event conditioning uses the same measure formula when
the event has positive mass and the evaluator is supported. A continuous point
event of zero mass requires an explicit regular conditional kernel/version (or
justified reduced parameterization) with the conditioning variable, base measure,
support and chosen version at the queried point. A density value is not the
probability of that point. No epsilon window or Gaussian penalty is invented.
General existence, uniqueness at null points and numerical evaluation remain
method obligations; symbolic expressions may be retained without a numeric answer.

## 4. Evidence updates and information reuse

An `ObservationBlock` records its immutable identity, purpose, observed values and
full financial context, source occurrences and assertion/reading references,
`information_atoms`, relations (`same_information`, `component_of`, `derived_from`,
`supersedes`), availability/time view, admission and dependencies. Information atoms
name semantic observations, not bytes: a duplicated PDF, a new extraction or a
repeated table entry does not automatically supply new information. Where semantic
equivalence cannot be decided, overlap is `unknown`; new IDs alone cannot prove
independence. No general automatic duplicate detector is claimed.

A `LikelihoodModel` records target family/coordinates, law purpose, observation
block(s), base measure for observed data, conditional arguments, parameter version,
units, support, consumed information and justification. Its output is a
nonnegative measurable L(s). For discrete observations L is a probability of the
specified observation; for continuous observations it can be a density and may
exceed one. Extraction confidence, expert preference and solver success are not
likelihoods. A finite update requires finite nonnegative values on all S and

    Z = sum_s P(s)L(s) > 0;    P_new(s) = P(s)L(s)/Z.

The result records unnormalized masses, Z, the complete posterior including zeros,
new consumed-information set and parent view. With P=(1/2,1/3,1/6) and
L=(1/2,1,0), unnormalized masses are (1/4,1/3,0), Z=7/12 and posterior
(3/7,4/7,0). If Z=0, return `ZERO_NORMALIZER`; do not substitute equal weights or
silently broaden support. A later observation inconsistent with every positive-mass
history calls for an explicit model/family revision, not an invisible numerical fix.

Two observation blocks can enter one joint likelihood L(D1,D2|s). Sequential
updating must use L(D2|D1,s); replacing this by L(D2|s) requires an explicit
conditional-independence assumption with target-specific justification. Different
information atoms are necessary bookkeeping, not a proof of independence. A
dependent conditional model may legitimately reuse D1 as a conditioning argument;
it must name D1 as already consumed and add only D2 as incremental information.
Unknown dependence blocks the independent-factor route while retaining the blocks
for a later joint model. Marginal likelihood tables alone do not define the joint
likelihood.

| Submission | Required result |
| --- | --- |
| Same immutable request/bytes | Idempotent receipt lookup, no second child or factor. |
| New request, same source occurrence/information block | `DUPLICATE_INFORMATION`; preserve prior posterior. |
| Total plus all its components as independent factors | `DERIVED_INFORMATION_REUSE`; one joint block or an explicit conditional model is required. A deterministic total adds no independent information beyond all components. |
| Alternative extraction of one source span | `ALTERNATE_READING_NOT_NEW_OBSERVATION`; resolve/branch the reading under admission U rules. A new noisy measurement model must be explicitly justified if intended. |
| Potentially overlapping blocks with unknown relation | `DEPENDENCE_UNRESOLVED`; no independent update. |
| Corrected reading multiplied into an old posterior | `CORRECTION_REQUIRES_REBASE`; retract/supersede in a new evidence view and recompute from a retained base preceding the affected block. |

A correction supplies the superseded block, corrected block, base view and the
ordered retained incremental updates to replay. Validate that none of the old
block's descendants survives without revalidation. Recompute from the base with
the corrected likelihood and any still-admissible downstream conditional factors.
Do not divide by the old likelihood: it may be zero and its support restriction
may already have removed alternatives. The old posterior, evidence view and
receipt remain unchanged. The illustrative corrected L=(1,1/2,1) on the original
P gives Z=5/6 and (3/5,1/5,1/5). This is a newly specified view, not historical
knowledge rewritten in place. Full crash-safe replay is a persistence obligation.

## 5. Conditional outcome payloads

A query selects exact family/view, condition, scenario, path set, dates, accounting
methods and output quantities. Each row key is `(history_ref, condition_ref,
scenario_ref, path_ref, date)`. Cells carry entity/perimeter, concept, dimensions,
currency/unit/scale/sign, instant or interval and measurement basis, together with
state/journal/report references, assumptions and dependencies. A joint statement
vector shares its path and state references; marginals from incompatible histories
cannot be recombined into a synthetic balance sheet. Expected statements need not
describe any admissible history and remain summaries, not journal postings.

Cell status is `exact`, `symbolic`, `sampled`, `certified_bound`, `explored_range`
or `unresolved`. Exact means exact under the declared model and inputs. Sampled
requires sampler/seed/stream, weighting and uncertainty metadata; it is not exact.
Certified bounds require a cited proof/certificate, domain and endpoint semantics;
explored ranges describe only visited regions. Symbolic values retain expression,
domain and unresolved dependencies. No computational tag asserts accounting
eligibility or empirical forecast validity.

For weighted finite reporting, allocate every elementary outcome once to a
disjoint partition `completed`, `unsupported`, `numerical_failure`,
`solver_unknown`, `cancelled` or `unexplored`. Coverage masses total one (or the
explicit parent event mass for an unnormalized subquery); unknown mass stays
unknown and prevents a false exact total. Economic default is an economic-state
flag orthogonal to this partition: a fully computed default belongs to completed;
an unsupported default branch can remain unresolved. Report default mass separately
with its overlap with completion so it is never added twice. Default retains legal
obligations and usable state. Stop only affected descendants when a required method
is unsupported, retaining independent quantities through their dependencies.

Suppose a,b have exact expense 10,20 and c's valuation is unsupported. Under
P=(1/2,1/3,1/6), completed mass is 5/6, unresolved mass 1/6 and the completed
unnormalized contribution is 35/3. The unconditional mean and quantiles are
unresolved; 35/3 is not the mean of the full outcome. A separately requested
`condition_on_completion` query reports event {a,b}, denominator 5/6 and mean 14.
Its labels state that this is a computational selection, not an economic forecast
condition or evidence update. This view cannot silently feed back into historical
probabilities. Partial values may support bounds only with explicit bounds for
the missing region; a missing value is neither zero nor default.

When history weights are absent, retain the feasible set and separate within-history
future laws K(h,scenario) if available. No uniform averaging across histories.
Without a within-history law retain a deterministic/symbolic feasible outcome set.
A complete finite set {10,20,30} has exact range [10,30] but no mean or quantile.
If only {10,20} was explored and c is unresolved, [10,20] is merely an explored
range and cannot become a full-family bound. Even when every K is valid, an
envelope of their quantiles is not a predictive distribution. An optional history
law plus a measurable kernel defines a mixture; discrete reporting sums disjoint
history/innovation atoms, and continuous mixtures require a supported integrator.

## 6. Interactions, alternatives and acceptance boundary

Evidence supplies contextual assertions and observation lineage; time determines
admissible information; admission separates the six uncertainty categories. History
families supply compatible joint states, scope, residual regions and refinement
maps. Accounting consumes a history/scenario/path and returns typed states and
journals with eligibility status; uncertainty never makes an unsupported treatment
admissible by giving it positive probability. Language/IR must type conditions,
measures, units, model purpose and requested aggregation; implicit casts from sets
to distributions are forbidden. Interfaces expose denominators, unresolved mass,
view lineage and evidence reuse receipts. Persistence retains immutable requests,
models and child derivations with resumable frontiers; failure semantics propagate
dependency-scoped unknowns. These are requirements on unfinished counterpart
contracts, not evidence that they are complete.

The two credible storage alternatives are a law linked to a family registry and
a self-contained joint model carrying its definitions. Compare them with identical
S, typed assignments, masses, evidence blocks, cutoffs, parent lineage and queries.
Under a bijection f of elementary outcomes require equal assignments and
P_embedded(x)=P_linked(f(x)); also preserve event sets, likelihood values and consumed
information. Finite conditioning and normalization then have equal sums by a change
of index. Registry links simplify shared revisions but require dependency closure;
self-contained packages simplify portable inspection but risk copied evidence being
counted twice. Both must retain semantic observation identities. A paired fixture
specifies the same conditional and posterior values in both forms; no throughput,
memory, empirical or general continuous-equivalence conclusion follows.

The provisional preference is explicit immutable shared identities with a
self-contained export containing the same identities and definitions. It follows
from traceable revisions and reuse, not from prototype convenience. Ownership and
initial-profile selection remain open. Weighted and unweighted reporting answer
different questions and are not competing estimators to rank on these examples.
Single joint likelihood and conditional sequential factorization are both credible
when their models match; naive multiplication is valid only under the stated
conditional independence. Correction by replay is chosen over division because
zero likelihoods make division lose recoverable histories.

This group is ready for independent substantive review when the full exchange,
fixtures and internal arithmetic/reference checks agree. Its finite capability
boundary is specified; continuous/mixed inference, causal identification,
calibration and empirical validation remain P17 obligations. Accounting, language,
persistence, interfaces, failure semantics, integrated profile/acceptance order,
E05 source conflict and full MC01–MC35/G1–G18 reconciliation remain open. Neither a
successful checker nor this candidate contract enables product implementation.

FILE docs/design/proposal/architecture/uncertainty-admission-contract-v1.md
# Uncertainty admission and revision v1 — partial proposal

A company may have reported an amount without disclosing its composition. An
analyst may also be uncertain about what a note means, which accounting treatment
is permitted, or how management will respond to a future event. These questions
require different evidence and different ways of changing an answer. This
contract specifies those distinctions before attaching any probability model.
It addresses MC10/G15 and the MC04/MC08/MC12/MC14/MC18/MC25/MC27 interfaces.
The complete uncertainty contract still needs joint measures, conditioning,
probability updates and conditional future outcome payloads.

## U1. Inputs, retained records and admission results

An `AdmissionRequest` contains an immutable proposed record, an operation,
a base-view version and a requested layer. Its shared header is:

| Field | Required meaning |
| --- | --- |
| `record_id`, `version`, `predecessor` | Stable logical identity, immutable version and explicit predecessor or null. Reusing an existing version with different content is invalid. A predecessor alone does not authorise supersession. |
| `category`, `payload_version` | One of the six categories below and the version of that category's payload rules. Unknown categories or payload versions remain preserved but unsupported. |
| `context` | Entity, perimeter/version, concept/mapping, dimensions, instant or reporting interval, calendar/version, currency, unit, scale, sign and measurement basis, with explicit unknown/not-applicable values. Numeric rounding follows E3; missing values never imply a global default. |
| `evidence_view`, `review_snapshot`, `time_view` | Exact immutable manifests; the time view includes admission mode, selection, cutoffs, calendars and byte-vintage evidence as required by T1–T3. |
| `scope` | Family ID/version, named branches or explicit all-branches selection, and candidate-selection key/version. Empty branch lists do not silently mean all. |
| `provenance` | Source occurrence/reading versions, derivations or authored assumptions, author, rationale and review-event references. Synthetic support is labelled synthetic. |
| `dependencies` | Exact typed/versioned dependencies, including applicability, information permissions, assumptions and selection membership. An empty list is explicit and still subject to category-required references. |
| `operation`, `requested_layer` | Operation from U3; evidence reading, reported-value, economic-history, accounting-history, decision-input or future-domain layer. Unsupported layer/category combinations return a reason. |

The category payload adds the substantive proposition or policy, not just a tag.
An operation event records its ID, author, rationale, proposed predecessor,
base view, selection changes and intended successor. Submitting an assertion
preserves it even when its interpretation or treatment cannot be admitted.
Invalid structured requests retain their submitted envelope and validation
errors for repair; they do not become valid semantic records.

An `AdmissionResult` contains request/record IDs, the old and proposed new view,
`disposition`, reason codes, requested layer, an admitted predicate or selected
assumption (null when neither is admitted), exact support references, unresolved
obligations, affected dependencies, family/branch effects, preserved record IDs,
and the next permissible operation. It keeps separate fields for:

* evidence review disposition and source truth (`not_established` unless a
  separately justified claim supplies more);
* category admission and conditional assumptions;
* accounting applicability/validity, which this admission alone cannot establish;
* capability support and computation status (these examples execute no engine).

`ADMITTED_CONSTRAINT` means the declared support and layer's admission rules
are satisfied, conditional on all listed assumptions. It does not make the
issuer's assertion true. `ADMITTED_ASSUMPTION` explicitly selects an authored
condition; `RETAINED_ONLY` leaves it unselected. `EVIDENCE_REFUTED` names a
supported predicate and a check that contradicts the candidate in this scope.
`UNRESOLVED` identifies missing information or an undecided check. `UNSUPPORTED`
identifies unavailable authority, semantics or capability. `REQUEST_INVALID`
identifies a malformed transition/reference. `SCOPED_CONFLICT` preserves an
incompatible proposed conjunction and its exact context. These dispositions
must not be collapsed into one Boolean or a probability.

## U2. Six categories and their admission rules

### Disclosure readings: extraction and semantic interpretation

An extraction payload links immutable bytes, occurrence/locator, literal reading
and extraction review. Review that accepts a reading establishes fidelity to the
inspected occurrence within that review's scope. A synthetic scan showing 120
refutes an OCR candidate 720 as a reading; it does not establish an underlying
company balance. A faithful reading of an erroneous issuer statement survives.

A semantic-interpretation payload separately names the extraction version,
contextual meaning, modality, mappings and alternatives. A phrase such as
“credit facility 100” does not establish that 100 is drawn debt. If commitment
and drawn-balance interpretations remain unresolved, retain both. Selecting one
as an explicit analytical assumption creates a conditional reported-value
branch; selecting an interpretation cannot manufacture authority for journals.
Review events must specify whether they concern fidelity or meaning. A semantic
review may admit a meaning at the requested layer only with its source/context
support; an unsupported implication remains unresolved. Competing readings
never receive weights from OCR confidence or reviewer preference. (UA01.)

### Historical facts

A fact payload identifies an economic quantity/event, its declared domain and
supported constraints. Domains may be finite, continuous, mixed or symbolic;
any unsupported solver operation returns its unmodified domain as unresolved.
A continuous real-valued amount is not implicitly discretised to cents.
Evidence and context must support each new constraint, and shared quantities
retain their history-family links. A hypothetical assumption about an unknown
fact remains an assumption, even if it selects one factual value.

For the synthetic same-view amount x, let D0=[0,100]. New admissible evidence
supplies C1=[20,60]. Under unchanged assumptions, D1=D0 intersect C1=[20,60]:
x must satisfy both pairs of endpoint inequalities. Evidence C2=[70,80] gives
D1 intersect C2=empty since x<=60 and x>=70 cannot both hold. This is a conflict
in the named conjunction/branch, not a finding that every family or the real
company is impossible. A candidate x=80 is refuted within D1 because 80>60.
The closed endpoints, exact real domain and common units are explicit fixture
assumptions, not defaults for rounded reported values. (UA02.)

### Accounting elections

An election payload names the dated rule package, exact permission and
eligibility evidence, relevant entity/transaction/class, effective period,
permitted options, chosen option and any consistency/transition obligations.
Permission must originate in the package's reviewed authority, not in a list
asserted by the request. Eligibility false refutes this proposed election within
that package; eligibility unknown remains unresolved. Missing or unverified
permission produces `UNSUPPORTED`, preserving the asserted treatment without
an accounting constraint. Even a selected permitted election needs separate
recognition/measurement/journal checks. An assumed election cannot be substituted
for evidence of what an issuer historically elected.

UA03 uses an explicitly synthetic rule P allowing options A and B during 2026
for class C when eligibility is true. Choosing B is a conditional design example;
option Z is refuted by P's exhaustive permission list. An absent real authority
is unsupported, not evidence that the treatment is prohibited in every regime.
No IFRS, US GAAP, ASBE or tax permission is established by this example. P17
must supply actual dated sources, eligibility and treatment consequences.

### Measurement estimates

An estimate payload states the estimand, economic/measurement date, method and
version, units, inputs and their information dates, judgments, assumptions,
output domain/value and applicability requirements. A model-produced amount
remains an estimate. A reported estimate remains separately a reported assertion;
copying its number does not establish its measurement method.

UA04 uses the synthetic formula e=quantity times a stipulated price estimate:
10 times 2=20. Later admissible input 3 produces a new estimate 30 for a newly
specified view of the same measurement target. The revised estimate is neither
a narrowed factual interval nor evidence that the earlier input was fraudulent.
Retrospective revision is labelled with the later information view; it cannot
be used by a decision confined to the original cutoff. Actual accounting rules
must determine whether a change is prospective, a correction, a restatement or
impermissible. Missing applicability is retained as an obligation. General
estimators are representable; unsupported evaluation returns the symbolic method,
inputs and reason without inventing a value. (UA04.)

### Behaviour policies

A policy payload identifies its decision date(s), feasible actions/constraints,
state and information inputs, versioned decision rule, author and assumption
selection. A policy is a proposed conditional choice rule, not a realised fact.
All reads must resolve to the actor's declared information view at the decision
instant, including dynamically selected inputs and model-generated forecasts.
An audit list alone cannot prove that an eventual plugin obeys this rule.
Runtime information mediation is an interfaces/language obligation.

UA05's decision is dated 2026-03-01. An announcement known on 2026-02-28 about
a June stress can be used as announced information. The actual June outcome,
known in July, cannot be used at that decision date. Admission of the announcement
does not condition a historical probability model or make the June outcome known.
A fixed-action or state-dependent policy is permitted as a selected assumption
when its semantics and information checks are supported; the P06 hold-only
restriction is not a whole-product rule. Optimisation, randomised choices and
causal interventions need separately specified methods. Unsupported evaluation
preserves the policy but produces no executed decision. (UA05.)

### Future innovations

A future-innovation payload identifies driver, future period, unit, scenario
version, feasible domain, joint constraints and assumptions. It may specify
unweighted possibilities. UA06 uses the synthetic continuous rate change
[-1/10,1/10], with no law. The future-domain layer can admit that authored domain
as a selected assumption without claiming any probability, independence,
expectation or relative plausibility. Correlated/shared driver constraints must
survive; the six category tags do not make variables independent.

A probability attachment, likelihood update, conditional distribution or measure
conversion requires the later joint-measure contract. For this slice these
operations return `UNSUPPORTED: JOINT_MEASURE_CONTRACT_REQUIRED`, preserving
the proposed model. No uniform distribution, equal branch weights, confidence
weights or normalization over successful branches is allowed. Absence of a law
is not grounds for rejecting an otherwise admissible unweighted scenario.

## U3. Operations and revisions

Each operation names a base view and exact input versions. The support must pass
context, review, authority where applicable, and time checks for the requested
layer. A stale base view is `REQUEST_INVALID: STALE_BASE_VIEW`; retry requires
rebasing and reassessing newly competing evidence. No partial write may expose
new constraints with old dependency metadata. Persistence must atomically save
the new records, review/selection events, dependency changes and successor view;
its transaction/replay mechanism is still to be specified.

| Operation | Preconditions | Postconditions |
| --- | --- | --- |
| `new_evidence` | Resolved source/reading references, explicit context and view, category checks. New evidence can also be retained while checks are unresolved. | Preserve the source and proposal; admit only supported predicates at the requested layer. Recompute candidate membership even when the new candidate is not selected. A new source cannot silently replace the incumbent. |
| `narrow` | Same target, units, assumptions, interpretation/election choices and branch scope; new constraint has independent admissible support. | Child domain is the intersection of old domain and supported new constraint. Retain both supports. Empty intersection creates a scoped conflict; unknown intersection remains unresolved. Domain enlargement or changed assumptions is not narrowing. |
| `correct` / `supersede` | Exact predecessor, supported explanation of the error/correction and a review event naming which assertion/meaning/constraint is replaced and in which view. | New immutable version removes only the superseded active constraint in the successor view and supplies its replacement. No monotonic-domain claim. Original source and frozen views survive; other constraints still apply. A different economic target normally requires a new record, not replacement. |
| `select_assumption` | Authored proposition and alternatives, explicit rationale, scope and time view; requested layer permits conditional assumptions. | New conditional branch retains the original uncertainty and selected assumption. Unselected assumptions impose no constraint. Selection cannot establish factual truth or missing accounting permission. |
| `select_election` | Dated authority, eligibility and consistency/transition obligations established within scope; selection distinguishes assumed treatment from evidenced historical election. | New election version/conditional branch plus its obligations. Actual postings remain subject to accounting checks. Unsupported permission admits no treatment branch. |
| `revise_estimate` | Named old estimate, new method/input/judgment versions, same estimand or explicitly new target, valid information view and method applicability. | New estimate and lineage, invalidated dependent measurements/results, frozen prior estimate. Record how information date differs from measurement date; accounting treatment of the revision remains separately determined. |
| `revise_policy` / `revise_driver` | Named predecessor, explicit changed rule/domain/information set/scenario and rationale, capability and information checks. | New selected assumption/version. Reassess all affected paths and membership; no automatic narrowing, causal effect or change in historical weights. Old paths remain frozen. |

For a supported correction of [20,60] to [10,90], keeping background [0,100],
the new domain is [0,100] intersect [10,90]=[10,90]. Intersecting with the
superseded [20,60] would retain a known obsolete restriction. This example
stipulates that the correction replaces that entire bound and that no other
constraint survives; actual mixed-support claims must identify precisely which
part is corrected. A frozen prior query still returns [20,60]. (UA07a.)

Invalidation uses reverse dependencies, not only selected-record IDs. If the
old reading feeds interpretation I, fact constraint C, family F and query Q,
changing the reading invalidates I, C, F and Q for *current* reuse. If an estimate
E also uses C, its result is affected as well. Adding a rival source changes the
selection-population revision even if the winning candidate stays identical;
F and Q depend on that revision. Missing dependency metadata makes current reuse
unestablished. Unrelated families may be reused only with complete unchanged
dependencies and matching query/time views. Invalidation changes reuse status,
not the bytes of old results, and is not evidence that every old number changed.
A frozen export identifies its original version, assumptions and supersession
status; it never advertises an old result as current. (UA07b.)

The provenance/derivation graph must resolve all references and must not contain
unsupported cycles. A reference to a version that does not exist is a dangling
reference, even if a record with the same logical name exists. Cyclic economic
relations are a different matter: x+y=100 can jointly constrain both variables
in one supported constraint block without either being independently known.
Mutually constrained quantities do not imply a cyclic derivation or independent
random variables. A simultaneous block names its formula, variables and external
support; an unsupported block is retained as unresolved. Category substitution
(e.g. replacing an unknown fact with an election under the same identity) is
invalid. A legitimate cross-category inference creates a distinct record with
explicit derivation and category-specific admission. (UA08.)

## U4. Interactions, failures and next operations

| Contract | Exchange and responsibility |
| --- | --- |
| Evidence E1/E3/E4 | Supplies occurrences, extraction and interpretation review, context, conflicts and assumptions. Admission returns the predicate/assumption actually used, its scope and unresolved supports. Retention is independent of admission; no source text is overwritten. |
| Time T1–T3 | Supplies cutoff-qualified evidence and byte-vintage/review views. Admission checks information access at measurement and decision dates, and records later-information revisions separately. Unknown availability cannot pass a historical-information requirement. |
| Histories H1/H2/H5 | Consumes jointly admitted predicates, selected assumptions and membership revisions. Returns conditional families/candidate regions and unresolved obligations. Partial support never validates membership in the complete accounting-history family. |
| Accounting | Must establish package authority, eligibility, recognition, measurement and revision consequences. Receives retained unsupported treatments separately from selected permitted elections; returns layer-specific applicability and journal obligations. |
| Language/IR | Must encode category payloads, exact domains/units, simultaneous blocks, dependency types and explicit operation transitions. Unknown versions cannot be decoded using a convenient existing variant. These JSON examples do not select a runtime format/library. |
| Persistence | Owns atomic version/view creation, idempotency, stale-write detection, migration and reverse dependencies. Frozen reads must be distinguishable from current reuse; a failed write leaves the old view current with an explicit failure receipt. |
| Interfaces and failure semantics | Show requested layer, retained content, disposition, conditions, time view, unresolved obligations and next action. Preserve partial results on capability/resource failure. Harmonize reason codes without converting unsupported/unknown into false or successful computation. |

A refuted candidate can be reconsidered under a supported correction or an
explicitly different conditional view; its refutation remains valid in the old
scope. An unsupported treatment needs authority/applicability work. A dangling
reference needs correction, not solver execution. A local conflict needs source,
context or interpretation review; arbitrary deletion of the inconvenient source
is not a repair. Solver timeout preserves the expression and unresolved region.
It cannot establish evidence refutation or global family infeasibility.

Full scenario-mode semantics, stochastic information filtrations, joint measures,
likelihood identity/reuse, probability normalization and conditional outcome
payloads are the next uncertainty task. No operation in U3 changes probability
weights. A future implementation that attaches a model must identify that later
contract and preserve unavailable outcome regions rather than renormalizing
successful computations. The proposed interface here is a dependency obligation,
not a claim that these semantics are already complete.

## U5. Matched encoding alternatives and default audit

Both alternatives receive the same UA01–UA08 requests and must return the same
expected dispositions, retained records, family effects and invalidations.
Neither representation is credited for accepting more unsupported cases.

| Same fixture question | Tagged variants with shared header | Generic record with versioned validator registry |
| --- | --- | --- |
| UA01: fidelity versus meaning | Two explicit payload variants within disclosure readings require different fields/reviews. | A category/subtype validator must distinguish them; generic fields alone cannot. |
| UA02: continuous domains | Domain variant carries exact endpoints/symbolic predicates; no finite-only restriction. | Domain-validator version must be pinned; changing it cannot silently change endpoint meaning. |
| UA03: permission versus asserted choice | Election variant requires authority and eligibility references; absence returns unsupported. | Registry validator must enforce the same sourced permissions, not trust arbitrary fields. |
| UA04: estimate/date revision | Estimate transition checks input versions and view separately from fact narrowing. | Operation and category validators must be coordinated and versioned together. |
| UA05: future information | Policy variant exposes decision inputs and their information roles. | Extensible policy validator must still use the shared information rule; extensions cannot bypass it. |
| UA06: unweighted future domain | Law attachment is explicitly optional; this slice rejects probability operations. | Registry must separate domain admission from a later probability plugin and report its absence. |
| UA07: corrections and invalidation | Shared revision header and typed dependency edges support the declared successor/frozen distinction. | Shared validator protocol must supply all changed dependencies; an extension that omits them cannot support reuse. |
| UA08: substitutions and cycles | Closed category discriminants reject wrong payload/identity changes; simultaneous blocks have their own representation. | Unknown/new categories are easier to register but must return unsupported until reviewed migration/admission semantics exist. |

Provisionally prefer tagged payload variants with the shared header for the
initial specification: the six categories have materially different admission
conditions, and explicit variants make missing conditions visible to reviewers.
A versioned registry remains credible where later domains need additional
payload types. The choice does not select Python classes, JSON as a wire format,
a database or a solver. Either needs an extension/migration policy preserving
old record interpretation, adapter conformance and unknown-version retention.
Changing category meaning requires a new version and explicit migration, never
reinterpretation of frozen content. This is a semantic comparison, not an
implemented benchmark or performance ranking.

| Material choice | Provenance and justification | Failure mode | Smallest diagnostic | Status |
| --- | --- | --- | --- | --- |
| Six categories, explicit semantic subtype | MC10/P15 G15 and E1; different admission rules | Treat extraction fidelity as factual truth | UA01 competing reading/meaning | User requirement; encoding proposed |
| Full shared context/view/header | E3/T1/H1/H5 and MC25/27 | Mix periods, views or source with assumptions | Inspect every fixture's context and layer | Proposed integration |
| Immutable versions and reverse membership dependencies | H5 and MC27 | Old query reused after a new rival source | UA07 closure and frozen read | Proposed behavior; transaction mechanism open |
| Intersect only for same-assumption narrowing | Set definition in U2/U3 | Widening called narrowing or correction overconstrained | UA02/UA07 exact endpoints | Derived semantics in declared example |
| Exact closed real intervals | Synthetic exercise, to expose continuous uncertainty | Accidentally infer cents or reported-rounding behavior | Check interior 1/3 in [0,100] and stated endpoints | Fixture convenience only |
| Synthetic P and multiply estimator | Bounded interface examples, no new authority research | Mistake permission or formula for accounting law | Check synthetic labels and pending accounting obligations | Convenience, never production default |
| Tagged variants | Matched U5 comparison | Hard-to-extend closed enumeration or concealed custom fields | UA08 unknown version and future migration review | Provisional proposal |
| Unweighted scenarios and no implicit independence | MC08/12/14/18 | Invent probabilities from enumeration/confidence | UA06 absent-law outcomes and deferred attachment | Required preservation; measure design unfinished |
| P06 finite facts, finite weighted innovations, hold-only policy and restricted methods | Historical `admit_uncertainty` at lines 539–686 | Promote probe limits into universal requirements | Compare UA02, UA05 and UA06 with those branches | Historical baseline only; not adopted |

## U6. Scope of completion and source support

The companion fixture file specifies eight groups with explicit inputs, support,
expected results and preserved records. Its sources are synthetic by construction.
Local diagnostics check document/reference consistency, example arithmetic and
dependency closure. They cannot establish that a future implementation enforces
the rules, that source-grounded treatments are valid, or that forecasting works.
Independent substantive review and human acceptance remain pending.

The requirements come from `docs/plans/accounting-mission-requirements.md`
(MC04/08/10/12/14/18/25/27) and the accepted P15 `coverage.json` rows MC10/12/14
and G15. Interactions use proposed evidence-contract-v3 E1/E3/E4,
time-contract-v2 T1–T3 and history-families-contract-v1 H1/H2/H5. The inspected
P06 implementation is historical counterevidence for accidental defaults, not
accounting authority. No new academic theorem or official accounting permission
is asserted; the two interval relations are derived in U2/U3 and the estimate
multiplications are stipulated arithmetic.

Completion of this admission slice leaves the whole uncertainty contract
unfinished. The next separately reviewed task must specify justified joint
measures, conditioning, probability updates and conditional outcome payloads,
then reconcile both groups before registering uncertainty as a complete proposed
contract. Accounting, language/IR, persistence, interfaces and failure semantics,
initial-profile selection and dependency order also remain open. All fourteen
P15 decisions and MC01–MC35/G1–G18 remain active. Optional bounded result review
must not become a prerequisite that blocks the next reviewed drafting task;
full independent P16 result review remains required before phase acceptance.

FILE docs/design/proposal/architecture/uncertainty-measure-attachment-contract-v2.md
# Joint-measure attachment and event identity v2

This document specifies the next bounded part of the P16 uncertainty contract.
It attaches a declared joint measure to an already versioned history family and
evaluates events against that one measure. It does not select a measure from
data, infer independence, condition on observations, update likelihoods, run a
solver, or produce financial statements. The examples are synthetic design
fixtures; they establish no probability for an actual company and no
accounting permission.

This version repairs the saved examples only. Systematic matched-alternative
assessment and remaining failure-case coverage remain the next bounded task.

The contract is needed for MC08--MC14, MC18, MC25 and MC27 and for G1, G15 and
G16. It consumes the evidence, time, history-family and admission records
already described in this directory. Accounting validity, empirical forecast
validity, implementation correctness and human acceptance remain separate
questions.

## A. Request, result and identity

`MeasureAttachmentRequest` is an immutable, versioned record with these fields:

| Field | Required meaning |
| --- | --- |
| `request_id`, `version`, `predecessor` | Stable request identity and an explicit predecessor; changing the bytes creates a new version. |
| `family_ref`, `view_ref` | Exact immutable history-family and view references, each resolving an ID and version. A measure never silently follows a successor family. |
| `model_ref` | Exact model ID/version reference with the declared measure representation and evaluator. Explicit null preserves an unweighted domain. |
| `coordinates` | Ordered typed coordinates, including entity/perimeter, concept, dimensions, units, time and any shared drivers. Coordinate identity is semantic, not an array position chosen by a caller. |
| `sample_space` | Explicit elementary outcomes or a declared continuous/mixed domain, with support and measurability metadata. Missing support is unresolved. |
| `event_representation` | Versioned selectors for elementary outcomes, measurable cells or symbolic predicates. A display label is never an event key. |
| `measure_kind`, `purpose` | `finite_joint`, `discrete_joint`, `continuous_joint` or `mixed_joint`; purpose is one of scenario, pricing, risk, or another declared use. Purposes cannot be mixed implicitly. |
| `mass_or_density` | Exact masses, a versioned density, or a symbolic measure expression. Finite examples use rational strings; unsupported evaluation retains the expression. |
| `support_restrictions`, `dependence` | Restrictions and all declared cross-coordinate dependence. Empty dependence means “unspecified”, not independence. |
| `provenance`, `justification` | Source/model record versions, author, rationale, assumptions and whether the law is synthetic, stipulated, estimated or empirically supported. |
| `information_cutoff`, `evidence_cutoff` | Time views used to justify the model and to admit its inputs. Later information cannot silently enter an earlier view. |
| `dependencies` | Exact versioned family, evidence, time, category and model dependencies. A missing or stale dependency blocks current reuse. |

Section F defines the exact field names and operation-specific result schema.
The result is a `MeasureAttachmentResult` with the request and record identity,
old and proposed view, a disposition, reason codes, preserved records,
support references, unresolved obligations, structural validity, attachment
status, mathematical obligations, empirical-justification status,
capability status, computation status and permitted next operations. These
fields are separate. A syntactically valid finite law can be attached as an
assumption while its empirical justification remains `not_established`.

The dispositions are:

* `ATTACHED_ASSUMPTION`: the declared law is structurally valid and explicitly
  admitted as a model assumption; no empirical claim follows.
* `ATTACHED_SUPPORTED`: a separately inspected source/model record supports the
  law for this purpose and scope. This status is not created by a fixture.
* `RETAINED_ONLY`: the submission is preserved but not selected.
* `REQUEST_INVALID`: identity, version, support, representation or the proposed
  finite probability law fails its stated invariant.
* `UNSUPPORTED`: the requested evaluator or measure representation is outside
  declared capability; the expression and domain remain intact.
* `SCOPED_CONFLICT`: restrictions or attached records are incompatible in the
  named family/view. It is not a claim of global infeasibility.

## B. Attachment invariants

1. The family/view, model version, coordinate order, purpose and information
   cutoffs are part of the identity. A law attached to `F@1/V@1` cannot be
   reused for `F@2/V@1` merely because the labels look alike. A changed support
   invalidates reuse until an explicit alignment or update operation records
   what changed.
2. For a finite joint law, each elementary outcome ID is unique, each mass is
   finite and non-negative, and the exact total is one. A duplicate ID is a
   malformed representation, not extra mass. The declared sample space S is
   distinct from positive-mass support {s in S: m(s)>0}. Every member of a finite
   S has an explicit mass, including zero. Omitting a member is an error, not an
   assertion of zero mass. An event may include zero-mass members. A partition
   must cover S, not merely its positive-mass subset.
3. No mass is inferred from solver counts, branch counts, labels, extraction
   confidence, reviewer preference, successful-run frequency or a convenient
   equal-weight default. An unweighted future domain remains unweighted until a
   separate attachment is explicitly accepted.
4. Dependence is joint information. Identical marginal summaries do not permit
   an independence assumption. Shared drivers, entity links, dates, lots and
   contract states stay in the coordinate and dependency records.
5. A real-world scenario measure and a pricing or risk measure are different
   records. Changing `purpose` requires a new attachment and justification; it
   is not a unit conversion.
6. An attachment may be conditional on admitted evidence, an authored
   assumption, or a future-domain restriction. It cannot turn an unsupported
   accounting election into authority or turn a reported value into an economic
   fact.
7. Every accepted operation is append-only. A correction creates a new measure
   version and records the predecessor, changed support and affected results.
   Old views remain readable as historical records but are not current by
   default. Failed writes leave the old view current and return a failure
   receipt.

The historical Core 0 probe required a joint law for future innovations and
therefore rejected an unweighted future domain. This proposal supersedes that
probe restriction for the whole product: an unweighted domain is admissible as
an explicit scenario assumption, but probability, expectation, likelihood and
quantile operations require this attachment contract and an attached law. The
older restriction remains evidence about the prototype, not a universal
semantic rule.

## C. Event identity and evaluation

An `EventIdentity` contains an event ID/version, the exact family/view and
measure identity, coordinate bindings, selector kind, selector expression,
projection metadata and provenance. A named event may be an overlapping view;
it need not be a cell in a partition. Distinct elementary outcomes that map to
the same displayed coordinate remain distinct IDs. A duplicate event
description with the same identity is an idempotent reference; a new selector
version is a new event.

For a finite space `S` with masses `m(s)`, a selector `E` evaluates as

\[
  P(E)=\sum_{s\in S:\,E(s)}m(s).
\]

For events `A` and `B`, evaluation uses the same joint law:

\[
P(A\cap B)=\sum_{s:\,A(s)\land B(s)}m(s),\qquad
P(A\cup B)=P(A)+P(B)-P(A\cap B).
\]

The subtraction is required when views overlap; summing named-view masses
without the intersection double-counts shared outcomes. A finite partition must
carry coverage and pairwise-disjointness evidence before a caller may treat its
cell masses as an exhaustive decomposition. For continuous or mixed spaces,
the request preserves the declared domain and measure expression. If no
validated evaluator is available, the result is `UNSUPPORTED` with the
symbolic event and unresolved numerical obligation; it never fabricates a
grid, density normalization or probability.

Projection is explicit. If two elementary outcomes `(region=A, rate=1)` and
`(region=B, rate=1)` both project to `rate=1`, the projected display has mass
one but the elementary outcomes remain two distinct members of the joint
space. Collapsing them is allowed only through a named measurable projection
that records the lost coordinate and the resulting event algebra.

## D. Failures and interactions

The evidence and admission contracts supply immutable records, category
dispositions and selected assumptions. The time contract supplies information
cutoffs, byte vintages and review views. Histories consume an attached law and
return family-scoped events; they must retain unweighted domains and unresolved
branches when no law is attached. Accounting receives a measure only as a
scenario/model input and must perform its own recognition, measurement and
journal checks. Language/IR must encode exact versions, selectors, domains and
reason codes. Persistence owns atomic append, stale-version detection and
reverse dependencies. Interfaces expose the purpose, conditions, cutoffs,
support, dependence and unresolved obligations. Failure semantics preserve
partial records on resource or evaluator failure.

The following are explicit failures: negative or non-unit finite mass;
duplicate elementary IDs; omitted support; stale family/model version;
incompatible purpose; implicit independence; event references outside the
declared space; a partition advertised without coverage/disjointness evidence;
and unsupported continuous evaluation. None of these failures authorises
discarding mass, renormalising successful branches, or replacing an unresolved
outcome with a default.

Conditioning, likelihood updates, measure conversion, calibration and
conditional statement/outcome payloads are future operations. They must name a
denominator/event identity, information set and resulting family version and
will be specified in a separate reviewed task.

## E. Matched alternatives and default audit

Two credible representations are proposed for a future matched assessment
against the same fixtures. That assessment has not been completed:

* **Family-linked record (provisional choice).** The attachment stores the exact
  family/view and references the model record. Revisions and invalidation are
  straightforward, and a reader can trace a probability back to the joint
  history family. Portability requires a stable family identity service.
* **Self-contained joint-model record.** The attachment carries a complete
  joint model and an explicit projection to a family. It is easier to export,
  but duplicated family definitions can drift and a correction must reconcile
  two version graphs.

The family-linked design remains a provisional candidate because preserving
shared history identity and revision lineage is a stated mission requirement.
This is a design rationale, not a performance or usability ranking; both
alternatives remain implementation candidates until the language, persistence
and interface contracts are reviewed. The material defaults have the following
audit:

| Choice | Provenance and justification | Failure mode | Smallest diagnostic | Status |
| --- | --- | --- | --- | --- |
| Rational finite masses in fixtures | Exact arithmetic makes overlap and normalization inspectable. | Decimal parsing could hide rounding. | Recompute with `Fraction` and compare exact strings. | Synthetic diagnostic convention |
| Explicit elementary IDs | Needed to distinguish equal projections. | Callers may use labels as IDs. | Duplicate-ID and projection-collision fixtures. | Proposed invariant |
| No implicit independence | Required by joint-history dependence. | Marginal-only input may be treated as independent. | Same-marginal/different-joint fixtures. | Proposed invariant |
| Separate purpose | Scenario and pricing measures answer different questions. | A converter may relabel a measure. | Purpose-mismatch rejection fixture. | Proposed invariant |
| Family-linked identity | Preserves revisions and dependency closure. | Export/import may lack family registry. | Version-mismatch and changed-support fixtures. | Candidate; profile unselected |

All fixture outputs are specified behavior only. They do not show that a
runtime, accounting treatment, company probability or forecast is correct.


## F. Operation-specific records and fixture convention (v2)

The companion v2 JSON stores complete request/result records in each case. There
are no implicit case overrides or defaults. `records` is an immutable registry:
its key equals `id@version`, and references always use that complete key.
`family_ref`, `view_ref`, `model_ref`, coordinate references and dependency lists
resolve there. An explicitly null model denotes an unweighted domain, not a
missing field. A stored malformed model remains a submitted candidate; registry
presence is not admission. The same key must never describe different bytes.
Family and view versions are independent; a view identifies exactly one family
version. Model versions bind the family, view, coordinate order, sample space,
purpose, dependence and mass/density representation. A new law requires a new
key. These examples use explicit references rather than duplicating id/version
pairs that could disagree.

Every request has `request_id`, `version`, `predecessor`, `operation`, exact
family/view/model references, ordered `coordinates`, `sample_space`,
`measure_kind`, `purpose`, `mass_or_density`, `dependence`,
`support_restrictions`, `event_representation`, `provenance`, `justification`,
`information_cutoff`, `evidence_cutoff`, and `dependencies`. Coordinates resolve
to typed concept/entity/perimeter/dimension/unit/time metadata. Dependencies
include every direct semantic reference and the time/admission/evidence records.
Transitive dependencies follow the registry references. Cutoffs here are both
2026-03-01T00:00:00Z; fixture records were authored for this synthetic time view.
No claim about the information available for a real company follows.

`MeasureAttachmentRequest` uses `operation=attach_measure`. The deliberately
invalid branch-count request uses `infer_from_branch_count`; its rejection is
specified even though this is not an admitted operation. Marginal-only inputs
are retained as constraints on possible laws, with no attached joint measure.
For finite laws, masses cover the declared outcomes exactly and joint outcome
assignments cover every coordinate. `support_restrictions=[]` means no added
restriction, not permission to discard an outcome. A density is expressed
relative to its declared base measure; missing normalization remains explicit.

`EventEvaluationRequest` uses `operation=evaluate_event` and also requires
`attachment_ref`, `event_refs`, and `query`. The attachment is either an admitted
synthetic precondition or a retained symbolic candidate with explicit status.
Each event binds its own model/family/view and coordinates, selector kind,
selector expression, projection metadata and provenance. Queries are one-event
probability, two-event overlap, finite partition validation, or finite
projection. MA03c repeats one event reference; it does not request an evidence
update and proves nothing about semantic duplicate likelihoods. Symbolic
requests retain expressions when the proposed evaluator cannot compute them.

These examples validate required fields and resolvable references first, then
attachment family/support, purpose and model compatibility. An incompatible
family/purpose is rejected; a newer requested model is retained without reuse.
For finite inputs, duplicate IDs precede mass coverage, non-negativity and unit
total checks. Event selection/partition checks follow valid-law checks. Symbolic
models retain missing mathematical obligations when evaluation is unsupported.
An invalid probability law can have a well-formed representation: MA02b/c thus
have valid structure and failed mathematics. A request without a joint law has
unresolved mathematics, not an assertion that no such law exists.

Every result includes `result_id`, `version`, `request_ref`, `operation`,
`old_view`, `proposed_view`, `disposition`, `reason_codes`, `preserved_records`,
`support_references`, `unresolved_obligations`, `structural_validity`,
`attachment_status`, `mathematical_status`, `mathematical_obligations`,
`empirical_justification`, `capability_status`, `computation_status`,
`next_permissible_operations`, `future_dependencies`, `family_effect`,
`probability`, and `observations`. Attachment success additionally identifies
`attachment_ref`; evaluated results retain the input attachment. `probability`
is populated only for a single defined event; multi-event/projection answers
are named in `observations`. Invalid total mass is an observation about a
candidate, not an event probability. Unsupported or rejected evaluations return
no numerical probability. Receipt preservation is not an attached law.

Attachment dispositions retain section A meanings. Event results add
`EVALUATED` for a computed, mathematically valid query under the named law;
`REQUEST_INVALID` for incompatible identity/purpose or malformed selectors;
`RETAINED_ONLY` for a stale model that needs explicit migration; and
`UNSUPPORTED` for a retained symbolic request without a validated evaluator.
`structural_validity` concerns the representation, not normalization;
`mathematical_status` is independently `satisfied`, `failed`, or `unresolved`.
An unavailable evaluator can leave structure valid and mathematics unresolved.
All empirical statuses here are `not_established`. `capability_status` means
capability proposed by this document, never an installed runtime capability.
All results are specified expectations, not executed product responses.

An attachment appends a measure record referencing its existing family/view;
it does not change the history family or select a probability for unweighted
alternatives. `old_view` and `proposed_view` therefore match in these examples.
Rejections leave the old view/attachment current. Stale-model and changed-family
requests preserve that original view and require a new explicitly reviewed
attachment; they cannot silently redirect it. Atomic persistence remains a
separate unfinished contract.

The currently specified next operations are revise_request, attach_measure,
evaluate_event, and retain_symbolic. These names describe the proposal only.
Conditioning, likelihood updates, model migration, evaluator installation and
conditional financial outcomes occur only in `future_dependencies`. No example
advertises condition_or_update as a presently permissible operation.

## G. Repaired examples and exact local deductions

MA01 preserves an unweighted continuous domain and rejects branch counting as
a law. MA02 uses one three-atom family and separately identified valid,
negative-mass, non-unit and duplicate-ID submissions. MA03 evaluates the valid
law with masses 1/2, 1/3, 1/6: for A={a,b} and B={b,c}, P(A)=5/6,
P(B)=1/2, P(A intersection B)=1/3, hence P(A union B)=5/6+1/2-1/3=1.
A partition omitting c fails even though its listed cells are disjoint.

MA04a retains Bernoulli marginals without inventing a coupling. MA04c and MA04d
use the same four assignments (0,0), (0,1), (1,0), (1,1). The first law places
1/2 on each diagonal assignment and explicit zeros elsewhere; the second puts
1/2 on each off-diagonal assignment and zeros on the diagonal. Summing over Y
or X gives the same Bernoulli(1/2) marginals under each law. Summing the diagonal
masses gives P(X=Y)=1 and 0. Thus these marginals cannot determine that event.
These are local finite-sum deductions, not claims from an external source.

MA04b has its own two-outcome family and law: (A,1) and (B,1), each mass 1/2.
The explicit rate projection sums both preimages to mass 1 while preserving
both elementary IDs. This law never reuses the three-atom model identity.
MA05 rejects changed family/support and changed purpose, and retains a stale
model request without migrating it. MA06 uses distinct compatible continuous
and mixed domains/models. Both preserve their symbolic expressions and missing
mathematical/evaluator obligations, with null numerical probability.

The finite fixture convention is exact rational arithmetic, not a proposed
restriction on all real implementations. The local diagnostic recomputes from
inputs, checks identity/reference/domain compatibility, and compares specified
outputs. It is an author consistency check, not an engine or prose acceptance
test. Comprehensive failure coverage, matched alternatives and uncertainty
integration remain open; independent substantive review is pending.

FILE docs/design/proposal/architecture/uncertainty-chaining-contract-v1.md
# Uncertainty operation chaining — proposed supplement v1

This supplement repairs the result-to-request boundary in uncertainty-contract-v1,
sections 2–4, and the UC01, UC02 and UC08 fixtures. Those immutable fixtures
contain correct illustrative masses but their child `model_ref` points to the
original prior. That reference is wrong as the governing law for a subsequent
query. The mappings in uncertainty-chaining-fixtures-v1.json replace that meaning
for this proposal; the original records remain historical evidence. No product
implementation or independent acceptance is claimed.

## 1. Bounded question and evidence contract

Can a specified uncertainty result become the next request without reverting to
prior masses, losing consumed information or silently granting admission? The
comparator is attachment v2 A–F and uncertainty admission U3: exact immutable
bindings, explicit selection and preserved parents. This task addresses MC12,
MC14, MC25, MC27, MC33–MC35, with MC08/G6/G15 interactions. It does not select
the initial profile, accounting policy, persistence engine or inference method.

Pass requires consistent complete bundles, an explicit admission boundary, exact
finite chained arithmetic and rejection receipts preserving domain state.
A mismatched law/view/attachment, repeated information or broken reference vetoes
internal consistency and requires repair. Structural checker counts explain
coverage only. There is no empirical comparison, stochastic ranking, accounting
eligibility finding or runtime transaction claim. Stop after these specifications
and bounded checks; independent uncertainty review is next, before accounting.

| Choice and provenance | Rationale and failure mode | Early diagnostic; status |
| --- | --- | --- |
| Immutable derived law, attachment B | Separate provenance from the law actually used; otherwise later queries use prior masses. | Consume UC02's output and reject an original-law substitution; provisional representation. |
| Separate admission/selection, uncertainty section 2 and admission U3 | A calculated candidate is not permission to use it in an admitted analysis. | Candidate-only request fails; admission receipt names exact bundle; proposed invariant. |
| Full finite space, attachment B.2 | A zero-mass outcome remains identifiable for future correction. | Retain c at zero through ordinary updates and restore it only by rebase; finite example convenience. |
| Stipulated binary observation kernel, uncertainty section 4 | Conditional factors require a joint model; distinct atoms alone do not justify independence. | Recompute sequential and joint posteriors; hypothetical model, no calibration claim. |

Skeptical audit passed for this bounded document repair: fixed semantic baseline,
explicit stop, no proxy promotion, no runtime/environment comparison and no
transfer of prototype defaults. Both representation alternatives below must
answer the same chained question. Five counterpart contracts, all fourteen open
decisions, the integrated initial profile and all wider mission obligations remain.

## 2. Complete derivation bundle

A successful weighted condition/update emits an immutable bundle containing:

* a child view with exact family, coordinate, time and evidence references,
  parent view, operation request, `model_ref` for its governing derived law,
  candidate attachment, consumed atoms and assumption-condition identities;
* a derived law with the same child view/family/ordered coordinates/purpose,
  full sample space, every mass including zero, parent law and `base_model_ref`;
* a candidate attachment binding that child and law, with status
  `candidate_not_admitted`, plus the input admission used to justify derivation;
* operation lineage naming parent, condition or likelihood/observation records,
  normalizer, unnormalized masses, incremental/conditioning atoms and applicable
  corrected/superseded records; and
* a result receipt naming all created records, payload and separate structural,
  mathematical, empirical, capability, accounting and human-acceptance statuses.

`base_model_ref` is origin/provenance, never an instruction to evaluate with the
base law. `parent_model_ref` identifies the immediate mathematical input;
`model_ref` identifies the law governing the child. A request's view, law and
attachment must agree on exact identities, not merely numerical masses. The
view's displayed masses, receipt posterior and governing-law masses must agree.
All typed references resolve; dependencies include their transitive closure.
Mutual view/law references are identity links, not recursive content hashes;
each registry record is hashed as canonical JSON separately.

For P on S and nonnegative factor f, the lineage stores w(s)=P(s)f(s),
Z=sum w(s)>0 and Q(s)=w(s)/Z. A condition uses f=1_A. Zero Z produces no bundle.
Consumed observations are the union of parent consumed atoms and the new
incremental atoms. Assumption conditions have separate semantic identities;
conditioning on an authored scenario does not itself consume a measurement.
If a condition represents observed information, its atom must instead be recorded
and protected against later likelihood reuse. Calibration atoms of the base law
remain in the information audit even if absent from the view's incremental list.

Output creation never changes the selected pointer. The receipt's domain writes
are exactly the new view/law/candidate attachment/lineage records; a stored receipt
is an audit write. Candidate presence alone never grants admission. Unsupported
continuous/mixed operations keep their symbolic obligations and do not manufacture
finite bundles. Unweighted results continue under the earlier feasible-set rules.

## 3. Admission and the next request

`admit_derived_bundle` takes the exact candidate/result, intended time/evidence
view and purpose, requested assumption scope, named reviewer/decision authority,
rationale and the expected selection revision. It verifies bundle closure,
normalization, binding, input admissibility, information lineage and complete
support. It returns an immutable admission decision, an admitted attachment
binding the same child/law, and a receipt. The candidate attachment is retained.
Neither law nor view is mutated to change its status. For these synthetic
fixtures the decision authority is the fixture author and the only admissible
status is `admitted_as_authored_assumption`; this is not accounting, empirical or
independent approval. Real authority and review policy remain caller obligations.

A separate `select_admitted_view` names that receipt and attachment, the expected
current selection revision and rationale. It returns a new selection revision
and receipt. Admission alone leaves the selected pointer unchanged. Explicit
queries may name any still-admissible frozen view without changing selection;
requests for the current view must match the current revision. Corrections record
supersession/reuse status in new records, preserving frozen historical queries.
A concurrent/stale selection revision rejects with `STALE_BASE_VIEW`.

The next probability request must name the child's governing law, admitted
attachment and admission receipt, with matching purpose/time/evidence scope.
A candidate-only attachment fails `ADMISSION_REQUIRED`; old prior-law or
parent-attachment substitutions fail `LAW_VIEW_ATTACHMENT_MISMATCH` before
arithmetic. No fallback to an earlier admission or newest record is permitted.
An admission decision missing authority/rationale or unsupported in its requested
scope fails `ADMISSION_INVALID`. Failed admission, selection or update creates
no domain records and leaves selection, admitted attachment and parent hashes
unchanged; only submitted bytes and the rejection receipt may be stored.
Request-identity retries retain the existing idempotence/conflict rules.
These are specified postconditions; persistence atomicity remains unimplemented.

## 4. Chaining and correction examples

UC02 has P=(1/2,1/3,1/6) and P(D=1|s)=(1/2,1,0). Its actual saved payload gives
Z_D=7/12 and Q_D=(3/7,4/7,0). The mapping copies that payload into a repaired
bundle, then explicitly admits and selects it. The next request refers to that
bundle, not to the separately authored UC.posterior fixture.

Specify binary E with P(E=1|D=1,s)=(1,1/2,1) and
P(E=1|D=0,s)=(1/4,1/4,1/4). Complements define the other outcomes. This kernel,
together with P(D=1|s), defines a coherent joint distribution of (D,E) for every
s. The E|D=1 value at c is a stipulated kernel value on a zero-probability D
branch; it does not restore c's posterior mass. No conditional independence is
assumed. The E update adds only measurement.E, retaining D as consumed and as a
conditional argument. The unnormalized masses are (3/7,2/7,0), Z_E|D=5/7 and
Q_D,E=(3/5,2/5,0). Direct joint weighting gives (1/4,1/6,0), Z_D,E=5/12 and the
same answer. Reusing D as an incremental observation rejects, even under a new
request ID. E's distinct atom alone would not suffice without the declared kernel.

UC01's condition A={a,b} yields (3/5,2/5,0) and P(B|A)=2/5 for B={b,c}.
After admission, repeating A uses a newly bound event record with the original
semantic condition identity and the child's exact view/law. Its denominator is
one and masses are unchanged. The second request is a new derivation receipt;
mathematical idempotence does not equate record identities. The same semantic
condition is stored once. A repeated request ID is separately receipt-idempotent.
The original event cannot be silently rebound. Equal member sets alone do not
prove equal semantic conditions across changed coordinates or evidence.

UC08's corrected likelihood (1,1/2,1) must apply to the unaffected original
prior, giving Z=5/6 and (3/5,1/5,1/5). The repaired mapping names the actual UC02
child as superseded and creates an explicit revised evidence/time/admission view.
The corrected block supersedes D's reading while retaining semantic atom D. It
replaces D once; it is not an extra independent observation. The old posterior
and its admission stay readable in their frozen scope, and their current-reuse
status is superseded in the new evidence view. The mapping's replay list is
explicitly empty. If the D,E descendant is present, it is invalid for current
reuse until the conditional E model is revalidated under corrected D and replayed;
this example does not silently reuse it. Correction can restore c because its
unaffected prior mass is positive; an ordinary update of Q_D cannot do so.

## 5. Representation alternatives and review boundary

The explicit bundle materializes masses and lets the next request inspect its
exact law. A lazy parent-plus-transformation law can avoid duplication, but must
have its own immutable law identity, child binding, complete dependency closure,
normalizer and consumed information. Its evaluator must resolve to exactly the
same measure and reject missing/stale inputs. A provenance pointer to P alone
is neither alternative. The fixtures compare both mathematical evaluations on
identical inputs, without performance or storage claims. Explicit materialization
is provisional here because it makes the boundary reviewable, not because it
has been shown superior. General lazy evaluators remain unspecified.

The mapping table and exact chains are proposed examples. Internal calculations
and structural checks cannot establish software behavior, accounting validity,
empirical forecasting, architecture superiority or human acceptance. Independent
review must inspect this supplement with the retained uncertainty/admission/
attachment contracts; it must not treat the original child references as repaired
in place. P17 still owns continuous/mixed inference, causal methods and calibration.

For a correction, the request's ordinary view/law/attachment/admission fields
bind the frozen mathematical input. The separate `target_time_ref`,
`target_evidence_view_ref` and `target_admission_ref` authorize the revised inputs
and output context. Validate each side against its own context; do not demand
that a newly corrected observation was admitted in the frozen base. All output
view/law/candidate records bind the target context. A submission of the corrected
block as an ordinary incremental update may supply this target authorization;
it still fails `CORRECTION_REQUIRES_REBASE` because D has already been consumed.

FILE docs/design/proposal/architecture/uncertainty-rejection-status-contract-v1.md
# Rejected uncertainty requests — status correction v1

This supplement corrects five specified rejection receipts in
`uncertainty-chaining-fixtures-v1.json`. The independent uncertainty review in
`data/accounting-master/runs/20261005T120206-bdb3a74d/P16/execution-0/review_result-0.response.json`
returned REVISE: its arithmetic agreed, but the receipts assigned `not_computed`
to `mathematical_status`, contrary to uncertainty-contract-v1.md §2. The current
fixtures are `uncertainty-chaining-fixtures-v2.json`. The original files and
records remain evidence of the defect, not active expected rejection outputs.
This proposal correction carries MC08–MC14, MC18, MC25, MC27 and MC33–MC35,
principally G1/G6/G15/G16. It requires independent result review.

## 1. Bounded question and acceptance

Can a consumer interpret all five rejected requests using the existing common
status vocabulary? The comparator is uncertainty-contract-v1.md §2 and the
unchanged chaining v1 requests and rejection consequences. Acceptance of this
slice requires all seven status fields below, exactly five explicit correction
mappings, unambiguous active expected receipts, and preservation of every original
registry record and every successful case. Changed requests, laws, payloads,
masses, normalizers, selected state, parent hashes, audit writes or rejection
reasons veto the correction. Missing reference closure or an active malformed
predecessor also veto it. These are repair triggers; they do not reject the wider
uncertainty research direction. Checker totals explain structural coverage only.

Skeptical audit: the baseline is the declared exchange, not prototype behavior;
no arithmetic reassessment, runtime experiment, statistical ranking or environment
comparison is needed. The same requests and consequences are compared. Stop after
the supplement, versioned fixture, focused preservation report, registered check
and updated P16 records. No accounting design begins in this slice.

The status interpretation is a proposed clarification, with provenance in the
reviewed repair plan and the governing vocabulary. Its risk is that `unresolved`
could be mistaken for permission to continue an invalid request. The decisive
`REQUEST_INVALID` disposition, unchanged reason code, explicit no-computation
status and no-output postconditions prevent that inference. A focused field and
state check is the early diagnostic; independent review decides semantic adequacy.
No new empirical, accounting or mathematical default is selected.

## 2. Common status envelope for pre-evaluation rejection

Request validation decides whether evaluation may proceed. Here it fails before
mathematical evaluation, so each corrected receipt contains:

| Field | Value | Meaning for this request |
| --- | --- | --- |
| `structural_validity` | `invalid` | Request validation failed, including semantic binding/admission/reuse checks. This does not mean the receipt itself is malformed. |
| `mathematical_status` | `unresolved` | The requested calculation was not evaluated. This is no finding that its mathematics is false or undefined. |
| `computation_status` | `not_computed` | Validation stopped evaluation; there is no computed result. |
| `empirical_justification` | `not_established` | The rejection establishes no empirical support. |
| `capability_status` | `specified_only_no_runtime` | This file specifies behavior; it reports no runtime execution. |
| `accounting_validity` | `not_assessed` | Rejection supplies no accounting eligibility judgment. |
| `human_acceptance` | `pending` | Neither fixture consistency nor the prior review establishes human acceptance. |

`disposition="REQUEST_INVALID"` and the existing `reason_codes` remain decisive.
`unresolved` never authorizes use of a result or admission of the request. Reserve
`undefined` for established undefined mathematics, such as the specified zero
normalizer; reserve `failed` for an established mathematical failure. Neither
finding was made for these five invalid requests.

The common envelope was chosen over a separate rejection schema because it uses
the vocabulary already required of consumers and retains one interpretation for
each status field. A separate schema could omit inapplicable mathematical fields,
but would require a new discriminator, consumer branches and explicit migration
rules. That broader change is unnecessary for this defect. This choice does not
settle the later language, interface or persistence design.

## 3. Versioned correction and active selection

The v2 fixture copies all 125 v1 registry records without canonical JSON changes.
It adds exactly five records with the same logical receipt IDs, `version=2`, and
the corresponding `@1` receipt as `predecessor`. The only record changes are
version, predecessor, the corrected/added status fields, correction provenance,
and dependency closure including that predecessor. Requests remain version 1.

| Active case | Corrected receipt | Preserved rejection reason |
| --- | --- | --- |
| `candidate_only` | `CH.rejection.candidate_only@2` | `ADMISSION_REQUIRED` |
| `duplicate_D` | `CH.rejection.duplicate_D@2` | `DUPLICATE_INFORMATION` |
| `stale_law` | `CH.rejection.stale_law@2` | `LAW_VIEW_ATTACHMENT_MISMATCH` |
| `stale_attachment` | `CH.rejection.stale_attachment@2` | `LAW_VIEW_ATTACHMENT_MISMATCH` |
| `correction_on_posterior` | `CH.rejection.correction_on_posterior@2` | `CORRECTION_REQUIRES_REBASE` |

`rejection_status_corrections` is the explicit old-to-new map;
`active_rejection_receipts` and the five `cases[].expected_ref` values agree with
it. The `historical_rejection_receipts` entries mark each predecessor ineligible
as an active expected output. Registry presence alone confers no eligibility.
Consumers of this proposal select the named v2 fixture and its explicit case
references; they must not infer a version by scanning for the latest ID. Successful
case references, bundles, admissions and representation alternatives are unchanged.

This is a revision of authored specification examples, not a runtime replay or
an exception to request idempotency. No runtime receipt has been overwritten or
reissued. A future runtime implementing a fixed specification must still return
the same logical receipt for identical request bytes; operational migration and
historical replay rules remain obligations of the unfinished persistence contract.

## 4. Unchanged rejection consequences and retained evidence

Every corrected receipt retains its request reference, exact reasons, selected
family/view/attachment/model snapshots, selection revision and parent hashes.
`state_before == state_after`, `domain_writes=[]`, the audit writes remain
`submitted_bytes` and `rejection_receipt`, and both `proposed_view_ref` and the
output `model_ref` remain null. No posterior, aggregate result or candidate view
is created. Corrected provenance identifies the pinned predecessor file and
terminal review; it is not a new observation or likelihood factor.

The current focused diagnostic is preserved in `uncertainty-rejection-status-check-v2.json`
with its command and input hashes; the fresh registered result and execution
record use `uncertainty-rejection-status-structural-check-v1.json` and
`uncertainty-rejection-status-structural-execution-v1.json`. Their actual outcomes
are recorded in P16/result.md. They test specification consistency, not runtime
enforcement. Five counterpart contracts, the integrated initial profile and
dependency order, fourteen open decisions, P17 methods, E05 and all wider mission
obligations remain. Accounting validity, empirical forecast validity, product
readiness and human acceptance remain unestablished.

Diagnostic correction: the first check treated the frozen `perimeter` value
`single_entity@1` as a registry reference solely because it contained `@1`.
It is a scope label in these fixtures; the v2 diagnostic excludes that field
from registry-reference traversal. The failed v1 report and checker source are
preserved. This changes no request or specified receipt. General perimeter
representation remains outside this bounded repair.

FILE docs/design/proposal/architecture/architecture-integration-v1.md
# Integration of the nine proposed contracts

The active contract list in P16 architecture.json is the document index. This
supplement resolves interactions among those contracts without altering earlier
evidence or treating saved fixture outcomes as executed product behavior. It
addresses MC02–MC14, MC18–MC27 and MC33–MC35. The baseline is the five existing
P16 contracts and their accepted amendments; Core 0/P03/P07 are investigated
prototypes, not automatic defaults.

## Meaning carried between contracts

| Boundary | Meaning that must survive | Rejection or unresolved consequence |
| --- | --- | --- |
| Evidence → time | Original bytes, source occurrence, review layer, economic/reporting/publication/ingestion clocks | Missing clocks cannot support stronger historical-knowledge claims |
| Evidence/time → history | Scoped admitted interpretation/assumption, joint symbols, conflicts and exclusions | Faithful reading alone cannot become an admitted accounting constraint |
| History → uncertainty | Full family/view, partition, dependence and query-relevant economic memory | No weights from witness counts; missing law gives a symbolic/unweighted result |
| Scenario/history → accounting | Branch opening, exact event identity, date/context, permitted information and eligible method | Unresolved or unsupported treatment produces no posting |
| Accounting → persistence | Validated request, source/method versions, proposal/delta and expected head | Exact replay before freshness; all-or-none transition; unknown commit reconciled under original identity |
| Calculation → report | Common history/scenario index, native statuses, unresolved regions/mass and unit/time semantics | No successful-subset renormalization or independent selection of line extrema |
| Correction → all descendants | Immutable old view, replacement scope, candidate-set membership and transitive dependency | Current reuse invalidated even for descendants created after the correction |
| Any contract → IR/interface | Versioned type, lineage and admission requirements | Unknown schema or required semantics cannot be ignored or coerced |

## Explicit amendments and precedence

L1's portable encoding applies only to new portable records. Existing native
record digests, original files, source byte hashes and receipts stay unchanged.
Integer metadata remains integer; financial quantities use exact rationals.
There is no global NFC normalization. A named legacy import retains both IDs
and checked decoded correspondence. Source-map identity is separate from model
identity, so formatting changes do not alter a model's financial meaning.

P2 resolves the early accounting contract's ambiguous “event/version” language:
the stable lookup key excludes version and payload. A correction uses a new
business-event identity with an explicit treatment/lineage; merely changing a
version under an existing key conflicts. Branch identity includes an explicit
projection namespace, distinguishing separately requested hypotheticals from
retries of the same projection. No double counting of hypothetical projections
is permitted when reporting realized transactions.

Native accounting retains its established validation order and assess-only
boundary. New portable wrappers validate their own envelopes and then delegate
to that native order. Dependency recognition is guarded by reference shape;
malformed refs are not followed. A shape error cannot be masked by finding an
old receipt. Output defects are distinguished from ineligible economic events:
reject publication as ASSESSMENT_OUTPUT_INVALID while retaining the validated
request and diagnostic candidate. All four committed accounting domains remain
unchanged for assess-only, rejection and replay.

Uncertainty fixture v2 rejection receipts supersede only their explicitly named
v1 predecessors. Their valid requests, joint laws, calculation payloads and
unchanged successes remain evidence. Derived law/view bundles require separate
admission and selection; a numerical posterior does not admit itself. No
platform wrapper changes an existing domain's status values in place.

## Status mapping at the new platform boundary

The native uncertainty schema has seven distinct statuses. The new platform
schema preserves the full native result and applies these mappings only with
the operation's tagged disposition and payload. Unknown combinations return
`STATUS_MAPPING_UNSUPPORTED`; they are not guessed.

| Native meaning | Platform interpretation |
| --- | --- |
| REQUEST_INVALID with invalid/unresolved/not_computed | rejected; invalid/unresolved/not_computed; no usable payload |
| satisfied + specified_exact, with a valid finite calculation payload | completed; valid/defined/complete; evidence_mode=specification_example |
| undefined, with established zero normalizer | completed; valid/undefined/complete; no posterior |
| specified_partial with retained unresolved regions | partial; valid/unresolved/partial, even when some local values are defined |
| symbolic without a requested executable evaluator | partial with retained formulas; valid/unresolved/not_computed |
| UNSUPPORTED operation/capability | unsupported; valid/unresolved/not_computed; retain input family |
| failed mathematics, such as an invalid proposed law | rejected; mathematical_status=failed, preserving the native finding; never `infeasible` without proof of an empty family |

For the last row a platform diagnostic names the failed mathematical predicate
and preserves the native result; no probability value is published.
`structural_validity` is copied from the native request validation,
not inferred from the law's failure. A proof of infeasibility is a different
tagged result and maps to `infeasible`. Numeric/service failure has computation
`failed` and math `unresolved`, not mathematical infeasibility. These rules
preserve the failed mathematical verdict without conflating it with an empty
financial model or a service failure.

Native accounting `assessed` with `eligible` means the requested assessment was
specified, not that a journal was committed. Outer disposition is completed,
commit observation not_committed; its native accounting-validity field remains
not_assessed for the synthetic examples. `unresolved`/`outside_scope`/`ineligible`
remain explicit assessment results, with no JournalProposal. Input rejection
maps as above. A replay payload carries the original committed receipt and
additional_commit=false; outer disposition replayed, commit observation
not_committed. A lost acknowledgement of a requested write maps to commit_unknown
with unknown observation until the original identity is reconciled.

Empirical justification and capability values are preserved. Forecast validity,
product readiness and human acceptance cannot be inferred from any mapping.
All platform examples are specification examples; their finite arithmetic is
checked separately, and product_implemented remains false.

## Continuous company family and insufficient summaries

The protected Northstar example has one shared unidentified floating fraction
x∈[0,1]. Historical interest of 5 does not identify it when both loan types
charged 5%. The 2025 scenario changes floating interest, profit, tax, cash and
equity together. I3's statement payload must therefore retain their common x,
not just independent endpoint lists. The source package's closed synthetic
scope, teaching tax model, assumed intraperiod ordering and aggregate event
resolution all travel with the result.

Grouping two instruments with the same currency, rate/reset schedule, maturity,
seniority, collateral/guarantee rights and relevant accounting memory may preserve
a specified linear interest query by adding principals. Grouping fixed and
floating instruments only by their historical interest loses the stress exposure
and fails that query. Even the safe grouping must be reconsidered for a new
default, prepayment or instrument-specific tax question. This is a query-scoped
sufficiency rule, not a general compiler proof of economic equivalence.

The real source-backed conflict requested in E05 is still missing: seven inspected
candidates did not establish one. The fourteen synthetic conflict cases specify
behavior but cannot supply that source evidence. P17 must complete the exact
authority/method and real-source obligations. The initial-profile choice and
interface decisions are proposed answers now, with actual evidence and owning
phase in P16's decision records. Open source/method decisions remain proposal
blockers through P19; they are not closed by writing this integration document.

FILE docs/design/proposal/architecture/interfaces-contract-v1.md
# Operations across the financial model, proposed version 1

The interfaces connect an acquired disclosure to a proposed reading, an admitted
financial model, alternative histories and conditional statements. Each operation
names the version it consumes and the authority it needs. In particular, an
extraction service cannot accept its own interpretation, a valuation service
cannot authorize accounting, and a report cannot commit journals. This contract
addresses MC01–MC27 and MC33–MC35, with the software obligations of MC29–MC32.
It specifies exchanges; it does not provide runtime endpoints.

## I1. Common request and response

`OperationRequest` is a portable L1 record with schema
`accdsl.operation.request.v1`. Its body has exactly:

| Field | Required type and meaning |
| --- | --- |
| `operation` | Qualified operation name from I2; no implicit version selection |
| `request_id` | ASCII identifier, stable across retries of the same request |
| `workspace_key` | ASCII identifier for the store namespace |
| `profile_ref`, `signature_ref` | Exact profile and operation-signature Refs |
| `view_ref` | Immutable evidence/review/time view Ref; never a mutable `current` alias |
| `arguments` | Closed tagged record for the named signature, with fields in I2 |
| `execution` | `{mode, budget, environment_ref}`; mode is `specification_example` or `runtime`; budget explicitly states operation count and elapsed-time limits or a reason each is inapplicable |
| `expected_head` | Null for a read, or `{owner_key, state_ref, generation}` for a requested mutation |

All fields are present. Null is allowed only where stated. A caller asking for
the current view first resolves it and receives its revision; mutation compares
that revision again. Arguments contain typed Refs and typed values, never
arbitrary host-language objects. Required closure is the transitive closure of
request dependencies plus schema/package definitions in its lock. A missing
optional source attachment remains a named coverage obligation; a missing
required rule, record, admission or decoder rejects affected use. Schema version,
argument type or unsupported operation is diagnosed before calculation. A
request fingerprint covers the exact portable request; accounting's historical
fingerprint is retained by an explicit legacy adapter, not recomputed as this one.

`OperationResult` has exactly `submission_ref`, `request_ref`, `operation`, `input_view_ref`,
`disposition`, `statuses`, `payload`, `diagnostics`, `coverage`, `unresolved`,
`continuation_ref`, `commit_observation`, `receipt_ref`, and `evidence_mode`.
References are typed. `submission_ref` identifies the preserved exact submitted
bytes and transport/decoder metadata; it always exists, even when decoding fails.
`request_ref` is null until a typed request passes validation. `operation` and
`input_view_ref` are null when the corresponding validated identities are not
available; a diagnostic may quote the untrusted submitted values. Continuation
and receipt references may also be null. `payload` is a tagged
union selected by the signature; rejected input has null payload. `diagnostics`
and `unresolved` are ordered lists (possibly empty). `coverage` contains the
requested domain Ref and completed/unresolved/unsupported/infeasible/cancelled
region Refs, with their partition/overlap relation. Reads may use one singleton
request region; they cannot invent an economic-family denominator. When request
validation prevents establishing the requested domain, coverage is null with
the blocking diagnostic; it is not an empty completed domain. `statuses`
and disposition obey F1. `evidence_mode` repeats specification/runtime, so an
expected `complete` in a document never asserts runtime execution.

`commit_observation` describes the mutation requested by this operation:
`committed`, `not_committed`, or `unknown`. A read returns `not_committed` even
when it inspects an earlier committed receipt. Accounting's replay payload may
say the original event is committed while the outer result says this invocation
made no new commit. The payload must carry `additional_commit=false`; this is
not a contradiction. A successful review or checkpoint mutation has its own
receipt and is never described as an accounting posting.

Transport status and financial status are independent. An HTTP error or client
timeout is not evidence of noncommit. A local Python, CLI or service binding
must preserve the same argument values, input versions and result union. There
is no required network deployment, server framework or user interface in P16.

## I2. Operation signatures and ownership

In this table each listed input is required unless explicitly marked optional.
Lists are explicit even when empty. Domain records retain the detailed fields
in their named contracts; the table does not replace them with untyped prose.

| Versioned operation | Arguments → payload | Effect and controlling contract |
| --- | --- | --- |
| `source.prepare@1` | package manifest, source snapshot, adapter/config lock, prior review, traversal budget and optional continuation → ExtractionPreparation | Acquires/preserves sources and constructs candidates under extraction-v1; no semantic admission |
| `review.propose@1` | target Ref, layer, decision kind, evidence Refs, actor, rationale, replacement Ref or null → ReviewProposal | Candidate construction; accepts no layer |
| `review.commit@1` | ReviewProposal, expected review view/revision → immutable ReviewDecision and new view | Review transaction under evidence E4/persistence P4; admissible action/layer required |
| `time.select@1` | package/view, investor/system/exploratory mode, cutoffs, revision and unknown-time policy → selected assertions, conflicts and temporal obligations | Pure selection under time T1–T6; no invented ingestion or publication time |
| `model.compile@1` | CompileRequest from L4 → candidate Module, source map, diagnostics and target admission/capability report | Candidate construction; no solver or posting |
| `history.construct@1` | admitted Module, opening, scope, template registry, query/horizon, resource budget → HistoryFamily, partition, witnesses and unresolved formulas | H1–H7; witnesses are examples within the family, not its definition |
| `history.refine@1` | frozen family, additional admitted constraint or refinement, dependency view, budget → child family and inclusion relation | Candidate construction; record whether correction replaces constraints instead of intersecting them |
| `history.query@1` | family, typed joint observable, bound/feasibility request, capability manifest → symbolic/partial/exact answer, coverage and endpoint attainability | Pure; unsupported expressions remain explicit |
| `uncertainty.evaluate@1` | exact native uncertainty request, law/attachment/admission and operation-specific event or observation block → native UncertaintyResult and candidate derived bundle | Native admission/attachment/chaining rules; never selects its result automatically |
| `uncertainty.admit@1` | candidate bundle, target time/evidence/purpose, actor, rationale, requested assumption scope, expected selection revision → admitted attachment and decision | Admission transaction; author-stipulated measures keep that label |
| `uncertainty.select@1` | admitted attachment/receipt, rationale and expected selection revision → new selected-view revision | Selection transaction; no probability recomputation |
| `scenario.project@1` | family, exogenous scenario, policy/method lock, horizon/calendar, explicit information policy, resource budget → conditional event/journal/state proposals by history and scenario | Candidate construction; budgets preserve unresolved regions; no historical-book commit |
| `accounting.assess@1` | native assessment request, event, opening, context/time, authority/method, evidence/assumptions and admissions → TreatmentAssessment | Pure accounting assessment; inherited `assess_only` profile cannot post |
| `accounting.propose@1` | eligible assessment, exact request/opening, posting/rounding method → JournalProposal and independent EconomicDelta | Candidate construction; revalidate bindings; unsupported method gives no journal |
| `accounting.commit@1` | validated commit request, eligible assessment, proposal/delta and expected branch head/generation → StateTransitionReceipt | Single atomic transaction in P2; separate signature from assess-only |
| `report.build@1` | frozen branch/family result, statement-map version, interval/view, typed requested statements and presentation policy → joint statement family, reconciliation and coverage | Pure; derive from retained state/journals, no balancing plug or hidden branch selection |
| `record.explain@1` | output Ref, its frozen view, requested lineage depth → source/method/assumption/decision paths and unresolved dependencies | Pure; depth truncation is explicit; cannot substitute today's view |
| `work.resume@1` | checkpoint Ref, original semantic manifest, scheduling budget → operation-specific resumed result | Resume the original operation; checkpoint ownership/atomicity in P3; no model change hidden as resume |
| `store.export@1` | snapshot/root Refs, format/decoder, destination → closed manifest or explicit incomplete export | Derivative publication under P3; no domain mutation |
| `store.import@1` | closed manifest, exact blobs/records, decoder and target namespace → import receipt and original-to-local mappings | Verify before metadata transaction; import alone grants no financial admission |
| `store.migrate@1` | migration request from P5 → preserved originals, new representation, comparison/mapping and receipt | Transaction only after required semantic comparisons; no changed-model-as-format claim |

Compilation and history queries may be pure with respect to committed accounting
state while producing immutable candidates in a scratch or candidate store.
Persisting those candidates requires the named owner and receipt. The effect
classification is not a promise that no bytes are written anywhere.

## I3. Scenario information and joint statements

The initial `ExogenousScenario` specifies dated values or formulas for named
drivers, their domains, units, admissibility assumptions and dependencies. An
`InformationView` exposed to a policy or measurement operation contains only
admitted historical information up to its decision instant and permitted
simulated past. Future simulated values are withheld, even when the scheduler
already knows the full imposed path. Deterministic stress does not by itself
authorize perfect-foresight decisions; a separate assumption must do that.
Observational conditioning uses the uncertainty interface. A causal intervention
requires a specified causal model/replacement operation and is unsupported by
the initial exogenous profile.

The result remains indexed by history, admissible treatment and scenario. Every
statement amount refers to that common index, opening and event sequence.
Cash flow, profit, balance sheet and equity movement are reconciled jointly.
Reporting may return separate conditional answers or a pushforward of an
admitted law. It cannot create one statement from independent minima/maxima
that occur in incompatible histories. Aggregating an axis requires a pinned
disjoint/exhaustive partition or returns an unallocated residual with a reason.
An unsupported tax/lease/FX method makes dependent lines unresolved; unaffected
amounts remain available with their dependence stated.

## I4. Extension boundary and adapters

An `ExtensionPackage` declares `{package_key, version, record_schemas,
operation_signatures, supported_contexts, state_requirements, authority_refs,
method_refs, capability_requirements, migration_refs, example_refs}` and pins
every member. Empty authority lists mean no accounting-authority claim, not
universal eligibility. Callers verify the method's dated entity/instrument/basis
scope and uncertainty admission separately from schema loading.

Corporate records retain receivable/payable terms, inventory lots and cost
method, assets and depreciation memory, tax bases, leases, debt/equity rights
and contingencies. Groups retain legal entity, control evidence, dated perimeter,
ownership/NCI, functional/presentation currencies and elimination links. Banks
add cash-flow terms, effective rate, credit-risk stage, default/cure history,
collateral/guarantees and prudential-rule context; prudential capital is not
accounting equity. Insurers add coverage units, cohort/group eligibility,
fulfilment cash-flow assumptions, discount/risk adjustment, CSM/loss component,
reinsurance and service history. These are structural obligations; P17 must
specify their method fields, transitions, authority and matched cases before an
operation using them becomes supported.

An extraction adapter returns located candidates; a contract scheduler returns
dated contractual events; a valuation adapter returns a quantity with method,
currency/date and numerical evidence; an accounting method returns an assessment
and proposed entries; a ledger adapter exchanges concrete entries/receipts.
None inherits another's authority. Each adapter manifest identifies upstream
version/license, supported subset, input/output schema mapping, calendar/unit/
rounding transformations, preserved lineage, information loss and unavailable-
backend behavior. Lost economically relevant fields veto that exchange. Retaining
raw upstream output permits inspection but does not repair lost meaning.
P17 owns pinned official-interface/license inspection and executable adapter
feasibility; existing exploratory tool presence is not completed integration.

## I5. Precedence and versioning

The active P16 architecture index pins its contracts. Domain-specific validation
and accounting/uncertainty vocabulary take precedence within their versioned
native interfaces. Platform v1 adds explicit wrappers and cross-contract rules;
it does not rewrite saved native receipts. `architecture-integration-v1.md`
records status mapping and the precise historical rules that are superseded.
A later amendment prevails only for the fields and profile it expressly names;
date alone or a file named “latest” grants no precedence.

Two conflicts are resolved explicitly. The stable accounting event key is P2's
entity/book/branch/business-event key, not an event-version or transient-run key.
For native assessment validation, the established parse → recognizable
dependencies → shape → source versions → bindings sequence prevails over a
generic platform ordering. A wrapper may reject its own malformed envelope
first; it cannot expose a receipt before native validation. New portable-only
operations use F2's order. This preserves historical outcomes without letting
the old generic Core 0 contracts silently select defaults for new domains.

IX01–IX06 in the shared example file cover a connected company, changed stress,
an unresolved operating input, later-information rejection, overlapping report
classes and a sector call without an eligible method. Together with the native
complete accounting exchanges they make the contracts' interaction inspectable.
They specify results; the document calculation verifies only finite arithmetic
and reference consistency. Compatible implementations still require actual
frontend, backend, storage and recovery conformance evidence.

FILE docs/design/proposal/architecture/initial-profile-v1.md
# Proposed first implementation profile

The first implementation should connect a company's disclosures, alternative
histories, economic events and complete statements. A financing-only example
would leave the working-capital, operating-asset, tax and reporting interfaces
untested. The proposed domain is therefore a bounded corporate company; the
initial authoring interface is typed constructors into the portable IR, with a
matched, bounded textual notation. These are separate choices. This proposal
addresses MC01–MC35 without asserting that every requested method is now supplied.

## Scope and the alternatives compared

P15 compared four candidates. Corporate/shared-IR and typed-library-first can
have exactly the same domain and differ only in authoring. Instrument-first
would make financing lifecycle work earlier, but cannot meet the whole-company
goal until the operating-company continuation is added. Broad sector-first
would require bank, insurance, group and cross-standard methods at entry, with
more currently unresolved authority. The chosen order exposes interactions in
one connected company while specifying extension requirements now. It does not
establish that this order is cheapest, fastest or easiest to use.

The profile is `CorporateJointHistory/1`. It includes one legal entity and book
per branch, a declared domestic functional currency, annual/interim evidence,
multiple source vintages and reviewed alternatives. Context and schema design
retain multiple-entity/perimeter/currency fields so an unsupported operation
is explicit. “One book” is an execution scope, not a global uniqueness rule for
companies or future groups. A company with subsidiaries, leases or contingencies
cannot be admitted as a closed single-company model merely by omitting them.

Evidence preparation must account for the declared statement and note inventory,
incorporated references and unresolved source units. Readings, interpretations,+assumptions and treatment eligibility are separate layers. Investor-information,
system-as-of and exploratory archival questions use the time contract's distinct
admission rules. Exact financial quantities, source precision and conditional
rounding assumptions remain distinct. Source limitations accompany each dependent
query; there is no global “complete” flag inferred from pages parsed.

The initial economic methods must connect sales/delivery/collection, purchases/
inventory/cost of sales/payables, payroll, tangible-asset additions/depreciation,
simple debt/equity/dividends and a declared simple tax model. They produce profit,
balance sheet, cash flows and changes in equity from the same event histories.
The simple tax model is an authored teaching assumption; actual tax requires
P17's jurisdictional method. Northstar supplies a closed synthetic example,
not proof that these methods cover Apple or a representative real issuer.

The initial reconstruction method is the history contract's admitted-template,
rational affine family with finite choices and bounded integers. It preserves
unidentified debt mix, unknown payment timing and other query-relevant state.
The declared half-year event slots do not recover invoices or prove daily
liquidity. Querying a finer horizon requires refinement or an unresolved answer.
Exact bounds require whole-domain reasoning and endpoint attainability; search
witnesses and explored extrema are not promoted to complete families or bounds.

Scenario execution initially supports imposed exogenous paths with explicit
behavior and information restrictions. Joint finite rational probability is an
optional extension under the admitted-measure contract. Unweighted alternatives
remain valid initial results. Continuous inference, causal interventions,
calibration and empirically validated forecasts require P17 methods and later
execution evidence. An imposed interest-rate stress does not reweight historical
contract alternatives or become a probability forecast.

Typed constructors must express all included records without embedding opaque
Python functions. The bounded text frontend initially covers the matched debt
and constraint fragment; unsupported declarations produce located diagnostics.
Textual whole-company authoring is a later frontend obligation, with the same
domain semantics and validation. Deferring that parser does not defer the
whole-company typed model, the DSL design or the portable representation.

## Acceptance examples and limits

The primary integrated example is the protected Northstar disclosure fixture
and chapter, interpreted through the new contracts. Its opening and half-year
events support independently calculable statements and a continuous debt family.
For the 2025 stress, let x be the floating fraction. The common joint result is:

| Quantity | Conditional value in currency units |
| --- | --- |
| Debt interest | 5 + 2x |
| Profit before tax | 82 − 2x |
| Tax at the stipulated 20% rate | 16.4 − 0.4x |
| Profit | 65.6 − 1.6x |
| Operating cash flow | 48.6 − 1.6x |
| Closing cash | 95.2 − 1.6x |
| Closing equity | 148.2 − 1.6x |
| Closing assets | 288.2 − 1.6x |

Here 0 ≤ x ≤ 1, payables plus debt are 140, receivables 55, inventory 40 and
net plant 98. Every row uses the same x. The endpoints are not equiprobable
scenarios, and the output is not a rectangular box of independently selectable
amounts. Changing the floating rate to 9% changes the interest slope to 4 and
the cash/profit/equity slopes to −3.2; independent arithmetic must detect that
change even if both frontends share an erroneous constant.

Acceptance of the specification requires exact expected exchanges for the
following connected cases, with preserved sources and explicit assumptions:

1. Annual/interim source inventory, missing incorporated reference, alternative
   narrative translation, rounding unknowns and separately admitted constraints.
2. Joint working-capital reconstruction and unidentified fixed/floating debt
   mix, with known aggregate movements and unknown intraperiod timing.
3. Conditional 2025 events, eligible treatments, balanced proposals, reconciled
   complete statements and debt-mix dependence, plus a changed-rate control.
4. Original versus corrected interim information views without later-information
   leakage; no automatic source-derived accounting permission.
5. Partial or unsupported region preservation, unavailable methods, exact versus
   approximate capabilities and unweighted versus admitted-measure queries.
6. Valid replay, changed-payload conflict, concurrent stale-head rejection,
   unknown commit recovery, review correction/invalidation and failed migration.

The shared platform examples exercise these connections alongside retained
evidence/time/history/uncertainty/accounting examples. A bounded real filing
case must retain its full declared inventory and all unformalized disclosures;
Apple's partial source preparation cannot satisfy that case by itself. E05's
real source-backed conflict and P17's dated accounting methods remain proposal
work. A document calculation satisfies only the finite arithmetic part of this
list. Runtime acceptance additionally needs implemented source/typed lowering,
solver/simulator, transaction fault tests and adapter checks. Human understanding
and accounting/forecast validity have separate evidence.

## Dependencies and retained later work

Implementation should proceed in dependency order, after the proposal has been
completed and the user has authorized implementation:

1. Versioned record definitions, exact values/context, source byte retention,
   dependency closure and pinned package/schema loading.
2. Review and time selection, provenance/invalidation, immutable views and the
   initial transaction store's receipt/replay behavior.
3. Typed constructors and validation; the matched debt text fragment and source
   maps; independent expected IR and adverse input cases.
4. Admitted history templates, joint affine constraints, finite-choice search,
   partial checkpoints, typed capability failures and query-dependent refinement.
5. The connected corporate economic and accounting methods with their actual
   authority, event scheduling and information boundaries; statement mapping.
6. The integrated company case, source corrections, replay/recovery and bounded
   real-filing coverage; then optional justified measure operations and adapters.

P17 must complete actual source-grounded methods for corporate operations,
bonds/equity, groups/FX, IFRS/US GAAP/ASBE, banks and insurers. The extension
records in I4 make dependencies visible; they do not count as method completion.
Examples must include a changed group perimeter, intercompany elimination and
FX translation, credit loss and credit-risk memory, and insurance service/
measurement memory. Imported official rules and software interfaces require
located inspected sources and explicit limits. General nonlinear inference,
calibrated forecasting, multiwriter throughput and distributed durability are
later implementation/evaluation obligations, not inferred from prototype tests.

P18 integrates the completed methods and contracts into the governing LaTeX
manuscript and inspects its actual rendering. P19 assesses the full proposal
against MC01–MC35 and G1–G18. The current architecture may be judged specified
within its scope while those later proposal blockers remain open. Neither that
judgment nor a successful PDF build authorizes product implementation.

ACTUAL NATIVE CHAINING RECORD PROJECTIONS (only verbose closure/hash lists omitted):
{"UC.law@1":{"id":"UC.law","version":1,"predecessor":null,"family_ref":"UC.family@1","view_ref":"UC.view@1","time_ref":"UC.time@1","purpose":"scenario","sample_space":["a","b","c"],"masses":{"a":"1/2","b":"1/3","c":"1/6"},"coordinate_refs":["UC.expense@1"],"justification":"stipulated","calibration_information_atoms":[]},"UC.likelihood@1":{"id":"UC.likelihood","version":1,"predecessor":null,"family_ref":"UC.family@1","observation_refs":["UC.observation@1"],"time_ref":"UC.time@1","values":{"a":"1/2","b":"1","c":"0"},"base_measure":"counting_measure_on_discrete_observation_space","conditional_on_atoms":[],"incremental_atoms":["measurement.D"],"justification":"stipulated observation model, no empirical support"},"CH.admission.D@1":{"id":"CH.admission.D","version":1,"predecessor":null,"request_ref":"CH.admit_request.D@1","view_ref":"CH.view.UC02@1","model_ref":"CH.law.UC02@1","candidate_ref":"CH.candidate.UC02@1","time_ref":"UC.time@1","evidence_view_ref":"UC.evidence@1","purpose":"scenario","decision":"admitted_as_authored_assumption","authority":"fixture_author","rationale":"no empirical or accounting approval","dependencies":["CH.admit_request.D@1","CH.candidate.UC02@1","CH.law.UC02@1","CH.lineage.UC02@1","CH.request.UC02@1","CH.result.UC02@1","CH.view.UC02@1","UC.admission@1","UC.attachment@1","UC.evidence@1","UC.expense@1","UC.family@1","UC.law@1","UC.likelihood@1","UC.observation@1","UC.source@1","UC.time@1","UC.view@1"]},"CH.attached.D@1":{"id":"CH.attached.D","version":1,"predecessor":null,"view_ref":"CH.view.UC02@1","model_ref":"CH.law.UC02@1","family_ref":"UC.family@1","admission_ref":"CH.admission.D@1","candidate_ref":"CH.candidate.UC02@1","time_ref":"UC.time@1","evidence_view_ref":"UC.evidence@1","purpose":"scenario","status":"attached_assumption","admission_receipt_ref":"CH.admission_receipt.D@1","dependencies":["CH.admission.D@1","CH.admission_receipt.D@1","CH.admit_request.D@1","CH.candidate.UC02@1","CH.law.UC02@1","CH.lineage.UC02@1","CH.request.UC02@1","CH.result.UC02@1","CH.view.UC02@1","UC.admission@1","UC.attachment@1","UC.evidence@1","UC.expense@1","UC.family@1","UC.law@1","UC.likelihood@1","UC.observation@1","UC.source@1","UC.time@1","UC.view@1"]},"CH.kernel.DE@1":{"id":"CH.kernel.DE","version":1,"predecessor":null,"family_ref":"UC.family@1","observation_refs":["UC.observation@1","CH.observation.E@1"],"binary_observations":["D","E"],"p_D_1":{"a":"1/2","b":"1","c":"0"},"p_E_1_given_D_1":{"a":"1","b":"1/2","c":"1"},"p_E_1_given_D_0":{"a":"1/4","b":"1/4","c":"1/4"},"complements":"P(0)=1-P(1)","justification":"stipulated conditional kernel including null branches; no independence claim","dependencies":["CH.observation.E@1","CH.source.E@1","UC.admission@1","UC.evidence@1","UC.expense@1","UC.family@1","UC.observation@1","UC.source@1","UC.time@1"]},"CH.likelihood.EgivenD@1":{"id":"CH.likelihood.EgivenD","version":1,"predecessor":null,"family_ref":"UC.family@1","observation_refs":["CH.observation.E@1"],"conditioning_observation_refs":["UC.observation@1"],"kernel_ref":"CH.kernel.DE@1","time_ref":"UC.time@1","purpose":"scenario","base_measure":"counting on binary E","values":{"a":"1","b":"1/2","c":"1"},"conditional_on_atoms":["measurement.D"],"incremental_atoms":["measurement.E"],"justification":"stipulated conditional model, not an unconditional likelihood","dependencies":["CH.kernel.DE@1","CH.observation.E@1","CH.source.E@1","UC.admission@1","UC.evidence@1","UC.expense@1","UC.family@1","UC.observation@1","UC.source@1","UC.time@1"]},"CH.request.D_then_E@1":{"id":"CH.request.D_then_E","version":1,"predecessor":null,"request_id":"CH.D_then_E","operation":"likelihood_update","family_ref":"UC.family@1","view_ref":"CH.view.UC02@1","model_ref":"CH.law.UC02@1","attachment_ref":"CH.attached.D@1","admission_ref":"CH.admission.D@1","time_ref":"UC.time@1","evidence_view_ref":"UC.evidence@1","purpose":"scenario","information_cutoff":"2026-03-01T00:00:00Z","evidence_cutoff":"2026-03-01T00:00:00Z","query":{"likelihood_ref":"CH.likelihood.EgivenD@1","observation_ref":"CH.observation.E@1"},"provenance":"authored finite example; specified only","admission_receipt_ref":"CH.admission_receipt.D@1","dependencies":["CH.admission.D@1","CH.admission_receipt.D@1","CH.admit_request.D@1","CH.attached.D@1","CH.candidate.UC02@1","CH.kernel.DE@1","CH.law.UC02@1","CH.likelihood.EgivenD@1","CH.lineage.UC02@1","CH.observation.E@1","CH.request.UC02@1","CH.result.UC02@1","CH.source.E@1","CH.view.UC02@1","UC.admission@1","UC.attachment@1","UC.evidence@1","UC.expense@1","UC.family@1","UC.law@1","UC.likelihood@1","UC.observation@1","UC.source@1","UC.time@1","UC.view@1"]},"CH.evidence.corrected@1":{"id":"CH.evidence.corrected","version":1,"predecessor":null,"predecessor_ref":"UC.evidence@1","time_ref":"CH.time.corrected@1","superseded_observation_ref":"UC.observation@1","superseded_view_refs":["CH.view.UC02@1"],"invalidated_descendant_refs":["CH.view.D_then_E@1"],"scope":"new corrected reading; prior views frozen; E conditional model requires revalidation","dependencies":["CH.admission.D@1","CH.admission_receipt.D@1","CH.admit_request.D@1","CH.attached.D@1","CH.candidate.D_then_E@1","CH.candidate.UC02@1","CH.kernel.DE@1","CH.law.D_then_E@1","CH.law.UC02@1","CH.likelihood.EgivenD@1","CH.lineage.D_then_E@1","CH.lineage.UC02@1","CH.observation.E@1","CH.request.D_then_E@1","CH.request.UC02@1","CH.result.UC02@1","CH.source.E@1","CH.time.corrected@1","CH.view.D_then_E@1","CH.view.UC02@1","UC.admission@1","UC.attachment@1","UC.evidence@1","UC.expense@1","UC.family@1","UC.law@1","UC.likelihood@1","UC.observation@1","UC.source@1","UC.time@1","UC.view@1"]},"CH.likelihood.corrected@1":{"id":"CH.likelihood.corrected","version":1,"predecessor":null,"origin_ref":"UC.correctedLikelihood@1","family_ref":"UC.family@1","observation_refs":["CH.observation.corrected@1"],"time_ref":"CH.time.corrected@1","purpose":"scenario","base_measure":"counting on binary corrected D","values":{"a":"1","b":"1/2","c":"1"},"conditional_on_atoms":[],"incremental_atoms":["measurement.D"],"justification":"stipulated corrected binary likelihood; complements sum to one","dependencies":["CH.admission.D@1","CH.admission.corrected_inputs@1","CH.admission_receipt.D@1","CH.admit_request.D@1","CH.attached.D@1","CH.candidate.D_then_E@1","CH.candidate.UC02@1","CH.evidence.corrected@1","CH.kernel.DE@1","CH.law.D_then_E@1","CH.law.UC02@1","CH.likelihood.EgivenD@1","CH.lineage.D_then_E@1","CH.lineage.UC02@1","CH.observation.E@1","CH.observation.corrected@1","CH.request.D_then_E@1","CH.request.UC02@1","CH.result.UC02@1","CH.source.E@1","CH.time.corrected@1","CH.view.D_then_E@1","CH.view.UC02@1","UC.admission@1","UC.attachment@1","UC.corrected@1","UC.correctedLikelihood@1","UC.evidence@1","UC.expense@1","UC.family@1","UC.law@1","UC.likelihood@1","UC.observation@1","UC.source@1","UC.time@1","UC.view@1"]},"CH.request.UC08@1":{"id":"CH.request.UC08","version":1,"predecessor":null,"request_id":"CH.UC08","operation":"correct_and_rebase","family_ref":"UC.family@1","view_ref":"UC.view@1","model_ref":"UC.law@1","attachment_ref":"UC.attachment@1","admission_ref":"UC.admission@1","time_ref":"UC.time@1","evidence_view_ref":"UC.evidence@1","purpose":"scenario","information_cutoff":"2026-03-01T00:00:00Z","evidence_cutoff":"2026-03-01T00:00:00Z","query":{"base_view_ref":"UC.view@1","base_model_ref":"UC.law@1","superseded_view_ref":"CH.view.UC02@1","superseded_block_ref":"UC.observation@1","observation_ref":"CH.observation.corrected@1","likelihood_ref":"CH.likelihood.corrected@1","replay_incremental_refs":[],"invalidated_descendant_refs":["CH.view.D_then_E@1"]},"provenance":"authored finite example; specified only","target_time_ref":"CH.time.corrected@1","target_evidence_view_ref":"CH.evidence.corrected@1","target_admission_ref":"CH.admission.corrected_inputs@1","dependencies":["CH.admission.D@1","CH.admission.corrected_inputs@1","CH.admission_receipt.D@1","CH.admit_request.D@1","CH.attached.D@1","CH.candidate.D_then_E@1","CH.candidate.UC02@1","CH.evidence.corrected@1","CH.kernel.DE@1","CH.law.D_then_E@1","CH.law.UC02@1","CH.likelihood.EgivenD@1","CH.likelihood.corrected@1","CH.lineage.D_then_E@1","CH.lineage.UC02@1","CH.observation.E@1","CH.observation.corrected@1","CH.request.D_then_E@1","CH.request.UC02@1","CH.result.UC02@1","CH.source.E@1","CH.time.corrected@1","CH.view.D_then_E@1","CH.view.UC02@1","UC.admission@1","UC.attachment@1","UC.corrected@1","UC.correctedLikelihood@1","UC.evidence@1","UC.expense@1","UC.family@1","UC.law@1","UC.likelihood@1","UC.observation@1","UC.source@1","UC.time@1","UC.view@1"]},"CH.result.UC02@1":{"id":"CH.result.UC02","version":1,"predecessor":null,"request_ref":"CH.request.UC02@1","old_view_ref":"UC.view@1","proposed_view_ref":"CH.view.UC02@1","model_ref":"CH.law.UC02@1","attachment_ref":"CH.candidate.UC02@1","lineage_ref":"CH.lineage.UC02@1","disposition":"SPECIFIED_RESULT","payload":{"normalizer":"7/12","unnormalized":{"a":"1/4","b":"1/3","c":"0"},"posterior":{"a":"3/7","b":"4/7","c":"0"},"consumed_information_atoms":["measurement.D"]},"domain_writes":["CH.view.UC02@1","CH.law.UC02@1","CH.candidate.UC02@1","CH.lineage.UC02@1"],"state_before":{"family_ref":"UC.family@1","selected_view_ref":"UC.view@1","attachment_ref":"UC.attachment@1","model_ref":"UC.law@1","selection_revision":0},"state_after":{"family_ref":"UC.family@1","selected_view_ref":"UC.view@1","attachment_ref":"UC.attachment@1","model_ref":"UC.law@1","selection_revision":0},"structural_validity":"valid","mathematical_status":"satisfied","empirical_justification":"stipulated","capability_status":"specified_only_no_runtime","computation_status":"specified_exact","accounting_validity":"not_assessed","human_acceptance":"pending","reason_codes":[]},"CH.result.D_then_E@1":{"id":"CH.result.D_then_E","version":1,"predecessor":null,"request_ref":"CH.request.D_then_E@1","old_view_ref":"CH.view.UC02@1","proposed_view_ref":"CH.view.D_then_E@1","model_ref":"CH.law.D_then_E@1","attachment_ref":"CH.candidate.D_then_E@1","lineage_ref":"CH.lineage.D_then_E@1","disposition":"SPECIFIED_RESULT","payload":{"normalizer":"5/7","unnormalized":{"a":"3/7","b":"2/7","c":"0"},"posterior":{"a":"3/5","b":"2/5","c":"0"},"consumed_information_atoms":["measurement.D","measurement.E"]},"domain_writes":["CH.view.D_then_E@1","CH.law.D_then_E@1","CH.candidate.D_then_E@1","CH.lineage.D_then_E@1"],"state_before":{"family_ref":"UC.family@1","selected_view_ref":"CH.view.UC02@1","attachment_ref":"CH.attached.D@1","model_ref":"CH.law.UC02@1","selection_revision":1},"state_after":{"family_ref":"UC.family@1","selected_view_ref":"CH.view.UC02@1","attachment_ref":"CH.attached.D@1","model_ref":"CH.law.UC02@1","selection_revision":1},"structural_validity":"valid","mathematical_status":"satisfied","empirical_justification":"stipulated","capability_status":"specified_only_no_runtime","computation_status":"specified_exact","accounting_validity":"not_assessed","human_acceptance":"pending","reason_codes":[]},"CH.result.A_then_A@1":{"id":"CH.result.A_then_A","version":1,"predecessor":null,"request_ref":"CH.request.A_then_A@1","old_view_ref":"CH.view.UC01@1","proposed_view_ref":"CH.view.A_then_A@1","model_ref":"CH.law.A_then_A@1","attachment_ref":"CH.candidate.A_then_A@1","lineage_ref":"CH.lineage.A_then_A@1","disposition":"SPECIFIED_RESULT","payload":{"normalizer":"1","unnormalized":{"a":"3/5","b":"2/5","c":"0"},"posterior":{"a":"3/5","b":"2/5","c":"0"},"consumed_information_atoms":[]},"domain_writes":["CH.view.A_then_A@1","CH.law.A_then_A@1","CH.candidate.A_then_A@1","CH.lineage.A_then_A@1"],"state_before":{"family_ref":"UC.family@1","selected_view_ref":"UC.view@1","attachment_ref":"UC.attachment@1","model_ref":"UC.law@1","selection_revision":0},"state_after":{"family_ref":"UC.family@1","selected_view_ref":"UC.view@1","attachment_ref":"UC.attachment@1","model_ref":"UC.law@1","selection_revision":0},"structural_validity":"valid","mathematical_status":"satisfied","empirical_justification":"stipulated","capability_status":"specified_only_no_runtime","computation_status":"specified_exact","accounting_validity":"not_assessed","human_acceptance":"pending","reason_codes":[]},"CH.result.UC08@1":{"id":"CH.result.UC08","version":1,"predecessor":null,"request_ref":"CH.request.UC08@1","old_view_ref":"UC.view@1","proposed_view_ref":"CH.view.UC08@1","model_ref":"CH.law.UC08@1","attachment_ref":"CH.candidate.UC08@1","lineage_ref":"CH.lineage.UC08@1","disposition":"SPECIFIED_RESULT","payload":{"normalizer":"5/6","unnormalized":{"a":"1/2","b":"1/6","c":"1/6"},"posterior":{"a":"3/5","b":"1/5","c":"1/5"},"consumed_information_atoms":["measurement.D"]},"domain_writes":["CH.view.UC08@1","CH.law.UC08@1","CH.candidate.UC08@1","CH.lineage.UC08@1"],"state_before":{"family_ref":"UC.family@1","selected_view_ref":"CH.view.UC02@1","attachment_ref":"CH.attached.D@1","model_ref":"CH.law.UC02@1","selection_revision":1},"state_after":{"family_ref":"UC.family@1","selected_view_ref":"CH.view.UC02@1","attachment_ref":"CH.attached.D@1","model_ref":"CH.law.UC02@1","selection_revision":1},"structural_validity":"valid","mathematical_status":"satisfied","empirical_justification":"stipulated","capability_status":"specified_only_no_runtime","computation_status":"specified_exact","accounting_validity":"not_assessed","human_acceptance":"pending","reason_codes":[]},"CH.rejection.candidate_only@2":{"id":"CH.rejection.candidate_only","version":2,"predecessor":"CH.rejection.candidate_only@1","request_ref":"CH.request.candidate_only@1","disposition":"REQUEST_INVALID","reason_codes":["ADMISSION_REQUIRED"],"domain_writes":[],"audit_writes":["submitted_bytes","rejection_receipt"],"state_before":{"family_ref":"UC.family@1","selected_view_ref":"UC.view@1","attachment_ref":"UC.attachment@1","model_ref":"UC.law@1","selection_revision":0},"state_after":{"family_ref":"UC.family@1","selected_view_ref":"UC.view@1","attachment_ref":"UC.attachment@1","model_ref":"UC.law@1","selection_revision":0},"proposed_view_ref":null,"model_ref":null,"mathematical_status":"unresolved","capability_status":"specified_only_no_runtime","human_acceptance":"pending","structural_validity":"invalid","computation_status":"not_computed","empirical_justification":"not_established","accounting_validity":"not_assessed","provenance":{"kind":"specification_correction_not_runtime_replay","source_fixture":{"path":"docs/design/proposal/architecture/uncertainty-chaining-fixtures-v1.json","sha256":"70644fee4969843bdfee72e5a3d5a698c3acf1327438df30b8562fda3a949e3c","locator":"records[CH.rejection.candidate_only@1]"},"review":{"path":"data/accounting-master/runs/20261005T120206-bdb3a74d/P16/execution-0/review_result-0.response.json","sha256":"450e65d44a56c289ee9d13fdb77f36a14d00408c1057e021446f2d9fab38d0c8","locator":"issues[0]"},"contract":{"path":"docs/design/proposal/architecture/uncertainty-rejection-status-contract-v1.md","sha256":"cc5ec2bd69cf4ba0bf4f0d7fb6e6d668cf7975244afa4464fbb7e412c4eeee8c","locator":"Sections 2–4"},"reason":"Restore governing status vocabulary; preserve request and rejection consequences."}},"CH.rejection.duplicate_D@2":{"id":"CH.rejection.duplicate_D","version":2,"predecessor":"CH.rejection.duplicate_D@1","request_ref":"CH.request.duplicate_D@1","disposition":"REQUEST_INVALID","reason_codes":["DUPLICATE_INFORMATION"],"domain_writes":[],"audit_writes":["submitted_bytes","rejection_receipt"],"state_before":{"family_ref":"UC.family@1","selected_view_ref":"CH.view.UC02@1","attachment_ref":"CH.attached.D@1","model_ref":"CH.law.UC02@1","selection_revision":1},"state_after":{"family_ref":"UC.family@1","selected_view_ref":"CH.view.UC02@1","attachment_ref":"CH.attached.D@1","model_ref":"CH.law.UC02@1","selection_revision":1},"proposed_view_ref":null,"model_ref":null,"mathematical_status":"unresolved","capability_status":"specified_only_no_runtime","human_acceptance":"pending","structural_validity":"invalid","computation_status":"not_computed","empirical_justification":"not_established","accounting_validity":"not_assessed","provenance":{"kind":"specification_correction_not_runtime_replay","source_fixture":{"path":"docs/design/proposal/architecture/uncertainty-chaining-fixtures-v1.json","sha256":"70644fee4969843bdfee72e5a3d5a698c3acf1327438df30b8562fda3a949e3c","locator":"records[CH.rejection.duplicate_D@1]"},"review":{"path":"data/accounting-master/runs/20261005T120206-bdb3a74d/P16/execution-0/review_result-0.response.json","sha256":"450e65d44a56c289ee9d13fdb77f36a14d00408c1057e021446f2d9fab38d0c8","locator":"issues[0]"},"contract":{"path":"docs/design/proposal/architecture/uncertainty-rejection-status-contract-v1.md","sha256":"cc5ec2bd69cf4ba0bf4f0d7fb6e6d668cf7975244afa4464fbb7e412c4eeee8c","locator":"Sections 2–4"},"reason":"Restore governing status vocabulary; preserve request and rejection consequences."}},"CH.rejection.stale_law@2":{"id":"CH.rejection.stale_law","version":2,"predecessor":"CH.rejection.stale_law@1","request_ref":"CH.request.stale_law@1","disposition":"REQUEST_INVALID","reason_codes":["LAW_VIEW_ATTACHMENT_MISMATCH"],"domain_writes":[],"audit_writes":["submitted_bytes","rejection_receipt"],"state_before":{"family_ref":"UC.family@1","selected_view_ref":"CH.view.UC02@1","attachment_ref":"CH.attached.D@1","model_ref":"CH.law.UC02@1","selection_revision":1},"state_after":{"family_ref":"UC.family@1","selected_view_ref":"CH.view.UC02@1","attachment_ref":"CH.attached.D@1","model_ref":"CH.law.UC02@1","selection_revision":1},"proposed_view_ref":null,"model_ref":null,"mathematical_status":"unresolved","capability_status":"specified_only_no_runtime","human_acceptance":"pending","structural_validity":"invalid","computation_status":"not_computed","empirical_justification":"not_established","accounting_validity":"not_assessed","provenance":{"kind":"specification_correction_not_runtime_replay","source_fixture":{"path":"docs/design/proposal/architecture/uncertainty-chaining-fixtures-v1.json","sha256":"70644fee4969843bdfee72e5a3d5a698c3acf1327438df30b8562fda3a949e3c","locator":"records[CH.rejection.stale_law@1]"},"review":{"path":"data/accounting-master/runs/20261005T120206-bdb3a74d/P16/execution-0/review_result-0.response.json","sha256":"450e65d44a56c289ee9d13fdb77f36a14d00408c1057e021446f2d9fab38d0c8","locator":"issues[0]"},"contract":{"path":"docs/design/proposal/architecture/uncertainty-rejection-status-contract-v1.md","sha256":"cc5ec2bd69cf4ba0bf4f0d7fb6e6d668cf7975244afa4464fbb7e412c4eeee8c","locator":"Sections 2–4"},"reason":"Restore governing status vocabulary; preserve request and rejection consequences."}},"CH.rejection.stale_attachment@2":{"id":"CH.rejection.stale_attachment","version":2,"predecessor":"CH.rejection.stale_attachment@1","request_ref":"CH.request.stale_attachment@1","disposition":"REQUEST_INVALID","reason_codes":["LAW_VIEW_ATTACHMENT_MISMATCH"],"domain_writes":[],"audit_writes":["submitted_bytes","rejection_receipt"],"state_before":{"family_ref":"UC.family@1","selected_view_ref":"CH.view.UC02@1","attachment_ref":"CH.attached.D@1","model_ref":"CH.law.UC02@1","selection_revision":1},"state_after":{"family_ref":"UC.family@1","selected_view_ref":"CH.view.UC02@1","attachment_ref":"CH.attached.D@1","model_ref":"CH.law.UC02@1","selection_revision":1},"proposed_view_ref":null,"model_ref":null,"mathematical_status":"unresolved","capability_status":"specified_only_no_runtime","human_acceptance":"pending","structural_validity":"invalid","computation_status":"not_computed","empirical_justification":"not_established","accounting_validity":"not_assessed","provenance":{"kind":"specification_correction_not_runtime_replay","source_fixture":{"path":"docs/design/proposal/architecture/uncertainty-chaining-fixtures-v1.json","sha256":"70644fee4969843bdfee72e5a3d5a698c3acf1327438df30b8562fda3a949e3c","locator":"records[CH.rejection.stale_attachment@1]"},"review":{"path":"data/accounting-master/runs/20261005T120206-bdb3a74d/P16/execution-0/review_result-0.response.json","sha256":"450e65d44a56c289ee9d13fdb77f36a14d00408c1057e021446f2d9fab38d0c8","locator":"issues[0]"},"contract":{"path":"docs/design/proposal/architecture/uncertainty-rejection-status-contract-v1.md","sha256":"cc5ec2bd69cf4ba0bf4f0d7fb6e6d668cf7975244afa4464fbb7e412c4eeee8c","locator":"Sections 2–4"},"reason":"Restore governing status vocabulary; preserve request and rejection consequences."}},"CH.rejection.correction_on_posterior@2":{"id":"CH.rejection.correction_on_posterior","version":2,"predecessor":"CH.rejection.correction_on_posterior@1","request_ref":"CH.request.correction_on_posterior@1","disposition":"REQUEST_INVALID","reason_codes":["CORRECTION_REQUIRES_REBASE"],"domain_writes":[],"audit_writes":["submitted_bytes","rejection_receipt"],"state_before":{"family_ref":"UC.family@1","selected_view_ref":"CH.view.UC02@1","attachment_ref":"CH.attached.D@1","model_ref":"CH.law.UC02@1","selection_revision":1},"state_after":{"family_ref":"UC.family@1","selected_view_ref":"CH.view.UC02@1","attachment_ref":"CH.attached.D@1","model_ref":"CH.law.UC02@1","selection_revision":1},"proposed_view_ref":null,"model_ref":null,"mathematical_status":"unresolved","capability_status":"specified_only_no_runtime","human_acceptance":"pending","structural_validity":"invalid","computation_status":"not_computed","empirical_justification":"not_established","accounting_validity":"not_assessed","provenance":{"kind":"specification_correction_not_runtime_replay","source_fixture":{"path":"docs/design/proposal/architecture/uncertainty-chaining-fixtures-v1.json","sha256":"70644fee4969843bdfee72e5a3d5a698c3acf1327438df30b8562fda3a949e3c","locator":"records[CH.rejection.correction_on_posterior@1]"},"review":{"path":"data/accounting-master/runs/20261005T120206-bdb3a74d/P16/execution-0/review_result-0.response.json","sha256":"450e65d44a56c289ee9d13fdb77f36a14d00408c1057e021446f2d9fab38d0c8","locator":"issues[0]"},"contract":{"path":"docs/design/proposal/architecture/uncertainty-rejection-status-contract-v1.md","sha256":"cc5ec2bd69cf4ba0bf4f0d7fb6e6d668cf7975244afa4464fbb7e412c4eeee8c","locator":"Sections 2–4"},"reason":"Restore governing status vocabulary; preserve request and rejection consequences."}}}

MATCHED_ALTERNATIVE
{"explicit_bundle_ref": "CH.result.D_then_E@1", "lazy_expression": "normalize(normalize(P * L_D) * L_E_given_D)", "direct_joint_expression": "normalize(P * L_D * L_E_given_D)", "joint_normalizer": "5/12", "expected_masses": {"a": "3/5", "b": "2/5", "c": "0"}, "status": "exact finite identity only; no storage/runtime comparison"}
ACTUAL NORTHSTAR FINANCIAL INPUTS AND EXPECTATIONS:
{"schema":"accdsl-design-fixture/1","entity":"Northstar Components (synthetic)","currency":"USD","units":"one currency unit","basis":"DemoCorporate/1; not GAAP certification","disclosure_scope":"Closed synthetic goods company; the listed source package is complete by construction","assumptions":{"historical_resolution":"half-year aggregate flows; existence of intraperiod schedules required, not recovered invoices","inventory":"one homogeneous good at cost 5; purchases before delivery; quantities equal costs/5","sales":"delivery transfers control; no returns, services, variable consideration or foreign currency","tax":"20% positive taxable profit, all expenses deductible, no deferred tax; excess payment is prepaid tax","plant":"opening cost 100, annual depreciation 10; end-H1 addition 10 lives 5 years; end-H2 addition 12 lives 12 years; zero residuals","debt":"100 throughout; fixed and floating both 5% in 2024; fixed 5%, floating resets to 7% in 2025; all maturities after forecast","time":"half-year accrual fractions 1/2, annual 1; explicit teaching convention","closing":"temporary accounts closed after each H1/H2; annual income uses movements excluding closing","universe":"no omitted company, OCI, acquisition, tax or off-balance-sheet operations inside this synthetic package"},"accounts":{"cash":"asset","receivables":"asset","inventory":"asset","plant_cost":"asset","accum_depreciation":"contra_asset","tax_prepaid":"asset","payables":"liability","debt":"liability","capital":"equity","retained":"equity","revenue":"income","cost_of_sales":"expense","payroll":"expense","depreciation":"expense","interest":"expense","tax":"expense"},"opening":{"cash":"60","receivables":"20","inventory":"30","plant_cost":"100","accum_depreciation":"-20","tax_prepaid":"0","payables":"-20","debt":"-100","capital":"-50","retained":"-20"},"historical_events":[{"id":"2024H1.sale","date":"2024-06-30","period":"2024H1","postings":[{"account":"receivables","signed_amount":"110"},{"account":"revenue","signed_amount":"-110"}],"cash_class":null,"state_changes":{}},{"id":"2024H1.collect","date":"2024-06-30","period":"2024H1","postings":[{"account":"cash","signed_amount":"110"},{"account":"receivables","signed_amount":"-110"}],"cash_class":"operating","state_changes":{}},{"id":"2024H1.buy","date":"2024-06-30","period":"2024H1","postings":[{"account":"inventory","signed_amount":"70"},{"account":"payables","signed_amount":"-70"}],"cash_class":null,"state_changes":{}},{"id":"2024H1.supplier","date":"2024-06-30","period":"2024H1","postings":[{"account":"payables","signed_amount":"65"},{"account":"cash","signed_amount":"-65"}],"cash_class":"operating","state_changes":{}},{"id":"2024H1.deliver","date":"2024-06-30","period":"2024H1","postings":[{"account":"cost_of_sales","signed_amount":"75"},{"account":"inventory","signed_amount":"-75"}],"cash_class":null,"state_changes":{}},{"id":"2024H1.wages","date":"2024-06-30","period":"2024H1","postings":[{"account":"payroll","signed_amount":"20"},{"account":"cash","signed_amount":"-20"}],"cash_class":"operating","state_changes":{}},{"id":"2024H1.plant","date":"2024-06-30","period":"2024H1","postings":[{"account":"plant_cost","signed_amount":"10"},{"account":"cash","signed_amount":"-10"}],"cash_class":"investing","state_changes":{}},{"id":"2024H1.depreciate","date":"2024-06-30","period":"2024H1","postings":[{"account":"depreciation","signed_amount":"5"},{"account":"accum_depreciation","signed_amount":"-5"}],"cash_class":null,"state_changes":{}},{"id":"2024H1.interest","date":"2024-06-30","period":"2024H1","postings":[{"account":"interest","signed_amount":"2.5"},{"account":"cash","signed_amount":"-2.5"}],"cash_class":"operating","state_changes":{}},{"id":"2024H1.tax","date":"2024-06-30","period":"2024H1","postings":[{"account":"tax","signed_amount":"1.5"},{"account":"tax_prepaid","signed_amount":"2"},{"account":"cash","signed_amount":"-3.5"}],"cash_class":"operating","state_changes":{}},{"id":"2024H1.dividend","date":"2024-06-30","period":"2024H1","postings":[{"account":"retained","signed_amount":"4"},{"account":"cash","signed_amount":"-4"}],"cash_class":"financing","state_changes":{}},{"id":"2024H2.sale","date":"2024-12-31","period":"2024H2","postings":[{"account":"receivables","signed_amount":"150"},{"account":"revenue","signed_amount":"-150"}],"cash_class":null,"state_changes":{}},{"id":"2024H2.collect","date":"2024-12-31","period":"2024H2","postings":[{"account":"cash","signed_amount":"135"},{"account":"receivables","signed_amount":"-135"}],"cash_class":"operating","state_changes":{}},{"id":"2024H2.buy","date":"2024-12-31","period":"2024H2","postings":[{"account":"inventory","signed_amount":"85"},{"account":"payables","signed_amount":"-85"}],"cash_class":null,"state_changes":{}},{"id":"2024H2.supplier","date":"2024-12-31","period":"2024H2","postings":[{"account":"payables","signed_amount":"80"},{"account":"cash","signed_amount":"-80"}],"cash_class":"operating","state_changes":{}},{"id":"2024H2.deliver","date":"2024-12-31","period":"2024H2","postings":[{"account":"cost_of_sales","signed_amount":"90"},{"account":"inventory","signed_amount":"-90"}],"cash_class":null,"state_changes":{}},{"id":"2024H2.wages","date":"2024-12-31","period":"2024H2","postings":[{"account":"payroll","signed_amount":"22"},{"account":"cash","signed_amount":"-22"}],"cash_class":"operating","state_changes":{}},{"id":"2024H2.plant","date":"2024-12-31","period":"2024H2","postings":[{"account":"plant_cost","signed_amount":"12"},{"account":"cash","signed_amount":"-12"}],"cash_class":"investing","state_changes":{}},{"id":"2024H2.depreciate","date":"2024-12-31","period":"2024H2","postings":[{"account":"depreciation","signed_amount":"6"},{"account":"accum_depreciation","signed_amount":"-6"}],"cash_class":null,"state_changes":{}},{"id":"2024H2.interest","date":"2024-12-31","period":"2024H2","postings":[{"account":"interest","signed_amount":"2.5"},{"account":"cash","signed_amount":"-2.5"}],"cash_class":"operating","state_changes":{}},{"id":"2024H2.tax","date":"2024-12-31","period":"2024H2","postings":[{"account":"tax","signed_amount":"5.9"},{"account":"tax_prepaid","signed_amount":"-2"},{"account":"cash","signed_amount":"-3.9"}],"cash_class":"operating","state_changes":{}},{"id":"2024H2.dividend","date":"2024-12-31","period":"2024H2","postings":[{"account":"retained","signed_amount":"5"},{"account":"cash","signed_amount":"-5"}],"cash_class":"financing","state_changes":{}}],"expected":{"2024H1":{"cash":"65","receivables":"20","inventory":"25","plant_net":"85","tax_prepaid":"2","assets":"197","payables":"25","debt":"100","equity":"72","revenue":"110","profit":"6","operating_cash":"19","investing_cash":"-10","financing_cash":"-4"},"2024H2":{"cash":"74.6","receivables":"35","inventory":"20","plant_net":"91","tax_prepaid":"0","assets":"220.6","payables":"30","debt":"100","equity":"90.6","revenue":"150","profit":"23.6","operating_cash":"26.6","investing_cash":"-12","financing_cash":"-5"},"2024FY":{"revenue":"260","profit":"29.6","operating_cash":"45.6","investing_cash":"-22","financing_cash":"-9","cash_change":"14.6"},"2025_fixed":{"cash":"95.2","receivables":"55","inventory":"40","plant_net":"98","tax_prepaid":"0","assets":"288.2","payables":"40","debt":"100","equity":"148.2","revenue":"300","profit":"65.6","interest":"5","tax":"16.4","operating_cash":"48.6","investing_cash":"-20","financing_cash":"-8"},"2025_floating":{"cash":"93.6","receivables":"55","inventory":"40","plant_net":"98","tax_prepaid":"0","assets":"286.6","payables":"40","debt":"100","equity":"146.6","revenue":"300","profit":"64","interest":"7","tax":"16","operating_cash":"47","investing_cash":"-20","financing_cash":"-8"}},"forecast":{"start":"2025-01-01","end_exclusive":"2026-01-01","demand_units":"30","price":"10","unit_cost":"5","target_inventory_units":"8","current_sales_collection_fraction":"0.9","legacy_receivable_collections":"10","old_payables_paid":"30","new_purchases_paid":"130","payroll":"50","capex_at_period_end":"20","dividend":"8","tax_rate":"0.2","funding_limit":"0"},"coverage_units":[{"id":"NS.opening","kind":"statement","disposition":"structured","content":"Opening balance sheet and account balances"},{"id":"NS.h1.original","kind":"statement","disposition":"superseded_reading_preserved","content":"Originally revenue 120, receivables 30, tax expense/payment 3.5, profit 14, equity 80"},{"id":"NS.h1.correction","kind":"note","disposition":"structured","content":"Premature invoice 10: reverse revenue and receivable; reduce tax expense 2 into tax prepayment; corrected profit 6"},{"id":"NS.fy","kind":"statement","disposition":"structured","content":"Annual and revised interim statements derived from listed events"},{"id":"NS.operations","kind":"policy","disposition":"structured","content":"Goods, inventory, asset and working-capital assumptions above"},{"id":"NS.debt","kind":"note","disposition":"alternative_family","content":"Principal 100, interest 5; fixed/floating composition undisclosed"},{"id":"NS.equity","kind":"note","disposition":"structured","content":"Capital 50; original retained 20; dividends H1 4, H2 5"},{"id":"NS.reference","kind":"cross_reference","disposition":"resolved","target":"NS.debt","content":"Financing note applies to debt and interest in every statement"}]}
