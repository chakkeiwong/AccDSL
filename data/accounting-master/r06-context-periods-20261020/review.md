# Author review

The pre-run plan identifies the right comparator: role-specific XBRL implied
boundaries rather than lexical date order or a fixed reporting-year length.
The primitive schema date value and XBRL endpoint interpretation are separate.
Missing timezone stays absent; none of the code calls timestamp conversion or
the host's timezone APIs.

The calculation implements a bounded Gregorian profile and independently
cross-checks ordinals and rollover against Python date. Fixtures cover leap
years/centuries, month/year ends, a valid same-day interval, a zero implied
interval, a reversed interval, invalid calendar tokens, XML-only whitespace,
scope refusals and wrong context shapes/forms. The source shape is tested as
an ordered child sequence so duplicate elements cannot disappear into a dict.

All 382 declaration anchors and parsed declaration attributes match the
source map; direct item substitution and periodType are inspected. All
1,127 facts have their own exact context join and an opposite-type rejection.
The three corruption checks operate on separate copies, preserving source
records. Prior source/portable evidence is bound and all financial Context
time/calendar fields stay Unknown.

The actual c-114 witness rules out the literal strict-date shortcut. The
364/371-day observations rule out describing all retained annual spans as
365 days; no financial day-count convention is inferred. Thirteen repeated
period signatures are explanatory only and confer no context equality.

The source paragraph's statement about hour 24 conflicts with its cited XSD
Second Edition lexical rule; the canonical form excludes 24. The discrepancy
is recorded directly and its cause is not assigned to a historical edition.
The selected actual data contain no time components, so this does not block
the present interpretation. Broader time forms need their own source-supported
handling and do not become invalid simply because this checker returns
outside_scope.

No confirmed manuscript defect follows from this unit. The proposal deliberately
preserves financial time as Unknown in these native examples. The result adds
documentary evidence, not an admitted interface or financial mapping. Author
review is not independent/domain/human acceptance. Current source-value records,
53 obligations, six interactions,46 operations and zero whole-row closures
must remain unchanged through recording and read-only replay.
