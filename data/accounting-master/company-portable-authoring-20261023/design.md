# Typed portable references to the preserved company drafts

The company drafts and portable record contract use different identities.
The company engine hashes compact JSON with escaped non-ASCII characters;
portable records hash their typed envelope with a schema prefix and literal
UTF-8 scalars. Neither identity replaces the other. An import preserves original
blob bytes, their raw hash and decoder, the old decoded draft hash, and a new
typed record identity with explicit dependencies.

The existing company-path admission module supplies the portable encoder,
record digest, dependency discovery and reachable-closure validator. Reuse
those functions. Add strict JSON duplicate-key/float/Unicode rejection at the
decode boundary and schema-specific semantic checks; do not rewrite the
protected predecessor merely to extend its meaning.

An import also references DraftContent: the canonical decoded value with its
decoder and profile. Equivalent escaped/literal Unicode and whitespace share
that content identity; original imports and whole exchanges still differ when
their source bytes differ. Codepoint normalization is never performed. Original
files and extracted subvalues are distinguished with a parent reference and
strict JSON pointer. No reconstructed subvalue is labelled an original file.

The extension is a portable reference to a declared legacy draft, not a claim
that all draft fields have become the full portable numeric/type IR. Each
DraftImport record binds raw bytes, exact local decoder/profile/schema and
decoded content identity. Member records expose name, path/result imports,
context, common opening identity, status and annual outcome records. Family
records expose ordered members, common source/opening/horizon, unweighted
authored-scenario meaning and the whole result import. Thus dependency closure
and partial-year meaning do not disappear inside an opaque blob.

Expression-policy records explicitly connect the program, base policy, parent
path, output map, evaluated policy, materialized child and result. Their input
dependency names come from static analysis and their result is recomputed with
the exact caller-supplied evaluator and generator. A family member referring
to the same child path must bind that identity. No prior policy availability
declaration is automatically inherited by the expression program.

Recovery records bind the exact family, method descriptor, checkpoint prefix
and final result. The validator replays the saved prefix through the caller's
trusted method. Import establishes neither publication nor a durable work
world. Keeping physical durability false is mandatory. Changed representation
does not authorize execution of packet-supplied code.

Every record has its own closed schema and exact dependency list. The root
requires all retained authoring components and the preserved source bytes.
Missing, extra, mis-typed or unreachable records/blobs are invalid. Content
binding and trusted semantic replay remain separately reported. Rehashed false
financial results may satisfy identity consistency but fail trusted execution.

The first implementation will wrap existing schemas and decoded draft content
as explicit legacy imports rather than claim a universal field conversion.
The full normalized portable expression/type IR, source maps, time admission,
general module interfaces and real company evidence remain open obligations.
This narrows the implementation claim while preserving the reviewed task:
one exact trace from original bytes through typed dependencies to checked
company results. No new accounting rule, observation date or probability is
introduced.
