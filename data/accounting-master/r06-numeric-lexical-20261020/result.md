# Retained numeric lexical interpretation

20 October 2026. MC01–06, MC23–26, MC28–35; P15/P16/P17/P19.

All 961 retained numeric candidates have lexical forms and exact rational
values consistent with the inspected XML Schema 1.0 Second Edition
decimal/integer paths. There are 958 decimal terminals and three integer
terminals, across 263 selected concepts and 13 type nodes when the two nil
occurrences are included. All eleven custom type nodes were checked against
their actual retained declarations and derivation children; they introduce
no additional numeric value facet. Numeric attribute groups carry obligations
that this inquiry does not validate.

The calculation uses the decoded source text after the specification's XML
whitespace collapse, admits only the explicit ASCII lexical grammar, and
accumulates digits into an exact Fraction. An independent Decimal tuple
conversion checks the value after lexical admission. Every result equals the
frozen portable rational candidate. For example, f-53 remains exactly
2628553000000; its decimals attribute of -6 is not a multiplier of that value.
All raw spellings, source spans, context/unit identifiers and original
candidate Values remain unchanged.

The two nil observations, f-191 and f-192, remain separate Nil records.
Both have explicit xsi:nil=true, an inspected nillable declaration without
a fixed value constraint, empty raw content, no decoded text and no element
children. Those are checked conditions from Part 1 section 3.3.4, not a
finding that every element-validity or XBRL rule has passed. Neither is parsed
as a decimal or converted to zero.

The exact specification sections are preserved in six bounded readable
extracts, with source and excerpt hashes. Eleven retained input bindings,
the 263 concept paths and all 963 occurrence records are in the adjacent
JSON files. There were no new acquisitions and no acquired code executions.
All original schema/XBRL validation statuses remain not_run.

The verifier passes 1,184 explicitly counted assertions, including 87
hand-authored grammar fixtures and nine altered-evidence controls. Fixtures
distinguish lexical membership from canonical spelling, accept the allowed
sign/zero/point forms, and reject exponents, NaN/INF, non-ASCII digits,
non-XML whitespace, underscores, empty tokens and internal spaces. Integer
rejects 1.0 and 1. even though their decimal values would be integral.
The negative-zero spelling is retained separately from its zero value.
Finite arbitrary-precision examples do not promise universal resource limits
or installed-processor support.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Accept this narrow occurrence interpretation | All 961 lexical/value comparisons agree | No unsupported selected facet or changed protected input | Full attribute, context, unit and schema constraints remain outside the check | Carry separate evidence into R06 preparation | Full filing validity or processor-value admission |
| Preserve the two Nil observations | Inspected nil/nillable/empty/no-fixed conditions hold | Zero coercion and altered conditions are rejected | Other validity requirements remain untested | Preserve nil distinctions in any proposed adapter | Nil is zero, missing economic value, or a complete accounting conclusion |
| Retain provisional mission status | Additive source evidence only | No release criterion newly satisfied | Independent domain/human/runtime evidence remains pending | Continue distinct ready work | Whole-row closure or manuscript acceptance |

Engineering evidence is the retained-byte/type-path correspondence and local
deterministic checker behavior. Numerical evidence is exact rational equality
for this finite set. Scientific/accounting interpretation gains no new
forecasting, measurement-accuracy or compliance evidence. This is not a
stochastic comparison and supports no method ranking.

The strongest alternative explanation for an apparent broader success is
scope omission: a lexical/value check can pass while a context, attribute,
unit or schema constraint fails. Full validation evidence could therefore
reject a filing without contradicting this bounded finding. A mismatched
source slice, overlooked custom value facet or independently demonstrated
lexical/value error would overturn the corresponding local conclusion.
The source-rule formalization and incomplete full-validation scope are the
weakest parts of any attempted extrapolation.

The separate R08 supplement preserves Version 3.44, 396 pages, not_ready,
53 obligations, six interactions and 46 operations, with zero whole-row
closures. No manuscript contradiction was established. Use verify.py with
no flags for future read-only replay; completed lifecycle stages are one-time.
