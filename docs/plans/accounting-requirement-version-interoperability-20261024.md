# Connect dimensional and guarded requirements to authoring and input binding

24 October 2026. S2–S4; MC05/13/15/17/23/24/26/27/31 and G2/G3/G10/G13/G15/G17.
Preserve recorded v1/v2/v3 evaluators and existing v1 authoring/binder evidence.

Question: can the checked dimensional and guarded requirements be authored and
bound to exact records with the same semantics, without silently upgrading a
v1 definition? The baseline is each version's independently authored typed
record and evaluator. Version dispatch must be explicit and closed; supplied
strings cannot load code. Retain exact manifest, schema and raw-record identity.

Skeptical audit: v2 dimensions and scale cannot be inferred from informal v1
context strings; v3 guard/required_known fields cannot default silently. Reusing
an old parser by dropping new fields would change the method. Generic dispatch
must not promote an unsupported version, allow private lowering identities or
accept a caller-provided callback. Schema meaning remains caller-declared;
no source/accounting truth or full eligibility follows.

Specify a versioned frontend/exchange and binder successor. Reuse existing
strict JSON/token/pointer helpers where compatible, but do not mutate frozen
v1 files. Add explicit type fields, mul expressions, guard dependencies and
required_known declarations. Assess through each pinned evaluator and compare
typed/text/bound outputs exactly, including original unknown identities,
inactive/unknown activation and product type information. Keep conversion as an
explicit separately authored record, or reject it; no auto-migration.

Primary criteria: exact version identity and semantic equality across authoring
and record binding for v2/v3 independent examples, plus unchanged v1 replay.
Dropped fields, changed guards, inferred units, duplicate records, unknown
versions or hidden coercion veto acceptance. Counts/speed are explanatory.
No usability superiority, complete DSL, full accounting method or production
claim follows. Continue collection/state prerequisites after this repair.

Artifacts: data/accounting-master/requirement-version-interoperability-20261024/.
CPU-only deterministic checks; record command, commit, input/output hashes and
result. Audit manuscript integration after this coherent language increment.
S1–S5 partial; S6 held; S7 deferred. No global continuation veto is supported.
