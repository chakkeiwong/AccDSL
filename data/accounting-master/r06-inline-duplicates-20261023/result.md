# Inline duplicate processing: dated source comparison

23 October 2026. P16/P17/P19; MC01/02/04/24–26/29/30/32–35.
Plan: `docs/plans/accounting-r06-inline-duplicates-20261023.md`.

The inspected Inline XBRL sources permit some duplicate reduction during
transformation, subject to the mapping requirements for every input element.
They do not make the 2018 note's complete-duplicate class a sufficient rule for
merging Inline elements. Target-document generation and preservation of every
original presentation occurrence answer different questions.

## Sources and edition boundaries

Six official HTML documents were retained successfully: the exact 2013 Primer
and Part 1 linked by the 2018 note, the July 2026 Primer and corrected Part 1
listed in the retained official index, and their two release histories. The
Primers explicitly describe themselves as non-normative. Part 1 declares itself
normative, but that declaration does not turn its marked non-normative notes
into requirements. Receipts preserve exact URLs, transfer durations and observed
UTC brackets; those brackets are not exact process start/end measurements.

The comparison covers selected provisions, not complete equivalence of the
specifications. `reading-ledger.json` records the actual spans read. Both release
histories were read completely; their only images are navigation logos. The four
technical documents contain no embedded images. Previously completed reading of
the 2018 note supplies its frozen comparator, not new reading credit.

| Selected Part 1 text | 2013 versus corrected 2026 | Consequence within this inquiry |
| --- | --- | --- |
| Structure, through before 3.1.1 | Changed | Zero-or-more Inline elements and a corrected continuation-property name are visible differences. |
| 3.2 target documents | Identical | Each target partition still requires its mapped facts and relationships. |
| 3.3 processors | Changed | The corrected validating-processor definition excludes rules documented as non-validatable. |
| 10 nonFraction, through before 10.3 | Identical | Inspected numeric definition, constraints and mapping text is unchanged. |
| 11 nonNumeric, through before 11.3 | Changed | The corrected source adds the marked non-normative language clarification. |
| 12 references | Identical | Selected target-root mapping text is unchanged. |
| 13 relationships | Changed | The corrected pair is F and N; the original says f and F. |
| 15 tuples | Identical | Selected tuple definition, validation and ordered mapping text is unchanged. |
| 16.2, through before Appendix A | Changed | Registry compatibility is expressed for input valid under the earlier version. |

`version-comparison.json` preserves all nine exact visible-text comparisons.
Equality here does not establish schema, processor or whole-document equivalence.
Primer Appendix D's 17 November 2015 revision date and the release index's
9 December 2015 publication date have different roles; their difference alone
does not establish an error. Corrected Part 1 Appendix E lists four correction
entries, but does not separately identify the added 11.2.2 paragraph. Its precise
introduction date is not established by comparing these two editions.

## What can be reduced

Primer 5.2 makes item de-duplication discretionary. Part 1 sections 10.2 and
11.2 instead state that, for each relevant input element, there must exist an
output element satisfying the listed properties. This existential statement
does not itself require a distinct output for every input. It also does not
waive any property when two inputs share an output.

For non-nil numeric items, the required content applies the declared format
transformation, scale and sign. Concept, context and unit mapping also matter.
The declared decimals and precision attributes must be reproduced, including
their required absence. Two differently rounded disclosures therefore cannot
be replaced during this mapping merely because an analytical policy would
choose the most precise one. The nil exception concerns the child-content rule;
it is not a general exemption from the other mapping requirements.

Two small deductions make the merging limit precise. Let an output element
`o` satisfy the mapping obligations of inputs `a` and `b`. If both inputs have
non-absent IDs, the rules require `id(o) = id(a)` and `id(o) = id(b)`. Unequal
required IDs make those equations incompatible. Likewise, for one expanded
attribute name `q`, unequal required values `q(o) = v_a` and `q(o) = v_b` cannot
both hold. This argument does not exclude merging merely because one input
lacks an optional ID, or because the inputs carry different attribute names.
These are necessary conditions only; they are not a sufficient merging algorithm.

The 2018 note's complete-duplicate definition expressly ignores custom
attributes and attached footnotes. Consequently, complete-duplicate status
under that note alone cannot establish that every Inline output obligation is
compatible. Required relationships also survive as separate target obligations.
Neither the note nor this deduction licenses discarding their information.

Tuple child reduction is a separate provision. The inspected definition gives
tuple content with unique tuple-order values; the validation text requires
same-order entries to have the same Whitespace Normalized Value. The definition
of that value includes attributes. Mapping emits tuple content in order. The
Primer describes removal of duplicate tuple children as necessary. We retain
the exact definition/validation wording rather than claiming an independently
validated tuple-collapse implementation.

## Language clarification and remaining uncertainty

Both Primers' 5.12 explanations say that a language on an element or its
ancestors carries through to target facts. The added Part 1 paragraph explains
that nonNumeric elements have no special handling of in-scope language, and
directs reports to use an explicit element attribute or the language mapped from
`ix:references` to the target root. Inspection of the retained HTML places this
paragraph inside `div.nonNormativeNote`. It is clarification within the normative
document, not a new normative MUST. The broader Primer wording and this narrower
explanation remain a source tension; no installed processor behavior is inferred.

No Part 2 schema, transformation-registry implementation, conformance suite or
processor was executed. The selected sources do not establish issuer compliance,
archival completeness or an implemented reduction policy. Calculations 1.1
sections 5.1/5.4 remain unresolved as previously recorded. Formula claims in the
2018 note's 5.2 require their own primary-source inquiry; Inline transformation
rules cannot establish them.

## Decision and continuation

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next justified action | What is not concluded |
| --- | --- | --- | --- | --- | --- |
| Complete this bounded documentary comparison | Fourteen obligation/permission rows, 42 exact anchors, nine edition comparisons and selected reading record are present | No source-edition mismatch or missing relevant figure; marked clarification distinguished from normative requirements | Uninspected dependencies and actual processor behavior | Preserve the records and use the distinctions when evaluating future adapters | Full Inline conformance or a sufficient de-duplication algorithm |
| Retain source occurrences independently of target output | Optional reduction plus the checked mapping obligations support the distinction | No source-preservation requirement is inferred from processor discretion | Exact future archive/adapter implementation remains held | Keep raw IXDS and occurrence links in the proposed design | A transformed instance preserves all presentation occurrences |
| Continue ready internal source work | The current candidate has not triggered a continuation veto | Protected bytes and held-action boundaries must remain intact | Formula source claims and other authority gaps remain | Inspect the exact retained note reference before a fresh bounded Formula plan | A failed or qualified claim rejects the research direction |

The claimed target is the dated documentary obligation, and the quantity
actually checked is retained primary-source text plus the two elementary
compatibility deductions above. They support that bounded conclusion. They do
not measure runtime behavior, accounting correctness or empirical performance.
There is no stochastic comparison or statistically supported ranking here.

Version 3.48 remains 401 pages and **not_ready**. All 53 obligations, six
interactions and 46 operations remain; zero whole rows close. All 192 vintages
remain unadmitted, and E3 plus six scientific choices remain unselected. No
manuscript edit, runtime/controller execution, installation, empirical campaign,
acquired-code execution, commit, outreach, publication or fee follows. Independent
reader, implementability, domain and human acceptance remain pending. None of
those pending acceptance states stops the next feasible internal inquiry.
