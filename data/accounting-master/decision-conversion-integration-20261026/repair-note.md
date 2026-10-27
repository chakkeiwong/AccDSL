# Verification harness repair

26 October 2026. Both build-attempt-01 PDFs compiled successfully. The first
verification failed before citation checking because transport escaping
removed regular-expression backslashes in the citation pattern, producing
`multiple repeat at position 8`. This is a verifier implementation error,
not a document or scientific result failure. The failed script is preserved
as verification-attempt-01-integrate.py.

The corrected pattern builds punctuation with re.escape. No manuscript
source, predecessor, successful evidence or PDF changed. Retry only the
unfinished verification phase. The build budget remains one completed dual
build; no successful evidence writer is rerun.
