# Native term-state obligations and declarative gaps

26 October 2026. Target: receivable_term_history_v1.validate. Exact source and
frozen states are pinned by probe.py. This audit distinguishes representability
from a complete replacement validator. No row here claims accounting authority.

| Native condition | Existing declarative support | Remaining requirement |
|---|---|---|
| Typed book, exact claim/clock schema, operating role/cost setup | Typed book, opening structural checks and selected roles/cost already exist | A reviewed term-profile structural selection, retaining migration premise |
| Cursor within reporting period | Scalar date comparisons | Explicit period-end binding, not a guessed calendar year |
| Sum remaining claims equals receivables | Complete-map projection and collection sum | Reuse unchanged with the new claim row schema |
| Sale event seen, issue date no later than book, nonnegative remaining | References to seen, per-row guarded predicates | Reuse with exact field bindings |
| Nonempty terms; current term belongs to same claim | Single-field references exist; static map pointer can name one known claim | Dynamic nested populations and claim-qualified term keys; empty child must stay observable |
| Terms strictly ordered by effective date | Nondecreasing ordered constraint and uniqueness exist separately | Per-claim sorted view with equal-date refusal; preserve original order as evidence |
| Predecessor equals previous effective term | No adjacent-row value binding | Explicit per-group predecessor selection, with initial sentinel declared |
| Issue <= effective <= book date; effective <= due; event seen | Scalar comparisons and references after binding | Parent issue date and claim ownership must propagate to nested rows |
| Current term is final effective term; current due matches it | No per-group maximum/selected-row value binding | Explicit greatest/unique selection and equality to parent summary |
| Assessment dates unique per claim and before cursor | Uniqueness and scalar comparisons after binding | Grouped uniqueness and parent issue date |
| Assessment references greatest term effective by as_of | Single-field reference proves existence only | Claim-qualified filtered greatest-date selection; existence alone is insufficient |
| Historical overdue uses referenced term's due and assessed remaining | Scalar conditional comparisons exist | Typed selected-term due binding; preserve historical rather than current due |
| Imported event unknown; recorded event seen | Guarded predicates and references | Origin guard and conditional reference, not unconditional seen membership |
| Assessed flag equals nonempty assessment population | No grouped count/exists scalar binding | Per-claim cardinality/exists with empty-map semantics |
| Latest assessment is max date; summary equals chosen record | No grouped selected-row binding | Per-claim unique latest selection and field reads |
| Unassessed sentinel/zero summaries | Guarded scalar predicates | Empty-assessment premise supplied by explicit grouped cardinality |

Current BookStateInvariant/1 binds a memory_map at a static pointer and only
scalar paths through record fields. A concrete claim can be named, but a reusable
invariant cannot enumerate every claim's nested term/assessment map without
either generated claim-specific definitions or a new general traversal binding.
Single-field references also cannot ensure same-claim ownership unless a
collision-free qualified key is explicitly constructed. A financial special
case hidden in a binder would leave the rule-authoring gap unresolved.

The first justified primitive is a bounded typed nested-map projection with
parent and child identities, parent scalar bindings, exact escaped source
pointers, declaration validation even for empty maps, and no hidden sorting or
completeness inference. It supplies rows, not term-chain validity. Subsequent
general grouped cardinality, adjacency and greatest-applicable-row bindings
need separate contracts and failure semantics before a term validator replacement.
