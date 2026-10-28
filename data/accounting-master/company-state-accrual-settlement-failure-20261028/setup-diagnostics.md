# Pre-run fixture diagnostics

28 October2026. Native unmodified accrual/report/carry/payment/report smoke
completed. Reports showed2027 expense5/payable5/cash20 and January1,2028
expense0/payable0/cash15. These are setup diagnostics, not the evidence result.

The first deliberately bad payment mutation added an expense account without
adding its role classification. Native static validation correctly refused
with role_class_population. A diagnostic print then raised KeyError: current
because invalid-program results have no current field. This was a harness
mutation/printing error, not evidence about the economic control. The mutation
now declares the extra expense role explicitly; the complete run preserves its
actual outcome and checks all required states independently.

