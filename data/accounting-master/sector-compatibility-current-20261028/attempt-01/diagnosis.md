# Attempt01: extracted representation is not a native record

All seven full PAA results and21 controls passed. The first bank comparison
failed because the worked-case extraction stores canonical Fraction strings
and omits dependency_refs, while the full native records store numerator/
denominator objects and explicit dependencies. The quantities are not shown
to differ. Attempt02 compares the extraction's defined value/status/diagnostic
projection, checks every native dependency exists, and then independently
recalculates the amounts and ratios. Full native packet bytes remain locked.
No financial implementation, extraction or expected value is changed.
