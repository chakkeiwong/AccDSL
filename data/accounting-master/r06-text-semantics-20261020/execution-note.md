# Implementation audit and retained boundaries

20 October 2026. Preparation inherited 2,777 protected files and the unchanged
36 dirty paths from the numeric inquiry. No completed predecessor stage ran
again. The source reading covers the base types, actual selected derivation
children, length/enumeration constraints, whitespace, calendar prerequisites
and the relevant Appendix F pattern rules.

A first source correspondence check found a wrong implementation assumption:
all 157 original packet values are tagged UnvalidatedText, while the portable
values are tagged Text. Their actual text is identical. The local checker
now compares those two expected records separately and retains both; it does
not treat the tag difference as a data error or silently change either tag.

Fourteen custom restricted nodes are present. Generic Python regex behavior
is not an XSD regex implementation. The local rules spell out the five
inspected pattern families; ASCII name/category membership is supported,
and non-ASCII initial names or enumeration names return unknown. Date
interpretation is limited to positive four-digit years without timezones;
other forms return outside_scope without a lexical-invalidity conclusion.

The DTR documentation is consequential even when its restrictions have no
numeric/string facets. Fifty-six selected text-block occurrences carry
unescaped XML-node/XHTML content obligations. Sixteen enumeration-set
occurrences have domain and set-semantics obligations. This unit records
both separately and checks neither by accepting their string lexical forms.

Preconstruction skeptical audit passes for the stated bounded deliverable.
Passing base/facet checks answers only that subquestion. No installed
processor, embedded-markup validator, financial type mapping or full filing
validation is executed or admitted. The exact original candidate text is
preserved, and no days-per-month, timezone, Unicode version or duration
canonicalization default is silently introduced.
