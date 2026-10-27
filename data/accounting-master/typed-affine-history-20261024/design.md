# TypedAffineHistory/1 reference contract

24 October 2026. This is a finite conditional family over exact rational unknowns.
It is a new profile; the monetary history, measurement attachment and native method
contracts remain unchanged. Only authored assumptions are used in its examples.

## Closed record and semantics

The definition has exactly profile, scope, value_type, opening_date, dates,
accounts, memory, balance_premise, templates, events, measurements, obligations
and state_constraints. scope has name and exclusions. value_type is one rational
currency dimension with exponent one, a positive exact scale and the complete
book context. Dates are canonical civil dates. No temporal key occurs in the
book context. Opening precedes the strictly ascending unique snapshot dates;
events are in nondecreasing date order, strictly after opening and no later than
the last snapshot. Same-day order is the supplied list order.

accounts maps each name to an opening domain and has the common monetary type.
memory maps each name to exactly type and domain. Every type is rational and
uses the exact book context. Dimension exponents and positive rational scales
follow MethodRequirements/2; a field is never silently converted to another unit.
A domain has interval, premise, source_ref. interval has lower, upper,
lower_inclusive, upper_inclusive, with reduced rational strings and nonempty
support. A premise is the unchanged JointMeasurementConstraints/1 proposed
interpretation record or null. Null prevents conditional solving. Shared premise
identities must denote identical records. Source references preserve their meaning
as authored support pointers; they are not externally verified facts.

A template has event_type, postings, memory, premise, provenance. Each posting or
memory entry maps a declared field to a coefficient with exactly value and type.
Coefficient values are fixed nonzero reduced rationals; their type times the
event_type must equal the field type, including scale and context. All posting
coefficient values sum to zero, since every posting has the common book type.
Balanced incidence is bookkeeping algebra, not accounting authority. An event has
id, date, template and amount; amount is a nonnegative domain in the template's
event_type. Unknown-dependent coefficients and nonlinear expressions are rejected.

A measurement has id, date, value_type, terms and domain. date names an opening
or snapshot date. A term has kind (account or memory), field and coefficient.
Coefficient type times field type must equal the measurement value_type exactly.
The sum of typed terms is constrained by domain. A snapshot includes every event
on or before its date. Identified memory remains in the family even if unmeasured.

A state constraint has exactly id, value_type, terms and domain with the same
typed term rules. It constrains the opening and each intermediate post-event
state, including separate events on one day. There is no implicit nonnegativity,
inventory capacity, cash limit or contract rule. The result reports the explicit
constraint IDs and checked states. An empty list means none were checked. Callers
retain missing target rules in obligations (id, meaning, nonempty affects list).
Missing premises stop solving; target obligations permit a relaxed candidate but
keep target_existence unknown and formulation_complete false.

## Lowering, result and failure interface

validate_and_lower(definition,budget) checks all types before constructing a
private scalar skeleton for the existing monetary structural/date/domain
validator. This skeleton is not an economic monetary interpretation of quantities.
The result preserves the complete original typed definition and a digest of the
explicit numeric lowering. build_problem adds constraints at each prefix to the
exact lower-level rational solver. No state constraint is merely an endpoint test.

replay_witness evaluates the original typed definition with Python Fractions,
independently of Z3 expressions and the scalar skeleton. It checks every domain,
opening balance, event postings, post-event balance, state constraint and snapshot
measurement. Its trace retains field types and each event size type. The same
typed definition and amount assignment must reproduce the complete trace exactly.
verify_result permits alternate independently valid witnesses and rechecked
unsatisfiable cores, but rejects changed definitions, status, boundary, types,
trace, constraints or unsupported completeness claims.

assess returns conditional_family_witness, candidate_witness_with_unresolved_obligations,
conditionally_infeasible, unresolved, unknown, unsupported or invalid. Target
existence, candidate feasibility, search completeness and formulation completeness
remain separate. A solver/resource unknown never means empty. No response admits
source facts, accounting, native execution or an executable real-company opening.
The profile uses continuous rational quantities, not integer lots or event discovery.

## Bounds and acceptance

Reuse the existing byte/scalar/depth, 256-variable, 256-event, explicit budget and
exact rational limits. Additionally cap total typed coefficient terms and
constraint-state instances and expanded constraint terms at 4096 each. Build
symbolic states incrementally in event order. Permit at most 256 state constraints. A zero
solver budget remains unknown. Parser/text authoring remains a separate dependency;
this profile specifies its Python record interface only.

Acceptance compares a monetary embedding with the unchanged monetary family and
tests typed unit-price effects, explicit scale mismatches, mixed contexts, missing
premises, forged replay, unresolved target obligations and resource stops. A sale
before a replenishment may satisfy the closing balances while violating an
explicit inventory bound at the intermediate state. Reversing same-day order must
change feasibility. These are deterministic conformance cases, not empirical
evidence of accounting compliance or forecast performance.
