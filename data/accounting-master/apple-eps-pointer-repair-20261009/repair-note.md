# Final live-pointer correction

9 October 2026. MC32/34. Final review after the EPS unit's manifest was written
found one stale line at the bottom of the live roadmap: its label still called
Version 2.10 the current manuscript, although the top and current checkpoint
correctly named Version 2.11. Correct that link and preserve its before-copy.
The scientific result, PDF and closed EPS artifacts remain unchanged.

Skeptical audit: use the completed Version 2.11 PDF hash and result as the
comparator, not the historical tax paragraph surrounding the link. Link
existence alone did not detect this semantic mismatch. The repair passes when
the live current-manuscript label and target agree with the completed PDF, all
four pointer hashes are preserved before editing, and the closed manifest
still resolves using those copies. This is a small pointer repair, not a new
source study or readiness assessment.

The repair's cumulative `run-manifest.json` and `completion.json` are the next
unit's preservation entry. They include the unchanged EPS artifacts and final
live pointers. The EPS unit's original manifest resolves its pre-correction
pointer paths through this repair's `pointers-before/`. Do not rerun the closed
EPS generator or rewrite its hashes.
