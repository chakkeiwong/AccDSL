# Calculation alignment changes the contributing data points

20 October 2026. The retained Calculations 1.1 §5.1 definition requires every
non-concept dimension of a to occur equally in b, without stating the converse.
That directed relation is different from equality of the two dimension sets.
On this report the difference changes actual joins. It must be resolved or
kept as an explicit conditional interpretation before interpreting sums.

| Interpretation | Contributor joins | Bound total data points | Nonbinding totals | Extra joins over equality |
| --- | ---: | ---: | ---: | ---: |
| Equal non-concept dimensions | 528 | 172 | 51 | 0 |
| Contributor dimensions contained in total | 801 | 204 | 19 | 273 |
| Total dimensions contained in contributor | 1,001 | 180 | 43 | 473 |

These are deterministic counts, not performance rankings. The 5,085 candidate
pair comparisons use the same 209 retained effective relationships across
23 roles and 68 calculations. All 185 endpoint concepts have item substitution
and decimal/integer ancestry; balance/weight checks and relationship uniqueness
replay against the frozen network. There are 223 nonnil total data-point
candidates. The old 274 occurrence candidates map exactly to them: duplicate
total occurrences no longer count as distinct data points, but every original
fact remains present. The 110 old bound occurrences remain a separate XBRL 2.1
result. The new 172 potential bindings are not 172 consistent calculations;
no numeric arithmetic has been performed. Two aligned nil-only contributor
data points are excluded, and no total concept is absent from this report.

All 746 strict subset joins retain exact roles, arcs, fact IDs and differing
dimensions. For example, contributor f-202 for CommonStocksIncludingAdditional-
PaidInCapital would join StockholdersEquity total f-214/f-227 under contributor-
subset matching even though the latter has StatementEquityComponentsAxis =
CommonStockIncludingAdditionalPaidInCapitalMember. Conversely, CashAndCash-
EquivalentsAtCarryingValue fact f-419 has FinancialInstrumentAxis = CashMember
and would join AssetsCurrent f-159 under total-subset matching. Equal-dimension
matching rejects both joins. These are concrete semantic differences, not
numeric-rounding discrepancies or established errors in the filing.

74 counted checks, 13 fixtures, five source anchors and 43 input bindings pass.
Every pair decision is recomputed using independent set-containment operations.
The exact equality join set also matches all old occurrence-level joins after
mapping occurrences to data points. Fixtures expose asymmetry, language/unit/
period/entity changes, missing dimensions and differing members.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Reject silent symmetric alignment assumption | Actual join sets differ | Target ambiguity blocks unqualified arithmetic | Intended normative converse/orientation | Inspect exact official clarification and pinned official processor code | Authoritative erratum or filing error |
| Retain conditional finite join evidence | Exact pair and occurrence bridge passes | No protected-state or input veto | Generic processor behavior remains unexecuted | Continue bounded source inquiry | OIM conformance or installed correspondence |
| Keep old result distinct | Frozen network and all 274 old candidates preserved | No comparison baseline change | Mode/adoption not selected | Any later arithmetic names its mode and alignment rule | 172 potential bindings are calculation passes |

The strongest alternative explanation is that the source intended ordinary
symmetric alignment and merely omitted the converse. That would justify a
contextual equality implementation but is not established by this wording
alone. Exact official clarification or a normative correction could settle it;
implementation code can document practice, not correct a normative document.
The result invalidates the proposed unqualified calculation target, not the
retained evidence or wider research direction. No manuscript change is yet
required. 3.44/396/not_ready and 53/6/46 remain unchanged; zero rows close.
