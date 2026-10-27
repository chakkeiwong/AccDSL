# Pre-implementation audit and evidence contract

MC13/14/23/24/25/26/28/32/34/35. Primary target:source lowers to the exact sealed
CompanyFunctions/1 request, and execution reproduces all six saved policy cases,
including complete three-year statements. Comparator is the typed compiler,
not a new evaluator. Independently check byte slices, line offsets and Unicode/
CRLF locations. Wrong request, wrong span, changed predecessor or unintended
evaluation veto the candidate. Check counts are explanatory only.

Main risks:duplicate-key loss, block capture, ambiguous endings, offsets computed
after normalization, or arithmetic evaluation during parsing. Tests cover each.
A local failure triggers repair; an invalid required baseline vetoes continuation
until repaired. No empirical ranking applies. Line-oriented quoting inherits the
existing notation; exact UTF-8 preserves source. Limits are convenience choices,
tested at boundaries. No new accounting, forecasting or numerical assumption is
introduced. Audit passes for a bounded optional frontend; broader work remains.
