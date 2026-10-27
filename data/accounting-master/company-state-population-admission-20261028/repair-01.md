# Preserve source refusal before verifying a successful chain

The first admission check reached a deliberately corrupted source. Native
execution retained partial/source_digest, but the wrapper tried to verify a
successful source-bound chain first and raised ValueError. This was a new
wrapper ordering defect. The original failed source remains rejected; no
population was fabricated or source admitted.

The first implementation and checker are preserved in attempt-01. The repaired
wrapper returns the full native source refusal before chain verification when
the supplied bytes do not match the declared source digest. All other complete
or partial chains still require verification. Continue in attempt-02.
