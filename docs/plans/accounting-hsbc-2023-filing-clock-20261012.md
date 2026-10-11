# HSBC 2023 annual-report filing clock

12 October 2026. E01/MC01/04/05/30/33–35; G5/G11/G13/G18. Question:
does an official regulator record identify the original 2023 HSBC Holdings
plc annual filing, and how does its event clock relate to the selected
annual-report PDF and the 21 February 2024 results-group date?

Baseline: the selected `hsbc-2023-annual` PDF and its coverage URL/hash,
the two closed HSBC results-group units, and the frozen 56/136 selected-date
inventory. The candidate regulator issuer identifier is SEC CIK 1089113;
verify its returned legal issuer before using any rows. No inspected local
HSBC source or completed result supplies this regulator event.

Evidence contract and diagnostic roles: a regulator-event record requires
the official source body, HSBC Holdings plc identity, original Form 20-F,
report period 31 December 2023, exact accession, filing date, acceptance
clock and primary-document name. Preserve any 20-F/A in the inspected
period separately. A wrong parent entity, wrong report period, unavailable
source, missing event or ambiguous original vetoes the event inference.
A selected-file clock additionally requires proved document/version
correspondence; a title, year, matching URL or nearby event alone cannot
satisfy that criterion. The results-group date, URL digits, PDF internal
approvals and HTTP dates are explanatory only. No first-public-access time,
unchanged selected bytes, exhaustive amendments or G13 completion follows
from a passing metadata check. Preserve the source, request receipt,
bounded event findings and uncertainty in
`data/accounting-master/hsbc-2023-filing-clock-20261012/`.

Skeptical audit: a Form 20-F may incorporate or wrap an annual report, so its
filing event cannot automatically date the complete selected PDF. The exact
parent issuer and period are the comparator, not similarly named HSBC
subsidiaries. CIK 1089113 is a lookup hypothesis, not a verified identity.
Read the current submissions index first; if 2023 is absent, fetch only
the listed historical shard needed for that period. Inspect originals and
amendments in the returned scope rather than selecting a convenient row.
Source GETs are bounded to three requests, 45 seconds and 5 MB each; a
403 or transport failure ends that unchanged route. No document bytes are
admitted from HTTP success alone. Standard-library CPU parsing fits this
source question; no stochastic comparison, GPU or new dependency is needed.
The resulting event or access limitation is useful only within this scope.
After this unit, move to an E07/E08/E14 source obligation unless a genuinely
report-specific version lead is exposed. Do not repeat the Group archive.

First command: bounded GET of
`https://data.sec.gov/submissions/CIK0001089113.json`, preserving headers and
body locally. Use the existing trusted curl capability for external reads.
No runtime implementation, corpus rewrite, manuscript increment, paid
review, outreach or publication is planned. The user's subsequent Git-commit
instruction applies to the reviewed work, subject to filesystem permissions.

Continuation audit: the retained SEC body verifies CIK 1089113 and contains
the original 2023 event at recent row 935, so no older shard is needed. The
official archive separately links a 490-page Form 20-F PDF with an advertised
size of 6,757,111 bytes at line 8301. Its annual report is 450 pages. Read that
distinct issuer-hosted Form 20-F candidate to check cover, report period and
incorporation scope; do not equate it to SEC-filed or selected annual bytes.
For this one identified PDF, revise the transfer cap to 8 MB (from 5 MB),
retaining the three-request/45-second limits. The increase follows the
observed source size, not an unbounded search. Compare selected text spans
only to explain scope; full equivalence is neither tested nor inferred.
