# Auxiliary label parser repaired

Both PDF builds passed on their first attempt. The first verification invocation
passed source preservation, references, warning comparison and page bounds for
both documents, then failed to locate the standalone body-end label. Its regular
expression incorrectly required two literal backslashes. A first correction
also lost a digit escape in tool transport. The final parser uses the inspected
literal label prefix and brace delimiters; no manuscript or PDF changed. Re-run the
verification only, not the completed prepare/build writers.
