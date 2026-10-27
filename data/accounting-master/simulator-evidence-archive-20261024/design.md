# SimulatorEvidenceArchive/1 reference

This optional single-writer reference archives complete JSON evidence. It does
not execute a financial model, accept a source interpretation or commit a native
state. A storage receipt means that the supplied bytes and dependencies were
archived. Semantic verification and every admission/execution flag remain false,
even if the archived payload itself asserts something stronger.

The closed SimulatorEvidenceBundle/1 contains profile and an ordered records
list. Each record contains name, role, profile, json and dependencies. Names are
unique local ASCII identifiers. Roles are definition, state, proposal, result
or note. The declared profile must match a payload profile when present;
unrecognized profiles can be retained as unverified evidence. Dependencies are
distinct names of earlier records. Their declared order is retained separately
from P07's unordered physical dependency edges.

The exact UTF-8 JSON text is retained, including whitespace, numeric lexemes,
Unicode spelling, list order, unknown fields and finite timing metadata. JSON
must have an object root, no duplicate keys, no nonfinite numeric tokens and no
invalid Unicode scalar. Decimal parsing checks numbers without altering their
original representation. No quantity rounding or record filtering is performed.
Callers supply positive integer max_records, max_record_bytes and max_total_bytes.
These are explicit convenience ceilings rather than recommended performance
settings. Validation rejects before mutation. Python parser/resource failure is
not evidence that a scientific result is invalid.

Each exact payload and exact declared-profile label is hex-encoded in a small
closed envelope with byte count, SHA256, role, local name and ordered parent
names. This avoids P07 Unicode and field-name normalization aliases. The record
node depends on the archive marker and its named predecessor nodes. A receipt
contains ordered name/node descriptors, total bytes and the unverified boundary,
and depends on all records plus the marker. All insertions occur in one explicit
P07 transaction. An exact retry yields the same receipt; changed bytes produce
a new content identity. There is no mutable request-name registry.

Read validates the marker and code lock, closed receipt/record envelopes, exact
node identities and physical edges, byte counts/hashes, limits, decoded UTF-8,
JSON and declared dependencies. Archive also rereads the receipt before commit:
P07's existing-key shortcut must not hide a corrupted payload on an exact retry.
The focused review added this check and a marker recheck before each write.
The read-only preflight connection is explicitly closed before P07 opens the
database. Smaller read limits can refuse an otherwise valid larger archive.

An existing unrelated P07 file is refused by read-only preflight before trigger
installation. A new archive is initialized and marked in a same-directory
temporary file, closed and published with a non-overwriting hard link. A crash
before publication leaves no destination; a crash after publication leaves the
complete marked archive. A hard process exit can leave an unreferenced staging
file. The reference does not sweep other files or overwrite an existing path.
Filesystems without this hard-link operation are outside the tested reference.

Original P07 implementation hashes are checked before storage use. Seven
inspected inputs remain protected by source-lock.json; package verification also
records its own implementation and complete replay cases. No frozen P07 or native
method file is changed. No schema migration is implemented: an unknown database
version or incompatible marker is refused.

The evidence concerns exact local retention, fresh-process reads, retry behavior,
and the tested before/after-commit process-exit points. It establishes neither
power-loss durability, multiwriter/distributed operation, adversarial authenticity,
native event cursor execution, source admission, sector-module composition nor
general migration. Those remain independent simulator obligations.
