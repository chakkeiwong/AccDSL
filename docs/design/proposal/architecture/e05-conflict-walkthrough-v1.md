# E05 cross-layer walkthrough, version 1

The retained-source investigation found no qualifying real conflict in its
seven candidates. This walkthrough is entirely synthetic. It proposes behavior
for MC04/MC27 and their MC05/MC25 dependencies; it does not satisfy E05's real
source example or select an accounting treatment. Its companion JSON contains
specified inputs and expected outputs, not executable implementation or actual
review decisions. Independent review and human acceptance remain pending.

## The disagreement and the review sequence

Two invented disclosures concern one invented entity, Example Company, one
perimeter P1, synthetic basis B1, and revenue for [2025-01-01, 2025-07-01).
Source A says exactly USD 120; source B says exactly USD 110. Both explicitly
state that their amounts are unrounded. Exactness is a stipulation chosen to
isolate disagreement from rounding, not an assumption about real disclosures.
The sources are distinct assertions with the same context and no initially
supported supersession relation. Source D separately reports cash USD 40 at
June 30. Dates, receipts, reviewers and source labels in this example are
invented inputs; they establish nothing about actual historical availability.

The analyst first sees immutable source text, contextual headings and links to
candidate readings. Reading A as 720 fails literal fidelity. Rejecting that
reading preserves both the source and the rejected proposal; accepting a new
reading of 120 records an extraction correction, not an issuer revision.
Reading B as 110 is also faithful. The proposed reviewers accept both at the
extraction layer. An interface must display “faithful extraction” with that
layer name; a generic green “accepted” indicator is insufficient.

Interpretation review next checks entity, perimeter, interval, concept, basis,
unit and precision. Both readings mean the same quantity. The proposed decision
admits them as competing interpretations and records a conflict with its exact
scope. It neither averages to 115 nor attaches 50/50 weights. A reported-value
query exposes both alternatives. Separate assumptions selecting A or B can
support explicitly conditional exploratory arithmetic; they are not evidence
that either disclosure is correct. A query for a single unconditional value
returns unresolved with the two supporting spans and the missing resolution.

Accounting admission is a separate action requiring the applicable standard,
effective rule version, recognition and measurement analysis, event and opening
state, and the interpretation/assumption dependencies. None is supplied by this
synthetic basis. The accounting query returns `TREATMENT_UNSUPPORTED`, no journal
and no compliant statement. Even an interpretation accepted after a correction
cannot supply this missing authority. P17 must prepare source-grounded treatment
answers before any professional referral; this example authorises no referral.

## Concrete views, revisions and query outcomes

V2 is the proposed August 31 snapshot: both A and B have supported synthetic
public/receipt dates and layer decisions by that cutoff. Its reported-value
query returns alternatives A=120 and B=110, status unresolved. The independent
cash query returns disclosed cash 40. Conditional revenue-to-cash arithmetic
is A: 120/40=3 and B: 110/40=11/4; the units cancel. This is arithmetic on
stipulated reported amounts, not a financial forecast, accounting reconciliation
or probability distribution. A future-statement query also needs a scenario,
behavior and treatment specification and returns unresolved dependencies.

An invented September source C expressly corrects A's revenue for this exact
period from 120 to 110. Source inspection and separate proposed extraction and
interpretation decisions support a scoped A→C supersession edge. They do not
supersede B, the cash assertion, unrelated periods, or every assertion in A's
source document. V3's latest query selects B and C at 110, retaining both source
identities with a compatible-value relation. Equal value does not make them
independent corroboration or permit deleting either occurrence. A latest query
at August 31 still excludes future C. `original` at the later cutoff retains
roots A and B and their original disagreement. Resolution is local to the
specified latest view, not a rewriting of historical truth.

C without correction support cannot silently replace A because it is newer.
Its new same-context assertion is another candidate and the conflict remains.
A malformed/cyclic or wrong-context edge is rejected under T4 with the prior
view unchanged. A known later C is excluded at an earlier cutoff; a relevant
candidate whose availability is unknown is instead unresolved. If B's public
availability is unknown, an investor-information query can select eligible A
but must keep the affected claim unresolved. Archival exploration can show B
with historical admissibility unestablished. A pure system-as-of query can use
B's supported receipt and layer decisions without claiming public availability.

## Dependencies, ownership and selective reuse

The evidence layer owns immutable source/occurrence identities and their hash
checks. Review records own layer, reviewer, scope, rationale, timestamp and
expected prior-view version. Interpretation records own exact reading, context
and mapping versions. A temporal selector owns the candidate-set revision for
each query key and its cutoff/review filters. The persistence layer will own
snapshot commits, reverse dependency edges and stale-request checks; this is
an interface requirement for its later contract, not a choice of database.

The JSON graph separates revenue selection from cash selection. A new competing
assertion must invalidate the revenue selection even when it changes none of
the old assertion IDs: therefore the graph includes membership revisions for
the key, not only positive edges to selected records. Review rejection or
supersession invalidates the changed interpretation's current eligibility,
then the selector, reported-value result, conditional ratio and downstream
scenario result. An unrelated cash selector and cash result have no such edge.
Unknown dependency completeness prevents reuse; it does not prove independence.

The stored V2 result stays immutable. In V3 it cannot be relabelled current.
A cash result may be reused only after comparing its complete dependency
fingerprint, context, operation version, relevant candidate-set revision and
query cutoffs, or proving the cutoff extension adds no eligible candidate for
that key. The reuse receipt names both views and the unchanged key/subgraph;
the old payload remains historical and a new response records the reuse.
Changed scenario, treatment, numerical method or query semantics would also
break reuse. This example does not specify the final hash encoding or storage
transaction mechanism.

A current mutation carrying expected V2 after V3 is committed returns
`STALE_VIEW` before any append. A new current result depending on superseded A
under latest selection returns `SUPERSEDED_INPUT`; checking only whether a
cached result predates invalidation would miss this late-descendant case.
Explicit frozen V2 access returns the old conflict result with V2/review IDs,
cutoffs and a historical label. It does not alter the current view or falsely
claim current eligibility. A historical reconstruction is a separate requested
operation with its own recorded inputs; it cannot smuggle later review into a
system-as-of claim.

## Alternatives and interfaces still to specify

With one undifferentiated `accepted` flag, the same two faithful extractions
would either become contradictory unconditional constraints (empty history set),
be reduced to whichever was accepted last, or be averaged by an unstated rule.
All three lose the supplied distinction between accurate transcription and
truth/treatment endorsement. Global invalidation avoids some stale results but
needlessly discards independent cash work; positive-edge-only invalidation
misses newly arriving competitors. Layer decisions plus scoped membership and
transitive dependencies are proposed because they preserve this example's
meaning and permit justified local reuse. No performance advantage is measured.

The later history_families contract must explain how interpretation alternatives
become joint constraints and how incompatible branches are diagnosed. Uncertainty
must preserve unweighted alternatives and distinguish conditional assumptions.
Accounting must specify authority and journal admission. Language/IR must carry
layered statuses, context and query dimensions. Persistence, interfaces and
failure_semantics must provide the ownership, version checks, atomic append,
reuse receipt and typed outcomes named here. These contracts are not supplied
by this walkthrough. Its illustrative error names must be reconciled with those
contracts before phase acceptance.

Stop condition for this task: the bounded source dispositions, precise no-pair
limit and complete specified transitions are saved and locally checked. E05 and
full P16 remain open. Pending bounded result review is not a prerequisite for a
fresh history_families plan and its independent plan review. Full independent
P16 result review remains mandatory before acceptance.
