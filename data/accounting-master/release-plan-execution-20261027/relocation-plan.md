# Protected candidate relocation preflight

27 October 2026. C1/C6 preflight; MC24/25/30/31/32/33. This continues the
reviewed release-closure plan without asserting full C1 or C6 completion.

Question: do the copied 5.51-R1 document sources build both volumes without
reading source or evidence from the original AccDSL worktree? Baseline: final
attempt-04 PDFs and all candidate input bytes, including the preserved bibliography.
Copy only documented package inputs to a new /tmp directory, use an absolute
writable local TeX cache, disable shell escape, and run the two documented roots.

Pass: both builds succeed, extracted text agrees page by page with the candidate,
page counts agree, no undefined references/citations appear, original inputs stay
unchanged, and the TeX recorder shows no reads from the original worktree or
MathDevMCP. Record system/toolchain inputs separately. PDF byte equality is reported
but is not required because metadata timestamps are not controlled. Financial
component result equality has its own stronger checks and is not relaxed.

Vetoes: changed candidate input, failed build, different page text, unresolved
reference, or an original-worktree read invalidates this preflight and triggers
repair. External TeX/font files must be listed; an undeclared source dependency
cannot be treated as a system dependency merely to pass. Runtime, warning counts
and file counts are explanatory. The audit does not prove an independent
installation, network/process isolation, complete evidence closure, accounting
correctness, whole-document readability, or distribution rights.

Skeptical audit: copying prior auxiliary files could conceal a missing input, so
exclude all generated TeX intermediates and caches. Use a fresh directory and
fresh outputs. The original candidate remains unchanged. Comparing page text
checks content/layout pagination, not independent mathematical correctness.
The earlier relative font-cache failure is repaired with an absolute cache.
No research experiment, stochastic comparison, dependency install or frozen
writer is involved. Timeout is 240 seconds per volume; a failure is local.

Command: python3 data/accounting-master/release-plan-execution-20261027/relocate_manuscript.py
Evidence: relocation/ and relocation-result.json under this execution directory.
