# Typed state and history inspection request

28 October 2026. T01/T03/C04/R01 supporting work; MC04/08/09/13/18/19/24/25/28/33/35.

## Skeptical audit

The common construction contract now distinguishes state categories and native
responsibilities, but a caller still lacks a closed request with explicit
subject, owner, source binding and historical query. Add a bounded typed
inspection request over the guarded native operation path. Do not claim that
one owner implements the other native profiles or that a request language
creates actor knowledge. T01 remains open for broader common definitions.

One exact owner is supported initially: CompanyOperationPathDraft/1. Requests
for another profile, a cross-profile join or public/system/manager knowledge
return unsupported rather than invoking arbitrary code or using the full audit
record as a policy observation. No code path or filename comes from request
input. The owner is selected by the local reviewed adapter.

## Evidence contract

Question: can typed queries select annual reports, event prefixes and named
claim/asset histories while preserving native status, lifetime memory and
unresolved coverage? Baseline: the guarded population result, native report_view
and retained full claim/cohort traces.

Primary criteria: exact source/path/context binding; duplicate IDs, unexpected
fields and wrong query fields refused by closed schema; each valid query equals
the native report or exact recorded population prefix. Requests before creation
distinguish a known empty supplied history from a missing/unknown population.
A failed or unexecuted event supplies no successful snapshot. Missing opening
data preserves obligations. Cross-profile/actor admission remains unsupported.

Vetoes: fabricated empty population, wrong period/entity, stale path, silent
query omission, future-event success, lost refusal or actor information upgrade.
Failure stops the affected adapter for repair and a new attempt. Counts are
structural diagnostics only. No evidence of actual company completeness,
probabilistic inference or generic constructor correctness follows.

Material defaults: selected owner and archival information mode come from the
native profile; the typed request must name them explicitly. Query results are
audit-only. A claim/asset absent from a supplied executed prefix means not
present in that supplied prefix, not absent in the real company. Full native
results remain attached, and population_complete is false. The adapter performs
no mutation, dynamic code loading from input, state reduction or source import.

## Implementation and checks

Use jsonschema already present. Define a closed versioned schema and one local
dispatch function. Query kinds: annual_report, event_prefix, claim_history and
asset_history. All entity/book/currency, owner, path/source digest and
information-use fields are mandatory. Query arrays must be nonempty.

Use complete baseline and event-level partial cases, an unknown opening, future
period/event, wrong identities, duplicates, ambiguous reused event IDs across
years, malformed fields, unsupported owner/join and actor knowledge. Preserve
all input and native data.

Command: python3 -B data/accounting-master/company-state-typed-request-20261028/check_request.py --output data/accounting-master/company-state-typed-request-20261028/attempt-01
Environment: existing Python/jsonschema, CPU-only exact operations, no GPU
imports or stochastic seeds. Save schema, request/result, adverse controls,
manifest, checks and decision. No existing successful writer is rerun.
