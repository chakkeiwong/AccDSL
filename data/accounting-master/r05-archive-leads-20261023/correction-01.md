# Correction 01 — distinguish archive payload digest from CDX length

23 October 2026, after the initial archive result was written. Raw CDX digests
were independently checked against SHA-1 of both replay bodies, and PDF trailing
bytes/response headers were inspected. The original HTTP bodies and headers are
unchanged.

For the 19 November capture, the retrieved 5,242,880-byte body's SHA-1 base32
exactly matches the CDX digest `UKWQHSIM42BGR4WYIYJF4X2GQS4TQAH3`. Its CDX
`length` field is 4,746,152, while the replay response's
`x-archive-orig-content-length` is 5,242,880. The body lacks `%%EOF` in its
last 1,024 bytes. Therefore it is wrong to call its payload hash inconsistent:
the digest corroborates the returned archive payload. The capture is still
rejected as a complete PDF because the returned body is truncated/incomplete;
the differing length fields have unresolved semantics.

For the 26 December capture, the 10,427,256-byte complete PDF has SHA-1
base32 `LS2BNUU7DSTN74XFWSOV2I6HHXBENRJ3`, exactly the CDX digest. CDX's length
field is 8,602,727, not the retrieved body length. The replay's SHA-256 and
byte count match the retained 10,427,256-byte, 358-page corpus PDF exactly.
Thus CDX digest and direct SHA-256 comparisons support byte identity; CDX
`length` is not used as a byte-count acceptance condition.

Correction to the initial result's characterization: replace “length/hash-
inconsistent” with “CDX digest matches the returned partial payload; the
response is not a complete PDF (no EOF trailer), and CDX/replay length metadata
disagree.” The complete byte-matched 26 December lead is unchanged. No source
admission or forecast claim changes. The initial wording is preserved in the
historical result copy; `result.md` and `archive-record.json` are superseded by
the corrected wording and bind this note.
