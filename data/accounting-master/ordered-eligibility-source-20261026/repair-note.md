# Source conformance repairs

26 October 2026. First full replay passed all 72 saved gate comparisons, then
the missing-required-known control failed because the fixture attempted to
remove a non-existent nonempty declaration. The source uses an explicit empty
list. The control now removes the actual declared line. This is a harness
failure, not evidence against the grammar or the saved gate. No earlier
evidence was modified.

Author review also narrowed diagnostics: JSON duplicate-key hooks do not expose
the duplicate key offset. They now report the containing declaration, rather
than incorrectly marking the opening brace as the offending token. UTF-8
offsets remain exact for that declared span. Line splitting now recognizes only
LF/CRLF, so a valid Unicode line-separator character inside a JSON string does
not incorrectly become a declaration boundary.

Post-pass review found the renderer still used Python splitlines on reused rule
source, which splits a literal Unicode line separator inside a JSON string.
It now splits only LF. A full manifest roundtrip containing that character
passes. Added explicit false-approval/malformed-late-stage execution and
duplicate-stage controls. Final result: 35 controls and 603 assertions.
