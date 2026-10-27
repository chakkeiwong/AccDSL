# Query declared groups without inferring a history

26 October 2026. MC20/24/25/28/33/34; S2–S4. Build on the frozen
NestedMapProjection/1 and its 44 complete retained comparisons. This phase adds
typed group queries, not financial methods or a replacement term validator.

Question: can declarations select a unique row, the greatest dated row before
an explicit boundary, or a predecessor within one supplied parent group while
preserving empty, missing and ambiguous outcomes? These operations supply the
state relations required by the existing term-chain/latest-assessment rules.

Skeptical audit: row order is not chronology; group identity is not child ID;
existence is not greatest-applicable selection; a tie cannot be resolved by
insertion order. Recompute the bound projection on each query; never trust an
unverified caller output. Compare against a separate simple scan of original
Python fixture dictionaries, not the candidate's projected rows. Dates/units
and field types must agree before comparisons. An absent group is invalid;
a known empty group is an explicit no-row result. Unknown inputs remain
unresolved, and partial populations cannot become complete through selection.

The first grammar is a finite query record with exact group identity and mode:
count, match, or greatest. Match compares one typed field to a typed value;
greatest declares one date/rational ordering field, optional inclusive/exclusive
typed upper bound, and whether empty is allowed as a result. The query returns
the selected complete row and lineage, candidate indices, count and explicit
none/ambiguous status. No hidden sorting or tie-breaker. Strict greatest excludes
the boundary, supplying a predecessor search. Inclusive greatest supplies
the term applicable at an assessment date. Global latest omits the bound.

Primary criterion: complete statuses, selected rows, provenance, candidates and
empty/ambiguous results agree with the original-state scan over all retained
groups and meaningful dates. Controls: duplicate field matches/dates, foreign
group, exact inclusive/exclusive boundary, empty groups, missing/unknown bound,
wrong type/context, non-orderable field, stale queries/projections, Unicode
ownership and reordered input. Counterexamples must retain original ordering
while returning the same semantic selection. Full input identity keeps order
differences visible. Financial/native callbacks remain disabled.

Defaults: greatest supports date or exact rational order; this is a typed
subset, not a general product rule. Existing row/group limits are retained
compatibility bounds; no performance claim. The comparator uses original
fixture state and independent Fraction/date conversion. Changed frozen bytes
or unexpected result differences veto promotion; fixture/code errors trigger
repair. No scientific ranking, accounting authority, source completeness or
production claim follows.

Save declaration, implementation, complete pairs, controls and manifest under
data/accounting-master/grouped-row-query-20261026/. CPU-only bounded work.
Then audit how guarded invariants compose these query results without making
missing/ambiguous rows silently true. No agents, commits, installations, GPU,
fees, outreach, publication or E3.
