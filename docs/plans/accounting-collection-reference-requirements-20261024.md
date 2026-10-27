# Make finite collection and reference conditions reusable

24 October 2026. S2–S4; MC05/13/15/17/23/24/26/27/31 and
G2/G3/G10/G13/G15/G17. Preserve all recorded scalar versions and Version 3.60.

Question: can independently authored collection declarations reproduce the
retained return record's identity, reference and chronology checks without
confusing an input list with an executed accounting state? The exact baseline
is company-return-schema-20261023/return_schema.py validate, especially lot/event
identity, component references, opening acquisition dates, event date ordering,
period membership and the known-lot/sold-lot sequence. Existing generic IR and
repeat/authoring facilities must be inspected before selecting a new layer.

Skeptical audit: unordered membership cannot establish that a lot existed before
a sale. Sorting events to make them pass changes the supplied schedule. Equal
dates retain caller order. A missing or incomplete collection cannot silently
become an empty complete collection. Unknown identities cannot be guessed; a
known duplicate remains invalid even if an unrelated value is unknown. A unique
reference is not source authority or book-state feasibility. Do not map a true
caller finding to a missing collection calculation.

First audit exact source branches and existing reusable machinery. Separate
snapshot conditions (uniqueness, references, per-row predicates and date order)
from ordered identity creation/consumption and from monetary state effects.
Implement the smallest coherent reusable fragment with explicit typed records,
complete/unknown collection semantics and no implicit normalization. Use the
existing scalar evaluator where its semantics match. Keep ordered lifecycle and
shared-book effects as distinct obligations until their own checks exist.

Primary criterion: independent expectations and matched original-validator
cases for exactly the selected branches; source identities and field context
must survive lowering. Known contradictions, malformed records, stale hashes,
missing coverage declarations or changed order veto acceptance. Existing count
and AST inventories are explanatory, not complete branch attribution. No whole
method, economic feasibility, actual-history or accounting-admission claim.

Default audit: the retained schema currently requires complete structural IDs
and dates; extending it to unknown collections is a new declared language rule,
not claimed legacy equivalence. Nondecreasing event dates and half-open periods
come from inspected native code; exact caller order is preserved. Empty-list
behavior must be explicit per condition. Bounded work and source/record size
limits are engineering hypotheses to be tested at the boundary, not financial
restrictions. Record chosen limits and their refusal behavior in the design.

Evidence contract: compare selected validators and independently authored
typed cases; retain each original result, common result and any deliberate
unknown distinction. Add adversarial duplicates, missing references, equal-date
reordering, boundary dates and unknown/known contradiction mixtures. A source
or implementation mismatch triggers repair; a candidate failure does not end
the simulator program. No stochastic ranking or forecasting run is involved.

Artifacts: data/accounting-master/collection-reference-requirements-20261024/.
Use bounded CPU-only deterministic tests; preserve plan, command/environment,
commit and exact source/output hashes. Refresh controls after evidence passes.
S1–S5 remain partial, S6 held, S7 deferred; full method eligibility stays open.
