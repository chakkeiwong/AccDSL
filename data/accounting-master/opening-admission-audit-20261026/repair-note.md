# Audit fixture repair

Repeating 65 full event commands hit the native aggregate record-structure limit
before the explicit command count. Preserve that observation as its own probe.
Use 65 empty command objects to isolate the count check: native opening validate
does not inspect individual command shape. No native code or limit changed.

The attempted zero-capacity accepted-opening probe was wrong: the existing typed
schema requires a positive bounded map capacity. Record its actual typed-memory
refusal and use capacity one as the valid empty-opening contrast. The audit
does not promote an assumed zero-capacity behavior into a native fact.
