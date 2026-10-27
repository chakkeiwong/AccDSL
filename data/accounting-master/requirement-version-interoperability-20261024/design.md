# Versioned authoring and binding for requirement successors

MethodRequirementExchange/2 is a new transport with explicit definition profile
dispatch to exactly MethodRequirements/1, /2 or /3. Each preserved evaluator
validates its own definition and supplies its own result. Unknown profiles fail;
no version is inferred and no callback or module path can be supplied. The old
exchange and frontend remain unchanged and continue their own exact replay.

The named text grammar uses strict JSON strings, complete type objects and
prefix expressions. This replaces no old spelling: its header explicitly names
the new exchange. Input declarations carry the entire original type object,
role and source reference. Constants likewise carry the full type. A v3
guarded declaration carries separate guard/body dependency lists and expressions;
required_known declarations are explicit: v3 requires exactly one list declaration,
including an explicit empty list when no fact is separately required. Omission is
invalid; it does not default to an empty list. A v1/v2 require declaration cannot
contain guards. v3 rejects unguarded declarations rather than assuming true.
Shared token/JSON helpers retain duplicate-key refusal and exact Unicode values.

The exchange has profile, definition, selected_digest, values and
available_capabilities. Selected digest must match exact definition content.
Rendering and lowering preserve dimensions, scale, context, guard semantics,
missing bindings, order of requirements and required_known list. Input-map order
is canonicalized only as already done by content hashing. No source truth,
capability installation or human usability is inferred from a roundtrip.

MethodInputBinding/2 maps the same requirement versions to raw records through
RequirementInputSchema/2, whose requirements_profile explicitly identifies the
expected version. Its field types and roles must exactly match the selected
definition. No v1 unit string becomes a dimension automatically. The binder
first validates original profile, schema identity and fields, then uses an
internal binding-only v1 shadow to reuse the protected byte decoder/pointer
selection and missing-value conventions. Full dimensional types are encoded
losslessly in reserved internal context keys. Original raw/schema/manifest/plan
identities and type declarations are restored in public lineage; internal
identities remain separately labeled. The shadow never authorizes a method.

Semantic assessment runs only through the selected original version on the
bound values. Binding success is independent of requirement satisfaction: a
correctly bound record can contain invalid or unresolved method inputs. Private
lowering names and reserved dimensional context keys are refused where the
selected type version requires. All admission/execution flags remain false.

Evidence compares independent typed records, versioned text, strict exchange,
exact raw binding and original evaluator outputs for all three versions. Include
known, unknown, false-guard/all-inactive, dimensional mismatch, changed guards,
swapped schema versions and changed byte identities. Protected v1 tests replay;
retained scalar, dimensional and guarded examples remain separately identified.
No migration, full method, authority, production or forecasting claim follows.
