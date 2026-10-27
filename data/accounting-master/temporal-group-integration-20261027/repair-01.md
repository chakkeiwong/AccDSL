# Escaped-reference repair — 27 October 2026

The first builds completed, but the Python sentence transform interpreted a LaTeX backslash-r as a carriage return. Compilation success did not establish the intended cross-reference. The pre-repair generator, preservation record and affected source are retained in repair-01; both first-build PDFs/logs remain in build-attempt-01.

The sentence is now a raw Python string. The target source was regenerated from the protected 5.26 predecessor using the declared transform, and the precise edit record was updated. A byte check rejects any carriage return and checks the literal LaTeX reference. No scientific evidence or predecessor source changed. Build attempt 02 and full source/reference/render verification are required before link advancement.

This was a document-generator defect, not a rejection of the timing method.
