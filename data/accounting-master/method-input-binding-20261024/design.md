# Declarative requirement inputs tied to exact supplied records

The protected evaluator accepts typed declarations and separate values. This
increment supplies a generic bridge from caller-pinned records to those values.
It does not reconstruct a company, allocate consolidated disclosures to books,
grant accounting authority or declare the complete source record valid.

## Reuse and audit

The company-portable-authoring portable.py select helper already checks pointer
prefixes, escape syntax and canonical array indices and returns deep copies.
Its strict decoder rejects duplicate keys, floats/non-finite numbers, invalid
UTF-8 and non-ASCII object keys. Reuse those exact helpers through an explicitly
pinned module, adding a bounded structural walk and complete pointer-syntax
validation before selection. Its dependencies are local definition-only code.
No code named by a supplied manifest is imported or executed. Unicode values
remain supported; non-ASCII keys are an explicit decoder limitation.

The simpler statement/XBRL pointers omit some escape/index checks and are not
used as a universal validator. An absent early path must not conceal an invalid
later escape: validate the full pointer first. A scalar encountered before the
end of a path is a wrong record shape, not a missing fact.

## Records, schemas and selection

The binding plan is MethodInputBinding/1 with manifest_digest, records and
bindings. Each named record pins a raw UTF-8 JSON SHA256 and a field-schema
digest. Bytes come from a caller-provided blob registry; schemas and requirement
manifests come from separate caller-owned registries. The binder performs no
file, network or dynamic code lookup based on supplied strings.

A RequirementInputSchema/1 declares named scalar paths. Every field has an exact
type/context, role, encoding and missing policy. It describes selected fields;
it does not assert that the entire source document conforms to an accounting
schema. The encoding is scalar, legacy_unknown_string or tagged_binding. Only
the explicitly selected legacy encoding interprets the exact string unknown as
missing evidence. Tagged bindings preserve known/unknown and reasons. Scalar
text unknown remains known text. Missing may be invalid or unresolved; the
plan must choose per field. Null is not a missing value unless already encoded
as an explicit tagged unknown; it fails scalar validation.

Each input maps to one record name and JSON pointer, with no duplicates or
implicit fields. The mapping covers exactly the manifest inputs. Each selected
pointer must exist in the pinned field schema, and its type and role must equal
the manifest declaration. The manifest source_ref must be exactly
sha256:RAW_DIGEST#POINTER. Changing record bytes, schema context, role, encoding
or mapping changes a pinned identity. Source_ref now identifies the actual
supplied record, including any explicit scenario mutation, instead of pointing
to the unchanged fixture that originally supplied a field.

The binder returns the extracted known/unknown values, per-input raw/schema
identities, pointer, type, role and missing convention, plus plan identity.
An optional assessment calls the protected core on those exact values. Required
records or schemas unavailable to the caller are unsupported; mismatched hashes,
bad syntax, bad shapes, undeclared fields and type/context/role mismatches are
invalid. A declared unresolved missing field remains unknown. No default zero,
conversion, role relabeling, source admission or full eligibility is inferred.

## Evidence and limits

Compare the actual operations example and independently projected retained
return record with the previous imperative bridge. Changing any source value
requires repinning its raw bytes and all affected source references. Test
unknown and known mutations, wrong hashes, schema swaps, missing paths,
duplicate mappings, escaped keys, canonical array indices, scalar traversal,
duplicate JSON keys and unused/extra mapping. The schema's context is a caller
declaration, not independent evidence of its truth; this limitation appears in
every result. A reported consolidated amount cannot be silently matched to a
legal-book declaration with a different context or role.

All checks are deterministic engineering conformance. The exact comparator is
the retained input values and declared assessment, not accounting correctness.
Primary criteria are accurate binding, pinned identity and explicit refusals.
Missing source facts block stronger real-company claims, not this generic
language work. No whole requirement closes or global continuation veto fires.
