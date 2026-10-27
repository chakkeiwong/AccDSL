# Source-anchor wording repair — 27 October 2026

Verification attempt 01 stopped after 64 checks because AASB2026-2 physical
page 7 does not contain the shorthand word "earlier". Inspection of that page
shows paragraph 3 instead says "may be applied to annual periods beginning
before 1 July 2029" and requires disclosure. The expectation now uses that
exact passage. No interpretation, source byte or method specification changed.
The failed attempt and its manifest remain preserved. Run the next check in
a new attempt directory; never overwrite successful evidence.

Attempt 02 then stopped at check 90. AASB107 paragraph 44A breaks the word
"non-cash" across a physical line; whitespace-normalized extraction yields
"non- cash". The expectation now matches the complete extracted phrase
"cash flows and non- cash changes". Direct inspection confirms the intended
cash/noncash distinction. All earlier page checks, including the repaired
AASB2026-2 passage, passed. Preserve both failed attempts.
