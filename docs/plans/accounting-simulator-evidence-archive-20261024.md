# Exact-byte atomic archive for simulator evidence

24 October 2026. S2-S4 reference design; MC04/05/10/24/25/26/28/35; G18.
Question: can a bounded reference preserve complete simulator record bytes,
ordered dependencies and a group receipt across process restart using unchanged
P07 storage primitives? This is an evidence archive, not a native execution
store or production promotion. It addresses a shared dependency across methods.

Skeptical audit incorporates25 checks/17 probes. Direct P07 canonical identities
can alias Unicode or constraints order and refuse float timing metadata. A
whole record must therefore be stored as its exact UTF-8 bytes plus SHA256,
with a small closed outer envelope. Semantic verification remains a separate
profile operation; archiving a forged proposal cannot mark it valid.

Define SimulatorEvidenceBundle/1 with an ordered list of uniquely named records.
Each record has a role, declared profile, exact JSON text and dependencies on
prior records in the same bundle. Closed finite roles distinguish definition,
state, proposal, result and note. Profile is an exact label, not an authorization.
Validate strict UTF-8, duplicate-free JSON, finite JSON numbers and top-level
object; retain original whitespace, numeric lexemes, Unicode and list order.
A declared profile must equal the payload profile when the payload has one.
Unknown profiles may be retained as unverified evidence; no callback execution.
No automatic source or accounting admission, method eligibility or native commit.

Expose archive(bundle), read(receipt), and integrity verification in a new
reference module backed by an unchanged P07 Store opened on a fresh explicit
archive file. Reject an existing unrelated P07 database via an archive marker;
refuse unknown schema/profile rather than migrate it. Store code-lock identity
for the selected original primitives; checks precede mutation. Explicit byte and
record-count limits reject before any write; these are convenience ceilings,
not performance recommendations. Limit values must be caller-supplied.

The bundle receipt depends on all record nodes. Insert marker initialization,
record nodes and receipt under the appropriate outer transactions. Exact retry
returns the same retained receipt. Changed bytes yield a new identity; record
names are local to a bundle, not a mutable global key. The reader recomputes all
byte hashes, closed envelopes, ordered descriptors, exact dependency edges and
bundle identity, and preserves every unverified/admission boundary. No arbitrary
SQL or native transition is accepted through this interface.

Primary criterion: exact byte equality and complete group publication across
normal reopen, retries and bounded subprocess exits before/after commit.
Comparators: original bytes and unchanged P07 nodes/transactions; native
proposal replay demonstrates the separate semantic boundary. Veto: normalization,
dropped unknown fields, changed dependency order, partial receipt publication,
false semantic/admission flags or frozen input mutation. Expected unsupported
payloads should reject atomically. Timing/counts are explanatory only.

Tests: Unicode normalization pair, reordered constraints, float diagnostics,
whitespace/numeric lexeme variants, duplicate names/JSON keys, missing/cyclic or
forward dependencies, invalid UTF-8/nonfinite numbers, wrong profile, explicit
limits, retry/reopen, forged bytes/hash/edge/receipt, unrelated database refusal,
initialization and bundle interruption, original native forged-proposal check.
Use fresh/tmp databases with GPU hidden. Record actual manifests, finite cases,
source locks, conditions and saved replay before updating controls.

No claim about power-loss durability, multiwriter/distributed correctness,
whole-state execution or general schema migration. Those remain explicit gaps.
After the reference, integrate its boundary and storage findings with the
manuscript and inventory; then return to broader module/history semantics.
