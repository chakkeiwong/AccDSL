# Native term-state structural audit

26 October 2026. MC20/24/25/28/33/34. Baseline is the inspected
receivable_term_history_v1.validate and called dependency checks. The semantic
bundle is frozen. This audit passes only after adding the omitted whitespace
premise check below; existing typed text rejects empty/control strings but
allows whitespace, whereas native engine.text also requires nonblank content.

| Native structural condition | Reuse or explicit addition | Early discriminator |
|---|---|---|
| Exact state fields and profile | Declared record_fields and equals before normalization | Missing/extra field, wrong profile |
| Bounded input | Preserved binding.bounded and memory.bounded on original state | Original whole-state node/byte limit |
| Typed book and actual context | Existing typed_book stage | Missing schema or changed leaf type |
| Exact term-claim values schema and clock schema | map_values and equals | Added field despite internally consistent derived schema |
| Operating role population/injection/classes/cash | Existing role stages | Missing, duplicate or misclassified role |
| Cost leaf, exact dimensions and positive amount | Existing memory/predicate stages | Missing leaf, wrong units, zero cost |
| Exact migration fields and scope | Existing record_fields/equals | Preserved migration-scope discriminator |
| Migration premise is nonblank | Existing text stage using engine.text | Space-only premise |
| Source-book digest syntax | Explicit sha256_format check using existing hash_string | Nonhex, wrong length, uppercase; no invented source provenance |
| Each term premise is nonblank | Declared projected field text check using existing engine.text | Space-only term premise |
| Claim/term/assessment keys are nonblank | Preserved typed-memory map-key validation | Space-only key |
| Native dependency pins | Explicit union of inspected constants, verified before candidate | Changed file or altered dependency declaration |

The operating builder performs input checks before constructing six method
records. No later validation occurs in that construction; skipping the unused
records is therefore valid for this structural question. It is not permission
to replace method execution. Native life.control is not called by native term
validate and must not be added: its current-due overdue rule is different.

Normalize by renaming the original book field to opening, retaining every
other field/value and insertion order. Reject the original envelope before
adaptation; retain original and normalized identities. The old opening-stage
evaluator is reused without empty-map, report, cursor-equals-book or command
stages. Its internal success label does not grant new-period admission; the
outer result explicitly reports selected term-state structure.

The reviewed combined contract binds the structural template, text/digest
checks, exact selected roles/cost pointer and frozen semantic bundle. Native
validation allows other compatible roles; the reviewed contract is explicitly
narrower. Test that discriminator rather than claiming equivalence over all
native configurations. Success means selected synthetic structural/semantic
conditions, with source/accounting/execution flags false. Snapshot validation
does not validate future commands or source history.

Promotion criterion: valid retained states and native-refused corruptions
agree; normalized inputs and all reused stage/subresults match direct calls.
Structural/migration or dependency omission vetoes promotion. Unknown supplied
population remains unresolved. Harness defects trigger repair. Source digest
syntax does not prove the referenced source exists, and no such claim follows.
