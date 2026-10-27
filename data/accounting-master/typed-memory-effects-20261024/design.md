# Typed memory updates from immutable inputs

24 October 2026. S2–S4; MC05/13/15/17/23/24/26/27/31.

## Source audit and skeptical decision

Inspected method_input_binding_v1.py pointer_parts, located and bounded: they
already provide strict pointer escaping, canonical array indices, bounded depth
and exact reads through the pinned portable selector. Reuse those helpers. The
native state-structure adapter validates the complete concrete runtime record,
including exact canonical scalar extensions. Native transition stages a copy,
and the company engine has the same atomic pattern. Neither inspected generic
helper exposes a reusable, typed mutation language. No repository helper named
apply_patch, resolve_pointer or validate_delta was found in scripts/tests beyond
the binder; this is a scoped search, not an exhaustive software survey.

MethodMemoryEffects/1 names exact state and input schema digests and an ordered
operation list. Operations are replace an existing object member, insert an
absent object member, and append one array item. No deletion, root replacement,
array-index writes, callback or executable import is supported. Replacement and
insertion require an object parent. Append requires an existing array. The whole
before and resulting records must satisfy the same selected state schema.

Paths are token arrays. Literal tokens are exact strings; a dynamic token has
one input-pointer field whose resolved input is a nonempty string. Such a key
is one token even if it contains slash or tilde; it cannot escape its map.
Reads may address the original before record or the supplied input record;
they never observe staged mutations. Value forms are literal, read, object and
array constructors. No arithmetic occurs here: the preceding monetary program
supplies separately checked amounts to a later composition adapter.

All definitions, shapes and original records are checked before staging.
The complete operation list is checked for path overlap before any write:
identical append paths may repeat in supplied order; any other equal/ancestor/
descendant write paths conflict. A failed replacement, duplicate insertion,
missing reference, schema violation or complexity bound returns no after record.
The caller's before and input records stay byte-semantically unchanged. Staging
is diagnostic only; execution/admission/eligibility/commit flags remain false.

## Closed schema subset and bounds

Reuse Draft202012Validator with FormatChecker and the exact-scalar checks from
the existing state-validation convention. Permit only the keyword subset used
by the retained native state: type, properties, required, additionalProperties,
propertyNames, items, const, enum, oneOf, not, pattern, format, minLength,
maxLength and x-exact-kind, plus the fixed draft identifier. Reject remote/local
references, extension keywords and arbitrary regexes. The five retained patterns
are an explicit allowlist. Objects are closed fixed records or typed maps;
arrays have a complete item schema; scalar forms have explicit scalar constraints.
No JSON numeric financial values are admitted: rationals remain canonical strings.

Limits are engineering hypotheses: 1,000,000 canonical bytes per definition,
schema or record; 4096 nodes and depth 48; 256 operations; 4096-character text.
Check schema structure, all value templates and before/input/after records against
those limits. Test boundary rejections. Reusing those finite limits preserves the
existing input discipline but does not establish capacity for all companies.

## Evidence contract and next dependency

Baseline: native returned component, lots, adjustments, seen/date and gross-flow
memory for settlement and sale, with amount inputs recomputed by the recorded
monetary program. The independent criterion is exact generic replace/insert/
append behavior, read-before semantics and atomic rejection. Source drift,
mutated inputs, partial after-state, malformed schemas, path ambiguity or hidden
defaults veto promotion and trigger repair. A broken comparator prevents result
interpretation until repaired. Counts are explanatory only.

First implement and check the generic mutation language; then compare selected
native memory. A matching patch is not a complete method: event schema,
preconditions, exact input binding, balance/funding checks and trusted proposal
recomputation remain explicit composition obligations. No source/accounting
admission, production persistence or concurrency claim follows.

## Checked composition boundary

The comparison harness recomputes amounts with MethodMonetaryEffects/1, adds each
derived delta to the preceding balance, and constructs typed memory inputs. Nine
known cases produce exactly the native complete after-state; one unknown-NRV
case stops before memory staging. The memory primitive does not verify the
economic truth of supplied balances or bind those inputs to the preceding
monetary result. A future caller could supply structurally valid wrong amounts.
Complete transition composition must own that binding and recompute the full
proposal. This is the next engineering dependency, not an acceptance claim.
