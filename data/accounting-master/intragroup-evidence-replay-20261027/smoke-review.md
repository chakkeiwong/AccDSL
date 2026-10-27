# Copied smoke and audit-bookkeeping refinement

The first copied smoke passed one positive and one refusal in each of the five
profiles: ten exchanges, 431 comparison checks and 169 independent rational
assertions. There was no financial or oracle mismatch and no observed undeclared
access. Its exact preparation and output are retained as debugging evidence.

Before full replay, review found that dependency-version metadata was collected
after the saved access inventory. The audit hook was active, but those later
reads were absent from the persisted inventory. Move metadata collection before
the inventory snapshot and prepare a fresh tree. This changes only audit
bookkeeping, not native code, inputs, expected outputs or comparison criteria.
The full run will verify this revised driver; do not reuse the smoke's manifest.
