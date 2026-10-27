# Selecting a policy-generated company path by information date

A company input path and a settlement rule can become available on different
dates. Reusing the input path's date for the rule would admit information that
was unavailable at the requested cutoff. The query therefore selects the
parent information, policy body and materializer separately, using one view
and cutoff. Its selected result is a derived synthetic consequence.

The policy declaration binds the locked exchange, exact parent and child path
hashes, policy hash and materializer descriptor hash. The descriptor binds the
local generator source and input schema. Executable callbacks come from the
trusted local caller; the exchange does not supply executable code. The
declaration must cover the two exact components once each. External trusted
observation hashes bind authorship, publication, ingestion and acceptance
declarations to those bytes. A missing timing declaration is unresolved; an
observed reference whose bytes are absent or misbound is invalid.

For a dated view, any ineligible required dependency makes the result
ineligible. Otherwise an unresolved dependency makes it unresolved. Only
eligible parent, policy and method information produces `eligible_synthetic`.
Archival exploration retains the conditional calculation without temporal
admission. Day precision denotes a half-open interval; an equal exact instant
is allowed, while publication sometime during a day is not assumed to have
occurred at its beginning.

Before returning an eligible result, the query regenerates the whole path and
accounting result and compares canonical content hashes. This includes changed
allocations and unchanged fields. A valid partial calculation retains its
unresolved annual lines and cannot provide closing memory for a later year.
Unknown policy amounts and unsupported policy scope retain their respective
outcomes instead of becoming zero settlements or successful accounting.

No child authoring, publication, ingestion or acceptance date is inferred.
Recomputing now from eligible inputs establishes what this local method
derives; establishing that a calculation actually existed before the cutoff
requires separate historical execution evidence. Every branch keeps
`historical_execution_established`, `real_world_admission`,
`forecast_admission` and `real_behavior_evidence` false.

The synthetic fixture separates the clocks: the parent is public on March 7,
the policy on March 10 and the method on March 12, all in 2025 with day
precision. Public eligibility begins on March 13. These dates exercise the
selector and do not describe actual company information or model releases.
