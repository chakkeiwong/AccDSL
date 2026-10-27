# Recovering company-family evaluation

A company-family checkpoint records completed member evaluations and the next
member to evaluate. It binds the exact family, source bytes and local method
descriptor. A completed member may contain a partial accounting path: unknown
payroll has finished evaluation with an unresolved annual report. It does not
become an interrupted work item merely because accounting could not continue.

This boundary permits recovery between members, not within a member's year or
operation sequence. The completed records must be the exact ordered prefix of
the authored family. Resume first replays that prefix to validate it, then
evaluates at most the requested number of new members. The result separately
reports validation replay and new work counts. The budget is a count of new
members and does not bound total replay cost. A zero budget is valid; an empty
family is already finished. Boolean budgets and noninteger counts are invalid.

The checkpoint has exactly profile, family_sha256, source_sha256,
engine_sha256, next_index and completed. The prefix length equals next_index.
Each member entry preserves its ID, path and result hashes, execution status
and whole result. A changed model, method or source requires a new operation;
it cannot be disguised as resume. Rehashing a forged report does not pass
trusted recomputation. No schema migration is inferred.

Publication is a pure reference exchange over an explicit work world. That
world has a work owner, generation, checkpoint and immutable decision list.
Each decision stores the exact request and complete response. A new request
checks its expected generation, checkpoint and dependencies before appending
one decision and replacing the checkpoint together. Invalid or stale requests
leave the supplied world unchanged. A different request under an existing
identity conflicts. An exact retry returns the old response before comparing
the request with the current head, so a later publication cannot make a
previously completed request appear uncommitted.

After a lost acknowledgement, the client may observe either the unchanged
world or the complete new world. Retrying the same request publishes in the
first case and returns the stored response in the second. A world containing
only part of the checkpoint/decision/generation update is invalid. The
reference validates the entire decision chain by replay; this is correctness
evidence for the small exchange, not a production persistence algorithm or a
claim of efficient recovery. It changes no company accounting state and
establishes no physical crash durability.
