# Version 2.46: valid tokens and rectangular cells

12 October 2026. E08/C06, E14/C07, P18; MC23/25/29–35, G8/G9/G10/G18.
The separate **183-page Version 2.46** explains why local OTSL token rules
do not suffice to validate rectangular merged cells. The material addition
is on PDF 150 (printed 143), within the existing adapter discussion.

Candidate: docs/design/proposal/manuscript-otsl-20261012/accounting-product-proposal.pdf
SHA256: b13be68b6c5de2027f9f7a773dee70361feedb2c4b46a65bf81836e98418513e

All **127 integration checks pass**. All old adapter prose, all 48 displays
and all 92 earlier references remain; the identified arXiv v1 reference brings
the total to 93. The LuaLaTeX/BibTeX build has no TeX, box, citation, reference
or bibliography warnings. All input and artifact hashes of the closed 50-check
OTSL inquiry match. Version 2.45 and earlier corrections remain protected.

## Bounded author review

Final PDF pages 1, 149–152, 179–180 and 183 were inspected at page resolution,
in batches of at most two. PDF 149 supplies the prior model/text context;
PDF 150 contains the token meanings, finite counterexample and specific decoder
finding together. PDF 151 continues the existing taxonomy, evaluation and
licensing explanation; PDF 152 completes that discussion without clipping.
The short chapter-ending page is a consequence of retaining the existing
argument and the new explanation; no paragraph or qualification was deleted.
The cover prints Version 2.46. The new Lysak entry is intact on PDF 179 and
distinguishes the inspected arXiv v1 from the unverified published full text.
The adjacent and final bibliography pages remain legible.

Answers to the four questions fixed before editing, by the author:

1. C starts a cell, L joins left, U joins above, X joins both and NL ends
   a row. The six source rules constrain local neighbors, row/column starts
   and row widths; their role differs from correctness of a prediction.
2. In C L NL / U C NL, L and U have the required C neighbors, both boundary
   rules and equal widths hold, and there is no X condition to check. The
   first cell nevertheless occupies three positions of a two-by-two grid.
   A two-row/two-column HTML span would also cover the second C's position.
3. Each cell must occupy a complete rectangle, cells must not overlap and
   every declared grid position must belong to a cell. These proposed checks
   still do not prove correspondence with the financial source table.
4. The later retained decoder's row counter remains zero, so the condition
   described as first-row-only also applies later. This is a checked source
   defect relative to that scope. Actual occurrence and downstream prediction
   effects have not been measured.

The surface auditor was run on both root and adapter source because it does
not follow includes. Neither run reported duplicate/missing labels, long
sentence candidates, repeated words, punctuation candidates or placeholders.
Combined-source checks and the full build cover cross-file references. These
diagnostics and author answers are not independent or human acceptance.

| Decision | Primary criterion status | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Keep Version 2.46 as current provisional candidate | Material source-supported explanation, exact preservation, 127 checks, clean build and eight inspected pages | No identity, preservation, source or build veto | Independent/human comprehension and full-document regression remain pending | Commit and rotate to the exact Apple 2018 indenture source question | Whole-document acceptance or closure of E08/E14 |
| Require geometry beyond local syntax in the proposed adapter | Finite counterexample checks every printed rule and merge interpretation | Universal rectangular-geometry sufficiency is contradicted under these six rules | Additional uninspected published constraint could narrow the finding | Preserve arXiv-version and rectangular-exchange scope | Rejection of OTSL, a full grammar theorem or implemented validator |
| Keep performance and runtime conclusions held | No new local model run | Unsupported checkpoint/performance transfer remains a claim veto | Frequency and consequences of the source-code defect | Later target-specific runtime validation under a separate contract | Parser ranking, accounting accuracy or default readiness |

No stochastic comparison ran and no ranking is supported. Reported paper
scores remain source-attributed descriptive evidence. A ranking would need
identified models, matched financial inputs, downstream criteria and adequate
uncertainty evidence. No numerical or library default changed.

Post-run red team: the strongest alternative is that an additional constraint
outside the six inspected rules forbids the example. The text therefore
attributes the result to those rules and the inspected author version. The
specific code finding is static evidence, not an observed failure rate.
Author comprehension review remains the weakest acceptance evidence. The
findings require a local specification repair; they do not invalidate the
whole research direction or justify stopping independent internal work.

Full readiness remains **not_ready**, with E01/E05/E07/E08/E14 open. The
frozen 56/136 date split and forty-target exhibit frontier remain unchanged.
Next: docs/plans/accounting-apple-2018-indenture-source-20261012.md.
