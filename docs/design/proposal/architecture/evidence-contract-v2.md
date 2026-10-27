# Evidence contract v2 — proposed semantics

This contract addresses MC01–MC04 and the admission boundary of MC27
(G2/G11/G17). It specifies evidence preparation for the whole product, including
later group, bank, insurance and cross-standard work. It does not select an
initial product profile. P15-E01–E03 receive concrete proposed answers; E05
still needs a real conflicting-disclosure walkthrough. Examples are in
`evidence-fixtures-v2.json`. Synthetic text is identified there and supplies
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

The source-backed Apple example uses Note 9 of the 2024 10-K (printed page 42),
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
