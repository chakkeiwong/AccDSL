# Explicit typed parameters over a complete authored method

26 October 2026. MC05/15/17/18/20/24/25/33/34. Plan:
docs/plans/accounting-parameterized-method-construction-20261026.md.

Skeptical audit passes with deliberately narrow ownership. Existing source
already authors the full method algorithm and dynamic memory paths exist.
The missing stage here is substitution of explicit event-dependent constants
and escaped read pointers into the complete method before its ordinary typed
validation. Native full-intent eligibility remains explicitly selected and
separate. This unit does not claim a portable lifecycle contract, arbitrary
dynamic loops, general accounting rules or inference of real company facts.

## Template and instance

ParameterizedCompanyMethod/1 contains profile, transition_profile, context,
parameters, method_template, input_schema_definition and residuals. All fields
are closed. Each parameter declares an existing scalar type and a source.
The method template is a tree of explicit literal, object, array or parameter
nodes; only named parameter nodes substitute values. Literal data is never
reparsed as syntax. Objects have literal field names; there is no dynamic object
key generation, JSON patch, callable, import or evaluator selection by method
name. The complete monetary algorithm remains visible in the template tree.

A source is one of: typed known full-intent event input; event metadata id/date;
current book metadata date/memory_schema; or a pointer assembled from literal
segments and earlier text parameters. Declaration order binds derived pointers;
forward references, cycles and unused parameters refuse. Exact JSON pointer
escaping uses the retained type helper; slash, tilde and Unicode remain data.
Required unknown input returns unresolved. Event values must retain their exact
declared type and provenance. No value is coerced from text or substituted from
another chart. A template's fixed context must equal the current book context.

The template explicitly carries the typed memory input-schema definition. The
existing schema compiler derives its digest for the current context. The method
tree contains a dedicated derived-input-schema parameter bound by that compiler;
this is a declared compiler primitive, not a callback. State schema comes from
the current book. Supplied schema registries are checked against their digests;
the compiled input schema is added without silently overwriting conflicting
content. The complete request contains the unchanged full event, current-state
digest, complete method and its digest, schemas and memory definition.

Binding fields in the call are expected template, book and event digests. All
are checked before construction. The resulting instance includes resolved
parameters and a source identity for each. A local mutation cannot alter the
input template or book. One-megabyte serialized input, 4096 template nodes and
48 levels are inherited reference limits, not production capacity evidence.
No partially constructed method is returned after a refusal.

## Accounting and eligibility boundary

The constructor must not import the native lifecycle specializer. It imports
only the retained typed method frontend, scalar/type helpers and schema compiler.
After construction the unchanged typed frontend checks the full method against
the actual book/event; the existing source renderer must lower back to that
method exactly. This validates the authored method, not full event eligibility.
The test harness separately checks the explicitly selected native contract and
uses native.make_request only as comparator, never inside construction.

Sale and collection templates are supplied for the two retained contexts.
They retain fixed role mappings, unit-cost pointer and financial algorithms.
They vary claim identity, customer, due and event dates, event id, current-state
schema and the resulting claim balance pointer. Monetary input values remain
ordinary event values, so changed amounts exercise the financial evaluator.
Different accounts, algorithms, policies and map iteration require explicit
new declarations or later work; a chart-specific template is not a universal
company template.

## Evidence and repair criteria

Compare the full request with native specialization for all retained sale and
collection events and new consequential sequences. Compare complete transition
results, not cash only. Check both charts, several escaped/Unicode keys, new
customers/due dates/amounts, multiple claims and changed current schema. Check
rendered source/typed equality. Deliberately edit an algorithm and show that its
changed financial consequence is visible and differs from the selected native
contract. Eligibility refusal remains owned by that selected contract.

Malformed/duplicate/unused/forward parameters, wrong source types, stale
template/state/event, unknown inputs, incorrect context, invalid pointer and
resource limits must refuse without returning a request. Preservation hashes
cover the audit evidence and native/frontend dependencies. False equality,
hidden native construction, lost unknown or source mutation veto acceptance
and trigger repair. Counts/runtime are explanatory only. No statistical
ranking, source/accounting admission, production readiness or forecast evidence.
