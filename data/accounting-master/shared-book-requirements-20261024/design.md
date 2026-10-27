# Exact collection totals as explicitly bound requirement inputs

24 October 2026. Native return invariant uses exact Fraction sums for signed book
balance and inventory allocation. The inspected Core 0 opening-book check also
uses a fixed Fraction sum; it does not provide the complete/partial collection
and unknown-reason semantics needed here. Reuse exact rational arithmetic and
the recorded collection/guarded evaluators, not their unrelated state adapters.

MethodCollectionTotals/1 embeds a MethodCollections/1 snapshot definition and
a MethodRequirements/3 assessment, with an exact binding for every assessment
input. A binding selects either a declared global input or a sum over one declared
collection field. The selected type and role must equal the original assessment
input type and role. Sum fields are rational with exact dimensions/context/scale;
no selection predicates, sign conversion, currency conversion or implicit filtering
are introduced. Field projections and required subsets are caller-authored.

A complete collection with known field values has the exact reduced rational sum.
The empty complete sum is zero. A partial or absent collection, or any unknown or
missing selected field, produces an unknown total and preserves all observed
contributors and their original row positions/reasons. Cancellation of known
terms cannot resolve an unknown contribution. A correctly computed subtotal of
observed rows is retained only as a diagnostic and is never bound as the total.

The original guarded evaluator assesses bound totals and globals. All complete
snapshot and scalar findings remain visible, with invalid > unsupported > unresolved
precedence. A passed sum does not override a duplicate account, context mismatch
or missing registry entry. Source references on the original assessment definition
remain caller declarations; the output supplies exact derived binding lineage and
both original definition and values hashes, without relabeling derived sums as
raw source records. Method eligibility, source/accounting admission and executed
stay false. No state changes or proposal application occur.

The retained declaration separately checks both directions of account-registry
membership and unique keys against the pinned native ACCOUNTS list. It checks
book sum zero, inventory = other inventory + lot carrying, refund-liability =
negative component refund, recovery asset = component recovery, and per-lot tax
basis = carrying. Other native domains, disposition memory, cash funding and
event effects remain explicit residual conditions. Context and currency follow
the supplied retained legal book; this is not an actual company reconstruction.

Limits inherit snapshot bounds and add 8,192 total visits across sum bindings.
Repeated sums consume work each time; a definition may not evade the bound by
naming the same field repeatedly. This is an engineering default with boundary
tests. Empty, unknown, partial, duplicate registry, wrong sign and dimension cases
are required evidence. Native comparisons use intact saved states and isolated
mutations; full native-invariant equivalence is not claimed.

Audit passes for this scoped increment. Primary criterion is exact independent
arithmetic and declared native comparisons; invariant promotion is vetoed by
uncovered state domains, not by check counts. The next repair must connect these
predicates to typed atomic monetary effects and replay with explicit source/state
identity. No stochastic ranking or forecasting evidence follows.
