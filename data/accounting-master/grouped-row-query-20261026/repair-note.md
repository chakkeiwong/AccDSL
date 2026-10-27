# Numeric fixture correction

The first run reached the numeric controls after the historical-state and
earlier adverse comparisons passed. It stopped while deriving the synthetic
numeric leaf because that fixture omitted the required company context.
The failure was `numeric_company_context`, before query execution.

Attempt-01 preserves the implementation, comparator, controls, assertions and
dependency lock. The correction uses the existing book's declared monetary
type for the synthetic metric. It changes no query logic or financial method.
The same exact-rational ordering and wrong-unit/scale controls remain required.
