# Surface and rendering disposition

The root-only audit does not expand inputs and cannot describe the body. It is
retained as a scope diagnostic; the final audit targets the changed section.
The missing `sec:apple-legal` target is a cross-file false positive: it is defined
in `sections/apple-legal.tex`, resolves to Section 2.12 in the rendered PDF and
is covered by the full-tree checker. The new unreferenced section label supports
navigation and future citations; it is retained intentionally. No typo or
long-sentence candidates were returned. Counts are diagnostics, not acceptance.

Initial page 35 began with a one-word continuation, “flows.” The defense-cost
sentence was repaired without removing services, amounts, timing or obligations.
The first build/render and surface outputs remain under explicit before-repair
names; `render-repair-comparison.json` resolves moved image paths. Final pages
34–36 were read again in order. Page 33 and navigation 1–7 are pixel-identical
to the already inspected initial rendering. Two builds took 15.21 and 3.73
seconds; their receipts retain actual duration. Final log is clean.
