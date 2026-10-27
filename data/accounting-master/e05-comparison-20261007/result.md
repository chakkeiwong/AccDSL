# Bounded comparison of retained source assertions

7 October 2026. E05 remains open. The source-format repair made the proposed
comparison meaningful, but the inspected scope supplied no genuine conflict.
This completes the bounded search, not the real-conflicting-disclosure requirement.

The active corpus selects 24 HTML reports, Apple 18 and Caterpillar 6. Only
Apple FY2025 Q1 contains inline numeric tags. The 23 other selected HTML reports
retain visible statement text; absent tags cannot be interpreted as absence
of financial facts or conflicts. Other retained HTML versions on disk were not
counted as additional active reports.

The comparison extracts five consolidated balance-sheet captions from those
24 reports and seven selected annual PDF comparators: total assets, current
assets, liabilities, equity and the issuer's reported cash caption. Each
observation retains the statement heading, two dated columns, unit, exact quote,
original hash and source location. All 31 planned statements yielded all five
captions for both dates: 310 observations. This is a defined search scope, not
complete financial-statement or note annotation.

The 290 pairs with matching issuer, caption, date, unit, reported accounting
family and consolidated perimeter have equal displayed amounts. Dates and
headings were inspected in the resulting source-bound records. The comparison
does not infer economic equality beyond those displayed values, check every
accounting election or certify historical availability. No unequal candidate
required a substantive conflict/supersession verdict.

Within the Apple tagged filing, 516 of 525 numeric occurrences were parsed under
the supported transforms and explicit-dimension contexts. Thirty duplicate
concept/context/unit groups have identical computed values, consistent with
their stated decimals. Nine occurrences were excluded: two nil facts, four
facts with typed-dimension contexts and three SEC word-number transformations.
These are unexamined numerical comparisons, not agreement or zero values.
`inline-comparisons.json` identifies every occurrence and exclusion. The aid
does not implement full XBRL validation or claim actual economic precision.

The first statement pass excluded five Caterpillar quarters because their
heading is “Consolidated Statement of Financial Position.” The heading rule
was repaired from inspected source text; the first attempt and its disposition
are retained in `attempt-1/`. All five statements are included in the final
result. Split Apple HTML table containers also demonstrate why a single table
element is an unsafe completeness assumption: some equity rows follow the
first container within the same dated statement.

`check_results.py` passes 1,151 source/consistency assertions. Besides exact
hashes and quotes, it checks assets = liabilities + equity for all 62 dated
statements and independently compares all ten Apple Q1 balance-sheet values
to native tagged facts. These checks detect specific extraction/context mistakes;
they are not a semantic accuracy measurement or independent human review.
The final comparison took 28.12 seconds; the initial attempt took 29.22 seconds.
Commands, actual environment and exact inputs are in the receipts and manifest.

| Decision | Primary criterion status | Veto status | Main uncertainty | Next justified action | What is not concluded |
| --- | --- | --- | --- | --- | --- |
| Complete this bounded comparison | All planned visible statements accounted for; tagged exclusions explicit | Initial heading failure repaired; no remaining detected scoped consistency failure | Caption matching and five captions do not cover narrative/contract assertions | Keep records as negative scoped evidence and improve other proposal workstreams | Absence of conflicts in the issuer/corpus or accounting correctness |
| Keep E05 open | No same-context incompatible pair found | Genuine-pair promotion criterion unmet | Other notes, disclosures, issuers and versions remain unexamined | A future targeted search needs a new substantive candidate source; do not repeat this scan unchanged | Real-conflict admission/invalidation demonstration or full proposal readiness |

Post-run red team: repeated equal totals may conceal offsetting errors or
conflicting narrative descriptions. A valid source pair elsewhere would overturn
only the broader absence claim that is deliberately not made here. This result
rejects neither the research direction nor its source-review design. It ends a
defined search; E01/E07/E08/E14 internal preparation continues independently.
No stochastic ranking, product implementation or controller restart occurred.
