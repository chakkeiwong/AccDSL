# Common program text: bounded design

26 October 2026. MC20/23/24/25/33/34. Language composition design, not closure
of the financial-statement DSL or simulator specification.

## Findings and field ownership

field-ownership.json maps every top-level program, registry-entry, invariant,
event-contract and command field in the two retained eleven-command examples.
DeclaredCompanyText/2 imports one scalar registry. Its receivable successor
instead imports lifecycle configuration and generates native methods. Neither
expresses the complete authored methods and their explicit registries.
The new typed runner has those semantics but no common source language.

Reuse CompanyMethodAuthoring/1 for whole method bodies and the checked
event/report/carry grammar for commands. Import opening facts, shared schemas,
statement mapping and memory types by exact hashes. Entry schema populations
are separate resources: merging them into shared report schemas changes report
request identity. Explicitly select a hashed BookStateInvariant/1 resource.
That selection imports executable rules; it does not author their algorithms.
The collection/totals engines have no corresponding text frontend. General
invariant authoring remains a gap; its full typed rule source stays in the bundle.

## Grammar and semantic ownership

The AuthoredCompanyText/1 header explicitly names either the guarded or
contracted typed target and a program name. Required fixed-order declarations:
import_opening, import_schemas, import_mapping, import_memory_definition, each
with its resource hash; then select_invariant PROFILE HASH.

A registry ALIAS contains entry METHOD_KEY blocks. Each entry declares
entry_schemas HASH, account_class ROLE CLASS, supplied_input NAME TYPE,
metadata_input NAME FIELD, clock KIND, and, for transition v2 only,
entry_memory_definition HASH. Its begin_method_source / end_method_source
block contains the entire existing method source unchanged. Transition version
comes from that source header. Registry context equals the opening-book context,
as required by the typed runner. Entry and registry hashes are derived from
actual contents. Names are local aliases, not runtime callback names.

For the contracted target, select_event_contract PROFILE native HASH opens
an explicit block of contract_role ROLE ACCOUNT, unit_cost_pointer POINTER
and policy PROFILE past_due RULE carry RULE because PROVENANCE, ending at
end_event_contract. Only the implemented selected receivable contract is admitted.
Its pinned native semantics are selected, not newly authored. The guarded
target contains no such block. This is an explicit semantic choice.

The existing event header gains registry ALIAS before method KEY. Existing
input NAME known VALUE because SOURCE or unknown REASON lines carry projected
method inputs. For the contracted target, every event additionally declares
intent ID on DATE and full intent_input lines using the same value grammar.
The source retains customer, claim and interval facts removed by specialization.
Projected and original event identities/dates are both preserved. Input types
come from explicit registry declarations; full-intent types come from the
explicitly selected native interface. Eligibility and exact request equality
remain runtime checks on the current book, not compile-time forecasts.

Report, equity, note, carry, retained-account, next-period and per-leaf memory
policy syntax are reused exactly. Empty report lists are part of that existing
grammar. A reset can inherit a type only from an explicitly present opening
leaf; no type is invented for a future dynamic leaf. Preserve policies on
future claim leaves are explicit in the fixture.

All declarations end with semicolons. Definitions precede commands; duplicate
aliases/fields/inputs, unknown declarations, missing terminators and extras
are invalid. Resource population must exactly equal referenced hashes.
The compiler does not fetch files or URLs or execute imported code.

## Source, errors and bounds

Use UTF-8 byte offsets and SHA256 of original bytes. Old parser character
offsets are diagnostic only; convert them through the actual prefix when
locating errors in the enclosing source. Store outer line spans and absolute
translated method spans. Do not normalize indentation, Unicode or line endings.
Inline method source must end in a line ending for exact block framing;
no-final-newline embedding is an explicit refusal. BOMs, lone CRs, forbidden
controls, oversize source/resources and excess commands/entries/declarations
are invalid under the existing bounded limits.

Compilation means syntax/resource/structural validation only. Eligibility,
invariants, selected-native request comparison, unresolved inputs and accepted
prefixes belong to the retained runner. Errors retain stage and source line/byte
range. Native refusal statuses remain distinct from syntax or source admission.

## Evidence required before credit

Compare the whole compiled typed program with both retained fixtures, then the
whole runtime result, all 22 commands, reports, archives and original intended
requests. Edit a collection algorithm directly in source: guarded execution
must change its outcome; the selected full-payment contract must refuse the
mismatch. Exercise missing intent, altered identities/resources, duplicates,
unknown inputs, Unicode/CRLF spans, report/carry content and failed prefixes.
A render/parse cycle alone earns no executable-language credit.

Hard vetoes: incorrect reconstruction, changed protected files, hidden
generation, lost intent, accepted tampering or an incorrect refused-prefix
state. No statistical ranking applies. Finite conformance does not establish
accounting authority, actual-source completeness, general invariant authoring,
production readiness or human acceptance. After this unit, reassess the broader
queue rather than indefinitely enlarging the synthetic receivable example.
