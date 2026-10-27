# Retained XBRL2.1 calculation bindings

20 October 2026. All 209 calculation arcs in 23 extended-link roles resolve
to retained numeric-item declarations. The arcs are optional, priority zero,
and survive the effective-relationship check. Their weights comprise 182
positive ones and 27 negative ones. All 196 relationships with two declared
balances satisfy the source's balance/weight sign constraints; the other 13
are not constrained by two declared balances.

The source supplies 274 summation-fact/role candidates. Exactly 110 bind under
the retained XBRL2.1 rules, and all 110 satisfy the rounded-sum comparison.
Every bound calculation has independent Fraction and Decimal agreement. No
bound calculation has an unreported conceptual component edge. This last
observation concerns this retained relationship set, not complete financial
disclosure or a general requirement that every linked concept be reported.

The remaining 164 candidates do not bind:

| Exact reason combination | Candidates |
| --- | ---: |
| Duplicate contributor only | 31 |
| Duplicate summation only | 57 |
| No nonnil contributor and duplicate summation | 14 |
| No nonnil contributor only | 44 |
| Duplicate summation and duplicate contributor | 18 |

Reason counts overlap: 49 candidates have a duplicate contributor, 89 have a
duplicate summation and 58 have no nonnil contributor. Two nil contributor
occurrences are excluded. Nonbinding candidates are not successful arithmetic
checks. No repeated fact was removed or selected as a representative.

Each arithmetic witness preserves its source amounts and decimals, separately
rounded contributions, weights, exact sum, rounded comparison and residual.
Rounding precedes weighting. The 22 fixtures distinguish this order, negative
ties, exact values, incompatible sums, role separation, nil/duplicate binding
rules and declared balance-sign constraints. All 75 counted assertions pass,
including 37 input bindings and seven exact source excerpts.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Preserve 110 consistent binding checks | Source-bound relationships and independent exact arithmetic | No inconsistent binding found | Retained resources versus an installed DTS | Compare later calculation/duplicate specifications as a separate optional contract | Whole-instance validity, financial correctness or complete disclosure |
| Preserve 164 nonbinding candidates | Every exclusion reason and contributor occurrence recorded | Original duplicate/nil rules enforced | Whether a later explicitly selected contract could use consistent duplicates | Inspect the primary successor specification before selecting any alternative | Nonbinding means successful, or deduplication is authorised |

Engineering correctness here concerns extraction, identity and arithmetic.
The numerical result is deterministic; no stochastic ranking is claimed.
Financial interpretation, schema validation and installed correspondence remain
unadmitted. No manuscript contradiction requiring a rebuild was found.
Candidate3.44/396/not_ready and all53 obligations/six interactions/46 operations
remain, with zero whole-row closures.

Post-run red team: incomplete or different installed taxonomy discovery could
change relationships and therefore the candidate bindings. A verified added
arc, equivalent-arc override or context-equality correction would overturn the
affected result. The weakest evidence remains installed/full-schema
correspondence, which has not been evaluated. Passing source arithmetic cannot
remove that limitation.
