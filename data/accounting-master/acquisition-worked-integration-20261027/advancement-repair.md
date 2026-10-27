# Preflight guard repair — 27 October 2026

The first advancement invocation stopped before any backup, gap-directory or
control write. Its whole-object equality guard incorrectly required two control
schemas to match: the catalog includes work-unit routing, while next-plan retains
historical execution results and distinct metadata. Their active candidate, PDF
hashes and routes are the consistency boundary.

The repaired preflight compares those explicit active fields. Each object's other
fields are independently preserved and checked, so the repair neither discards
history nor weakens concurrency protection. The failed invocation did not advance
5.29. This is a harness-precondition repair, not evidence against the manuscript.
