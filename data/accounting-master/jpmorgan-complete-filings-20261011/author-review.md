# Author review

Read the four downloaded PDF metadata records, extracted text and source
receipts. Confirmed each candidate has the expected issuer, Form 10-K, SEC,
Item 1A and signatures markers. Cross-checked the four prior exclusion notices
and retained their original annual-report hashes.

The first checker attempt incorrectly required a contiguous `2025 Form 10-K`
phrase in a notice whose wording places “2025 stockholders’ equity” between the
year and “Form 10-K”. The failed check is preserved in
`checks-attempt-1.json`; the corrected predicate passes. This does not alter
source files. The current manuscript was unchanged and not rebuilt or reread.
Semantic filing completeness, byte-vintage equality and independent acceptance
remain pending.
