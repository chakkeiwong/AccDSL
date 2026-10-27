# Conditional interval calculations on the retained report

20 October 2026. Under explicit equal non-concept dimensions and the contextual
OIM6.2 duplicate rule, 172 of the 223 total data-point candidates bind. All
172 have overlapping reported and calculated intervals in each separate mode:
round-to-nearest and truncation. The other 51 lack a reported contributor and
remain nonbinding. They are not passes. No issuer rounding policy is selected,
and these conditional diagnostics are not a conforming processor run.

| Evidence denominator | Round-to-nearest | Truncation |
| --- | ---: | ---: |
| Candidate total data points | 223 | 223 |
| Bound and interval-consistent calculations | 172 | 172 |
| Nonbinding, no reported contributor | 51 | 51 |
| Numeric dimension groups inspected | 879 | 879 |
| Nonnil groups consistent under the declared reading | 877 | 876 |
| Inconsistent duplicate groups | 0 | 1 |
| All-nil groups ignored | 2 | 2 |
| Frozen XBRL 2.1 bound occurrences also passing this conditional check | 110 | 110 |

The old 274 occurrence candidates map into 223 total data points. The 110 old
bound passes retain their meaning; the conditional interpretation permits
62 additional candidate calculations because it can use consistent duplicate
groups. All original occurrences remain preserved. The 172 bindings refer to
162 distinct total points across roles. Passing these interval tests neither
reconstructs undisclosed journal history nor establishes accounting validity.

The truncation-only inconsistent group is dp-0753, facts f-802/f-805/f-824:
UnrecognizedTaxBenefits in c-22 has 19,500,000,000 at decimals -8 and two
19,454,000,000 observations at decimals -6. Nearest intervals overlap, but
positive truncation intervals do not: the coarse lower bound is 19,500,000,000,
above the finer upper bound 19,455,000,000. This group enters none of the
172 bound calculations. Thus an explanatory whole-report duplicate screen
differs between modes while all actual binding statuses agree. The source
requires inconsistent-duplicate diagnostics when a calculation binds to the
affected point; this finding must not be mislabeled as a failed calculation.
No accounting-error conclusion follows.

Two bound totals, f-209 and f-210 in the consolidated balance-sheet role,
have no nonnil contributor for arc calc-arc-0021. Their other reported
contributors still allow binding under the source rule. The absent amounts
were not inserted as zeros. This differs from the frozen 110 old bound
cases, all of which had complete reported component edges within that network.

Both arithmetic implementations agree on 2,204 checks: 879 numeric points and
223 calculation candidates in each mode. One uses exact Fraction intervals;
the other uses Decimal with precision 120, observed value/weight length bounds,
and separate endpoint/intersection/sum logic. Twenty additional fixtures cover
same-precision duplicates, mixed nil, excess digits and precedence, missing
totals/contributors, exact sums, negative weights and open endpoints. Fifty
counted wrapper/source checks, five source anchors and 14 direct bindings
also pass. The arithmetic is deterministic; no method ranking is inferred.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain conditional per-mode arithmetic | Every candidate classified; independent arithmetic agrees | No arithmetic/source/protection veto | Equal alignment and OIM6.2 reading remain explicit hypotheses | Preserve alongside old results; reconcile remaining reuse admission duties | Normative conformance, issuer policy or full validity |
| Preserve truncation duplicate finding | Exact disjoint intervals for dp-0753 | Veto for that duplicate point only, not a binding calculation | Actual measurement/filing policy unknown | Retain both source observations and mode distinction | Issuer error or research-direction rejection |
| Keep full reuse admission pending | Structural/numeric evidence is finite and source-bound | Full schema/OIM/XHTML, installed and source-clarification gaps remain | Missing execution and authority | Continue distinct internal source work; no repeat of completed arithmetic | Whole-row closure, installed readiness or acceptance |

The strongest alternative explanation for all passing bindings is that interval
consistency is a weak necessary local screen and the retained network covers
only certain relations. It does not validate an entire financial report.
Different authoritative alignment semantics or newly applicable relationships
would require another conditional result. The weakest evidence is full
validation and installed correspondence. Manuscript 3.44 remains 396 pages
and not_ready, with 53 obligations, six interactions, 46 operations and zero
whole-row closures. No upstream processor, installation or empirical run.
