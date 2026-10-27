# Preserve the date-pattern repair

Attempt-01 rejected a valid annual date. The written Python regex contained
literal d characters because the JavaScript transport consumed its backslash.
The checker then assumed a queries field despite the invalid result. This is
an adapter authoring/checker defect, not a native history or source failure.

The failed source and checker are retained. The date pattern now uses explicit
[0-9] classes, alongside the existing date-format validator; the checker guards
the baseline status before reading queries. Continue in attempt-02.
