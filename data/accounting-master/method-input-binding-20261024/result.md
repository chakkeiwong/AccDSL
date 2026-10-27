# Exact record binding for reusable requirements

24 October 2026. MethodInputBinding/1 now binds every declared requirement
input to caller-pinned raw JSON, selected-field schema and exact JSON pointer.
The binder reuses the retained strict portable decoder and pointer selector;
it adds full-path syntax checks, bounded traversal and exact type/role/context
agreement. It does not load code from a supplied record or infer conversions.

The increment passes 157 checks and 28 combined unit-test methods across two
retained record comparisons, with 122 protected inputs unchanged. The original
operations record and explicitly derived retained-return record reproduce the
prior bridge values and selected assessments. The return record is labeled a
projection; its canonical bytes are not misrepresented as the original source.

Changed values require new raw and manifest identities. Each resulting input
preserves its actual raw SHA256, schema digest, pointer, type, role, encoding and
missing policy. This resolves the bridge's previous loose source-reference
convention for newly bound records without rewriting frozen bridge evidence.
Unknown sentinel interpretation is explicit per field; literal text unknown
and numeric zero remain distinct from missing evidence.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Retain generic input binding reference | Exact expected values, pinned identities and adversarial refusals pass | No source/context/role substitution, hidden coercion or retained-byte mutation found | Completeness of all prerequisites of an actual method boundary | Inventory every return-module check and choose the next reusable extension | Truth of supplied schema contexts, source/accounting admission, full eligibility or production readiness |

The tests reject changed hashes, schema swaps, undeclared or duplicate mappings,
invalid escapes and array indices, scalar traversal, duplicate JSON keys and
non-exact numbers. Declared missing facts remain unresolved; malformed binding
remains invalid; unavailable registries remain unsupported. A true caller
schema declaration is still not independently verified financial evidence.

Evidence is deterministic engineering conformance only. All successful results
retain method_eligible=false, source_admission=false, accounting_admission=false
and executed=false. No whole requirement closes or global continuation veto
fires. S1–S5 partial; S6 held; S7 deferred. Version 3.59 remains 429 pages and
not_ready; this new binding increment awaits a later coherent integration.

Reproduce with python3 -B data/accounting-master/method-input-binding-20261024/verify.py --replay.
Manifest, source locks and binding-records.json preserve commands, commit,
environment, exact raw records, definitions, schema and outputs. Next:
docs/plans/accounting-complete-method-coverage-20261024.md.
