# Source-anchor audit repair before completion

20 October 2026. The first lifecycle check passed byte/range consistency and
all 50 exact mathematical assertions. A separate semantic spot check found
that some anchor labels pointed to the wrong nearby passages. The constructor
used Python `splitlines`, which treats PDF form feeds as extra line breaks;
the inspected `sed` line numbers count newline characters only.

Preserve the first constructor, source ledger and check result under
`anchor-attempt-01/`. Repair the constructor to count newline delimiters only
and rebuild only the ledger's anchor offsets/excerpts from its existing
declared line ranges. Do not repeat the one-time constructor or lifecycle
`--check` stage. Read each repaired anchor and directly replay `compare.check`
before recording. No calculation, source bytes, scope, baseline or manuscript
changes. The first check is evidence of internal range consistency, not of
semantic source fidelity; this follow-up supplies the latter author review.
