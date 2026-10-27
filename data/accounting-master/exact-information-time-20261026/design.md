# ExactInstantProjection/1

This profile converts exactly bound timestamp strings into rational seconds
since 0001-01-01T00:00:00Z on a proleptic Gregorian, fixed-offset time axis.
The axis omits leap seconds; a string naming one is unsupported. It is a
comparison coordinate for this profile, not a claim about physical elapsed time.

Inputs are the existing MethodInputBinding/2 registries and plan. The original
binder validates bytes, schemas, pointers, roles, contexts and original manifest
identities. Projection uses bind, not assess: text self-equalities in diagnostic
input manifests declare selections only. Every selected input must have text
type. Known strings use the grammar in the plan; unknown bindings keep their
original reasons. No role is upgraded by conversion.

The numeric coordinate is (ordinal(date)-1)*86400 + hour*3600 + minute*60
+ second + exact_decimal_fraction - signed_offset_seconds. Parsing validates
the original civil date and time fields first. An offset-equivalent spelling
gives the same coordinate but keeps different original source bytes and strings.
Offsets are restricted to 00:00–23:59; -00:00 is unsupported because an unknown
local offset cannot supply the needed conversion. UTC results outside supported
years 1–9999 refuse. Fraction precision is at most 18 digits, with no truncation.

Each output retains the input lineage, original tagged value and complete text
type. Its rational type uses the utc_second dimension and scale 1/1. Original
context is serialized losslessly in source_context; time_axis is explicit.
The wrapper avoids treating a source currency key as the unit of a timestamp.
Only equal complete contexts and time axes compare under the existing engine.

The projection record includes source-plan/manifest identities and its own
digest. A caller can explicitly serialize it and bind its tagged values through
the existing binder, retaining projection identity as provenance. Requirement
ordering is still MethodRequirements/2, never a callback into this converter.
Projection and assessment remain distinct results: invalid/unsupported parsing
does not produce a partial numeric record; missing evidence remains unknown.

No returned flag admits execution, source authority, accounting applicability
or a native request. Evidence membership, available-at truth, ingestion truth,
measurement date and current view remain separate native obligations. The old
native parser and retained sources are not modified. This is a finite design
reference, not adoption by every native profile.
